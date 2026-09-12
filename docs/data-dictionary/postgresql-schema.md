\# PostgreSQL Schema Design



\## Purpose



This document defines the analytical PostgreSQL schema for the

Real-Time Flight Operations \& Aviation Analytics project.



The database stores normalized aircraft observations received from ADSB.lol

and processed by the Python streaming service.



The schema is designed for:



\- Real-time aircraft monitoring

\- Historical aircraft analysis

\- Regional traffic analysis

\- Aircraft type analysis

\- Altitude and speed analysis

\- Power BI reporting

\- Future anomaly detection



\---



\## Database



Database name:



```text

flight\_analytics

