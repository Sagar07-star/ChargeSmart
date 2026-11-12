from math import radians,sin,cos,atan2,sqrt

def distance(a,b):
    p,q=radians(a['lat']),radians(b['lat'])
    dp=q-p; dl=radians(b['lon']-a['lon'])
    v=sin(dp/2)**2+cos(p)*cos(q)*sin(dl/2)**2
    return 6371*2*atan2(sqrt(v),sqrt(max(0,1-v)))

def impact(km,efficiency=.16,grid=.7):
    return {'distance_saved_km':round(km,2),'energy_saved_kwh':round(km*efficiency,3),'emissions_avoided_kg':round(km*efficiency*grid,3),'assumptions':{'kwh_per_km':efficiency,'kg_co2e_per_kwh':grid},'source':'hypothetical scenario, not verified savings'}
