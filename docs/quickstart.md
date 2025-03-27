# Quick Start

## Basic Usage

Initialize the client:

```python
from sorterpy import Sorter

sorter = Sorter(
    api_key="your-api-key",
    base_url="http://localhost:3000"
)
```

## Creating Tags and Items

```python
# Create a tag
tag = sorter.tag("My Tag", description="A tag for testing")

# Add items
item1 = tag.item("Item 1", description="First item")
item2 = tag.item("Item 2", description="Second item")
```

## Voting

```python
# Vote on items
tag.vote(item1, item2, 25)  # Prefer item1 over item2
```

## Getting Rankings

```python
# Get tag rankings
rankings = tag.rankings()

# Access sorted and unsorted items
sorted_items = rankings.sorted()
unsorted_items = rankings.unsorted()

# Get next voting pair
left_item, right_item = rankings.pair()
```