<div align="center">

  <img src="frontend/assets/structura-icon.png" alt="Structura Forge" width="112" height="112" style="border-radius: 22px; border: 1px solid rgba(16, 185, 129, 0.35); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);" />

  # Structura Forge

  **PostgreSQL Schema Visualizer & Relational Synthetic Data Engine**

  *Inspect live schemas, generate relational entity diagrams, and stream high-volume mock data with strict referential integrity.*

  <br />

  <p align="center">
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11+-10B981?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+" /></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.110+-059669?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" /></a>
    <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-14+-047857?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL" /></a>
    <img src="https://img.shields.io/badge/Telemetry-Zero-10B981?style=flat-square" alt="Zero Telemetry" />
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-065F46?style=flat-square" alt="MIT License" /></a>
  </p>

</div>

---

## Overview

Working with complex PostgreSQL schemas often presents two core developer friction points:

1. **Schema comprehension:** Tracing primary keys, composite foreign keys, and multi-level relationship hierarchies across dozens of tables.
2. **Realistic data population:** Generating thousands of realistic records without triggering constraint violations, duplicate key collisions, or missing parent foreign key dependencies.

**Structura Forge** provides a self-contained local workspace to address both. Available as both an interactive terminal console (TUI) and a browser-based visualization studio, it gives developers instantaneous clarity into their database topology alongside a high-throughput mock data pipeline.

Everything runs strictly on `localhost`. No telemetry, no cloud relays, no outbound network requests.

---

## Key Capabilities

- **Interactive Visual Topology:** Hardware-accelerated entity diagram canvas with pan, zoom, auto-fit, and direct SVG export.
- **Topological Dependency Resolution:** Tables are analyzed as a directed acyclic graph (DAG). If a target table references an unpopulated parent, Structura Forge automatically resolves and seeds prerequisite records first.
- **High-Throughput Batch Seeding:** Streams up to 50,000 realistic rows per batch using low-level PostgreSQL batch execution primitives (`execute_batch`).
- **Context-Aware Synthesis:** Powered by `Faker` to produce realistic business entities (names, email addresses, geographical coordinates, temporal ranges, UUIDs, and valid JSON payloads).
- **Collision-Resistant Constraints:** Analyzes `UNIQUE` constraints and dynamically scopes unique sets during generation to eliminate constraint rollback exceptions.
- **Bi-directional Interfaces:** Use the dark-mode terminal UI (`Rich`) for quick local operations, or launch the single-page browser studio for interactive exploration.
- **Mermaid.js Blueprint Generator:** Automatically extracts schema metadata and compiles Markdown-ready Mermaid diagrams (`erd_blueprint.md`).
- **Offline Preview Sandbox:** Includes a 6-table e-commerce test schema with fallback mock fixtures so you can test features instantly without an active database connection.

---

## Architecture & Layout

```text
structura-forge/
├── structura.py                # Unified CLI & Terminal interface
├── requirements.txt            # Core runtime dependencies
├── specs.md                    # System architecture & API specifications
├── erd_blueprint.md            # Generated Mermaid entity relationship diagram
├── .env.example               # Environment configuration template
├── LICENSE                     # MIT License
├── backend/
│   ├── main.py                 # FastAPI application & data generation engine
│   └── test_schema.sql         # Reference 6-table test schema
└── frontend/
    ├── index.html              # Responsive single-page application
    └── assets/
        └── structura-icon.png  # Brand icon asset
```

---

## Quickstart

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14+ (optional: sandbox fallback available if disconnected)

### 1. Installation

Clone the repository and set up a virtual environment:

```bash
# Clone repository
git clone https://github.com/your-username/structura-forge.git
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

Create your local `.env` configuration:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Define your database connection parameters in `.env`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/postgres
PORT=8000
HOST=127.0.0.1
```

> **Note:** If the configured PostgreSQL instance is unreachable, Structura Forge automatically prompts to launch in **Preview Sandbox Mode**, allowing you to explore all features safely.

---

## Usage

### Terminal Interface (TUI)

Launch the interactive console application:

```bash
python structura.py
```

| Option | Function |
| :---: | :--- |
| `1` | Inspect database schema as a color-coded hierarchy tree |
| `2` | Compile and export Mermaid ERD blueprint to `erd_blueprint.md` |
| `3` | Execute relational mock data injection with real-time progress bars |
| `4` | Spin up and open the local Web Studio in your default browser |
| `6` | Reconfigure connection parameters or deploy the reference test schema |
| `5` | Exit |

---

### Web Studio

Launch the browser interface directly:

```bash
python structura.py --web
```

Or run the server via Uvicorn:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Navigate to `http://localhost:8000` to access the visual studio:

- **Entity Graph Canvas:** Pan, zoom, inspect column data types, primary keys, and foreign key relationships. Press <kbd>F</kbd> to fit diagram to screen.
- **Data Generator Panel:** Select any table, choose batch sizes (from 100 to 50,000 rows), preview sample payloads, and inject data with foreign key cascading.
- **Top Bar Actions:** Export diagrams as clean SVG images, copy raw Mermaid markup, or invoke fuzzy search (<kbd>Ctrl</kbd> + <kbd>K</kbd>) to navigate large schemas.

---

## Keyboard Shortcuts (Web Studio)

| Key | Action |
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

## Security Model

- **Zero Telemetry:** Operates exclusively offline on loopback (`127.0.0.1`). No metrics, diagnostics, or payloads are transmitted externally.
- **Sanitized Execution:** Employs parameterized queries and strict SQL identifier escaping (`psycopg2.sql`) to prevent injection vulnerabilities.
- **Credential Protection:** Connection strings and passwords are masked across CLI logs and web responses.

---

## License

Distributed under the [MIT License](LICENSE). Built for local PostgreSQL workflows.
