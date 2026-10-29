# Architecture & Technical Decisions (FS-7)

## 1. What We Built
We engineered an enterprise-ready, full-stack AI image generation platform tailored for marketing creators. Built with **React (Vite)**, **Bootstrap 5**, **Django REST Framework (Python 3.10+)**, and **MySQL 8.x**, the solution automates the generation of brand-aligned visual assets across standard dimensions (**Tile 864×770**, **Banner 1024×500**, **Timeline Card 784×500**) and arbitrary custom dimensions.

## 2. Architecture & Design Decisions

### Brand Profiles & Prompt Engineering
Rather than costly model fine-tuning, branding consistency is achieved procedurally. Each brand (`Campus Life`, `Carelon.engage`, `LifeCykul`, `Zap Creative`) defines an expressive style prompt and accent hex color. The backend prepends these style constraints with compositional directives before dispatching to the AI generator, producing consistently on-brand results.

### Refinement Loop & Prompt Accumulation Strategy
Refinements are modeled as a hierarchical round tree linked by `parent_image_id`. When a user selects a variation and inputs a revision, the backend traces the lineage back to the root, concatenating the thread's `original_prompt` with all prior round directives. This preserves context continuity across multi-round evolutionary iterations without losing the original marketing intent.

### Parametric Template Engine
Built purely with Pillow (`ImageDraw` / `ImageFont`), the template engine features 6 parametric layouts (`diagonal_swoosh`, `dot_grid_corner`, `color_band_bottom`, `framing_border`, `gradient_fade`, and `duotone_accent`). Each layout dynamically injects brand accent colors, geometric badges, dot-matrices, and typography zones, ensuring visual variety without static asset dependencies.

### Dimension & Unit Resolution
The platform enforces non-negotiable target dimensions via server-side center cover crop (`LANCZOS`). Custom dimensions in centimeters or feet are converted at a standard **96 DPI** (`px = cm / 2.54 * 96`, `px = ft * 12 / 2.54 * 96`), clamped to a safe 64px–4000px range. Saved assets adhere strictly to `{image_type}_{width}x{height}_{id}.png`.

## 3. What Was Skipped & Future Improvements
In accordance with scope guardrails, user authentication, heavy cloud storage (S3), and localized inpainting masks were omitted. Future enhancements will introduce WebSocket progress streaming, bulk zip downloads, and SVG vector export.
