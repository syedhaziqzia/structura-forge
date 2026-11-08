# MODULE 04: SEEDER ENGINE SPECIFICATION (`04_SEEDER_ENGINE_SPEC.md`)

## 1. Postgres-to-Faker Type Mapping

| PostgreSQL Data Type | Generator Strategy | Logic & Sanitization |
| --- | --- | --- |
| `uuid` | `uuid.uuid4()` | Converted to standard string |
| `varchar`, `text` (email in name) | `faker.email()` | Context-aware regex check on column name |
| `varchar`, `text` (name in name) | `faker.name()` | Sliced to `character_maximum_length` if set |
| `varchar`, `text` (generic) | `faker.sentence(nb_words=4)` | Sliced to column max length |
| `integer`, `int4`, `smallint` | `faker.random_int(1, 10000)` | Numerical integer range |
| `bigint`, `int8` | `faker.random_int(10000, 9999999)` | 64-bit safe bounds |
| `boolean` | `faker.boolean(chance_of_getting_true=50)` | Native boolean |
| `date` | `faker.date_between('-2y', 'today')` | Standard ISO date string |
| `timestamp`, `timestamptz` | `faker.date_time_between('-1y')` | Native datetime object |
| `numeric`, `decimal` | `round(faker.pyfloat(10, 5000), 2)` | Precision matched to numeric schema |

## 2. Foreign Key Integrity Protocol

1. **Pre-Flight Lookup:** When seeding a table with foreign keys, query the parent table:
```sql
SELECT {foreign_column} FROM {foreign_table} ORDER BY RANDOM() LIMIT 500;
```

2. **Zero-Parent Abort:** If the parent table has 0 rows, abort with HTTP 400:
`"Cannot seed child table '{table_name}': Parent table '{foreign_table}' contains no rows."`
3. **In-Memory Sampling:** Loaded parent IDs are cached in an in-memory list. Child rows sample from this list randomly to maintain 100% referential integrity.
4. **Serial PK Handling:** Columns marked as `SERIAL`, `BIGSERIAL`, or containing `nextval(...)` are omitted from the insert payload so Postgres handles sequences natively.

