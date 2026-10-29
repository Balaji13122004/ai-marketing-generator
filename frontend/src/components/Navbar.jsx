import React from 'react';

export default function Navbar({ brandCount = 0, libraryCount = 0 }) {
  return (
    <nav className="app-navbar mb-4">
      <div className="container">
        <div className="d-flex align-items-center justify-content-between flex-wrap gap-3">
          <div className="d-flex align-items-center gap-3">
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: 12,
                background: 'linear-gradient(135deg, #3377FF, #2659BF)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontSize: 22,
                boxShadow: '0 4px 14px rgba(51, 119, 255, 0.35)',
              }}
            >
              <i className="bi bi-palette"></i>
            </div>
            <div>
              <div className="d-flex align-items-center gap-2">
                <h1 className="h5 mb-0 fw-bold" style={{ color: 'var(--color-dark-1)' }}>
                  FS-7 AI Creative Platform
                </h1>
                <span className="brand-badge">
                  <i className="bi bi-stars"></i> GenAI Studio
                </span>
              </div>
              <small style={{ color: 'var(--color-dark-2)', fontSize: 13 }}>
                On-Brand Marketing Visuals • Parametric Compositing • Multi-Round Refinement
              </small>
            </div>
          </div>

          <div className="d-flex align-items-center gap-3">
            <a href="#generation-panel" className="btn btn-sm btn-secondary-custom">
              <i className="bi bi-magic"></i> Generator{brandCount > 0 ? ` (${brandCount} Brands)` : ''}
            </a>
            <a href="#refinement-panel" className="btn btn-sm btn-secondary-custom">
              <i className="bi bi-chat-dots"></i> Refinement Loop
            </a>
            <a href="#image-library" className="btn btn-sm btn-secondary-custom">
              <i className="bi bi-collection"></i> Library ({libraryCount})
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}
