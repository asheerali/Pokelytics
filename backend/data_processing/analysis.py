import sqlite3
from typing import Dict, List, Any
from collections import Counter


def get_pokemon_stats_average(conn) -> Dict[str, float]:
    """
    Calculate average stats across all Pokémon for the radar chart.
    Returns dict with stat names and their average values.
    """
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        query = """
            SELECT stat_name, AVG(base_stat) as avg_stat
            FROM pokemon_stats
            GROUP BY stat_name
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        stats = {row[0]: round(row[1], 2) for row in results}
        cursor.close()
        return stats
    except Exception:
        return {}


def get_type_distribution(conn) -> Dict[str, int]:
    """
    Get the count of Pokémon for each type for the pie chart.
    Returns dict with type names and their counts.
    """
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        query = """
            SELECT type_name, COUNT(DISTINCT pokemon_id) as count
            FROM pokemon_types
            GROUP BY type_name
            ORDER BY count DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        distribution = {row[0]: row[1] for row in results}
        cursor.close()
        return distribution
    except Exception:
        return {}


def get_abilities_frequency(conn, top_n: int = 10) -> Dict[str, int]:
    """
    Get the most common abilities and their frequency for bar chart.
    Returns dict with ability names and their counts.
    """
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        query = """
            SELECT ability_name, COUNT(DISTINCT pokemon_id) as count
            FROM pokemon_abilities
            GROUP BY ability_name
            ORDER BY count DESC
            LIMIT ?
        """
        cursor.execute(query, (top_n,))
        results = cursor.fetchall()
        
        abilities = {row[0]: row[1] for row in results}
        cursor.close()
        return abilities
    except Exception:
        return {}


def get_moves_frequency(conn, top_n: int = 15) -> Dict[str, int]:
    """
    Get the most common moves and their frequency for bar chart.
    Returns dict with move names and their counts.
    """
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        query = """
            SELECT move_name, COUNT(DISTINCT pokemon_id) as count
            FROM pokemon_moves
            GROUP BY move_name
            ORDER BY count DESC
            LIMIT ?
        """
        cursor.execute(query, (top_n,))
        results = cursor.fetchall()
        
        moves = {row[0]: row[1] for row in results}
        cursor.close()
        return moves
    except Exception:
        return {}


def get_evolution_stage_distribution(conn) -> Dict[str, int]:
    """
    Get the count of evolved vs non-evolved Pokémon for pie/bar chart.
    Returns dict with evolution status and their counts.
    """
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                CASE WHEN is_evolved = 1 THEN 'Evolved' ELSE 'Not Evolved' END as status,
                COUNT(*) as count
            FROM pokemon
            GROUP BY is_evolved
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        distribution = {row[0]: row[1] for row in results}
        cursor.close()
        return distribution
    except Exception:
        return {}


def get_type_combination_distribution(conn) -> Dict[str, int]:
    """
    Get the count of single-type vs dual-type Pokémon for bar chart.
    Returns dict with type combination counts.
    """
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                CASE 
                    WHEN type_count = 1 THEN 'Single Type'
                    WHEN type_count = 2 THEN 'Dual Type'
                    ELSE 'Multi Type'
                END as combination,
                COUNT(*) as count
            FROM (
                SELECT pokemon_id, COUNT(*) as type_count
                FROM pokemon_types
                GROUP BY pokemon_id
            )
            GROUP BY combination
            ORDER BY count DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        distribution = {row[0]: row[1] for row in results}
        cursor.close()
        return distribution
    except Exception:
        return {}


def generate_all_analysis(conn) -> Dict[str, Any]:
    """
    Generate all analysis data for the dashboard.
    Returns a dictionary with all 6 graph data.
    """
    if not conn:
        return {}
    
    analysis_data = {
        "pokemon_stats": {
            "data": get_pokemon_stats_average(conn),
            "title": "Average Pokémon Stats",
            "type": "radar"
        },
        "type_distribution": {
            "data": get_type_distribution(conn),
            "title": "Type Distribution",
            "type": "pie"
        },
        "abilities_frequency": {
            "data": get_abilities_frequency(conn, top_n=10),
            "title": "Top 10 Most Common Abilities",
            "type": "bar"
        },
        "moves_frequency": {
            "data": get_moves_frequency(conn, top_n=15),
            "title": "Top 15 Most Common Moves",
            "type": "bar"
        },
        "evolution_distribution": {
            "data": get_evolution_stage_distribution(conn),
            "title": "Evolution Stage Distribution",
            "type": "pie"
        },
        "type_combination": {
            "data": get_type_combination_distribution(conn),
            "title": "Type Combination Distribution",
            "type": "bar"
        }
    }
    
    return analysis_data