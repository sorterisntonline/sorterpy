# First part of the file remains the same until the Sorter class methods

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

# Tag class methods to add:

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

# Item class methods to add:

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

# Attribute class methods to add:

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