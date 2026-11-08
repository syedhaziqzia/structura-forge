<div align="center">

  <img src="frontend/assets/structura-icon.png" alt="Structura Forge Logo" width="130" height="130" style="border-radius: 26px; border: 2px solid rgba(16, 185, 129, 0.4); box-shadow: 0 8px 32px rgba(16, 185, 129, 0.25);" />

  # Structura Forge

  **PostgreSQL Schema Visualizer & Fast Mock Data Seeder**

  *A clean, local developer tool that maps out your PostgreSQL database, draws live entity diagrams, and seeds thousands of realistic rows without breaking foreign keys.*

  <p align="center">
    <img src="https://badgen.net/badge/Python/3.11+/10B981?icon=python" alt="Python 3.11+" />
    <img src="https://badgen.net/badge/FastAPI/0.110+/059669?icon=fastapi" alt="FastAPI 0.110+" />
    <img src="https://badgen.net/badge/PostgreSQL/14+/047857?icon=postgresql" alt="PostgreSQL 14+" />
    <img src="https://badgen.net/badge/Privacy/Zero%20Telemetry/10B981" alt="Zero Telemetry" />
    <img src="https://badgen.net/badge/License/MIT/065F46" alt="MIT License" />
  </p>

</div>

---

## What is Structura Forge?

When building apps with PostgreSQL, two things take too much time:
1. **Understanding the database:** Figuring out how tables, primary keys, and foreign keys connect to each other.
2. **Getting good test data:** Filling tables with realistic data without getting blocked by foreign key or unique constraint errors.

**Structura Forge** solves both problems in one local tool. It gives you:
- A **Terminal Interface (CLI)** you can run right from your command line.
- A **Web Studio** you can open in your browser with an interactive visual graph.
- A **Fast Mock Data Engine** that generates and inserts 1,000 to 50,000 rows in seconds.

Everything runs on your computer (`localhost`). No internet connection is needed, and no data is ever sent anywhere.

---

## Features

- **Terminal Interface (TUI):** Clean, pitch-black and emerald green terminal menu with full schema trees, live progress bars, and ASCII blueprints.
- **Web Dashboard:** Clean browser studio with an interactive diagram (zoom, pan, fit, and export as SVG).
- **Smart Dependency Seeding:** If a table depends on a parent table that is empty, Structura Forge can automatically seed the parent first so inserts never fail.
- **Fast Batch Streaming:** Uses PostgreSQL batch streaming (`execute_batch`) to insert thousands of rows in milliseconds.
- **Realistic Data:** Uses `Faker` to create realistic names, emails, addresses, numbers, dates, timestamps, UUIDs, and JSON payloads.
- **Unique-Safe:** Automatically tracks unique columns and adds unique tags so you never hit duplicate key errors.
- **Instant Mermaid Diagrams:** Exports clean Mermaid.js diagram code right into `erd_blueprint.md` so you can view it in VS Code or GitHub.
- **Built-in Test Database:** Includes a ready-to-use 6-table test schema (`backend/test_schema.sql`) so you can try all features even if you don't have your own database yet.

---

## Project Structure

```text
structura-forge/
├── .env.example               # Template for your local PostgreSQL credentials
├── .gitignore                  # Keeps passwords, logs, and temp files safe
├── LICENSE                     # MIT License
├── README.md                   # You are here
├── specs.md                    # Consolidated technical specifications
├── requirements.txt            # Python packages needed
├── structura.py                # Terminal tool & CLI entrypoint
├── erd_blueprint.md            # Exported visual diagram
├── backend/
│   ├── main.py                 # FastAPI backend & data generator
│   └── test_schema.sql         # Sample 6-table store database
└── frontend/
    ├── assets/
    │   └── structura-icon.png  # Logo icon
    └── index.html              # Single-page web dashboard
```

---

## Quick Setup (3 Steps)

### 1. Install dependencies

```bash
# Optional: create and activate a virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate # On macOS/Linux

# Install required packages
pip install -r requirements.txt
```

### 2. Set your database connection

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Open `.env` and put in your PostgreSQL password:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/postgres
PORT=8000
HOST=127.0.0.1
```

> **Tip:** If your PostgreSQL is not running or your password is wrong, Structura Forge won't crash — it will ask if you want to use the built-in **Preview Sandbox** so you can test everything right away!

---

## How to Run

### Method A: Run in the Terminal (TUI)

```bash
python structura.py
```

This opens the interactive menu:
- Press **`1`** to view your database schema as a color-coded tree.
- Press **`2`** to export a visual Mermaid ERD blueprint to `erd_blueprint.md`.
- Press **`3`** to seed any table with mock rows and watch the animated progress bar.
- Press **`4`** to launch the Web Dashboard in your browser.
- Press **`6`** to update connection credentials or create the test database tables.
- Press **`5`** to exit.

---

### Method B: Run the Web Dashboard

```bash
python structura.py --web
```
Or:
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
Then open `http://localhost:8000` in your browser.

- **On the left:** Click and drag to pan the database diagram, use the zoom buttons or press `F` to fit to screen. Click any table box to select it.
- **On the right:** Choose a table, pick how many rows you want (from 100 up to 50,000), and click **Inject Rows**.
- **Inspect button:** Click **Inspect Schema & Sample** to see sample data and dependency order before inserting.
- **Top Right Menu (☰):** Download the diagram as SVG, copy Mermaid code, or jump to any table (`Ctrl+K`).

---

## Keyboard Shortcuts (Web Studio)

| Shortcut | What it does |
| :--- | :--- |
| <kbd>Ctrl</kbd> + <kbd>K</kbd> | Search and jump to any table |
| <kbd>R</kbd> | Refresh database schema |
| <kbd>Enter</kbd> | Start seeding rows |
| <kbd>F</kbd> | Fit diagram to screen |
| <kbd>+</kbd> / <kbd>−</kbd> | Zoom in / Zoom out |
| <kbd>0</kbd> | Reset zoom to 100% |
| <kbd>G</kbd> | View Mermaid diagram code |
| <kbd>Esc</kbd> | Close any popup window |

---

## Security & Safety

- **No Passwords on Screen:** Connection passwords are never displayed in the terminal or web dashboard.
- **Safe Queries:** Uses strict SQL identifier quoting (`psycopg2.sql`) and name validation to prevent any SQL injection.
- **Local Only:** Network access is restricted to `localhost` (`127.0.0.1`).
- **Safe `.gitignore`:** Keeps your `.env` file, logs, backups, and credentials out of Git so they are never accidentally pushed to GitHub.

---

## License

MIT License — Syed Haziq Zia Naqvi

This project is licensed under the [MIT License](LICENSE) — see the [LICENSE](LICENSE) file for details. Free for personal, academic, and commercial use.
