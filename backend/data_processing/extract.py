# data_processing/extract.py
import requests
from time import sleep
from constants import (
    POKEAPI_BASE_URL,
    POKEMON_ENDPOINT,
    API_DELAY,
)

def extract_pokemons(pokemon_id):
    """Fetch Pokémon data including evolution chain from PokeAPI without logging."""
    
    # Input validation
    if not isinstance(pokemon_id, int) or pokemon_id <= 0:
        return None

    url = f"{POKEAPI_BASE_URL}/{POKEMON_ENDPOINT}/{pokemon_id}/"
    
    # Step 1: Fetch main Pokémon data
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    try:
        data = response.json()
    except ValueError:
        return None
    
    # Apply API delay after successful fetch of main data
    sleep(API_DELAY)

    # Step 2: Fetch species data
    species_url = data.get("species", {}).get("url")
    if not species_url:
        return None

    try:
        species_response = requests.get(species_url, timeout=10)
        species_response.raise_for_status()
        species_data = species_response.json()
    except requests.exceptions.RequestException:
        return None
    except ValueError:
        return None
    
    # Apply API delay after successful fetch of species data
    sleep(API_DELAY)

    # Step 3: Fetch evolution chain
    evolution_chain_url = species_data.get("evolution_chain", {}).get("url")
    if not evolution_chain_url:
        return None

    try:
        evolution_response = requests.get(evolution_chain_url, timeout=10)
        evolution_response.raise_for_status()
        evolution_data = evolution_response.json()
    except requests.exceptions.RequestException:
        return None
    except ValueError:
        return None

    # Helper: Recursively extract evolution names
    def extract_evolution_names(chain):
        names = [chain["species"]["name"]]
        for evolution in chain.get("evolves_to", []):
            names.extend(extract_evolution_names(evolution))
        return names

    try:
        evolution_chain = extract_evolution_names(evolution_data["chain"])
    except Exception:
        evolution_chain = []

    # Determine if evolved
    is_evolved = evolution_chain and evolution_chain[0] != data["name"]

    # Build final Pokémon dict
    pokemon = {
        "name": data["name"],
        "id": data["id"],
        "types": [t["type"]["name"] for t in data["types"]],
        "abilities": [a["ability"]["name"] for a in data["abilities"]],
        "moves": [m["move"]["name"] for m in data["moves"]],
        "stats": {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
        "evolution_chain": evolution_chain,
        "is_evolved": is_evolved
    }

    return pokemon
