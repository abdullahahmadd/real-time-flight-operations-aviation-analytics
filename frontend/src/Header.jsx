import { useEffect, useState } from 'react'

function useKsaClock() {
  const [now, setNow] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000)

    return () => clearInterval(timer)
  }, [])

  return now
}

function formatKsaTime(date) {
  return date.toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
    timeZone: 'Asia/Riyadh',
  })
}

function formatKsaDate(date) {
  const parts = new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    timeZone: 'Asia/Riyadh',
  }).formatToParts(date)

  const day = parts.find((part) => part.type === 'day')?.value
  const month = parts.find((part) => part.type === 'month')?.value
  const year = parts.find((part) => part.type === 'year')?.value

  return `${day}-${month}-${year}`
}

export default function Header({
  navigation,
  activeSection,
  onNavigate,
  apiOnline,
  theme,
  onToggleTheme,
}) {
  const [menuOpen, setMenuOpen] = useState(false)
  const ksaNow = useKsaClock()

  const handleNavigate = (id) => {
    onNavigate(id)
    setMenuOpen(false)
  }

  return (
    <header className="site-header">
      <div className="header-inner">
        <button
          className="brand"
          type="button"
          onClick={() => handleNavigate('overview')}
        >
          <div className="brand-mark" aria-hidden="true">
            <span className="brand-plane">✈</span>
          </div>

          <div className="brand-text">
            <strong>Real-Time Flight Operations</strong>
            <span>Aviation Analytics Platform</span>
          </div>
        </button>

        <nav
          className={
            menuOpen
              ? 'main-navigation open'
              : 'main-navigation'
          }
          aria-label="Main navigation"
        >
          {navigation.map((item) => (
            <button
              key={item.id}
              type="button"
              className={
                activeSection === item.id
                  ? 'nav-item active'
                  : 'nav-item'
              }
              onClick={() => handleNavigate(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="header-meta">
          <div
            className="ksa-clock"
            title="Saudi Arabia Standard Time"
            aria-label={`Current Saudi Arabia time ${formatKsaTime(
              ksaNow,
            )} on ${formatKsaDate(ksaNow)}`}
          >
            <span className="ksa-label">KSA TIME</span>

            <strong>{formatKsaTime(ksaNow)}</strong>

            <span className="ksa-date">
              {formatKsaDate(ksaNow)}
            </span>
          </div>

          <button
            type="button"
            className="theme-toggle"
            onClick={onToggleTheme}
            aria-label={
              theme === 'dark'
                ? 'Switch to light theme'
                : 'Switch to dark theme'
            }
            title={
              theme === 'dark'
                ? 'Switch to light theme'
                : 'Switch to dark theme'
            }
          >
            {theme === 'dark' ? '☀' : '☾'}
          </button>

          <div className="live-indicator">
            <span
              className={
                apiOnline
                  ? 'live-dot'
                  : 'live-dot offline'
              }
            />

            <div className="live-status-text">
              <strong>
                {apiOnline ? 'LIVE' : 'OFFLINE'}
              </strong>

              <span>
                {apiOnline
                  ? 'Live data'
                  : 'Data unavailable'}
              </span>
            </div>
          </div>

          <button
            type="button"
            className={
              menuOpen
                ? 'menu-toggle open'
                : 'menu-toggle'
            }
            aria-label="Toggle navigation menu"
            aria-expanded={menuOpen}
            onClick={() =>
              setMenuOpen((open) => !open)
            }
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </div>
    </header>
  )
}