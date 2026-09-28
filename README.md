# Real-Time Flight Operations & Aviation Analytics

An end-to-end real-time aviation analytics platform that continuously ingests live aircraft data, processes streaming events, stores operational data in PostgreSQL, exposes analytics through a FastAPI backend, and presents interactive insights through a React web application and Power BI dashboards.

---

## Project Overview

**Real-Time Flight Operations & Aviation Analytics** is a portfolio project designed to demonstrate an end-to-end real-time data engineering, analytics, and visualization workflow.

The platform collects live aircraft position data from **ADSB.lol**, publishes observations through **Redpanda**, processes streaming events with Python, stores the results in **PostgreSQL**, exposes analytical APIs through **FastAPI**, and visualizes the data through a **React + Vite** web application and **Power BI**.

The current monitoring configuration covers seven aviation regions across the Gulf:

- Riyadh
- Dammam
- Dubai
- Doha
- Muscat
- Manama
- Kuwait City

Each region uses a **250 nautical mile point-radius monitoring area** centered on the corresponding city coordinates. Therefore, regional counts represent aircraft returned by the ADSB.lol geographic query rather than aircraft physically located within administrative city boundaries.

---

## Objectives

The project was developed to demonstrate the ability to:

- Ingest live aviation data from an external API
- Build a real-time streaming data pipeline
- Publish events using a Kafka-compatible streaming platform
- Process streaming aircraft observations
- Detect and record aviation events
- Store operational and analytical data in PostgreSQL
- Create reusable SQL analytics views
- Build REST APIs for analytical consumption
- Develop an interactive real-time web dashboard
- Connect Power BI directly to the PostgreSQL analytics layer
- Deploy the frontend publicly
- Document a complete end-to-end analytics architecture

---

## Architecture

```text
                         ┌───────────────────────┐
                         │    ADSB / MLAT        │
                         │       NETWORK         │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       ADSB.lol        │
                         │     HTTPS / JSON      │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   Python Producer     │
                         │  Regional Collection  │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       Redpanda        │
                         │ Kafka-Compatible      │
                         │    Event Streaming    │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Python Stream         │
                         │     Processor         │
                         │ Events & Processing   │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │      PostgreSQL       │
                         │ Operational +         │
                         │ Analytics Data        │
                         └───────┬─────────┬─────┘
                                 │         │
                     ┌───────────┘         └────────────┐
                     ▼                                  ▼
           ┌───────────────────────┐          ┌───────────────────────┐
           │       FastAPI         │          │      Power BI         │
           │      REST API         │          │    Live Analytics     │
           └───────────┬───────────┘          └───────────────────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │    React + Vite       │
           │ Interactive Dashboard │
           └───────────────────────┘

Technology Stack
Layer	Technology
Data Source	ADSB.lol
Programming	Python
Streaming	Redpanda
Database	PostgreSQL 16
API	FastAPI
Frontend	React
Build Tool	Vite
Charts	Recharts
Maps	Leaflet / React Leaflet
BI	Power BI Desktop
Containerization	Docker / Docker Compose
Version Control	Git / GitHub
Development	Visual Studio Code
Public Frontend	Netlify
API Tunnel	Cloudflare Quick Tunnel


Regional Monitoring
The producer currently monitors seven regions:
Region	Country	Center Latitude	Center Longitude	Radius
Riyadh	Saudi Arabia	24.7136	46.6753	250 NM
Dammam	Saudi Arabia	26.4207	50.0888	250 NM
Dubai	United Arab Emirates	25.2048	55.2708	250 NM
Doha	Qatar	25.2854	51.5310	250 NM
Muscat	Oman	23.5880	58.3829	250 NM
Manama	Bahrain	26.2235	50.5876	250 NM
Kuwait City	Kuwait	29.3759	47.9774	250 NM


Regional Query Model
Each region is represented by a geographic point and a 250 nautical mile radius.
For example:
Riyadh
Latitude:  24.7136
Longitude: 46.6753
Radius:    250 NM

The system sends regional requests to ADSB.lol and processes the aircraft returned by those geographic queries.
Data Pipeline
1. Data Ingestion
The Python producer requests live aircraft snapshots from ADSB.lol for each configured region.
The producer:
- Requests aircraft data
- Processes regional snapshots
- Tracks the current pipeline run
- Publishes aircraft observations to Redpanda
- Records received, published, skipped, and duplicate observations
- Repeats the collection cycle continuously
Example pipeline logging:
Configured regions:
riyadh, dammam, dubai, doha, muscat, manama, kuwait_city

Region polling interval:
60 seconds

2. Event Streaming
Aircraft observations are published to Redpanda using a Kafka-compatible event streaming architecture.
The streaming layer provides a decoupled connection between:
Producer
   ↓
Redpanda
   ↓
Stream Processor

This allows the producer and processor to operate independently while continuously exchanging aircraft events.
3. Stream Processing
The Python stream processor consumes aircraft observations from Redpanda and processes the incoming stream.
The processor is responsible for:
- Consuming aircraft observations
- Processing live aircraft positions
- Registering aircraft
- Generating aviation events
- Writing processed data to PostgreSQL
- Maintaining pipeline run tracking
4. PostgreSQL Storage
PostgreSQL provides the persistent data layer for the platform.
The database contains aviation schemas for operational data and analytical views for dashboard consumption.
Core database objects include:
aviation
├── fact_aircraft_position
├── fact_aviation_event
└── dim_region

analytics
├── v_current_run
├── v_aircraft_summary
├── v_current_aircraft
├── v_event_summary
├── v_recent_events
├── v_region_movements
├── v_regional_traffic_summary
└── v_traffic_timeseries

Pipeline Run Tracking
The platform uses a run_id to distinguish the current pipeline execution from previous historical runs.
Example:
RUN_20260928_171332_403278

Run tracking is stored in the aircraft position and aviation event fact tables.
The current run is identified through:
CREATE OR REPLACE VIEW analytics.v_current_run AS
SELECT MAX(run_id) AS run_id
FROM aviation.fact_aircraft_position
WHERE run_id IS NOT NULL;

Analytics views use the current pipeline run to ensure that the dashboards display the active operational dataset.
Database Schema
Aviation Schema
The main operational schema contains:
aviation.fact_aircraft_position
aviation.fact_aviation_event
aviation.dim_region

Analytics Schema
The analytics layer contains reusable views designed for API and BI consumption.
Examples include:
analytics.v_aircraft_summary
analytics.v_current_aircraft
analytics.v_event_summary
analytics.v_recent_events
analytics.v_region_movements
analytics.v_regional_traffic_summary
analytics.v_traffic_timeseries

This separation allows the application and BI layers to consume prepared analytical datasets instead of repeatedly querying raw operational tables.
FastAPI Backend
The project includes a FastAPI backend that exposes aviation analytics through REST endpoints.
API Base URL
http://127.0.0.1:8001

Available Endpoints
GET /api/overview
GET /api/aircraft
GET /api/aircraft/summary
GET /api/events
GET /api/regional
GET /api/timeseries
GET /api/database

Regional Endpoint
GET /api/regional

The endpoint returns regional operational statistics for the current pipeline run.
Example response structure:
{
  "count": 7,
  "data": [
    {
      "region_code": "dubai",
      "position_count": 121,
      "unique_aircraft": 121
    },
    {
      "region_code": "muscat",
      "position_count": 99,
      "unique_aircraft": 99
    }
  ]
}

The actual values change continuously as new aircraft observations are ingested.
React Web Application
The frontend is built using React and Vite.
Local development URL:
http://localhost:5174/

Public frontend:
https://real-time-flight-operations.netlify.app/

Dashboard Pages
The application contains five primary analytical sections:
1. Overview
Provides a high-level operational view of the aviation monitoring platform.
Key information includes:
- Current aircraft activity
- Regional traffic
- Aviation events
- Operational KPIs
- Live system status
2. Live Operations
Provides real-time aircraft monitoring.
Features include:
- Live aircraft positions
- Interactive map
- Aircraft distribution
- Regional activity
- Operational information
3. Regional Traffic
Provides regional comparisons across the seven monitored areas.
Regions displayed:
Riyadh
Dammam
Dubai
Doha
Muscat
Manama
Kuwait City

The page uses live API data from PostgreSQL.
4. Events & Anomalies
Displays aviation events generated by the streaming processing layer.
This section is designed to provide visibility into operational events and detected conditions within the streaming dataset.
5. Aircraft Analytics
Provides aircraft-level analytical information and operational summaries.
The page uses processed aircraft data exposed through the FastAPI backend.
Power BI
The project also includes a Power BI Desktop dashboard connected to the PostgreSQL analytics layer.
Power BI provides an additional BI interface for analyzing the real-time aviation dataset.
The Power BI project contains four analytical dashboards.
The Power BI file is located at:
powerbi/
└── Real-Time Flight Operations & Aviation Analytics.pbix

The PostgreSQL container exposes port 5433 on the host for local Power BI connectivity:
Host: localhost
Port: 5433
Database: aviation

Inside the Docker network, PostgreSQL continues to use:
postgres:5432

Docker Deployment
The project uses Docker Compose to run the backend infrastructure.
Deployment configuration:
docker/docker-compose.deploy.yml

Main services:
redpanda
producer
postgres
api
processor

Service Architecture
┌───────────────────────────────────────────────┐
│                 Docker Compose                │
│                                               │
│  ┌───────────┐       ┌───────────┐            │
│  │ Producer  │──────▶│ Redpanda  │            │
│  └───────────┘       └─────┬─────┘            │
│                             │                  │
│                             ▼                  │
│                     ┌──────────────┐           │
│                     │  Processor   │           │
│                     └──────┬───────┘           │
│                            │                   │
│                            ▼                   │
│                     ┌──────────────┐           │
│                     │  PostgreSQL  │           │
│                     └──────┬───────┘           │
│                            │                   │
│                            ▼                   │
│                     ┌──────────────┐           │
│                     │   FastAPI    │           │
│                     └──────────────┘           │
└───────────────────────────────────────────────┘

Docker Ports
Service	Container Port	Host Port
FastAPI	8000	8001
PostgreSQL	5432	5433
Redpanda	9092	Internal Docker network


The producer, processor, API, and PostgreSQL services communicate through the Docker Compose network.
Project Structure
Real-Time Flight Operations & Aviation Analytics/
│
├── backend/
│   └── main.py
│
├── database/
│   ├── 01_create_schema.sql
│   ├── 02_add_run_tracking.sql
│   ├── 03_create_analytics_views.sql
│   └── 04_seed_muscat.sql
│
├── docker/
│   ├── .env
│   ├── docker-compose.deploy.yml
│   └── docker-compose.yml
│
├── docs/
│   ├── architecture/
│   ├── data-dictionary/
│   │   ├── postgresql-schema.md
│   │   ├── raw-event-schema.md
│   │   └── redpanda-topics.md
│   └── screenshots/
│
├── frontend/
│   ├── .env
│   ├── .env.example
│   ├── .env.local
│   ├── .gitignore
│   ├── .oxlintrc.json
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── README.md
│   ├── vite.config.js
│   └── dist/
│
├── ingestion/
│   ├── __init__.py
│   ├── adsb_client.py
│   ├── config.py
│   └── postgres_loader.py
│
├── processing/
│   └── aircraft_stream_processor.py
│
├── streaming/
│   ├── __init__.py
│   └── aircraft_producer.py
│
├── tests/
│
├── powerbi/
│   └── Real-Time Flight Operations & Aviation Analytics.pbix
│
├── Dockerfile
├── README.md
├── requirements.txt
├── .env
└── .env.example

Configuration
The project uses environment variables for configuration.
Example environment configuration:
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=aviation
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

REDPANDA_BOOTSTRAP_SERVERS=redpanda:9092

Do not commit real credentials or sensitive environment variables to GitHub.
Use:
.env

for local secrets and:
.env.example

as a configuration template.
Local Setup
1. Clone the Repository
git clone https://github.com/abdullahahmadd/real-time-flight-operations-aviation-analytics.git

Navigate into the project:
cd real-time-flight-operations-aviation-analytics

2. Configure Environment Variables
Create or update the required environment configuration:
.env

and:
docker/.env

Use .env.example files as references where available.
3. Start Docker Services
From the project root:
docker compose --env-file docker/.env -f docker/docker-compose.deploy.yml up -d

Check running containers:
docker compose --env-file docker/.env -f docker/docker-compose.deploy.yml ps

Expected services:
redpanda
producer
postgres
api
processor

4. Check Producer Logs
docker logs flight-analytics-deploy-producer-1

The producer should report the configured regions:
Configured regions:
riyadh, dammam, dubai, doha, muscat, manama, kuwait_city

5. Check Stream Processor Logs
docker logs flight-analytics-deploy-processor-1

The processor should establish connections to:
Redpanda
PostgreSQL

and begin consuming aircraft observations.
6. Check API
Open:
http://127.0.0.1:8001/api/overview

Regional analytics:
http://127.0.0.1:8001/api/regional

Aircraft data:
http://127.0.0.1:8001/api/aircraft

Events:
http://127.0.0.1:8001/api/events

Running the Frontend
Navigate to the frontend:
cd frontend

Install dependencies:
npm install

Start the development server:
npm run dev

The application should be available at:
http://localhost:5174/

Production Build
To create a production build:
npm run build

The generated files are placed in:
frontend/dist/

Public Deployment
The React frontend is publicly deployed through Netlify:
https://real-time-flight-operations.netlify.app/

The frontend communicates with the FastAPI backend through the configured API URL.
For local development, the API runs on:
http://127.0.0.1:8001

Cloudflare Quick Tunnel
A Cloudflare Quick Tunnel can be used to expose the local FastAPI service for temporary public access.
Example:
cloudflared tunnel --url http://127.0.0.1:8001

The generated URL is temporary and changes when a new Quick Tunnel is created.
Important
Cloudflare Quick Tunnel is intended for development/demo access rather than permanent production API hosting.
The original cloudflared process must remain running while the public API endpoint is required.
API and Data Flow
The complete live data flow is:
ADSB.lol
   │
   │ HTTPS / JSON
   ▼
Python Producer
   │
   │ aircraft-observations
   ▼
Redpanda
   │
   ▼
Python Stream Processor
   │
   ├── Aircraft Positions
   ├── Aviation Events
   └── Run Tracking
   │
   ▼
PostgreSQL
   │
   ├── Operational Tables
   └── Analytics Views
   │
   ├───────────────┐
   ▼               ▼
FastAPI         Power BI
   │
   ▼
React Dashboard

Current Pipeline Validation
The seven-region configuration has been validated across ingestion and producer configuration.
Current configured regions:
riyadh
dammam
dubai
doha
muscat
manama
kuwait_city

The ingestion and producer configurations match:
INGESTION:
['riyadh', 'dammam', 'dubai', 'doha', 'muscat', 'manama', 'kuwait_city']

PRODUCER:
['riyadh', 'dammam', 'dubai', 'doha', 'muscat', 'manama', 'kuwait_city']

MATCH:
True

The /api/regional endpoint returns:
{
  "count": 7
}

confirming that the API currently exposes all seven configured regions.
Example Streaming Cycle
A typical producer cycle follows this pattern:
Starting collection cycle for region riyadh
        ↓
Fetch aircraft snapshot
        ↓
Publish aircraft observations
        ↓
Starting collection cycle for region dammam
        ↓
Fetch aircraft snapshot
        ↓
Publish aircraft observations
        ↓
...
        ↓
Starting collection cycle for region kuwait_city

The producer reports:
received
published
skipped
duplicates

for each region.
Key Analytics
The platform supports analysis of:
Aircraft Operations
- Aircraft counts
- Unique aircraft
- Aircraft positions
- Aircraft movement
- Regional aircraft activity
Regional Traffic
- Regional aircraft volume
- Unique aircraft by region
- Traffic distribution
- Regional movement activity
- Traffic time series
Events
- Aviation event counts
- Recent events
- Event summaries
- Operational event monitoring
System Operations
- Pipeline run tracking
- Current pipeline state
- Database connectivity
- Streaming pipeline status
- API availability
Data Quality and Current-Run Isolation
The project uses a dedicated run_id to prevent dashboards from mixing data from different pipeline executions.
This provides a clear separation between:
Historical pipeline runs

and:
Current active pipeline run

Analytics views reference the current run so that the operational dashboards remain focused on the active streaming session.
Git Workflow
The project uses Git for version control.
Check repository status:
git status

Add changes:
git add .

Commit changes:
git commit -m "Update aviation analytics project"

Push changes:
git push origin main

Repository
GitHub:
https://github.com/abdullahahmadd/real-time-flight-operations-aviation-analytics
Live Dashboard
Public frontend:
https://real-time-flight-operations.netlify.app/
Author
Abdullah Ahmad
Data Analytics | Business Intelligence | Data Engineering | Software Engineering
LinkedIn:
https://www.linkedin.com/in/aabdullah-ahmad/
GitHub:
https://github.com/abdullahahmadd
Project Status
The project currently provides:
- Live aircraft data ingestion
- Seven-region aviation monitoring
- Redpanda streaming
- Python stream processing
- PostgreSQL storage
- Current-run tracking
- Aviation event processing
- FastAPI analytics endpoints
- React interactive dashboard
- Live regional traffic monitoring
- Interactive aircraft operations view
- Events and anomaly dashboard
- Aircraft analytics dashboard
- Power BI analytics dashboards
- Docker-based deployment
- Public frontend deployment
The platform is structured as an end-to-end real-time aviation analytics solution combining data ingestion, streaming, processing, database engineering, API development, business intelligence, and interactive visualization.
```
