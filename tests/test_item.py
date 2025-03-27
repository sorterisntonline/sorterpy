"""Tests for Item functionality."""

import pytest
import responses
from sorterpy import Sorter

def test_get_item(mock_sorter, mock_api_responses):
    """Test getting an item by title."""
    with responses.RequestsMock() as rsps:
        # Mock tag retrieval for item's parent tag
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
        
        # Mock feed retrieval (for listing items)
        rsps.add(
            responses.GET,
            "https://sorter.social/api/feed?tag_id=1",
            json={"items": [mock_api_responses["item"]]},
            status=200
        )
        
        tag = mock_sorter.get_tag("test_tag")
        item = tag.get_item("test_item")
        
        assert item is not None
        assert item.title == "test_item"
        assert item.id == 1

def test_get_nonexistent_item(mock_sorter, mock_api_responses):
    """Test getting a nonexistent item."""
    with responses.RequestsMock() as rsps:
        # Mock tag retrieval
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
        
        # Mock empty feed
        rsps.add(
            responses.GET,
            "https://sorter.social/api/feed?tag_id=1",
            json={"items": []},
            status=200
        )
        
        tag = mock_sorter.get_tag("test_tag")
        item = tag.get_item("nonexistent")
        
        assert item is None

def test_create_item(mock_sorter, mock_api_responses):
    """Test creating a new item."""
    with responses.RequestsMock() as rsps:
        # Mock tag retrieval
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
        
        # Mock empty feed (no existing items)
        rsps.add(
            responses.GET,
            "https://sorter.social/api/feed?tag_id=1",
            json={"items": []},
            status=200
        )
        
        # Mock item creation
        rsps.add(
            responses.POST,
            "https://sorter.social/api/item",
            json=mock_api_responses["item"],
            status=200
        )
        
        tag = mock_sorter.get_tag("test_tag")
        item = tag.item("test_item", body="Test body")
        
        assert item is not None
        assert item.title == "test_item"
        assert item.id == 1

def test_item_update(mock_sorter, mock_api_responses):
    """Test updating item properties."""
    with responses.RequestsMock() as rsps:
        # Mock tag retrieval
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
        
        # Mock item retrieval
        rsps.add(
            responses.GET,
            "https://sorter.social/api/feed?tag_id=1",
            json={"items": [mock_api_responses["item"]]},
            status=200
        )
        
        # Mock item update
        updated_response = mock_api_responses["item"].copy()
        updated_response["body"] = "Updated body"
        
        rsps.add(
            responses.POST,
            "https://sorter.social/api/item",
            json=updated_response,
            status=200
        )
        
        tag = mock_sorter.get_tag("test_tag")
        item = tag.get_item("test_item")
        updated_item = item.update(body="Updated body")
        
        assert updated_item.body == "Updated body"

def test_item_link(mock_sorter, mock_api_responses):
    """Test generating item links."""
    with responses.RequestsMock() as rsps:
        # Setup tag and item
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
        
        rsps.add(
            responses.GET,
            "https://sorter.social/api/feed?tag_id=1",
            json={"items": [mock_api_responses["item"]]},
            status=200
        )
        
        tag = mock_sorter.get_tag("test_tag")
        item = tag.get_item("test_item")
        link = item.link()
        
        # Link should include both tag and item identifiers
        assert f"{tag.id}/{tag.slug}?item={item.id}" in link

def test_item_exists(mock_sorter, mock_api_responses):
    """Test the static Item.exists method."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://sorter.social/api/item/exists?title=test_item&tag_id=1",
            json={"exists": True, "id": 1},
            status=200
        )
        
        exists = Sorter.Item.exists("test_item", tag_id=1)
        assert exists is True