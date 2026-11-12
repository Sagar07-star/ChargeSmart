# API reference

Complete validated schemas: `/docs`. OpenAPI JSON: `/openapi.json`.

| Method | Path | Behavior |
|---|---|---|
| GET | `/api/health` | Service health and availability capability |
| GET | `/api/stations` | Filters: mode, q, connector, min_power, operator, status, lat, lon, radius. Sort: distance/power. Bounded page/limit. |
| GET | `/api/stations/nearby` | Required lat/lon, demo stations within 20 km |
| GET | `/api/stations/{id}` | Local station or 404 |
| GET | `/api/vehicles` | Sample profiles |
| GET | `/api/locations` | Supported neighborhoods |
| POST | `/api/routes/plan` | Feasible charging chain or 422; live provider failure: 503 |
| POST | `/api/recommendations` | Reachable compatible demo stations, score and category picks |
| POST | `/api/predictions/wait-time` | Synthetic model or explicit rules, hourly series, prediction persistence |
| GET | `/api/analytics/accessibility` | Sample radius/count/nearest-distance coverage |
| GET | `/api/analytics/environmental-impact` | saved_km, efficiency, grid |
| POST | `/api/reports` | Station ID, allowed issue, 5–2000-character description; 201 |
| GET | `/api/reports` | Newest observations; optional station_id; bounded limit |

Route example:

```json
{"start":{"lat":12.9063,"lon":77.5857},"end":{"lat":13.246,"lon":77.711},"capacity":45,"battery":25,"reserve":15,"efficiency":0.16,"connector":"CCS2","max_charge_kw":60,"mode":"demo"}
```

Statuses default to Status Unknown. OCM non-operational flags may show Out of Service with the supplied timestamp. Operational never means unoccupied. No live Available/Occupied feed exists. Reports never overwrite station status. All demo tariffs and station locations are fictional.

OCM process-local cache: 15 minutes. OSRM route cache: 5 minutes. Live OCM requires a backend key. Unavailable live providers produce explicit errors; the user may select labeled Demo mode.
