# data_processing/load.py
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """
    Create a connection to SQLite database with error handling.
    """
    if not db_file or not isinstance(db_file, str):
        return None

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error:
        pass
    except Exception:
        pass
    if conn:
        try:
            conn.close()
        except:
            pass
    return None


def create_tables(conn):
    """
    Create all required tables in the SQLite database.
    """
    if not conn:
        return False

    table_definitions = [
        ("pokemon", """
            CREATE TABLE IF NOT EXISTS pokemon (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                is_evolved BOOLEAN NOT NULL
            );
        """),
        ("types", """
            CREATE TABLE IF NOT EXISTS types (
                name TEXT PRIMARY KEY
            );
        """),
        ("abilities", """
            CREATE TABLE IF NOT EXISTS abilities (
                name TEXT PRIMARY KEY
            );
        """),
        ("moves", """
            CREATE TABLE IF NOT EXISTS moves (
                name TEXT PRIMARY KEY
            );
        """),
        ("stats", """
            CREATE TABLE IF NOT EXISTS stats (
                name TEXT PRIMARY KEY
            );
        """),
        ("pokemon_types", """
            CREATE TABLE IF NOT EXISTS pokemon_types (
                pokemon_id INTEGER,
                type_name TEXT,
                PRIMARY KEY (pokemon_id, type_name),
                FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
                FOREIGN KEY (type_name) REFERENCES types (name)
            );
        """),
        ("pokemon_abilities", """
            CREATE TABLE IF NOT EXISTS pokemon_abilities (
                pokemon_id INTEGER,
                ability_name TEXT,
                PRIMARY KEY (pokemon_id, ability_name),
                FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
                FOREIGN KEY (ability_name) REFERENCES abilities (name)
            );
        """),
        ("pokemon_moves", """
            CREATE TABLE IF NOT EXISTS pokemon_moves (
                pokemon_id INTEGER,
                move_name TEXT,
                PRIMARY KEY (pokemon_id, move_name),
                FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
                FOREIGN KEY (move_name) REFERENCES moves (name)
            );
        """),
        ("pokemon_stats", """
            CREATE TABLE IF NOT EXISTS pokemon_stats (
                pokemon_id INTEGER,
                stat_name TEXT,
                base_stat INTEGER NOT NULL,
                PRIMARY KEY (pokemon_id, stat_name),
                FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
                FOREIGN KEY (stat_name) REFERENCES stats (name)
            );
        """)
    ]

    cursor = None
    success_count = 0
    total_tables = len(table_definitions)

    try:
        cursor = conn.cursor()
        for table_name, sql in table_definitions:
            sql = sql.strip()
            try:
                cursor.execute(sql)
                success_count += 1
            except Error:
                pass

        if success_count == total_tables:
            conn.commit()
        else:
            conn.rollback()

        return success_count == total_tables
    except Error:
        try:
            conn.rollback()
        except:
            pass
        return False
    except Exception:
        try:
            conn.rollback()
        except:
            pass
        return False
    finally:
        if cursor:
            cursor.close()


def load_pokemons(conn, transformed_data: dict):
    """
    Load one Pokémon's transformed data into the database.
    Idempotent using INSERT OR IGNORE.
    """
    if not conn:
        return False
    if not transformed_data or "main" not in transformed_data:
        return False

    pokemon_id = transformed_data["main"].get("id")
    cursor = None
    try:
        cursor = conn.cursor()

        # === 1. Insert into Lookup Tables ===
        try:
            types = [(t,) for t in transformed_data.get("types", [])]
            if types:
                cursor.executemany("INSERT OR IGNORE INTO types (name) VALUES (?)", types)

            abilities = [(a,) for a in transformed_data.get("abilities", [])]
            if abilities:
                cursor.executemany("INSERT OR IGNORE INTO abilities (name) VALUES (?)", abilities)

            moves = [(m,) for m in transformed_data.get("moves", [])]
            if moves:
                cursor.executemany("INSERT OR IGNORE INTO moves (name) VALUES (?)", moves)

            stats = [(s["stat_name"],) for s in transformed_data.get("stats", [])]
            if stats:
                cursor.executemany("INSERT OR IGNORE INTO stats (name) VALUES (?)", stats)
        except Error:
            conn.rollback()
            return False

        # === 2. Insert Main Pokémon ===
        try:
            main = transformed_data["main"]
            cursor.execute(
                "INSERT OR IGNORE INTO pokemon (id, name, is_evolved) VALUES (?, ?, ?)",
                (main["id"], main["name"], main["is_evolved"])
            )
        except Error:
            conn.rollback()
            return False

        # === 3. Insert Junction Tables ===
        try:
            type_data = [(pokemon_id, t) for t in transformed_data.get("types", [])]
            if type_data:
                cursor.executemany("INSERT OR IGNORE INTO pokemon_types (pokemon_id, type_name) VALUES (?, ?)", type_data)

            ability_data = [(pokemon_id, a) for a in transformed_data.get("abilities", [])]
            if ability_data:
                cursor.executemany("INSERT OR IGNORE INTO pokemon_abilities (pokemon_id, ability_name) VALUES (?, ?)", ability_data)

            move_data = [(pokemon_id, m) for m in transformed_data.get("moves", [])]
            if move_data:
                cursor.executemany("INSERT OR IGNORE INTO pokemon_moves (pokemon_id, move_name) VALUES (?, ?)", move_data)

            stat_data = [(pokemon_id, s["stat_name"], s["base_stat"]) for s in transformed_data.get("stats", [])]
            if stat_data:
                cursor.executemany("INSERT OR IGNORE INTO pokemon_stats (pokemon_id, stat_name, base_stat) VALUES (?, ?, ?)", stat_data)
        except Error:
            conn.rollback()
            return False

        conn.commit()
        return True
    except Exception:
        try:
            conn.rollback()
        except:
            pass
        return False
    finally:
        if cursor:
            cursor.close()