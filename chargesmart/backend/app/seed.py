import random
from sqlalchemy import select
from .models import Station, Vehicle, Connector, UsageHistory, ChargingSession
AREAS = [('Indiranagar',12.9784,77.6408),('Koramangala',12.9352,77.6245),('JP Nagar',12.9063,77.5857),('Jayanagar',12.925,77.5938),('Whitefield',12.9698,77.75),('HSR Layout',12.9121,77.6446),('Hebbal',13.0354,77.5988),('Yelahanka',13.1007,77.5963),('Electronic City',12.8452,77.6602),('Rajajinagar',12.9915,77.5533),('Kengeri',12.914,77.483),('Devanahalli',13.246,77.711)]
def seed(db):
    if db.scalar(select(Station.id).limit(1)): return
    rng = random.Random(42)
    for i in range(42):
        area,lat,lon=AREAS[i%len(AREAS)]
        power=[22,30,60,120,150][i%5]
        kinds=['CCS2'] if power>22 else ['Type 2']
        s=Station(id=f'demo-{i+1:03}',name=f'Demo {area} Hub {i//12+1}',address=f'Sample location near {area}, Bengaluru (fictional)',lat=lat+rng.uniform(-.012,.012),lon=lon+rng.uniform(-.012,.012),operator=['Demo Volt','Demo GreenGrid','Demo UrbanCharge'][i%3],power_kw=power,connectors=kinds,ports=2+i%5,status='Status Unknown',tariff=round(14+rng.random()*8,2),source='simulated')
        db.add(s);db.flush()
        for k in kinds: db.add(Connector(station_id=s.id,kind=k,power_kw=power))
        for h in range(24): db.add(UsageHistory(station_id=s.id,hour=h,occupancy=.7 if 17<=h<=21 else .25,wait_minutes=20 if 17<=h<=21 else 4))
        db.add(ChargingSession(station_id=s.id,duration=30+i%20))
    for i,(n,c,e,k,p) in enumerate([('Compact EV (sample)',30,.13,'CCS2',30),('Family EV (sample)',45,.16,'CCS2',60),('Long-range EV (sample)',75,.18,'CCS2',120),('City EV AC (sample)',25,.12,'Type 2',11)]):
        db.add(Vehicle(id=i+1,name=n,capacity=c,efficiency=e,connector=k,max_charge_kw=p))
    db.commit()
