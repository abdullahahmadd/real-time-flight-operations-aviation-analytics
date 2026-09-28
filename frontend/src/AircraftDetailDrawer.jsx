function formatRegion(value) {
  if (!value) return 'Unknown'

  return String(value)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase())
}

function DrawerRow({ label, value }) {
  return (
    <div className="drawer-row">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

export default function AircraftDetailDrawer({ aircraft, onClose }) {
  if (!aircraft) return null

  const altitude = aircraft.altitude_baro ?? aircraft.altitude_geom ?? null
  const speed = aircraft.ground_speed ?? null
  const verticalRate = aircraft.vertical_rate

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <aside
        className="drawer-panel"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="drawer-header">
          <div>
            <span className="drawer-eyebrow">AIRCRAFT DETAIL</span>
            <h3>
              {aircraft.callsign || aircraft.registration || aircraft.aircraft_hex}
            </h3>
          </div>

          <button
            type="button"
            className="drawer-close"
            onClick={onClose}
            aria-label="Close detail panel"
          >
            ×
          </button>
        </div>

        <div className="drawer-body">
          <DrawerRow label="Registration" value={aircraft.registration || '—'} />
          <DrawerRow label="Aircraft type" value={aircraft.aircraft_type || '—'} />
          <DrawerRow label="ICAO hex" value={aircraft.aircraft_hex || '—'} />
          <DrawerRow label="Region" value={formatRegion(aircraft.region_code)} />
          <DrawerRow
            label="Altitude"
            value={
              altitude === null || altitude === undefined
                ? '—'
                : `${Math.round(altitude).toLocaleString()} ft`
            }
          />
          <DrawerRow
            label="Ground speed"
            value={
              speed === null || speed === undefined
                ? '—'
                : `${Number(speed).toFixed(1)} kt`
            }
          />
          <DrawerRow
            label="Vertical rate"
            value={
              verticalRate === null || verticalRate === undefined
                ? '—'
                : `${Math.round(verticalRate).toLocaleString()} fpm`
            }
          />
          <DrawerRow
            label="Position"
            value={
              aircraft.latitude && aircraft.longitude
                ? `${Number(aircraft.latitude).toFixed(3)}°, ${Number(
                    aircraft.longitude,
                  ).toFixed(3)}°`
                : '—'
            }
          />
          <DrawerRow
            label="Last observed"
            value={
              aircraft.observed_at
                ? new Date(aircraft.observed_at).toLocaleString()
                : '—'
            }
          />
        </div>
      </aside>
    </div>
  )
}