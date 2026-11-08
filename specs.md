# Structura Forge — Technical Specifications (`specs.md`)

This document consolidates the complete architectural, database, backend, seeder engine, and frontend specifications for **Structura Forge**.

---

## 1. Project Brief & Core Philosophy

Structura Forge is an offline, zero-telemetry local developer utility designed for PostgreSQL environments. It solves two critical bottlenecks in database development and academic lab workflows:

1. Automatically extracting and rendering clean Entity-Relationship Diagrams (ERDs) in Mermaid.js syntax directly from live PostgreSQL catalogs.
2. Intelligently generating thousands of constraint-compliant mock data rows using `Faker` and high-speed `psycopg2.extras.execute_batch` streaming without violating foreign key relationships.

### Core Philosophy
* **Ephemeral & Local:** Operates entirely against `localhost:5432`. No external SaaS, telemetry, or third-party cloud data persistence.
* **Architectural Minimalism:** Core files driven by environment variables (`.env`).
* **Safety First:** Non-destructive catalog inspection; transactional rollback safeguards (`try/except/rollback`) on all batch insertions.

### Core Deliverables
* `GET /api/schema`: Introspects tables, columns, PKs, and FKs; returns structured JSON and ready-to-render Mermaid.js ERD syntax.
* `POST /api/seed`: Ingests a validated seeding payload, resolves foreign key lookups dynamically, and batch-inserts mock rows.
* Obsidian / Emerald-Green interface featuring a split-pane ERD canvas, real-time execution metrics, and an interactive Rich Terminal User Interface (`structura.py`).

---

## 2. Database Specification & Catalog Queries

Structura Forge inspects PostgreSQL metadata using ANSI-compliant `information_schema` and `pg_catalog` queries.

```sql
SELECT 
    c.table_name,
    c.column_name,
    c.data_type,
    c.is_nullable,
    c.character_maximum_length,
    c.numeric_precision,
    c.numeric_scale,
    CASE WHEN tc.constraint_type = 'PRIMARY KEY' THEN TRUE ELSE FALSE END AS is_primary_key,
    CASE WHEN tc.constraint_type = 'UNIQUE' THEN TRUE ELSE FALSE END AS is_unique_constraint,
    kcu2.table_name AS foreign_table,
    kcu2.column_name AS foreign_column,
    c.column_default,
    c.is_identity
FROM information_schema.columns c
INNER JOIN information_schema.tables t
    ON c.table_name = t.table_name 
    AND c.table_schema = t.table_schema
    AND t.table_type = 'BASE TABLE'
LEFT JOIN information_schema.key_column_usage kcu
    ON c.table_name = kcu.table_name 
    AND c.column_name = kcu.column_name
    AND c.table_schema = kcu.table_schema
LEFT JOIN information_schema.table_constraints tc
    ON kcu.constraint_name = tc.constraint_name
    AND kcu.table_schema = tc.table_schema
LEFT JOIN information_schema.referential_constraints rc
    ON tc.constraint_name = rc.constraint_name
    AND tc.table_schema = rc.constraint_schema
LEFT JOIN information_schema.key_column_usage kcu2
    ON rc.unique_constraint_name = kcu2.constraint_name
    AND rc.unique_constraint_schema = kcu2.constraint_schema
    AND COALESCE(kcu.position_in_unique_constraint, 1) = kcu2.ordinal_position
WHERE c.table_schema = 'public'
ORDER BY c.table_name, c.ordinal_position;
```

### Mermaid.js ERD Grammar Mapping
The backend iteratively converts the introspected schema dictionary into Mermaid `erDiagram` syntax:

```text
erDiagram
    users {
        uuid id PK
        varchar email
        timestamptz created_at
    }
    orders {
        bigserial order_id PK
        uuid user_id FK
        numeric total_amount
    }
    users ||--o{ orders : "user_id"
```

* **One-to-Many rule:** `PARENT ||--o{ CHILD : "foreign_key"`
* **Self-referencing tables:** Handled safely without recursive loops.

---

## 3. Backend Architecture & API Specification

### Technical Stack
* **Runtime:** Python 3.11+ / FastAPI / Uvicorn
* **Database Driver:** `psycopg2-binary` (Context manager connection pools + `psycopg2.sql` safe quoting)
* **Data Validation:** `pydantic` (v2.x) with strict SQL identifier validation
* **Environment Handling:** `python-dotenv`

### Pydantic Models & Schemas
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class ColumnMeta(BaseModel):
    name: str
    data_type: str
    is_nullable: bool
    is_pk: bool = False
    is_fk: bool = False
    is_unique: bool = False
    foreign_table: Optional[str] = None
    foreign_column: Optional[str] = None
    char_max_len: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None
    is_identity: bool = False
    column_default: Optional[str] = None

class TableMeta(BaseModel):
    table_name: str
    row_count: int = 0
    columns: List[ColumnMeta]

class SchemaResponse(BaseModel):
    tables: List[TableMeta]
    mermaid_syntax: str

class SeedRequest(BaseModel):
    table_name: str
    row_count: int = Field(default=1000, ge=1, le=50000)
    batch_size: int = Field(default=1000, ge=100, le=5000)

class SeedResponse(BaseModel):
    status: str
    table: str
    rows_inserted: int
    execution_time_ms: float
```

### API Endpoints
* `GET /api/health`: Executes `SELECT 1;`. Returns HTTP 200 on success, HTTP 503 if credentials in `.env` are invalid.
* `GET /api/config`: Returns active connection parameters (`host`, `port`, `database`, `user`).
* `POST /api/config`: Verifies new connection credentials and optionally writes them to `.env`.
* `POST /api/init-lab`: Provisions the 6-table test schema from `backend/test_schema.sql`.
* `GET /api/schema`: Returns `SchemaResponse` with raw entity data and compiled Mermaid ERD string.
* `POST /api/seed`: Ingests `SeedRequest`, executes bulk generation via `psycopg2.extras.execute_batch`, and returns `SeedResponse`.

---

## 4. Seeder Engine & Data Generation Heuristics

### Postgres-to-Faker Type Mapping

| PostgreSQL Data Type | Generator Strategy | Logic & Sanitization |
| --- | --- | --- |
| `uuid` | `uuid.uuid4()` | Standard UUIDv4 string |
| `varchar`, `text` (email in name) | `f"user{seq}_{salt}@{fake.free_email_domain()}"` | Monotonic row counter + salt to guarantee uniqueness |
| `varchar`, `text` (name in name) | `faker.name()` | Sliced to `character_maximum_length` if set |
| `varchar`, `text` (generic) | `faker.sentence(nb_words=4)` | Sliced to column max length |
| `integer`, `int4`, `smallint` | `faker.random_int(1, 10000)` | Numerical integer range |
| `bigint`, `int8` | `faker.random_int(10000, 9999999)` | 64-bit safe bounds |
| `boolean` | `faker.boolean(chance_of_getting_true=50)` | Native boolean |
| `date` | `faker.date_between('-2y', 'today')` | Standard ISO date string |
| `timestamp`, `timestamptz` | `faker.date_time_between('-1y')` | Native datetime object |
| `numeric`, `decimal` | `round(faker.pyfloat(10, 5000), scale)` | Precision and scale matched to column definition |
| `json`, `jsonb` | `json.dumps({"event": faker.word(), "ok": True})` | Valid JSON payload |

### Foreign Key Integrity Protocol
1. **Pre-Flight Lookup:** When seeding a table with foreign keys, query the parent table:
   ```sql
   SELECT foreign_column FROM parent_table WHERE foreign_column IS NOT NULL ORDER BY RANDOM() LIMIT 500;
   ```
2. **Multi-Hop Dependency Resolution:** Walks all transitive ancestors in topological order (`users`, `categories` &rarr; `orders`, `products` &rarr; `order_items`) and auto-seeds missing parents before child insertion.
3. **In-Memory Sampling:** Parent keys are cached per `parent_table.parent_column`. Child rows sample from this list randomly to maintain 100% referential integrity.
4. **Serial PK Handling:** Columns marked as `SERIAL`, `BIGSERIAL`, `IDENTITY`, or containing `nextval(...)` are omitted from the insert payload so Postgres manages sequences natively.

---

## 5. Frontend & UI/UX Specification

### Visual Language & Design Tokens
* **Theme:** Obsidian Dark Mode (`#030303`).
* **Surfaces:** Frosted card panels (`#090c0a`) with subtle 1px border (`rgba(255, 255, 255, 0.08)`).
* **Accent Colors:** Emerald Green (`#10B981` / `#34D399`) with Amber warnings (`#FBBF24`).
* **Typography:** Inter for UI controls; JetBrains Mono for table names, SQL types, and log telemetry.

### Split-Pane Layout
* **Left Column (60%): Live ERD Canvas:**
  * Renders Mermaid.js in dark mode with emerald connector lines.
  * Interactive zoom (`+` / `-`), pan (click & drag), fit-to-screen (`F`), and SVG export.
  * Direct table node clicking automatically selects that table in the right pane.
* **Right Column (40%): Data Injection Studio:**
  * Custom app-themed table selector ordered by dependency sequence.
  * Number stepper and range slider (100 to 50,000 rows).
  * Table Inspector Modal with column badges, 3-row Faker sample previews, and dependency trees.
  * Live Telemetry Console with KPI strips, filter chips (`All`, `Errors`, `Metrics`), and re-runnable run history.

---

## 6. Security & Safety Principles

1. **SQL Identifier Protection:** Table and column names are checked against strict identifier patterns and quoted using `psycopg2.sql.Identifier`.
2. **Credential Sanitization:** Passwords are never displayed in the terminal UI or web dashboard.
3. **CORS Localhost Restriction:** Cross-Origin Resource Sharing is locked to local addresses (`localhost:8000`, `127.0.0.1:8000`).
4. **Offline Isolation:** Runs 100% locally with zero analytics, external telemetry, or network persistence.
