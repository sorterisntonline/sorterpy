# Configuration

## Client Options

Configure the Sorter client with these options:

### Vote Magnitude (Deprecated)

```python
options = {
    "vote_magnitude": "equal"  # or "positive"
}
```

Note: The vote_magnitude option is deprecated and will be removed in a future version. All votes will use a standardized scale. Current implementations should prepare to migrate away from this option.

### Logging

```python
options = {
    "verbose": False,  # Enable detailed logging
    "quiet": False,    # Reduce logging to warnings/errors
}
```

Note: `quiet` takes precedence if both are True.

### Compatibility

```python
options = {
    "compatibility_warnings": True,  # Show API version warnings
    "debug_http_full": False        # Show full HTTP payloads
}
```

## Voting Method Parameters (Deprecated)

The current implementation allows multiple parameter orderings for the vote method:

```python
# These are currently equivalent but the flexibility is deprecated
tag.vote(left_item, right_item, magnitude)
tag.vote(left_item, magnitude, right_item)
```

Note: This parameter flexibility is deprecated and will be removed in a future version. All vote calls should use the standard ordering: `vote(left_item, right_item, magnitude)`.

## Logging Format

The SDK uses loguru with format:
```
12:34:56 | INFO | sorterpy:__init__:42 - Message
```

Components:
- Time (HH:MM:SS)
- Log level
- Module:function:line
- Message