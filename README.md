# sorterpy

[![PyPI version](https://img.shields.io/pypi/v/sorterpy.svg)](https://pypi.python.org/pypi/sorterpy)
[![Build and Release Status](https://github.com/sorterisntonline/sorterpy/actions/workflows/release_package.yml/badge.svg)](https://github.com/sorterisntonline/sorterpy/actions/workflows/release_package.yml)
[![Documentation Status](https://readthedocs.org/projects/sorterpy/badge/?version=latest)](https://sorterpy.readthedocs.io/en/latest/?version=latest)

The official Python SDK for sorter.social's seamless data labeling solutions for any AI/ML workflow.

* Free software: MIT license
* Documentation: https://sorterpy.readthedocs.io

> _Created by [`@zudsniper`](https://github.com/zudsniper) for [`sorter`](https://github.com/sorterisntonline)._   

## Installation

```bash
pip install sorterpy
```

## API Compatibility

This SDK is compatible with the following sorter.social API versions:
- 2.x
- 2.1.x
- 2.1.1

## Basic Usage

```python
from sorterpy import Sorter

# Initialize the client with options
sorter = Sorter(
    api_key="your-api-key",
    base_url="http://localhost:3000",
    options={
        "vote_magnitude": "equal",  # Use -50 to 50 scale (default)
        "verbose": False,           # Disable detailed logging (default)
        "quiet": False,             # Don't suppress logs (default)
        "compatibility_warnings": True  # Show API version compatibility warnings (default)
        "debug_http_full": False    # Truncate long http bodies when debug printing them (default)
    }
)

# Create a tag
tag = sorter.tag("My Tag", description="A tag for testing")

# Add items to the tag
item1 = tag.item("Item 1", description="First item")
item2 = tag.item("Item 2", description="Second item")

# Vote on items (flexible parameter ordering)
tag.vote(item1, item2, 25)  # Prefer item1 over item2 with magnitude 25
# OR
tag.vote(item1, 25, item2)  # Same result, different parameter order

# Get tag rankings
rankings = tag.rankings()

# Get sorted and unsorted items
sorted_items = rankings.sorted()
unsorted_items = rankings.unsorted()

# Get a voting pair
left_item, right_item = rankings.pair()
```

## Client Options

The Sorter client accepts the following options:

- `vote_magnitude`: Determines the scale for vote magnitudes
  - `"equal"` (default): Uses a scale from -50 to 50, where 0 is neutral
  - `"positive"`: Uses a scale from 0 to 100, where 50 is neutral
- `verbose`: Enables detailed logging including HTTP requests and responses
  - `False` (default): Normal logging (INFO level)
  - `True`: Detailed logging (DEBUG level)
- `quiet`: Reduces logging to only warnings and errors
  - `False` (default): Normal logging (INFO level)
  - `True`: Reduced logging (WARNING level)
- `compatibility_warnings`: Show API version compatibility warnings
  - `True` (default): Show warnings when API version might not be fully compatible
  - `False`: Suppress compatibility warnings
- `debug_http_full`: Display the entire body of HTTP request / response objects. 
  - `False` (default): Truncate long HTTP req/resp payloads.
  - `True`: Print full HTTP req/resp payloads. _(will result in very long sysout)_

Note: If both `verbose` and `quiet` are set to `True`, `quiet` takes precedence.

## Features

- Authenticate Sorter Client with API Key
- Create & Manage Tags
- Create & Utilize Items
- Vote on Pairs (of Items) within Tags
- Get Live Links to Tags or Items
- Retrieve Rankings on Tags (Elo, Sorted Items, Unsorted Items)
- Work with Multiple Attributes for Voting
- Flexible Vote Magnitude Scales[^1]
- Comprehensive Logging System
- API Version Compatibility Checking

## Working with Attributes

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
```

## Working with Rankings

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

# Get users who voted
users = rankings.users_who_voted()
```

## Logging

The SDK uses loguru for logging with a customized format:

```
12:34:56 | INFO     | sorterpy:__init__:42 - Sorter SDK initialized with base URL: https://sorter.social
```

The format includes:
- Time (HH:MM:SS)
- Log level
- Abbreviated module name, function, and line number
- Message

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [`audreyr/cookiecutter-pypackage`](https://github.com/audreyr/cookiecutter-pypackage) project template. 

[^1]: This will be removed soon. 