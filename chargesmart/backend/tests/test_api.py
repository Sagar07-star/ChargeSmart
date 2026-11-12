import os,tempfile
os.environ['DATABASE_URL']='sqlite:///'+tempfile.mktemp(suffix='.db')
from fastapi.testclient import TestClient
from app.main import app
from app.services.energy import distance,impact

def test_seed_and_filter():
    with TestClient(app) as c:
        assert c.get('/api/health').json()['status']=='ok'
        r=c.get('/api/stations').json();assert r['total']==42
        assert all(x['status']=='Status Unknown' for x in r['items'])
        assert all(x['power_kw']>=100 for x in c.get('/api/stations?min_power=100').json()['items'])
        assert c.get('/api/stations/nearby?lat=12.97&lon=77.59').status_code==200
        assert c.get('/api/stations?lat=100').status_code==422

def test_reports_do_not_change_status():
    with TestClient(app) as c:
        r=c.post('/api/reports',json={'station_id':'demo-001','issue':'Charger not working','description':'Test connector is broken.'});assert r.status_code==201
        assert c.get('/api/stations/demo-001').json()['status']=='Status Unknown'
        assert c.get('/api/reports').json()['items'][0]['description']=='Test connector is broken.'
        assert c.post('/api/reports',json={'station_id':'missing','issue':'Other issue','description':'Unknown location'}).status_code==404

def payload(**kwargs):
    p={'start':{'lat':12.9063,'lon':77.5857},'end':{'lat':13.246,'lon':77.711},'capacity':45,'battery':25,'reserve':15,'efficiency':.16,'connector':'CCS2','mode':'demo'};p.update(kwargs);return p

def test_route_energy_and_multi_stop():
    with TestClient(app) as c:
        direct=c.post('/api/routes/plan',json=payload(battery=90));assert direct.status_code==200
        assert direct.json()['stops']==[]
        r=c.post('/api/routes/plan',json=payload());assert r.status_code==200,r.text
        out=r.json();assert out['arrival_battery']>=15;assert len(out['stops'])>=1
        assert all(s['arrival_battery']>=15 and 'CCS2' in s['connectors'] for s in out['stops'])
        assert out['total_minutes']>=out['driving_minutes']
        assert c.post('/api/routes/plan',json=payload(battery=10)).status_code==422
        assert c.post('/api/routes/plan',json=payload(connector='impossible')).status_code==422

def test_recommendations_predictions_and_analytics():
    with TestClient(app) as c:
        r=c.post('/api/recommendations',json={'location':{'lat':12.97,'lon':77.59}}).json()
        assert r['items'];assert all('CCS2' in s['connectors'] for s in r['items'])
        assert r['items']==sorted(r['items'],key=lambda x:x['total_minutes'])
        p=c.post('/api/predictions/wait-time',json={'station_id':'demo-001'}).json();assert len(p['hourly'])==24;assert 'Simulated' in p['source'] or 'Demo' in p['source']
        assert len(c.get('/api/analytics/accessibility').json()['areas'])==12
        assert c.get('/api/analytics/environmental-impact?saved_km=-1').status_code==422
        assert c.get('/api/vehicles').json()

def test_transparent_math():
    assert distance({'lat':0,'lon':0},{'lat':0,'lon':0})==0
    result=impact(10,.2,.5);assert result['energy_saved_kwh']==2;assert result['emissions_avoided_kg']==1
