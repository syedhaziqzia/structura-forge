# MODULE 06: MASTER IMPLEMENTATION PROMPT (`06_IMPLEMENTATION_PROMPT.md`)

```markdown
Build Structura, an offline developer tool for PostgreSQL schema visualization and mock data seeding.

Follow the exact technical and architectural specifications outlined across MODULE 01 through MODULE 05.

### Execution Constraints:
1. File Structure:
   - Put all backend code in `backend/main.py`.
   - Put the entire single-page UI in `frontend/index.html`.
   - Read PostgreSQL connection string from root `.env` (`DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres`).

2. Backend Requirements:
   - Use FastAPI, psycopg2-binary, and Faker.
   - Use Pydantic v2 models for schema validation and request payloads.
   - Query information_schema to extract tables, columns, primary keys, and foreign keys.
   - Convert extracted schema into valid Mermaid.js erDiagram syntax.
   - Bulk insert data using psycopg2.extras.execute_batch inside a single transaction block.
   - Auto-exclude SERIAL/auto-increment columns from insert queries.
   - Implement Foreign Key pre-flight checking: query parent tables for valid foreign keys before seeding child tables.

3. Frontend Requirements:
   - Single HTML file using Tailwind CSS CDN and Mermaid.js CDN.
   - Obsidian dark theme with emerald-green (`#10B981` / `#34D399`) accents.
   - Split-pane layout: Left pane renders the Mermaid ERD; Right pane contains table selector, row count slider, and Inject button.
   - Make asynchronous fetch requests to /api/schema and /api/seed without reloading the page.
```

