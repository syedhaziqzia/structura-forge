"""
Structura Forge - Master Backend Service
Offline, zero-telemetry local developer utility for PostgreSQL schema introspection
and high-speed foreign-key aware mock data generation.
"""

import os
import re
import time
import uuid
import json
import logging
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse, quote_plus
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator
import psycopg2
from psycopg2 import pool, extras, sql
from faker import Faker

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("structura-forge")

# Safe SQL identifier validator
IDENTIFIER_REGEX = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]{0,62}$")

def validate_identifier(name: str) -> str:
    cleaned = name.strip()
    if not IDENTIFIER_REGEX.match(cleaned):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid SQL identifier format: '{name}'. Must contain only alphanumeric characters and underscores."
        )
    return cleaned

# Load Environment Variables from root .env
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postgres"
)
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

fake = Faker()

# Connection Pool Management
db_pool: Optional[pool.SimpleConnectionPool] = None


def init_db_pool():
    global db_pool
    if db_pool is not None:
        try:
            db_pool.closeall()
        except Exception:
            pass
        db_pool = None

    try:
        db_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=DATABASE_URL,
            connect_timeout=3
        )
        logger.info("PostgreSQL connection pool initialized successfully.")
    except Exception as exc:
        logger.warning("Could not establish immediate pool connection: %s", exc)
        db_pool = None


def get_db_connection():
    global db_pool
    if db_pool is None:
        try:
            init_db_pool()
        except Exception:
            pass

    if db_pool:
        try:
            return db_pool.getconn()
        except Exception:
            return psycopg2.connect(DATABASE_URL, connect_timeout=3)
    return psycopg2.connect(DATABASE_URL, connect_timeout=3)


def release_db_connection(conn):
    global db_pool
    if conn is None:
        return
    if db_pool:
        try:
            db_pool.putconn(conn)
            return
        except Exception:
            pass
    try:
        conn.close()
    except Exception:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_pool()
    yield
    global db_pool
    if db_pool:
        try:
            db_pool.closeall()
            logger.info("PostgreSQL connection pool closed.")
        except Exception:
            pass


# FastAPI Application
app = FastAPI(
    title="Structura Forge",
    description="PostgreSQL Architecture Mapping & High-Velocity Seeder",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local cross-origin development (restricted to local origins by default)
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

# Mount frontend assets if directory exists
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
assets_dir = os.path.join(frontend_dir, "assets")

if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


# ---------------------------------------------------------
# Pydantic Schemas (Module 03 Specification + Extensions)
# ---------------------------------------------------------
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

    @field_validator("table_name")
    @classmethod
    def sanitize_table(cls, v: str) -> str:
        return validate_identifier(v)


class SeedResponse(BaseModel):
    status: str
    table: str
    rows_inserted: int
    execution_time_ms: float


class ConnectionConfigRequest(BaseModel):
    host: str = "localhost"
    port: int = 5432
    database: str = "postgres"
    user: str = "postgres"
    password: str = "postgres"
    persist_env: bool = True


# ---------------------------------------------------------
# Helper Functions: Mermaid Normalization & Grammar
# ---------------------------------------------------------
def sanitize_mermaid_type(raw_type: str) -> str:
    """Normalize Postgres SQL data types into clean Mermaid erDiagram attribute types."""
    t = raw_type.lower().strip()
    mapping = {
        "character varying": "varchar",
        "varchar": "varchar",
        "character": "char",
        "timestamp without time zone": "timestamp",
        "timestamp with time zone": "timestamptz",
        "time without time zone": "time",
        "time with time zone": "timetz",
        "double precision": "float8",
        "real": "float4",
        "smallint": "int2",
        "integer": "int4",
        "bigint": "int8",
        "boolean": "bool",
        "numeric": "numeric",
        "decimal": "decimal",
        "uuid": "uuid",
        "text": "text",
        "json": "json",
        "jsonb": "jsonb",
        "bytea": "bytea",
        "date": "date"
    }
    for k, v in mapping.items():
        if t.startswith(k):
            return v
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", t)
    return cleaned or "string"


def sanitize_identifier(ident: str) -> str:
    """Sanitize entity names for Mermaid compatibility."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", ident)


def generate_mermaid_erd(tables: List[TableMeta]) -> str:
    """
    Compile introspected table schemas into standard Mermaid.js erDiagram syntax.
    Enforces One-to-Many rule (PARENT ||--o{ CHILD : "references") and safe self-referencing.
    """
    lines = ["erDiagram"]
    relationships = set()

    # 1. Define Entities & Attributes
    for table in tables:
        t_name = sanitize_identifier(table.table_name)
        lines.append(f"    {t_name} {{")
        for col in table.columns:
            m_type = sanitize_mermaid_type(col.data_type)
            col_name = sanitize_identifier(col.name)
            modifier = ""
            if col.is_pk and col.is_fk:
                modifier = "PK,FK"
            elif col.is_pk:
                modifier = "PK"
            elif col.is_fk:
                modifier = "FK"

            if modifier:
                lines.append(f"        {m_type} {col_name} {modifier}")
            else:
                lines.append(f"        {m_type} {col_name}")

            # Collect relationships
            if col.is_fk and col.foreign_table:
                parent_name = sanitize_identifier(col.foreign_table)
                label = f"{col.name}"
                # Parent has many children: PARENT ||--o{ CHILD : "label"
                rel_str = f'    {parent_name} ||--o{{ {t_name} : "{label}"'
                relationships.add(rel_str)

        lines.append("    }")

    # 2. Append Relationships (ordered for determinism)
    for rel in sorted(relationships):
        lines.append(rel)

    return "\n".join(lines)


# ---------------------------------------------------------
# Static Frontend Serving
# ---------------------------------------------------------
@app.get("/", include_in_schema=False)
@app.get("/index.html", include_in_schema=False)
async def serve_index():
    """Serve the single-page frontend interface."""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        {"message": "Structura Forge API is running. frontend/index.html not found."},
        status_code=status.HTTP_200_OK
    )


# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------
@app.get("/api/health")
def health_check():
    """
    Executes SELECT 1; against PostgreSQL.
    Returns HTTP 200 on success, HTTP 503 if credentials in .env are invalid or DB is offline.
    """
    parsed = urlparse(DATABASE_URL)
    fallback_host = parsed.hostname or "localhost"
    fallback_port = parsed.port or 5432
    fallback_db = parsed.path.lstrip("/") or "postgres"
    fallback_user = parsed.username or "postgres"

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1, current_database(), inet_server_addr(), inet_server_port();")
            row = cur.fetchone()
            db_name = row[1] if row and len(row) > 1 and row[1] else fallback_db
            host = row[2] if row and len(row) > 2 and row[2] else fallback_host
            port = row[3] if row and len(row) > 3 and row[3] else fallback_port

        return {
            "status": "connected",
            "database": str(db_name),
            "host": str(host),
            "port": str(port),
            "user": str(fallback_user),
            "timestamp": time.time()
        }
    except Exception as exc:
        logger.error("Health check failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"PostgreSQL connection failed: {str(exc)}"
        )
    finally:
        release_db_connection(conn)


@app.get("/api/config")
def get_connection_config():
    """Return current parsed connection settings (excluding raw password)."""
    parsed = urlparse(DATABASE_URL)
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/") or "postgres",
        "user": parsed.username or "postgres"
    }


@app.post("/api/config")
def update_connection_config(cfg: ConnectionConfigRequest):
    """Test new PostgreSQL connection settings and optionally persist to .env."""
    global DATABASE_URL
    encoded_user = quote_plus(cfg.user.strip())
    encoded_pw = quote_plus(cfg.password)
    new_dsn = f"postgresql://{encoded_user}:{encoded_pw}@{cfg.host.strip()}:{cfg.port}/{cfg.database.strip()}"

    # Test connection directly before saving
    test_conn = None
    try:
        test_conn = psycopg2.connect(new_dsn, connect_timeout=3)
        with test_conn.cursor() as cur:
            cur.execute("SELECT current_database();")
            db_name = cur.fetchone()[0]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection test failed: {str(exc)}"
        )
    finally:
        if test_conn:
            test_conn.close()

    DATABASE_URL = new_dsn
    init_db_pool()

    if cfg.persist_env:
        try:
            env_content = (
                "# Structura Environment Variables\n"
                f"DATABASE_URL={new_dsn}\n"
                f"PORT={PORT}\n"
                f"HOST={HOST}\n"
            )
            with open(ENV_PATH, "w", encoding="utf-8") as f:
                f.write(env_content)
        except Exception as exc:
            logger.warning("Could not write to .env file: %s", exc)

    return {
        "status": "connected",
        "host": cfg.host.strip(),
        "port": str(cfg.port),
        "database": str(db_name),
        "user": cfg.user.strip()
    }


@app.post("/api/init-lab")
def initialize_lab_schema():
    """Execute backend/test_schema.sql against the active PostgreSQL database."""
    sql_path = os.path.join(os.path.dirname(__file__), "test_schema.sql")
    if not os.path.exists(sql_path):
        fallback_path = os.path.join(os.path.dirname(__file__), "setup_lab_db.sql")
        if os.path.exists(fallback_path):
            sql_path = fallback_path
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="test_schema.sql not found in backend directory."
            )

    conn = None
    try:
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(sql_script)
        conn.commit()
        return {"status": "success", "message": "Sample test schema (test_schema.sql) initialized successfully."}
    except Exception as exc:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize test schema: {str(exc)}"
        )
    finally:
        release_db_connection(conn)


@app.get("/api/schema", response_model=SchemaResponse)
def get_schema():
    """
    Introspects tables, columns, primary keys, foreign keys, unique constraints, and live row counts.
    Returns structured JSON metadata and ready-to-render Mermaid.js ERD syntax.
    """
    query = """
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
    """

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

        # Deduplicate & aggregate columns per table
        tables_dict: Dict[str, Dict[str, ColumnMeta]] = {}
        for row in rows:
            (
                t_name,
                c_name,
                d_type,
                is_null,
                char_len,
                num_prec,
                num_scale,
                is_pk,
                is_uniq,
                fk_table,
                fk_col,
                col_def,
                is_ident
            ) = row

            if t_name not in tables_dict:
                tables_dict[t_name] = {}

            if c_name not in tables_dict[t_name]:
                tables_dict[t_name][c_name] = ColumnMeta(
                    name=c_name,
                    data_type=d_type or "text",
                    is_nullable=(is_null == "YES"),
                    is_pk=bool(is_pk),
                    is_fk=bool(fk_table),
                    is_unique=bool(is_uniq),
                    foreign_table=fk_table,
                    foreign_column=fk_col,
                    char_max_len=char_len,
                    numeric_precision=num_prec,
                    numeric_scale=num_scale,
                    is_identity=(is_ident == "YES"),
                    column_default=col_def
                )
            else:
                existing = tables_dict[t_name][c_name]
                if is_pk:
                    existing.is_pk = True
                if is_uniq:
                    existing.is_unique = True
                if fk_table:
                    existing.is_fk = True
                    existing.foreign_table = fk_table
                    existing.foreign_column = fk_col

        # Fetch exact row counts per table using safe sql.Identifier quoting
        row_counts: Dict[str, int] = {}
        with conn.cursor() as cur:
            for t_name in tables_dict.keys():
                try:
                    cur.execute(
                        sql.SQL("SELECT COUNT(*) FROM {};").format(sql.Identifier(t_name))
                    )
                    row_counts[t_name] = int(cur.fetchone()[0] or 0)
                except Exception:
                    conn.rollback()
                    row_counts[t_name] = 0

        table_meta_list: List[TableMeta] = []
        for t_name, cols_map in tables_dict.items():
            table_meta_list.append(
                TableMeta(
                    table_name=t_name,
                    row_count=row_counts.get(t_name, 0),
                    columns=list(cols_map.values())
                )
            )

        mermaid_code = generate_mermaid_erd(table_meta_list)

        return SchemaResponse(
            tables=table_meta_list,
            mermaid_syntax=mermaid_code
        )

    except Exception as exc:
        logger.error("Schema introspection failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schema introspection error: {str(exc)}"
        )
    finally:
        release_db_connection(conn)


# ---------------------------------------------------------
# Mock Data Generator (Module 04 Specification)
# ---------------------------------------------------------
def generate_mock_value(
    col: ColumnMeta,
    fk_cache: Dict[str, List[Any]],
    pk_counters: Dict[str, int],
    row_seq: int
) -> Any:
    """Generate constraint-compliant mock values based on Postgres data type and column name context."""
    # 1. Foreign Key resolution (keyed by parent_table.parent_column)
    if col.is_fk and col.foreign_table and col.foreign_column:
        cache_key = f"{col.foreign_table}.{col.foreign_column}"
        if cache_key in fk_cache:
            cached_ids = fk_cache[cache_key]
            if cached_ids:
                if col.is_nullable and fake.boolean(chance_of_getting_true=12):
                    return None
                return fake.random_element(cached_ids)
            if col.is_nullable:
                return None

    # Nullable non-PK, non-UNIQUE columns get a 10% chance of NULL
    if col.is_nullable and not col.is_pk and not col.is_unique and fake.boolean(chance_of_getting_true=10):
        return None

    d_type = col.data_type.lower()
    c_name = col.name.lower()
    max_len = col.char_max_len or 255

    # 2. Sequential integer PK or UNIQUE integer handling (prevents collision)
    if (col.is_pk or col.is_unique) and any(s in d_type for s in ["int", "bigint", "smallint", "numeric"]):
        pk_counters[col.name] = pk_counters.get(col.name, 0) + 1
        return pk_counters[col.name]

    # 3. UUID
    if "uuid" in d_type:
        return str(uuid.uuid4())

    # 4. Text / Varchar Context-Aware (with collision-proof unique/email handling)
    if any(s in d_type for s in ["char", "text", "character varying"]):
        if "email" in c_name:
            salt = uuid.uuid4().hex[:6]
            return f"user{row_seq}_{salt}@{fake.free_email_domain()}"[:max_len]
        if col.is_pk or col.is_unique:
            salt = uuid.uuid4().hex[:6]
            return f"{c_name}_{row_seq}_{salt}"[:max_len]
        if "name" in c_name:
            return fake.name()[:max_len]
        if "phone" in c_name:
            return fake.phone_number()[:max_len]
        if any(w in c_name for w in ["address", "street", "city"]):
            return fake.street_address()[:max_len]
        if "country" in c_name:
            return fake.country()[:max_len]
        if any(w in c_name for w in ["zip", "postal"]):
            return fake.postcode()[:max_len]
        if any(w in c_name for w in ["url", "website"]):
            return fake.url()[:max_len]
        if "status" in c_name:
            return fake.random_element(["active", "pending", "completed", "inactive"])[:max_len]
        if any(w in c_name for w in ["password", "hash", "token"]):
            return fake.sha256()[:max_len]
        if "title" in c_name:
            return fake.sentence(nb_words=3).rstrip(".")[:max_len]
        if any(w in c_name for w in ["desc", "detail", "content", "bio"]):
            return fake.paragraph(nb_sentences=2)[:max_len]

        words_num = max(2, min(6, max_len // 10))
        return fake.sentence(nb_words=words_num).rstrip(".")[:max_len]

    # 5. Integers
    if any(s in d_type for s in ["smallint", "int2"]):
        return fake.random_int(1, 32767)
    if any(s in d_type for s in ["integer", "int4", "int"]):
        return fake.random_int(1, 10000)
    if any(s in d_type for s in ["bigint", "int8"]):
        return fake.random_int(10000, 9999999)

    # 6. Booleans
    if "bool" in d_type:
        return fake.boolean(chance_of_getting_true=50)

    # 7. Dates & Timestamps
    if d_type == "date":
        return fake.date_between(start_date="-2y", end_date="today")
    if "timestamp" in d_type:
        return fake.date_time_between(start_date="-1y", end_date="now")
    if "time" in d_type:
        return fake.time()

    # 8. Numerics & Decimals (respecting precision & scale)
    if any(s in d_type for s in ["numeric", "decimal", "real", "double precision", "float", "money"]):
        scale = int(col.numeric_scale) if col.numeric_scale is not None else 2
        precision = int(col.numeric_precision) if col.numeric_precision is not None else 10
        max_whole_digits = max(1, precision - scale)
        upper_bound = min(5000.0, float((10 ** max_whole_digits) - 1))
        return round(fake.pyfloat(min_value=1.5, max_value=max(2.0, upper_bound)), max(0, scale))

    # 9. JSON / JSONB
    if "json" in d_type:
        return json.dumps({
            "code": fake.word(),
            "count": fake.random_int(1, 100),
            "active": fake.boolean()
        })

    # 10. Network types
    if any(s in d_type for s in ["inet", "cidr"]):
        return fake.ipv4()
    if "macaddr" in d_type:
        return fake.mac_address()

    return fake.word()[:max_len]


@app.post("/api/seed", response_model=SeedResponse)
def seed_table(req: SeedRequest):
    """
    Executes high-throughput mock row injection into target PostgreSQL table.
    Enforces foreign-key preflight validation, auto-omits sequence/serial columns,
    and streams inserts using psycopg2.extras.execute_batch inside an atomic transaction.
    """
    start_time = time.perf_counter()
    table_name = req.table_name.strip()
    row_count = req.row_count
    batch_size = req.batch_size

    conn = None
    try:
        conn = get_db_connection()

        # Step 1: Introspect specific table columns & constraints
        col_query = """
        SELECT 
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
        WHERE c.table_schema = 'public' AND c.table_name = %s
        ORDER BY c.ordinal_position;
        """

        with conn.cursor() as cur:
            cur.execute(col_query, (table_name,))
            rows = cur.fetchall()

        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table '{table_name}' does not exist in 'public' schema."
            )

        columns_map: Dict[str, ColumnMeta] = {}
        for row in rows:
            (
                c_name,
                d_type,
                is_null,
                char_len,
                num_prec,
                num_scale,
                is_pk,
                is_uniq,
                fk_table,
                fk_col,
                col_def,
                is_ident
            ) = row
            if c_name not in columns_map:
                columns_map[c_name] = ColumnMeta(
                    name=c_name,
                    data_type=d_type or "text",
                    is_nullable=(is_null == "YES"),
                    is_pk=bool(is_pk),
                    is_fk=bool(fk_table),
                    is_unique=bool(is_uniq),
                    foreign_table=fk_table,
                    foreign_column=fk_col,
                    char_max_len=char_len,
                    numeric_precision=num_prec,
                    numeric_scale=num_scale,
                    is_identity=(is_ident == "YES"),
                    column_default=col_def
                )
            else:
                if is_pk:
                    columns_map[c_name].is_pk = True
                if is_uniq:
                    columns_map[c_name].is_unique = True
                if fk_table:
                    columns_map[c_name].is_fk = True
                    columns_map[c_name].foreign_table = fk_table
                    columns_map[c_name].foreign_column = fk_col

        # Step 2: Auto-exclude SERIAL, BIGSERIAL, IDENTITY, nextval columns
        insertable_cols: List[ColumnMeta] = []
        for col in columns_map.values():
            default_val = (col.column_default or "").lower()
            if col.is_identity:
                continue
            if "nextval(" in default_val:
                continue
            if col.data_type.lower() in ["serial", "bigserial", "smallserial"]:
                continue
            insertable_cols.append(col)

        if not insertable_cols:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Table '{table_name}' has no writable columns (all columns are generated or identity)."
            )

        # Step 3: Foreign Key Pre-Flight Lookup (safe sql.Identifier quoting)
        fk_cache: Dict[str, List[Any]] = {}
        with conn.cursor() as cur:
            for col in insertable_cols:
                if col.is_fk and col.foreign_table and col.foreign_column:
                    parent_table = col.foreign_table
                    parent_col = col.foreign_column
                    cache_key = f"{parent_table}.{parent_col}"

                    if cache_key not in fk_cache:
                        fk_sql = sql.SQL(
                            "SELECT {col} FROM {tbl} WHERE {col} IS NOT NULL ORDER BY RANDOM() LIMIT 500;"
                        ).format(
                            col=sql.Identifier(parent_col),
                            tbl=sql.Identifier(parent_table)
                        )
                        try:
                            cur.execute(fk_sql)
                            parent_records = [r[0] for r in cur.fetchall()]
                        except Exception as fk_err:
                            conn.rollback()
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Failed querying parent table '{parent_table}': {str(fk_err)}"
                            )

                        if not parent_records:
                            if parent_table == table_name and col.is_nullable:
                                fk_cache[cache_key] = []
                            else:
                                conn.rollback()
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Cannot seed child table '{table_name}': Parent table '{parent_table}' contains no rows."
                                )
                        else:
                            fk_cache[cache_key] = parent_records

        # Step 4: Initialize PK/Unique counters for non-serial integer keys
        pk_counters: Dict[str, int] = {}
        with conn.cursor() as cur:
            for col in insertable_cols:
                if (col.is_pk or col.is_unique) and any(s in col.data_type.lower() for s in ["int", "bigint", "smallint", "numeric"]):
                    try:
                        cur.execute(
                            sql.SQL("SELECT COALESCE(MAX({col}), 0) FROM {tbl};").format(
                                col=sql.Identifier(col.name),
                                tbl=sql.Identifier(table_name)
                            )
                        )
                        max_val = cur.fetchone()[0] or 0
                        pk_counters[col.name] = int(max_val)
                    except Exception:
                        conn.rollback()
                        pk_counters[col.name] = 0

        # Step 5: Construct safe INSERT query via psycopg2.sql
        insert_query = sql.SQL("INSERT INTO {tbl} ({cols}) VALUES ({vals})").format(
            tbl=sql.Identifier(table_name),
            cols=sql.SQL(", ").join(sql.Identifier(col.name) for col in insertable_cols),
            vals=sql.SQL(", ").join(sql.Placeholder() for _ in insertable_cols),
        )

        # Step 6: High-speed Batch Seeding inside single transaction
        with conn.cursor() as cur:
            rows_remaining = row_count
            row_seq = 1
            while rows_remaining > 0:
                current_batch_size = min(rows_remaining, batch_size)
                batch_data = []
                for _ in range(current_batch_size):
                    row_vals = tuple(
                        generate_mock_value(col, fk_cache, pk_counters, row_seq) for col in insertable_cols
                    )
                    batch_data.append(row_vals)
                    row_seq += 1

                extras.execute_batch(
                    cur,
                    insert_query,
                    batch_data,
                    page_size=current_batch_size
                )
                rows_remaining -= current_batch_size

            conn.commit()

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "Seeded %d rows into '%s' in %.2f ms",
            row_count, table_name, elapsed_ms
        )

        return SeedResponse(
            status="success",
            table=table_name,
            rows_inserted=row_count,
            execution_time_ms=elapsed_ms
        )

    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as exc:
        if conn:
            conn.rollback()
        logger.error("Seeding operation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Seeding transaction failed and rolled back: {str(exc)}"
        )
    finally:
        release_db_connection(conn)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
