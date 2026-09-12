# Redpanda Topic Design



## Purpose



This document defines the Redpanda topics used by the

Real-Time Flight Operations & Aviation Analytics project.



The project uses Redpanda as the Kafka-compatible event streaming platform.



## Topic 1: aircraft-observations



### Purpose



Stores one event for every aircraft observation collected from ADSB.lol.



### Producer



Python ingestion service.



### Consumers



\- Python stream processor

\- PostgreSQL loader

\- Future analytics services



### Message key



The aircraft `hex` identifier.



### Example message key



```text

7100c3


