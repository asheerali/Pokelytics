# tests/test_load.py
import pytest
import sqlite3
import os
from data_processing.load import create_connection, create_tables, load_pokemons


class TestCreateConnection:
    """Test suite for create_connection function"""

    def test_create_connection_success(self, tmp_path):
        """Test successful database connection creation"""
        db_file = tmp_path / "test.db"
        conn = create_connection(str(db_file))
        
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        
        # Verify foreign keys are enabled
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        assert result[0] == 1
        
        conn.close()

    def test_create_connection_invalid_input(self):
        """Test that invalid inputs return None"""
        # None input
        result = create_connection(None)
        assert result is None
        
        # Non-string input
        result = create_connection(123)
        assert result is None
        
        # Empty string
        result = create_connection("")
        assert result is None

    def test_create_connection_invalid_path(self):
        """Test connection with invalid path"""
        # This might succeed or fail depending on OS permissions
        # The function should handle it gracefully
        result = create_connection("/invalid/path/test.db")
        # Should either return None or a valid connection
        assert result is None or isinstance(result, sqlite3.Connection)
        if result:
            result.close()


class TestCreateTables:
    """Test suite for create_tables function"""

    def test_create_tables_success(self, tmp_path):
        """Test successful table creation"""
        db_file = tmp_path / "test.db"
        conn = create_connection(str(db_file))
        
        result = create_tables(conn)
        assert result is True
        
        # Verify all tables were created
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'abilities',
            'moves',
            'pokemon',
            'pokemon_abilities',
            'pokemon_moves',
            'pokemon_stats',
            'pokemon_types',
            'stats',
            'types'
        ]
        
        for table in expected_tables:
            assert table in tables
        
        conn.close()

    def test_create_tables_none_connection(self):
        """Test that None connection returns False"""
        result = create_tables(None)
        assert result is False

    def test_create_tables_idempotent(self, tmp_path):
        """Test that creating tables multiple times succeeds (idempotent)"""
        db_file = tmp_path / "test.db"
        conn = create_connection(str(db_file))
        
        # Create tables first time
        result1 = create_tables(conn)
        assert result1 is True
        
        # Create tables second time (should use IF NOT EXISTS)
        result2 = create_tables(conn)
        assert result2 is True
        
        conn.close()

    def test_create_tables_foreign_keys(self, tmp_path):
        """Test that foreign key relationships are properly created"""
        db_file = tmp_path / "test.db"
        conn = create_connection(str(db_file))
        create_tables(conn)
        
        cursor = conn.cursor()
        
        # Test foreign key constraint on pokemon_types
        cursor.execute("INSERT INTO types (name) VALUES ('fire')")
        cursor.execute("INSERT INTO pokemon (id, name, is_evolved) VALUES (1, 'charmander', 0)")
        cursor.execute("INSERT INTO pokemon_types (pokemon_id, type_name) VALUES (1, 'fire')")
        conn.commit()
        
        # This should fail due to foreign key constraint
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO pokemon_types (pokemon_id, type_name) VALUES (999, 'fire')")
            conn.commit()
        
        conn.close()


class TestLoadPokemons:
    """Test suite for load_pokemons function"""

    @pytest.fixture
    def db_with_tables(self, tmp_path):
        """Fixture to provide a database with tables already created"""
        db_file = tmp_path / "test.db"
        conn = create_connection(str(db_file))
        create_tables(conn)
        return conn

    def test_load_pokemons_success(self, db_with_tables):
        """Test successful loading of Pokemon data"""
        conn = db_with_tables
        
        transformed_data = {
            "main": {
                "id": 1,
                "name": "bulbasaur",
                "is_evolved": False
            },
            "types": ["grass", "poison"],
            "abilities": ["overgrow", "chlorophyll"],
            "moves": ["tackle", "vine-whip"],
            "stats": [
                {"stat_name": "hp", "base_stat": 45},
                {"stat_name": "attack", "base_stat": 49}
            ]
        }
        
        result = load_pokemons(conn, transformed_data)
        assert result is True
        
        # Verify data was loaded
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM pokemon WHERE id = 1")
        pokemon = cursor.fetchone()
        assert pokemon[0] == "bulbasaur"
        
        cursor.execute("SELECT type_name FROM pokemon_types WHERE pokemon_id = 1")
        types = [row[0] for row in cursor.fetchall()]
        assert "grass" in types
        assert "poison" in types
        
        conn.close()

    def test_load_pokemons_none_connection(self):
        """Test that None connection returns False"""
        transformed_data = {
            "main": {"id": 1, "name": "bulbasaur", "is_evolved": False},
            "types": [],
            "abilities": [],
            "moves": [],
            "stats": []
        }
        
        result = load_pokemons(None, transformed_data)
        assert result is False

    def test_load_pokemons_invalid_data(self, db_with_tables):
        """Test that invalid data returns False"""
        conn = db_with_tables
        
        # None data
        result = load_pokemons(conn, None)
        assert result is False
        
        # Empty dict
        result = load_pokemons(conn, {})
        assert result is False
        
        # Missing 'main' key
        result = load_pokemons(conn, {"types": []})
        assert result is False
        
        conn.close()

    def test_load_pokemons_idempotent(self, db_with_tables):
        """Test that loading same Pokemon twice is idempotent (uses INSERT OR IGNORE)"""
        conn = db_with_tables
        
        transformed_data = {
            "main": {
                "id": 1,
                "name": "bulbasaur",
                "is_evolved": False
            },
            "types": ["grass"],
            "abilities": ["overgrow"],
            "moves": ["tackle"],
            "stats": [{"stat_name": "hp", "base_stat": 45}]
        }
        
        # Load first time
        result1 = load_pokemons(conn, transformed_data)
        assert result1 is True
        
        # Load second time (should not fail due to INSERT OR IGNORE)
        result2 = load_pokemons(conn, transformed_data)
        assert result2 is True
        
        # Verify only one record exists
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pokemon WHERE id = 1")
        count = cursor.fetchone()[0]
        assert count == 1
        
        conn.close()

    def test_load_pokemons_empty_lists(self, db_with_tables):
        """Test loading Pokemon with empty types, abilities, moves, stats"""
        conn = db_with_tables
        
        transformed_data = {
            "main": {
                "id": 1,
                "name": "bulbasaur",
                "is_evolved": False
            },
            "types": [],
            "abilities": [],
            "moves": [],
            "stats": []
        }
        
        result = load_pokemons(conn, transformed_data)
        assert result is True
        
        # Verify pokemon was created but no related data
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM pokemon WHERE id = 1")
        pokemon = cursor.fetchone()
        assert pokemon[0] == "bulbasaur"
        
        cursor.execute("SELECT COUNT(*) FROM pokemon_types WHERE pokemon_id = 1")
        count = cursor.fetchone()[0]
        assert count == 0
        
        conn.close()

    def test_load_pokemons_rollback_on_error(self, db_with_tables):
        """Test that transaction is rolled back on error"""
        conn = db_with_tables
        
        # Create invalid data that should cause an error
        transformed_data = {
            "main": {
                "id": "invalid",  # Should be integer
                "name": "bulbasaur",
                "is_evolved": False
            },
            "types": [],
            "abilities": [],
            "moves": [],
            "stats": []
        }
        
        result = load_pokemons(conn, transformed_data)
        assert result is False
        
        # Verify no data was inserted
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pokemon")
        count = cursor.fetchone()[0]
        assert count == 0
        
        conn.close()

    def test_load_pokemons_multiple_stats(self, db_with_tables):
        """Test loading Pokemon with multiple stats"""
        conn = db_with_tables
        
        transformed_data = {
            "main": {
                "id": 1,
                "name": "bulbasaur",
                "is_evolved": False
            },
            "types": [],
            "abilities": [],
            "moves": [],
            "stats": [
                {"stat_name": "hp", "base_stat": 45},
                {"stat_name": "attack", "base_stat": 49},
                {"stat_name": "defense", "base_stat": 49},
                {"stat_name": "special-attack", "base_stat": 65},
                {"stat_name": "special-defense", "base_stat": 65},
                {"stat_name": "speed", "base_stat": 45}
            ]
        }
        
        result = load_pokemons(conn, transformed_data)
        assert result is True
        
        # Verify all stats were loaded
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pokemon_stats WHERE pokemon_id = 1")
        count = cursor.fetchone()[0]
        assert count == 6
        
        cursor.execute("SELECT base_stat FROM pokemon_stats WHERE pokemon_id = 1 AND stat_name = 'hp'")
        hp = cursor.fetchone()[0]
        assert hp == 45
        
        conn.close()

    def test_load_pokemons_with_all_data(self, db_with_tables):
        """Integration test: Load complete Pokemon data"""
        conn = db_with_tables
        
        transformed_data = {
            "main": {
                "id": 1,
                "name": "bulbasaur",
                "is_evolved": False
            },
            "types": ["grass", "poison"],
            "abilities": ["overgrow", "chlorophyll"],
            "moves": ["tackle", "vine-whip", "growl"],
            "stats": [
                {"stat_name": "hp", "base_stat": 45},
                {"stat_name": "attack", "base_stat": 49},
                {"stat_name": "defense", "base_stat": 49}
            ]
        }
        
        result = load_pokemons(conn, transformed_data)
        assert result is True
        
        # Comprehensive verification
        cursor = conn.cursor()
        
        # Check main pokemon
        cursor.execute("SELECT id, name, is_evolved FROM pokemon WHERE id = 1")
        pokemon = cursor.fetchone()
        assert pokemon == (1, "bulbasaur", 0)
        
        # Check types
        cursor.execute("SELECT COUNT(*) FROM pokemon_types WHERE pokemon_id = 1")
        assert cursor.fetchone()[0] == 2
        
        # Check abilities
        cursor.execute("SELECT COUNT(*) FROM pokemon_abilities WHERE pokemon_id = 1")
        assert cursor.fetchone()[0] == 2
        
        # Check moves
        cursor.execute("SELECT COUNT(*) FROM pokemon_moves WHERE pokemon_id = 1")
        assert cursor.fetchone()[0] == 3
        
        # Check stats
        cursor.execute("SELECT COUNT(*) FROM pokemon_stats WHERE pokemon_id = 1")
        assert cursor.fetchone()[0] == 3
        
        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])