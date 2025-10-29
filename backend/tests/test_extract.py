# tests/test_extract.py
import pytest
from unittest.mock import patch, Mock
from data_processing.extract import extract_pokemons


class TestExtractPokemons:
    """Test suite for extract_pokemons function"""

    def test_invalid_pokemon_id_zero(self):
        """Test that pokemon_id of 0 returns None"""
        result = extract_pokemons(0)
        assert result is None

    def test_invalid_pokemon_id_negative(self):
        """Test that negative pokemon_id returns None"""
        result = extract_pokemons(-1)
        assert result is None

    def test_invalid_pokemon_id_string(self):
        """Test that string pokemon_id returns None"""
        result = extract_pokemons("1")
        assert result is None

    @patch('data_processing.extract.requests.get')
    @patch('data_processing.extract.sleep')
    def test_successful_extraction(self, mock_sleep, mock_get):
        """Test successful Pokemon data extraction"""
        # Mock main Pokemon data
        mock_pokemon_response = Mock()
        mock_pokemon_response.json.return_value = {
            "name": "bulbasaur",
            "id": 1,
            "types": [{"type": {"name": "grass"}}, {"type": {"name": "poison"}}],
            "abilities": [{"ability": {"name": "overgrow"}}],
            "moves": [{"move": {"name": "tackle"}}],
            "stats": [{"stat": {"name": "hp"}, "base_stat": 45}],
            "species": {"url": "https://pokeapi.co/api/v2/pokemon-species/1/"}
        }
        mock_pokemon_response.raise_for_status = Mock()

        # Mock species data
        mock_species_response = Mock()
        mock_species_response.json.return_value = {
            "evolution_chain": {"url": "https://pokeapi.co/api/v2/evolution-chain/1/"}
        }
        mock_species_response.raise_for_status = Mock()

        # Mock evolution chain data
        mock_evolution_response = Mock()
        mock_evolution_response.json.return_value = {
            "chain": {
                "species": {"name": "bulbasaur"},
                "evolves_to": [
                    {
                        "species": {"name": "ivysaur"},
                        "evolves_to": [
                            {"species": {"name": "venusaur"}, "evolves_to": []}
                        ]
                    }
                ]
            }
        }
        mock_evolution_response.raise_for_status = Mock()

        # Set up mock to return different responses for each call
        mock_get.side_effect = [
            mock_pokemon_response,
            mock_species_response,
            mock_evolution_response
        ]

        result = extract_pokemons(1)

        # Assertions
        assert result is not None
        assert result["name"] == "bulbasaur"
        assert result["id"] == 1
        assert "grass" in result["types"]
        assert "poison" in result["types"]
        assert "overgrow" in result["abilities"]
        assert "tackle" in result["moves"]
        assert result["stats"]["hp"] == 45
        assert result["evolution_chain"] == ["bulbasaur", "ivysaur", "venusaur"]
        assert result["is_evolved"] is False

    @patch('data_processing.extract.requests.get')
    @patch('data_processing.extract.sleep')
    def test_evolved_pokemon(self, mock_sleep, mock_get):
        """Test extraction of evolved Pokemon (is_evolved should be True)"""
        # Mock main Pokemon data for Ivysaur
        mock_pokemon_response = Mock()
        mock_pokemon_response.json.return_value = {
            "name": "ivysaur",
            "id": 2,
            "types": [{"type": {"name": "grass"}}],
            "abilities": [{"ability": {"name": "overgrow"}}],
            "moves": [{"move": {"name": "tackle"}}],
            "stats": [{"stat": {"name": "hp"}, "base_stat": 60}],
            "species": {"url": "https://pokeapi.co/api/v2/pokemon-species/2/"}
        }
        mock_pokemon_response.raise_for_status = Mock()

        # Mock species data
        mock_species_response = Mock()
        mock_species_response.json.return_value = {
            "evolution_chain": {"url": "https://pokeapi.co/api/v2/evolution-chain/1/"}
        }
        mock_species_response.raise_for_status = Mock()

        # Mock evolution chain data (starts with bulbasaur, not ivysaur)
        mock_evolution_response = Mock()
        mock_evolution_response.json.return_value = {
            "chain": {
                "species": {"name": "bulbasaur"},
                "evolves_to": [
                    {
                        "species": {"name": "ivysaur"},
                        "evolves_to": [
                            {"species": {"name": "venusaur"}, "evolves_to": []}
                        ]
                    }
                ]
            }
        }
        mock_evolution_response.raise_for_status = Mock()

        mock_get.side_effect = [
            mock_pokemon_response,
            mock_species_response,
            mock_evolution_response
        ]

        result = extract_pokemons(2)

        assert result is not None
        assert result["name"] == "ivysaur"
        assert result["is_evolved"] is True

    @patch('data_processing.extract.requests.get')
    @patch('data_processing.extract.sleep')
    def test_api_request_exception(self, mock_sleep, mock_get):
        """Test handling of API request exceptions"""
        import requests
        # Change from generic Exception to requests.exceptions.RequestException
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = extract_pokemons(1)

        assert result is None
    
    @patch('data_processing.extract.requests.get')
    @patch('data_processing.extract.sleep')
    def test_invalid_json_response(self, mock_sleep, mock_get):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = extract_pokemons(1)

        assert result is None

    @patch('data_processing.extract.requests.get')
    @patch('data_processing.extract.sleep')
    def test_missing_species_url(self, mock_sleep, mock_get):
        """Test handling when species URL is missing"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "bulbasaur",
            "id": 1,
            "types": [],
            "abilities": [],
            "moves": [],
            "stats": [],
            "species": {}  # Missing URL
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = extract_pokemons(1)

        assert result is None

    @patch('data_processing.extract.requests.get')
    @patch('data_processing.extract.sleep')
    def test_api_timeout(self, mock_sleep, mock_get):
        """Test handling of API timeout"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

        result = extract_pokemons(1)

        assert result is None

    @patch('data_processing.extract.requests.get')
    @patch('data_processing.extract.sleep')
    def test_http_error(self, mock_sleep, mock_get):
        """Test handling of HTTP errors (404, 500, etc.)"""
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        result = extract_pokemons(999999)

        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])