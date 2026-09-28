import { useEffect, useMemo, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Free, no-API-key basemaps. Swap for Mapbox/MapTiler tiles if you outgrow
// CARTO's usage terms for a production/commercial deployment.
const TILE_LIGHT = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const TILE_DARK = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

function altitudeColor(altitude) {
  if (altitude === null || altitude === undefined) return '#64748b'
  if (altitude < 10000) return '#c84b4b'
  if (altitude < 25000) return '#e0a94a'
  if (altitude < 35000) return '#35a9c6'
  return '#087ea4'
}

// NOTE: adjust the field name here if your API exposes true heading under
// a different key than `track` / `heading` / `true_heading`.
function getHeading(item) {
  const value = item.track ?? item.heading ?? item.true_heading ?? null
  return Number.isFinite(Number(value)) ? Number(value) : 0
}

function planeIcon(heading, color) {
  const html = `
    <div class="aircraft-icon-inner" style="transform: rotate(${heading}deg);">
      <svg width="18" height="18" viewBox="0 0 24 24">
        <path
          d="M12 2 L15 10 L22 13 L22 15 L15 13.5 L13.5 20 L16 22 L16 23 L12 22 L8 23 L8 22 L10.5 20 L9 13.5 L2 15 L2 13 L9 10 Z"
          fill="${color}"
          stroke="white"
          stroke-width="0.8"
        />
      </svg>
    </div>`

  return L.divIcon({
    html,
    className: 'aircraft-icon',
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  })
}

function FitToAircraft({ aircraft, hasFit }) {
  const map = useMap()

  useEffect(() => {
    if (hasFit.current || !aircraft.length) return

    const bounds = L.latLngBounds(
      aircraft.map((item) => [Number(item.latitude), Number(item.longitude)]),
    )

    map.fitBounds(bounds, { padding: [30, 30] })
    hasFit.current = true
  }, [aircraft, map, hasFit])

  return null
}

export default function AircraftMap({
  aircraft,
  theme = 'light',
  onSelectAircraft,
}) {
  const hasFit = useRef(false)

  const plotted = useMemo(
    () =>
      aircraft.filter(
        (item) =>
          Number.isFinite(Number(item.latitude)) &&
          Number.isFinite(Number(item.longitude)),
      ),
    [aircraft],
  )

  if (!plotted.length) {
    return (
      <div className="map-empty-state">
        <div className="chart-loading-spinner" />
        <strong>Waiting for aircraft positions</strong>
        <span>No ADS-B coordinates in the current feed.</span>
      </div>
    )
  }

  const center = [
    plotted.reduce((sum, item) => sum + Number(item.latitude), 0) /
      plotted.length,
    plotted.reduce((sum, item) => sum + Number(item.longitude), 0) /
      plotted.length,
  ]

  return (
    <div className="live-map-real">
      <div className="map-label">
        LIVE ADS-B POSITIONS · {plotted.length} AIRCRAFT
      </div>

      <div className="leaflet-shell">
        <MapContainer
          center={center}
          zoom={6}
          scrollWheelZoom
          className="leaflet-container-custom"
        >
          <TileLayer
            key={theme}
            url={theme === 'dark' ? TILE_DARK : TILE_LIGHT}
            attribution='&copy; OpenStreetMap contributors'
          />

          <FitToAircraft aircraft={plotted} hasFit={hasFit} />

          {plotted.slice(0, 600).map((item) => {
            const altitude = item.altitude_baro ?? item.altitude_geom ?? null
            const speed = item.ground_speed ?? null

            return (
              <Marker
                key={`${item.aircraft_hex}-${item.observed_at}`}
                position={[Number(item.latitude), Number(item.longitude)]}
                icon={planeIcon(getHeading(item), altitudeColor(altitude))}
                eventHandlers={{
                  click: () => onSelectAircraft?.(item),
                }}
              >
                <Popup>
                  <strong>
                    {item.callsign || item.registration || item.aircraft_hex}
                  </strong>
                  <br />
                  {altitude !== null
                    ? `${Math.round(altitude).toLocaleString()} ft`
                    : '—'}
                  {' · '}
                  {speed !== null && speed !== undefined
                    ? `${Number(speed).toFixed(0)} kt`
                    : '—'}
                </Popup>
              </Marker>
            )
          })}
        </MapContainer>
      </div>

      <div className="map-legend">
        <span>
          <i style={{ background: '#c84b4b' }} /> Below 10,000 ft
        </span>
        <span>
          <i style={{ background: '#e0a94a' }} /> 10,000–25,000 ft
        </span>
        <span>
          <i style={{ background: '#35a9c6' }} /> 25,000–35,000 ft
        </span>
        <span>
          <i style={{ background: '#087ea4' }} /> Above 35,000 ft
        </span>
      </div>
    </div>
  )
}