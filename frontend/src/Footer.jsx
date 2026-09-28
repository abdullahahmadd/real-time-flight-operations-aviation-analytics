export default function Footer({ dataSource = 'ADSB.lol' }) {
  const year = new Date().getFullYear()

  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-top">
          <div className="footer-brand-block">
            <span className="footer-project-name">
              Real-Time Flight Operations &amp; Aviation Analytics
            </span>

            <p className="footer-disclaimer">
              Data is sourced from public ADS-B feeds and refreshed
              continuously for analytical purposes only. It is not intended
              for navigation, air traffic control, or any safety-critical
              operational use.
            </p>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="footer-meta">
            <span>© {year} Real-Time Flight Operations</span>

            <span className="footer-divider" aria-hidden="true">
              •
            </span>

            <span>
              Live data via {dataSource} · refreshed every 2 seconds
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
      </div>
    </footer>
  )
}