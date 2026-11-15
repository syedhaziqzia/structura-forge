<div align="center">

  <img src="frontend/assets/structura-icon.png" alt="Structura Forge" width="112" height="112" style="border-radius: 22px; border: 1px solid rgba(16, 185, 129, 0.35); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);" />

  # Structura Forge

  **See your PostgreSQL database as a diagram, and fill it with realistic test data in seconds.**

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

## What Is It?

Structura Forge is a free tool that runs on your own computer and helps with two common database chores:

1. **Understanding your tables.** It draws a diagram of your PostgreSQL tables and shows how they connect to each other.
2. **Creating test data.** It fills your tables with realistic fake rows (names, emails, prices, dates, and more) without breaking any links between tables.

You can use it in two ways:

- **Terminal app (TUI):** a menu that runs in your command line.
- **Web Studio:** a visual dashboard you open in your browser at `http://localhost:8000`.

Everything stays on your computer. Nothing is sent to the internet.

### Why I Built This

When I first started using PostgreSQL for my university **Advanced Database Management Systems** course labs, I kept running into the same two slowdowns: tracing how tables and foreign keys connected across growing schemas, and filling tables with realistic test rows without hitting foreign-key or unique-constraint errors. I built **Structura Forge** to turn that manual guesswork into a fast, visual local workflow.

---

## Features

- **Table diagram:** See all your tables and the links between them. Zoom, drag around, fit to screen, and save the diagram as an image (SVG).
- **Realistic test data:** Add anywhere from **1 to 50,000** rows to a table in one go.
- **No broken links:** When a table points to another table (a foreign key), Structura Forge only uses values that really exist in that other table.
- **Fills empty parent tables for you:** If a table depends on another table that is still empty, it can fill that one first.
- **Avoids duplicates:** Columns that must be unique always get unique values. Auto-numbered ID columns are left for PostgreSQL to fill in.
- **All-or-nothing saves:** If anything goes wrong while adding rows, nothing is saved, so your data is never left half-done.
- **Diagram export:** Saves your diagram as Mermaid code in `erd_blueprint.md`, which GitHub and VS Code can display.
- **Try it without a database:** Preview Sandbox mode comes with 6 sample tables so you can explore every feature right away.

---

## Interface Preview

### Web Studio (`http://localhost:8000`)

**Interactive Table Diagram & Parent-FK Highlighting**
<p align="center">
  <img src="frontend/assets/screenshots/web-studio-erd.png" alt="Web Studio table diagram with parent foreign key highlighting" width="100%" />
</p>

**Batch Data Injection & Committed Telemetry**
<p align="center">
  <img src="frontend/assets/screenshots/web-studio-seeder.png" alt="Web Studio batch data injection and telemetry" width="100%" />
</p>

### Terminal App (TUI)

**Control Deck & Live Connection Status**
<p align="center">
  <img src="frontend/assets/screenshots/tui-control-deck.png" alt="TUI main control deck" width="100%" />
</p>

**Schema Architecture Tree & High-Velocity Seeder**
<p align="center">
  <img src="frontend/assets/screenshots/tui-tree-seeder.png" alt="TUI schema tree and batch seeder" width="100%" />
</p>

---

## Getting Started

### What You Need
- **Python 3.11** or newer
- **PostgreSQL 14** or newer, running on your computer (optional: you can try everything in Preview Sandbox mode without it)

### Step 1: Download and Install

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

### Step 2: Add Your Database Password

Make your own settings file by copying the example:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env
# macOS / Linux
cp .env.example .env
```

Open the new `.env` file and replace `CHANGE_ME` with your PostgreSQL password:

```env
DATABASE_URL=postgresql://postgres:CHANGE_ME@localhost:5432/postgres
PORT=8000
HOST=127.0.0.1
```

> [!TIP]
> Don't want to edit files? Choose option **`6`** in the terminal app, or click the connection button (top-right) in the Web Studio and choose **Configure Connection**. Either way, your password is saved only in your own `.env` file.

### Step 3: Start It

```bash
python structura.py          # Open the terminal app
python structura.py --web    # Open the Web Studio at http://localhost:8000
```

---

## Sample Tables for Testing

Don't have a database ready? This project includes 6 sample shop tables in [`backend/test_schema.sql`](backend/test_schema.sql):

- **`users`**, **`orders`**, **`order_items`**, **`products`**, **`categories`** (categories can have sub-categories)
- **`audit_logs`**, which stores JSON data linked to users

**Add them to your database in one of these ways:**

| Where | How |
| :--- | :--- |
| **Terminal app** | Run `python structura.py`, then choose option **`6`** |
| **Web Studio** | Open the **☰ menu** and click **Provision 6 Lab Tables** |
| **Command line** | `psql -U postgres -d postgres -f backend/test_schema.sql` |

Running this again is safe. Tables that already exist are skipped.

### Am I Connected to My Real Database?

If Structura Forge can't reach your database, it switches to **Preview Sandbox** mode, where the data is pretend and nothing is saved. Here's how to tell which mode you're in:

| | Real database (Live) | Pretend data (Preview) |
| :--- | :--- | :--- |
| **Web Studio** | Green **`Live`** label, your real tables are shown | Amber **`Preview`** label and banner, Console marked **`Simulated`** |
| **Terminal app** | **`[ LIVE CONNECTED ]`** | **`[ DB UNREACHABLE ]`** |

---

## Using Multiple Databases

| Question | Answer |
| :--- | :--- |
| **Which database types work?** | **PostgreSQL only.** MySQL, SQLite, SQL Server, and others are not supported. |
| **Can I use different PostgreSQL databases?** | **Yes, one at a time.** Change the **Database Name** in the Web Studio's connection form (or use option **`6`** in the terminal app) to switch, for example from `postgres` to `school_db`. |
| **Can I connect to several at once?** | **No.** Only one database is connected at a time. Saving a new connection replaces the old one in `.env`. |
| **Which tables are shown?** | Only tables in the **`public`** schema (the default place PostgreSQL puts tables). |

> [!NOTE]
> The terminal app reads `.env` fresh every time you pick an option. The Web Studio keeps the connection it started with. So if you switch databases in the terminal app, restart the Web Studio (or switch it using its own connection form).

---

## How to Use the Web Studio

Click the **`? Help`** button in the top-right corner any time to see a quick guide inside the app.

**Adding test rows in 4 steps:**
1. **Pick a table:** click it in the diagram, or choose it from the **Target table** list.
2. **Take a look (optional):** click **Inspect** to see the table's columns, 3 example rows, and which tables it depends on.
3. **Choose how many rows:** type any number from **1 to 50,000**, drag the slider, or click a preset (500, 1,000, 10,000, 50,000).
4. **Add them:** click **Inject N Rows**. For more than 25,000 rows, you'll be asked to confirm first.

**What the buttons do:**

| Button | What it does |
| :--- | :--- |
| **Connection button** (top-right) | Switch between your real database and Preview Sandbox, or change your connection details |
| **↻** | Reload your tables from the database |
| **☰ Menu** | Jump to a table, view or copy the diagram code, save the diagram as an image, show a mini-map, add the 6 sample tables |
| **⚙ Settings** | Choose the **batch size** and turn **auto-fill empty parent tables** on or off |
| **Console** | Shows whether the last run worked, how many rows were added, and how long it took. Also keeps a history you can re-run |

> [!NOTE]
> **Rows vs. batch size:** "Rows" is the total number of rows you want to add. "Batch size" is just how many rows are sent to the database at a time. For example, 55 rows with a batch size of 50 is sent as 50 rows, then 5 rows. You still get 55 rows.

**Keyboard shortcuts:**

| Key | What it does |
| :--- | :--- |
| <kbd>?</kbd> | Open the help guide |
| <kbd>Ctrl</kbd> + <kbd>K</kbd> | Search for a table |
| <kbd>R</kbd> | Reload tables |
| <kbd>Enter</kbd> | Add rows to the selected table |
| <kbd>F</kbd> | Fit the diagram to the screen |
| <kbd>+</kbd> / <kbd>−</kbd> / <kbd>0</kbd> | Zoom in / zoom out / reset zoom |
| <kbd>G</kbd> | Show the diagram code |
| <kbd>Esc</kbd> | Close a popup |

---

## How to Use the Terminal App

```bash
python structura.py
```

| Key | What it does |
| :---: | :--- |
| `1` | Show your tables as a tree (primary keys in gold, links in green) |
| `2` | Save the table diagram to `erd_blueprint.md` |
| `3` | Add test rows: pick a table, type how many rows and the batch size, then watch the progress bar |
| `4` | Open the Web Studio in your browser |
| `5` | Quit (or type `q`) |
| `6` | Change your connection details or add the 6 sample tables |

Type `b` at any question to go back to the main menu.

---

## Running Both at the Same Time

You can use the terminal app and the Web Studio together:

1. In **one** terminal window, run: `python structura.py --web`
2. In **another** terminal window, run: `python structura.py`

Rows added in one show up in the other after you reload (press <kbd>R</kbd> in the Web Studio, or option `1` in the terminal app). If the Web Studio is already running, option `4` in the terminal app just opens your browser instead of starting it again.

---

## Common Problems

| Problem | What to do |
| :--- | :--- |
| Stuck in **Preview** or **`DB UNREACHABLE`** | Make sure PostgreSQL is running and the password in `.env` is right. Then click **Retry Live** or press <kbd>R</kbd> |
| **"password authentication failed"** | Your password is wrong. Fix it with option `6` in the terminal app or **Configure Connection** in the Web Studio |
| **Port 8000 is already in use** | The Web Studio is probably already running. Just open `http://localhost:8000` |
| **"Blocked: Parent table is empty"** | Turn on **auto-fill empty parent tables** in ⚙ Settings, or add rows to the parent table first |
| **No tables are showing** | Your database has no tables yet. Add the [6 sample tables](#sample-tables-for-testing) |

---

## Project Files

```text
structura-forge/
├── structura.py                # Terminal app (start here)
├── requirements.txt            # Python packages to install
├── erd_blueprint.md            # Saved table diagram
├── .env.example                # Example settings (copy to .env)
├── LICENSE                     # MIT License
├── backend/
│   ├── main.py                 # Web server and test-data engine
│   └── test_schema.sql         # 6 sample tables
└── frontend/
    ├── index.html              # Web Studio page
    └── assets/
        ├── structura-icon.png  # App icon
        ├── tui-banner.svg      # Terminal banner image
        └── screenshots/        # Screenshots used in this README
```

---

## Privacy & Security

- **Only on your computer:** The Web Studio runs at `127.0.0.1`, which only your own computer can open. Other people can't reach it.
- **Your password stays private:** It's saved only in your local `.env` file, which is never uploaded to GitHub. The app never shows it on screen.
- **Safe database queries:** Table and column names are checked before use, which protects against SQL injection.
- **No tracking:** No analytics, no data collection, no internet connection needed.

> [!WARNING]
> The Web Studio has no login screen. Keep it on your own computer (`127.0.0.1`). Don't put it on a public server or open port 8000 to the internet.

---

## License

Free to use under the [MIT License](LICENSE).
