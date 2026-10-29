import React, { useState, useMemo } from 'react';
import { calculateCustomPixels } from '../services/api';

const PRESET_FORMATS = [
  { id: 'tile', label: 'Tile', width: 864, height: 770, desc: 'Square-like marketing tiles' },
  { id: 'banner', label: 'Banner', width: 1024, height: 500, desc: 'Wide hero & campaign headers' },
  { id: 'timeline_card', label: 'Timeline Card', width: 784, height: 500, desc: 'Feed & timeline cards' },
  { id: 'custom', label: 'Custom Dimensions', width: null, height: null, desc: 'Specify px, cm, or feet' },
];

const SAMPLE_PROMPTS = [
  "Students collaborating on a laptop at a sunny outdoor campus cafe",
  "A modern healthcare specialist consulting with an elderly patient with care and empathy",
  "High energy cyclist racing through mountain trails during vibrant golden hour",
  "Futuristic digital marketing studio with glowing geometric hologram screens",
];

export default function GenerationPanel({
  brands,
  onGenerate,
  isGenerating,
  error,
  onDismissError,
}) {
  const [selectedBrand, setSelectedBrand] = useState('');
  const [selectedFormat, setSelectedFormat] = useState('banner');
  const [prompt, setPrompt] = useState('');
  const [customWidth, setCustomWidth] = useState(1200);
  const [customHeight, setCustomHeight] = useState(800);
  const [customUnit, setCustomUnit] = useState('px');

  // Derive selected brand with fallback to first brand
  const currentBrand = selectedBrand || (brands.length > 0 ? brands[0].app_name : '');

  const activeBrandProfile = useMemo(() => {
    return brands.find((b) => b.app_name === currentBrand) || null;
  }, [brands, currentBrand]);

  // Live conversion for custom size
  const customConversion = useMemo(() => {
    return calculateCustomPixels(customWidth, customHeight, customUnit);
  }, [customWidth, customHeight, customUnit]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim() || !currentBrand) return;

    onGenerate({
      app_name: currentBrand,
      image_type: selectedFormat,
      prompt: prompt.trim(),
      custom_width: selectedFormat === 'custom' ? customWidth : undefined,
      custom_height: selectedFormat === 'custom' ? customHeight : undefined,
      custom_unit: selectedFormat === 'custom' ? customUnit : undefined,
    });
  };

  return (
    <div id="generation-panel" className="custom-card">
      <div className="d-flex align-items-center justify-content-between mb-3 flex-wrap gap-2">
        <div>
          <h2 className="card-section-title">
            <i className="bi bi-magic" style={{ color: 'var(--color-main)' }}></i>
            Section 1 — Generate Marketing Visuals
          </h2>
          <p className="card-section-subtitle mb-0">
            Pick a branded app, select the required output format, describe your scene, and generate 3 variations.
          </p>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger d-flex align-items-center justify-content-between mb-4" role="alert">
          <div className="d-flex align-items-center gap-2">
            <i className="bi bi-exclamation-triangle-fill fs-5"></i>
            <div>
              <strong>Generation Error:</strong> {error}
            </div>
          </div>
          {onDismissError && (
            <button type="button" className="btn-close" onClick={onDismissError} aria-label="Close"></button>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="row g-4">
          {/* Brand Profile Selector */}
          <div className="col-lg-6">
            <label className="form-label" htmlFor="brandSelect">
              <i className="bi bi-briefcase me-1"></i> Target App & Brand Identity
            </label>
            <select
              id="brandSelect"
              className="form-select form-select-lg"
              value={currentBrand}
              onChange={(e) => setSelectedBrand(e.target.value)}
              required
            >
              {brands.map((b) => (
                <option key={b.id} value={b.app_name}>
                  {b.app_name}
                </option>
              ))}
            </select>

            {activeBrandProfile && (
              <div
                className="mt-3 p-3 rounded-3"
                style={{
                  backgroundColor: 'var(--color-light-4)',
                  border: `1.5px solid ${activeBrandProfile.accent_color || '#3377FF'}`,
                  borderLeftWidth: '6px',
                }}
              >
                <div className="d-flex align-items-center justify-content-between mb-1">
                  <span className="fw-bold" style={{ color: 'var(--color-dark-1)', fontSize: 14 }}>
                    Brand Style Guidelines
                  </span>
                  <span
                    className="badge rounded-pill"
                    style={{
                      backgroundColor: activeBrandProfile.accent_color || '#3377FF',
                      color: '#ffffff',
                    }}
                  >
                    Accent {activeBrandProfile.accent_color}
                  </span>
                </div>
                <small className="text-muted d-block">{activeBrandProfile.style_prompt}</small>
              </div>
            )}
          </div>

          {/* Prompt Input & Chips */}
          <div className="col-lg-6">
            <label className="form-label" htmlFor="promptInput">
              <i className="bi bi-chat-left-text me-1"></i> Image Prompt Description
            </label>
            <textarea
              id="promptInput"
              className="form-control"
              rows="4"
              placeholder="e.g. Energetic students celebrating graduation ceremony in sunny campus courtyard..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              required
            ></textarea>

            <div className="mt-2">
              <small className="text-muted d-block mb-1 fw-semibold">Quick Prompt Ideas:</small>
              <div className="d-flex flex-wrap gap-2">
                {SAMPLE_PROMPTS.map((sp, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="prompt-chip"
                    onClick={() => setPrompt(sp)}
                  >
                    <i className="bi bi-lightbulb"></i> {sp.slice(0, 32)}...
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Design Format Selector */}
          <div className="col-12">
            <label className="form-label mb-2">
              <i className="bi bi-aspect-ratio me-1"></i> Output Design Format (Fixed Mandated Dimensions)
            </label>
            <div className="row g-3">
              {PRESET_FORMATS.map((fmt) => {
                const isActive = selectedFormat === fmt.id;
                return (
                  <div key={fmt.id} className="col-sm-6 col-md-3">
                    <div
                      className={`format-card ${isActive ? 'active' : ''}`}
                      onClick={() => setSelectedFormat(fmt.id)}
                    >
                      <div className="format-card-title">{fmt.label}</div>
                      <div className="format-card-dims">
                        {fmt.width && fmt.height ? `${fmt.width} × ${fmt.height} px` : 'User Defined'}
                      </div>
                      <small className="d-block mt-2 text-muted" style={{ fontSize: 11 }}>
                        {fmt.desc}
                      </small>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Custom Dimension Controls (Visible only when 'custom' selected) */}
          {selectedFormat === 'custom' && (
            <div className="col-12">
              <div className="p-4 rounded-3" style={{ background: 'var(--color-light-3)', border: '1px solid var(--color-light-2)' }}>
                <h6 className="fw-bold mb-3 d-flex align-items-center gap-2">
                  <i className="bi bi-sliders"></i> Custom Dimension Configuration (96 DPI Conversion)
                </h6>
                <div className="row g-3 align-items-center">
                  <div className="col-md-4">
                    <label className="form-label" htmlFor="customWidth">Width</label>
                    <input
                      id="customWidth"
                      type="number"
                      step="any"
                      min="1"
                      max="4000"
                      className="form-control"
                      value={customWidth}
                      onChange={(e) => setCustomWidth(e.target.value)}
                      required
                    />
                  </div>
                  <div className="col-md-4">
                    <label className="form-label" htmlFor="customHeight">Height</label>
                    <input
                      id="customHeight"
                      type="number"
                      step="any"
                      min="1"
                      max="4000"
                      className="form-control"
                      value={customHeight}
                      onChange={(e) => setCustomHeight(e.target.value)}
                      required
                    />
                  </div>
                  <div className="col-md-4">
                    <label className="form-label" htmlFor="customUnit">Measurement Unit</label>
                    <select
                      id="customUnit"
                      className="form-select"
                      value={customUnit}
                      onChange={(e) => setCustomUnit(e.target.value)}
                    >
                      <option value="px">Pixels (px)</option>
                      <option value="cm">Centimeters (cm)</option>
                      <option value="ft">Feet (ft)</option>
                    </select>
                  </div>
                </div>

                <div className="mt-3 p-2 bg-white rounded-2 d-inline-block border">
                  <span className="text-primary fw-bold" style={{ fontSize: 14 }}>
                    <i className="bi bi-info-circle me-1"></i> Resolved Target:
                  </span>{' '}
                  <span className="fw-semibold text-dark">
                    ≈ {customConversion.widthPx} × {customConversion.heightPx} px
                  </span>{' '}
                  <small className="text-muted">(enforces 96 DPI conversion, max 4000×4000 px)</small>
                </div>
              </div>
            </div>
          )}

          {/* Action button */}
          <div className="col-12 d-flex align-items-center justify-content-between flex-wrap gap-3 pt-2">
            <div className="text-muted" style={{ fontSize: 13 }}>
              <i className="bi bi-shield-check text-success me-1"></i>
              Generates 3 variations composited with distinct parametric template layouts.
            </div>

            <button
              type="submit"
              className="btn btn-primary-custom"
              disabled={isGenerating || !prompt.trim()}
            >
              {isGenerating ? (
                <>
                  <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                  <span>Generating 3 Variations...</span>
                </>
              ) : (
                <>
                  <i className="bi bi-stars"></i>
                  <span>Generate 3 Variations</span>
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
