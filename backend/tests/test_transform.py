# tests/test_transform.py
import pytest
from data_processing.transform import transform_pokemons


class TestTransformPokemons:
    """Test suite for transform_pokemons function"""

    def test_none_input(self):
        """Test that None input returns None"""
        result = transform_pokemons(None)
        assert result is None

    def test_empty_dict_input(self):
        """Test that empty dict returns None"""
        result = transform_pokemons({})
        assert result is None

    def test_invalid_input_type(self):
        """Test that non-dict input returns None"""
        result = transform_pokemons("not a dict")
        assert result is None
        
        result = transform_pokemons([1, 2, 3])
        assert result is None

    def test_missing_required_fields(self):
        """Test that missing required fields returns None"""
        # Missing 'id'
        result = transform_pokemons({"name": "bulbasaur", "is_evolved": False})
        assert result is None

        # Missing 'name'
        result = transform_pokemons({"id": 1, "is_evolved": False})
        assert result is None

        # Missing 'is_evolved'
        result = transform_pokemons({"id": 1, "name": "bulbasaur"})
        assert result is None

    def test_successful_transformation(self):
        """Test successful transformation of valid Pokemon data"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "types": ["grass", "poison"],
            "abilities": ["overgrow", "chlorophyll"],
            "moves": ["tackle", "vine-whip"],
            "stats": {
                "hp": 45,
                "attack": 49,
                "defense": 49,
                "special-attack": 65,
                "special-defense": 65,
                "speed": 45
            },
            "evolution_chain": ["bulbasaur", "ivysaur", "venusaur"]
        }

        result = transform_pokemons(input_data)

        # Check main data
        assert result is not None
        assert result["main"]["id"] == 1
        assert result["main"]["name"] == "bulbasaur"
        assert result["main"]["is_evolved"] is False

        # Check types
        assert "grass" in result["types"]
        assert "poison" in result["types"]

        # Check abilities
        assert "overgrow" in result["abilities"]
        assert "chlorophyll" in result["abilities"]

        # Check moves
        assert "tackle" in result["moves"]
        assert "vine-whip" in result["moves"]

        # Check stats
        assert len(result["stats"]) == 6
        hp_stat = next(s for s in result["stats"] if s["stat_name"] == "hp")
        assert hp_stat["base_stat"] == 45

        # Check evolution chain
        assert result["evolution_chain_identifier"] == "bulbasaur"
        assert len(result["evolution_links"]) == 3
        assert result["evolution_links"][0]["name"] == "bulbasaur"
        assert result["evolution_links"][0]["stage"] == 1

    def test_is_evolved_conversion(self):
        """Test that is_evolved is properly converted to boolean"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": 1,  # Integer instead of boolean
            "stats": {"hp": 45},
            "evolution_chain": ["bulbasaur"]
        }

        result = transform_pokemons(input_data)
        assert result is not None
        assert result["main"]["is_evolved"] is True

    def test_types_not_list(self):
        """Test handling when types is not a list"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "types": "grass",  # Single value instead of list
            "stats": {"hp": 45},
            "evolution_chain": ["bulbasaur"]
        }

        result = transform_pokemons(input_data)
        assert result is not None
        assert "grass" in result["types"]

    def test_abilities_not_list(self):
        """Test handling when abilities is not a list"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "abilities": "overgrow",  # Single value instead of list
            "stats": {"hp": 45},
            "evolution_chain": ["bulbasaur"]
        }

        result = transform_pokemons(input_data)
        assert result is not None
        assert "overgrow" in result["abilities"]

    def test_moves_not_list(self):
        """Test handling when moves is not a list"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "moves": "tackle",  # Single value instead of list
            "stats": {"hp": 45},
            "evolution_chain": ["bulbasaur"]
        }

        result = transform_pokemons(input_data)
        assert result is not None
        assert "tackle" in result["moves"]

    def test_missing_optional_fields(self):
        """Test that missing optional fields are handled gracefully"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "stats": {"hp": 45},
            "evolution_chain": ["bulbasaur"]
            # Missing types, abilities, moves
        }

        result = transform_pokemons(input_data)
        assert result is not None
        assert result["types"] == []
        assert result["abilities"] == []
        assert result["moves"] == []

    def test_invalid_stats_type(self):
        """Test that invalid stats type returns None"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "stats": "not a dict",  # Invalid type
            "evolution_chain": ["bulbasaur"]
        }

        result = transform_pokemons(input_data)
        assert result is None

    def test_stats_with_invalid_values(self):
        """Test that invalid stat values are filtered out"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "stats": {
                "hp": 45,
                "attack": "invalid",  # Invalid value
                "defense": 49
            },
            "evolution_chain": ["bulbasaur"]
        }

        result = transform_pokemons(input_data)
        assert result is not None
        # Only hp and defense should be included
        assert len(result["stats"]) == 2
        stat_names = [s["stat_name"] for s in result["stats"]]
        assert "hp" in stat_names
        assert "defense" in stat_names
        assert "attack" not in stat_names

    def test_missing_evolution_chain(self):
        """Test that missing evolution_chain returns None"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "stats": {"hp": 45}
            # Missing evolution_chain
        }

        result = transform_pokemons(input_data)
        assert result is None

    def test_empty_evolution_chain(self):
        """Test that empty evolution_chain returns None"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "stats": {"hp": 45},
            "evolution_chain": []
        }

        result = transform_pokemons(input_data)
        assert result is None

    def test_invalid_evolution_chain_type(self):
        """Test that invalid evolution_chain type returns None"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "stats": {"hp": 45},
            "evolution_chain": "bulbasaur"  # Not a list
        }

        result = transform_pokemons(input_data)
        assert result is None

    def test_evolution_links_stages(self):
        """Test that evolution stages are correctly numbered"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "stats": {"hp": 45},
            "evolution_chain": ["bulbasaur", "ivysaur", "venusaur"]
        }

        result = transform_pokemons(input_data)
        assert result is not None
        
        # Check stages
        assert result["evolution_links"][0]["stage"] == 1
        assert result["evolution_links"][1]["stage"] == 2
        assert result["evolution_links"][2]["stage"] == 3

    def test_evolution_chain_with_non_string_values(self):
        """Test evolution chain with non-string values filters them out"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "stats": {"hp": 45},
            "evolution_chain": ["bulbasaur", 123, "ivysaur", None, "venusaur"]
        }

        result = transform_pokemons(input_data)
        assert result is not None
        
        # Only string values should be included
        assert len(result["evolution_links"]) == 3
        names = [link["name"] for link in result["evolution_links"]]
        assert "bulbasaur" in names
        assert "ivysaur" in names
        assert "venusaur" in names

    def test_float_stats_conversion(self):
        """Test that float stats are converted to integers"""
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "stats": {
                "hp": 45.7,  # Float value
                "attack": 49.2
            },
            "evolution_chain": ["bulbasaur"]
        }

        result = transform_pokemons(input_data)
        assert result is not None
        
        # Check that stats are integers
        for stat in result["stats"]:
            assert isinstance(stat["base_stat"], int)

    def test_exception_handling(self):
        """Test that unexpected exceptions are caught and return None"""
        # This tests the general exception handler
        input_data = {
            "id": 1,
            "name": "bulbasaur",
            "is_evolved": False,
            "stats": {"hp": 45},
            "evolution_chain": ["bulbasaur"]
        }
        
        # The function should handle any unexpected errors gracefully
        result = transform_pokemons(input_data)
        assert result is not None  # This should succeed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])