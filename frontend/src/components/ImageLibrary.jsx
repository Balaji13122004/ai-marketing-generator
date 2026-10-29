import React, { useState } from 'react';

const TYPE_FILTERS = [
  { id: 'All', label: 'All Formats' },
  { id: 'tile', label: 'Tile' },
  { id: 'banner', label: 'Banner' },
  { id: 'timeline_card', label: 'Timeline Card' },
  { id: 'custom', label: 'Custom' },
];

export default function ImageLibrary({
  images = [],
  brands = [],
  selectedApp,
  onAppFilterChange,
  selectedType,
  onTypeFilterChange,
  onPreviewImage,
  onRefresh,
}) {
  const [copiedId, setCopiedId] = useState(null);

  const handleDownload = async (img) => {
    try {
      const response = await fetch(img.image_url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      // Extract or compute standard filename: {image_type}_{width}x{height}_{id}.png
      const parts = img.image_url.split('/');
      const filename = parts[parts.length - 1] || `image_${img.id}.png`;
      link.download = filename;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download error:', err);
      // Fallback: direct window open
      window.open(img.image_url, '_blank');
    }
  };

  const handleCopyLink = (img) => {
    const fullUrl = window.location.origin + img.image_url;
    navigator.clipboard.writeText(fullUrl);
    setCopiedId(img.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div id="image-library" className="custom-card">
      <div className="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">
        <div>
          <h2 className="card-section-title">
            <i className="bi bi-collection" style={{ color: 'var(--color-main)' }}></i>
            Section 3 — Generated Marketing Image Library
          </h2>
          <p className="card-section-subtitle mb-0">
            Browse, filter, preview, and download all generated and composited assets across all threads.
          </p>
        </div>

        <button
          type="button"
          className="btn btn-secondary-custom btn-sm"
          onClick={onRefresh}
          title="Refresh Library"
        >
          <i className="bi bi-arrow-clockwise"></i> Refresh
        </button>
      </div>

      {/* Filter Bar */}
      <div className="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-4 pb-3 border-bottom">
        {/* Type Filter Pills */}
        <div className="d-flex flex-wrap gap-2">
          {TYPE_FILTERS.map((f) => (
            <button
              key={f.id}
              type="button"
              className={`filter-btn ${selectedType === f.id ? 'active' : ''}`}
              onClick={() => onTypeFilterChange(f.id)}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Brand Dropdown Filter */}
        <div className="d-flex align-items-center gap-2">
          <label className="text-muted small fw-semibold text-nowrap" htmlFor="brandFilterSelect">
            Filter by Brand:
          </label>
          <select
            id="brandFilterSelect"
            className="form-select form-select-sm"
            style={{ width: 'auto', minWidth: 170 }}
            value={selectedApp}
            onChange={(e) => onAppFilterChange(e.target.value)}
          >
            <option value="All">All Brands</option>
            {brands.map((b) => (
              <option key={b.id} value={b.app_name}>
                {b.app_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Images Grid */}
      {images.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">
            <i className="bi bi-images"></i>
          </div>
          <h5 className="fw-bold">No Generated Images Found</h5>
          <p className="text-muted mb-0">
            {selectedType !== 'All' || selectedApp !== 'All'
              ? 'Try adjusting your filters above to see more assets.'
              : 'Generate your first set of images above to see them in this library.'}
          </p>
        </div>
      ) : (
        <div className="row g-4">
          {images.map((img) => {
            const cleanType = (img.image_type || 'image').replace(/_/g, ' ');

            return (
              <div key={img.id} className="col-sm-6 col-lg-4 col-xl-3">
                <div className="image-variation-card h-100 shadow-sm">
                  {/* Template Badge */}
                  {img.template_used && (
                    <div className="template-badge-pill">
                      {img.template_used.replace(/_/g, ' ')}
                    </div>
                  )}

                  {/* Image Thumbnail */}
                  <div
                    className="image-wrapper"
                    style={{ cursor: 'pointer' }}
                    onClick={() => onPreviewImage(img)}
                  >
                    <img
                      src={img.image_url}
                      alt={`Image #${img.id}`}
                      loading="lazy"
                    />
                  </div>

                  {/* Card Body & Details */}
                  <div className="p-3 bg-white flex-grow-1 d-flex flex-column justify-content-between">
                    <div>
                      <div className="d-flex align-items-center justify-content-between mb-2">
                        <span className="badge bg-light text-dark border">
                          #{img.id} • {cleanType}
                        </span>
                        <span className="badge bg-primary-subtle text-primary border border-primary">
                          {img.width} × {img.height} px
                        </span>
                      </div>

                      <div className="fw-bold text-truncate mb-1" style={{ fontSize: 14 }}>
                        {img.app_name || 'Marketing Creative'}
                      </div>

                      <small className="text-muted d-block text-truncate mb-2" style={{ fontSize: 12 }}>
                        {img.prompt_text || 'AI Generated Asset'}
                      </small>
                    </div>

                    {/* Action Buttons */}
                    <div className="d-flex align-items-center gap-2 pt-2 border-top">
                      <button
                        type="button"
                        className="btn btn-sm btn-primary flex-grow-1 d-flex align-items-center justify-content-center gap-1"
                        onClick={() => handleDownload(img)}
                        title="Download with standard naming convention"
                      >
                        <i className="bi bi-download"></i> Download
                      </button>

                      <button
                        type="button"
                        className="btn btn-sm btn-outline-secondary"
                        onClick={() => handleCopyLink(img)}
                        title="Copy direct file link"
                      >
                        {copiedId === img.id ? (
                          <i className="bi bi-check text-success"></i>
                        ) : (
                          <i className="bi bi-link-45deg"></i>
                        )}
                      </button>

                      <button
                        type="button"
                        className="btn btn-sm btn-outline-secondary"
                        onClick={() => onPreviewImage(img)}
                        title="Preview full screen"
                      >
                        <i className="bi bi-arrows-angle-expand"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
