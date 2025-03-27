"""Tests for voting functionality."""

import pytest
import responses
from sorterpy import Sorter

def test_vote_equal_scale(mock_sorter, mock_api_responses):
    """Test voting with equal scale (-50 to 50)."""
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
        
        # Mock two items in feed
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
        
        # Mock vote submission
        rsps.add(
            responses.POST,
            "https://sorter.social/api/vote",
            json=mock_api_responses["vote"],
            status=200
        )
        
        # Create vote with equal scale (-50 to 50)
        mock_sorter.options(vote_magnitude="equal")
        tag = mock_sorter.get_tag("test_tag")
        items = tag.item()  # Get all items
        
        # Test both parameter orderings (though one is deprecated)
        vote1 = tag.vote(items[0], items[1], 25)  # Standard ordering
        vote2 = tag.vote(items[0], 25, items[1])  # Deprecated ordering
        
        assert vote1.magnitude == -25  # Converted from backend scale
        assert vote2.magnitude == -25

def test_vote_positive_scale(mock_sorter, mock_api_responses):
    """Test voting with positive scale (0 to 100)."""
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
        
        # Mock two items in feed
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
        
        # Mock vote submission
        vote_response = mock_api_responses["vote"].copy()
        vote_response["magnitude"] = 75
        
        rsps.add(
            responses.POST,
            "https://sorter.social/api/vote",
            json=vote_response,
            status=200
        )
        
        # Create vote with positive scale (0 to 100)
        mock_sorter.options(vote_magnitude="positive")
        tag = mock_sorter.get_tag("test_tag")
        items = tag.item()
        
        vote = tag.vote(items[0], items[1], 75)
        assert vote.magnitude == 75  # No conversion needed

def test_vote_with_attribute(mock_sorter, mock_api_responses):
    """Test voting with an attribute."""
    with responses.RequestsMock() as rsps:
        # Setup tag, items, and attribute
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
        
        # Mock attribute creation/retrieval
        rsps.add(
            responses.GET,
            "https://sorter.social/api/attribute/exists?title=quality",
            json={"exists": True, "id": 1},
            status=200
        )
        
        rsps.add(
            responses.GET,
            "https://sorter.social/api/attribute?id=1",
            json={"attributes": [mock_api_responses["attribute"]]},
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
        
        # Mock vote with attribute
        vote_response = mock_api_responses["vote"].copy()
        vote_response["attribute"] = 1
        
        rsps.add(
            responses.POST,
            "https://sorter.social/api/vote",
            json=vote_response,
            status=200
        )
        
        # Create vote with attribute
        tag = mock_sorter.get_tag("test_tag")
        items = tag.item()
        attribute = mock_sorter.attribute("quality")
        
        vote = tag.vote(items[0], items[1], 75, attribute=attribute)
        assert vote.attribute == 1