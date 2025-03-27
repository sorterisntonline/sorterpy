# API Reference

This comprehensive reference documents all major components of the sorterpy SDK. Each section includes detailed explanations of methods, their parameters, return values, and common usage patterns.

## Sorter Client

The Sorter client is your main entry point to interact with the sorter.social API. It manages authentication, configuration, and provides access to all core functionality.

### Initialization

```python
Sorter(
    api_key: str,
    base_url: str = "https://sorter.social",
    options: dict = None
)
```

#### Parameters

- `api_key`: Your API authentication key from sorter.social
- `base_url`: The API endpoint URL. Use default for production or "https://staging.sorter.social" for testing
- `options`: A dictionary of configuration options:
  ```python
  {
      # Note: Deprecated - will be removed in future versions
      "vote_magnitude": "equal" | "positive",  # Vote scale type
                                              # "equal": -50 to 50
                                              # "positive": 0 to 100
      
      "verbose": bool,      # Enable detailed logging (default: False)
      "quiet": bool,        # Reduce logging to warnings/errors (default: False)
      
      "compatibility_warnings": bool,  # Show API version warnings (default: True)
      "debug_http_full": bool         # Show complete HTTP payloads (default: False)
  }
  ```

#### Returns
Returns a configured Sorter client instance.

#### Example
```python
sorter = Sorter(
    api_key="your-api-key",
    base_url="https://sorter.social",
    options={
        "verbose": True,
        "compatibility_warnings": True
    }
)
```

### Methods

#### tag
Creates a new tag or retrieves an existing one.

```python
tag(
    title: str,
    description: str = None
) -> Tag
```

The `title` parameter serves as a unique identifier for the tag. If a tag with the given title exists, it will be retrieved; otherwise, a new tag is created.

#### create_attribute
Creates a new attribute for multi-dimensional voting.

```python
create_attribute(
    title: str,
    description: str = None
) -> Attribute
```

Attributes allow you to capture different aspects or dimensions of comparison between items. For example, you might have attributes for "quality", "relevance", and "creativity".

#### get_attribute
Retrieves an existing attribute.

```python
get_attribute(
    title: str
) -> Attribute
```

If no attribute with the given title exists, raises a `SorterAPIError`.

#### list_attributes
Lists all available attributes.

```python
list_attributes() -> List[Attribute]
```

Returns a list of all attributes available to your API key.

## Tag Class

The Tag class represents a collection of items that can be sorted through voting.

### Methods

#### item
Creates a new item or retrieves an existing one within the tag.

```python
item(
    title: str,
    description: str = None
) -> Item
```

When creating items:
- Each item must have a unique title within its tag
- The description is optional but recommended for clarity
- Items are automatically assigned a unique identifier

#### get_or_create_item
A safer alternative to `item()` that explicitly handles the create/retrieve logic.

```python
get_or_create_item(
    title: str,
    description: str = None
) -> Item
```

This method is preferred over `item()` as it makes the create/retrieve behavior explicit.

#### vote
Records a vote comparing two items.

```python
vote(
    item1: Item,
    item2: Item,
    magnitude: int,
    attribute: str = None
)
```

Note: The current flexible parameter ordering (e.g., `vote(item1, magnitude, item2)`) is deprecated. Always use the order shown above.

Parameters:
- `item1`: The first item in the comparison
- `item2`: The second item in the comparison
- `magnitude`: The strength and direction of preference
- `attribute`: Optional attribute ID for multi-dimensional voting

#### rankings
Retrieves the current rankings for the tag.

```python
rankings() -> Rankings
```

Returns a Rankings object that provides access to sorted and unsorted items.

#### link
Generates a shareable URL for the tag.

```python
link() -> str
```

Returns a web URL that can be used to view the tag in a browser.

## Rankings Class

The Rankings class provides methods to access and analyze the current state of item sorting.

### Methods

#### sorted
Returns items that have received enough votes to be ranked.

```python
sorted(
    attribute: str = None
) -> List[Item]
```

The optional `attribute` parameter allows retrieving rankings for a specific voting dimension.

#### unsorted
Returns items that haven't received enough votes to be ranked.

```python
unsorted() -> List[Item]
```

#### pair
Gets the next pair of items that should be voted on.

```python
pair() -> Tuple[Item, Item]
```

The pair selection algorithm optimizes for:
- Covering all items
- Resolving close comparisons
- Validating existing rankings

#### skipped
Returns items that were skipped during voting.

```python
skipped() -> List[Item]
```

#### votes
Returns all votes recorded for the tag.

```python
votes() -> List[Vote]
```

Each Vote object contains:
- The items compared
- The vote magnitude
- Timestamp
- Attribute (if any)

#### users_who_voted
Returns a list of users who have voted on this tag.

```python
users_who_voted() -> List[str]
```

## Error Handling

The SDK uses custom exceptions for error handling:

```python
try:
    tag = sorter.tag("New Tag")
except SorterAPIError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
```

Common exceptions:
- `SorterAPIError`: General API communication errors
- `SorterAuthError`: Authentication failures
- `SorterValidationError`: Invalid input data
- `SorterNotFoundError`: Requested resource not found