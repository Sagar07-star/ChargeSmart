from datetime import datetime,timezone
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy import select,func
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Station,Vehicle,Report,PredictionRecord,SavedRoute
from ..schemas import Plan,Recommend,Wait,ReportIn
from ..services.energy import distance,impact
from ..services.planner import plan_trip
from ..integrations.maps import live_stations
from ..ml.predict import predict
from ..seed import AREAS
router=APIRouter(prefix='/api')
def serialize(s):
    return {c.name:getattr(s,c.name) for c in s.__table__.columns}
def station_rows(db):return [serialize(s) for s in db.scalars(select(Station)).all()]
async def fetch_stations(db,mode,lat,lon):
    if mode=='demo':return station_rows(db)
    data=await live_stations(lat,lon);out=[]
    for x in data:
        a=x.get('AddressInfo') or {};cs=x.get('Connections') or [];kinds=[]
        for c in cs:
            title=(c.get('ConnectionType') or {}).get('Title','Unknown')
            kinds.append('CCS2' if 'CCS' in title and 'Type 2' in title else 'Type 2' if 'Type 2' in title else title)
        out.append({'id':f"ocm-{x['ID']}",'name':a.get('Title','Unnamed charger'),'address':', '.join(filter(None,[a.get('AddressLine1'),a.get('Town')])),'lat':a.get('Latitude'),'lon':a.get('Longitude'),'operator':(x.get('OperatorInfo') or {}).get('Title','Unknown'),'power_kw':max([c.get('PowerKW') or 0 for c in cs]+[0]),'connectors':list(set(kinds)),'ports':sum(c.get('Quantity') or 1 for c in cs),'status':'Out of Service' if (x.get('StatusType') or {}).get('IsOperational') is False else 'Status Unknown','tariff':None,'source':'Open Charge Map location data; no live occupancy','updated_at':x.get('DateLastStatusUpdate')})
    return [s for s in out if s['lat'] is not None and s['lon'] is not None]
@router.get('/health')
def health():return {'status':'ok','live_availability':False}
@router.get('/stations')
async def stations(mode:Literal['demo','live']='demo',q:str='',connector:str='',min_power:float=0,operator:str='',status:str='',lat:float=Query(12.9716,ge=-90,le=90),lon:float=Query(77.5946,ge=-180,le=180),radius:float=Query(200,gt=0,le=1000),sort:Literal['distance','power']='distance',page:int=Query(1,ge=1),limit:int=Query(50,ge=1,le=200),db:Session=Depends(get_db)):
    rows=await fetch_stations(db,mode,lat,lon)
    for s in rows:s['distance_km']=round(distance({'lat':lat,'lon':lon},s),2)
    rows=[s for s in rows if (q.lower() in (s['name']+' '+s['address']).lower()) and (not connector or connector in s['connectors']) and s['power_kw']>=min_power and (not operator or s['operator']==operator) and (not status or s['status']==status) and s['distance_km']<=radius]
    rows.sort(key=lambda s:s['distance_km'] if sort=='distance' else -s['power_kw'])
    return {'items':rows[(page-1)*limit:page*limit],'total':len(rows),'page':page,'mode':mode,'distance_basis':'straight-line, not road distance'}
@router.get('/stations/nearby')
async def nearby(lat:float=Query(...,ge=-90,le=90),lon:float=Query(...,ge=-180,le=180),db:Session=Depends(get_db)):
    return await stations(lat=lat,lon=lon,db=db,page=1,limit=50,radius=20,mode='demo',q='',connector='',min_power=0,operator='',status='',sort='distance')
@router.get('/stations/{station_id}')
def station(station_id:str,db:Session=Depends(get_db)):
    s=db.get(Station,station_id)
    if not s:raise HTTPException(404,'Station not found in local dataset')
    return serialize(s)
@router.get('/vehicles')
def vehicles(db:Session=Depends(get_db)):return [serialize(v) for v in db.scalars(select(Vehicle))]
@router.get('/locations')
def locations():return [{'name':a,'lat':b,'lon':c} for a,b,c in AREAS]
@router.post('/routes/plan')
async def plan(req:Plan,db:Session=Depends(get_db)):
    rows=await fetch_stations(db,req.mode,req.start.lat,req.start.lon)
    return await plan_trip(req,rows)
@router.post('/recommendations')
def recommendations(req:Recommend,db:Session=Depends(get_db)):
    rows=[]
    for s in station_rows(db):
        if req.connector not in s['connectors']:continue
        d=distance(req.location.model_dump(),s)*1.3
        if d*req.efficiency>req.capacity*(req.battery-req.reserve)/100:continue
        wait=predict(datetime.now().hour,datetime.now().weekday(),s['ports'],.5)
        arrival=req.battery-d*req.efficiency/req.capacity*100
        energy=max(0,req.capacity*(80-arrival)/100)
        charge=energy/(.9*min(s['power_kw'],req.max_charge_kw))*60
        travel=d/30*60;total=travel+wait['minutes']+charge
        rows.append({**s,'distance_km':round(d,2),'travel_minutes':round(travel,1),'wait_minutes':wait['minutes'],'charging_minutes':round(charge,1),'total_minutes':round(total,1),'cost':round(energy/.9*s['tariff'],2) if s['tariff'] else None,'score':round(100/(1+total/30),1),'explanation':'Score = 100 / (1 + total minutes / 30); total = simulated travel + synthetic wait + estimated charge to 80%.'})
    rows.sort(key=lambda s:s['total_minutes'])
    return {'items':rows,'source':'Demo only · rule-based ranking, simulated travel and synthetic waiting times','best':rows[0]['id'] if rows else None,'nearest':min(rows,key=lambda s:s['distance_km'])['id'] if rows else None,'fastest':min(rows,key=lambda s:s['charging_minutes'])['id'] if rows else None,'cheapest':min(rows,key=lambda s:s['cost'] if s['cost'] is not None else float('inf'))['id'] if rows else None}
@router.post('/predictions/wait-time')
def wait(req:Wait,db:Session=Depends(get_db)):
    s=db.get(Station,req.station_id)
    if not s:raise HTTPException(404,'Station not found')
    result=predict(req.hour,req.day,s.ports,req.occupancy)
    result['hourly']=[{'hour':h,**predict(h,req.day,s.ports,req.occupancy)} for h in range(24)]
    db.add(PredictionRecord(station_id=s.id,minutes=result['minutes'],source=result['source']));db.commit();return result
@router.get('/analytics/accessibility')
def accessibility(db:Session=Depends(get_db)):
    rows=station_rows(db);areas=[]
    for name,lat,lon in AREAS:
        ds=[distance({'lat':lat,'lon':lon},s) for s in rows];near=[s for s,d in zip(rows,ds) if d<=3];nearest=min(ds)
        score=round(min(100,len(near)*12+max(0,40-nearest*10)))
        areas.append({'name':name,'lat':lat,'lon':lon,'count':len(near),'nearest_km':round(nearest,2),'capacity_kw':sum(s['power_kw'] for s in near),'score':score,'suggestion':'Limited sample coverage; may warrant further assessment' if score<65 else 'Higher sample coverage'})
    return {'areas':areas,'source':'Simulated stations · illustrative geographic coverage, not demand','formula':'min(100, 12 × stations within 3 km + max(0, 40 − 10 × nearest distance km))','radius_km':3}
@router.get('/analytics/environmental-impact')
def environmental(saved_km:float=Query(5,ge=0,le=10000),efficiency:float=Query(.16,gt=0,le=2),grid:float=Query(.7,ge=0,le=3)):
    return impact(saved_km,efficiency,grid)
@router.post('/reports',status_code=201)
def create_report(req:ReportIn,db:Session=Depends(get_db)):
    if not db.get(Station,req.station_id):raise HTTPException(404,'Station not found in local dataset')
    r=Report(**req.model_dump());db.add(r);db.commit();db.refresh(r);return serialize(r)
@router.get('/reports')
def reports(station_id:str|None=None,limit:int=Query(50,ge=1,le=200),db:Session=Depends(get_db)):
    query=select(Report).order_by(Report.id.desc()).limit(limit)
    if station_id:query=query.where(Report.station_id==station_id)
    return {'items':[serialize(r) for r in db.scalars(query)],'source':'Unverified Community Reports'}
