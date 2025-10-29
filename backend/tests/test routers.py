# tests/test_routers.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sqlite3
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

client = TestClient(app)


class TestRootEndpoint:
    """Test suite for root endpoint"""

    def test_root_endpoint(self):
        """Test root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello, FastAPI! AI Agent is ready."}


class TestETLPipelineRouter:
    """Test suite for ETL pipeline router"""

    @patch('routers.etl_pipeline.run_etl_pipeline')
    def test_run_pipeline_endpoint(self, mock_run_etl):
        """Test ETL pipeline endpoint"""
        mock_run_etl.return_value = True
        
        response = client.post("/pokemon/etl/run-pipeline")
        
        assert response.status_code == 200
        assert response.json() == {"detail": "Pipeline completed."}
        mock_run_etl.assert_called_once()

    @patch('routers.etl_pipeline.run_etl_pipeline')
    def test_run_pipeline_endpoint_failure(self, mock_run_etl):
        """Test ETL pipeline endpoint when pipeline fails"""
        mock_run_etl.return_value = False
        
        response = client.post("/pokemon/etl/run-pipeline")
        
        # Endpoint should still return 200 even if pipeline fails
        assert response.status_code == 200
        mock_run_etl.assert_called_once()


class TestPokemonRouter:
    """Test suite for Pokemon router"""

    @patch('routers.pokemon.sqlite3.connect')
    def test_get_pokemon_success(self, mock_connect):
        """Test getting list of all Pokemon"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock fetchall to return Pokemon names
        mock_cursor.fetchall.return_value = [
            {"name": "bulbasaur"},
            {"name": "ivysaur"},
            {"name": "venusaur"}
        ]
        
        response = client.get("/pokemon/")
        
        assert response.status_code == 200
        assert response.json() == ["bulbasaur", "ivysaur", "venusaur"]
        mock_conn.close.assert_called_once()

    @patch('routers.pokemon.sqlite3.connect')
    def test_get_pokemon_database_error(self, mock_connect):
        """Test get Pokemon endpoint with database error"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simulate database error
        mock_cursor.execute.side_effect = Exception("Database error")
        
        response = client.get("/pokemon/")
        
        assert response.status_code == 500
        assert "detail" in response.json()
        mock_conn.close.assert_called_once()

    @patch('routers.pokemon.sqlite3.connect')
    def test_filter_pokemons_no_filters(self, mock_connect):
        """Test filter Pokemon endpoint with no filters"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {"name": "bulbasaur", "hp": 45},
            {"name": "charmander", "hp": 39}
        ]
        
        response = client.get("/pokemon/filter_pokemons")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "bulbasaur"
        assert data[0]["hp"] == 45

    @patch('routers.pokemon.sqlite3.connect')
    def test_filter_pokemons_by_evolution(self, mock_connect):
        """Test filter Pokemon by evolution status"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {"name": "ivysaur", "hp": 60}
        ]
        
        response = client.get("/pokemon/filter_pokemons?is_evolved=true")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "ivysaur"

    @patch('routers.pokemon.sqlite3.connect')
    def test_filter_pokemons_by_hp(self, mock_connect):
        """Test filter Pokemon by minimum HP"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {"name": "snorlax", "hp": 160}
        ]
        
        response = client.get("/pokemon/filter_pokemons?hp_min=100")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["hp"] >= 100

    @patch('routers.pokemon.sqlite3.connect')
    def test_filter_pokemons_by_attack(self, mock_connect):
        """Test filter Pokemon by minimum attack"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {"name": "machamp", "hp": 90}
        ]
        
        response = client.get("/pokemon/filter_pokemons?attack_min=130")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    @patch('routers.pokemon.sqlite3.connect')
    def test_filter_pokemons_by_type(self, mock_connect):
        """Test filter Pokemon by type"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {"name": "charmander", "hp": 39},
            {"name": "charmeleon", "hp": 58}
        ]
        
        response = client.get("/pokemon/filter_pokemons?type_name=fire")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @patch('routers.pokemon.sqlite3.connect')
    def test_filter_pokemons_multiple_filters(self, mock_connect):
        """Test filter Pokemon with multiple filters"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {"name": "charizard", "hp": 78}
        ]
        
        response = client.get(
            "/pokemon/filter_pokemons?is_evolved=true&type_name=fire&hp_min=70"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "charizard"

    @patch('routers.pokemon.sqlite3.connect')
    def test_filter_pokemons_database_error(self, mock_connect):
        """Test filter Pokemon endpoint with database error"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.execute.side_effect = Exception("Database error")
        
        response = client.get("/pokemon/filter_pokemons")
        
        assert response.status_code == 500
        assert "detail" in response.json()


class TestPokemonAnalysisRouter:
    """Test suite for Pokemon analysis router"""

    @patch('routers.pokemon_analysis.generate_all_analysis')
    @patch('routers.pokemon_analysis.create_connection')
    def test_get_analysis_success(self, mock_create_connection, mock_generate_analysis):
        """Test getting all analysis data"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        
        mock_generate_analysis.return_value = {
            "pokemon_stats": {"hp": 50, "attack": 55},
            "type_distribution": {"fire": 10, "water": 15},
            "abilities_frequency": {"overgrow": 5},
            "moves_frequency": {"tackle": 20},
            "evolution_distribution": {"evolved": 30, "not_evolved": 70},
            "type_combination": {"single": 60, "dual": 40}
        }
        
        response = client.get("/pokemon/analysis")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "pokemon_stats" in data["data"]
        mock_conn.close.assert_called_once()

    @patch('routers.pokemon_analysis.create_connection')
    def test_get_analysis_connection_failure(self, mock_create_connection):
        """Test analysis endpoint when database connection fails"""
        mock_create_connection.return_value = None
        
        response = client.get("/pokemon/analysis")
        
        assert response.status_code == 500
        assert "Failed to connect to database" in response.json()["detail"]

    @patch('routers.pokemon_analysis.generate_all_analysis')
    @patch('routers.pokemon_analysis.create_connection')
    def test_get_analysis_generation_failure(
        self,
        mock_create_connection,
        mock_generate_analysis
    ):
        """Test analysis endpoint when analysis generation fails"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_generate_analysis.return_value = None
        
        response = client.get("/pokemon/analysis")
        
        assert response.status_code == 500
        assert "Failed to generate analysis data" in response.json()["detail"]

    @patch('routers.pokemon_analysis.generate_all_analysis')
    @patch('routers.pokemon_analysis.create_connection')
    def test_get_analysis_exception(
        self,
        mock_create_connection,
        mock_generate_analysis
    ):
        """Test analysis endpoint when exception occurs"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_generate_analysis.side_effect = Exception("Unexpected error")
        
        response = client.get("/pokemon/analysis")
        
        assert response.status_code == 500
        assert "Error generating analysis" in response.json()["detail"]

    @patch('routers.pokemon_analysis.get_pokemon_stats_average')
    @patch('routers.pokemon_analysis.create_connection')
    def test_get_specific_analysis_pokemon_stats(
        self,
        mock_create_connection,
        mock_get_stats
    ):
        """Test getting specific graph data - pokemon_stats"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_get_stats.return_value = {"hp": 50, "attack": 55, "defense": 60}
        
        response = client.get("/pokemon/analysis/pokemon_stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["graph_name"] == "pokemon_stats"
        assert data["chart_type"] == "radar"
        assert "hp" in data["data"]

    @patch('routers.pokemon_analysis.get_type_distribution')
    @patch('routers.pokemon_analysis.create_connection')
    def test_get_specific_analysis_type_distribution(
        self,
        mock_create_connection,
        mock_get_type_dist
    ):
        """Test getting specific graph data - type_distribution"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_get_type_dist.return_value = {"fire": 10, "water": 15, "grass": 12}
        
        response = client.get("/pokemon/analysis/type_distribution")
        
        assert response.status_code == 200
        data = response.json()
        assert data["chart_type"] == "pie"
        assert "fire" in data["data"]

    def test_get_specific_analysis_invalid_graph_name(self):
        """Test getting specific graph with invalid name"""
        response = client.get("/pokemon/analysis/invalid_graph")
        
        assert response.status_code == 400
        assert "Invalid graph name" in response.json()["detail"]

    @patch('routers.pokemon_analysis.create_connection')
    def test_get_specific_analysis_connection_failure(self, mock_create_connection):
        """Test specific analysis endpoint when connection fails"""
        mock_create_connection.return_value = None
        
        response = client.get("/pokemon/analysis/pokemon_stats")
        
        assert response.status_code == 500
        assert "Failed to connect to database" in response.json()["detail"]

    @patch('routers.pokemon_analysis.get_abilities_frequency')
    @patch('routers.pokemon_analysis.create_connection')
    def test_get_specific_analysis_abilities(
        self,
        mock_create_connection,
        mock_get_abilities
    ):
        """Test getting abilities frequency data"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_get_abilities.return_value = {"overgrow": 5, "blaze": 8}
        
        response = client.get("/pokemon/analysis/abilities_frequency")
        
        assert response.status_code == 200
        data = response.json()
        assert data["chart_type"] == "bar"

    @patch('routers.pokemon_analysis.get_moves_frequency')
    @patch('routers.pokemon_analysis.create_connection')
    def test_get_specific_analysis_moves(
        self,
        mock_create_connection,
        mock_get_moves
    ):
        """Test getting moves frequency data"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_get_moves.return_value = {"tackle": 20, "scratch": 15}
        
        response = client.get("/pokemon/analysis/moves_frequency")
        
        assert response.status_code == 200
        data = response.json()
        assert data["chart_type"] == "bar"

    @patch('routers.pokemon_analysis.get_evolution_stage_distribution')
    @patch('routers.pokemon_analysis.create_connection')
    def test_get_specific_analysis_evolution(
        self,
        mock_create_connection,
        mock_get_evolution
    ):
        """Test getting evolution distribution data"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_get_evolution.return_value = {"evolved": 40, "not_evolved": 60}
        
        response = client.get("/pokemon/analysis/evolution_distribution")
        
        assert response.status_code == 200
        data = response.json()
        assert data["chart_type"] == "pie"

    @patch('routers.pokemon_analysis.get_type_combination_distribution')
    @patch('routers.pokemon_analysis.create_connection')
    def test_get_specific_analysis_type_combination(
        self,
        mock_create_connection,
        mock_get_type_combo
    ):
        """Test getting type combination data"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_get_type_combo.return_value = {"single": 70, "dual": 30}
        
        response = client.get("/pokemon/analysis/type_combination")
        
        assert response.status_code == 200
        data = response.json()
        assert data["chart_type"] == "bar"


class TestAPIIntegration:
    """Integration tests for API with real database"""

    def test_full_api_flow(self, tmp_path):
        """Integration test for complete API flow"""
        # This test would require setting up a real database
        # For now, we test that the endpoints are accessible
        
        # Test root
        response = client.get("/")
        assert response.status_code == 200
        
        # Test that endpoints exist (they may return errors without DB)
        response = client.get("/pokemon/")
        assert response.status_code in [200, 500]  # Either success or DB error
        
        response = client.get("/pokemon/filter_pokemons")
        assert response.status_code in [200, 500]
        
        response = client.get("/pokemon/analysis")
        assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])