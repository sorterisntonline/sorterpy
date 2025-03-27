# Changelog

## [0.2.15] - 2025-03-27

### Added
- New testing workflow for master branch
- Improved CI/CD pipeline separation between stable and master

## [0.2.14] - 2024-03-27

### Added
- Comprehensive test suite with pytest and responses
  - Tests for Tag operations (creation, retrieval, updates)
  - Tests for Item management (CRUD operations)
  - Tests for Voting functionality
  - Tests for Attribute handling
  - Tests for error conditions and edge cases
- New development dependencies for testing
  - pytest-mock for mocking
  - pytest-cov for coverage reporting
  - responses for HTTP mocking

## [0.2.13] - 2024-03-27

### Added
- New get_* methods to complement get_or_create methods
  - get_tag()
  - get_tag_by_id()
  - get_item()
  - get_item_by_id()
- Static exists() methods for Tags, Items, and Attributes
  - Tag.exists() and Sorter.exists_tag()
  - Item.exists()
  - Attribute.exists()

## [0.2.12] - 2024-03-27

### Added
- Detailed example walkthrough documentation
- Extended ReadTheDocs configuration

### Changed
- Marked vote_magnitude option as deprecated
- Marked flexible vote parameter ordering as deprecated
- Updated documentation to reflect deprecation notices
- Enhanced configuration documentation

## [0.2.11] - 2024-03-27

### Added
- Initial Markdown documentation support
- ReadTheDocs integration
- Skip release workflow option

## [0.2.10] - 2024-03-27

### Added
- Initial release
- Basic tag and item management
- Voting functionality
- Rankings retrieval
- Attribute support
- Configurable logging
- API version compatibility checks