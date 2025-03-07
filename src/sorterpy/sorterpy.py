"""Main module for the sorterpy SDK."""

import httpx
from loguru import logger
from typing import Dict, List, Optional, Union, Any
from enum import IntEnum

class SorterOptions(IntEnum):
    """Options for the Sorter client."""
    EQUAL = 0
    POSITIVE = 1

class Sorter:
    """Main client for the Sorter API."""
    
    def __init__(self, api_key: str, base_url: str = "https://sorter.social", vote_magnitude_scale: SorterOptions = SorterOptions.EQUAL):
        """Initialize the Sorter client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the Sorter API
            vote_magnitude_scale: Scale for vote magnitudes (EQUAL: -50 to 50, POSITIVE: 0 to 100)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client()
        self.client.headers.update({
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        })
        self._options = {
            "vote_magnitude_scale": vote_magnitude_scale
        }
        logger.info(f"Sorter SDK initialized with base URL: {self.base_url}")
    
    def options(self, **kwargs) -> Dict:
        """Update client options and return current options.
        
        Args:
            **kwargs: Options to update
            
        Returns:
            Dict: Current options after update
        """
        # Update options if provided
        for key, value in kwargs.items():
            if key in self._options:
                self._options[key] = value
        
        return self._options
    
    def _convert_magnitude_to_backend(self, magnitude: int) -> int:
        """Convert magnitude from client scale to backend scale.
        
        Args:
            magnitude: Magnitude in client scale
            
        Returns:
            int: Magnitude in backend scale (0-100)
        """
        if self._options["vote_magnitude_scale"] == SorterOptions.EQUAL:
            # Convert from -50 to 50 scale to 0 to 100 scale
            return magnitude + 50
        else:
            # Already in 0 to 100 scale
            return magnitude
    
    def _convert_magnitude_from_backend(self, magnitude: int) -> int:
        """Convert magnitude from backend scale to client scale.
        
        Args:
            magnitude: Magnitude in backend scale (0-100)
            
        Returns:
            int: Magnitude in client scale
        """
        if self._options["vote_magnitude_scale"] == SorterOptions.EQUAL:
            # Convert from 0 to 100 scale to -50 to 50 scale
            return magnitude - 50
        else:
            # Keep in 0 to 100 scale
            return magnitude
    
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
        
    def tag(self, title: str, description: str = "", unlisted: bool = False, namespace: Optional[str] = None) -> "Tag":
        """Create a new tag or get an existing one.
        
        Args:
            title: Tag title
            description: Tag description
            unlisted: Whether the tag is unlisted
            namespace: Optional namespace for the tag
            
        Returns:
            Tag: New or existing tag instance
        """
        # Check if tag exists
        namespace_param = f"&namespace={namespace}" if namespace else ""
        response = self._request("GET", f"/api/tag/exists?title={title}{namespace_param}")
        
        payload = {
            "title": title,
            "description": description,
            "unlisted": unlisted
        }
        
        # Only include namespace in payload if explicitly provided
        if namespace:
            payload["namespace"] = namespace
        
        # If tag exists, include its ID in the payload to update it
        if response.get("exists"):
            payload["id"] = response.get("id")
        
        response = self._request("POST", "/api/tag", json=payload)
        return Tag(self, response)
    
    def list_tags(self, namespace: Optional[str] = None) -> Dict[str, List[Dict]]:
        """List all tags.
        
        Args:
            namespace: Optional namespace to filter tags by
            
        Returns:
            Dict with keys: public, private, unlisted. Each contains a list of tag data.
        """
        response = self._request("GET", "/api/tag")
        logger.info(f"Retrieved {len(response.get('public', []))} public, {len(response.get('private', []))} private, {len(response.get('unlisted', []))} unlisted tags")
        
        # Filter by namespace if provided
        if namespace:
            result = {"public": [], "private": [], "unlisted": []}
            for category in ["public", "private", "unlisted"]:
                result[category] = [
                    tag for tag in response.get(category, [])
                    if tag.get("namespace") == namespace
                ]
            return result
        
        return response
    
    def create_attribute(self, title: str, description: str = "") -> "Attribute":
        """Create a new attribute.
        
        Args:
            title: Title for the attribute
            description: Optional description
            
        Returns:
            Attribute: Created attribute instance
        """
        payload = {
            "title": title,
            "description": description
        }
        
        response = self._request("POST", "/api/attribute", json=payload)
        logger.info(f"Created attribute: {title}")
        return Attribute(self, response)
    
    def list_attributes(self) -> List["Attribute"]:
        """List all available attributes.
        
        Returns:
            List[Attribute]: List of attribute instances
        """
        response = self._request("GET", "/api/attribute")
        attributes = []
        for attr_data in response.get("attributes", []):
            attributes.append(Attribute(self, attr_data))
        logger.info(f"Retrieved {len(attributes)} attributes")
        return attributes
    
    def get_attribute(self, title: str) -> Optional["Attribute"]:
        """Get an attribute by title.
        
        Args:
            title: Title of the attribute to find
            
        Returns:
            Optional[Attribute]: Attribute if found, None otherwise
        """
        attributes = self.list_attributes()
        for attr in attributes:
            if attr.title.lower() == title.lower():
                return attr
        return None


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
        self.namespace = data.get("namespace") or data.get("ns")  # Support both new and old API responses
        self.owner = data.get("owner")
        self.created_at = data.get("created_at")
        self.edited_at = data.get("edited_at")
        self.unlisted = data.get("unlisted", False)
        self.domain_pk_namespace = data.get("domain_pk_namespace")
        self.domain_pk = data.get("domain_pk")
        self.vote_count = data.get("vote_count", 0)
        logger.info(f"Tag initialized: {self.title} (ID: {self.id})")
    
    def update(self, title: Optional[str] = None, description: Optional[str] = None, 
               unlisted: Optional[bool] = None, domain_pk_namespace: Optional[str] = None,
               domain_pk: Optional[str] = None) -> "Tag":
        """Update tag properties.
        
        Args:
            title: New title
            description: New description
            unlisted: New unlisted status
            domain_pk_namespace: New domain namespace
            domain_pk: New domain primary key
            
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
        if domain_pk_namespace is not None:
            payload["domain_pk_namespace"] = domain_pk_namespace
        if domain_pk is not None:
            payload["domain_pk"] = domain_pk
        
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
    
    def attribute(self, title: str, description: str = "") -> int:
        """Get or create an attribute by title.
        
        Args:
            title: Title of the attribute
            description: Optional description for new attributes
            
        Returns:
            int: ID of the attribute
            
        Examples:
            >>> # Get existing attribute ID
            >>> attr_id = tag.attribute("quality")
            
            >>> # Create new attribute with description
            >>> attr_id = tag.attribute("difficulty", "How hard the item is to use")
            
            >>> # Use attribute ID in voting
            >>> tag.vote(1, 2, 3, attribute=attr_id)
        """
        attr = self.client.get_attribute(title)
        if attr is None:
            attr = self.client.create_attribute(title, description)
        return attr.id

    def vote(self, left_item: "Item", magnitude_or_right_item: Union[int, "Item"], right_item_or_magnitude: Union["Item", int], attribute: Optional[int] = None) -> "Vote":
        """Record a vote between two items in this tag.
        
        Supports two parameter orderings:
        1. vote(left_item, magnitude, right_item)
        2. vote(left_item, right_item, magnitude)
        
        Args:
            left_item: Left item in comparison
            magnitude_or_right_item: Either the magnitude (-50 to 50 or 0 to 100) or the right item
            right_item_or_magnitude: Either the right item or the magnitude
            attribute: Optional attribute ID for this vote
            
        Returns:
            Vote: Recorded vote instance
        """
        # Determine parameter order
        if isinstance(magnitude_or_right_item, int) and isinstance(right_item_or_magnitude, Item):
            # First ordering: vote(left_item, magnitude, right_item)
            magnitude = magnitude_or_right_item
            right_item = right_item_or_magnitude
        elif isinstance(magnitude_or_right_item, Item) and isinstance(right_item_or_magnitude, int):
            # Second ordering: vote(left_item, right_item, magnitude)
            right_item = magnitude_or_right_item
            magnitude = right_item_or_magnitude
        else:
            raise TypeError("Invalid parameter types. Expected either (Item, int, Item) or (Item, Item, int).")
        
        # Validate items are in the tag
        items = self.list_items()
        if left_item not in items or right_item not in items:
            raise ValueError("Both items must belong to the tag.")
        
        # Validate magnitude based on scale
        if self.client._options["vote_magnitude_scale"] == SorterOptions.EQUAL:
            if not (-50 <= magnitude <= 50):
                raise ValueError("Magnitude must be between -50 and 50.")
            backend_magnitude = self.client._convert_magnitude_to_backend(magnitude)
        else:
            if not (0 <= magnitude <= 100):
                raise ValueError("Magnitude must be between 0 and 100.")
            backend_magnitude = magnitude
        
        if attribute is None:
            attribute = 0  # Default attribute ID is 0
        
        payload = {
            "left_item_id": left_item.id,
            "right_item_id": right_item.id,
            "magnitude": backend_magnitude,
            "tag_id": self.id,
            "attribute": attribute
        }
        
        response = self.client._request("POST", "/api/vote", json=payload)
        return Vote(self, response)

    def votes(self, until: Optional[str] = None, attribute: Optional[int] = None, user: Optional[str] = None, since: Optional[str] = None) -> List["Vote"]:
        """Retrieve votes for this tag.
        
        Args:
            until: Optional timestamp to filter votes up until (ISO8601 format)
            attribute: Optional attribute ID to filter by
            user: Optional username to filter votes by
            since: Optional timestamp to filter votes starting from (ISO8601 format)
            
        Returns:
            List[Vote]: List of vote instances
        """
        params = {"tag": self.id}
        if until:
            params["until"] = until
        if attribute:
            params["attribute"] = attribute
        if user:
            params["user"] = user
        if since:
            params["since"] = since
        
        response = self.client._request("GET", "/api/vote", params=params)
        return [Vote(self, vote_data) for vote_data in response.get("votes", [])]


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
        self.slug = data.get("slug")
        self.body = data.get("body", "")
        self.url = data.get("url", "")
        self.owner = data.get("owner")
        self.created_at = data.get("created_at")
        self.edited_at = data.get("edited_at")
        self.domain_pk_namespace = data.get("domain_pk_namespace")
        self.domain_pk = data.get("domain_pk")
        logger.info(f"Item initialized: {self.title} (ID: {self.id})")
    
    def update(self, title: Optional[str] = None, description: Optional[str] = None,
               body: Optional[str] = None, url: Optional[str] = None) -> "Item":
        """Update item properties.
        
        Args:
            title: New title
            description: New description
            body: New body content, can include markdown
            url: New URL for the item
            
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
        if body is not None:
            payload["body"] = body
        if url is not None:
            payload["url"] = url
        
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


class Vote:
    """Represents a vote in Sorter."""
    
    def __init__(self, tag: Tag, data: Dict):
        """Initialize a vote.
        
        Args:
            tag: Tag instance
            data: Vote data from API
        """
        self.tag = tag
        self.client = tag.client
        self.id = data.get("id")
        self.left_item_id = data.get("left_item_id")
        self.right_item_id = data.get("right_item_id")
        backend_magnitude = data.get("magnitude")
        self.magnitude = self.client._convert_magnitude_from_backend(backend_magnitude)
        self.owner = data.get("owner")
        self.created_at = data.get("created_at")
        self.edited_at = data.get("edited_at")
        self.attribute = data.get("attribute", 0)  # Default attribute ID is 0
        self.domain_pk_namespace = data.get("domain_pk_namespace")
        logger.info(f"Vote initialized: ID {self.id} between items {self.left_item_id} and {self.right_item_id}")
    
    def delete(self) -> bool:
        """Delete the vote.
        
        Returns:
            bool: True if deleted successfully
        """
        response = self.client._request("DELETE", "/api/vote", json={"vote_id": self.id})
        return response.get("ok", False)


class Attribute:
    """Represents an attribute in Sorter."""
    
    def __init__(self, sorter: Sorter, data: Dict):
        """Initialize an attribute.
        
        Args:
            sorter: Sorter instance
            data: Attribute data from API
        """
        self.client = sorter
        self.id = data.get("id")
        self.title = data.get("title")
        self.description = data.get("description", "")
        self.owner = data.get("owner")
        self.created_at = data.get("created_at")
        self.edited_at = data.get("edited_at")
        logger.info(f"Attribute initialized: ID {self.id} with title {self.title}")
