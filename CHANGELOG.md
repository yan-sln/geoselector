# CHANGELOG

All notable changes to this project will be documented in this file.

## [Unreleased]
- Added detailed docstrings to `GeoService` methods.
- Added detailed docstrings to `EntitySelector` methods.
- Uniformized logging levels and removed duplicate logs.
- Implemented custom `ApiError` exception and raised it in `ApiStrategy._request`.
- Updated callers to handle `ApiError` and removed unnecessary `None` checks.
- Extracted pagination logic into `ApiStrategy._paged_fetch`.
- Refactored `GouvFrApiStrategy.search` and `IGNApiStrategy.search` to use `_paged_fetch`.
- Normalized method signatures to use `limit: int | None = None` and `page: int = 1`.
- Added unit tests for error handling (`tests/test_api_error.py`).

## [0.1.0] - 2026-03-10
- Initial release with core functionality for geographic entity selection.
