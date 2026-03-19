# Implementation Checklist for GeoSelector

This document enumerates everything that needs to be implemented for the **GeoSelector** project based on the current design, UML diagram, and JSON configuration. It is intended for the next developer/agent to have a complete, step‑by‑step guide so that nothing is missed.

---

## 1️⃣ Core Components

### 1.1 RequestTemplate (`core/config.py`)
- [ ] Create a dataclass `RequestTemplate` with the constant fields `SERVICE`, `VERSION`, `REQUEST`, `OUTPUTFORMAT`.
- [ ] Implement `build(self, typename: str, propertyname: str, cql: str | None = None, **extra: Any) -> dict` that returns the full parameter dictionary for `urllib.parse.urlencode`.
- [ ] Add comprehensive docstrings and type hints.
- [ ] Write unit tests covering:
    - building a URL with only required fields,
    - adding optional `extra` parameters (e.g., `DISTINCT`).

### 1.2 ApiClient (`core/api_client.py`)
- [ ] Load `config/apis.json` in `__init__(self, config_path: str)` and store the JSON dict.
- [ ] Instantiate a `RequestTemplate` from the `common` section.
- [ ] Implement private method `_build_url(entity: str, operation: str, **values) -> str`:
    - Retrieve the entity definition from the JSON.
    - Resolve the operation block (`search_by_name`, `search_by_code`, `search`, `geometry`, `list_sections`).
    - Replace placeholders (`{value}`, `{code_insee}`, `{section}`, `{feuille}`, `{feature_id}`, `{idu_parcel}`) with the supplied `values`.
    - Append pagination/limit parameters when the operation supports it (e.g., `COUNT`).
- [ ] Implement `_cached_get(url: str) -> dict` using `@lru_cache(maxsize=256)` for caching.
- [ ] Implement public `search(entity: str, mode: str, **values) -> list[dict]` that:
    - Calls `_build_url` with the appropriate operation.
    - Calls `_cached_get` and returns the list of feature dictionaries.
- [ ] Implement public `fetch_geometry(entity: str, **values) -> dict | None` that:
    - Calls `_build_url` with the `geometry` operation.
    - Returns the first feature's geometry (or `None`).
- [ ] Add proper logging (`debug` for request building, `info` for successful calls, `error` for exceptions).
- [ ] Write integration tests that mock HTTP responses (using `responses` or `requests‑mock`).

### 1.3 GeoEntity (`core/entities.py`)
- [ ] Define abstract base class `GeoEntity` with attributes:
    - `code: str`
    - `_geometry: dict | None`
    - `_service: GeoService | None`
- [ ] Implement methods:
    - `set_service(self, service: GeoService) -> None`
    - `get_geometry(self, force: bool = False) -> dict`
    - `has_geometry(self) -> bool`
- [ ] Create concrete subclasses with **minimal attributes** derived from `config/apis.json`:
    - `Region` (`code`, `name`)
    - `Departement` (`code`, `name`)
    - `Commune` (`code`, `name`)
    - `Arrondissement` (`code_insee`, `name`, `code_arr`)
    - `Feuille` (`code_insee`, `section`, `feuille`)
    - `Parcelle` (`code_insee`, `section`, `numero`, `idu`)
    - `SubdivisionFiscale` (`gid`, `idu_parcel`, `lettre`)
- [ ] Each subclass must implement a `@classmethod from_api(cls, raw: dict) -> Self` that extracts the appropriate fields from the raw feature dict.
- [ ] Write unit tests for each subclass ensuring correct attribute extraction.

### 1.4 GeoService (`core/service.py`)
- [ ] Constructor `__init__(self, client: ApiClient)` stores the client.
- [ ] Implement `search_entities(cls: Type[GeoEntity], text: str, limit: int | None = None) -> list[GeoEntity]`:
    - Determine which operation to use (`search_by_name` or `search_by_code`) based on the entity type and the length of `text`.
    - Pass `limit` only for entities that support pagination (Region, Departement, Commune).
    - Convert raw dicts to entity instances via `entity_cls.from_api` and inject the service (`entity.set_service(self)`).
- [ ] Implement `fetch_entity_geometry(cls: Type[GeoEntity], code: str) -> dict` that delegates to `client.fetch_geometry`.
- [ ] Add logging for entry/exit of each method.
- [ ] Write tests covering both limited and unlimited search scenarios.

### 1.5 SelectorImpl (`core/selector.py`)
- [ ] Constructor receives `entity_cls: Type[GeoEntity]` and a `GeoService` instance.
- [ ] `select(self, text: str) -> list[GeoEntity]` forwards to `service.search_entities`.
- [ ] `get_geometry(self, code: str) -> dict` forwards to `service.fetch_entity_geometry`.
- [ ] Ensure the returned entities already have the service injected.
- [ ] Unit tests for selection and geometry retrieval.

### 1.6 SelectorFactory (`core/selector.py` or a new file)
- [ ] Maintain a private dict `_services: dict[str, GeoService]` keyed by the `base_url` (or a source identifier).
- [ ] `create_selector(entity_cls: Type[GeoEntity]) -> SelectorImpl`:
    - Determine the source (`base_url`) from the JSON configuration for the given entity.
    - Reuse an existing `GeoService` from `_services` or instantiate a new one (`GeoService(ApiClient(config_path))`).
    - Return a new `SelectorImpl` with the selected service.
- [ ] Provide a `reset()` method to clear the cache (useful for tests).
- [ ] Write tests ensuring the same service instance is reused for the same source.

## 2️⃣ Configuration
- [ ] Ensure `config/apis.json` follows the structure already defined (base_url, common, entities).
- [ ] Add a validation script (`scripts/validate_config.py`) that checks:
    - All required keys (`TYPENAME`, operation blocks) exist for each entity.
    - Place‑holder names in `CQL_FILTER` match the keys used in the code.
    - No duplicate `TYPENAME` values.
- [ ] Write a unit test for the validator.

## 3️⃣ Logging & Error Handling
- [ ] Central logging configuration (`logging_config.py`) with a formatter that includes timestamp, level, module, and message.
- [ ] Define a custom exception `ApiError` in `core/api_client.py` that wraps network errors and provides a clear message.
- [ ] Ensure all public methods catch `ApiError` and either re‑raise or return an empty list / `None` as appropriate.

## 4️⃣ Caching
- [ ] The `ApiClient` already uses `@lru_cache` for GET requests.
- [ ] Verify that geometry caching works across multiple entity instances (same `code`).
- [ ] Add optional configuration to control cache size via `config/apis.json` (e.g., `"cache_size": 256`).

## 5️⃣ Tests
- [ ] **Unit tests** for each class (use `pytest`).
- [ ] **Integration tests** that spin up a mock WFS server (or use recorded HTTP fixtures) to verify end‑to‑end behavior.
- [ ] **Coverage** target ≥ 90 %.
- [ ] Place all tests under the `tests/` directory, mirroring the existing `test_*.py` naming convention.

## 6️⃣ Documentation
- [ ] Update `README.md` with a quick‑start guide showing how to:
    - Create a selector via `SelectorFactory.create_selector(Commune)`.
    - Perform a search and retrieve geometry.
- [ ] Add a section describing the JSON configuration format.
- [ ] Include the PlantUML diagram (`architecture.puml`) with a link.
- [ ] Document the public API of `GeoService`, `SelectorImpl`, and `SelectorFactory`.

## 7️⃣ CI / Linting
- [ ] Add a GitHub Actions workflow that runs:
    - `flake8` / `black` for code style.
    - `mypy` for static typing.
    - `pytest` with coverage.
- [ ] Ensure the workflow fails on linting or test failures.

## 8️⃣ Packaging
- [ ] Verify `requirements.txt` includes all runtime dependencies (`requests`, `pydantic` optional, `pytest`, `responses`).
- [ ] Add a `setup.cfg` or `pyproject.toml` if needed for packaging.

---

### Final Note for the Implementer

Follow the order above: start with the **core components** (template, client, entities, service, selector, factory), then **configuration validation**, **logging/error handling**, **caching**, **tests**, **documentation**, and finally **CI/packaging**.  Each step builds on the previous one, ensuring a solid foundation before moving to higher‑level concerns.

Feel free to adjust naming conventions (e.g., `RequestTemplate` → `WfsRequestTemplate`) as long as the responsibilities remain clearly separated.

