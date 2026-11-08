# MODULE 01: PROJECT BRIEF (`01_PROJECT_BRIEF.md`)

## 1. Executive Summary

Structura is an offline, zero-telemetry local developer utility designed for PostgreSQL environments. It solves two critical bottlenecks in database development and academic lab workflows:

1. Automatically extracting and rendering clean Entity-Relationship Diagrams (ERDs) in Mermaid.js syntax directly from live PostgreSQL catalogs.
2. Intelligently generating thousands of constraint-compliant mock data rows using `Faker` and high-speed `psycopg2.extras.execute_batch` streaming without violating foreign key relationships.

## 2. Core Philosophy

* **Ephemeral & Local:** Operates entirely against `localhost:5432`. No external SaaS, telemetry, or third-party cloud data persistence.
* **Architectural Minimalism:** 2-core-file codebase (`backend/main.py` and `frontend/index.html`) driven by environment variables (`.env`).
* **Safety First:** Non-destructive catalog inspection; transactional rollback safeguards (`try/except/rollback`) on all batch insertions.

## 3. Core Deliverables

* `GET /api/schema`: Introspects tables, columns, PKs, and FKs; returns structured JSON and ready-to-render Mermaid.js ERD syntax.
* `POST /api/seed`: Ingests a validated seeding payload, resolves foreign key lookups dynamically, and batch-inserts mock rows.
* Obsidian / Emerald-Green interface featuring a split-pane ERD canvas, real-time execution metrics, and a Rich Terminal User Interface (`structura.py`).

