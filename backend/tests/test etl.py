# tests/test_etl.py
import pytest
from unittest.mock import patch, Mock, MagicMock
import sqlite3
from data_processing.etl import run_etl_pipeline


class TestETLPipeline:
    """Test suite for ETL pipeline"""

    @patch('data_processing.etl.POKEMON_TO_FETCH', 2)
    @patch('data_processing.etl.sleep')
    @patch('data_processing.etl.load_pokemons')
    @patch('data_processing.etl.transform_pokemons')
    @patch('data_processing.etl.extract_pokemons')
    @patch('data_processing.etl.create_tables')
    @patch('data_processing.etl.create_connection')
    def test_etl_pipeline_success(
        self,
        mock_create_connection,
        mock_create_tables,
        mock_extract,
        mock_transform,
        mock_load,
        mock_sleep
    ):
        """Test successful ETL pipeline execution"""
        # Setup mocks
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_create_tables.return_value = True
        
        # Mock extract returns valid data
        mock_extract.side_effect = [
            {
                "name": "bulbasaur",
                "id": 1,
                "types": ["grass"],
                "abilities": ["overgrow"],
                "moves": ["tackle"],
                "stats": {"hp": 45},
                "evolution_chain": ["bulbasaur"],
                "is_evolved": False
            },
            {
                "name": "ivysaur",
                "id": 2,
                "types": ["grass"],
                "abilities": ["overgrow"],
                "moves": ["tackle"],
                "stats": {"hp": 60},
                "evolution_chain": ["bulbasaur", "ivysaur"],
                "is_evolved": True
            }
        ]
        
        # Mock transform returns valid data
        mock_transform.return_value = {
            "main": {"id": 1, "name": "bulbasaur", "is_evolved": False},
            "types": ["grass"],
            "abilities": ["overgrow"],
            "moves": ["tackle"],
            "stats": [{"stat_name": "hp", "base_stat": 45}]
        }
        
        # Mock load succeeds
        mock_load.return_value = True
        
        # Run pipeline
        result = run_etl_pipeline()
        
        # Assertions
        assert result is True
        assert mock_create_connection.called
        assert mock_create_tables.called
        assert mock_extract.call_count == 2
        assert mock_transform.call_count == 2
        assert mock_load.call_count == 2
        mock_conn.close.assert_called_once()

    @patch('data_processing.etl.create_connection')
    def test_etl_pipeline_database_connection_failure(self, mock_create_connection):
        """Test ETL pipeline when database connection fails"""
        mock_create_connection.return_value = None
        
        result = run_etl_pipeline()
        
        assert result is False

    @patch('data_processing.etl.POKEMON_TO_FETCH', 1)
    @patch('data_processing.etl.sleep')
    @patch('data_processing.etl.extract_pokemons')
    @patch('data_processing.etl.create_tables')
    @patch('data_processing.etl.create_connection')
    def test_etl_pipeline_extract_failure(
        self,
        mock_create_connection,
        mock_create_tables,
        mock_extract,
        mock_sleep
    ):
        """Test ETL pipeline when extraction fails"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_create_tables.return_value = True
        mock_extract.return_value = None  # Extraction fails
        
        result = run_etl_pipeline()
        
        # Pipeline should continue but with 0 successes
        assert result is False
        mock_conn.close.assert_called_once()

    @patch('data_processing.etl.POKEMON_TO_FETCH', 1)
    @patch('data_processing.etl.sleep')
    @patch('data_processing.etl.load_pokemons')
    @patch('data_processing.etl.transform_pokemons')
    @patch('data_processing.etl.extract_pokemons')
    @patch('data_processing.etl.create_tables')
    @patch('data_processing.etl.create_connection')
    def test_etl_pipeline_transform_failure(
        self,
        mock_create_connection,
        mock_create_tables,
        mock_extract,
        mock_transform,
        mock_load,
        mock_sleep
    ):
        """Test ETL pipeline when transformation fails"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_create_tables.return_value = True
        
        mock_extract.return_value = {
            "name": "bulbasaur",
            "id": 1,
            "types": ["grass"],
            "abilities": ["overgrow"],
            "moves": ["tackle"],
            "stats": {"hp": 45},
            "evolution_chain": ["bulbasaur"],
            "is_evolved": False
        }
        
        mock_transform.return_value = None  # Transformation fails
        
        result = run_etl_pipeline()
        
        # Pipeline should continue but with 0 successes
        assert result is False
        assert mock_load.call_count == 0  # Load should not be called
        mock_conn.close.assert_called_once()

    @patch('data_processing.etl.POKEMON_TO_FETCH', 1)
    @patch('data_processing.etl.sleep')
    @patch('data_processing.etl.load_pokemons')
    @patch('data_processing.etl.transform_pokemons')
    @patch('data_processing.etl.extract_pokemons')
    @patch('data_processing.etl.create_tables')
    @patch('data_processing.etl.create_connection')
    def test_etl_pipeline_load_failure(
        self,
        mock_create_connection,
        mock_create_tables,
        mock_extract,
        mock_transform,
        mock_load,
        mock_sleep
    ):
        """Test ETL pipeline when loading fails"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_create_tables.return_value = True
        
        mock_extract.return_value = {
            "name": "bulbasaur",
            "id": 1,
            "types": ["grass"],
            "abilities": ["overgrow"],
            "moves": ["tackle"],
            "stats": {"hp": 45},
            "evolution_chain": ["bulbasaur"],
            "is_evolved": False
        }
        
        mock_transform.return_value = {
            "main": {"id": 1, "name": "bulbasaur", "is_evolved": False},
            "types": ["grass"],
            "abilities": ["overgrow"],
            "moves": ["tackle"],
            "stats": [{"stat_name": "hp", "base_stat": 45}]
        }
        
        mock_load.return_value = False  # Load fails
        
        result = run_etl_pipeline()
        
        # Pipeline should complete but with 0 successes
        assert result is False
        mock_conn.close.assert_called_once()

    @patch('data_processing.etl.POKEMON_TO_FETCH', 3)
    @patch('data_processing.etl.sleep')
    @patch('data_processing.etl.load_pokemons')
    @patch('data_processing.etl.transform_pokemons')
    @patch('data_processing.etl.extract_pokemons')
    @patch('data_processing.etl.create_tables')
    @patch('data_processing.etl.create_connection')
    def test_etl_pipeline_partial_success(
        self,
        mock_create_connection,
        mock_create_tables,
        mock_extract,
        mock_transform,
        mock_load,
        mock_sleep
    ):
        """Test ETL pipeline with mixed success and failures"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_create_tables.return_value = True
        
        # First succeeds, second fails extraction, third succeeds
        mock_extract.side_effect = [
            {"name": "bulbasaur", "id": 1, "types": ["grass"], "abilities": [], 
             "moves": [], "stats": {"hp": 45}, "evolution_chain": ["bulbasaur"], "is_evolved": False},
            None,  # Extraction fails
            {"name": "charmander", "id": 3, "types": ["fire"], "abilities": [], 
             "moves": [], "stats": {"hp": 39}, "evolution_chain": ["charmander"], "is_evolved": False}
        ]
        
        mock_transform.return_value = {
            "main": {"id": 1, "name": "test", "is_evolved": False},
            "types": [], "abilities": [], "moves": [], "stats": []
        }
        
        mock_load.return_value = True
        
        result = run_etl_pipeline()
        
        # Should have 2 successes and 1 failure
        assert result is True
        assert mock_extract.call_count == 3
        assert mock_transform.call_count == 2  # Only called for successful extractions
        assert mock_load.call_count == 2
        mock_conn.close.assert_called_once()

    @patch('data_processing.etl.POKEMON_TO_FETCH', 1)
    @patch('data_processing.etl.sleep')
    @patch('data_processing.etl.load_pokemons')
    @patch('data_processing.etl.transform_pokemons')
    @patch('data_processing.etl.extract_pokemons')
    @patch('data_processing.etl.create_tables')
    @patch('data_processing.etl.create_connection')
    def test_etl_pipeline_exception_handling(
        self,
        mock_create_connection,
        mock_create_tables,
        mock_extract,
        mock_transform,
        mock_load,
        mock_sleep
    ):
        """Test ETL pipeline exception handling during processing"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_create_tables.return_value = True
        
        # Extract raises an exception
        mock_extract.side_effect = Exception("Unexpected error")
        
        result = run_etl_pipeline()
        
        # Pipeline should handle exception and continue
        assert result is False
        mock_conn.close.assert_called_once()

    @patch('data_processing.etl.create_tables')
    @patch('data_processing.etl.create_connection')
    def test_etl_pipeline_table_creation_warning(
        self,
        mock_create_connection,
        mock_create_tables
    ):
        """Test ETL pipeline when table creation partially fails"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_create_tables.return_value = False  # Table creation fails
        
        # Pipeline should continue despite table creation failure
        # This test mainly ensures no crash occurs
        result = run_etl_pipeline()
        
        mock_conn.close.assert_called_once()

    @patch('data_processing.etl.POKEMON_TO_FETCH', 1)
    @patch('data_processing.etl.sleep')
    @patch('data_processing.etl.load_pokemons')
    @patch('data_processing.etl.transform_pokemons')
    @patch('data_processing.etl.extract_pokemons')
    @patch('data_processing.etl.create_tables')
    @patch('data_processing.etl.create_connection')
    def test_etl_pipeline_respects_api_delay(
        self,
        mock_create_connection,
        mock_create_tables,
        mock_extract,
        mock_transform,
        mock_load,
        mock_sleep
    ):
        """Test that ETL pipeline respects API delay"""
        mock_conn = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_create_tables.return_value = True
        
        mock_extract.return_value = {
            "name": "bulbasaur",
            "id": 1,
            "types": ["grass"],
            "abilities": [],
            "moves": [],
            "stats": {"hp": 45},
            "evolution_chain": ["bulbasaur"],
            "is_evolved": False
        }
        
        mock_transform.return_value = {
            "main": {"id": 1, "name": "bulbasaur", "is_evolved": False},
            "types": [], "abilities": [], "moves": [], "stats": []
        }
        
        mock_load.return_value = True
        
        run_etl_pipeline()
        
        # Sleep should be called once per Pokemon
        assert mock_sleep.call_count == 1

    @patch('data_processing.etl.create_connection')
    def test_etl_pipeline_critical_error(self, mock_create_connection):
        """Test ETL pipeline with critical error in setup"""
        mock_create_connection.side_effect = Exception("Critical database error")
        
        result = run_etl_pipeline()
        
        assert result is False


class TestETLIntegration:
    """Integration tests for ETL pipeline with real database"""

    def test_etl_integration_with_real_database(self, tmp_path):
        """Integration test with real database (mocked API calls)"""
        db_file = tmp_path / "test_pokemon.db"
        
        with patch('data_processing.etl.DATABASE_FILE', str(db_file)):
            with patch('data_processing.etl.POKEMON_TO_FETCH', 1):
                with patch('data_processing.etl.sleep'):
                    with patch('data_processing.etl.extract_pokemons') as mock_extract:
                        # Mock the API call to return valid data
                        mock_extract.return_value = {
                            "name": "bulbasaur",
                            "id": 1,
                            "types": ["grass", "poison"],
                            "abilities": ["overgrow"],
                            "moves": ["tackle"],
                            "stats": {
                                "hp": 45,
                                "attack": 49,
                                "defense": 49
                            },
                            "evolution_chain": ["bulbasaur", "ivysaur", "venusaur"],
                            "is_evolved": False
                        }
                        
                        result = run_etl_pipeline()
                        
                        assert result is True
                        
                        # Verify data in database
                        conn = sqlite3.connect(str(db_file))
                        cursor = conn.cursor()
                        
                        cursor.execute("SELECT name FROM pokemon WHERE id = 1")
                        pokemon = cursor.fetchone()
                        assert pokemon is not None
                        assert pokemon[0] == "bulbasaur"
                        
                        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])