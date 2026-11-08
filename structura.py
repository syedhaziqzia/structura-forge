#!/usr/bin/env python3
"""
STRUCTURA FORGE — Terminal User Interface (TUI) & CLI Entrypoint
PostgreSQL Architecture Mapping & High-Velocity Seeder

Usage:
  python structura.py          # Launch interactive Emerald/Obsidian TUI
  python structura.py --web    # Launch FastAPI + Web Studio directly
"""

import argparse
import json
import os
import random
import socket
import subprocess
import sys
import time
import uuid
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, quote_plus

import psycopg2
from psycopg2 import extras, sql
from dotenv import load_dotenv
from faker import Faker

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.rule import Rule
from rich.style import Style
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

# =====================================================================
# PATHS, ENVIRONMENT & THEME CONSTANTS
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
ERD_EXPORT_PATH = BASE_DIR / "erd_blueprint.md"
SETUP_SQL_PATH = BASE_DIR / "backend" / "test_schema.sql"

load_dotenv(dotenv_path=ENV_PATH, override=True)

# Exact Emerald Green Shades matching the Web Studio (#10B981 / #34D399)
EMERALD = "#10B981"
EMERALD_BRIGHT = "#34D399"
EMERALD_DEEP = "#059669"
EMERALD_DARK_BG = "#030504"
GOLD_PK = "#FBBF24"
MUTED_TEXT = "#A1A1AA"
DIM_TEXT = "#52525B"
ERROR_RED = "#F43F5E"

import io
import zlib
import base64

# Robust UTF-8 Console initialization across all Windows terminals
try:
    utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    console = Console(file=utf8_stdout, highlight=False, legacy_windows=False)
except Exception:
    console = Console(highlight=False, legacy_windows=False)

fake = Faker()

# =====================================================================
# AUTHENTIC 3D ISOMETRIC LOGO (SAMPLED DIRECTLY FROM STRUCTURA LOGO)
# Compressed 32x28 Truecolor RGB Pixel Matrix
# =====================================================================
LOGO_PIXELS_B64 = (
    "eNqdVntsU2UUv23v+317b9+3Xdt1He3adZtbW/Zwg43hGGPAeOwBCGyOt4CEMYa8BASCgGCIEhNM/APFo"
    "AEJaEAiZCwDFRBEhBglMVFmCEEQCI+xeu7AiHaI88td0n3fd16/8zvnfAjSj8UH3WKGG+nn0ung7yl3DAxJ"
    "OmQxO1XKSSXtRgNLJin5U4Xub7+funCToFRH+RwvrvC4wvV+PJ/tVUZEcbPQl7tJFp+wUIGhnAofcbNhN6jS"
    "mVgEA3uIzszBv2xGCh/xkKqCikx/EaP8dibdQToVXOYIi4hINGzKVvOG1zdt2LJZsZq1SxINRxALqcqM3077"
    "7X2g8RD5xwKB+7TXqoyKseEUwiEb7CJsmkKeFatW3rxy7WbPvZvdd29fu/7K6lXmkFfLi02AvLAZToCL9tlA"
    "PBmoh0uOB7hwCqBtoAkm1aptiZjgsixesPDGr1fvJno2du7xrJ9saRr66u4dd3q6b127vmRhq6CaEQlQQ2iP"
    "FWVJTOE1W/nBZEysVVEx5of0YQJtcMu8LLa0Lvqt68qDRGJz597A1ul0W5VQE8djPqQ8qDZWrN29434i8fvV"
    "a4vbFosmo16VMIkF/8Vomm3kwOSM41axlyG8NPyZ4evm/nz5l0Qi8fapg+Fts6lFlUJtAeXVgtLp9YTNiOWl"
    "ImUDXM2VWw68D9cud3WN2DDfODKmaTDxuE1KphDASJgFymU2KFzWphlrvtpT/u5SdsUodnSUiXh0vVfpDBd8"
    "eoMBrFDpqj6SggzPLFgzra3jvdCmZswE4iZAmHQoyfjIw3LpNDvKkITMqy2j09ZM4SYWm6ryWIcsDM3hIX0R"
    "N+WzkR4LFUoRxhaKVTHOZVLKs9iJxa7VE22zKkAQZSk61SpX5iaXHu2zQ1oBQyGapi4anbK8ThhTgPAU7ZBt"
    "jWWOlpFK4xC2NMKUZ6Hj41TdQNPIGByhUGuVUSroAjJLRUHcyDKpNuB2MoU06CQWap+NuF2tNWrbWHpUHFVl"
    "OCKiaeaZw6yzK52tNWkt4+a9tbZuUsOjGjRyegKDjw6ofNwP4mACIErGRywKAoEhBRAj4ONc1bD94Ec/nL/Y"
    "NGUqbuQQhSYGhZ3La/NWTj10vB1yeubk6RGVwxGnhNA6BDOgNIEJDFQclI/4bKiP3hjzswEV9HNBl5AfsM6s"
    "KNy+YNupT28nui99e7GxYZKBwBCvkanN11fllC5pPnz2C7By9vy56vE1CKZDKEzITiWsEht0CvkDkvkJR5jI"
    "oDxtG12gFIe1Ykm3YQ3x4GsvbD154Fbi/qVzF6bNmcE4ZMxjQUoCSHVOyZLmI+dOgpWjHe2h6dWm6jgq0JBB"
    "0mZM9h/4iRk5ymnSygQ4BkiKDOu1EdlurD4e3Ni87eQnXT23dx7aZ7ZadKiB8DuQAj9aO3DWri3rTu9zt4zR"
    "0QS0O2hZffLTWBoBagGMpPVRdeiznc6moXSKSUuKz4LXDwxtnZG5bDKuauKESWDT7Vx1njS5LLi+yTazAuhh"
    "oAhQYizPTtbPAD+9VkglGXHFRpS9s3fXmDdeRmRKOwLm242a6Sw3lm5HeQqYTIddmpgq0/VFrpX1jlmVYq4P"
    "xHv5qSbzE8B5SAAy05W/tGn/mc5ET0/HsWNDSsseAajK5uKwpTSLcGqkRUl87qw5Fy5cnL9jk3nZOGdLDZfl"
    "AXFIIiZzyf6bijNpj4W0SDjP6IMOpDAt96UJH355pCeR6DzaXt5rBY84sUzNt+frJ/z0/Y93Eg+2dH4c3fqi"
    "MrWMy/WhHAUkod0W86CsPvif6YEjgBqA0ut1MHCRDDtS4MueV7fr+GGwcqK9o+S5ssqa6u++/qY7kXjzxP7A"
    "2kZDXYzK8wF1AQnW7yCB/x6LFEl90ogEgomFQWlQGPgDCEC/QtKtSFFaZF7dB52fXb5z/fK9GztPfx7ZMA2d"
    "mE/meilVMeAYEFIqCYtFGdDbn/6cwAy4IgBRtYqQWIwhtfp1GZGyYObC+tyNM8nGYjSkwiY4ABcIm/SwbYLg"
    "kx8ofc53WqvHAU6YrRhPERBRxEXGfdpMZ0loJjCqYBbAM+Afyv7S9x/eJ8ArYXCY6OWn1gOhCcNbyG6EzT55"
    "8v8WND3SJpkGR8xDsqHSUY7uzwPusUD+NSJugFMIuPrl2B8eR2qe"
)

# =====================================================================
# PROFESSIONAL SLANT WORDMARK (EXACT 57-CHAR SYMMETRIC WIDTH PER LINE)
# =====================================================================
BANNER_WORDMARK_LINES = [
    "  ____ _____ ____  _   _  ____ _____ _   _ ____     _    ",
    " / ___|_   _|  _ \\| | | |/ ___|_   _| | | |  _ \\   / \\   ",
    " \\___ \\ | | | |_) | | | | |     | | | | | | |_) | / _ \\  ",
    "  ___) || | |  _ <| |_| | |___  | | | |_| |  _ < / ___ \\ ",
    " |____/ |_| |_| \\_\\\\___/ \\____| |_|  \\___/|_| \\_/_/   \\_\\",
]

# Built-in 6-Table Reference Schema (Fallback when Live DB is unreachable)
FALLBACK_SCHEMA_TABLES: List[Dict[str, Any]] = [
    {
        "table_name": "users",
        "row_count": 250,
        "columns": [
            {"name": "id", "data_type": "uuid", "is_nullable": False, "is_pk": True, "is_fk": False, "foreign_table": None, "foreign_column": None},
            {"name": "email", "data_type": "character varying", "char_max_len": 120, "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
            {"name": "full_name", "data_type": "character varying", "char_max_len": 100, "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
            {"name": "is_active", "data_type": "boolean", "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
            {"name": "created_at", "data_type": "timestamp with time zone", "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
        ],
    },
    {
        "table_name": "categories",
        "row_count": 24,
        "columns": [
            {"name": "category_id", "data_type": "serial", "is_nullable": False, "is_pk": True, "is_fk": False, "foreign_table": None, "foreign_column": None, "column_default": "nextval('categories_id_seq')"},
            {"name": "name", "data_type": "character varying", "char_max_len": 80, "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
            {"name": "parent_category_id", "data_type": "integer", "is_nullable": True, "is_pk": False, "is_fk": True, "foreign_table": "categories", "foreign_column": "category_id"},
        ],
    },
    {
        "table_name": "products",
        "row_count": 180,
        "columns": [
            {"name": "product_id", "data_type": "uuid", "is_nullable": False, "is_pk": True, "is_fk": False, "foreign_table": None, "foreign_column": None},
            {"name": "category_id", "data_type": "integer", "is_nullable": False, "is_pk": False, "is_fk": True, "foreign_table": "categories", "foreign_column": "category_id"},
            {"name": "product_name", "data_type": "character varying", "char_max_len": 150, "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
            {"name": "unit_price", "data_type": "numeric", "numeric_precision": 10, "numeric_scale": 2, "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
            {"name": "stock_qty", "data_type": "integer", "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
        ],
    },
    {
        "table_name": "orders",
        "row_count": 1200,
        "columns": [
            {"name": "order_id", "data_type": "bigserial", "is_nullable": False, "is_pk": True, "is_fk": False, "foreign_table": None, "foreign_column": None, "column_default": "nextval('orders_order_id_seq')"},
            {"name": "user_id", "data_type": "uuid", "is_nullable": False, "is_pk": False, "is_fk": True, "foreign_table": "users", "foreign_column": "id"},
            {"name": "total_amount", "data_type": "numeric", "numeric_precision": 12, "numeric_scale": 2, "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
            {"name": "order_date", "data_type": "date", "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
            {"name": "shipping_address", "data_type": "text", "is_nullable": True, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
        ],
    },
    {
        "table_name": "order_items",
        "row_count": 3400,
        "columns": [
            {"name": "item_id", "data_type": "bigserial", "is_nullable": False, "is_pk": True, "is_fk": False, "foreign_table": None, "foreign_column": None, "column_default": "nextval('order_items_id_seq')"},
            {"name": "order_id", "data_type": "bigint", "is_nullable": False, "is_pk": False, "is_fk": True, "foreign_table": "orders", "foreign_column": "order_id"},
            {"name": "product_id", "data_type": "uuid", "is_nullable": False, "is_pk": False, "is_fk": True, "foreign_table": "products", "foreign_column": "product_id"},
            {"name": "quantity", "data_type": "smallint", "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
            {"name": "line_total", "data_type": "numeric", "numeric_precision": 12, "numeric_scale": 2, "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
        ],
    },
    {
        "table_name": "audit_logs",
        "row_count": 0,
        "columns": [
            {"name": "log_id", "data_type": "uuid", "is_nullable": False, "is_pk": True, "is_fk": False, "foreign_table": None, "foreign_column": None},
            {"name": "actor_user_id", "data_type": "uuid", "is_nullable": False, "is_pk": False, "is_fk": True, "foreign_table": "users", "foreign_column": "id"},
            {"name": "payload", "data_type": "jsonb", "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
            {"name": "logged_at", "data_type": "timestamp without time zone", "is_nullable": False, "is_pk": False, "is_fk": False, "foreign_table": None, "foreign_column": None},
        ],
    },
]


def get_database_url() -> str:
    """Reloads .env and returns the current DATABASE_URL."""
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/postgres",
    )


def parse_dsn_summary(dsn: str) -> str:
    """Returns a safe host:port/db string without exposing passwords."""
    try:
        p = urlparse(dsn)
        host = p.hostname or "localhost"
        port = p.port or 5432
        db = (p.path or "/postgres").lstrip("/") or "postgres"
        user = p.username or "postgres"
        return f"{user}@{host}:{port}/{db}"
    except Exception:
        return "localhost:5432/postgres"


def render_error_card(title: str, error: Exception, hint: Optional[str] = None) -> None:
    """Renders a clean, Obsidian & Crimson/Amber error card without raw tracebacks."""
    dsn_summary = parse_dsn_summary(get_database_url())
    msg = str(error).strip()

    body = Text()
    body.append("[X] Database Operation Aborted\n\n", style=f"bold {ERROR_RED}")
    body.append("Target Instance : ", style=f"bold {MUTED_TEXT}")
    body.append(f"{dsn_summary}\n", style="bold white")
    body.append("Driver Detail   : ", style=f"bold {MUTED_TEXT}")
    body.append(f"{msg}\n", style="#FDA4AF")

    if hint:
        body.append("\n[TIP] Resolution : ", style=f"bold {GOLD_PK}")
        body.append(hint, style=f"{EMERALD_BRIGHT}")
    else:
        body.append("\n[TIP] Resolution : ", style=f"bold {GOLD_PK}")
        body.append(
            "Verify that your PostgreSQL service is running and that DATABASE_URL in .env has the valid password.",
            style=f"{EMERALD_BRIGHT}",
        )

    panel = Panel(
        body,
        title=f"[bold {ERROR_RED}][ ! {title} ][/]",
        border_style=ERROR_RED,
        box=box.SQUARE,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)


def get_authentic_isometric_logo() -> Text:
    """Renders the authentic Structura 3D isometric hexagon lattice logo with clean symmetric outlines."""
    raw = zlib.decompress(base64.b64decode(LOGO_PIXELS_B64))
    W, H = 32, 28

    pixels: List[List[List[int]]] = []
    for y in range(H):
        row = []
        for x in range(W):
            i = (y * W + x) * 3
            row.append([raw[i], raw[i + 1], raw[i + 2]])
        pixels.append(row)

    # Apply clean symmetric isometric hexagon mask (eliminates noisy outer floating dots)
    for y in range(H):
        if y < 4 or y > 24:
            for x in range(W):
                pixels[y][x] = [0, 0, 0]
        elif y <= 13:
            allowed_r = 3.0 + (y - 4) * 1.05
            for x in range(W):
                dist = abs(x - 15.5)
                if dist > allowed_r or (pixels[y][x][0] < 42 and pixels[y][x][1] < 42 and pixels[y][x][2] < 42):
                    pixels[y][x] = [0, 0, 0]
        else:
            allowed_r = 12.5 - (y - 14) * 0.95
            for x in range(W):
                dist = abs(x - 15.5)
                if dist > allowed_r or (pixels[y][x][0] < 42 and pixels[y][x][1] < 42 and pixels[y][x][2] < 42):
                    pixels[y][x] = [0, 0, 0]

    lines: List[Text] = []
    for y in range(4, 25, 2):
        line = Text()
        for x in range(5, 27):
            tr, tg, tb = pixels[y][x]
            br, bg, bb = pixels[y + 1][x]

            td = tr < 30 and tg < 30 and tb < 30
            bd = br < 30 and bg < 30 and bb < 30

            if td and bd:
                line.append(" ")
            elif not td and bd:
                line.append("▀", style=f"rgb({tr},{tg},{tb})")
            elif td and not bd:
                line.append("▄", style=f"rgb({br},{bg},{bb})")
            else:
                line.append("▀", style=f"rgb({tr},{tg},{tb}) on rgb({br},{bg},{bb})")
        lines.append(line)
    return Text("\n").join(lines)


def render_banner() -> None:
    """Displays the authentic 3D Isometric Hexagon Logo + Professional Slant Wordmark centered inside a precision-boxed Panel."""
    dsn = get_database_url()
    dsn_summary = parse_dsn_summary(dsn)

    # Check quick connectivity for header status pill
    is_online = False
    try:
        conn = psycopg2.connect(dsn, connect_timeout=2)
        conn.close()
        is_online = True
    except Exception:
        is_online = False

    # 1. Authentic 3D Isometric Hexagon Logo (each line is 22 cells wide, centered independently)
    logo_block = get_authentic_isometric_logo()

    # 2. Professional Slant Wordmark in Emerald Gradient (each line is 57 cells wide, centered independently)
    wordmark_lines: List[Text] = []
    for i, line in enumerate(BANNER_WORDMARK_LINES):
        if i == 0:
            wordmark_lines.append(Text(line, style="bold #6EE7B7"))
        elif i in (1, 2):
            wordmark_lines.append(Text(line, style="bold #34D399"))
        else:
            wordmark_lines.append(Text(line, style="bold #10B981"))
    wordmark_block = Text("\n").join(wordmark_lines)

    # 3. Subtitle (centered independently)
    subtitle_block = Text(
        "PostgreSQL Architecture Mapping & High-Velocity Seeder",
        style="bold white",
    )

    # 4. Status Indicator Badge (centered independently, 100% 1-cell ASCII characters)
    status_block = Text()
    if is_online:
        status_block.append(" [ LIVE CONNECTED ] ", style=f"bold #022016 on {EMERALD_BRIGHT}")
        status_block.append(f"  {dsn_summary}", style=f"bold {EMERALD_BRIGHT}")
    else:
        status_block.append(" [ DB UNREACHABLE ] ", style=f"bold #1F1200 on {GOLD_PK}")
        status_block.append(f"  {dsn_summary} (Check .env)", style=f"{GOLD_PK}")

    banner_group = Group(
        Align.center(logo_block),
        Text(""),
        Align.center(wordmark_block),
        Text(""),
        Align.center(subtitle_block),
        Text(""),
        Align.center(status_block),
    )

    banner_panel = Panel(
        banner_group,
        border_style=f"bold {EMERALD}",
        box=box.SQUARE,
        style=f"on {EMERALD_DARK_BG}",
        padding=(1, 2),
        title=f"[bold {EMERALD_BRIGHT}][ STRUCTURA FORGE TUI v1.0 ][/]",
        subtitle=f"[{MUTED_TEXT}]Zero-Telemetry Local Developer Utility[/]",
    )
    console.print()
    console.print(banner_panel)


# =====================================================================
# SCHEMA INTROSPECTION & MERMAID COMPILER
# =====================================================================
SQL_TYPE_SHORTHAND = {
    "character varying": "varchar",
    "varchar": "varchar",
    "character": "char",
    "timestamp with time zone": "timestamptz",
    "timestamp without time zone": "timestamp",
    "time with time zone": "timetz",
    "time without time zone": "time",
    "double precision": "float8",
    "real": "float4",
    "smallint": "int2",
    "integer": "int4",
    "bigint": "int8",
    "boolean": "bool",
    "uuid": "uuid",
    "text": "text",
    "date": "date",
    "numeric": "numeric",
    "decimal": "decimal",
    "jsonb": "jsonb",
    "json": "json",
    "serial": "serial",
    "bigserial": "bigserial",
}


def sanitize_mermaid_type(data_type: str) -> str:
    raw = (data_type or "text").lower().strip()
    mapped = SQL_TYPE_SHORTHAND.get(raw, raw)
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in mapped).strip("_")
    return cleaned or "text"


def introspect_public_schema() -> List[Dict[str, Any]]:
    """
    Connects to PostgreSQL and extracts all public base tables, columns,
    primary keys, foreign keys, and live row counts.
    Raises psycopg2.OperationalError if connection fails.
    """
    dsn = get_database_url()
    conn = psycopg2.connect(dsn, connect_timeout=3)
    try:
        with conn.cursor() as cur:
            # 1. Base tables
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name;
                """
            )
            table_names = [r[0] for r in cur.fetchall()]
            if not table_names:
                return []

            # 2. Columns
            cur.execute(
                """
                SELECT
                    table_name,
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    is_identity,
                    ordinal_position
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
                """
            )
            col_rows = cur.fetchall()

            # 3. Primary Keys & Unique Constraints
            cur.execute(
                """
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    tc.constraint_type
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type IN ('PRIMARY KEY', 'UNIQUE')
                  AND tc.table_schema = 'public';
                """
            )
            pk_set = set()
            unique_set = set()
            for tbl_n, col_n, c_type in cur.fetchall():
                if c_type == "PRIMARY KEY":
                    pk_set.add((tbl_n, col_n))
                elif c_type == "UNIQUE":
                    unique_set.add((tbl_n, col_n))

            # 4. Foreign Keys
            cur.execute(
                """
                SELECT
                    tc.table_name AS source_table,
                    kcu.column_name AS source_column,
                    ccu.table_name AS target_table,
                    ccu.column_name AS target_column
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                 AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = 'public';
                """
            )
            fk_map: Dict[Tuple[str, str], Tuple[str, str]] = {}
            for src_tbl, src_col, tgt_tbl, tgt_col in cur.fetchall():
                fk_map[(src_tbl, src_col)] = (tgt_tbl, tgt_col)

            # 5. Live Row Counts (using safe sql.Identifier quoting)
            row_counts: Dict[str, int] = {}
            for t_name in table_names:
                try:
                    cur.execute(
                        sql.SQL("SELECT COUNT(*) FROM {};").format(sql.Identifier(t_name))
                    )
                    row_counts[t_name] = int(cur.fetchone()[0])
                except Exception:
                    conn.rollback()
                    row_counts[t_name] = 0

            tables_dict: Dict[str, List[Dict[str, Any]]] = {t: [] for t in table_names}
            for (
                t_name,
                c_name,
                d_type,
                is_null,
                col_def,
                char_len,
                num_prec,
                num_scale,
                is_ident,
                _ord,
            ) in col_rows:
                if t_name not in tables_dict:
                    continue
                is_pk = (t_name, c_name) in pk_set
                is_uniq = (t_name, c_name) in unique_set
                fk_target = fk_map.get((t_name, c_name))
                is_fk = fk_target is not None
                tables_dict[t_name].append(
                    {
                        "name": c_name,
                        "data_type": d_type,
                        "is_nullable": (is_null == "YES"),
                        "is_pk": is_pk,
                        "is_fk": is_fk,
                        "is_unique": is_uniq,
                        "foreign_table": fk_target[0] if fk_target else None,
                        "foreign_column": fk_target[1] if fk_target else None,
                        "column_default": col_def,
                        "char_max_len": char_len,
                        "numeric_precision": num_prec,
                        "numeric_scale": num_scale,
                        "is_identity": (is_ident == "YES"),
                    }
                )

            return [
                {
                    "table_name": t_name,
                    "row_count": row_counts.get(t_name, 0),
                    "columns": tables_dict[t_name],
                }
                for t_name in table_names
            ]
    finally:
        conn.close()


def compile_mermaid_erd(tables: List[Dict[str, Any]]) -> str:
    """Compiles introspected table metadata into Mermaid.js erDiagram syntax."""
    lines = ["erDiagram"]
    relationships: List[str] = []

    for table in tables:
        t_name = table["table_name"]
        lines.append(f"    {t_name} {{")
        for col in table["columns"]:
            c_type = sanitize_mermaid_type(col["data_type"])
            c_name = col["name"]
            if col["is_pk"] and col["is_fk"]:
                lines.append(f"        {c_type} {c_name} PK,FK")
            elif col["is_pk"]:
                lines.append(f"        {c_type} {c_name} PK")
            elif col["is_fk"]:
                lines.append(f"        {c_type} {c_name} FK")
            else:
                lines.append(f"        {c_type} {c_name}")

            if col["is_fk"] and col["foreign_table"]:
                parent = col["foreign_table"]
                relationships.append(f'    {parent} ||--o{{ {t_name} : "{c_name}"')
        lines.append("    }")

    for rel in sorted(set(relationships)):
        lines.append(rel)

    return "\n".join(lines)


# =====================================================================
# OPTION [1]: VIEW SCHEMA TREE
# =====================================================================
def action_view_schema_tree() -> None:
    """Queries PostgreSQL information_schema and renders a Rich Tree (Gold PKs, Emerald FKs)."""
    try:
        with console.status(
            f"[bold {EMERALD_BRIGHT}]Introspecting PostgreSQL public schema...[/]",
            spinner="dots",
        ):
            tables = introspect_public_schema()
    except psycopg2.OperationalError as exc:
        render_error_card("PostgreSQL Connection Failed", exc)
        if Confirm.ask(
            f"\n[bold {EMERALD_BRIGHT}]Render Preview Sandbox schema tree (6-table reference lab) instead?[/]",
            default=True,
        ):
            tables = FALLBACK_SCHEMA_TABLES
        else:
            return
    except psycopg2.Error as exc:
        render_error_card("Database Query Error", exc)
        return

    if not tables:
        console.print(
            Panel(
                f"[bold {GOLD_PK}]No tables found in the 'public' schema.[/]\n"
                f"[{MUTED_TEXT}]Tip: You can provision the 6-table reference schema from [{EMERALD_BRIGHT}]backend/test_schema.sql[/].[/]",
                title=f"[bold {GOLD_PK}] Empty Schema [/]",
                border_style=GOLD_PK,
                box=box.SQUARE,
            )
        )
        if SETUP_SQL_PATH.exists() and Confirm.ask(
            f"[bold {EMERALD_BRIGHT}]Would you like to provision the 6 reference test tables (test_schema.sql) now?[/]",
            default=True,
        ):
            provision_lab_schema_interactive()
        return

    total_cols = sum(len(t["columns"]) for t in tables)
    total_fks = sum(1 for t in tables for c in t["columns"] if c["is_fk"])

    root_label = Text()
    root_label.append("[SCHEMA: public] ", style=f"bold {EMERALD_BRIGHT}")
    root_label.append(
        f"({len(tables)} tables | {total_cols} columns | {total_fks} foreign keys)",
        style=MUTED_TEXT,
    )
    tree = Tree(root_label, guide_style=f"{EMERALD_DEEP}")

    for tbl in tables:
        t_node_label = Text()
        t_node_label.append(f"+ {tbl['table_name']} ", style="bold white")
        t_node_label.append(f"[{tbl['row_count']:,} rows]", style=f"bold {EMERALD}")
        t_branch = tree.add(t_node_label)

        for col in tbl["columns"]:
            c_text = Text()
            c_name = col["name"]
            c_type = sanitize_mermaid_type(col["data_type"])
            if col.get("char_max_len"):
                c_type = f"varchar({col['char_max_len']})"

            if col["is_pk"] and col["is_fk"]:
                c_text.append("[PK][FK] ", style=f"bold {GOLD_PK}")
                c_text.append(f"{c_name:<22}", style=f"bold {GOLD_PK}")
                c_text.append(f" {c_type:<14} ", style=MUTED_TEXT)
                c_text.append(" PK ", style=f"bold #1F1200 on {GOLD_PK}")
                c_text.append(
                    f" FK -> {col['foreign_table']}.{col['foreign_column']} ",
                    style=f"bold #022016 on {EMERALD_BRIGHT}",
                )
            elif col["is_pk"]:
                c_text.append("[PK]     ", style=f"bold {GOLD_PK}")
                c_text.append(f"{c_name:<22}", style=f"bold {GOLD_PK}")
                c_text.append(f" {c_type:<14} ", style=MUTED_TEXT)
                c_text.append(" PRIMARY KEY ", style=f"bold #1F1200 on {GOLD_PK}")
            elif col["is_fk"]:
                c_text.append("[FK]     ", style=f"bold {EMERALD_BRIGHT}")
                c_text.append(f"{c_name:<22}", style=f"bold {EMERALD_BRIGHT}")
                c_text.append(f" {c_type:<14} ", style=MUTED_TEXT)
                c_text.append(
                    f" FK -> {col['foreign_table']}.{col['foreign_column']} ",
                    style=f"bold #022016 on {EMERALD}",
                )
            else:
                c_text.append("  -      ", style=DIM_TEXT)
                c_text.append(f"{c_name:<22}", style="white")
                c_text.append(f" {c_type:<14}", style=MUTED_TEXT)

            if not col["is_nullable"] and not col["is_pk"]:
                c_text.append(" NOT NULL", style=DIM_TEXT)

            t_branch.add(c_text)

    console.print()
    console.print(
        Panel(
            tree,
            title=f"[bold {EMERALD_BRIGHT}][ POSTGRESQL SCHEMA ARCHITECTURE TREE ][/]",
            subtitle=f"[bold {GOLD_PK}][PK] Gold = Primary Key[/]  |  [bold {EMERALD_BRIGHT}][FK] Emerald = Foreign Key[/]",
            border_style=EMERALD,
            box=box.SQUARE,
            padding=(1, 2),
        )
    )


def provision_lab_schema_interactive() -> None:
    """Executes backend/test_schema.sql against the active PostgreSQL database."""
    try:
        sql_script = SETUP_SQL_PATH.read_text(encoding="utf-8")
        conn = psycopg2.connect(get_database_url(), connect_timeout=3)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql_script)
            console.print(
                f"\n[bold {EMERALD_BRIGHT}][OK] Successfully provisioned the 6-table test schema (backend/test_schema.sql)![/]"
            )
        finally:
            conn.close()
    except psycopg2.OperationalError as exc:
        render_error_card("Cannot Provision Schema (DB Unreachable)", exc)
    except Exception as exc:
        render_error_card("Provisioning Failed", exc)


def configure_env_interactive() -> None:
    """Interactive prompt to update .env PostgreSQL connection settings and optionally provision test_schema.sql."""
    parsed = urlparse(get_database_url())
    default_host = parsed.hostname or "localhost"
    default_port = parsed.port or 5432
    default_db = (parsed.path or "/postgres").lstrip("/") or "postgres"
    default_user = parsed.username or "postgres"

    console.print()
    console.print(
        Panel(
            f"[bold white]Configure your local PostgreSQL credentials for [{EMERALD_BRIGHT}].env[/].[/]\n"
            f"[{MUTED_TEXT}]Press Enter on any prompt to keep the current value.[/]",
            title=f"[bold {EMERALD_BRIGHT}][ POSTGRESQL CONNECTION & TEST SCHEMA SETUP ][/]",
            border_style=EMERALD,
            box=box.SQUARE,
            padding=(1, 2),
        )
    )

    host = Prompt.ask(f"[bold {EMERALD_BRIGHT}]PostgreSQL Host[/]", default=default_host).strip()
    port = IntPrompt.ask(f"[bold {EMERALD_BRIGHT}]PostgreSQL Port[/]", default=default_port)
    database = Prompt.ask(f"[bold {EMERALD_BRIGHT}]Database Name[/]", default=default_db).strip()
    user = Prompt.ask(f"[bold {EMERALD_BRIGHT}]Database User[/]", default=default_user).strip()
    password = Prompt.ask(
        f"[bold {EMERALD_BRIGHT}]Database Password[/]",
        password=True,
        default=parsed.password or "postgres",
    )

    encoded_user = quote_plus(user)
    encoded_pw = quote_plus(password)
    new_dsn = f"postgresql://{encoded_user}:{encoded_pw}@{host}:{port}/{database}"

    # Test connection
    try:
        conn = psycopg2.connect(new_dsn, connect_timeout=3)
        conn.close()
        console.print(f"\n[bold {EMERALD_BRIGHT}][OK] Connection verified: {user}@{host}:{port}/{database}[/]")
    except Exception as exc:
        render_error_card("Connection Test Failed", exc)
        if not Confirm.ask(
            f"[bold {GOLD_PK}]Save these credentials to .env anyway?[/]",
            default=False,
        ):
            return

    env_text = (
        "# Structura Environment Variables\n"
        f"DATABASE_URL={new_dsn}\n"
        "PORT=8000\n"
        "HOST=127.0.0.1\n"
    )
    ENV_PATH.write_text(env_text, encoding="utf-8")
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    console.print(f"[bold {EMERALD_BRIGHT}][OK] Updated {ENV_PATH}[/]")

    if SETUP_SQL_PATH.exists() and Confirm.ask(
        f"\n[bold {EMERALD_BRIGHT}]Provision the 6-table reference schema from backend/test_schema.sql now?[/]",
        default=True,
    ):
        provision_lab_schema_interactive()

    render_banner()


# =====================================================================
# OPTION [2]: EXPORT MERMAID ERD
# =====================================================================
def action_export_mermaid_erd() -> None:
    """Compiles the live schema into Mermaid.js erDiagram syntax and writes erd_blueprint.md."""
    try:
        with console.status(
            f"[bold {EMERALD_BRIGHT}]Compiling Mermaid.js ERD blueprint...[/]",
            spinner="dots",
        ):
            tables = introspect_public_schema()
    except psycopg2.OperationalError as exc:
        render_error_card("PostgreSQL Connection Failed", exc)
        if Confirm.ask(
            f"\n[bold {EMERALD_BRIGHT}]Export Preview Sandbox ERD blueprint to erd_blueprint.md instead?[/]",
            default=True,
        ):
            tables = FALLBACK_SCHEMA_TABLES
        else:
            return
    except psycopg2.Error as exc:
        render_error_card("Database Query Error", exc)
        return

    if not tables:
        console.print(
            Panel(
                f"[bold {GOLD_PK}]No public tables found to export.[/]",
                border_style=GOLD_PK,
                box=box.SQUARE,
            )
        )
        return

    mermaid_code = compile_mermaid_erd(tables)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    markdown_content = (
        f"# STRUCTURA FORGE — PostgreSQL Entity-Relationship Blueprint\n\n"
        f"- **Generated At:** `{timestamp}`\n"
        f"- **Source Instance:** `{parse_dsn_summary(get_database_url())}`\n"
        f"- **Tables Mapped:** `{len(tables)}`\n\n"
        f"```mermaid\n"
        f"{mermaid_code}\n"
        f"```\n"
    )

    ERD_EXPORT_PATH.write_text(markdown_content, encoding="utf-8")

    msg = Text()
    msg.append("[OK] Mermaid ERD Blueprint Exported Successfully!\n\n", style=f"bold {EMERALD_BRIGHT}")
    msg.append("Output File : ", style=f"bold {MUTED_TEXT}")
    msg.append(f"{ERD_EXPORT_PATH}\n", style="bold white")
    msg.append("Tables      : ", style=f"bold {MUTED_TEXT}")
    msg.append(f"{len(tables)} entities mapped\n\n", style=f"bold {EMERALD}")
    msg.append("[TIP] Preview in VS Code:\n", style=f"bold {GOLD_PK}")
    msg.append(
        "   Open erd_blueprint.md in VS Code and press Ctrl+Shift+V (or Cmd+Shift+V) to render the interactive ERD diagram.",
        style="white",
    )

    console.print()
    console.print(
        Panel(
            msg,
            title=f"[bold {EMERALD_BRIGHT}][ MERMAID ERD COMPILER ][/]",
            border_style=EMERALD,
            box=box.SQUARE,
            padding=(1, 2),
        )
    )


# =====================================================================
# OPTION [3]: HIGH-VELOCITY CONSTRAINT-COMPLIANT SEEDER
# =====================================================================
def is_auto_generated_column(col: Dict[str, Any]) -> bool:
    """Detects SERIAL, BIGSERIAL, IDENTITY, or nextval() sequence columns."""
    col_default = (col.get("column_default") or "").lower()
    data_type = (col.get("data_type") or "").lower()
    if "nextval(" in col_default:
        return True
    if col.get("is_identity"):
        return True
    if data_type in ("serial", "bigserial", "smallserial"):
        return True
    return False


def generate_synthetic_value(col: Dict[str, Any], row_idx: int) -> Any:
    """Context-aware Faker value generator matching PostgreSQL column constraints."""
    col_name = (col.get("name") or "").lower()
    data_type = (col.get("data_type") or "").lower()
    char_max_len = col.get("char_max_len")
    num_precision = col.get("numeric_precision")
    num_scale = col.get("numeric_scale")
    is_pk = col.get("is_pk", False)
    is_unique = col.get("is_unique", False)

    # Nullable non-PK, non-UNIQUE columns get a 10% chance of NULL
    if col.get("is_nullable") and not is_pk and not is_unique and random.random() < 0.10:
        return None

    def clamp_str(val: str) -> str:
        if char_max_len and char_max_len > 0:
            return val[:char_max_len]
        return val

    if "uuid" in data_type:
        return str(uuid.uuid4())

    if data_type in ("boolean", "bool"):
        return fake.boolean(chance_of_getting_true=75)

    if data_type in ("smallint", "int2", "integer", "int4", "bigint", "int8"):
        if is_pk or is_unique:
            return row_idx
        if "qty" in col_name or "quantity" in col_name or "stock" in col_name:
            return random.randint(1, 250)
        if "age" in col_name:
            return random.randint(18, 80)
        if data_type in ("smallint", "int2"):
            return random.randint(1, 1000)
        return random.randint(1, 50000)

    if data_type in ("numeric", "decimal", "real", "float4", "double precision", "float8", "money"):
        scale = int(num_scale) if num_scale is not None else 2
        precision = int(num_precision) if num_precision is not None else 10
        max_whole_digits = max(1, precision - scale)
        upper_bound = min(9999.99, (10 ** max_whole_digits) - 1)
        return round(random.uniform(1.50, max(2.0, upper_bound)), max(0, scale))

    if data_type == "date":
        return fake.date_between(start_date="-2y", end_date="today")
    if "timestamp" in data_type:
        return fake.date_time_between(start_date="-1y", end_date="now")
    if "time" in data_type:
        return fake.time()

    if data_type in ("json", "jsonb"):
        return json.dumps(
            {
                "event": fake.word(),
                "source": "structura_tui",
                "ip": fake.ipv4(),
                "ok": True,
            }
        )

    # String & VARCHAR context heuristics
    if "email" in col_name:
        return clamp_str(f"user{row_idx}_{uuid.uuid4().hex[:6]}@{fake.free_email_domain()}")
    if is_pk or is_unique:
        return clamp_str(f"{col_name}_{row_idx}_{uuid.uuid4().hex[:6]}")
    if "first_name" in col_name:
        return clamp_str(fake.first_name())
    if "last_name" in col_name:
        return clamp_str(fake.last_name())
    if "full_name" in col_name or col_name in ("name", "username", "author"):
        return clamp_str(fake.name())
    if "phone" in col_name or "mobile" in col_name:
        return clamp_str(fake.phone_number())
    if "address" in col_name or "street" in col_name:
        return clamp_str(fake.street_address())
    if "city" in col_name:
        return clamp_str(fake.city())
    if "country" in col_name:
        return clamp_str(fake.country())
    if "company" in col_name:
        return clamp_str(fake.company())
    if "product" in col_name or "title" in col_name:
        return clamp_str(f"{fake.catch_phrase()} {random.randint(10, 999)}")
    if "status" in col_name or "state" in col_name:
        return clamp_str(random.choice(["ACTIVE", "PENDING", "COMPLETED", "ARCHIVED"]))
    if "url" in col_name or "link" in col_name:
        return clamp_str(fake.url())
    if char_max_len and char_max_len <= 16:
        return clamp_str(fake.lexify(text="?" * min(char_max_len, 8)).upper())

    return clamp_str(fake.sentence(nb_words=5))


def action_seed_table_data() -> None:
    """Interactive prompt to seed a target PostgreSQL table with a Rich Progress bar."""
    is_sandbox_sim = False
    try:
        tables = introspect_public_schema()
    except psycopg2.OperationalError as exc:
        render_error_card("PostgreSQL Connection Failed", exc)
        if Confirm.ask(
            f"\n[bold {EMERALD_BRIGHT}]Run Seeder in Preview Sandbox mode (simulated Faker + Progress bar) instead?[/]",
            default=True,
        ):
            tables = FALLBACK_SCHEMA_TABLES
            is_sandbox_sim = True
        else:
            return
    except psycopg2.Error as exc:
        render_error_card("Database Query Error", exc)
        return

    if not tables:
        console.print(
            Panel(
                f"[bold {GOLD_PK}]No tables available in the 'public' schema to seed.[/]",
                border_style=GOLD_PK,
                box=box.SQUARE,
            )
        )
        return

    # Display table summary list
    tbl_grid = Table(
        title=f"[bold {EMERALD_BRIGHT}]Available Target Tables[/]",
        box=box.SIMPLE_HEAVY,
        border_style=EMERALD_DEEP,
        header_style=f"bold {EMERALD_BRIGHT}",
    )
    tbl_grid.add_column("#", style=f"bold {EMERALD}", justify="right")
    tbl_grid.add_column("Table Name", style="bold white")
    tbl_grid.add_column("Current Rows", style=f"bold {EMERALD_BRIGHT}", justify="right")
    tbl_grid.add_column("Foreign Keys", style=MUTED_TEXT)

    for idx, t in enumerate(tables, start=1):
        fks = [
            f"{c['name']} -> {c['foreign_table']}"
            for c in t["columns"]
            if c["is_fk"] and c["foreign_table"]
        ]
        fk_str = ", ".join(fks) if fks else "None (Root Table)"
        tbl_grid.add_row(str(idx), t["table_name"], f"{t['row_count']:,}", fk_str)

    console.print()
    console.print(tbl_grid)

    choice = Prompt.ask(
        f"\n[bold {EMERALD_BRIGHT}]Enter Target Table Name or Number (1-{len(tables)})[/]",
        default="1",
    ).strip()

    selected_table: Optional[Dict[str, Any]] = None
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(tables):
            selected_table = tables[idx]
    else:
        for t in tables:
            if t["table_name"].lower() == choice.lower():
                selected_table = t
                break

    if not selected_table:
        console.print(f"[bold {ERROR_RED}][X] Invalid table selection: '{choice}'.[/]")
        return

    table_name = selected_table["table_name"]

    row_count = IntPrompt.ask(
        f"[bold {EMERALD_BRIGHT}]How many synthetic rows to inject into '{table_name}'?[/]",
        default=1000,
    )
    row_count = max(1, min(100000, row_count))

    batch_size = IntPrompt.ask(
        f"[bold {EMERALD_BRIGHT}]Transaction batch page size (execute_batch)[/]",
        default=1000,
    )
    batch_size = max(50, min(10000, batch_size))

    if is_sandbox_sim:
        insertable_cols = [
            c for c in selected_table["columns"] if not is_auto_generated_column(c)
        ]
        start_t = time.perf_counter()
        console.print()
        with Progress(
            SpinnerColumn(style=f"bold {EMERALD_BRIGHT}"),
            TextColumn("[bold white]{task.description}"),
            BarColumn(
                bar_width=42,
                style="#141d18",
                complete_style=f"bold {EMERALD}",
                finished_style=f"bold {EMERALD_BRIGHT}",
            ),
            MofNCompleteColumn(),
            TextColumn(f"[bold {EMERALD_BRIGHT}]{{task.percentage:>3.0f}}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task_id = progress.add_task(
                f"Seeding [bold {EMERALD_BRIGHT}]{table_name}[/] (Preview Sandbox)...",
                total=row_count,
            )
            remaining = row_count
            current_idx = 1
            while remaining > 0:
                chunk_len = min(batch_size, remaining)
                for _ in range(chunk_len):
                    _ = [
                        generate_synthetic_value(col, current_idx)
                        for col in insertable_cols
                    ]
                    current_idx += 1
                time.sleep(0.02)
                remaining -= chunk_len
                progress.update(task_id, advance=chunk_len)

        selected_table["row_count"] = selected_table.get("row_count", 0) + row_count
        elapsed_ms = round((time.perf_counter() - start_t) * 1000, 2)
        rows_per_sec = int(row_count / max(0.001, elapsed_ms / 1000.0))

        summary = Text()
        summary.append("[OK] Preview Sandbox Batch Simulation Complete\n\n", style=f"bold {EMERALD_BRIGHT}")
        summary.append("Target Table    : ", style=f"bold {MUTED_TEXT}")
        summary.append(f"{table_name}\n", style="bold white")
        summary.append("Rows Generated  : ", style=f"bold {MUTED_TEXT}")
        summary.append(f"+{row_count:,} rows\n", style=f"bold {EMERALD_BRIGHT}")
        summary.append("Execution Time  : ", style=f"bold {MUTED_TEXT}")
        summary.append(f"{elapsed_ms:,.2f} ms (simulated)\n", style="bold white")
        summary.append("Throughput      : ", style=f"bold {MUTED_TEXT}")
        summary.append(f"~{rows_per_sec:,} rows/sec (page_size={batch_size})", style=f"bold {EMERALD}")

        console.print()
        console.print(
            Panel(
                summary,
                title=f"[bold {EMERALD_BRIGHT}][ HIGH-VELOCITY SEEDER TELEMETRY ][/]",
                border_style=EMERALD,
                box=box.SQUARE,
                padding=(1, 2),
            )
        )
        return

    # Connect & resolve parent foreign keys in memory (with safe sql.Identifier quoting)
    try:
        conn = psycopg2.connect(get_database_url(), connect_timeout=3)
    except psycopg2.OperationalError as exc:
        render_error_card("PostgreSQL Connection Failed", exc)
        return

    try:
        with conn.cursor() as cur:
            fk_pools: Dict[str, List[Any]] = {}
            for col in selected_table["columns"]:
                if col["is_fk"] and col["foreign_table"] and col["foreign_column"]:
                    parent_tbl = col["foreign_table"]
                    parent_col = col["foreign_column"]
                    cur.execute(
                        sql.SQL(
                            "SELECT {col} FROM {tbl} WHERE {col} IS NOT NULL ORDER BY RANDOM() LIMIT 500;"
                        ).format(
                            col=sql.Identifier(parent_col),
                            tbl=sql.Identifier(parent_tbl),
                        )
                    )
                    parent_ids = [r[0] for r in cur.fetchall()]
                    if not parent_ids and parent_tbl != table_name and not col["is_nullable"]:
                        render_error_card(
                            "Foreign Key Pre-Flight Violation Prevented",
                            Exception(
                                f"Parent table '{parent_tbl}' contains 0 rows. Cannot satisfy NOT NULL foreign key '{table_name}.{col['name']}'."
                            ),
                            hint=f"Seed parent table '{parent_tbl}' first before seeding '{table_name}'.",
                        )
                        return
                    fk_pools[col["name"]] = parent_ids

            insertable_cols = [
                c for c in selected_table["columns"] if not is_auto_generated_column(c)
            ]
            if not insertable_cols:
                console.print(
                    f"[bold {GOLD_PK}]Table '{table_name}' only contains auto-generated sequence columns.[/]"
                )
                return

            # Determine safe starting offset for non-serial integer PK/Unique columns
            pk_start_offset = 1
            for col in insertable_cols:
                if (col["is_pk"] or col.get("is_unique")) and col["data_type"].lower() in (
                    "smallint",
                    "int2",
                    "integer",
                    "int4",
                    "bigint",
                    "int8",
                ):
                    cur.execute(
                        sql.SQL("SELECT COALESCE(MAX({col}), 0) FROM {tbl};").format(
                            col=sql.Identifier(col["name"]),
                            tbl=sql.Identifier(table_name),
                        )
                    )
                    pk_start_offset = max(pk_start_offset, int(cur.fetchone()[0]) + 1)

            insert_sql = sql.SQL("INSERT INTO {tbl} ({cols}) VALUES ({vals})").format(
                tbl=sql.Identifier(table_name),
                cols=sql.SQL(", ").join(sql.Identifier(c["name"]) for c in insertable_cols),
                vals=sql.SQL(", ").join(sql.Placeholder() for _ in insertable_cols),
            )

            start_t = time.perf_counter()

            console.print()
            with Progress(
                SpinnerColumn(style=f"bold {EMERALD_BRIGHT}"),
                TextColumn("[bold white]{task.description}"),
                BarColumn(
                    bar_width=42,
                    style="#141d18",
                    complete_style=f"bold {EMERALD}",
                    finished_style=f"bold {EMERALD_BRIGHT}",
                ),
                MofNCompleteColumn(),
                TextColumn(f"[bold {EMERALD_BRIGHT}]{{task.percentage:>3.0f}}%"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task_id = progress.add_task(
                    f"Seeding [bold {EMERALD_BRIGHT}]{table_name}[/]...",
                    total=row_count,
                )

                remaining = row_count
                current_idx = pk_start_offset

                while remaining > 0:
                    chunk_len = min(batch_size, remaining)
                    batch_records: List[Tuple[Any, ...]] = []

                    for _ in range(chunk_len):
                        row_vals: List[Any] = []
                        for col in insertable_cols:
                            c_name = col["name"]
                            if col["is_fk"]:
                                pool_ids = fk_pools.get(c_name, [])
                                if pool_ids:
                                    if col["is_nullable"] and random.random() < 0.12:
                                        row_vals.append(None)
                                    else:
                                        row_vals.append(random.choice(pool_ids))
                                else:
                                    row_vals.append(None)
                            else:
                                row_vals.append(generate_synthetic_value(col, current_idx))
                        batch_records.append(tuple(row_vals))
                        current_idx += 1

                    extras.execute_batch(cur, insert_sql, batch_records, page_size=chunk_len)
                    remaining -= chunk_len
                    progress.update(task_id, advance=chunk_len)

            conn.commit()
            elapsed_ms = round((time.perf_counter() - start_t) * 1000, 2)
            rows_per_sec = int(row_count / max(0.001, elapsed_ms / 1000.0))

            summary = Text()
            summary.append("[OK] Atomic Batch Transaction Committed\n\n", style=f"bold {EMERALD_BRIGHT}")
            summary.append("Target Table    : ", style=f"bold {MUTED_TEXT}")
            summary.append(f"{table_name}\n", style="bold white")
            summary.append("Rows Inserted   : ", style=f"bold {MUTED_TEXT}")
            summary.append(f"+{row_count:,} rows\n", style=f"bold {EMERALD_BRIGHT}")
            summary.append("Execution Time  : ", style=f"bold {MUTED_TEXT}")
            summary.append(f"{elapsed_ms:,.2f} ms\n", style="bold white")
            summary.append("Throughput      : ", style=f"bold {MUTED_TEXT}")
            summary.append(f"~{rows_per_sec:,} rows/sec (page_size={batch_size})", style=f"bold {EMERALD}")

            console.print()
            console.print(
                Panel(
                    summary,
                    title=f"[bold {EMERALD_BRIGHT}][ HIGH-VELOCITY SEEDER TELEMETRY ][/]",
                    border_style=EMERALD,
                    box=box.SQUARE,
                    padding=(1, 2),
                )
            )

    except psycopg2.Error as exc:
        conn.rollback()
        render_error_card("Transaction Rolled Back (Constraint / SQL Error)", exc)
    finally:
        conn.close()


# =====================================================================
# OPTION [4] & --web: LAUNCH WEB DASHBOARD
# =====================================================================
def is_port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def launch_web_server(open_browser: bool = True, reload_mode: bool = True) -> None:
    """Launches the FastAPI Web Studio via Uvicorn and opens http://localhost:8000."""
    url = "http://localhost:8000"

    if is_port_in_use("127.0.0.1", 8000):
        console.print(
            Panel(
                f"[bold {EMERALD_BRIGHT}][OK] Structura Forge Web Server is already running on {url}[/]\n"
                f"[{MUTED_TEXT}]Opening {url} in your default browser...[/]",
                title=f"[bold {EMERALD_BRIGHT}][ WEB STUDIO ACTIVE ][/]",
                border_style=EMERALD,
                box=box.SQUARE,
            )
        )
        if open_browser:
            webbrowser.open(url)
        return

    console.print(
        Panel(
            f"[bold {EMERALD_BRIGHT}][>>] Starting Structura Forge FastAPI Backend & Web Dashboard...[/]\n"
            f"[bold white]URL      :[/] [underline {EMERALD_BRIGHT}]{url}[/]\n"
            f"[bold white]Command  :[/] [{MUTED_TEXT}]uvicorn backend.main:app --host 127.0.0.1 --port 8000{' --reload' if reload_mode else ''}[/]\n"
            f"[{MUTED_TEXT}]Press Ctrl+C to stop the web server and return.[/]",
            title=f"[bold {EMERALD_BRIGHT}][ STRUCTURA FORGE WEB STUDIO ][/]",
            border_style=EMERALD,
            box=box.SQUARE,
        )
    )

    if open_browser:
        webbrowser.open(url)

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]
    if reload_mode:
        cmd.append("--reload")

    try:
        subprocess.run(cmd, cwd=str(BASE_DIR), check=False)
    except KeyboardInterrupt:
        console.print(f"\n[bold {EMERALD}]Web server stopped.[/]")


# =====================================================================
# INTERACTIVE TUI MENU LOOP
# =====================================================================
def render_main_menu() -> str:
    """Renders the Obsidian & Emerald interactive menu options (1–5)."""
    menu_table = Table.grid(padding=(0, 2))
    menu_table.add_column(style=f"bold {EMERALD_BRIGHT}", justify="right")
    menu_table.add_column(style="bold white")
    menu_table.add_column(style=MUTED_TEXT)

    menu_table.add_row(
        "[1]",
        "View Schema Tree",
        "Introspect public tables, PKs (Gold) & FKs (Emerald)",
    )
    menu_table.add_row(
        "[2]",
        "Export Mermaid ERD",
        "Compile schema to erd_blueprint.md for VS Code preview",
    )
    menu_table.add_row(
        "[3]",
        "Seed Table Data",
        "High-velocity Faker + execute_batch streaming with progress bar",
    )
    menu_table.add_row(
        "[4]",
        "Launch Web Dashboard",
        "Start FastAPI server & open http://localhost:8000",
    )
    menu_table.add_row(
        "[5]",
        "Exit",
        "Close Structura TUI",
    )
    menu_table.add_row(
        "[6]",
        "Configure DB & Test Schema",
        "Update .env credentials or provision backend/test_schema.sql",
    )

    console.print()
    console.print(
        Panel(
            menu_table,
            title=f"[bold {EMERALD_BRIGHT}][ CONTROL DECK ][/]",
            border_style=f"{EMERALD}",
            style=f"on {EMERALD_DARK_BG}",
            box=box.SQUARE,
            padding=(1, 2),
        )
    )

    return Prompt.ask(
        f"[bold {EMERALD_BRIGHT}]Select an operation[/]",
        choices=["1", "2", "3", "4", "5", "6"],
        default="1",
    )


def run_tui() -> None:
    """Main interactive TUI entrypoint."""
    render_banner()

    while True:
        try:
            choice = render_main_menu()
            if choice == "1":
                action_view_schema_tree()
            elif choice == "2":
                action_export_mermaid_erd()
            elif choice == "3":
                action_seed_table_data()
            elif choice == "4":
                launch_web_server(open_browser=True, reload_mode=True)
            elif choice == "5":
                console.print(
                    f"\n[bold {EMERALD_BRIGHT}][STRUCTURA FORGE] Thank you for using Structura Forge. Goodbye![/]\n"
                )
                break
            elif choice == "6":
                configure_env_interactive()
        except KeyboardInterrupt:
            console.print(
                f"\n\n[bold {EMERALD_BRIGHT}][STRUCTURA FORGE] Interrupted — exiting Structura Forge cleanly.[/]\n"
            )
            break


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="structura",
        description="STRUCTURA FORGE - PostgreSQL Architecture Mapping & High-Velocity Seeder",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch the FastAPI backend & Web Dashboard (uvicorn backend.main:app --reload)",
    )
    args = parser.parse_args()

    if args.web:
        render_banner()
        launch_web_server(open_browser=True, reload_mode=True)
    else:
        run_tui()


if __name__ == "__main__":
    main()
