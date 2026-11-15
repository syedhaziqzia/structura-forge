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

Working with PostgreSQL usually brings two recurring problems:

1. **Understanding the schema:** tracing primary keys, foreign keys, and multi-level relationships across many tables.
2. **Populating test data:** generating thousands of realistic rows without hitting foreign key violations, duplicate keys, or empty parent tables.

**Structura Forge** solves both in one local tool, offered through two interfaces that share the same database connection:

- **Terminal Console (TUI):** a fast, keyboard-driven Rich interface for your shell.
- **Web Studio:** a browser-based interactive ERD canvas and seeding dashboard at `http://localhost:8000`.

Everything runs on your own machine. No telemetry, no cloud services, no outbound requests.

---

## Key Features

- **Live Schema Introspection:** Reads tables, columns, primary keys, foreign keys, unique constraints, and row counts from the `public` schema.
- **Interactive ERD Canvas:** Pan, zoom, fit-to-screen, minimap, and SVG export. Selecting a table highlights it in emerald and its parent FK tables in amber.
- **Constraint-Safe Seeding:** Inserts **1 to 50,000** realistic rows per run using `Faker` and `psycopg2.extras.execute_batch`, sampling valid parent keys for every foreign key.
- **Automatic Parent Seeding:** If a target table depends on empty parent tables, Structura Forge can seed them first in topological order.
- **Unique & Serial Aware:** Skips `SERIAL` / `IDENTITY` / `nextval()` columns and generates collision-free values for `UNIQUE` columns.
- **Transactional Safety:** Every run is wrapped in a transaction and rolled back on failure, so no partial inserts are left behind.
- **Mermaid ERD Export:** Generates Mermaid `erDiagram` code to `erd_blueprint.md`, viewable on GitHub or in VS Code.
- **Preview Sandbox Mode:** A built-in 6-table schema lets you explore every feature without a running database.

---

## Screenshots

### Web Studio
| Interactive ERD & Parent-FK Highlighting | Batch Seeding & Committed Telemetry |
| :---: | :---: |
| <img src="frontend/assets/screenshots/web-studio-erd.png" alt="Web Studio ERD and Parent FK Highlighting" width="100%" /> | <img src="frontend/assets/screenshots/web-studio-seeder.png" alt="Web Studio Batch Seeding Telemetry" width="100%" /> |

### Terminal Console (TUI)
| Control Deck & Live Connection | Schema Tree & High-Velocity Seeder |
| :---: | :---: |
| <img src="frontend/assets/screenshots/tui-control-deck.png" alt="TUI Control Deck" width="100%" /> | <img src="frontend/assets/screenshots/tui-tree-seeder.png" alt="TUI Schema Tree and Seeder" width="100%" /> |

---

## Quickstart

### Prerequisites
- Python 3.11+
- PostgreSQL 14+ running locally (optional: Preview Sandbox works without it)

### 1. Install

```bash
git clone https://github.com/syedhaziqzia/structura-forge.git
cd structura-forge

python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Your Connection

```bash
# Windows (PowerShell)
Copy-Item .env.example .env
# macOS / Linux
cp .env.example .env
```

Open `.env` and replace `CHANGE_ME` with your local PostgreSQL password:

```env
DATABASE_URL=postgresql://postgres:CHANGE_ME@localhost:5432/postgres
PORT=8000
HOST=127.0.0.1
```

> [!TIP]
> You can also set credentials without editing files: use TUI option **`6`**, or click the connection pill in the Web Studio and choose **Configure Connection (.env)**. Both save to your local `.env` only.

### 3. Run

```bash
python structura.py          # Terminal Console (TUI)
python structura.py --web    # Web Studio at http://localhost:8000
```

---

## Database Setup & Test Schema

You can point Structura Forge at any existing local PostgreSQL database, or use the bundled reference schema in [`backend/test_schema.sql`](backend/test_schema.sql):

- **`users`** &rarr; **`orders`** &rarr; **`order_items`** &larr; **`products`** &larr; **`categories`** (self-referencing parent category)
- **`audit_logs`** with `jsonb` payloads referencing `users`

**Load it using any one of these:**

| Method | How |
| :--- | :--- |
| **TUI** | Run `python structura.py` &rarr; option **`6`** &rarr; provision test schema |
| **Web Studio** | **☰ Menu** &rarr; **Provision 6 Lab Tables** |
| **psql** | `psql -U postgres -d postgres -f backend/test_schema.sql` |

All statements use `CREATE TABLE IF NOT EXISTS`, so running them again is safe.

**Live vs. Preview:** If the database is unreachable, both interfaces fall back to **Preview Sandbox Mode** with simulated data. You can always tell which mode you are in:

| | Live PostgreSQL | Preview Sandbox |
| :--- | :--- | :--- |
| **Web Studio** | Green `Live` pill, real tables, Console shows `Committed` | Amber `Preview` pill + banner, Console marked `Simulated` |
| **TUI** | `[ LIVE CONNECTED ]` | `[ DB UNREACHABLE ]` |

---

## Using the Web Studio

Click **`? Help`** in the top-right corner at any time for an in-app quick guide.

**Basic workflow:**
1. **Pick a table:** click a node on the diagram, or use the **Target table** selector.
2. **Inspect (optional):** click **Inspect** to view columns and constraints, a 3-row Faker preview, and the parent dependency order.
3. **Choose a row count:** type any number from **1 to 50,000**, drag the slider, or use the 500 / 1,000 / 10,000 / 50,000 presets.
4. **Inject:** click **Inject N Rows**. Runs over 25,000 rows ask for confirmation first.

**Controls at a glance:**

| Control | What it does |
| :--- | :--- |
| **Connection pill** (top-right) | Switch between Live PostgreSQL and Preview Sandbox, or open **Configure Connection** |
| **↻ Refresh** | Re-read the schema from the database |
| **☰ Menu** | Jump to table, view or copy Mermaid code, export SVG, toggle minimap, provision test tables, quick-start guide |
| **⚙ Engine Settings** | Set the **batch size** (500 – 5,000 rows per `execute_batch` page) and toggle **Auto-seed empty parents** |
| **Console** | Live status, rows inserted, latency, log filters (`All` / `Errors` / `Metrics`), and re-runnable **Run History** |

> [!NOTE]
> **Row count vs. batch size:** the row count is the *total* number of rows to insert. The batch size only controls how many rows are sent to PostgreSQL per round-trip. For example, 55 rows with a batch size of 50 runs as one batch of 50 plus one of 5.

**Keyboard shortcuts:**

| Key | Action |
| :--- | :--- |
| <kbd>?</kbd> | Open the quick guide & shortcuts |
| <kbd>Ctrl</kbd> + <kbd>K</kbd> | Search and jump to a table |
| <kbd>R</kbd> | Refresh schema |
| <kbd>Enter</kbd> | Inject rows into the selected table |
| <kbd>F</kbd> | Fit diagram to screen |
| <kbd>+</kbd> / <kbd>−</kbd> / <kbd>0</kbd> | Zoom in / zoom out / reset to 100% |
| <kbd>G</kbd> | View Mermaid ERD code |
| <kbd>Esc</kbd> | Close any modal |

---

## Using the TUI

```bash
python structura.py
```

| Key | Action |
| :---: | :--- |
| `1` | View the schema as a color-coded tree (PKs in gold, FKs in emerald) |
| `2` | Export a Mermaid ERD to `erd_blueprint.md` |
| `3` | Seed a table: pick a table, enter the row count and batch size, and watch the progress bar |
| `4` | Launch the Web Studio and open it in your browser |
| `5` | Exit (or type `q`) |
| `6` | Configure connection credentials or provision the test schema |

At any prompt, type `b` to cancel and return to the Control Deck.

---

## Running the TUI and Web Studio Together

Both can run at the same time against the same database:

1. **Terminal 1:** `python structura.py --web`
2. **Terminal 2:** `python structura.py`

Rows seeded from one interface show up in the other after a refresh (<kbd>R</kbd> in the Web Studio, or option `1` in the TUI). If the Web Studio is already running, TUI option `4` detects it on port 8000 and simply opens your browser instead of starting a second server.

---

## Troubleshooting

| Problem | Fix |
| :--- | :--- |
| Stuck in **Preview** / `DB UNREACHABLE` | Check PostgreSQL is running and the password in `.env` is correct, then click **Retry Live** or press <kbd>R</kbd> |
| `password authentication failed` | Update credentials via TUI option `6` or **Configure Connection** in the Web Studio |
| Port 8000 already in use | Another instance is running. Open `http://localhost:8000`, or stop the other process |
| "Blocked: Parent table is empty" | Enable **Auto-seed empty parents** in ⚙ Engine Settings, or seed the parent table first |
| No tables shown | Your `public` schema is empty. Provision the 6 test tables (see [Database Setup](#database-setup--test-schema)) |

---

## Project Structure

```text
structura-forge/
├── structura.py                # Terminal interface (TUI) & CLI entrypoint
├── requirements.txt            # Python dependencies
├── erd_blueprint.md            # Exported Mermaid entity diagram
├── .env.example                # Connection template (copy to .env)
├── LICENSE                     # MIT License
├── backend/
│   ├── main.py                 # FastAPI API & data generation engine
│   └── test_schema.sql         # 6-table reference schema
└── frontend/
    ├── index.html              # Web Studio (single-page app)
    └── assets/
        ├── structura-icon.png  # Application icon
        ├── tui-banner.svg      # Terminal banner
        └── screenshots/        # README screenshots
```

---

## Security

- **Local only:** The server binds to `127.0.0.1`, so it is reachable only from your own computer. CORS is restricted to `localhost:8000` / `127.0.0.1:8000`.
- **Credentials stay on your machine:** Passwords are stored only in your local `.env`, which is excluded from version control. They are never returned by the API or shown in the TUI or Web Studio.
- **SQL injection protection:** Table and column names are validated and quoted with `psycopg2.sql.Identifier`; values are passed as parameters.
- **Zero telemetry:** No analytics, tracking, or external network calls.

> [!WARNING]
> The Web Studio has no login screen by design. Run it on `127.0.0.1` for local development only, and do not expose port 8000 to a network or the internet.

---

## License

Distributed under the [MIT License](LICENSE).
