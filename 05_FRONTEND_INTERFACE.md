# MODULE 05: FRONTEND INTERFACE SPECIFICATION (`05_FRONTEND_INTERFACE.md`)

## 1. Visual Language & Token System

* **Theme:** Obsidian Dark Mode.
* **Background:** `#030303` with a micro-dot grid pattern (`rgba(255, 255, 255, 0.04)`).
* **Surfaces/Cards:** Pitch-black frosted glass (`rgba(12, 12, 14, 0.8)`) with `backdrop-filter: blur(16px)` and `1px` border (`rgba(255, 255, 255, 0.08)`).
* **Accents:** Emerald Green (`#10B981` to `#34D399`).
* **Typography:** Inter or system sans-serif for UI labels; JetBrains Mono for table names, SQL types, and log telemetry.

## 2. Layout & Interactions

* **Header:**
  * Brand mark: `STRUCTURA` with emerald-green accent.
  * Live Connection Status Pill (Green dot: `Connected to localhost:5432/postgres`).
  * Action: "Refresh Schema" button.

* **Left Column (60%): Live ERD Canvas:**
  * Renders Mermaid.js via CDN (`https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js`).
  * Dark-mode Mermaid configuration: `theme: 'dark'`, dark node fills, emerald-green connector lines.
  * "Copy Mermaid Markdown" and "Download SVG" utility buttons.

* **Right Column (40%): Data Injection Studio:**
  * Table selection dropdown (populated dynamically via `/api/schema`).
  * Row Count range slider + sync number input (100 to 50,000 rows).
  * Primary Button: "Inject Mock Rows" with active loading spinner and disabled state during execution.
  * Telemetry console showing status, rows inserted, and execution latency in milliseconds.

