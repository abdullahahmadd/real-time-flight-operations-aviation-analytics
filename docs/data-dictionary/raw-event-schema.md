# Raw Aviation Event Schema



## Purpose



This document defines the normalized event structure produced by the ADSB.lol

ingestion service and published to Redpanda.



The project uses one event per aircraft observation.



## Event Structure



```json

{

&#x20; event\_metadata: {

&#x20;   event\_id: uuid,

&#x20;   observed\_at: UTC timestamp,

&#x20;   source: adsb.lol,

&#x20;   source\_region: riyadh,

&#x20;   api\_endpoint: https://api.adsb.lol/v2/point/24.7136/46.6753/250

&#x20; },

&#x20; source\_metadata: {

&#x20;   api\_now: 1789228581501,

&#x20;   api\_ctime: 1789228581501,

&#x20;   api\_ptime: 0,

&#x20;   snapshot\_total: 5,

&#x20;   snapshot\_messages: 2622,

&#x20;   api\_message: No error

&#x20; },

&#x20; aircraft\_data: {

&#x20;   hex: 7100c3,

&#x20;   flight: FAD452,

&#x20;   registration: HZ-FAL,

&#x20;   aircraft\_type: A20N,

&#x20;   latitude: 25.1987,

&#x20;   longitude: 46.039386,

&#x20;   altitude\_baro\_raw: 34975,

&#x20;   altitude\_baro\_feet: 34975,

&#x20;   altitude\_geom: 37350,

&#x20;   ground\_speed: 477.5,

&#x20;   track: 58.71,

&#x20;   vertical\_rate: -42,

&#x20;   category: A3,

&#x20;   squawk: 2503,

&#x20;   emergency: none,

&#x20;   seen\_seconds: 0.3,

&#x20;   messages: 357,

&#x20;   rssi: -32.3,

&#x20;   source\_type: adsb\_icao,

&#x20;   nic: 8,

&#x20;   nac\_p: 9,

&#x20;   nac\_v: 2,

&#x20;   sil: 3

&#x20; },

&#x20; raw\_data\_quality: {

&#x20;   is\_on\_ground: false,

&#x20;   has\_position: true,

&#x20;   has\_callsign: true,

&#x20;   has\_registration: true,

&#x20;   has\_altitude: true,

&#x20;   has\_speed: true

&#x20; }

}


