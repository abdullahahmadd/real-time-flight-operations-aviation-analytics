import { useEffect, useMemo, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from 'recharts'
import './App.css'

const API_URL = 'http://127.0.0.1:8000'
const REFRESH_MS = 2000

const navigation = [
  { id: 'overview', label: 'Overview' },
  { id: 'operations', label: 'Live Operations' },
  { id: 'regional', label: 'Regional Traffic' },
  { id: 'events', label: 'Events & Anomalies' },
  { id: 'aircraft', label: 'Aircraft Analytics' },
]

const pageInfo = {
  overview: {
    eyebrow: 'AVIATION INTELLIGENCE',
    title: 'Operations Overview',
    description:
      'Real-time visibility into aircraft activity, regional traffic and operational events.',
  },
  operations: {
    eyebrow: 'LIVE OPERATIONS',
    title: 'Live Flight Operations',
    description:
      'Monitor current aircraft activity across the monitored aviation region.',
  },
  regional: {
    eyebrow: 'REGIONAL INTELLIGENCE',
    title: 'Regional Traffic',
    description:
      'Explore current aviation activity across monitored KSA and Gulf regions.',
  },
  events: {
    eyebrow: 'EVENT INTELLIGENCE',
    title: 'Events & Anomalies',
    description:
      'Explore operational events identified from the live aviation data.',
  },
  aircraft: {
    eyebrow: 'AIRCRAFT INTELLIGENCE',
    title: 'Aircraft Analytics',
    description:
      'Explore aircraft activity, movement, altitude and speed analytics.',
  },
}

const emptyOverview = {
  active_aircraft: 0,
  total_events: 0,
  region_changes: 0,
  altitude_changes: 0,
  high_vertical_rate_events: 0,
}

const regionColors = {
  riyadh: '#087ea4',
  muscat: '#149c9c',
  dammam: '#3f83b8',
  dubai: '#0d82a5',
  doha: '#64748b',
}

const eventColors = {
  REGION_CHANGE: '#087ea4',
  ALTITUDE_CHANGE: '#3f83b8',
  HIGH_VERTICAL_RATE: '#7c5ce6',
  SPEED_CHANGE: '#149c9c',
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString()
}

function formatDecimal(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '—'
  }

  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })
}

function formatRegionName(value) {
  if (!value) return 'Unknown'

  return String(value)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase())
}

function formatDateTime(value) {
  if (!value) return '—'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return '—'

  return date.toLocaleString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function formatChartTime(value) {
  if (!value) return ''

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return String(value)

  return date.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function safeArray(response) {
  return Array.isArray(response?.data) ? response.data : []
}

function getAircraftAltitude(aircraft) {
  return aircraft?.altitude_baro ?? aircraft?.altitude_geom ?? null
}

function getAircraftSpeed(aircraft) {
  return aircraft?.ground_speed ?? null
}

function getAircraftLabel(aircraft) {
  return aircraft?.callsign || aircraft?.registration || aircraft?.aircraft_hex || 'Unknown'
}

function App() {
  const [activeSection, setActiveSection] = useState('overview')
  const [overview, setOverview] = useState(emptyOverview)
  const [regionalData, setRegionalData] = useState([])
  const [timeseriesData, setTimeseriesData] = useState([])
  const [aircraftData, setAircraftData] = useState([])
  const [aircraftSummary, setAircraftSummary] = useState([])
  const [events, setEvents] = useState([])
  const [lastUpdated, setLastUpdated] = useState(null)
  const [apiOnline, setApiOnline] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true

    const fetchLiveData = async () => {
      const endpoints = [
        ['overview', '/api/overview'],
        ['regional', '/api/regional'],
        ['timeseries', '/api/timeseries'],
        ['aircraft', '/api/aircraft'],
        ['aircraftSummary', '/api/aircraft/summary'],
        ['events', '/api/events'],
      ]

      try {
        const results = await Promise.all(
          endpoints.map(async ([key, path]) => {
            const response = await fetch(`${API_URL}${path}`)

            if (!response.ok) {
              throw new Error(`${path} returned ${response.status}`)
            }

            return [key, await response.json()]
          }),
        )

        if (!mounted) return

        const data = Object.fromEntries(results)

        setOverview({
          ...emptyOverview,
          ...(data.overview || {}),
        })

        setRegionalData(safeArray(data.regional))
        setTimeseriesData(safeArray(data.timeseries))
        setAircraftData(safeArray(data.aircraft))
        setAircraftSummary(safeArray(data.aircraftSummary))
        setEvents(safeArray(data.events))

        setApiOnline(true)
        setLastUpdated(new Date())
        setLoading(false)
      } catch (error) {
        console.error('Live API error:', error)

        if (!mounted) return

        setApiOnline(false)
        setLoading(false)
      }
    }

    fetchLiveData()
    const interval = setInterval(fetchLiveData, REFRESH_MS)

    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [])

  const handleNavigation = (section) => {
    setActiveSection(section)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const currentPage = pageInfo[activeSection]

  const eventDistribution = useMemo(() => {
    const counts = events.reduce((result, event) => {
      const type = event.event_type || 'OTHER'
      result[type] = (result[type] || 0) + 1
      return result
    }, {})

    return Object.entries(counts)
      .map(([event_type, count]) => ({
        event_type,
        label: formatEventType(event_type),
        count,
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8)
  }, [events])

  const aircraftTypeDistribution = useMemo(() => {
    const counts = aircraftSummary.reduce((result, aircraft) => {
      const type = aircraft.aircraft_type || 'Unknown'
      if (type === 'TWR') return result
      result[type] = (result[type] || 0) + 1
      return result
    }, {})

    return Object.entries(counts)
      .map(([aircraft_type, count]) => ({ aircraft_type, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8)
  }, [aircraftSummary])

  const altitudeDistribution = useMemo(() => {
    const bands = [
      { label: '0–10k ft', min: 0, max: 10000 },
      { label: '10–20k ft', min: 10000, max: 20000 },
      { label: '20–30k ft', min: 20000, max: 30000 },
      { label: '30–40k ft', min: 30000, max: 40000 },
      { label: '40k+ ft', min: 40000, max: Infinity },
    ]

    return bands.map((band) => ({
      band: band.label,
      count: aircraftData.filter((aircraft) => {
        const altitude = getAircraftAltitude(aircraft)
        return (
          altitude !== null &&
          altitude >= band.min &&
          altitude < band.max
        )
      }).length,
    }))
  }, [aircraftData])

  const speedDistribution = useMemo(() => {
    const bands = [
      { label: '0–150 kt', min: 0, max: 150 },
      { label: '150–300 kt', min: 150, max: 300 },
      { label: '300–450 kt', min: 300, max: 450 },
      { label: '450+ kt', min: 450, max: Infinity },
    ]

    return bands.map((band) => ({
      band: band.label,
      count: aircraftData.filter((aircraft) => {
        const speed = getAircraftSpeed(aircraft)
        return speed !== null && speed >= band.min && speed < band.max
      }).length,
    }))
  }, [aircraftData])

  const operationsMetrics = useMemo(() => {
    const validAltitude = aircraftData
      .map(getAircraftAltitude)
      .filter((value) => value !== null && Number.isFinite(Number(value)))

    const validSpeed = aircraftData
      .map(getAircraftSpeed)
      .filter((value) => value !== null && Number.isFinite(Number(value)))

    return {
      aircraft: aircraftData.length,
      altitude: validAltitude.length
        ? validAltitude.reduce((sum, value) => sum + Number(value), 0) /
          validAltitude.length
        : null,
      speed: validSpeed.length
        ? validSpeed.reduce((sum, value) => sum + Number(value), 0) /
          validSpeed.length
        : null,
    }
  }, [aircraftData])

  return (
    <div className="app">
      <header className="site-header">
        <div className="header-inner">
          <button
            className="brand"
            type="button"
            onClick={() => handleNavigation('overview')}
          >
            <div className="brand-mark" aria-hidden="true">
              <span className="brand-plane">✈</span>
            </div>

            <div className="brand-text">
              <strong>Real-Time Flight Operations</strong>
              <span>Aviation Analytics Platform</span>
            </div>
          </button>

          <nav className="main-navigation" aria-label="Main navigation">
            {navigation.map((item) => (
              <button
                key={item.id}
                type="button"
                className={
                  activeSection === item.id
                    ? 'nav-item active'
                    : 'nav-item'
                }
                onClick={() => handleNavigation(item.id)}
              >
                {item.label}
              </button>
            ))}
          </nav>

          <div className="live-indicator">
            <span
              className={apiOnline ? 'live-dot' : 'live-dot offline'}
            />

            <div className="live-status-text">
              <strong>{apiOnline ? 'LIVE' : 'OFFLINE'}</strong>
              <span>{apiOnline ? 'Live data' : 'Data unavailable'}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="main-content">
        <section className="page-header">
          <div className="page-heading">
            <span className="eyebrow">{currentPage.eyebrow}</span>
            <h1>{currentPage.title}</h1>
            <p>{currentPage.description}</p>
          </div>

          <div className="refresh-status">
            <span className="refresh-status-icon">↻</span>
            <div>
              <span>LIVE REFRESH</span>
              <strong>
                {lastUpdated
                  ? `Updated ${lastUpdated.toLocaleTimeString()}`
                  : 'Connecting...'}
              </strong>
            </div>
          </div>
        </section>

        {activeSection === 'overview' && (
          <OverviewPage
            overview={overview}
            regionalData={regionalData}
            timeseriesData={timeseriesData}
            eventDistribution={eventDistribution}
            loading={loading}
            onNavigate={handleNavigation}
          />
        )}

        {activeSection === 'operations' && (
          <OperationsPage
            overview={overview}
            aircraftData={aircraftData}
            altitudeDistribution={altitudeDistribution}
            speedDistribution={speedDistribution}
            operationsMetrics={operationsMetrics}
            loading={loading}
          />
        )}

        {activeSection === 'regional' && (
          <RegionalPage
            overview={overview}
            regionalData={regionalData}
            timeseriesData={timeseriesData}
            loading={loading}
          />
        )}

        {activeSection === 'events' && (
          <EventsPage
            overview={overview}
            events={events}
            eventDistribution={eventDistribution}
            loading={loading}
          />
        )}

        {activeSection === 'aircraft' && (
          <AircraftPage
            overview={overview}
            aircraftData={aircraftData}
            aircraftSummary={aircraftSummary}
            aircraftTypeDistribution={aircraftTypeDistribution}
            operationsMetrics={operationsMetrics}
            loading={loading}
          />
        )}
      </main>

      <footer className="site-footer">
        <div className="footer-inner">
          <div className="footer-project">
            <span className="footer-project-name">
              Real-Time Flight Operations &amp; Aviation Analytics
            </span>
          </div>

          <div className="footer-links">
            <a
              className="footer-social-link"
              href="https://www.linkedin.com/in/aabdullah-ahmad/"
              target="_blank"
              rel="noreferrer"
              aria-label="LinkedIn profile"
              title="LinkedIn"
            >
              <svg
                className="footer-social-icon"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M6.94 8.5H3.56V20h3.38V8.5ZM5.25 3A2.02 2.02 0 0 0 3.2 5.02c0 1.1.9 2 2.02 2 1.12 0 2.03-.9 2.03-2A2.02 2.02 0 0 0 5.25 3ZM20.8 13.41c0-3.47-1.85-5.09-4.31-5.09-1.99 0-2.88 1.1-3.38 1.87V8.5H9.73V20h3.38v-5.7c0-1.5.28-2.95 2.14-2.95 1.83 0 1.85 1.71 1.85 3.05V20h3.38l.32-6.59Z"
                  fill="currentColor"
                />
              </svg>
              <span>LinkedIn</span>
            </a>

            <a
              className="footer-social-link"
              href="https://github.com/abdullahahmadd"
              target="_blank"
              rel="noreferrer"
              aria-label="GitHub profile"
              title="GitHub"
            >
              <svg
                className="footer-social-icon"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M12 .7A11.3 11.3 0 0 0 8.42 22.92c.57.1.78-.25.78-.55v-2.14c-3.18.69-3.85-1.34-3.85-1.34-.52-1.32-1.27-1.67-1.27-1.67-1.04-.71.08-.7.08-.7 1.15.08 1.75 1.18 1.75 1.18 1.02 1.75 2.68 1.25 3.33.96.1-.74.4-1.25.73-1.54-2.54-.29-5.21-1.27-5.21-5.65 0-1.25.45-2.27 1.18-3.07-.12-.29-.51-1.45.11-3.02 0 0 .96-.31 3.14 1.17a10.8 10.8 0 0 1 5.72 0c2.18-1.48 3.14-1.17 3.14-1.17.62 1.57.23 2.73.11 3.02.73.8 1.18 1.82 1.18 3.07 0 4.39-2.68 5.35-5.23 5.64.41.36.78 1.07.78 2.16v3.2c0 .3.21.66.79.55A11.3 11.3 0 0 0 12 .7Z"
                  fill="currentColor"
                />
              </svg>
              <span>GitHub</span>
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}

function OverviewPage({
  overview,
  regionalData,
  timeseriesData,
  eventDistribution,
  loading,
  onNavigate,
}) {
  return (
    <>
      <section className="kpi-grid">
        <KpiCard
          label="ACTIVE AIRCRAFT"
          value={overview.active_aircraft}
          description="Current aircraft observations"
          icon="✈"
          loading={loading}
        />
        <KpiCard
          label="LIVE EVENTS"
          value={overview.total_events}
          description="Events in the current live session"
          icon="◈"
          loading={loading}
        />
        <KpiCard
          label="REGION CHANGES"
          value={overview.region_changes}
          description="Detected regional movements"
          icon="⇄"
          loading={loading}
        />
        <KpiCard
          label="HIGH VERTICAL RATE"
          value={overview.high_vertical_rate_events}
          description="Detected vertical-rate events"
          icon="↕"
          loading={loading}
        />
      </section>

      <section className="dashboard-grid dashboard-grid-primary">
        <Panel
          eyebrow="LIVE OPERATIONS"
          title="Aircraft Activity"
          description="Current aircraft activity from the live data feed."
          action="Open Live Operations"
          onAction={() => onNavigate('operations')}
        >
          <div className="activity-visual">
            <div className="activity-center">
              <span className="activity-center-label">ACTIVE</span>
              <strong>{formatNumber(overview.active_aircraft)}</strong>
              <span>aircraft</span>
            </div>
            <div className="activity-ring ring-one" />
            <div className="activity-ring ring-two" />
            <div className="activity-ring ring-three" />
            <span className="activity-point point-one" />
            <span className="activity-point point-two" />
            <span className="activity-point point-three" />
            <span className="activity-point point-four" />
          </div>

          <div className="visual-footer">
            <span>Data status</span>
            <strong>Live data available</strong>
          </div>
        </Panel>

        <Panel
          eyebrow="REGIONAL INTELLIGENCE"
          title="Regional Traffic"
          description="Current aircraft observations across monitored regions."
          action="View Regional Traffic"
          onAction={() => onNavigate('regional')}
        >
          <RegionalBarChart data={regionalData} />
        </Panel>
      </section>

      <section className="dashboard-grid dashboard-grid-secondary">
        <Panel
          eyebrow="STREAMING ANALYTICS"
          title="Event Activity"
          description="Current distribution of aviation events."
          action="Explore Events"
          onAction={() => onNavigate('events')}
        >
          <EventDistributionBars data={eventDistribution} />
        </Panel>

        <Panel
          eyebrow="TRAFFIC TREND"
          title="Live Regional Activity"
          description="Five-minute traffic activity from the current live session."
        >
          <TrafficTrendChart data={timeseriesData} compact />
        </Panel>
      </section>
    </>
  )
}

function OperationsPage({
  overview,
  aircraftData,
  altitudeDistribution,
  speedDistribution,
  operationsMetrics,
  loading,
}) {
  return (
    <>
      <section className="kpi-grid compact-kpi-grid">
        <KpiCard
          label="ACTIVE AIRCRAFT"
          value={overview.active_aircraft}
          description="Current aircraft observations"
          icon="✈"
          loading={loading}
        />
        <KpiCard
          label="LIVE EVENTS"
          value={overview.total_events}
          description="Current live session"
          icon="◈"
          loading={loading}
        />
      </section>

      <section className="dashboard-grid dashboard-grid-primary">
        <Panel
          eyebrow="LIVE MAP"
          title="Aircraft Operations Map"
          description="Current ADS-B aircraft positions from the live data feed."
        >
          <AircraftMap aircraft={aircraftData} />
        </Panel>

        <Panel
          eyebrow="CURRENT ACTIVITY"
          title="Operations Distribution"
          description="Live aircraft altitude and ground-speed distributions."
        >
          <div className="distribution-grid">
            <DistributionChart
              title="Altitude"
              data={altitudeDistribution}
              dataKey="count"
              categoryKey="band"
            />
            <DistributionChart
              title="Ground Speed"
              data={speedDistribution}
              dataKey="count"
              categoryKey="band"
            />
          </div>
        </Panel>
      </section>

      <section className="dashboard-grid dashboard-grid-secondary">
        <Panel
          eyebrow="OPERATIONAL PROFILE"
          title="Live Operating Metrics"
          description="Calculated directly from current aircraft observations."
        >
          <div className="metric-list">
            <MetricRow
              label="Aircraft records"
              value={formatNumber(operationsMetrics.aircraft)}
            />
            <MetricRow
              label="Average altitude"
              value={
                operationsMetrics.altitude === null
                  ? '—'
                  : `${formatNumber(Math.round(operationsMetrics.altitude))} ft`
              }
            />
            <MetricRow
              label="Average ground speed"
              value={
                operationsMetrics.speed === null
                  ? '—'
                  : `${formatDecimal(operationsMetrics.speed)} kt`
              }
            />
          </div>
        </Panel>

        <Panel
          eyebrow="POSITION FEED"
          title="Live Feed Status"
          description="Aircraft records currently available in the live data."
        >
          <div className="feed-status">
            <div className="feed-status-number">
              {formatNumber(aircraftData.length)}
            </div>
            <span>aircraft records currently available</span>
            <small>Refreshed every 2 seconds</small>
          </div>
        </Panel>
      </section>

      <Panel
        eyebrow="AIRCRAFT FEED"
        title="Live Aircraft Table"
        description="Current aircraft records from the live aviation data feed."
      >
        <AircraftTable aircraft={aircraftData} />
      </Panel>
    </>
  )
}

function RegionalPage({
  overview,
  regionalData,
  timeseriesData,
  loading,
}) {
  return (
    <>
      <section className="kpi-grid compact-kpi-grid">
        <KpiCard
          label="ACTIVE AIRCRAFT"
          value={overview.active_aircraft}
          description="Across monitored regions"
          icon="✈"
          loading={loading}
        />
        <KpiCard
          label="REGION CHANGES"
          value={overview.region_changes}
          description="Detected regional movements"
          icon="⇄"
          loading={loading}
        />
      </section>

      <Panel
        eyebrow="REGIONAL INTELLIGENCE"
        title="Regional Traffic Comparison"
        description="Current aircraft observations and unique aircraft across monitored regions."
      >
        <RegionalComparisonChart data={regionalData} />
      </Panel>

      <section className="dashboard-grid dashboard-grid-secondary">
        <Panel
          eyebrow="TRAFFIC TREND"
          title="Regional Activity Timeline"
          description="Five-minute regional traffic activity from the current live session."
        >
          <TrafficTrendChart data={timeseriesData} />
        </Panel>

        <Panel
          eyebrow="REGION DETAIL"
          title="Regional Distribution"
          description="Share of observed aircraft positions across monitored regions."
        >
          <RegionalDistributionChart data={regionalData} />
        </Panel>
      </section>

      <Panel
        eyebrow="REGIONAL METRICS"
        title="Regional Operating Profile"
        description="Altitude and ground-speed statistics by monitored region."
      >
        <RegionalMetricsTable data={regionalData} />
      </Panel>
    </>
  )
}

function EventsPage({
  overview,
  events,
  eventDistribution,
  loading,
}) {
  const recentEvents = events.slice(0, 40)

  return (
    <>
      <section className="kpi-grid">
        <KpiCard
          label="TOTAL EVENTS"
          value={overview.total_events}
          description="Current live session"
          icon="◈"
          loading={loading}
        />
        <KpiCard
          label="REGION CHANGES"
          value={overview.region_changes}
          description="Detected movements"
          icon="⇄"
          loading={loading}
        />
        <KpiCard
          label="ALTITUDE CHANGES"
          value={overview.altitude_changes}
          description="Detected altitude events"
          icon="↕"
          loading={loading}
        />
        <KpiCard
          label="HIGH VERTICAL RATE"
          value={overview.high_vertical_rate_events}
          description="Detected events"
          icon="↑"
          loading={loading}
        />
      </section>

      <section className="dashboard-grid dashboard-grid-primary">
        <Panel
          eyebrow="EVENT DISTRIBUTION"
          title="Event Type Activity"
          description="Distribution of events identified in the live aviation data."
        >
          <EventDistributionChart data={eventDistribution} />
        </Panel>

        <Panel
          eyebrow="EVENT TIMELINE"
          title="Recent Event Activity"
          description="Recent events ordered by event time."
        >
          <EventTimeline events={events} />
        </Panel>
      </section>

      <Panel
        eyebrow="EVENT LOG"
        title="Recent Events"
        description="Detailed event and anomaly records."
      >
        <EventTable events={recentEvents} />
      </Panel>
    </>
  )
}

function AircraftPage({
  overview,
  aircraftData,
  aircraftSummary,
  aircraftTypeDistribution,
  operationsMetrics,
  loading,
}) {
  return (
    <>
      <section className="kpi-grid compact-kpi-grid">
        <KpiCard
          label="ACTIVE AIRCRAFT"
          value={overview.active_aircraft}
          description="Current aircraft population"
          icon="✈"
          loading={loading}
        />
        <KpiCard
          label="REGION MOVEMENTS"
          value={overview.region_changes}
          description="Detected aircraft movements"
          icon="⇄"
          loading={loading}
        />
      </section>

      <section className="dashboard-grid dashboard-grid-primary">
        <Panel
          eyebrow="AIRCRAFT POPULATION"
          title="Aircraft Type Distribution"
          description="Aircraft population by type from the current aircraft data."
        >
          <AircraftTypeChart data={aircraftTypeDistribution} />
        </Panel>

        <Panel
          eyebrow="PERFORMANCE"
          title="Altitude & Speed Analysis"
          description="Current aircraft altitude and ground-speed relationship."
        >
          <AircraftPerformanceChart data={aircraftData} />
        </Panel>
      </section>

      <section className="dashboard-grid dashboard-grid-secondary">
        <Panel
          eyebrow="AIRCRAFT PROFILE"
          title="Current Operating Metrics"
          description="Aggregate values calculated from current aircraft observations."
        >
          <div className="metric-list">
            <MetricRow
              label="Aircraft records"
              value={formatNumber(operationsMetrics.aircraft)}
            />
            <MetricRow
              label="Average altitude"
              value={
                operationsMetrics.altitude === null
                  ? '—'
                  : `${formatNumber(Math.round(operationsMetrics.altitude))} ft`
              }
            />
            <MetricRow
              label="Average ground speed"
              value={
                operationsMetrics.speed === null
                  ? '—'
                  : `${formatDecimal(operationsMetrics.speed)} kt`
              }
            />
            <MetricRow
              label="Summary records"
              value={formatNumber(aircraftSummary.length)}
            />
          </div>
        </Panel>

        <Panel
          eyebrow="DATA QUALITY"
          title="Aircraft Coverage"
          description="Current aircraft data coverage from the live feed."
        >
          <div className="feed-status">
            <div className="feed-status-number">
              {formatNumber(aircraftData.filter(
                (aircraft) =>
                  aircraft.latitude !== null &&
                  aircraft.longitude !== null,
              ).length)}
            </div>
            <span>aircraft with coordinates</span>
            <small>Source: ADSB.lol</small>
          </div>
        </Panel>
      </section>

      <Panel
        eyebrow="AIRCRAFT INTELLIGENCE"
        title="Aircraft Analytics Table"
        description="Aircraft-level activity, registration, type, altitude and speed."
      >
        <AircraftAnalyticsTable aircraft={aircraftSummary} />
      </Panel>
    </>
  )
}

function KpiCard({ label, value, description, icon, loading }) {
  return (
    <article className="kpi-card">
      <div className="kpi-card-top">
        <span>{label}</span>
        <div className="kpi-icon">{icon}</div>
      </div>
      <strong>{loading ? '—' : formatNumber(value)}</strong>
      <small>{description}</small>
    </article>
  )
}

function Panel({
  eyebrow,
  title,
  description,
  action,
  onAction,
  children,
}) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="panel-eyebrow">{eyebrow}</span>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>

        {action && (
          <button
            type="button"
            className="panel-action"
            onClick={onAction}
          >
            {action} →
          </button>
        )}
      </div>

      <div className="panel-body">{children}</div>
    </section>
  )
}

function RegionalBarChart({ data }) {
  if (!data.length) return <ChartLoadingState />

  return (
    <div className="chart-container chart-container-small">
      <ResponsiveContainer width="100%" height={250}>
        <BarChart
          data={[...data].sort(
            (a, b) => b.position_count - a.position_count,
          )}
          layout="vertical"
          margin={{ top: 4, right: 18, left: 10, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal vertical={false} />
          <XAxis type="number" tick={{ fontSize: 11 }} />
          <YAxis
            type="category"
            dataKey="region_code"
            tickFormatter={formatRegionName}
            tick={{ fontSize: 11 }}
            width={68}
          />
          <Tooltip content={<RegionalTooltip />} />
          <Bar dataKey="position_count" radius={[0, 5, 5, 0]}>
            {data.map((item) => (
              <Cell
                key={item.region_code}
                fill={regionColors[item.region_code] || '#087ea4'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function RegionalComparisonChart({ data }) {
  if (!data.length) return <ChartLoadingState />

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={360}>
        <BarChart
          data={[...data].sort(
            (a, b) => b.position_count - a.position_count,
          )}
          margin={{ top: 12, right: 18, left: 8, bottom: 8 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="region_code"
            tickFormatter={formatRegionName}
            tick={{ fontSize: 11 }}
          />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip content={<RegionalComparisonTooltip />} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Bar
            dataKey="position_count"
            name="Positions"
            fill="#087ea4"
            radius={[5, 5, 0, 0]}
          />
          <Bar
            dataKey="unique_aircraft"
            name="Unique Aircraft"
            fill="#35a9c6"
            radius={[5, 5, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function TrafficTrendChart({ data, compact = false }) {
  if (!data.length) return <ChartLoadingState />

  const regions = [...new Set(data.map((item) => item.region_code))]
  const colors = regions.map(
    (region) => regionColors[region] || '#64748b',
  )

  return (
    <div
      className={
        compact
          ? 'chart-container chart-container-small'
          : 'chart-container'
      }
    >
      <ResponsiveContainer width="100%" height={compact ? 260 : 330}>
        <LineChart
          data={buildTimeseries(data)}
          margin={{ top: 12, right: 10, left: 0, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="time_bucket"
            tickFormatter={formatChartTime}
            tick={{ fontSize: 11 }}
            minTickGap={22}
          />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip
            labelFormatter={(value) => formatDateTime(value)}
            formatter={(value, name) => [
              formatNumber(value),
              formatRegionName(name),
            ]}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />

          {regions.map((region, index) => (
            <Line
              key={region}
              type="monotone"
              dataKey={region}
              name={formatRegionName(region)}
              stroke={colors[index]}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function RegionalDistributionChart({ data }) {
  if (!data.length) return <ChartLoadingState />

  const chartData = [...data]
    .sort((a, b) => b.position_count - a.position_count)
    .map((item) => ({
      name: formatRegionName(item.region_code),
      value: Number(item.position_count || 0),
      region_code: item.region_code,
    }))

  return (
    <div className="chart-container chart-container-pie">
      <ResponsiveContainer width="100%" height={330}>
        <PieChart>
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            innerRadius={62}
            outerRadius={105}
            paddingAngle={2}
          >
            {chartData.map((item) => (
              <Cell
                key={item.region_code}
                fill={regionColors[item.region_code] || '#087ea4'}
              />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => [
              formatNumber(value),
              'Positions',
            ]}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

function RegionalMetricsTable({ data }) {
  if (!data.length) return <ChartLoadingState />

  return (
    <DataTable>
      <thead>
        <tr>
          <th>Region</th>
          <th>Positions</th>
          <th>Aircraft</th>
          <th>Avg Altitude</th>
          <th>Avg Speed</th>
          <th>Max Altitude</th>
          <th>Max Speed</th>
        </tr>
      </thead>
      <tbody>
        {[...data]
          .sort((a, b) => b.position_count - a.position_count)
          .map((item) => (
            <tr key={item.region_code}>
              <td>{formatRegionName(item.region_code)}</td>
              <td>{formatNumber(item.position_count)}</td>
              <td>{formatNumber(item.unique_aircraft)}</td>
              <td>
                {item.avg_altitude_baro === null
                  ? '—'
                  : `${formatNumber(Math.round(item.avg_altitude_baro))} ft`}
              </td>
              <td>
                {item.avg_ground_speed === null
                  ? '—'
                  : `${formatDecimal(item.avg_ground_speed)} kt`}
              </td>
              <td>
                {item.max_altitude_baro === null
                  ? '—'
                  : `${formatNumber(Math.round(item.max_altitude_baro))} ft`}
              </td>
              <td>
                {item.max_ground_speed === null
                  ? '—'
                  : `${formatDecimal(item.max_ground_speed)} kt`}
              </td>
            </tr>
          ))}
      </tbody>
    </DataTable>
  )
}

function AircraftMap({ aircraft }) {
  const plotted = aircraft.filter(
    (item) =>
      Number.isFinite(Number(item.latitude)) &&
      Number.isFinite(Number(item.longitude)),
  )

  if (!plotted.length) return <ChartLoadingState />

  const latitudes = plotted.map((item) => Number(item.latitude))
  const longitudes = plotted.map((item) => Number(item.longitude))

  const minLat = Math.min(...latitudes)
  const maxLat = Math.max(...latitudes)
  const minLon = Math.min(...longitudes)
  const maxLon = Math.max(...longitudes)

  const latSpan = Math.max(maxLat - minLat, 1)
  const lonSpan = Math.max(maxLon - minLon, 1)

  const points = plotted.slice(0, 500).map((item) => ({
    ...item,
    x: 8 + ((Number(item.longitude) - minLon) / lonSpan) * 84,
    y: 90 - ((Number(item.latitude) - minLat) / latSpan) * 80,
  }))

  return (
    <div className="live-map">
      <div className="map-label map-label-top">LIVE ADS-B POSITIONS</div>

      <div className="map-grid">
        {Array.from({ length: 5 }).map((_, index) => (
          <span className="map-grid-line vertical" key={`v-${index}`} />
        ))}
        {Array.from({ length: 5 }).map((_, index) => (
          <span className="map-grid-line horizontal" key={`h-${index}`} />
        ))}

        {points.map((aircraft) => (
          <span
            key={`${aircraft.aircraft_hex}-${aircraft.observed_at}`}
            className="aircraft-map-point"
            style={{
              left: `${aircraft.x}%`,
              top: `${aircraft.y}%`,
            }}
            title={`${getAircraftLabel(aircraft)} • ${formatRegionName(
              aircraft.region_code,
            )}`}
          />
        ))}

        <div className="map-center-label">
          <strong>{formatNumber(points.length)}</strong>
          <span>aircraft plotted</span>
        </div>
      </div>

      <div className="map-footer">
        <span>Longitude {minLon.toFixed(1)}° to {maxLon.toFixed(1)}°</span>
        <span>Latitude {minLat.toFixed(1)}° to {maxLat.toFixed(1)}°</span>
      </div>
    </div>
  )
}

function DistributionChart({
  title,
  data,
  dataKey,
  categoryKey,
}) {
  return (
    <div className="distribution-card">
      <span className="distribution-title">{title}</span>
      <ResponsiveContainer width="100%" height={175}>
        <BarChart
          data={data}
          margin={{ top: 8, right: 6, left: -20, bottom: 2 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey={categoryKey}
            tick={{ fontSize: 8 }}
            interval={0}
          />
          <YAxis allowDecimals={false} tick={{ fontSize: 8 }} />
          <Tooltip />
          <Bar
            dataKey={dataKey}
            fill="#087ea4"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function AircraftTable({ aircraft }) {
  if (!aircraft.length) return <ChartLoadingState />

  return (
    <DataTable>
      <thead>
        <tr>
          <th>Callsign</th>
          <th>Registration</th>
          <th>Type</th>
          <th>Region</th>
          <th>Altitude</th>
          <th>Speed</th>
          <th>Vertical Rate</th>
          <th>Observed</th>
        </tr>
      </thead>
      <tbody>
        {aircraft.slice(0, 100).map((item) => (
          <tr key={`${item.aircraft_hex}-${item.observed_at}`}>
            <td>{item.callsign || item.aircraft_hex}</td>
            <td>{item.registration || '—'}</td>
            <td>{item.aircraft_type || '—'}</td>
            <td>{formatRegionName(item.region_code)}</td>
            <td>
              {getAircraftAltitude(item) === null
                ? '—'
                : `${formatNumber(Math.round(getAircraftAltitude(item)))} ft`}
            </td>
            <td>
              {getAircraftSpeed(item) === null
                ? '—'
                : `${formatDecimal(getAircraftSpeed(item))} kt`}
            </td>
            <td>
              {item.vertical_rate === null ||
              item.vertical_rate === undefined
                ? '—'
                : `${formatNumber(Math.round(item.vertical_rate))} fpm`}
            </td>
            <td>{formatDateTime(item.observed_at)}</td>
          </tr>
        ))}
      </tbody>
    </DataTable>
  )
}

function AircraftAnalyticsTable({ aircraft }) {
  if (!aircraft.length) return <ChartLoadingState />

  return (
    <DataTable>
      <thead>
        <tr>
          <th>Callsign</th>
          <th>Registration</th>
          <th>Type</th>
          <th>Positions</th>
          <th>Regions</th>
          <th>Avg Altitude</th>
          <th>Avg Speed</th>
          <th>Max Speed</th>
        </tr>
      </thead>
      <tbody>
        {aircraft.slice(0, 100).map((item) => (
          <tr key={item.aircraft_hex}>
            <td>{item.callsign || item.aircraft_hex}</td>
            <td>{item.registration || '—'}</td>
            <td>{item.aircraft_type || '—'}</td>
            <td>{formatNumber(item.position_count)}</td>
            <td>{formatNumber(item.regions_observed)}</td>
            <td>
              {item.avg_altitude_baro === null
                ? '—'
                : `${formatNumber(Math.round(item.avg_altitude_baro))} ft`}
            </td>
            <td>
              {item.avg_ground_speed === null
                ? '—'
                : `${formatDecimal(item.avg_ground_speed)} kt`}
            </td>
            <td>
              {item.max_ground_speed === null
                ? '—'
                : `${formatDecimal(item.max_ground_speed)} kt`}
            </td>
          </tr>
        ))}
      </tbody>
    </DataTable>
  )
}

function AircraftTypeChart({ data }) {
  if (!data.length) return <ChartLoadingState />

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={330}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 8, right: 20, left: 8, bottom: 8 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal vertical={false} />
          <XAxis type="number" allowDecimals={false} />
          <YAxis
            type="category"
            dataKey="aircraft_type"
            tick={{ fontSize: 11 }}
            width={54}
          />
          <Tooltip />
          <Bar
            dataKey="count"
            name="Aircraft"
            fill="#087ea4"
            radius={[0, 5, 5, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function AircraftPerformanceChart({ data }) {
  const plotted = data
    .filter(
      (item) =>
        getAircraftAltitude(item) !== null &&
        getAircraftSpeed(item) !== null,
    )
    .slice(0, 500)

  if (!plotted.length) return <ChartLoadingState />

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={330}>
        <ScatterChart margin={{ top: 12, right: 18, bottom: 12, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="altitude_baro"
            name="Altitude"
            unit=" ft"
            tick={{ fontSize: 11 }}
          />
          <YAxis
            type="number"
            dataKey="ground_speed"
            name="Ground speed"
            unit=" kt"
            tick={{ fontSize: 11 }}
          />
          <ZAxis range={[28, 28]} />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            formatter={(value, name) => [
              `${formatDecimal(value)}${name === 'Altitude' ? ' ft' : ' kt'}`,
              name,
            ]}
          />
          <Scatter
            name="Aircraft"
            data={plotted}
            fill="#087ea4"
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}

function EventDistributionBars({ data }) {
  if (!data.length) return <ChartLoadingState />

  const max = Math.max(...data.map((item) => item.count), 1)

  return (
    <div className="bar-chart large-bar-chart">
      {data.slice(0, 5).map((item) => (
        <div className="bar-chart-row" key={item.event_type}>
          <div className="bar-chart-label">
            <span>{item.label}</span>
            <strong>{formatNumber(item.count)}</strong>
          </div>

          <div className="bar-track">
            <div
              className="bar-fill"
              style={{
                width: `${Math.max(
                  (item.count / max) * 100,
                  item.count > 0 ? 4 : 0,
                )}%`,
                background:
                  eventColors[item.event_type] || undefined,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

function EventDistributionChart({ data }) {
  if (!data.length) return <ChartLoadingState />

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={330}>
        <BarChart
          data={data}
          margin={{ top: 8, right: 18, left: 0, bottom: 8 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11 }}
            interval={0}
          />
          <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Bar dataKey="count" name="Events" radius={[5, 5, 0, 0]}>
            {data.map((item) => (
              <Cell
                key={item.event_type}
                fill={eventColors[item.event_type] || '#087ea4'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function EventTimeline({ events }) {
  if (!events.length) return <ChartLoadingState />

  const timeline = buildEventTimeline(events)

  return (
    <div className="chart-container chart-container-small">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={timeline}
          margin={{ top: 12, right: 10, left: 0, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="time"
            tickFormatter={formatChartTime}
            tick={{ fontSize: 11 }}
          />
          <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
          <Tooltip
            labelFormatter={(value) => formatDateTime(value)}
          />
          <Line
            type="monotone"
            dataKey="count"
            name="Events"
            stroke="#087ea4"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function EventTable({ events }) {
  if (!events.length) return <ChartLoadingState />

  return (
    <DataTable>
      <thead>
        <tr>
          <th>Time</th>
          <th>Event</th>
          <th>Aircraft</th>
          <th>Region</th>
          <th>Value</th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>
        {events.slice(0, 100).map((event) => (
          <tr key={event.event_id}>
            <td>{formatDateTime(event.event_time)}</td>
            <td>
              <span className="event-type-badge">
                {formatEventType(event.event_type)}
              </span>
            </td>
            <td>{event.aircraft_hex || '—'}</td>
            <td>{formatRegionName(event.region_code)}</td>
            <td>
              {event.event_value === null ||
              event.event_value === undefined
                ? '—'
                : formatDecimal(event.event_value)}
            </td>
            <td className="event-description">
              {event.event_description || '—'}
            </td>
          </tr>
        ))}
      </tbody>
    </DataTable>
  )
}

function DataTable({ children }) {
  return <div className="data-table-wrapper"><table className="data-table">{children}</table></div>
}

function MetricRow({ label, value }) {
  return (
    <div className="metric-row">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function ChartLoadingState() {
  return (
    <div className="chart-loading-state">
      <div className="chart-loading-spinner" />
      <strong>Loading live analytics</strong>
      <span>Waiting for the current API response.</span>
    </div>
  )
}

function RegionalTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null

  return (
    <div className="chart-tooltip">
      <strong>{formatRegionName(label)}</strong>
      <span>
        Positions: {formatNumber(payload[0]?.value)}
      </span>
    </div>
  )
}

function RegionalComparisonTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null

  return (
    <div className="chart-tooltip">
      <strong>{formatRegionName(label)}</strong>
      {payload.map((item) => (
        <span key={item.dataKey}>
          {item.name}: {formatNumber(item.value)}
        </span>
      ))}
    </div>
  )
}

function formatEventType(value) {
  if (!value) return 'Other'

  return String(value)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase())
}

function buildTimeseries(data) {
  const buckets = {}

  data.forEach((item) => {
    const time = item.time_bucket

    if (!buckets[time]) {
      buckets[time] = { time_bucket: time }
    }

    buckets[time][item.region_code] = Number(item.position_count || 0)
  })

  return Object.values(buckets).sort(
    (a, b) =>
      new Date(a.time_bucket).getTime() -
      new Date(b.time_bucket).getTime(),
  )
}

function buildEventTimeline(events) {
  const buckets = {}

  events.forEach((event) => {
    if (!event.event_time) return

    const date = new Date(event.event_time)

    if (Number.isNaN(date.getTime())) return

    date.setSeconds(0, 0)
    const key = date.toISOString()

    buckets[key] = (buckets[key] || 0) + 1
  })

  return Object.entries(buckets)
    .map(([time, count]) => ({ time, count }))
    .sort(
      (a, b) =>
        new Date(a.time).getTime() - new Date(b.time).getTime(),
    )
    .slice(-30)
}

export default App
