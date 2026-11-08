# MODULE 02: DATABASE SPECIFICATION (`02_DATABASE_SPEC.md`)

## 1. System Catalog Querying

Structura inspects PostgreSQL metadata using ANSI-compliant `information_schema` and `pg_catalog` queries.

```sql
SELECT 
    c.table_name,
    c.column_name,
    c.data_type,
    c.is_nullable,
    c.character_maximum_length,
    CASE WHEN tc.constraint_type = 'PRIMARY KEY' THEN TRUE ELSE FALSE END AS is_primary_key,
    kcu2.table_name AS foreign_table,
    kcu2.column_name AS foreign_column
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
LEFT JOIN information_schema.key_column_usage kcu2
    ON rc.unique_constraint_name = kcu2.constraint_name
    AND kcu.ordinal_position = kcu2.ordinal_position
WHERE c.table_schema = 'public'
ORDER BY c.table_name, c.ordinal_position;
```

## 2. Mermaid.js ERD Grammar Mapping

The backend iteratively converts the introspected schema dictionary into Mermaid `erDiagram` syntax:

1. **Entity Definition:**
```text
erDiagram
    USERS {
        uuid id PK
        string email
        timestamp created_at
    }
    ORDERS {
        serial order_id PK
        uuid user_id FK
        numeric total_amount
    }
```

2. **Relationship Links:**
* One-to-Many rule: `USERS ||--o{ ORDERS : "references"`
* Self-referencing tables: handled safely without recursive loops.

