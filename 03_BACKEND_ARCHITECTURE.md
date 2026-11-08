# MODULE 03: BACKEND ARCHITECTURE (`03_BACKEND_ARCHITECTURE.md`)

## 1. Technical Stack

* Python 3.11+ / FastAPI / Uvicorn
* Database Driver: `psycopg2-binary` (Context manager connection pools)
* Data Validation: `pydantic` (v2.x)
* Environment Handling: `python-dotenv`

## 2. Pydantic Models & Schemas

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class ColumnMeta(BaseModel):
    name: str
    data_type: str
    is_nullable: bool
    is_pk: bool = False
    is_fk: bool = False
    foreign_table: Optional[str] = None
    foreign_column: Optional[str] = None

class TableMeta(BaseModel):
    table_name: str
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

## 3. API Endpoints

* `GET /api/health`: Executes `SELECT 1;`. Returns HTTP 200 on success, HTTP 503 if credentials in `.env` are invalid.
* `GET /api/schema`: Returns `SchemaResponse` with raw entity data and compiled Mermaid ERD string.
* `POST /api/seed`: Ingests `SeedRequest`, executes bulk generation via `psycopg2.extras.execute_batch`, and returns `SeedResponse`.

