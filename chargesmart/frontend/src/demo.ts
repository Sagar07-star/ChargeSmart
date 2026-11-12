import seed from './demo-data.json';
import type {AxiosAdapter} from 'axios';
const rad=(x:number)=>x*Math.PI/180;
export function distance(a:any,b:any){const v=Math.sin(rad(b.lat-a.lat)/2)**2+Math.cos(rad(a.lat))*Math.cos(rad(b.lat))*Math.sin(rad(b.lon-a.lon)/2)**2;return 6371*2*Math.atan2(Math.sqrt(v),Math.sqrt(Math.max(0,1-v)))}
const storage=(key:string)=>JSON.parse(localStorage.getItem(key)||'[]');
const wait=(hour:number,ports:number,occupancy:number)=>Math.round(Math.max(0,occupancy*25+(hour>=17&&hour<=21?12:0)-ports*1.5)*10)/10;
export function browserPlan(p:any){
 if(!(p.capacity>0&&p.efficiency>0&&p.battery>p.reserve&&p.battery<=100&&p.reserve>=0&&p.max_charge_kw>0))throw Error('Check battery, reserve and vehicle parameters.');
 const compatible=seed.stations.filter(s=>s.connectors.includes(p.connector)).sort((x,y)=>distance(p.start,x)+distance(x,p.end)-distance(p.start,y)-distance(y,p.end)).slice(0,18);
 const nodes:any[]=[p.start,...compatible,p.end],target=nodes.length-1,cost=new Map<number,number>([[0,0]]),prev=new Map<number,number>(),done=new Set<number>();
 while(done.size<nodes.length){let i=-1,best=Infinity;for(const [j,c]of cost)if(!done.has(j)&&c<best){i=j;best=c}if(i<0||i===target)break;done.add(i);const energy=p.capacity*((i===0?p.battery:90)-p.reserve)/100;for(let j=1;j<nodes.length;j++){if(i===j)continue;const d=distance(nodes[i],nodes[j])*1.3;if(d*p.efficiency>energy)continue;const dwell=j===target?0:p.capacity*(90-p.reserve)/100/(.9*Math.min(nodes[j].power_kw,p.max_charge_kw))*60;const v=best+d*2+dwell;if(v<(cost.get(j)??Infinity)){cost.set(j,v);prev.set(j,i)}}}
 if(!prev.has(target))throw Error('No feasible charging chain in this sample dataset. Try more battery or a different connector.');
 const path=[target];while(path.at(-1)!==0)path.push(prev.get(path.at(-1)!)!);path.reverse();let soc=p.battery,km=0,charge=0,rupees=0;const stops:any[]=[];
 for(let k=1;k<path.length;k++){const i=path[k-1],j=path[k],d=distance(nodes[i],nodes[j])*1.3;km+=d;soc-=d*p.efficiency/p.capacity*100;if(j!==target){const s=nodes[j],energy=p.capacity*(90-soc)/100,minutes=energy/(.9*Math.min(s.power_kw,p.max_charge_kw))*60,cost=energy/.9*s.tariff;charge+=minutes;rupees+=cost;stops.push({...s,arrival_battery:+soc.toFixed(1),departure_battery:90,charge_minutes:+minutes.toFixed(1),energy_kwh:+energy.toFixed(2),cost:+cost.toFixed(2)});soc=90}}
 const direct=distance(p.start,p.end)*1.3;
 return {distance_km:+km.toFixed(2),driving_minutes:+(km*2).toFixed(1),energy_kwh:+(km*p.efficiency).toFixed(2),arrival_battery:+soc.toFixed(1),charging_minutes:+charge.toFixed(1),total_minutes:+(km*2+charge).toFixed(1),stops,geometry:path.map(i=>[nodes[i].lon,nodes[i].lat]),source:'Browser demo · simulated straight-line × 1.3 at 30 km/h; not navigation',estimated_cost:+rupees.toFixed(2),algorithm:'Dijkstra feasible-leg search, 18 corridor candidates, conservative dwell weights',limitations:'90% departure target and 90% charging efficiency; constant charging power. Traffic, taper, terrain, weather and queues excluded. Range varies with conditions.',comparison:[{name:'Direct baseline',distance_km:+direct.toFixed(2),feasible_without_charge:direct*p.efficiency<=p.capacity*(p.battery-p.reserve)/100},{name:'Charging plan',distance_km:+km.toFixed(2),feasible_without_charge:!stops.length}]}
}
export const demoAdapter:AxiosAdapter=async config=>{
 const url=new URL(config.url||'','http://demo'),q=url.searchParams,path=url.pathname;const p=typeof config.data==='string'?JSON.parse(config.data):config.data||{};let data:any;
 try{
 if(q.get('mode')==='live'||p.mode==='live')throw Error('This hosted browser demo has no server credentials. Run the included FastAPI project for live OCM and OSRM integration.');
 if(path==='/api/health')data={status:'ok',source:'browser demonstration'};
 else if(path==='/api/vehicles')data=seed.vehicles;
 else if(path==='/api/locations')data=seed.locations;
 else if(path==='/api/stations'||path==='/api/stations/nearby'){
 const lat=+(q.get('lat')||12.9716),lon=+(q.get('lon')||77.5946),radius=+(q.get('radius')||200),connector=q.get('connector'),search=(q.get('q')||'').toLowerCase(),operator=q.get('operator'),status=q.get('status');
 const rows=seed.stations.map(s=>({...s,distance_km:distance({lat,lon},s)})).filter(s=>(s.name+' '+s.address).toLowerCase().includes(search)&&(!connector||s.connectors.includes(connector))&&s.power_kw>=+(q.get('min_power')||0)&&(!operator||s.operator===operator)&&(!status||s.status===status)&&s.distance_km<=radius).sort((a,b)=>q.get('sort')==='power'?b.power_kw-a.power_kw:a.distance_km-b.distance_km);
 const page=+(q.get('page')||1),limit=+(q.get('limit')||50);data={items:rows.slice((page-1)*limit,page*limit),total:rows.length,mode:'browser demo'};
 }
 else if(path==='/api/routes/plan')data=browserPlan(p);
 else if(path==='/api/recommendations'){
 const rows=seed.stations.filter(s=>s.connectors.includes(p.connector||'CCS2')).map(s=>{const d=distance(p.location,s)*1.3,battery=p.battery??60,capacity=p.capacity??45,eff=p.efficiency??.16,reserve=p.reserve??15,power=p.max_charge_kw??60;if(d*eff>capacity*(battery-reserve)/100)return null;const arrival=battery-d*eff/capacity*100,energy=Math.max(0,capacity*(80-arrival)/100),charging=energy/(.9*Math.min(s.power_kw,power))*60,w=wait(new Date().getHours(),s.ports,.5),total=d*2+w+charging;return {...s,distance_km:d,total_minutes:+total.toFixed(1),wait_minutes:w,charging_minutes:+charging.toFixed(1),score:+(100/(1+total/30)).toFixed(1),cost:energy/.9*s.tariff,explanation:'Score = 100 / (1 + total minutes / 30). Simulated travel + rule-based wait + estimated charging to 80%.'}}).filter((s):s is NonNullable<typeof s>=>s!==null).sort((a,b)=>a.total_minutes-b.total_minutes);
 data={items:rows,source:'Browser demo · rule-based ranking and rule-based waiting estimates',best:rows[0]?.id,nearest:[...rows].sort((a,b)=>a.distance_km-b.distance_km)[0]?.id,fastest:[...rows].sort((a,b)=>a.charging_minutes-b.charging_minutes)[0]?.id,cheapest:[...rows].sort((a,b)=>a.cost-b.cost)[0]?.id};
 }
 else if(path==='/api/predictions/wait-time'){const s=seed.stations.find(x=>x.id===p.station_id);if(!s)throw Error('Station not found');data={minutes:wait(p.hour??12,s.ports,p.occupancy??.5),source:'Demo estimate · browser rules; trained model requires FastAPI backend',metrics:null,hourly:Array.from({length:24},(_,hour)=>({hour,minutes:wait(hour,s.ports,p.occupancy??.5)}))}}
 else if(path==='/api/analytics/accessibility')data={source:'Simulated stations · illustrative coverage, not demand',formula:'min(100, 12 × stations within 3 km + max(0, 40 − 10 × nearest distance km))',areas:seed.locations.map(a=>{const ds=seed.stations.map(s=>distance(a,s)),near=seed.stations.filter((_,i)=>ds[i]<=3),nearest=Math.min(...ds),score=Math.round(Math.min(100,near.length*12+Math.max(0,40-nearest*10)));return {...a,count:near.length,nearest_km:+nearest.toFixed(2),capacity_kw:near.reduce((n,s)=>n+s.power_kw,0),score,suggestion:score<65?'Limited sample coverage; may warrant further assessment':'Higher sample coverage'}})};
 else if(path==='/api/analytics/environmental-impact'){const km=+(q.get('saved_km')||5),eff=+(q.get('efficiency')||.16),grid=+(q.get('grid')||.7);data={energy_saved_kwh:+(km*eff).toFixed(3),emissions_avoided_kg:+(km*eff*grid).toFixed(3)}}
 else if(path==='/api/reports'){const rows=storage('demo-reports');if(config.method==='post'){if(!seed.stations.some(s=>s.id===p.station_id)||p.description?.length<5)throw Error('Select a station and enter at least five characters.');const row={...p,id:Date.now(),created_at:new Date().toISOString()};localStorage.setItem('demo-reports',JSON.stringify([row,...rows]));data=row}else data={items:rows}}
 else throw Error('Endpoint unavailable in browser demo.');
 return {data,status:200,statusText:'OK',headers:{},config};
 }catch(e){throw new Error(e instanceof Error?e.message:'Demo request failed')}
};
