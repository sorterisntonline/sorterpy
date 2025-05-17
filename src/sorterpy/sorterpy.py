"""
Sorterpy - Python SDK for the Sorter API.

This module provides classes for interacting with the Sorter API.
"""

from typing import Optional, List, Dict, Any, Union

import httpx
import logging
from loguru import logger

class Sorter:
    """Main client for interacting with the Sorter API."""
    
    def __init__(self, api_key: str, base_url: str = "https://sorter.social", options: Dict[str, Any] = None):
        """Initialize the Sorter client.
        
        Args:
            api_key: Your Sorter API key
            base_url: Base URL for the Sorter API
            options: Additional options for the client
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.options = options or {}
        self.client = httpx.Client(
            headers={"Authorization": f"Bearer {api_key}"}
        )
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the Sorter API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to httpx
            
        Returns:
            Dict[str, Any]: Response JSON
        """
        url = f"{self.base_url}{endpoint}"
        response = self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def tag(self, title: str, description: Optional[str] = None, namespace: Optional[str] = None) -> "Tag":
        """Get or create a tag.
        
        Args:
            title: Tag title
            description: Optional tag description
            namespace: Optional namespace
            
        Returns:
            Tag: The tag object
            
        Example:
            >>> tag = sorter.tag("my_tag", "My tag description")
        """
        params = {"title": title}
        if namespace:
            params["namespace"] = namespace
            
        data = {}
        if description:
            data["description"] = description
            
        response = self._request("POST", "/api/tag", params=params, json=data)
        logger.debug(f"Created/retrieved tag: {title} (ID: {response.get('id')})")
        return Tag(self, response)
    
    def get_tag(self, title: str, namespace: Optional[str] = None) -> Optional["Tag"]:
        """Get a tag by title without creating it if it doesn't exist.
        
        Args:
            title: Tag title to find
            namespace: Optional namespace to look in
            
        Returns:
            Optional[Tag]: Tag if found, None otherwise
            
        Example:
            >>> tag = sorter.get_tag("my_tag")
            >>> if tag is None:
            ...     print("Tag not found")
        """
        namespace_param = f"&namespace={namespace}" if namespace else ""
        response = self._request("GET", f"/api/tag/exists?title={title}{namespace_param}")
        
        if response.get("exists"):
            logger.debug(f"Found tag: {title} (ID: {response.get('id')})")
            return Tag(self, response)
        
        logger.debug(f"Tag not found: {title}")
        return None

    @staticmethod
    def exists_tag(title: str, namespace: Optional[str] = None) -> bool:
        """Check if a tag exists without initializing a client.
        
        Args:
            title: Tag title to check
            namespace: Optional namespace to look in
            
        Returns:
            bool: True if tag exists
            
        Example:
            >>> if Sorter.exists_tag("my_tag"):
            ...     print("Tag exists")
        """
        # Note: This is a static method because existence checking doesn't 
        # require authentication or client initialization
        base_url = "https://sorter.social"  # Default base URL
        namespace_param = f"&namespace={namespace}" if namespace else ""
        
        try:
            response = httpx.get(f"{base_url}/api/tag/exists?title={title}{namespace_param}")
            response.raise_for_status()
            return response.json().get("exists", False)
        except Exception:
            return False

    def get_tag_by_id(self, tag_id: int) -> Optional["Tag"]:
        """Get a tag by its ID.
        
        Args:
            tag_id: The tag's ID
            
        Returns:
            Optional[Tag]: Tag if found, None otherwise
        """
        response = self._request("GET", f"/api/tag?id={tag_id}")
        if response:
            return Tag(self, response)
        return None
        
    def list_attributes(self, limit: int = 100) -> List["Attribute"]:
        """List all attributes.
        
        Args:
            limit: Maximum number of attributes to return
            
        Returns:
            List[Attribute]: List of attributes
        """
        response = self._request("GET", f"/api/attributes?limit={limit}")
        return [Attribute(self, attr) for attr in response.get("attributes", [])]
        
    def get_attribute(self, title: str) -> Optional["Attribute"]:
        """Get an attribute by title.
        
        Args:
            title: Attribute title
            
        Returns:
            Optional[Attribute]: Attribute if found, None otherwise
        """
        response = self._request("GET", f"/api/attribute?title={title}")
        if response:
            return Attribute(self, response)
        return None


class Tag:
    """Represents a tag in Sorter."""
    
    def __init__(self, client: Sorter, data: Dict[str, Any]):
        """Initialize a Tag object.
        
        Args:
            client: Sorter client
            data: Tag data from API
        """
        self.client = client
        self.id = data.get("id")
        self.title = data.get("title")
        self.description = data.get("description")
        self.url = data.get("url")
        self._data = data
        
    def item(self, title: str, description: Optional[str] = None, external_id: Optional[str] = None) -> "Item":
        """Get or create an item in this tag.
        
        Args:
            title: Item title
            description: Optional item description
            external_id: Optional external ID
            
        Returns:
            Item: The item object
            
        Example:
            >>> item = tag.item("A", "Option A")
        """
        params = {"tag_id": self.id, "title": title}
        
        data = {}
        if description:
            data["description"] = description
        if external_id:
            data["external_id"] = external_id
            
        response = self.client._request("POST", "/api/item", params=params, json=data)
        logger.debug(f"Created/retrieved item: {title} in tag {self.title} (ID: {response.get('id')})")
        return Item(self, response)
        
    def list_items(self, limit: int = 100) -> List["Item"]:
        """List all items in this tag.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List[Item]: List of items
        """
        response = self.client._request("GET", f"/api/items?tag_id={self.id}&limit={limit}")
        return [Item(self, item) for item in response.get("items", [])]
        
    def vote(self, item1_id: int, item2_id: int, score: int = 0, attribute_id: Optional[int] = None) -> "Vote":
        """Vote on a pair of items.
        
        Args:
            item1_id: ID of the first item
            item2_id: ID of the second item
            score: Score (-100 to 100, 0 is neutral)
            attribute_id: Optional attribute ID
            
        Returns:
            Vote: The vote object
            
        Example:
            >>> vote = tag.vote(item1.id, item2.id, score=25)
        """
        data = {
            "tag_id": self.id,
            "item1_id": item1_id,
            "item2_id": item2_id,
            "score": score
        }
        
        if attribute_id:
            data["attribute_id"] = attribute_id
            
        response = self.client._request("POST", "/api/vote", json=data)
        logger.debug(f"Voted on items {item1_id} vs {item2_id} in tag {self.title} with score {score}")
        return Vote(self, response)
        
    def rankings(self, attribute_id: Optional[int] = None) -> "Rankings":
        """Get rankings for this tag.
        
        Args:
            attribute_id: Optional attribute ID
            
        Returns:
            Rankings: The rankings object
            
        Example:
            >>> rankings = tag.rankings()
            >>> for item in rankings.sorted():
            ...     print(f"{item.title}: {item.score}")
        """
        params = {"tag_id": self.id}
        if attribute_id:
            params["attribute_id"] = attribute_id
            
        response = self.client._request("GET", "/api/rankings", params=params)
        return Rankings(self, response)
    
    def get_item(self, title: str) -> Optional["Item"]:
        """Get an item by title without creating it.
        
        Args:
            title: Item title to find
            
        Returns:
            Optional[Item]: Item if found, None otherwise
            
        Example:
            >>> item = tag.get_item("A")
            >>> if item is None:
            ...     print("Item not found")
        """
        items = self.list_items()
        return next((item for item in items if item.title == title), None)

    def get_item_by_id(self, item_id: int) -> Optional["Item"]:
        """Get an item by its ID.
        
        Args:
            item_id: The item's ID
            
        Returns:
            Optional[Item]: Item if found, None otherwise
        """
        response = self.client._request("GET", f"/api/item?id={item_id}")
        if response:
            return Item(self, response)
        return None

    @staticmethod
    def exists(title: str, namespace: Optional[str] = None) -> bool:
        """Check if a tag exists without initializing a client.
        
        This is an alias for Sorter.exists_tag for convenience.
        
        Args:
            title: Tag title to check
            namespace: Optional namespace to look in
            
        Returns:
            bool: True if tag exists
        """
        return Sorter.exists_tag(title, namespace)


class Item:
    """Represents an item in a tag."""
    
    def __init__(self, tag: Tag, data: Dict[str, Any]):
        """Initialize an Item object.
        
        Args:
            tag: Parent tag
            data: Item data from API
        """
        self.tag = tag
        self.client = tag.client
        self.id = data.get("id")
        self.title = data.get("title")
        self.description = data.get("description")
        self.external_id = data.get("external_id")
        self.url = data.get("url")
        self.score = data.get("score")
        self._data = data
    
    @staticmethod
    def exists(title: str, tag_id: int) -> bool:
        """Check if an item exists within a tag without initializing a client.
        
        Args:
            title: Item title to check
            tag_id: ID of the tag to check in
            
        Returns:
            bool: True if item exists
            
        Example:
            >>> if Item.exists("A", tag_id=123):
            ...     print("Item exists in tag")
        """
        base_url = "https://sorter.social"  # Default base URL
        try:
            response = httpx.get(f"{base_url}/api/item/exists?title={title}&tag_id={tag_id}")
            response.raise_for_status()
            return response.json().get("exists", False)
        except Exception:
            return False


class Vote:
    """Represents a vote between two items."""
    
    def __init__(self, tag: Tag, data: Dict[str, Any]):
        """Initialize a Vote object.
        
        Args:
            tag: Parent tag
            data: Vote data from API
        """
        self.tag = tag
        self.client = tag.client
        self.id = data.get("id")
        self.item1_id = data.get("item1_id")
        self.item2_id = data.get("item2_id")
        self.score = data.get("score")
        self.attribute_id = data.get("attribute_id")
        self._data = data


class Rankings:
    """Represents rankings for a tag."""
    
    def __init__(self, tag: Tag, data: Dict[str, Any]):
        """Initialize a Rankings object.
        
        Args:
            tag: Parent tag
            data: Rankings data from API
        """
        self.tag = tag
        self.client = tag.client
        self._data = data
        
    def sorted(self) -> List[Item]:
        """Get sorted items.
        
        Returns:
            List[Item]: Sorted items
        """
        return [Item(self.tag, item) for item in self._data.get("sorted_items", [])]
        
    def unsorted(self) -> List[Item]:
        """Get unsorted items.
        
        Returns:
            List[Item]: Unsorted items
        """
        return [Item(self.tag, item) for item in self._data.get("unsorted_items", [])]
        
    def skipped(self) -> List[Item]:
        """Get skipped items.
        
        Returns:
            List[Item]: Skipped items
        """
        return [Item(self.tag, item) for item in self._data.get("skipped_items", [])]
        
    def users_who_voted(self) -> List[Dict[str, Any]]:
        """Get users who voted.
        
        Returns:
            List[Dict[str, Any]]: Users who voted
        """
        return self._data.get("users_who_voted", [])
        
    def votes(self) -> List[Dict[str, Any]]:
        """Get votes.
        
        Returns:
            List[Dict[str, Any]]: Votes
        """
        return self._data.get("votes", [])


class Attribute:
    """Represents an attribute for voting."""
    
    def __init__(self, client: Sorter, data: Dict[str, Any]):
        """Initialize an Attribute object.
        
        Args:
            client: Sorter client
            data: Attribute data from API
        """
        self.client = client
        self.id = data.get("id")
        self.title = data.get("title")
        self.description = data.get("description")
        self._data = data
    
    @staticmethod
    def exists(title: str) -> bool:
        """Check if an attribute exists without initializing a client.
        
        Args:
            title: Attribute title to check
            
        Returns:
            bool: True if attribute exists
            
        Example:
            >>> if Attribute.exists("quality"):
            ...     print("Attribute exists")
        """
        base_url = "https://sorter.social"  # Default base URL
        try:
            response = httpx.get(f"{base_url}/api/attribute/exists?title={title}")
            response.raise_for_status()
            return response.json().get("exists", False)
        except Exception:
            return False
