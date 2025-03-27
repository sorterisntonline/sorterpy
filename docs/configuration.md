# Configuration

## Client Options

Configure the Sorter client with these options:

### Vote Magnitude

```python
options = {
    "vote_magnitude": "equal"  # or "positive"
}
```

- `"equal"` (default): -50 to 50 scale
- `"positive"`: 0 to 100 scale

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