# Contributing

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/sorterpy.git
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
pytest
```

## Documentation

Update docs in the `docs/` directory. Build locally:

```bash
cd docs
make html
```

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Update CHANGELOG.md
4. Submit PR with description of changes