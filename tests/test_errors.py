"""Tests for error handling in the SDK."""

import pytest
import responses
import httpx
from sorterpy import Sorter

def test_api_error_handling(mock_sorter):
    """Test handling of API errors."""
    with responses.RequestsMock() as rsps:
        # Mock a 404 error
        rsps.add(
            responses.GET,
            "https://sorter.social/api/tag/exists?title=error_tag",
            json={"error": "Not found"},
            status=404
        )
        
        # Test that the error is properly raised
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            mock_sorter.get_tag("error_tag")
        assert exc_info.value.response.status_code == 404

def test_validation_error_handling(mock_sorter, mock_api_responses):
    """Test handling of validation errors in voting."""
    with responses.RequestsMock() as rsps:
        # Setup tag and items
        rsps.add(
            responses.GET,
            "https://sorter.social/api/tag/exists?title=test_tag",
            json={"exists": True, "id": 1},
            status=200
        )
        
        rsps.add(
            responses.GET,
            "https://sorter.social/api/tag?id=1",
            json=mock_api_responses["tag"],
            status=200
        )
        
        # Mock items
        item1 = mock_api_responses["item"].copy()
        item2 = mock_api_responses["item"].copy()
        item2["id"] = 2
        item2["title"] = "test_item_2"
        
        rsps.add(
            responses.GET,
            "https://sorter.social/api/feed?tag_id=1",
            json={"items": [item1, item2]},
            status=200
        )
        
        tag = mock_sorter.get_tag("test_tag")
        items = tag.item()
        
        # Test invalid vote magnitude
        with pytest.raises(ValueError):
            tag.vote(items[0], items[1], 200)  # Magnitude too high
        
        with pytest.raises(ValueError):
            tag.vote(items[0], items[1], -100)  # Magnitude too low

def test_quiet_mode_error_handling(mock_sorter):
    """Test error handling in quiet mode."""
    with responses.RequestsMock() as rsps:
        # Enable quiet mode
        mock_sorter.options(quiet=True)
        
        # Mock a 500 error
        rsps.add(
            responses.GET,
            "https://sorter.social/api/tag/exists?title=error_tag",
            json={"error": "Internal server error"},
            status=500
        )
        
        # In quiet mode, should return None instead of raising
        result = mock_sorter.get_tag("error_tag")
        assert result is None

def test_invalid_parameter_types(mock_sorter, mock_api_responses):
    """Test handling of invalid parameter types."""
    with responses.RequestsMock() as rsps:
        # Setup tag
        rsps.add(
            responses.GET,
            "https://sorter.social/api/tag/exists?title=test_tag",
            json={"exists": True, "id": 1},
            status=200
        )
        
        rsps.add(
            responses.GET,
            "https://sorter.social/api/tag?id=1",
            json=mock_api_responses["tag"],
            status=200
        )
        
        tag = mock_sorter.get_tag("test_tag")
        
        # Test invalid parameter types for vote
        with pytest.raises(TypeError):
            tag.vote("not_an_item", "also_not_an_item", 50)
            
        # Test invalid attribute type
        with pytest.raises(TypeError):
            tag.vote(mock_api_responses["item"], mock_api_responses["item"], 50, attribute="not_an_attribute_id")