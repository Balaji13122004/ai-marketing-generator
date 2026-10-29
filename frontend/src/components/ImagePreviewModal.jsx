import React from 'react';

export default function ImagePreviewModal({ image, onClose }) {
  if (!image) return null;

  const handleDownload = async () => {
    try {
      const response = await fetch(image.image_url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const parts = image.image_url.split('/');
      link.download = parts[parts.length - 1] || `image_${image.id}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.warn('Direct download failed, opening in new tab:', err);
      window.open(image.image_url, '_blank');
    }
  };

  return (
    <div
      className="modal fade show d-block"
      tabIndex="-1"
      style={{ backgroundColor: 'rgba(15, 23, 42, 0.75)', backdropFilter: 'blur(6px)', zIndex: 1050 }}
      onClick={onClose}
    >
      <div
        className="modal-dialog modal-xl modal-dialog-centered"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-content shadow-lg border-0 overflow-hidden" style={{ borderRadius: 16 }}>
          <div className="modal-header bg-white border-bottom px-4 py-3">
            <div>
              <h5 className="modal-title fw-bold mb-0">
                Image #{image.id} — {image.app_name || 'Marketing Asset'}
              </h5>
              <small className="text-muted">
                {image.image_type} • {image.width} × {image.height} px • Template: {image.template_used || 'Standard'}
              </small>
            </div>
            <button
              type="button"
              className="btn-close"
              aria-label="Close"
              onClick={onClose}
            ></button>
          </div>

          <div className="modal-body p-0 bg-dark text-center" style={{ maxHeight: '75vh', overflow: 'auto' }}>
            <img
              src={image.image_url}
              alt={`Full view #${image.id}`}
              style={{ maxWidth: '100%', maxHeight: '75vh', objectFit: 'contain' }}
            />
          </div>

          <div className="modal-footer bg-white border-top px-4 py-3 d-flex align-items-center justify-content-between">
            <div className="text-muted small">
              <code>{image.image_url}</code>
            </div>

            <div className="d-flex align-items-center gap-2">
              <button
                type="button"
                className="btn btn-secondary-custom"
                onClick={onClose}
              >
                Close
              </button>
              <button
                type="button"
                className="btn btn-primary-custom"
                onClick={handleDownload}
              >
                <i className="bi bi-download"></i> Download Asset
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
