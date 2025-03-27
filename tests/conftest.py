"""Test configuration and fixtures for sorterpy."""

import pytest
from sorterpy import Sorter

@pytest.fixture
def mock_sorter():
    """Create a Sorter instance with mocked API responses."""
    return Sorter(
        api_key="test-api-key",
        base_url="https://sorter.social",
        options={
            "verbose": True,
            "compatibility_warnings": False  # Disable warnings during tests
        }
    )

@pytest.fixture
def mock_api_responses():
    """Common API response data for tests."""
    return {
        "tag": {
            "id": 1,
            "title": "test_tag",
            "slug": "test-tag",
            "description": "A test tag",
            "unlisted": False,
            "created_at": "2024-03-27T00:00:00Z",
            "edited_at": "2024-03-27T00:00:00Z",
            "owner": "test_user"
        },
        "item": {
            "id": 1,
            "title": "test_item",
            "slug": "test-item",
            "body": "Test item body",
            "created_at": "2024-03-27T00:00:00Z",
            "edited_at": "2024-03-27T00:00:00Z",
            "owner": "test_user"
        },
        "attribute": {
            "id": 1,
            "title": "test_attribute",
            "description": "A test attribute",
            "created_at": "2024-03-27T00:00:00Z",
            "edited_at": "2024-03-27T00:00:00Z",
            "owner": "test_user"
        },
        "vote": {
            "id": 1,
            "left_item_id": 1,
            "right_item_id": 2,
            "magnitude": 75,  # Backend scale (0-100)
            "created_at": "2024-03-27T00:00:00Z",
            "edited_at": "2024-03-27T00:00:00Z",
            "owner": "test_user",
            "attribute": 0
        },
        "rankings": {
            "tag": {"id": 1, "title": "test_tag"},
            "sorted": [
                {"id": 1, "title": "A", "slug": "a"},
                {"id": 2, "title": "B", "slug": "b"}
            ],
            "unsorted": [
                {"id": 3, "title": "C", "slug": "c"}
            ],
            "pair": [
                {"id": 1, "title": "A", "slug": "a"},
                {"id": 3, "title": "C", "slug": "c"}
            ],
            "votes": [],
            "attributes": [],
            "selected_attribute": None,
            "perms": {},
            "users_who_voted": []
        }
    }