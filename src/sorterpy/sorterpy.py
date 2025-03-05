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
        logger.info(f"Sorter SDK initialized with base URL: {self.base_url}")
    
    def project(self, name: str) -> "Project":
        """Get or create a project by name.
        
        Args:
            name: Unique name for the project
            
        Returns:
            Project: A project instance
        """
        return Project(self, name)
    
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


class Project:
    """Represents a project in Sorter."""
    
    def __init__(self, client: Sorter, name: str):
        """Initialize a project.
        
        Args:
            client: Sorter client instance
            name: Project name
        """
        self.client = client
        self.name = name
        self._namespace = name  # Using project name as namespace
        logger.info(f"Project initialized: {name}")
    
    def create_tag(self, title: str, description: str = "", unlisted: bool = False) -> "Tag":
        """Create a new tag.
        
        Args:
            title: Tag title
            description: Tag description
            unlisted: Whether the tag is unlisted
            
        Returns:
            Tag: Created tag instance
        """
        payload = {
            "title": title,
            "description": description,
            "ns": self._namespace,
            "unlisted": unlisted
        }
        
        response = self.client._request("POST", "/api/tag", json=payload)
        return Tag(self, response)
    
    def get_tag(self, tag_id: Optional[int] = None, title: Optional[str] = None) -> Optional["Tag"]:
        """Get a tag by ID or title.
        
        Args:
            tag_id: Tag ID
            title: Tag title
            
        Returns:
            Tag: Tag instance if found, None otherwise
        """
        # First check if tag exists by title if provided
        if title:
            response = self.client._request("GET", f"/api/tag/exists?title={title}&ns={self._namespace}")
            if response.get("exists"):
                tag_id = response.get("id")
            else:
                return None
                
        if not tag_id:
            return None
            
        # Get all tags and find the specific one
        all_tags = self.list_tags()
        for category in ["public", "private", "unlisted"]:
            for tag in all_tags.get(category, []):
                if tag.get("id") == tag_id:
                    return Tag(self, tag)
        
        return None
    
    def list_tags(self) -> Dict[str, List[Dict]]:
        """List all tags in the project.
        
        Returns:
            Dict: Dictionary with categories of tags (public, private, unlisted)
        """
        response = self.client._request("GET", "/api/tag")
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
    
    def __init__(self, project: Project, data: Dict):
        """Initialize a tag.
        
        Args:
            project: Project instance
            data: Tag data from API
        """
        self.project = project
        self.client = project.client
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
        payload = {"tag_id": self.id}
        
        if title:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        if unlisted is not None:
            payload["unlisted"] = unlisted
        
        response = self.client._request("POST", "/api/tag", json=payload)
        return Tag(self.project, response)
    
    def delete(self) -> bool:
        """Delete the tag.
        
        Returns:
            bool: True if deleted successfully
        """
        response = self.client._request("DELETE", f"/api/tag?id={self.id}")
        return response.get("deleted", False)
    
    def create_item(self, title: str, description: str = "") -> "Item":
        """Create a new item in this tag.
        
        Args:
            title: Item title
            description: Item description
            
        Returns:
            Item: Created item instance
        """
        payload = {
            "title": title,
            "description": description,
            "tag_id": self.id
        }
        
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
