"""Tests for Attribute functionality."""

import pytest
import responses
from sorterpy import Sorter

def test_create_attribute(mock_sorter, mock_api_responses):
    """Test creating a new attribute."""
    with responses.RequestsMock() as rsps:
        # Mock attribute existence check
        rsps.add(
            responses.GET,
            "https://sorter.social/api/attribute/exists?title=new_attribute",
            json={"exists": False},
            status=404
        )
        
        # Mock attribute creation
        attr_response = mock_api_responses["attribute"].copy()
        attr_response["title"] = "new_attribute"
        
        rsps.add(
            responses.POST,
            "https://sorter.social/api/attribute",
            json=attr_response,
            status=200
        )
        
        attribute = mock_sorter.create_attribute("new_attribute", "A new attribute")
        assert attribute.title == "new_attribute"
        assert attribute.id == 1

def test_get_attribute(mock_sorter, mock_api_responses):
    """Test getting an existing attribute."""
    with responses.RequestsMock() as rsps:
        # Mock attribute list retrieval
        rsps.add(
            responses.GET,
            "https://sorter.social/api/attribute",
            json={"attributes": [mock_api_responses["attribute"]]},
            status=200
        )
        
        attribute = mock_sorter.get_attribute("test_attribute")
        assert attribute is not None
        assert attribute.title == "test_attribute"
        assert attribute.id == 1

def test_get_nonexistent_attribute(mock_sorter):
    """Test getting a nonexistent attribute."""
    with responses.RequestsMock() as rsps:
        # Mock empty attribute list
        rsps.add(
            responses.GET,
            "https://sorter.social/api/attribute",
            json={"attributes": []},
            status=200
        )
        
        attribute = mock_sorter.get_attribute("nonexistent")
        assert attribute is None

def test_attribute_exists(mock_sorter, mock_api_responses):
    """Test the static Attribute.exists method."""
    with responses.RequestsMock() as rsps:
        # Test for existing attribute
        rsps.add(
            responses.GET,
            "https://sorter.social/api/attribute/exists?title=test_attribute",
            json={"exists": True, "id": 1},
            status=200
        )
        
        # Test for non-existing attribute
        rsps.add(
            responses.GET,
            "https://sorter.social/api/attribute/exists?title=nonexistent",
            json={"exists": False},
            status=404
        )
        
        assert Sorter.Attribute.exists("test_attribute") is True
        assert Sorter.Attribute.exists("nonexistent") is False

def test_list_attributes(mock_sorter, mock_api_responses):
    """Test listing all attributes."""
    with responses.RequestsMock() as rsps:
        # Create multiple test attributes
        attr1 = mock_api_responses["attribute"].copy()
        attr2 = mock_api_responses["attribute"].copy()
        attr2["id"] = 2
        attr2["title"] = "test_attribute_2"
        
        rsps.add(
            responses.GET,
            "https://sorter.social/api/attribute",
            json={"attributes": [attr1, attr2]},
            status=200
        )
        
        attributes = mock_sorter.list_attributes()
        assert len(attributes) == 2
        assert attributes[0].title == "test_attribute"
        assert attributes[1].title == "test_attribute_2"

def test_attribute_in_rankings(mock_sorter, mock_api_responses):
    """Test using attributes in rankings retrieval."""
    with responses.RequestsMock() as rsps:
        # Setup tag and attribute
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
        
        # Mock rankings with attribute filter
        rankings_response = mock_api_responses["rankings"].copy()
        rankings_response["selected_attribute"] = mock_api_responses["attribute"]
        
        rsps.add(
            responses.GET,
            "https://sorter.social/api/tag/page",
            json=rankings_response,
            status=200,
            match=[responses.matchers.query_param_matcher({"id": "1", "attribute": "1", "elo": "true"})]
        )
        
        tag = mock_sorter.get_tag("test_tag")
        rankings = tag.rankings(attribute="test_attribute")
        
        assert rankings._selected_attribute is not None
        assert rankings._selected_attribute.id == 1
        assert rankings._selected_attribute.title == "test_attribute"