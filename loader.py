import os
from pathlib import Path
from urllib.parse import unquote

import pandas as pd
import psycopg
from dotenv import load_dotenv
from psycopg import sql

# Load environment variables
_ = load_dotenv(Path(__file__).resolve().parent / ".env")

PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT", "5432")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = unquote(os.getenv("PGPASSWORD", ""))
PGSSLMODE = os.getenv("PGSSLMODE", "require")

# Admin/maintenance database used to manage other databases
ADMIN_DB = os.getenv("PGADMIN_DATABASE", "postgres")
# Target database to reset and apply schema migrations
TARGET_DB = os.getenv("RAW_DB_NAME", "raw")

# Table mapping: (table_name, parquet_file, primary_key) in exact foreign key order
TABLE_PARQUET_MAPPING = [
    ("fincas", "fincas.parquet", "id_finca"),
    ("variedades_cafe", "variedades.parquet", "id_variedad"),
    ("beneficios", "beneficios.parquet", "id_beneficio"),
    ("cuadrillas_corte", "cuadrillas.parquet", "id_cuadrilla"),
    ("clima_zonas_cafetaleras", "clima.parquet", "fecha"),
    ("lotes_acopio", "lotes.parquet", "id_lote"),
    ("procesamiento_beneficio", "procesamiento.parquet", "id_proceso"),
    ("embarques_exportacion", "embarques.parquet", "id_embarque"),
]


def get_conninfo(dbname: str) -> str:
    """Build a PostgreSQL connection string for a specific database."""
    return (
        f"host={PGHOST} "
        f"port={PGPORT} "
        f"user={PGUSER} "
        f"password={PGPASSWORD} "
        f"dbname={dbname} "
        f"sslmode={PGSSLMODE}"
    )


def reset_database(target_db: str = TARGET_DB, admin_db: str = ADMIN_DB) -> None:
    """Drop target database if it exists, then create a clean one."""
    print(f"Connecting to admin database '{admin_db}' on {PGHOST}...")
    with (
        psycopg.connect(get_conninfo(target_db)) as conn,
        conn.cursor() as cur,
    ):
        for table_name, file_name, pk in TABLE_PARQUET_MAPPING:
            ...
        # Terminate any remaining active connections to the target database
        _ = cur.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s AND pid <> pg_backend_pid();
            """,
            (target_db,),
        )

        print(f"Dropping database '{target_db}' if it exists...")
        _ = cur.execute(
            sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE);").format(
                sql.Identifier(target_db)
            )
        )

        print(f"Creating fresh database '{target_db}'...")
        _ = cur.execute(
            sql.SQL("CREATE DATABASE {};").format(sql.Identifier(target_db))
        )

    print(f"Database '{target_db}' created successfully.\n")


def apply_migrations(
    target_db: str = TARGET_DB, migration_file: Path | None = None
) -> None:
    """Connect to the target database and execute the schema migration directly."""
    target_file = migration_file if migration_file is not None else Path("migrations/01_schema.sql")
    print(f"Connecting to target database '{target_db}'...")
    sql_content = target_file.read_bytes()
    with (
        psycopg.connect(get_conninfo(target_db)) as conn,
        conn.cursor() as cur,
    ):
        print(f"Applying schema migration from '{target_file}'...")
        _ = cur.execute(sql_content)
        conn.commit()
    print(f"Schema migration '{target_file}' applied successfully.\n")


def load_parquet_data(
    target_db: str = TARGET_DB, raw_dir: Path | None = None
) -> None:
    """Load parquet data files into PostgreSQL tables in dependency order using psycopg COPY."""
    data_dir = raw_dir if raw_dir is not None else Path("data/raw")
    print(f"Connecting to target database '{target_db}' to load Parquet data...")

    with psycopg.connect(get_conninfo(target_db)) as conn:
        with conn.cursor() as cur:
            for table_name, file_name, pk in TABLE_PARQUET_MAPPING:
                file_path = data_dir / file_name
                if not file_path.exists():
                    print(f"⚠️ Warning: '{file_path}' not found. Skipping table '{table_name}'.")
                    continue

                df = pd.read_parquet(file_path)

                # Deduplicate by primary key if duplicates exist in source
                initial_count = len(df)
                df = df.drop_duplicates(subset=[pk])
                if len(df) < initial_count:
                    print(f"  [{table_name}] Deduplicated {initial_count - len(df)} redundant rows.")

                # Clean NaNs to None so Postgres receives NULL
                df = df.where(pd.notnull(df), None)

                columns = list(df.columns)
                col_identifiers = ", ".join([f'"{col}"' for col in columns])
                copy_sql = f'COPY "{table_name}" ({col_identifiers}) FROM STDIN'

                print(f"  Streaming {len(df):,} rows into '{table_name}' from {file_name}...")
                with cur.copy(copy_sql) as copy:
                    for row in df.itertuples(index=False, name=None):
                        copy.write_row(row)

                conn.commit()

                cur.execute(sql.SQL("SELECT COUNT(*) FROM {};").format(sql.Identifier(table_name)))
                total_loaded = cur.fetchone()[0]
                print(f"  ✅ '{table_name}' loaded successfully ({total_loaded:,} total rows).\n")

    print("All Parquet datasets loaded into raw database successfully!\n")


if __name__ == "__main__":
    reset_database(TARGET_DB)
    apply_migrations(TARGET_DB, Path("migrations/01_schema.sql"))
    load_parquet_data(TARGET_DB, Path("data/raw"))
