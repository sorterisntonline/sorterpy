# SorterPy

> `WARNING` this isn't really used in favor of 'README.rst' for some reason. this will show up on GitHub though so there's that.  

A Python SDK for interacting with the Sorter API.

## Installation

```bash
pip install sorterpy
```

## Usage

### Basic Usage

```python
from sorterpy import Sorter

# Initialize the client
sorter = Sorter(api_key="your-api-key")

# Create a tag
tag = sorter.tag("My Tag", description="A tag for testing")

# Add items to the tag
item1 = tag.item("Item 1", description="First item")
item2 = tag.item("Item 2", description="Second item")

# Vote on items (flexible parameter ordering)
tag.vote(item1, item2, 25)  # Prefer item1 over item2 with magnitude 25
# OR
tag.vote(item1, 25, item2)  # Same result, different parameter order

# You can also vote directly through the sorter
sorter.vote(item1, item2, 25)  # Same flexible parameter ordering
```

### Sorting Example

```python
from sorterpy import Sorter

# Initialize API client
sorter = Sorter(api_key="your-api-key")

# Step 1: Create the tag
tag = sorter.tag("alphabet")

# Step 2: Add letters A-Z
letters = {ch: tag.item(ch) for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}

# Step 3: Sort by voting
def letter_distance(a, b):
    """Returns a vote score based on letter distance (-50 to 50)."""
    return (ord(a.name) - ord(b.name)) * (50 / 25)  # Normalize to -50,50 range

correct_order = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
votes = 0

while "".join(x.name for x in tag.sorted()) != correct_order:
    left, right = tag.rankings().pair()  # Returns ItemObjects
    score = letter_distance(left, right)
    sorter.vote(left, right, score)
    votes += 1
    print(f"Voted on {left.name} vs {right.name}: {score:.1f} ({votes} votes so far)")

print(f"Alphabet sorted in {votes} votes!")
```

### Working with Rankings

```python
# Get tag rankings
rankings = tag.rankings()

# Get sorted items
sorted_items = rankings.sorted()

# Get unsorted items
unsorted_items = rankings.unsorted()

# Get a voting pair
left_item, right_item = rankings.pair()

# Get skipped items
skipped_items = rankings.skipped()

# Get votes
votes = rankings.votes()

# Get attributes
attributes = rankings.attributes()

# Get selected attribute
selected_attr = rankings.selected_attribute()

# Get permissions
perms = rankings.permissions()

# Get users who voted
users = rankings.users_who_voted()

# Convenience methods on Tag
sorted_items = tag.sorted()
unsorted_items = tag.unsorted()
left_item, right_item = tag.pair()
```

### Working with Attributes

```python
# Create an attribute
quality_attr = sorter.create_attribute("quality", "Quality of the item")

# Get an attribute by title
attr = sorter.get_attribute("quality")

# List all attributes
attributes = sorter.list_attributes()

# Vote with an attribute
tag.vote(item1, item2, 25, attribute=quality_attr.id)

# Get sorted items by attribute
sorted_by_quality = tag.sorted(attribute="quality")

# Get unsorted items by attribute
unsorted_by_quality = tag.unsorted(attribute="quality")
```

## License

MIT 