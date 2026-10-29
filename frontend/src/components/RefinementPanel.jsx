import React, { useState } from 'react';

export default function RefinementPanel({
  threadData,
  onRefine,
  isRefining,
  onSelectImage,
  onPreviewImage,
  refineError,
}) {
  const [selectedImageId, setSelectedImageId] = useState(null);
  const [refinementInstruction, setRefinementInstruction] = useState('');

  if (!threadData || !threadData.rounds || threadData.rounds.length === 0) {
    return (
      <div id="refinement-panel" className="custom-card">
        <h2 className="card-section-title">
          <i className="bi bi-chat-dots" style={{ color: 'var(--color-main)' }}></i>
          Section 2 — Refinement Chat Panel
        </h2>
        <div className="empty-state py-5">
          <div className="empty-state-icon">
            <i className="bi bi-arrow-repeat"></i>
          </div>
          <h5 className="fw-bold">No Active Refinement Thread</h5>
          <p className="text-muted mb-0">
            Generate an image in Section 1 to unlock the multi-round conversational refinement loop.
          </p>
        </div>
      </div>
    );
  }

  const handleRefineSubmit = (e) => {
    e.preventDefault();
    if (!selectedImageId) {
      alert('Please click on one of the 3 images to select it for refinement!');
      return;
    }
    if (!refinementInstruction.trim()) {
      alert('Please enter a refinement instruction (e.g. "make the lighting warmer", "remove background clutter")');
      return;
    }

    onRefine({
      selected_image_id: selectedImageId,
      refinement_instruction: refinementInstruction.trim(),
    });

    setRefinementInstruction('');
  };

  return (
    <div id="refinement-panel" className="custom-card">
      <div className="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-2">
        <div>
          <h2 className="card-section-title">
            <i className="bi bi-chat-dots" style={{ color: 'var(--color-main)' }}></i>
            Section 2 — Refinement Chat Panel
          </h2>
          <p className="card-section-subtitle mb-0">
            Pick your favorite variation, describe what to adjust, and iterate through multiple rounds.
          </p>
        </div>

        <div className="d-flex align-items-center gap-2">
          <span className="badge bg-light text-dark border px-3 py-2 fs-6">
            <i className="bi bi-hash"></i> Thread #{threadData.thread_id}
          </span>
          <span className="badge bg-primary px-3 py-2 fs-6">
            {threadData.app_name} • {threadData.image_type} ({threadData.width_px} × {threadData.height_px} px)
          </span>
        </div>
      </div>

      {refineError && (
        <div className="alert alert-danger d-flex align-items-center gap-2 mb-4" role="alert">
          <i className="bi bi-exclamation-octagon-fill fs-5"></i>
          <div>
            <strong>Refinement Error:</strong> {refineError}
          </div>
        </div>
      )}

      {/* Rounds Stack (Chat-style trail scrolling downward) */}
      <div className="rounds-trail">
        {threadData.rounds.map((round) => {
          const isLatestRound = round.round_number === threadData.rounds.length;

          return (
            <div key={round.round_number} className="round-container">
              <div className="d-flex align-items-center justify-content-between mb-3">
                <span className="round-badge">
                  <i className="bi bi-layers-half"></i>
                  Round {round.round_number} {round.round_number === 1 ? '(Initial Generation)' : '(Refinement)'}
                </span>

                {isLatestRound && (
                  <span className="badge bg-success-subtle text-success border border-success px-3 py-1">
                    <i className="bi bi-check-circle-fill me-1"></i> Active Round (Select an image below)
                  </span>
                )}
              </div>

              {round.refinement_instruction && (
                <div className="refinement-instruction-quote">
                  <i className="bi bi-chat-quote me-2"></i>
                  <strong>Refinement instruction:</strong> "{round.refinement_instruction}"
                </div>
              )}

              {/* 3 Variations in a row */}
              <div className="row g-4">
                {round.images.map((img) => {
                  const isSelectedForNext = selectedImageId === img.id;
                  const isMarkedFinal = img.is_selected;

                  return (
                    <div key={img.id} className="col-md-4">
                      <div
                        className={`image-variation-card h-100 ${isSelectedForNext ? 'selected' : ''}`}
                        onClick={() => setSelectedImageId(img.id)}
                        style={{ cursor: 'pointer' }}
                      >
                        {/* Template Badge */}
                        {img.template_used && (
                          <div className="template-badge-pill">
                            <i className="bi bi-palette2 me-1"></i>
                            {img.template_used.replace(/_/g, ' ')}
                          </div>
                        )}

                        {/* Selected Indicator */}
                        {isSelectedForNext && (
                          <div className="selected-indicator" title="Selected for next refinement">
                            <i className="bi bi-check-lg"></i>
                          </div>
                        )}

                        {/* Image Canvas / Preview */}
                        <div className="image-wrapper">
                          <img
                            src={img.image_url}
                            alt={`Variation ${img.id}`}
                            loading="lazy"
                          />
                        </div>

                        {/* Card Footer Controls */}
                        <div className="variation-card-footer">
                          <div>
                            <span className="fw-bold" style={{ fontSize: 13 }}>
                              #{img.id}
                            </span>
                            <span className="text-muted ms-2" style={{ fontSize: 12 }}>
                              {img.width || threadData.width_px}×{img.height || threadData.height_px}
                            </span>
                          </div>

                          <div className="d-flex align-items-center gap-2">
                            <button
                              type="button"
                              className="btn btn-sm btn-outline-secondary"
                              title="Preview Full Size"
                              onClick={(e) => {
                                e.stopPropagation();
                                onPreviewImage(img);
                              }}
                            >
                              <i className="bi bi-arrows-fullscreen"></i>
                            </button>

                            <button
                              type="button"
                              className={`btn btn-sm ${isMarkedFinal ? 'btn-success' : 'btn-outline-primary'}`}
                              onClick={(e) => {
                                e.stopPropagation();
                                onSelectImage(img.id);
                              }}
                            >
                              <i className="bi bi-star-fill me-1"></i>
                              {isMarkedFinal ? 'Chosen!' : 'Use this one'}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Chat-style Refinement Input Box */}
      <div className="refinement-chat-box">
        <form onSubmit={handleRefineSubmit}>
          <div className="d-flex align-items-center justify-content-between mb-2">
            <label className="form-label mb-0 fw-bold" htmlFor="refineInput">
              <i className="bi bi-chat-square-text me-1 text-primary"></i>
              Not quite right? Tell me what to change...
            </label>
            {selectedImageId ? (
              <span className="badge bg-primary-subtle text-primary border border-primary px-2 py-1">
                Selected Parent: Image #{selectedImageId}
              </span>
            ) : (
              <span className="badge bg-warning-subtle text-warning-emphasis border border-warning px-2 py-1">
                <i className="bi bi-hand-index-thumb me-1"></i> Click an image above to pick it
              </span>
            )}
          </div>

          <div className="input-group">
            <input
              id="refineInput"
              type="text"
              className="form-control form-control-lg"
              placeholder='e.g. "make the background darker and add warmer golden hour lighting..."'
              value={refinementInstruction}
              onChange={(e) => setRefinementInstruction(e.target.value)}
              disabled={isRefining}
            />
            <button
              type="submit"
              className="btn btn-primary-custom"
              disabled={isRefining || !selectedImageId || !refinementInstruction.trim()}
              style={{ padding: '12px 28px' }}
            >
              {isRefining ? (
                <>
                  <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                  <span>Refining...</span>
                </>
              ) : (
                <>
                  <i className="bi bi-arrow-repeat"></i>
                  <span>Refine (Generate 3 New)</span>
                </>
              )}
            </button>
          </div>
          <small className="text-muted mt-2 d-block">
            <i className="bi bi-info-circle me-1"></i>
            This links each new variation to the selected parent image via <code>parent_image_id</code> and records the full round history.
          </small>
        </form>
      </div>
    </div>
  );
}
