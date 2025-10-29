# data_processing/transform.py

def transform_pokemons(pokemon_data: dict) -> dict | None:
    """
    Transform raw Pokémon API data into a structured format for database loading.
    Returns dict on success, None on validation/transform error.
    """
    # Check for valid input data type
    if not pokemon_data or not isinstance(pokemon_data, dict):
        return None

    try:
        # === 1. Main Pokémon data (Validation) ===
        if "id" not in pokemon_data or "name" not in pokemon_data or "is_evolved" not in pokemon_data:
            return None

        pokemon_main = {
            "id": pokemon_data["id"],
            "name": pokemon_data["name"],
            "is_evolved": bool(pokemon_data["is_evolved"])  # Ensure boolean
        }

        # === 2. Types & Abilities (Handle non-list formats gracefully) ===
        types = pokemon_data.get("types", [])
        if not isinstance(types, list):
            # Convert to list if it's a single value or handle as empty if invalid
            types = [types] if types else []

        abilities = pokemon_data.get("abilities", [])
        if not isinstance(abilities, list):
            # Convert to list if it's a single value or handle as empty if invalid
            abilities = [abilities] if abilities else []

        # === 3. Moves (Handle non-list formats gracefully) ===
        moves = pokemon_data.get("moves", [])
        if not isinstance(moves, list):
            # Convert to list if it's a single value or handle as empty if invalid
            moves = [moves] if moves else []

        # === 4. Stats (Validation) ===
        raw_stats = pokemon_data.get("stats")
        if not isinstance(raw_stats, dict):
            return None

        # Filter out invalid stat values and convert to structured list
        pokemon_stats = [
            {"stat_name": name, "base_stat": int(value)}
            for name, value in raw_stats.items()
            if isinstance(value, (int, float))  # Only process valid numbers
        ]

        # Note: If no valid stats are found, we proceed with an empty list

        # === 5. Evolution Chain (Validation) ===
        evolution_chain = pokemon_data.get("evolution_chain", [])
        if not evolution_chain or not isinstance(evolution_chain, list) or len(evolution_chain) == 0:
            return None

        evolution_chain_identifier = evolution_chain[0]  # First element is the identifier
        evolution_links = [
            {"name": name, "stage": i + 1}  # Stage starts at 1
            for i, name in enumerate(evolution_chain)
            if isinstance(name, str)
        ]

        if len(evolution_links) == 0:
            return None

        # === Build final result ===
        transformed = {
            "main": pokemon_main,
            "types": types,
            "abilities": abilities,
            "moves": moves,
            "stats": pokemon_stats,
            "evolution_chain_identifier": evolution_chain_identifier,
            "evolution_links": evolution_links
        }

        return transformed

    except Exception:
        # Catch unexpected errors during transformation and return None
        return None
    
    
    


