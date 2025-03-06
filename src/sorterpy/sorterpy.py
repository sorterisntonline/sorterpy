"""Main module for the sorterpy SDK."""

import httpx
from loguru import logger
from typing import Dict, List, Optional, Union, Any

class Sorter:
    """Main client for the Sorter API."""
    
    def __init__(self, api_key: str, base_url: str = "https://sorter.social"):
        """Initialize the Sorter client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the Sorter API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client()
        self.client.headers.update({
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        })
        # Using API key as namespace
        self._namespace = api_key[:8]  # Using first 8 chars of API key as namespace
        logger.info(f"Sorter SDK initialized with base URL: {self.base_url}")
    
    def _request(self, method: str, path: str, **kwargs) -> Dict:
        """Make a request to the Sorter API.
        
        Args:
            method: HTTP method
            path: API endpoint path
            **kwargs: Additional arguments to pass to httpx
            
        Returns:
            Dict: Response from the API
        """
        url = f"{self.base_url}{path}"
        response = self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
        
    def tag(self, title: str, description: str = "", unlisted: bool = False) -> "Tag":
        """Create a new tag or get an existing one.
        
        Args:
            title: Tag title
            description: Tag description
            unlisted: Whether the tag is unlisted
            
        Returns:
            Tag: New or existing tag instance
        """
        # Check if tag exists
        response = self._request("GET", f"/api/tag/exists?title={title}&ns={self._namespace}")
        
        payload = {
            "title": title,
            "description": description,
            "ns": self._namespace,
            "unlisted": unlisted
        }
        
        # If tag exists, include its ID in the payload to update it
        if response.get("exists"):
            payload["id"] = response.get("id")
        
        response = self._request("POST", "/api/tag", json=payload)
        return Tag(self, response)
    
    def list_tags(self) -> Dict[str, List[Dict]]:
        """List all tags in the project.
        
        Returns:
            Dict: Dictionary with categories of tags (public, private, unlisted)
        """
        response = self._request("GET", "/api/tag")
        # Filter by namespace
        result = {"public": [], "private": [], "unlisted": []}
        for category in ["public", "private", "unlisted"]:
            result[category] = [
                tag for tag in response.get(category, [])
                if tag.get("ns") == self._namespace
            ]
        return result


class Tag:
    """Represents a tag in Sorter."""
    
    def __init__(self, sorter: Sorter, data: Dict):
        """Initialize a tag.
        
        Args:
            sorter: Sorter client instance
            data: Tag data from API
        """
        self.sorter = sorter
        self.client = sorter
        self.id = data.get("id")
        self.title = data.get("title")
        self.description = data.get("description")
        self.slug = data.get("slug")
        self.unlisted = data.get("unlisted", False)
        logger.info(f"Tag initialized: {self.title} (ID: {self.id})")
    
    def update(self, title: Optional[str] = None, description: Optional[str] = None, 
               unlisted: Optional[bool] = None) -> "Tag":
        """Update tag properties.
        
        Args:
            title: New title
            description: New description
            unlisted: New unlisted status
            
        Returns:
            Tag: Updated tag instance
        """
        payload = {"id": self.id}
        
        if title:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        if unlisted is not None:
            payload["unlisted"] = unlisted
        
        response = self.client._request("POST", "/api/tag", json=payload)
        return Tag(self.sorter, response)
    
    def delete(self) -> bool:
        """Delete the tag.
        
        Returns:
            bool: True if deleted successfully
        """
        response = self.client._request("DELETE", f"/api/tag?id={self.id}")
        return response.get("deleted", False)
    
    def item(self, title: str, description: str = "") -> "Item":
        """Create a new item or update an existing one in this tag.
        
        Args:
            title: Item title
            description: Item description
            
        Returns:
            Item: New or updated item instance
        """
        # We'll need to check existing items to see if one with this title exists
        items = self.list_items()
        existing_item = next((item for item in items if item.title == title), None)
        
        payload = {
            "title": title,
            "description": description,
            "tag_id": self.id
        }
        
        # If item exists, include its ID in the payload
        if existing_item:
            payload["id"] = existing_item.id
        
        response = self.client._request("POST", "/api/item", json=payload)
        return Item(self, response)
    
    def list_items(self) -> List["Item"]:
        """List all items in the tag.
        
        Returns:
            List[Item]: List of item instances
        """
        # According to the API spec, we need to get the feed for this tag
        response = self.client._request("GET", f"/api/feed?tag_id={self.id}")
        return [Item(self, item_data) for item_data in response.get("items", [])]


class Item:
    """Represents an item in Sorter."""
    
    def __init__(self, tag: Tag, data: Dict):
        """Initialize an item.
        
        Args:
            tag: Tag instance
            data: Item data from API
        """
        self.tag = tag
        self.client = tag.client
        self.id = data.get("id")
        self.title = data.get("title")
        self.description = data.get("description")
        self.owner = data.get("owner")
        self.created_at = data.get("created_at")
        logger.info(f"Item initialized: {self.title} (ID: {self.id})")
    
    def update(self, title: Optional[str] = None, description: Optional[str] = None) -> "Item":
        """Update item properties.
        
        Args:
            title: New title
            description: New description
            
        Returns:
            Item: Updated item instance
        """
        payload = {
            "id": self.id,
            "tag_id": self.tag.id
        }
        
        if title:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        
        response = self.client._request("POST", "/api/item", json=payload)
        return Item(self.tag, response)
    
    def delete(self) -> bool:
        """Delete the item.
        
        Note: API doesn't have a direct endpoint for deleting items.
        This would need to be implemented if the API supports it.
        
        Returns:
            bool: True if deleted successfully
        """
        logger.warning("Item deletion is not supported by the API")
        return False
