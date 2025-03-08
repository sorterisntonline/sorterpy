"""Main module for the sorterpy SDK."""

import httpx
from loguru import logger
from typing import Dict, List, Optional, Union, Any, Tuple
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
        
    def vote(self, left_item: "Item", magnitude_or_right_item: Union[int, "Item"], right_item_or_magnitude: Union["Item", int], attribute: Optional[int] = None) -> "Vote":
        """Record a vote between two items.
        
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
        
        # Ensure both items belong to the same tag
        if left_item.tag.id != right_item.tag.id:
            raise ValueError("Both items must belong to the same tag")
            
        # Get the tag and use its vote method
        tag = left_item.tag
        
        # Validate magnitude based on scale
        if tag.client._options["vote_magnitude_scale"] == SorterOptions.EQUAL:
            if not (-50 <= magnitude <= 50):
                raise ValueError("Magnitude must be between -50 and 50.")
            backend_magnitude = tag.client._convert_magnitude_to_backend(magnitude)
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
            "tag_id": tag.id,
            "attribute": attribute
        }
        
        response = tag.client._request("POST", "/api/vote", json=payload)
        return Vote(tag, response)


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
        
        # Validate items belong to this tag
        if left_item.tag.id != self.id or right_item.tag.id != self.id:
            raise ValueError("Both items must belong to this tag.")
        
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

    def rankings(self, attribute: Optional[Union[int, str]] = None, pinned_left: Optional[int] = None, 
                pinned_right: Optional[int] = None, elo: bool = True) -> "Rankings":
        """Get rankings data for this tag.
        
        Args:
            attribute: Optional attribute ID or title to filter by
            pinned_left: Optional item ID to pin on the left side of the voting pair
            pinned_right: Optional item ID to pin on the right side of the voting pair
            elo: Whether to use ELO ranking algorithm (default: True)
            
        Returns:
            Rankings: Rankings object containing sorted items, voting pairs, etc.
        """
        params = {"id": self.id, "elo": elo}
        
        # Handle attribute parameter
        if attribute is not None:
            if isinstance(attribute, str):
                # If attribute is a string, look up the attribute ID
                attr_obj = self.client.get_attribute(attribute)
                if attr_obj:
                    params["attribute"] = attr_obj.id
                else:
                    logger.warning(f"Attribute '{attribute}' not found, using default")
            else:
                # If attribute is an ID, use it directly
                params["attribute"] = attribute
        
        # Add pinned items if specified
        if pinned_left is not None:
            params["pinned_left"] = pinned_left
        if pinned_right is not None:
            params["pinned_right"] = pinned_right
        
        response = self.client._request("GET", "/api/tag/page", params=params)
        return Rankings(self, response)
    
    def sorted(self, attribute: Optional[Union[int, str]] = None, elo: bool = True) -> List["Item"]:
        """Get sorted items for this tag.
        
        Args:
            attribute: Optional attribute ID or title to filter by
            elo: Whether to use ELO ranking algorithm (default: True)
            
        Returns:
            List[Item]: List of sorted items
        """
        rankings = self.rankings(attribute=attribute, elo=elo)
        return rankings.sorted()

    def unsorted(self, attribute: Optional[Union[int, str]] = None, elo: bool = True) -> List["Item"]:
        """Get unsorted items for this tag.
        
        Args:
            attribute: Optional attribute ID or title to filter by
            elo: Whether to use ELO ranking algorithm (default: True)
            
        Returns:
            List[Item]: List of unsorted items
        """
        rankings = self.rankings(attribute=attribute, elo=elo)
        return rankings.unsorted()

    def pair(self) -> Tuple["Item", "Item"]:
        """Get a voting pair for this tag.
        
        Returns:
            Tuple[Item, Item]: Tuple of (left_item, right_item)
            
        Raises:
            ValueError: If no voting pair is available
        """
        return self.rankings().pair()


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
    
    def __eq__(self, other):
        """Check if two items are equal.
        
        Args:
            other: Other item to compare with
            
        Returns:
            bool: True if items are equal
        """
        if not isinstance(other, Item):
            return False
        return self.id == other.id
    
    def __hash__(self):
        """Get hash of item.
        
        Returns:
            int: Hash value
        """
        return hash(self.id)
        
    @property
    def name(self):
        """Get item name (alias for title).
        
        Returns:
            str: Item title
        """
        return self.title
    
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


class Rankings:
    """Represents tag rankings data from Sorter."""
    
    def __init__(self, tag: Tag, data: Dict):
        """Initialize rankings data.
        
        Args:
            tag: Tag instance
            data: Rankings data from API
        """
        self.tag = tag
        self.client = tag.client
        self._data = data
        
        # Parse tag data
        self.tag_data = data.get("tag", {})
        
        # Parse sorted items
        self._sorted_items = [Item(tag, item_data) for item_data in data.get("sorted", [])]
        
        # Parse unsorted items
        self._unsorted_items = [Item(tag, item_data) for item_data in data.get("unsorted", [])]
        
        # Parse skipped items
        self._skipped_items = [Item(tag, item_data) for item_data in data.get("skipped", [])]
        
        # Parse voting pair
        self._pair = [Item(tag, item_data) for item_data in data.get("pair", [])]
        if len(self._pair) != 2 and len(self._pair) != 0:
            logger.warning(f"Expected 2 items in voting pair, got {len(self._pair)}")
        
        # Parse votes
        self._votes = [Vote(tag, vote_data) for vote_data in data.get("votes", [])]
        
        # Parse attributes
        self._attributes = [Attribute(self.client, attr_data) for attr_data in data.get("attributes", [])]
        
        # Parse selected attribute
        self._selected_attribute = None
        if data.get("selected_attribute"):
            self._selected_attribute = Attribute(self.client, data.get("selected_attribute"))
        
        # Parse permissions
        self._permissions = data.get("perms", {})
        
        # Parse users who voted
        self._users_who_voted = data.get("users_who_voted", [])
        
        logger.info(f"Rankings initialized for tag {tag.title} with {len(self._sorted_items)} sorted items")
    
    def sorted(self) -> List[Item]:
        """Get sorted items.
        
        Returns:
            List[Item]: List of sorted items
        """
        return self._sorted_items
    
    def unsorted(self) -> List[Item]:
        """Get unsorted items.
        
        Returns:
            List[Item]: List of unsorted items
        """
        return self._unsorted_items
    
    def skipped(self) -> List[Item]:
        """Get skipped items.
        
        Returns:
            List[Item]: List of skipped items
        """
        return self._skipped_items
    
    def pair(self) -> Tuple[Item, Item]:
        """Get voting pair.
        
        Returns:
            Tuple[Item, Item]: Tuple of (left_item, right_item) if available
            
        Raises:
            ValueError: If no voting pair is available
        """
        if len(self._pair) != 2:
            raise ValueError("No voting pair available")
        return self._pair[0], self._pair[1]
    
    def votes(self) -> List[Vote]:
        """Get votes.
        
        Returns:
            List[Vote]: List of votes
        """
        return self._votes
    
    def attributes(self) -> List[Attribute]:
        """Get attributes.
        
        Returns:
            List[Attribute]: List of attributes
        """
        return self._attributes
    
    def selected_attribute(self) -> Optional[Attribute]:
        """Get selected attribute.
        
        Returns:
            Optional[Attribute]: Selected attribute if available
        """
        return self._selected_attribute
    
    def permissions(self) -> Dict:
        """Get permissions.
        
        Returns:
            Dict: Permissions dictionary
        """
        return self._permissions
    
    def users_who_voted(self) -> List[Dict]:
        """Get users who voted.
        
        Returns:
            List[Dict]: List of users who voted
        """
        return self._users_who_voted
