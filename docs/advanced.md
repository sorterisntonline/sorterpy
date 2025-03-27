# Advanced Usage

## Working with Attributes

Manage multiple voting dimensions:

```python
# Create attribute
quality = sorter.create_attribute("quality", "Quality metric")

# Vote with attribute
tag.vote(item1, item2, 25, attribute=quality.id)

# Get attribute-specific rankings
quality_rankings = tag.rankings(attribute="quality")
```

## Custom Vote Magnitudes

Use different voting scales:

```python
# Equal scale (-50 to 50)
sorter = Sorter(api_key="key", options={"vote_magnitude": "equal"})

# Positive scale (0 to 100)
sorter = Sorter(api_key="key", options={"vote_magnitude": "positive"})
```

## Error Handling

Handle API errors:

```python
from sorterpy.exceptions import SorterAPIError

try:
    tag = sorter.tag("New Tag")
except SorterAPIError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
```

## Batch Operations

Efficiently manage multiple items:

```python
# Create multiple items
items = [
    tag.item(f"Item {i}") for i in range(10)
]

# Get batch rankings
rankings = tag.rankings()
sorted_items = rankings.sorted()
```