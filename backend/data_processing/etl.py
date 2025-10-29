# data_processing/etl.py
import sqlite3
from time import sleep
import logging

from data_processing.extract import extract_pokemons
from data_processing.transform import transform_pokemons
from data_processing.load import create_connection, create_tables, load_pokemons

from constants import (
    DATABASE_FILE,
    POKEMON_TO_FETCH,
    API_DELAY,
    LOG_FORMAT,
    LOG_LEVEL,
)

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)


def run_etl_pipeline():
    """Run the full ETL pipeline: Extract → Transform → Load."""
    
    conn = None
    success_count = 0
    failure_count = 0

    try:
        # === 1. Database Setup ===
        logging.info("Starting ETL pipeline setup...")
        conn = create_connection(DATABASE_FILE)
        if not conn:
            logging.critical("Failed to connect to database.")
            raise Exception("Failed to connect to database.")

        if not create_tables(conn):
            logging.warning("Some tables failed to create. Continuing anyway...")

        logging.info(f"Starting ETL for first {POKEMON_TO_FETCH} Pokémon")

        # === 2. Main ETL Loop ===
        for i in range(1, POKEMON_TO_FETCH + 1):
            pokemon_name = f"ID:{i}"
            
            # Console status every 50 Pokémon
            if i % 50 == 0:
                print(f"Processing ID: {i}...")

            try:
                # --- EXTRACT ---
                logging.debug(f"Extracting Pokémon ID: {i}")
                raw_data = extract_pokemons(i)

                if not raw_data:
                    logging.warning(f"Failed to extract Pokémon ID: {i}")
                    failure_count += 1
                    continue

                pokemon_name = raw_data["name"].title()

                # --- TRANSFORM ---
                transformed_data = transform_pokemons(raw_data)
                if not transformed_data:
                    logging.warning(f"Failed to transform Pokémon: {pokemon_name}")
                    failure_count += 1
                    continue

                # --- LOAD ---
                if load_pokemons(conn, transformed_data):
                    success_count += 1
                    logging.info(f"✓ Successfully loaded: {pokemon_name}")
                else:
                    failure_count += 1
                    logging.error(f"✗ Failed to load: {pokemon_name}")

            except Exception as e:
                failure_count += 1
                logging.error(f"Unexpected error processing Pokémon ID {i}: {e}")

            # Respect API rate limit
            sleep(API_DELAY)

        # === 3. Summary ===
        total = success_count + failure_count
        logging.info("=" * 50)
        logging.info("ETL PIPELINE COMPLETE")
        logging.info(f"Total Processed      : {total}")
        logging.info(f"Successfully Loaded  : {success_count}")
        logging.info(f"Failed               : {failure_count}")
        logging.info("=" * 50)

    except Exception as e:
        logging.critical(f"CRITICAL ERROR in ETL pipeline: {e}")
        return False
    finally:
        if conn:
            try:
                conn.close()
                logging.info("Database connection closed.")
            except:
                logging.error("Failed to close database connection.")
    
    return success_count > 0


if __name__ == "__main__":
    run_etl_pipeline()