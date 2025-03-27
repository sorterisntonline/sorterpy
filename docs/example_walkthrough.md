# Detailed Example Walkthrough

This guide walks through a complete example of using the sorterpy SDK to create an alphabet sorting system. We'll explore how the SDK interfaces with the sorter API and examine important implementation details.

## Setup and Initialization

The example begins with setting up the Sorter client:

```python
from sorterpy.sorterpy import Sorter
import os
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path)

sorter = Sorter(
    api_key=os.getenv('SORT_API_KEY', 'your-api-key'),
    base_url=os.getenv('SORT_BASE_URL', 'https://sorter.social'),
    options={
        "vote_magnitude": "positive",  # Note: This option is deprecated
        "verbose": True,
        "quiet": False
    }
)
```

### API Connection Details
The initialization process establishes a connection to the sorter API:
- The `api_key` authenticates your requests
- `base_url` determines the API endpoint (production or staging)
- Options configure the client behavior

## Creating and Managing Tags

Tags are the primary organizational unit in sorter:

```python
tag = sorter.tag("alphabet_uniq")
```

When this code runs:
1. The SDK sends a POST request to `/api/v2/tags`
2. If a tag with this name exists, it retrieves the existing tag
3. If not, it creates a new tag

### Item Creation and Management

The example demonstrates two methods for creating items:

```python
# Recommended method using get_or_create_item
letters = {ch: tag.get_or_create_item(ch) for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
```

This triggers:
- A GET request to check for existing items
- POST requests to create any missing items
- All items are created under the tag's scope

## Voting Implementation

The example implements a custom voting system based on letter distance:

```python
def letter_distance(a, b):
    raw_score = (ord(a.name) - ord(b.name)) * (50 / 25)
    return int(raw_score + 50)  # Convert to 0,100 range
```

### Voting Process
When a vote is made:
1. The SDK gets a pair of items using `tag.rankings().pair()`
2. Calculates the vote magnitude using `letter_distance()`
3. Submits the vote through the API

```python
left, right = tag.rankings().pair()
score = letter_distance(left, right)
sorter.vote(left, right, int(score))
```

Note: The multiple parameter orderings for the vote method (e.g., `vote(left, score, right)` vs `vote(left, right, score)`) are deprecated and will be removed in a future version.

## Working with Rankings

The example shows how to retrieve and work with rankings:

```python
# Get current sorted order
sorted_items = tag.sorted()
current_order = "".join(item.name for item in sorted_items)

# Get unsorted items
unsorted_items = tag.unsorted()
```

These operations map to:
- GET `/api/v2/tags/{tag_id}/rankings` for overall rankings
- GET `/api/v2/tags/{tag_id}/items/sorted` for sorted items
- GET `/api/v2/tags/{tag_id}/items/unsorted` for unsorted items

## Attribute Voting

The example demonstrates attribute-based voting:

```python
quality_attr = sorter.attribute("quality", "How good is this letter")
tag.vote(left, right, 25, attribute=quality_attr)
```

This creates a new dimension for voting:
1. Creates or retrieves the attribute via `/api/v2/attributes`
2. Associates votes with this attribute
3. Allows for multiple ranking dimensions on the same items

## Runtime Configuration

The example shows how to modify client behavior at runtime:

```python
sorter.options(vote_magnitude="positive", verbose=False)
tag.vote(left, right, 75)
```

Note: The `vote_magnitude` option is deprecated and will be removed in a future version. All votes will use a standardized scale.

## URL Generation

The example demonstrates generating shareable URLs:

```python
tag_link = tag.link()
item_link = item_a.link()
```

These methods construct URLs that map to the sorter web interface, allowing for easy sharing and viewing of tags and items.