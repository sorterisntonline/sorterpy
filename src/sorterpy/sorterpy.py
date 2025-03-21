"""Main module for the sorterpy SDK."""

import httpx
from loguru import logger
from typing import Dict, List, Optional, Union, Any, Tuple
import sys
import json
import importlib.metadata
import re

# Configure default logger with custom format
logger.remove()
# Custom format: abbreviated timestamp, abbreviated module path, no color for DEBUG level
LOGGER_FORMAT = "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
logger.add(sys.stderr, format=LOGGER_FORMAT, level="INFO")

# Default compatible API versions if not specified in pyproject.toml
DEFAULT_COMPATIBLE_VERSIONS = ["2"]

def _is_version_compatible(api_version: str, compatible_versions: List[str]) -> Tuple[bool, bool, Optional[str]]:
    """Check if API version is compatible with any of the specified versions.
    
    Args:
        api_version: Version string from API (e.g., "2.1.0")
        compatible_versions: List of compatible version patterns
        
    Returns:
        Tuple[bool, bool, Optional[str]]: (fully_compatible, partially_compatible, matched_pattern)
        - fully_compatible: True if version exactly matches a pattern
        - partially_compatible: True if version matches a major version pattern
        - matched_pattern: The pattern that matched (used for recommendations)
    """
    # Parse the API version
    api_parts = api_version.split('.')
    
    # For simplicity, handle non-semantic versions or versions with suffixes
    # by just taking the first three numeric parts
    cleaned_parts = []
    for part in api_parts:
        # Extract just the numeric part at the beginning of the string
        match = re.match(r'^\d+', part)
        if match:
            cleaned_parts.append(match.group(0))
        if len(cleaned_parts) >= 3:
            break
    
    # Pad with zeros if needed
    while len(cleaned_parts) < 3:
        cleaned_parts.append('0')
    
    api_major, api_minor, api_patch = map(int, cleaned_parts)
    
    # Track if we have a partial match (major version only)
    fully_compatible = False
    partially_compatible = False
    matched_pattern = None
    
    # Check against each compatible version pattern
    for version in compatible_versions:
        pattern_parts = version.split('.')
        
        # Extract just the numeric parts for comparison
        cleaned_pattern_parts = []
        for part in pattern_parts:
            match = re.match(r'^\d+', part)
            if match:
                cleaned_pattern_parts.append(match.group(0))
        
        # Major version only (e.g., "2")
        if len(cleaned_pattern_parts) == 1:
            pattern_major = int(cleaned_pattern_parts[0])
            if api_major == pattern_major:
                partially_compatible = True
                matched_pattern = version
        
        # Major.minor version (e.g., "1.1")
        elif len(cleaned_pattern_parts) == 2:
            pattern_major, pattern_minor = map(int, cleaned_pattern_parts)
            if api_major == pattern_major and api_minor == pattern_minor:
                fully_compatible = True
                matched_pattern = version
        
        # Full semver (e.g., "1.0.0")
        elif len(cleaned_pattern_parts) == 3:
            pattern_major, pattern_minor, pattern_patch = map(int, cleaned_pattern_parts)
            if api_major == pattern_major and api_minor == pattern_minor and api_patch == pattern_patch:
                fully_compatible = True
                matched_pattern = version
    
    return fully_compatible, partially_compatible, matched_pattern

def _get_compatible_versions() -> List[str]:
    """Get compatible API versions from pyproject.toml or use defaults.
    
    Returns:
        List[str]: List of compatible version patterns
    """
    try:
        # Try to get metadata from pyproject.toml
        pkg_data = importlib.metadata.metadata('sorterpy')
        if hasattr(pkg_data, '_data') and 'tool.sorterpy.compatible_api_versions' in pkg_data._data:
            return json.loads(pkg_data._data['tool.sorterpy.compatible_api_versions'])
    except (importlib.metadata.PackageNotFoundError, AttributeError, KeyError, json.JSONDecodeError):
        pass
    
    # If we can't read from metadata or the key doesn't exist, use defaults
    return DEFAULT_COMPATIBLE_VERSIONS

def _format_version_for_display(version: str) -> str:
    """Format version pattern for display in logs.
    
    Args:
        version: Version pattern (e.g., "2", "2.1", "1.0.0")
        
    Returns:
        str: Formatted version for display (e.g., "2.x", "2.1.x", "1.0.0")
    """
    parts = version.split('.')
    
    # Extract just the numeric parts for counting
    numeric_parts = []
    for part in parts:
        match = re.match(r'^\d+', part)
        if match:
            numeric_parts.append(match.group(0))
    
    # Format based on number of parts
    if len(numeric_parts) == 1:
        return f"{parts[0]}.x"
    elif len(numeric_parts) == 2:
        return f"{parts[0]}.{parts[1]}.x"
    else:
        return version

class Sorter:
    """Main client for the Sorter API."""
    
    def __init__(self, api_key: str, base_url: str = "https://sorter.social", options: Optional[Dict] = None):
        """Initialize the Sorter client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the Sorter API
            options: Dictionary of client options
                - vote_magnitude: "equal" (-50 to 50) or "positive" (0 to 100), default "equal"
                - verbose: If True, enables detailed logging, default False
                - quiet: If True, reduces logging to warnings and errors, default False
                - compatibility_warnings: If True, show API version compatibility warnings, default True
                - debug_http_full: If True, log complete HTTP payloads; if False, truncate large payloads, default False
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client()
        self.client.headers.update({
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        })
        
        # Set default options
        self._options = {
            "vote_magnitude": "equal",
            "verbose": False,
            "quiet": False,
            "compatibility_warnings": True,
            "debug_http_full": False
        }
        
        # Update with user-provided options
        if options:
            self._options.update(options)
            
        # Configure logging based on options
        self._configure_logging()
        
        logger.debug(f"Sorter SDK initialized with base URL: {self.base_url}")
        logger.debug(f"Options: {self._pretty_json(self._options)}")
        
        # Check API version compatibility
        self._check_api_compatibility()
    
    def _check_api_compatibility(self):
        """Check if connected API version is compatible with this SDK."""
        # Check if compatibility warnings are explicitly disabled
        if self._options["compatibility_warnings"] is False:
            logger.debug("API compatibility checking is disabled")
            return
            
        try:
            # Get API version from health endpoint
            response = self.client.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                health_data = response.json()
                api_version = health_data.get("version")
                
                if api_version:
                    compatible_versions = _get_compatible_versions()
                    fully_compatible, partially_compatible, matched_pattern = _is_version_compatible(api_version, compatible_versions)
                    
                    # Get the best version (last in the list)
                    best_version = compatible_versions[-1] if compatible_versions else None
                    
                    # Format versions for display
                    display_versions = [_format_version_for_display(v) for v in compatible_versions]
                    display_best = _format_version_for_display(best_version) if best_version else None
                    
                    # Determine if warnings should be shown (considering quiet and verbose options)
                    # If compatibility_warnings option is explicitly set, respect it first
                    show_warnings = self._options["compatibility_warnings"]
                    
                    # Log compatibility info always
                    if not (fully_compatible or partially_compatible):
                        # Not compatible at all
                        if show_warnings:
                            logger.warning(
                                f"Connected API version '{api_version}' may not be compatible with this SDK. "
                                f"Supported versions: {', '.join(display_versions)}"
                            )
                        else:
                            logger.debug(
                                f"Connected API version '{api_version}' may not be compatible with this SDK. "
                                f"Supported versions: {', '.join(display_versions)}"
                            )
                    elif partially_compatible and not fully_compatible:
                        # Partially compatible (matched major version only)
                        if show_warnings:
                            logger.warning(
                                f"Connected API version '{api_version}' is partially compatible with this SDK. "
                                f"For best experience, consider using API version {display_best}."
                            )
                        else:
                            logger.debug(
                                f"Connected API version '{api_version}' is partially compatible with this SDK. "
                                f"For best experience, consider using API version {display_best}."
                            )
                    else:
                        # Fully compatible
                        logger.debug(f"Connected to API version {api_version}, which is compatible with this SDK")
        except Exception as e:
            # Don't fail initialization if version check fails
            logger.debug(f"Failed to check API version compatibility: {e}")
    
    def _configure_logging(self):
        """Configure logging based on options."""
        logger.remove()
        
        if self._options["quiet"]:
            log_level = "WARNING"
        elif self._options["verbose"]:
            log_level = "DEBUG"
        else:
            log_level = "INFO"
            
        logger.add(sys.stderr, format=LOGGER_FORMAT, level=log_level)
        logger.debug(f"Log level set to {log_level}")
    
    def _pretty_json(self, obj: Any) -> str:
        """Format object as pretty JSON string for logging.
        
        Args:
            obj: Object to format
            
        Returns:
            str: Pretty formatted JSON string
        """
        try:
            # Convert to JSON first
            json_str = json.dumps(obj, indent=2, sort_keys=True)
            
            # If debug_http_full is enabled, return the full JSON
            if self._options.get("debug_http_full", False):
                return json_str
            
            # Otherwise, truncate large arrays/objects for readability
            try:
                parsed = json.loads(json_str)
                return self._truncate_large_payload(parsed)
            except (json.JSONDecodeError, TypeError):
                return json_str  # Fall back to full string if truncation fails
                
        except (TypeError, ValueError):
            return str(obj)
    
    def _truncate_large_payload(self, obj: Any, threshold: int = 10) -> str:
        """Truncate large arrays and objects in JSON data.
        
        Args:
            obj: Object to truncate
            threshold: Maximum number of items before truncation
            
        Returns:
            str: Truncated JSON string
        """
        if isinstance(obj, list) and len(obj) > threshold:
            # For lists, show first 3, ellipsis, last 3
            truncated = obj[:3] + [f"... ({len(obj) - 6} more items) ..."] + obj[-3:]
            return json.dumps(truncated, indent=2, sort_keys=True)
        elif isinstance(obj, dict):
            # For dictionaries, truncate large values
            truncated = {}
            for key, value in obj.items():
                if isinstance(value, list) and len(value) > threshold:
                    truncated[key] = value[:3] + [f"... ({len(value) - 6} more items) ..."] + value[-3:]
                elif isinstance(value, dict):
                    truncated[key] = json.loads(self._truncate_large_payload(value, threshold))
                else:
                    truncated[key] = value
            return json.dumps(truncated, indent=2, sort_keys=True)
        else:
            # For other types, just convert to JSON
            return json.dumps(obj, indent=2, sort_keys=True)
    
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
        
        # Reconfigure logging if verbose or quiet options changed
        if "verbose" in kwargs or "quiet" in kwargs:
            self._configure_logging()
            
        logger.debug(f"Options updated: {self._pretty_json(self._options)}")
        return self._options
    
    def _convert_magnitude_to_backend(self, magnitude: int) -> int:
        """Convert magnitude from client scale to backend scale.
        
        Args:
            magnitude: Magnitude in client scale
            
        Returns:
            int: Magnitude in backend scale (0-100)
        """
        if self._options["vote_magnitude"] == "equal":
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
        if self._options["vote_magnitude"] == "equal":
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
        
        # Log request details if verbose
        logger.debug(f"Request: {method} {url}")
        if "params" in kwargs:
            logger.debug(f"Request params: {self._pretty_json(kwargs['params'])}")
        if "json" in kwargs:
            logger.debug(f"Request body: {self._pretty_json(kwargs['json'])}")
            
        response = self.client.request(method, url, **kwargs)
        
        # Log response details if verbose
        logger.debug(f"Response status: {response.status_code}")
        if self._options["verbose"]:
            try:
                logger.debug(f"Response body: {self._pretty_json(response.json())}")
            except Exception:
                logger.debug(f"Response body: {response.text}")
        
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP Error: {e.response.status_code} for {method} {url}"
            try:
                error_data = e.response.json()
                error_msg += f" - {self._pretty_json(error_data)}"
            except Exception:
                error_msg += f" - {e.response.text}"
            
            logger.error(error_msg)
            
            if not self._options["quiet"]:
                raise
            else:
                # In quiet mode, just log the error and return empty dict
                return {}
        
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
        
        # If the tag exists, return a Tag instance with the existing data
        if response.get("exists"):
            logger.debug(f"Tag '{title}' already exists with ID {response.get('id')}")
            return Tag(self, response)
        
        # Otherwise, create a new tag
        payload = {
            "title": title,
            "description": description,
            "unlisted": unlisted
        }
        
        # Only include namespace in payload if explicitly provided
        if namespace:
            payload["namespace"] = namespace
        
        logger.info(f"Creating new tag: '{title}'")
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
    
    def attribute(self, title: str, description: str = "") -> "Attribute":
        """Get an existing attribute or create a new one if it doesn't exist.
        
        Uses the /api/attribute/exists endpoint to efficiently check if the attribute exists.
        
        Args:
            title: Title of the attribute
            description: Optional description (used only if creating a new attribute)
            
        Returns:
            Attribute: Existing or new attribute instance
        """
        # Check if attribute exists
        try:
            response = self._request("GET", f"/api/attribute/exists?title={title}")
            # If we get here, the attribute exists
            if response.get("exists", False) and "id" in response:
                logger.debug(f"Attribute '{title}' already exists with ID {response.get('id')}")
                # Get the attribute by ID
                attr_response = self._request("GET", f"/api/attribute?id={response.get('id')}")
                if attr_response and "attributes" in attr_response and len(attr_response["attributes"]) > 0:
                    return Attribute(self, attr_response["attributes"][0])
        except httpx.HTTPStatusError:
            # 404 means attribute doesn't exist, continue to creation
            logger.debug(f"Attribute '{title}' doesn't exist, will create")
        
        # Create the attribute if it doesn't exist or we couldn't retrieve it
        return self.create_attribute(title, description)
        
    def vote(self, left_item: "Item", magnitude_or_right_item: Union[int, "Item"], right_item_or_magnitude: Union["Item", int], attribute: Optional[Union[int, "Attribute"]] = None) -> "Vote":
        """Record a vote between two items.
        
        Supports two parameter orderings:
        1. vote(left_item, magnitude, right_item)
        2. vote(left_item, right_item, magnitude)
        
        Args:
            left_item: Left item in comparison
            magnitude_or_right_item: Either the magnitude (-50 to 50 or 0 to 100) or the right item
            right_item_or_magnitude: Either the right item or the magnitude
            attribute: Optional attribute ID or Attribute object for this vote
            
        Returns:
            Vote: Recorded vote instance
        """
        # Determine parameter order
        if isinstance(magnitude_or_right_item, int) and isinstance(right_item_or_magnitude, Item):
            # First ordering: vote(left_item, magnitude, right_item)
            magnitude = magnitude_or_right_item
            right_item = right_item_or_magnitude
            logger.debug("Using first parameter ordering: vote(left_item, magnitude, right_item)")
        elif isinstance(magnitude_or_right_item, Item) and isinstance(right_item_or_magnitude, int):
            # Second ordering: vote(left_item, right_item, magnitude)
            right_item = magnitude_or_right_item
            magnitude = right_item_or_magnitude
            logger.debug("Using second parameter ordering: vote(left_item, right_item, magnitude)")
        else:
            raise TypeError("Invalid parameter types. Expected either (Item, int, Item) or (Item, Item, int).")
        
        # Ensure both items belong to the same tag
        if left_item.tag.id != right_item.tag.id:
            raise ValueError("Both items must belong to the same tag")
            
        # Get the tag and use its vote method
        tag = left_item.tag
        
        # Validate magnitude based on scale
        if self._options["vote_magnitude"] == "equal":
            if not (-50 <= magnitude <= 50):
                raise ValueError("Magnitude must be between -50 and 50.")
            backend_magnitude = self._convert_magnitude_to_backend(magnitude)
            logger.debug(f"Using 'equal' scale: {magnitude} -> {backend_magnitude}")
        else:
            if not (0 <= magnitude <= 100):
                raise ValueError("Magnitude must be between 0 and 100.")
            backend_magnitude = magnitude
            logger.debug(f"Using 'positive' scale: {magnitude}")
        
        # Handle attribute parameter
        if attribute is None:
            attribute_id = 0  # Default attribute ID is 0
        elif isinstance(attribute, Attribute):
            attribute_id = attribute.id
        elif isinstance(attribute, int):
            attribute_id = attribute
        else:
            raise TypeError("Invalid attribute type. Expected Attribute or int.")
        
        payload = {
            "left_item_id": left_item.id,
            "right_item_id": right_item.id,
            "magnitude": backend_magnitude,
            "tag_id": tag.id,
            "attribute": attribute_id
        }
        
        vote_info = {
            "left_item": {"id": left_item.id, "title": left_item.title},
            "right_item": {"id": right_item.id, "title": right_item.title},
            "magnitude": magnitude,
            "backend_magnitude": backend_magnitude,
            "attribute": attribute_id
        }
        logger.debug(f"Voting details: {self._pretty_json(vote_info)}")
        
        response = self._request("POST", "/api/vote", json=payload)
        return Vote(tag, response)


class Tag:
    """Represents a tag in Sorter."""
    
    def __init__(self, sorter: Sorter, data: Dict):
        """Initialize a Tag instance.
        
        Args:
            sorter: Sorter client instance
            data: Tag data from the API
        """
        self.client = sorter
        self.id = data.get("id")
        self.title = data.get("title")
        self.slug = data.get("slug")
        self.description = data.get("description", "")
        self.unlisted = data.get("unlisted", False)
        self.domain_pk = data.get("domain_pk")
        self.domain_pk_namespace = data.get("domain_pk_namespace")
        self.created_at = data.get("created_at")
        self.edited_at = data.get("edited_at")
        self.owner = data.get("owner")
        
        logger.debug(f"Tag initialized: {self.title} (ID: {self.id})")
    
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
        return Tag(self.client, response)
    
    def delete(self) -> bool:
        """Delete the tag.
        
        Returns:
            bool: True if deleted successfully
        """
        response = self.client._request("DELETE", f"/api/tag?id={self.id}")
        return response.get("deleted", False)
    
    def item(self, title: Optional[str] = None, body: str = "") -> Union["Item", List["Item"]]:
        """Create a new item or update an existing one in this tag.
        
        Args:
            title: Item title (if None, returns all items)
            body: Item body
            
        Returns:
            Union[Item, List[Item]]: New/updated item or list of all items if title=None
        """
        # If title is None, return all items in the tag
        if title is None:
            # Get rankings to access sorted and unsorted items
            rankings = self.rankings()
            
            # Combine sorted and unsorted items
            all_items = rankings.sorted() + rankings.unsorted()
            
            # Return unique items (in case there are duplicates)
            return list({item.id: item for item in all_items}.values())
            
        # We'll need to check existing items to see if one with this title or slug exists
        items = self.list_items()
        
        # First check by title (exact match)
        existing_item = next((item for item in items if item.title == title), None)
        
        # If not found by title, try to find by slug
        if not existing_item:
            # Simple approximation of slugification - actual implementation may vary
            expected_slug = title.lower().replace(' ', '-')
            existing_item = next((item for item in items if item.slug == expected_slug), None)
            if existing_item:
                logger.debug(f"Found existing item by slug: {existing_item.title} (slug: {existing_item.slug})")
        
        payload = {
            "title": title,
            "body": body,
            "tag_id": self.id
        }
        
        # If item exists, include its ID in the payload
        if existing_item:
            payload["id"] = existing_item.id
            logger.debug(f"Updating existing item: {existing_item.title} (ID: {existing_item.id})")
        else:
            logger.debug(f"Creating new item: {title}")
        
        response = self.client._request("POST", "/api/item", json=payload)
        
        # TODO: we need to handle the case where item is added to multiple tags returning multiple items, but not right now
        # Handle case where API returns a list of items
        if isinstance(response, list):
            if response:  # If the list is not empty
                response = response[0]  # Take the first item
            else:
                raise ValueError(f"API returned empty list when creating/updating item '{title}'")
                
        return Item(self, response)
    
    def list_items(self) -> List["Item"]:
        """List all items in the tag.
        
        Returns:
            List[Item]: List of item instances
        """
        # According to the API spec, we need to get the feed for this tag
        response = self.client._request("GET", f"/api/feed?tag_id={self.id}")
        
        # TODO: remove this once the API is updated
        # Handle case where response is an empty list for new tags
        if isinstance(response, list):
            return []
            
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
        attr = self.client.attribute(title, description)
        return attr.id

    def vote(self, left_item: "Item", magnitude_or_right_item: Union[int, "Item"], right_item_or_magnitude: Union["Item", int], attribute: Optional[Union[int, "Attribute"]] = None) -> "Vote":
        """Record a vote between two items in this tag.
        
        Supports two parameter orderings:
        1. vote(left_item, magnitude, right_item)
        2. vote(left_item, right_item, magnitude)
        
        Args:
            left_item: Left item in comparison
            magnitude_or_right_item: Either the magnitude (-50 to 50 or 0 to 100) or the right item
            right_item_or_magnitude: Either the right item or the magnitude
            attribute: Optional attribute ID or Attribute object for this vote
            
        Returns:
            Vote: Recorded vote instance
        """
        # Determine parameter order
        if isinstance(magnitude_or_right_item, int) and isinstance(right_item_or_magnitude, Item):
            # First ordering: vote(left_item, magnitude, right_item)
            magnitude = magnitude_or_right_item
            right_item = right_item_or_magnitude
            logger.debug("Using first parameter ordering: vote(left_item, magnitude, right_item)")
        elif isinstance(magnitude_or_right_item, Item) and isinstance(right_item_or_magnitude, int):
            # Second ordering: vote(left_item, right_item, magnitude)
            right_item = magnitude_or_right_item
            magnitude = right_item_or_magnitude
            logger.debug("Using second parameter ordering: vote(left_item, right_item, magnitude)")
        else:
            raise TypeError("Invalid parameter types. Expected either (Item, int, Item) or (Item, Item, int).")
        
        # Validate items belong to this tag
        if left_item.tag.id != self.id or right_item.tag.id != self.id:
            raise ValueError("Both items must belong to this tag.")
        
        # Validate magnitude based on scale
        if self.client._options["vote_magnitude"] == "equal":
            if not (-50 <= magnitude <= 50):
                raise ValueError("Magnitude must be between -50 and 50.")
            backend_magnitude = self.client._convert_magnitude_to_backend(magnitude)
            logger.debug(f"Using 'equal' scale: {magnitude} -> {backend_magnitude}")
        else:
            if not (0 <= magnitude <= 100):
                raise ValueError("Magnitude must be between 0 and 100.")
            backend_magnitude = magnitude
            logger.debug(f"Using 'positive' scale: {magnitude}")
        
        # Handle attribute parameter
        if attribute is None:
            attribute_id = 0  # Default attribute ID is 0
        elif isinstance(attribute, Attribute):
            attribute_id = attribute.id
        elif isinstance(attribute, int):
            attribute_id = attribute
        else:
            raise TypeError("Invalid attribute type. Expected Attribute or int.")
        
        payload = {
            "left_item_id": left_item.id,
            "right_item_id": right_item.id,
            "magnitude": backend_magnitude,
            "tag_id": self.id,
            "attribute": attribute_id
        }
        
        vote_info = {
            "left_item": {"id": left_item.id, "title": left_item.title},
            "right_item": {"id": right_item.id, "title": right_item.title},
            "magnitude": magnitude,
            "backend_magnitude": backend_magnitude,
            "attribute": attribute_id
        }
        logger.debug(f"Voting details: {self.client._pretty_json(vote_info)}")
        
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

    def find_item_by_slug(self, slug: str) -> Optional["Item"]:
        """Find an item by its slug.
        
        Args:
            slug: The slug to search for
            
        Returns:
            Optional[Item]: The item if found, None otherwise
        """
        items = self.list_items()
        return next((item for item in items if item.slug == slug), None)

    def get_or_create_item(self, title: str, body: str = "") -> "Item":
        """Get an existing item by title or slug, or create a new one if it doesn't exist.
        
        Args:
            title: Item title
            body: Item body (used only if creating a new item)
            
        Returns:
            Item: Existing or new item instance
            
        Examples:
            >>> # Get existing item or create new one
            >>> item = tag.get_or_create_item("A")
            
            >>> # Create new item with body content
            >>> item = tag.get_or_create_item("B", "This is the letter B")
        """
        # First check by title
        items = self.list_items()
        existing_item = next((item for item in items if item.title == title), None)
        
        # If not found by title, try to find by slug
        if not existing_item:
            # Simple approximation of slugification
            expected_slug = title.lower().replace(' ', '-')
            existing_item = next((item for item in items if item.slug == expected_slug), None)
        
        # If item exists, return it
        if existing_item:
            logger.debug(f"Found existing item: {existing_item.title} (ID: {existing_item.id})")
            return existing_item
        
        # Otherwise, create a new item
        logger.debug(f"Creating new item: {title}")
        return self.item(title, body)


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
        logger.debug(f"Item initialized: {self.title} (ID: {self.id})")
    
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
        logger.debug(f"Vote initialized: ID {self.id} between items {self.left_item_id} and {self.right_item_id}")
    
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
        logger.debug(f"Attribute initialized: ID {self.id} with title {self.title}")


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
        
        logger.debug(f"Rankings initialized for tag {tag.title} with {len(self._sorted_items)} sorted items")
    
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
