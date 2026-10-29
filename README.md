# FS-7 AI Marketing Visuals Platform

An enterprise-ready, full-stack AI image generation platform tailored for marketing creators. Built with **React 19 (Vite)**, **Bootstrap 5**, **Django REST Framework (Python 3.10+)**, and **MySQL 8.x**.

Automates the generation of brand-aligned visual assets across standard marketing dimensions (**Tile 864×770**, **Banner 1024×500**, **Timeline Card 784×500**) and arbitrary custom dimensions with a parametric Pillow compositing engine and multi-round iterative refinement.

---

## Features

- **Brand Profiles & Procedural Style Injection**: Preconfigured brand profiles (`Campus Life`, `Carelon.engage`, `LifeCykul`, `Zap Creative`) that procedurally inject brand style guidelines and accent colors into the AI generation loop.
- **Parametric Pillow Compositing Engine**: 6 parametric overlay layouts (`diagonal_swoosh`, `dot_grid_corner`, `color_band_bottom`, `framing_border`, `gradient_fade`, `duotone_accent`) featuring dynamic typography zones, dot matrices, and brand badge pills.
- **Multi-Round Refinement Loop**: Hierarchical lineage tracking (`parent_image_id`) preserving conversational prompt history across evolutionary rounds.
- **Fixed & Custom Dimension Handling**: Precise 96 DPI conversion for physical units (`cm`, `ft`, `px`) with center-cover cropping (LANCZOS).
- **Flexible GenAI Providers**: Built-in support for Stability AI (SDXL), OpenAI (DALL-E), Google Gemini (Imagen 3), and automatic fallback to Pollinations Diffusion.
- **Asset Library**: Filterable library with direct asset preview and download named per standard conventions (`{image_type}_{width}x{height}_{id}.png`).

---

## Tech Stack

- **Frontend**: React 19, Vite, Bootstrap 5, Bootstrap Icons, Axios
- **Backend**: Django 5.2 / Django REST Framework, Pillow, Requests, python-dotenv
- **Database**: MySQL 8.x (with schema migrations)

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ & npm
- MySQL Server 8.x

### 1. Database Setup

Create the database and seed the default brand profiles:

```sql
mysql -u root -p < schema.sql
```

### 2. Backend Setup

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your MySQL credentials and optional AI API keys

# Apply migrations
python manage.py migrate

# Seed brand profiles (if not loaded via schema.sql)
python manage.py seed_brands

# Start development server
python manage.py runserver
```

Backend will be running at `http://127.0.0.1:8000/`.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Frontend will be running at `http://localhost:5173/`.

---

## Project Structure

```text
├── backend/
│   ├── config/            # Django project settings & URLs
│   ├── generator/         # Core image generation & refinement app
│   │   ├── models.py      # BrandProfile, GenerationThread, GeneratedImage
│   │   ├── views.py       # REST API endpoints
│   │   ├── services.py    # Multi-provider AI dispatch & fallback
│   │   └── templates.py   # Parametric Pillow compositing engine
│   ├── media/             # Saved marketing image assets
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Navbar, GenerationPanel, RefinementPanel, ImageLibrary
│   │   ├── services/      # Axios API client & DPI calculator
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── schema.sql             # MySQL schema & initial seed data
├── DECISIONS.md           # Architecture and technical design documentation
└── README.md
```
