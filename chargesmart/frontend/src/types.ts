export type Station={id:string;name:string;address:string;lat:number;lon:number;operator:string;power_kw:number;connectors:string[];ports:number;status:string;tariff:number|null;source:string;updated_at:string;distance_km?:number;total_minutes?:number;score?:number;wait_minutes?:number;charging_minutes?:number;cost?:number;explanation?:string};
export type Location={name:string;lat:number;lon:number};
export function usableRange(capacity:number,battery:number,reserve:number,efficiency:number){return Math.max(0,capacity*(battery-reserve)/100/efficiency)}
