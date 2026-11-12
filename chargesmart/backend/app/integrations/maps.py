import os,time
import httpx
from fastapi import HTTPException
_cache={}
async def route(a,b,mode='demo'):
    from ..services.energy import distance
    if mode=='demo':
        d=distance(a,b)*1.3
        return {'distance_km':d,'duration_minutes':d/30*60,'geometry':[[a['lon'],a['lat']],[b['lon'],b['lat']]],'source':'simulated: straight-line × 1.3, 30 km/h; not navigation'}
    key=(a['lat'],a['lon'],b['lat'],b['lon'])
    if key in _cache and time.time()-_cache[key][0]<300: return _cache[key][1]
    url=os.getenv('OSRM_URL','https://router.project-osrm.org')
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            r=await client.get(f"{url}/route/v1/driving/{a['lon']},{a['lat']};{b['lon']},{b['lat']}",params={'overview':'full','geometries':'geojson'})
            r.raise_for_status();data=r.json()
        x=data['routes'][0];out={'distance_km':x['distance']/1000,'duration_minutes':x['duration']/60,'geometry':x['geometry']['coordinates'],'source':'OSRM road route'}
        _cache[key]=(time.time(),out);return out
    except (httpx.HTTPError,KeyError,IndexError,ValueError): raise HTTPException(503,'Road routing unavailable. Choose Demo mode for a labeled simulation.')

async def live_stations(lat,lon):
    key=os.getenv('OPEN_CHARGE_MAP_API_KEY')
    if not key: raise HTTPException(503,'OPEN_CHARGE_MAP_API_KEY is not configured. Demo mode remains available.')
    cachekey=('ocm',round(lat,2),round(lon,2))
    if cachekey in _cache and time.time()-_cache[cachekey][0]<900:return _cache[cachekey][1]
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r=await client.get('https://api.openchargemap.io/v3/poi/',params={'key':key,'output':'json','latitude':lat,'longitude':lon,'distance':40,'distanceunit':'KM','maxresults':200,'compact':False,'verbose':False},headers={'User-Agent':'ChargeSmart college project'})
            r.raise_for_status();rows=r.json()
        _cache[cachekey]=(time.time(),rows);return rows
    except (httpx.HTTPError,ValueError):raise HTTPException(503,'Station provider unavailable. Choose Demo mode.')
