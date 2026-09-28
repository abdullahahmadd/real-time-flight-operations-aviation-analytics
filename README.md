# Real-Time Flight Operations & Aviation Analytics

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Analytics-F2C811?logo=powerbi&logoColor=black)

An end-to-end real-time aviation analytics platform that collects live aircraft data, processes streaming observations, stores operational and analytical data, exposes analytics through APIs, and presents live aviation insight through an interactive web application and Power BI dashboards.

**Live Dashboard:** [real-time-flight-operations.netlify.app](https://real-time-flight-operations.netlify.app/)

---

## Table of Contents

- [Overview](#overview)
- [Business Problem](#business-problem)
- [Objectives](#objectives)
- [Technology Stack](#technology-stack)
- [Methodology - End-to-End Data Flow](#methodology---end-to-end-data-flow)
- [Architecture](#architecture)
- [Regional Monitoring Configuration](#regional-monitoring-configuration)
- [REST API](#rest-api)
- [Interactive Web Dashboard](#interactive-web-dashboard)
- [Docker Services](#docker-services)
- [Getting Started](#getting-started)
- [Key Performance Indicators](#key-performance-indicators)
- [Project Structure](#project-structure)
- [Conclusion](#conclusion)

---

## Overview

Real-Time Flight Operations & Aviation Analytics is a full-stack data engineering and analytics project built around live aircraft tracking data from ADSB.lol. It demonstrates the complete journey from live data ingestion to business-facing analytics: Python ingestion feeds a Redpanda streaming pipeline, a stream processor writes to PostgreSQL, and the resulting operational and analytical data is exposed through both a FastAPI/React web application and Power BI dashboards.

---

## Business Problem

Aviation traffic data is inherently real-time and high-volume - useful analytics require continuously ingesting live aircraft positions rather than working from static snapshots. Without a structured pipeline, raw live feeds don't translate into usable operational visibility: there's no persistent record for trend analysis, no API for downstream consumption, and no way to compare regional traffic patterns side by side. This project addresses that gap by building a complete pipeline from live ingestion through to both a self-service web dashboard and a BI reporting layer, covering 7 aviation regions across the Gulf.

---

## Objectives

- Build a live ingestion layer pulling continuous aircraft observations from an external data source
- Implement a real-time streaming pipeline (Redpanda) decoupling collection from processing
- Design a PostgreSQL schema with both operational tables and a dedicated analytics layer for dashboard/API consumption
- Expose that analytics layer through a REST API (FastAPI) and a Power BI connection simultaneously
- Deliver an interactive React web dashboard covering live operations, regional traffic, events, and aircraft-level analytics
- Containerize the full backend stack with Docker for reproducible deployment

---

## Technology Stack

| Category | Technology |
|---|---|
| Data Source | ADSB.lol |
| Programming | Python |
| Streaming | Redpanda |
| Database | PostgreSQL 16 |
| Backend API | FastAPI |
| Frontend | React, Vite |
| Visualization | Recharts, Leaflet / React Leaflet |
| Business Intelligence | Power BI Desktop |
| Containerization | Docker / Docker Compose |
| Deployment | Netlify (frontend), Cloudflare Quick Tunnel (temporary API exposure) |
| Version Control | Git / GitHub |

---

## Methodology - End-to-End Data Flow

**1. Live Data Collection**
The Python ingestion layer requests aircraft snapshots from ADSB.lol for each of the 7 configured monitoring regions.

**2. Streaming**
Collected aircraft observations are published to Redpanda for real-time processing, decoupling collection from downstream consumption.

**3. Stream Processing**
The processing layer consumes aircraft observations, identifies relevant aviation activity, and prepares records for storage.

**4. Data Storage**
Processed aviation data is stored in PostgreSQL, which maintains both operational data and analytical views used by downstream applications.

**5. API Layer**
FastAPI exposes the PostgreSQL analytics layer through 7 REST endpoints.

**6. Web Analytics**
The React application consumes the API and presents the information through interactive dashboards, charts, maps, and operational views across 5 analytical areas.

**7. Business Intelligence**
Power BI connects directly to the PostgreSQL analytics layer, providing a second analytical interface on the same underlying data.

---

## Architecture

```
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

Run tracking distinguishes the active processing session from previous pipeline runs, letting the analytics layer focus dashboard queries on current operational data while preserving full historical data underneath.

---

## Regional Monitoring Configuration

| Region | Country | Monitoring Radius |
|---|---|---|
| Riyadh | Saudi Arabia | 250 NM |
| Dammam | Saudi Arabia | 250 NM |
| Dubai | United Arab Emirates | 250 NM |
| Doha | Qatar | 250 NM |
| Muscat | Oman | 250 NM |
| Manama | Bahrain | 250 NM |
| Kuwait City | Kuwait | 250 NM |

Each region uses a geographic point and a 250 nautical mile radius. Regional results represent aircraft returned by that geographic query, not exact administrative city boundaries.

---

## REST API

FastAPI provides the interface between the PostgreSQL analytics layer and the frontend, with 7 endpoints:

```
GET /api/overview
GET /api/aircraft
GET /api/aircraft/summary
GET /api/events
GET /api/regional
GET /api/timeseries
GET /api/database
```

---

## Interactive Web Dashboard

The React frontend covers 5 analytical areas:

| Area | Focus |
|---|---|
| Overview | Operational KPIs, system status, aircraft/regional activity |
| Live Operations | Live aircraft map, positions, regional distribution |
| Regional Traffic | Regional activity, traffic distribution, comparisons, trends |
| Events & Anomalies | Aviation events, recent events, operational event detail |
| Aircraft Analytics | Aircraft-level information, activity, operational summaries |

---

## Docker Services

| Service | Purpose |
|---|---|
| redpanda | Real-time event streaming |
| producer | Live aircraft data ingestion |
| processor | Stream processing and event generation |
| postgres | Persistent aviation data storage |
| api | REST API for analytics |

For local Power BI connectivity, PostgreSQL is exposed on `localhost:5433` (internally, services communicate via `postgres:5432`).

---

## Getting Started

**Requirements:** Python 3.14+, Node.js, npm, Docker Desktop, Git, Power BI Desktop (optional, for BI analysis).

**1. Clone the repository**
```bash
git clone https://github.com/abdullahahmadd/real-time-flight-operations-aviation-analytics.git
cd real-time-flight-operations-aviation-analytics
```

**2. Configure environment variables**
Create the required environment files from the provided examples (`.env.example`, `docker/.env`, `frontend/.env.example`). Do not commit credentials.

**3. Start the backend stack**
```bash
docker compose --env-file docker/.env -f docker/docker-compose.deploy.yml up -d
docker compose --env-file docker/.env -f docker/docker-compose.deploy.yml ps
```

**4. Verify the API**
API runs at `http://127.0.0.1:8001` (e.g., `/api/overview`, `/api/regional`, `/api/aircraft`, `/api/events`).

**5. Start the frontend**
```bash
cd frontend
npm install
npm run dev
```
Development app runs at `http://localhost:5174/`.

**Production build:**
```bash
npm run build
```
Output generated in `frontend/dist/`.

---

## Key Performance Indicators

| Metric | Result |
|---|---|
| Aviation Regions Monitored | 7 (Gulf region) |
| Monitoring Radius per Region | 250 NM |
| REST API Endpoints Exposed | 7 |
| Dashboard Analytical Areas | 5 |
| Docker Services Orchestrated | 5 |
| Analytics Interfaces | 2 (React web dashboard, Power BI) |
| Pipeline Stages | 7 (ingestion → streaming → processing → storage → API → web → BI) |

---

## Project Structure

```
real-time-flight-operations-aviation-analytics/
├── backend/
│   └── main.py
├── database/
│   ├── 01_create_schema.sql
│   ├── 02_add_run_tracking.sql
│   ├── 03_create_analytics_views.sql
│   └── 04_seed_muscat.sql
├── docker/
│   ├── docker-compose.deploy.yml
│   └── docker-compose.yml
├── docs/
│   ├── architecture/
│   ├── data-dictionary/
│   └── screenshots/
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── dist/
├── ingestion/
│   ├── adsb_client.py
│   ├── config.py
│   └── postgres_loader.py
├── processing/
│   └── aircraft_stream_processor.py
├── streaming/
│   └── aircraft_producer.py
├── powerbi/
│   └── Real-Time Flight Operations & Aviation Analytics.pbix
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Conclusion

This project demonstrates a complete real-time data engineering pipeline - live ingestion, event streaming, stream processing, relational + analytical database design, REST API development, interactive web visualization, and BI reporting - built around a genuinely live external data source rather than a static dataset. Covering 7 Gulf aviation regions through a single PostgreSQL analytics layer feeding both a React dashboard and Power BI shows the same processed data supporting two very different downstream consumers without duplicating the pipeline.

---
