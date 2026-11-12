import {MapContainer,TileLayer,CircleMarker,Popup,Polyline,ImageOverlay,useMap} from 'react-leaflet';
import {useEffect,useState} from 'react';
import type {Station} from './types';
import 'leaflet/dist/leaflet.css';
function View({points}:{points:[number,number][]}){const map=useMap();useEffect(()=>{if(points.length)map.fitBounds(points,{padding:[35,35],maxZoom:13})},[map,JSON.stringify(points)]);return null}
export function ChargerMap({stations=[],route=[],selected,onSelect,heat=false}:{stations?:Station[];route?:number[][];selected?:string;onSelect?:(s:Station)=>void;heat?:boolean}){
 const [online,setOnline]=useState(false);
 const pts:[number,number][]=route.length?route.map(c=>[c[1],c[0]]):stations.map(s=>[s.lat,s.lon]);
 return <div className="map-wrap"><label className="online-toggle"><input type="checkbox" checked={online} onChange={e=>setOnline(e.target.checked)}/> Online street map</label><MapContainer center={[12.9716,77.5946]} zoom={11} className="map" scrollWheelZoom>{online?<TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>:<ImageOverlay url="/demo-grid.svg" bounds={[[12.75,77.35],[13.35,77.95]]}/>}<View points={pts}/>{stations.map(s=><CircleMarker key={s.id} center={[s.lat,s.lon]} radius={heat?28:selected===s.id?13:8} pathOptions={{color:heat?'#3b82f6':selected===s.id?'#102d28':'#059669',fillColor:heat?'#3b82f6':'#10b981',fillOpacity:heat?.16:.85,weight:heat?0:3}} eventHandlers={{click:()=>onSelect?.(s)}}><Popup><b>{s.name}</b><br/>{s.power_kw} kW · {s.connectors.join(', ')}<br/>{s.status}<br/>{s.source}</Popup></CircleMarker>)}{route.length>0&&<Polyline positions={pts} pathOptions={{color:'#2465eb',weight:5,dashArray:undefined}}/>}</MapContainer></div>
}
