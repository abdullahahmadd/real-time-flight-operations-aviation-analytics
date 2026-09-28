# ✈️ Real-Time Flight Operations & Aviation Analytics

<p align="center">
  <a href="https://real-time-flight-operations.netlify.app/"><img src="https://img.shields.io/badge/Live%20Demo-Netlify-00C7B7?style=for-the-badge&logo=netlify&logoColor=white" alt="Live Demo"></a>
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Data-Real--Time-blue?style=for-the-badge" alt="Real-Time">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Redpanda-E2401B?style=flat-square&logo=redpanda&logoColor=white" alt="Redpanda">
  <img src="https://img.shields.io/badge/PostgreSQL_16-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/Leaflet-199900?style=flat-square&logo=leaflet&logoColor=white" alt="Leaflet">
  <img src="https://img.shields.io/badge/Recharts-22B5BF?style=flat-square" alt="Recharts">
  <img src="https://img.shields.io/badge/Power_BI-F2C811?style=flat-square&logo=powerbi&logoColor=black" alt="Power BI">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Netlify-00C7B7?style=flat-square&logo=netlify&logoColor=white" alt="Netlify">
  <img src="https://img.shields.io/badge/Cloudflare-F38020?style=flat-square&logo=cloudflare&logoColor=white" alt="Cloudflare">
  <img src="https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white" alt="Git">
</p>

<p align="center">
  <a href="https://github.com/abdullahahmadd/real-time-flight-operations-aviation-analytics"><img src="https://img.shields.io/github/stars/abdullahahmadd/real-time-flight-operations-aviation-analytics?style=flat-square&logo=github" alt="Stars"></a>
  <a href="https://github.com/abdullahahmadd/real-time-flight-operations-aviation-analytics/commits/main"><img src="https://img.shields.io/github/last-commit/abdullahahmadd/real-time-flight-operations-aviation-analytics?style=flat-square&logo=github" alt="Last Commit"></a>
  <a href="https://github.com/abdullahahmadd/real-time-flight-operations-aviation-analytics"><img src="https://img.shields.io/github/repo-size/abdullahahmadd/real-time-flight-operations-aviation-analytics?style=flat-square&logo=github" alt="Repo Size"></a>
</p>

An end-to-end real-time aviation analytics platform that continuously ingests live aircraft data, processes streaming events, stores operational data in PostgreSQL, exposes analytics through a FastAPI backend, and presents interactive insights through a React web application and Power BI dashboards.

---

## 📑 Table of Contents

- [Project Overview](#-project-overview)
- [Objectives](#-objectives)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Regional Monitoring](#-regional-monitoring)
- [Data Pipeline](#-data-pipeline)
- [Database Schema](#-database-schema)
- [FastAPI Backend](#-fastapi-backend)
- [React Web Application](#-react-web-application)
- [Power BI](#-power-bi)
- [Docker Deployment](#-docker-deployment)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Getting Started](#-getting-started)
- [Public Deployment](#-public-deployment)
- [Key Analytics](#-key-analytics)
- [Data Quality & Current-Run Isolation](#-data-quality--current-run-isolation)
- [Git Workflow](#-git-workflow)
- [Project Status](#-project-status)
- [Author](#-author)

---

## 📌 Project Overview

**Real-Time Flight Operations & Aviation Analytics** is a portfolio project that demonstrates an end-to-end real-time data engineering, analytics, and visualization workflow.

The platform collects live aircraft position data from **ADSB.lol**, publishes observations through **Redpanda**, processes streaming events with Python, stores the results in **PostgreSQL**, exposes analytical APIs through **FastAPI**, and visualizes the data through a **React + Vite** web application and **Power BI**.

The current monitoring configuration covers **seven aviation regions** across the Gulf:

`Riyadh` · `Dammam` · `Dubai` · `Doha` · `Muscat` · `Manama` · `Kuwait City`

> [!NOTE]
> Each region uses a **250 nautical mile point-radius monitoring area** centered on the corresponding city coordinates. Regional counts therefore represent aircraft returned by the ADSB.lol geographic query, **not** aircraft physically located within administrative city boundaries.

---

## 🎯 Objectives

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

## 🏗️ Architecture

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
                         │   Kafka-Compatible    │
                         │    Event Streaming    │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │    Python Stream      │
                         │      Processor        │
                         │  Events & Processing  │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │      PostgreSQL       │
                         │     Operational +     │
                         │    Analytics Data     │
                         └───────┬─────────┬─────┘
                                 │         │
                     ┌───────────┘         └────────────┐
                     ▼                                  ▼
           ┌───────────────────────┐          ┌───────────────────────┐
           │       FastAPI         │          │       Power BI        │
           │       REST API        │          │    Live Analytics     │
           └───────────┬───────────┘          └───────────────────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │     React + Vite      │
           │  Interactive Dashboard│
           └───────────────────────┘
```

---

## 🧰 Technology Stack

| Layer | Technology |
|-------|------------|
| Data Source | ADSB.lol |
| Programming | Python |
| Streaming | Redpanda |
| Database | PostgreSQL 16 |
| API | FastAPI |
| Frontend | React |
| Build Tool | Vite |
| Charts | Recharts |
| Maps | Leaflet / React Leaflet |
| BI | Power BI Desktop |
| Containerization | Docker / Docker Compose |
| Version Control | Git / GitHub |
| Development | Visual Studio Code |
| Public Frontend | Netlify |
| API Tunnel | Cloudflare Quick Tunnel |

---

## 🌍 Regional Monitoring

The producer currently monitors seven regions:

| Region | Country | Center Latitude | Center Longitude | Radius |
|--------|---------|-----------------|------------------|--------|
| Riyadh | Saudi Arabia | 24.7136 | 46.6753 | 250 NM |
| Dammam | Saudi Arabia | 26.4207 | 50.0888 | 250 NM |
| Dubai | United Arab Emirates | 25.2048 | 55.2708 | 250 NM |
| Doha | Qatar | 25.2854 | 51.5310 | 250 NM |
| Muscat | Oman | 23.5880 | 58.3829 | 250 NM |
| Manama | Bahrain | 26.2235 | 50.5876 | 250 NM |
| Kuwait City | Kuwait | 29.3759 | 47.9774 | 250 NM |

### Regional Query Model

Each region is represented by a geographic point and a 250 nautical mile radius. For example:

```text
Riyadh
Latitude:  24.7136
Longitude: 46.6753
Radius:    250 NM
```

The system sends regional requests to ADSB.lol and processes the aircraft returned by those geographic queries.

---

## 🔄 Data Pipeline

### 1. Data Ingestion

The Python producer requests live aircraft snapshots from ADSB.lol for each configured region. The producer:

- Requests aircraft data
- Processes regional snapshots
- Tracks the current pipeline run
- Publishes aircraft observations to Redpanda
- Records received, published, skipped, and duplicate observations
- Repeats the collection cycle continuously

Example pipeline logging:

```text
Configured regions:
riyadh, dammam, dubai, doha, muscat, manama, kuwait_city

Region polling interval:
60 seconds
```

A typical producer cycle:

```text
Starting collection cycle for region riyadh
        ↓
Fetch aircraft snapshot
        ↓
Publish aircraft observations
        ↓
Starting collection cycle for region dammam
        ↓
...
        ↓
Starting collection cycle for region kuwait_city
```

For each region the producer reports `received`, `published`, `skipped`, and `duplicates`.

### 2. Event Streaming

Aircraft observations are published to Redpanda using a Kafka-compatible event streaming architecture, providing a decoupled connection between the producer and the stream processor:

```text
Producer → Redpanda → Stream Processor
```

This allows both components to operate independently while continuously exchanging aircraft events.

### 3. Stream Processing

The Python stream processor consumes aircraft observations from Redpanda and is responsible for:

- Consuming aircraft observations
- Processing live aircraft positions
- Registering aircraft
- Generating aviation events
- Writing processed data to PostgreSQL
- Maintaining pipeline run tracking

### 4. PostgreSQL Storage

PostgreSQL provides the persistent data layer, containing schemas for operational data and analytical views for dashboard consumption.

### Complete Data Flow

```text
ADSB.lol
   │  HTTPS / JSON
   ▼
Python Producer
   │  aircraft-observations
   ▼
Redpanda
   ▼
Python Stream Processor
   ├── Aircraft Positions
   ├── Aviation Events
   └── Run Tracking
   ▼
PostgreSQL
   ├── Operational Tables
   └── Analytics Views
   ├───────────────┐
   ▼               ▼
FastAPI         Power BI
   ▼
React Dashboard
```

---

## 🗄️ Database Schema

```text
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
```

- **`aviation` schema** — operational tables for aircraft positions, aviation events, and region dimensions.
- **`analytics` schema** — reusable views designed for API and BI consumption, so the application and BI layers use prepared datasets instead of repeatedly querying raw operational tables.

### Pipeline Run Tracking

The platform uses a `run_id` to distinguish the current pipeline execution from previous historical runs.

```text
RUN_20260928_171332_403278
```

Run tracking is stored in the aircraft position and aviation event fact tables. The current run is identified through:

```sql
CREATE OR REPLACE VIEW analytics.v_current_run AS
SELECT MAX(run_id) AS run_id
FROM aviation.fact_aircraft_position
WHERE run_id IS NOT NULL;
```

Analytics views use the current pipeline run to ensure dashboards display the active operational dataset.

---

## ⚡ FastAPI Backend

The FastAPI backend exposes aviation analytics through REST endpoints.

**Base URL (local Docker):** `http://127.0.0.1:8001`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/overview` | High-level KPIs for the current run |
| GET | `/api/aircraft` | Current aircraft positions |
| GET | `/api/aircraft/summary` | Aircraft-level analytical summaries |
| GET | `/api/events` | Recent aviation events |
| GET | `/api/regional` | Regional operational statistics |
| GET | `/api/timeseries` | Traffic time series |
| GET | `/api/database` | Database connectivity status |

### Regional Endpoint

`GET /api/regional` returns regional operational statistics for the current pipeline run:

```json
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
```

Actual values change continuously as new aircraft observations are ingested.

---

## 🖥️ React Web Application

Built with React and Vite. The frontend polls the API every 2 seconds for live updates.

- **Local development:** http://localhost:5174/
- **Public frontend:** https://real-time-flight-operations.netlify.app/

### Dashboard Pages

| Page | Description |
|------|-------------|
| **Overview** | High-level operational view: current aircraft activity, regional traffic, aviation events, operational KPIs, and live system status |
| **Live Operations** | Real-time aircraft monitoring: live aircraft positions, interactive map, aircraft distribution, regional activity, and operational information |
| **Regional Traffic** | Regional comparisons across the seven monitored areas, powered by live PostgreSQL data |
| **Events & Anomalies** | Aviation events generated by the streaming processing layer, giving visibility into detected operational conditions |
| **Aircraft Analytics** | Aircraft-level analytical information and operational summaries from the FastAPI backend |

### Interface Highlights

- Interactive Leaflet map with live aircraft positions
- Dark / light theme toggle
- Live UTC (Zulu) clock and connection status indicator
- Sortable and searchable data tables
- Aircraft detail drawer for drill-down
- Severity-coded event log
- Responsive layout with mobile navigation

---

## 📊 Power BI

The project also includes a Power BI Desktop dashboard connected to the PostgreSQL analytics layer, providing an additional BI interface for analyzing the real-time aviation dataset. The Power BI project contains **four analytical dashboards**.

**File location:**

```text
powerbi/
└── Real-Time Flight Operations & Aviation Analytics.pbix
```

**PostgreSQL connection for Power BI (local):**

```text
Host:     localhost
Port:     5433
Database: aviation
```

Inside the Docker network, PostgreSQL continues to use `postgres:5432`.

---

## 🐳 Docker Deployment

Docker Compose runs the backend infrastructure. Deployment configuration: `docker/docker-compose.deploy.yml`

**Main services:** `redpanda` · `producer` · `postgres` · `api` · `processor`

```text
┌───────────────────────────────────────────────┐
│                 Docker Compose                │
│                                               │
│  ┌───────────┐       ┌───────────┐            │
│  │ Producer  │──────▶│ Redpanda  │            │
│  └───────────┘       └─────┬─────┘            │
│                            │                  │
│                            ▼                  │
│                     ┌──────────────┐          │
│                     │  Processor   │          │
│                     └──────┬───────┘          │
│                            │                  │
│                            ▼                  │
│                     ┌──────────────┐          │
│                     │  PostgreSQL  │          │
│                     └──────┬───────┘          │
│                            │                  │
│                            ▼                  │
│                     ┌──────────────┐          │
│                     │   FastAPI    │          │
│                     └──────────────┘          │
└───────────────────────────────────────────────┘
```

### Docker Ports

| Service | Container Port | Host Port |
|---------|----------------|-----------|
| FastAPI | 8000 | 8001 |
| PostgreSQL | 5432 | 5433 |
| Redpanda | 9092 | Internal Docker network |

The producer, processor, API, and PostgreSQL services communicate through the Docker Compose network.

---

## 📁 Project Structure

```text
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
```

---

## ⚙️ Configuration

The project uses environment variables. Example:

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=aviation
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

REDPANDA_BOOTSTRAP_SERVERS=redpanda:9092
```

> [!WARNING]
> Do not commit real credentials or sensitive environment variables to GitHub. Use `.env` for local secrets and `.env.example` as a configuration template.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/abdullahahmadd/real-time-flight-operations-aviation-analytics.git
cd real-time-flight-operations-aviation-analytics
```

### 2. Configure Environment Variables

Create or update `.env` and `docker/.env`, using the `.env.example` files as references where available.

### 3. Start Docker Services

From the project root:

```bash
docker compose --env-file docker/.env -f docker/docker-compose.deploy.yml up -d
```

Check running containers:

```bash
docker compose --env-file docker/.env -f docker/docker-compose.deploy.yml ps
```

Expected services: `redpanda`, `producer`, `postgres`, `api`, `processor`.

### 4. Check Producer Logs

```bash
docker logs flight-analytics-deploy-producer-1
```

The producer should report the configured regions:

```text
Configured regions:
riyadh, dammam, dubai, doha, muscat, manama, kuwait_city
```

### 5. Check Stream Processor Logs

```bash
docker logs flight-analytics-deploy-processor-1
```

The processor should connect to Redpanda and PostgreSQL and begin consuming aircraft observations.

### 6. Verify the API

| Endpoint | URL |
|----------|-----|
| Overview | http://127.0.0.1:8001/api/overview |
| Regional analytics | http://127.0.0.1:8001/api/regional |
| Aircraft data | http://127.0.0.1:8001/api/aircraft |
| Events | http://127.0.0.1:8001/api/events |

### 7. Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

The application will be available at http://localhost:5174/.

### Production Build

```bash
npm run build
```

Generated files are placed in `frontend/dist/`.

---

## 🌐 Public Deployment

The React frontend is publicly deployed through Netlify: https://real-time-flight-operations.netlify.app/

The frontend communicates with the FastAPI backend through the configured API URL (`VITE_API_URL`). For local development, the API runs on `http://127.0.0.1:8001`.

### Cloudflare Quick Tunnel

A Cloudflare Quick Tunnel can expose the local FastAPI service for temporary public access:

```bash
cloudflared tunnel --url http://127.0.0.1:8001
```

> [!IMPORTANT]
> Cloudflare Quick Tunnel is intended for development/demo access, not permanent production API hosting. The generated URL is temporary and changes whenever a new tunnel is created, and the original `cloudflared` process must remain running while the public API endpoint is required.

---

## 📈 Key Analytics

**Aircraft Operations** — aircraft counts, unique aircraft, aircraft positions, aircraft movement, regional aircraft activity

**Regional Traffic** — regional aircraft volume, unique aircraft by region, traffic distribution, regional movement activity, traffic time series

**Events** — aviation event counts, recent events, event summaries, operational event monitoring

**System Operations** — pipeline run tracking, current pipeline state, database connectivity, streaming pipeline status, API availability

---

## ✅ Data Quality & Current-Run Isolation

A dedicated `run_id` prevents dashboards from mixing data from different pipeline executions, providing a clear separation between:

```text
Historical pipeline runs    vs.    Current active pipeline run
```

Analytics views reference the current run so operational dashboards stay focused on the active streaming session.

### Pipeline Validation

The seven-region configuration is validated across ingestion and producer configuration:

```text
INGESTION: ['riyadh', 'dammam', 'dubai', 'doha', 'muscat', 'manama', 'kuwait_city']
PRODUCER:  ['riyadh', 'dammam', 'dubai', 'doha', 'muscat', 'manama', 'kuwait_city']
MATCH:     True
```

The `/api/regional` endpoint returns `"count": 7`, confirming that the API exposes all seven configured regions.

---

## 🔧 Git Workflow

```bash
git status
git add .
git commit -m "Update aviation analytics project"
git push origin main
```

---

## 📋 Project Status

The project currently provides:

- [x] Live aircraft data ingestion
- [x] Seven-region aviation monitoring
- [x] Redpanda streaming
- [x] Python stream processing
- [x] PostgreSQL storage
- [x] Current-run tracking
- [x] Aviation event processing
- [x] FastAPI analytics endpoints
- [x] React interactive dashboard
- [x] Live regional traffic monitoring
- [x] Interactive aircraft operations view
- [x] Events and anomaly dashboard
- [x] Aircraft analytics dashboard
- [x] Power BI analytics dashboards
- [x] Docker-based deployment
- [x] Public frontend deployment

The platform is structured as an end-to-end real-time aviation analytics solution combining data ingestion, streaming, processing, database engineering, API development, business intelligence, and interactive visualization.

---

## 👤 Author

**Abdullah Ahmad** — Data Analytics | Business Intelligence | Data Engineering | Software Engineering

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/aabdullah-ahmad/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/abdullahahmadd)

**Repository:** https://github.com/abdullahahmadd/real-time-flight-operations-aviation-analytics
**Live Dashboard:** https://real-time-flight-operations.netlify.app/
