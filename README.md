<div align="center">

  <img src="frontend/assets/structura-icon.png" alt="Structura Forge" width="112" height="112" style="border-radius: 22px; border: 1px solid rgba(16, 185, 129, 0.35); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);" />

  # Structura Forge

  **PostgreSQL Schema Visualizer & Relational Synthetic Data Engine**

  *Inspect live schemas, generate relational entity diagrams, and stream high-volume mock data with strict referential integrity.*

  <br />

  <p align="center">
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11+-10B981?style=flat&logo=python&logoColor=white" alt="Python 3.11+" /></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.110+-059669?style=flat&logo=fastapi&logoColor=white" alt="FastAPI" /></a>
    <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-14+-047857?style=flat&logo=postgresql&logoColor=white" alt="PostgreSQL" /></a>
    <img src="https://img.shields.io/badge/Telemetry-Zero-10B981?style=flat" alt="Zero Telemetry" />
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-065F46?style=flat" alt="MIT License" /></a>
  </p>

</div>

---

<div align="center">

<img src="frontend/assets/tui-banner.svg" alt="Structura Forge Terminal Banner" width="760" />

</div>

---

## Overview

Working with complex PostgreSQL schemas often presents two core developer friction points:
1. **Schema comprehension:** Tracing primary keys, composite foreign keys, and multi-level relationship hierarchies across dozens of tables.
2. **Realistic data population:** Generating thousands of realistic records without triggering constraint violations, duplicate key collisions, or missing parent foreign key dependencies.

**Structura Forge** provides a self-contained local workspace to address both via two complementary interfaces: an **Interactive Terminal (TUI)** and a **Local Web Studio**. Everything runs strictly on `localhost` with zero telemetry and zero cloud dependencies.

---

## Interfaces

### 1. Terminal Console (TUI)
Designed for speed and keyboard-driven workflows directly in your shell:
- Launch via `python structura.py`.
- Color-coded schema trees, relationship mapping, and live ASCII diagrams.
- Real-time animated progress bars during multi-batch row injection.
- Option to generate Mermaid ERD blueprints (`erd_blueprint.md`) on demand.

### 2. Local Web Studio (`http://localhost:8000`)
Designed for visual inspection and interactive operations:
- Launch via `python structura.py --web` (or `uvicorn backend.main:app --port 8000`).
- Canvas with pan, zoom (<kbd>+</kbd> / <kbd>−</kbd>), auto-fit (<kbd>F</kbd>), and instant SVG export.
- Quick table lookup with fuzzy search (<kbd>Ctrl</kbd> + <kbd>K</kbd>).
- Seeding drawer to preview generated sample rows and inject 100 to 50,000 rows with single-click execution.

---

## Database Setup & Reference Test Schema

Structura Forge works with your existing PostgreSQL databases or with the built-in reference schema provided in this repository.

### Built-in 6-Table Test Schema
The repository includes a ready-to-use e-commerce schema located at [`backend/test_schema.sql`](backend/test_schema.sql) covering realistic relational patterns:
- **`users`** &rarr; **`orders`** &rarr; **`order_items`** &larr; **`products`** &larr; **`categories`** (self-referencing parent category)
- **`audit_logs`** with `jsonb` payloads and foreign key references

#### Option A: Initialize Directly via TUI
1. Run `python structura.py`.
2. Choose **`6`** (Connection & Test Database Setup).
3. Confirm deployment — Structura Forge will automatically execute `test_schema.sql` on your target database.

#### Option B: Initialize via `psql`
```bash
psql -U postgres -d postgres -f backend/test_schema.sql
```

#### Option C: Offline Preview Sandbox
If PostgreSQL is offline or credentials are not yet configured, Structura Forge automatically prompts to enter **Preview Sandbox Mode**. This uses built-in schema fixtures so you can explore all visual diagrams and seeding workflows immediately.

---

## Quickstart

### 1. Installation

```bash
# Clone repository
git clone https://github.com/syedhaziqzia/structura-forge.git
cd structura-forge

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment configuration:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Set your database credentials in `.env`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/postgres
PORT=8000
HOST=127.0.0.1
```

---

## Usage Guide

### Terminal User Interface (TUI)

```bash
python structura.py
```

| Key | Action |
| :---: | :--- |
| `1` | Inspect database schema as a color-coded hierarchy tree |
| `2` | Compile and export Mermaid ERD blueprint to `erd_blueprint.md` |
| `3` | Execute relational mock data injection with real-time progress bars |
| `4` | Launch and open the local Web Studio in your browser |
| `6` | Configure connection settings or deploy the built-in test database |
| `5` | Exit |

---

### Local Web Studio

```bash
python structura.py --web
```

Open `http://localhost:8000` in your browser.

| Shortcut | Action |
| :--- | :--- |
| <kbd>Ctrl</kbd> + <kbd>K</kbd> | Search and focus table |
| <kbd>R</kbd> | Refresh schema topology |
| <kbd>Enter</kbd> | Trigger data injection on active table |
| <kbd>F</kbd> | Fit diagram to viewport |
| <kbd>+</kbd> / <kbd>−</kbd> | Zoom in / Zoom out |
| <kbd>0</kbd> | Reset zoom level to 100% |
| <kbd>G</kbd> | View Mermaid ERD definition |
| <kbd>Esc</kbd> | Dismiss active modal or overlay |

---

## Project Structure

```text
structura-forge/
├── structura.py                # Unified CLI & Terminal interface
├── requirements.txt            # Python dependencies
├── specs.md                    # Technical specification & architecture
├── erd_blueprint.md            # Exported Mermaid entity diagram
├── .env.example               # Environment variables template
├── LICENSE                     # MIT License
├── backend/
│   ├── main.py                 # FastAPI backend & data generator engine
│   └── test_schema.sql         # 6-table reference test database
└── frontend/
    ├── index.html              # Web Studio interface
    └── assets/
        ├── structura-icon.png  # Application icon
        └── tui-banner.svg      # Terminal banner asset
```

---

## Security Model

- **Zero Telemetry:** Operates exclusively offline on loopback (`127.0.0.1`). No metrics, diagnostics, or payloads are transmitted externally.
- **Sanitized Execution:** Employs parameterized queries and strict SQL identifier escaping (`psycopg2.sql`) to prevent injection vulnerabilities.
- **Credential Protection:** Connection strings and passwords are masked across CLI logs and web responses.

---

## License

Distributed under the [MIT License](LICENSE). Built for local PostgreSQL workflows.
