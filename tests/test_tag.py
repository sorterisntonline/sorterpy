"""Tests for Tag functionality."""

import pytest
import responses
from sorterpy import Sorter

@pytest.mark.parametrize("title,expected_exists", [
    ("existing_tag", True),
    ("nonexistent_tag", False)
])
def test_tag_exists(title, expected_exists):
    """Test the static Tag.exists method."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            f"https://sorter.social/api/tag/exists?title={title}",
            json={"exists": expected_exists, "id": 1 if expected_exists else None},
            status=200
        )
        
        exists = Sorter.exists_tag(title)
        assert exists == expected_exists

def test_get_tag(mock_sorter, mock_api_responses):
    """Test getting an existing tag."""
    with responses.RequestsMock() as rsps:
        # Mock exists check
        rsps.add(
            responses.GET,
            "https://sorter.social/api/tag/exists?title=test_tag",
            json={"exists": True, "id": 1},
            status=200
        )
        
        # Mock tag retrieval
        rsps.add(
            responses.GET,
            "https://sorter.social/api/tag?id=1",
            json=mock_api_responses["tag"],
            status=200
        )
        
        tag = mock_sorter.get_tag("test_tag")
        assert tag is not None
        assert tag.title == "test_tag"
        assert tag.id == 1

def test_get_nonexistent_tag(mock_sorter):
    """Test getting a nonexistent tag."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://sorter.social/api/tag/exists?title=nonexistent",
            json={"exists": False},
            status=200
        )
        
        tag = mock_sorter.get_tag("nonexistent")
        assert tag is None

def test_create_tag(mock_sorter, mock_api_responses):
    """Test creating a new tag."""
    with responses.RequestsMock() as rsps:
        # Mock exists check
        rsps.add(
            responses.GET,
            "https://sorter.social/api/tag/exists?title=new_tag",
            json={"exists": False},
            status=200
        )
        
        # Mock tag creation
        rsps.add(
            responses.POST,
            "https://sorter.social/api/tag",
            json=mock_api_responses["tag"],
            status=200
        )
        
        tag = mock_sorter.tag("new_tag", description="A new tag")
        assert tag is not None
        assert tag.title == "test_tag"  # From mock response
        assert tag.id == 1

def test_tag_update(mock_sorter, mock_api_responses):
    """Test updating tag properties."""
    with responses.RequestsMock() as rsps:
        # First get the tag
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
        
        # Then update it
        updated_response = mock_api_responses["tag"].copy()
        updated_response["description"] = "Updated description"
        
        rsps.add(
            responses.POST,
            "https://sorter.social/api/tag",
            json=updated_response,
            status=200
        )
        
        tag = mock_sorter.get_tag("test_tag")
        updated_tag = tag.update(description="Updated description")
        
        assert updated_tag.description == "Updated description"

def test_tag_link(mock_sorter, mock_api_responses):
    """Test generating tag links."""
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
        
        tag = mock_sorter.get_tag("test_tag")
        link = tag.link()
        
        assert "https://sorter.social/1/test-tag" in link