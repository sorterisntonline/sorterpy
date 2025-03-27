# API Reference

## Sorter Client

### Initialization

```python
Sorter(api_key: str, base_url: str = "https://sorter.social", options: dict = None)
```

### Methods

#### tag
Create or retrieve a tag.
```python
tag(title: str, description: str = None) -> Tag
```

#### create_attribute
Create a new attribute.
```python
create_attribute(title: str, description: str = None) -> Attribute
```

#### get_attribute
Retrieve an existing attribute.
```python
get_attribute(title: str) -> Attribute
```

#### list_attributes
List all attributes.
```python
list_attributes() -> List[Attribute]
```

## Tag Class

### Methods

#### item
Create or retrieve an item in the tag.
```python
item(title: str, description: str = None) -> Item
```

#### vote
Vote on a pair of items.
```python
vote(item1: Item, item2: Item, magnitude: int, attribute: str = None)
```

#### rankings
Get tag rankings.
```python
rankings() -> Rankings
```

## Rankings Class

### Methods

#### sorted
Get sorted items.
```python
sorted(attribute: str = None) -> List[Item]
```

#### unsorted
Get unsorted items.
```python
unsorted() -> List[Item]
```

#### pair
Get next voting pair.
```python
pair() -> Tuple[Item, Item]
```

#### skipped
Get skipped items.
```python
skipped() -> List[Item]
```

#### votes
Get all votes.
```python
votes() -> List[Vote]
```

#### users_who_voted
Get users who voted.
```python
users_who_voted() -> List[str]
```