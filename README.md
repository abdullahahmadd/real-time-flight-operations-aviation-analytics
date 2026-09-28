# Real-Time Flight Operations & Aviation Analytics

[![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Analytics-F2C811?logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)

An end-to-end real-time aviation analytics platform that collects live aircraft data, processes streaming observations, stores operational and analytical data, exposes analytics through APIs, and presents live aviation insights through an interactive web application and Power BI dashboards.

---

## Overview

**Real-Time Flight Operations & Aviation Analytics** is a full-stack data engineering and analytics project built around live aircraft tracking data from **ADSB.lol**.

The project demonstrates the complete journey from live data ingestion to business-facing analytics:

```text
Live Aircraft Data
        |
        v
    ADSB.lol
        |
        v
 Python Data Ingestion
        |
        v
     Redpanda
        |
        v
 Stream Processing
        |
        v
   PostgreSQL
        |
        +------------------+
        |                  |
        v                  v
     FastAPI           Power BI
        |
        v
 React Web Dashboard
```

The platform continuously collects aircraft observations from defined aviation regions, processes the incoming stream, stores the resulting data in PostgreSQL, and makes the information available through both a web-based analytics application and Power BI.

---

## Project Objectives

The project was developed to demonstrate an end-to-end real-time analytics workflow covering:

- Live external data ingestion
- Real-time event streaming
- Stream processing
- Relational database design
- Analytical SQL views
- REST API development
- Interactive data visualization
- Geographic aircraft monitoring
- Business intelligence reporting
- Docker-based application deployment
- Public web deployment
- Git and GitHub project management

---

## Key Features

### Live Aircraft Monitoring

The platform continuously retrieves live aircraft observations from ADSB.lol and processes them through the streaming pipeline.

The system provides visibility into:

- Aircraft activity
- Aircraft positions
- Regional traffic
- Aircraft movement
- Current operational activity

### Regional Aviation Monitoring

The current platform monitors seven aviation regions:

| Region | Country | Monitoring Radius |
|--------|---------|-------------------|
| Riyadh | Saudi Arabia | 250 NM |
| Dammam | Saudi Arabia | 250 NM |
| Dubai | United Arab Emirates | 250 NM |
| Doha | Qatar | 250 NM |
| Muscat | Oman | 250 NM |
| Manama | Bahrain | 250 NM |
| Kuwait City | Kuwait | 250 NM |

The regional model uses a geographic point and a 250 nautical mile radius for each monitored area.

Regional results therefore represent aircraft returned by the corresponding geographic query and should not be interpreted as exact administrative city boundaries.

### Real-Time Streaming

Aircraft observations move through a streaming pipeline using Redpanda.

The streaming architecture separates:

- Data collection
- Message streaming
- Stream processing
- Database storage

This allows the platform to continuously process new observations as they arrive.

### Aviation Event Processing

The processing layer analyzes incoming aircraft observations and records aviation events for downstream analytics.

These events are made available through the API and the web dashboard.

### PostgreSQL Analytics Layer

PostgreSQL acts as the central persistent data store.

The database contains operational aviation data together with an analytics layer designed for dashboard and API consumption.

The analytics layer provides prepared datasets for:

- Aircraft analytics
- Regional traffic
- Aviation events
- Traffic trends
- Current operational activity

### REST API

FastAPI provides the application interface between the PostgreSQL analytics layer and the frontend.

Available endpoints include:

```text
GET /api/overview
GET /api/aircraft
GET /api/aircraft/summary
GET /api/events
GET /api/regional
GET /api/timeseries
GET /api/database
```

### Interactive Web Dashboard

The React frontend provides five main analytical areas:

1. **Overview**
   - Operational KPIs
   - Current system status
   - Aircraft activity
   - Regional activity
2. **Live Operations**
   - Live aircraft map
   - Aircraft positions
   - Regional distribution
   - Operational activity
3. **Regional Traffic**
   - Regional aircraft activity
   - Traffic distribution
   - Regional comparisons
   - Traffic trends
4. **Events & Anomalies**
   - Aviation events
   - Recent events
   - Operational event information
5. **Aircraft Analytics**
   - Aircraft-level information
   - Aircraft activity
   - Operational summaries

### Power BI Analytics

The project also includes a Power BI solution connected to the PostgreSQL analytics layer.

The Power BI dashboards provide an additional business intelligence interface for exploring:

- Aircraft activity
- Regional traffic
- Aviation events
- Operational trends
- Current aviation data

---

## Technology Stack

| Category | Technology |
|----------|------------|
| Data Source | ADSB.lol |
| Programming | Python |
| Streaming | Redpanda |
| Database | PostgreSQL 16 |
| Backend API | FastAPI |
| Frontend | React |
| Frontend Build | Vite |
| Visualization | Recharts |
| Mapping | Leaflet / React Leaflet |
| Business Intelligence | Power BI Desktop |
| Containerization | Docker / Docker Compose |
| Version Control | Git / GitHub |
| Public Frontend | Netlify |
| Temporary API Exposure | Cloudflare Quick Tunnel |

---

## End-to-End Data Flow

The complete project workflow is:

### 1. Live Data Collection

The Python ingestion layer requests aircraft snapshots from ADSB.lol for the configured monitoring regions.

### 2. Streaming

Collected aircraft observations are published to Redpanda for real-time processing.

### 3. Stream Processing

The processing layer consumes aircraft observations, processes the incoming stream, identifies relevant aviation activity, and prepares records for storage.

### 4. Data Storage

Processed aviation data is stored in PostgreSQL.

The database maintains operational data and analytical views used by downstream applications.

### 5. API Layer

FastAPI exposes the PostgreSQL analytics layer through REST endpoints.

### 6. Web Analytics

The React application consumes the API and presents the information through interactive dashboards, charts, maps, and operational views.

### 7. Business Intelligence

Power BI connects to the PostgreSQL analytics layer to provide an additional analytical and reporting interface.

---

## Architecture

```text
                         ADSB.lol
                            |
                            v
                  +-------------------+
                  |  Python Ingestion |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  |     Redpanda      |
                  |  Event Streaming  |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  | Stream Processor  |
                  |      Python       |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  |    PostgreSQL     |
                  | Operational Data  |
                  | Analytics Views   |
                  +----+---------+----+
                       |         |
                       |         |
                       v         v
                +----------+  +----------+
                | FastAPI  |  | Power BI |
                +----+-----+  +----------+
                     |
                     v
                +----------+
                |  React   |
                |Dashboard |
                +----------+
```

---

## Project Structure

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
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
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

## Requirements

Before running the project locally, install:

- Python 3.14+
- Node.js
- npm
- Docker Desktop
- Git
- Power BI Desktop if Power BI analysis is required

The project is designed to run with Docker for the main backend infrastructure.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/abdullahahmadd/real-time-flight-operations-aviation-analytics.git
cd real-time-flight-operations-aviation-analytics
```

### 2. Configure Environment Variables

Create the required environment files using the provided examples.

```text
.env.example
docker/.env
frontend/.env.example
```

Do not commit passwords, API credentials, or other sensitive configuration values.

### 3. Start the Backend Stack

From the project root:

```bash
docker compose --env-file docker/.env -f docker/docker-compose.deploy.yml up -d
```

Check the running services:

```bash
docker compose --env-file docker/.env -f docker/docker-compose.deploy.yml ps
```

The main services are:

```text
redpanda
producer
postgres
api
processor
```

### 4. Verify the API

The local API is available at:

```text
http://127.0.0.1:8001
```

Example endpoints:

```text
http://127.0.0.1:8001/api/overview
http://127.0.0.1:8001/api/regional
http://127.0.0.1:8001/api/aircraft
http://127.0.0.1:8001/api/events
```

### 5. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The development application runs at:

```text
http://localhost:5174/
```

---

## Docker Services

The Docker deployment contains the following services:

| Service | Purpose |
|---------|---------|
| redpanda | Real-time event streaming |
| producer | Live aircraft data ingestion |
| processor | Stream processing and event generation |
| postgres | Persistent aviation data storage |
| api | REST API for analytics |

For local Power BI connectivity, PostgreSQL is exposed through:

```text
Host: localhost
Port: 5433
```

Inside Docker, services communicate with PostgreSQL through:

```text
postgres:5432
```

---

## Frontend Build

To create a production build:

```bash
cd frontend
npm run build
```

The production output is generated in:

```text
frontend/dist/
```

---

## Power BI

The Power BI file is located at:

```text
powerbi/Real-Time Flight Operations & Aviation Analytics.pbix
```

The dashboard connects to the PostgreSQL analytics layer and provides an additional interface for exploring the aviation data.

For local Docker deployment, the PostgreSQL connection uses:

```text
Server: localhost
Port: 5433
```

---

## Public Application

The React frontend is deployed publicly through Netlify:

**Live Dashboard:**

https://real-time-flight-operations.netlify.app/

The public dashboard provides access to the project's interactive aviation analytics interface.

---

## Temporary API Access

The project can use Cloudflare Quick Tunnel to temporarily expose the local FastAPI service for public access.

Example:

```bash
cloudflared tunnel --url http://127.0.0.1:8001
```

The generated `trycloudflare.com` address is temporary and depends on the active Quick Tunnel session.

For a permanent production deployment, the API should be hosted on a persistent backend infrastructure rather than relying on a Quick Tunnel.

---

## Current Monitoring Configuration

The current system monitors:

```text
Riyadh
Dammam
Dubai
Doha
Muscat
Manama
Kuwait City
```

Each region uses a 250 nautical mile radius around its configured geographic center.

The regional monitoring configuration is designed for operational aviation analytics rather than exact city-boundary measurement.

---

## Analytics Capabilities

The completed platform supports:

- Live aircraft monitoring
- Regional traffic analysis
- Aircraft activity analysis
- Aviation event monitoring
- Current operational status
- Traffic time-series analysis
- Interactive aircraft mapping
- PostgreSQL-based analytical reporting
- REST API access
- Power BI reporting
- Real-time web visualization

---

## Data and Analytics Layers

The project separates the platform into several logical layers:

```text
Data Source
    ↓
Ingestion
    ↓
Streaming
    ↓
Processing
    ↓
Database
    ↓
Analytics
    ↓
API / BI
    ↓
Visualization
```

This structure allows the same processed aviation data to support both the React dashboard and Power BI.

---

## Run Tracking

The pipeline uses run tracking to distinguish the active processing session from previous pipeline data.

This allows the analytics layer to focus dashboard queries on the current operational run while maintaining the underlying historical data.

---

## Development Workflow

Typical development workflow:

```bash
# Start backend services
docker compose --env-file docker/.env -f docker/docker-compose.deploy.yml up -d

# Check services
docker compose --env-file docker/.env -f docker/docker-compose.deploy.yml ps

# Start frontend
cd frontend
npm install
npm run dev

# Build frontend
npm run build
```

For source control:

```bash
git status
git add .
git commit -m "Update aviation analytics project"
git push origin main
```

---

## Repository

GitHub repository:

https://github.com/abdullahahmadd/real-time-flight-operations-aviation-analytics

---

## Project Deliverables

The completed project includes:

- Real-time aviation data ingestion
- Seven-region monitoring configuration
- Redpanda streaming pipeline
- Python stream processing
- PostgreSQL operational database
- PostgreSQL analytics layer
- FastAPI backend
- React and Vite frontend
- Interactive aircraft map
- Regional traffic analytics
- Aviation event analytics
- Aircraft analytics
- Power BI dashboards
- Docker deployment configuration
- Project documentation
- Public frontend deployment

---

## Author

**Abdullah Ahmad**

Data Analytics | Business Intelligence | Data Engineering | Software Engineering

LinkedIn

GitHub

---

## Project Status

The platform is currently structured as a complete end-to-end real-time aviation analytics solution covering:

```text
Live Data
   ↓
Ingestion
   ↓
Streaming
   ↓
Processing
   ↓
PostgreSQL
   ↓
FastAPI
   ↓
React Dashboard
   +
Power BI
```

The project demonstrates the integration of data engineering, real-time streaming, database development, API development, business intelligence, and interactive data visualization in a single aviation analytics platform.
