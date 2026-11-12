import heapq
from fastapi import HTTPException
from .energy import distance
from ..integrations.maps import route

async def plan_trip(req,stations):
    a=req.start.model_dump();b=req.end.model_dump()
    base=await route(a,b,req.mode)
    usable=req.capacity*(req.battery-req.reserve)/100
    if base['distance_km']*req.efficiency<=usable:
        return finish(req,base,[],base['distance_km'],base['duration_minutes'],req.battery-base['distance_km']*req.efficiency/req.capacity*100,0)
    # Directed graph: start has initial usable energy; stations depart at 90%.
    # Edges are exact OSRM roads in live mode, simulated distances only in demo.
    compatible=[s for s in stations if req.connector in s['connectors'] and s['status']!='Out of Service']
    # Keep corridor candidates to bound external calls. Report candidate limit explicitly.
    compatible.sort(key=lambda s:distance(a,s)+distance(s,b))
    candidates=compatible[:18]
    nodes=[a]+candidates+[b];target=len(nodes)-1
    cache={};cost={0:0};prev={};queue=[(0,0)]
    while queue:
        value,i=heapq.heappop(queue)
        if value!=cost[i]:continue
        if i==target:break
        energy=usable if i==0 else req.capacity*(.90-req.reserve/100)
        for j in range(1,len(nodes)):
            if i==j:continue
            if distance(nodes[i],nodes[j])*req.efficiency>energy:continue
            leg=await route(nodes[i],nodes[j],req.mode);cache[i,j]=leg
            used=leg['distance_km']*req.efficiency
            if used>energy:continue
            # Conservative dwell charges arrival from reserve up to 90%; later refined on chosen path.
            dwell=0 if j==target else req.capacity*(.90-req.reserve/100)/(.9*min(nodes[j]['power_kw'],req.max_charge_kw))*60
            new=value+leg['duration_minutes']+dwell
            if new<cost.get(j,float('inf')):
                cost[j]=new;prev[j]=i;heapq.heappush(queue,(new,j))
    if target not in prev:raise HTTPException(422,'No feasible charging chain in the available station set. Increase battery, change connector, or use a shorter trip. Coverage is limited to fetched candidates.')
    path=[target]
    while path[-1]!=0:path.append(prev[path[-1]])
    path.reverse();geometry=[];stops=[];dist=drive=charge=0;soc=req.battery;cost_rupees=0
    for i,j in zip(path,path[1:]):
        leg=cache[i,j];geometry+=leg['geometry'];dist+=leg['distance_km'];drive+=leg['duration_minutes'];soc-=leg['distance_km']*req.efficiency/req.capacity*100
        if j!=target:
            s=nodes[j];energy=req.capacity*(90-soc)/100;minutes=energy/(.9*min(s['power_kw'],req.max_charge_kw))*60
            charge+=minutes;price=energy/.9*s['tariff'] if s['tariff'] is not None else None
            cost_rupees=cost_rupees+price if price is not None and cost_rupees is not None else None
            stops.append({**s,'arrival_battery':round(soc,1),'departure_battery':90,'charge_minutes':round(minutes,1),'energy_kwh':round(energy,2),'cost':round(price,2) if price is not None else None});soc=90
    base['geometry']=geometry
    out=finish(req,base,stops,dist,drive,soc,charge);out['estimated_cost']=round(cost_rupees,2) if cost_rupees is not None else None
    out['candidate_limit']=18;return out

def finish(req,base,stops,dist,drive,soc,charge):
    return {'distance_km':round(dist,2),'driving_minutes':round(drive,1),'energy_kwh':round(dist*req.efficiency,2),'arrival_battery':round(soc,1),'charging_minutes':round(charge,1),'total_minutes':round(drive+charge,1),'stops':stops,'geometry':base['geometry'],'source':base['source'],'estimated_cost':0,'algorithm':'Dijkstra over feasible charging legs with conservative dwell weights; not globally optimal','limitations':'90% departure target, 90% charging efficiency, constant average charger power; no traffic, taper, weather, terrain or queue guarantees. Range varies with conditions.','comparison':[{'name':'Direct baseline','distance_km':round(base['distance_km'],2),'feasible_without_charge':not stops},{'name':'Charging plan','distance_km':round(dist,2),'feasible_without_charge':not stops}]}
