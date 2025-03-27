# Changelog

## [0.2.21] - 2025-03-27

### Fixed
- Properly testing simplified workflow with SKIP-TESTS flag
- Testing workflow flag handling capability

## [0.2.20] - 2025-03-27

### Fixed
- Completely replaced workflow with simplified version
- Removed all complex condition logic
- Created direct release pipeline

## [0.2.19] - 2025-03-27

### Fixed
- Clean release attempt without skip flags
- Testing release pipeline behavior

## [0.2.18] - 2025-03-27

### Fixed
- Fixed output handling in CI workflow
- Improved debug logging for GitHub Actions
- Explicit variable handling for CI/CD flags

## [0.2.17] - 2025-03-27

### Added
- Complete workflow overhaul with more reliable flag detection
- Improved release decision making process
- Added comprehensive debugging to CI/CD pipeline

## [0.2.16] - 2025-03-27

### Added
- Enhanced CI workflow debugging
- Fixed workflow flag parsing

## [0.2.14] - 2025-03-27

### Added
- Fixed workflow issues
- Version increment for improved testing

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