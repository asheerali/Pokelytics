# routers/pokemon_analysis.py

from fastapi import APIRouter, HTTPException
from data_processing.load import create_connection
from data_processing.analysis import generate_all_analysis
from constants import DATABASE_FILE

router = APIRouter(
    prefix="/pokemon",
    tags=["Pokemon-analysis"]
)


@router.get("/analysis")
async def analysis():
    """
    Get comprehensive Pokémon analysis data for dashboard visualizations.
    
    Returns:
        dict: Analysis data including 6 graphs:
            1. pokemon_stats: Average stats across all Pokémon (radar chart)
            2. type_distribution: Count of Pokémon by type (pie chart)
            3. abilities_frequency: Most common abilities (bar chart)
            4. moves_frequency: Most common moves (bar chart)
            5. evolution_distribution: Evolved vs Not Evolved (pie chart)
            6. type_combination: Single-type vs Dual-type Pokémon (bar chart)
    """
    # Connect to database
    conn = create_connection(DATABASE_FILE)
    
    if not conn:
        raise HTTPException(
            status_code=500,
            detail="Failed to connect to database"
        )
    
    try:
        # Generate all analysis
        analysis_data = generate_all_analysis(conn)
        
        if not analysis_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate analysis data"
            )
        
        return {
            "status": "success",
            "data": analysis_data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating analysis: {str(e)}"
        )
    
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


@router.get("/analysis/{graph_name}")
async def get_specific_analysis(graph_name: str):
    """
    Get data for a specific graph.
    
    Args:
        graph_name: Name of the graph 
            (pokemon_stats, type_distribution, abilities_frequency, 
             moves_frequency, evolution_distribution, type_combination)
    
    Returns:
        dict: Data for the requested graph
    """
    valid_graphs = [
        "pokemon_stats",
        "type_distribution",
        "abilities_frequency",
        "moves_frequency",
        "evolution_distribution",
        "type_combination"
    ]
    
    if graph_name not in valid_graphs:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid graph name. Valid options: {', '.join(valid_graphs)}"
        )
    
    conn = create_connection("pokemon.db")
    
    if not conn:
        raise HTTPException(
            status_code=500,
            detail="Failed to connect to database"
        )
    
    try:
        # Import the specific function
        from data_processing.analysis import (
            get_pokemon_stats_average,
            get_type_distribution,
            get_abilities_frequency,
            get_moves_frequency,
            get_evolution_stage_distribution,
            get_type_combination_distribution
        )
        
        # Map graph names to functions
        function_map = {
            "pokemon_stats": get_pokemon_stats_average,
            "type_distribution": get_type_distribution,
            "abilities_frequency": get_abilities_frequency,
            "moves_frequency": get_moves_frequency,
            "evolution_distribution": get_evolution_stage_distribution,
            "type_combination": get_type_combination_distribution
        }
        
        # Get the data
        data = function_map[graph_name](conn)
        
        # Determine chart type
        chart_types = {
            "pokemon_stats": "radar",
            "type_distribution": "pie",
            "abilities_frequency": "bar",
            "moves_frequency": "bar",
            "evolution_distribution": "pie",
            "type_combination": "bar"
        }
        
        return {
            "status": "success",
            "graph_name": graph_name,
            "chart_type": chart_types[graph_name],
            "data": data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating analysis: {str(e)}"
        )
    
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass