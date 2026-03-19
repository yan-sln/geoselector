# GeoSelector

## 1. General Architecture

The repository is organized into three main modules:

```
geo_selector/
  api/          # Adapters for various geographic APIs
  core/         # Core logic and entities
  factory/      # Factories to create entity selectors
```

* **`api`**: contains concrete implementations of strategies to access geographic data (Gouv.fr and IGN).
* **`core`**: the heart of the system, with entities, services, selectors, and the **HandlerRegistry** that provides operation handlers.
* **`factory`**: allows easy creation of typed selectors with a given API and strategy.

---

## 2. `core`: Functional Core

### a) Entities (`entities.py`)

* Defines the abstract class `GeoEntity` with a `from_dict` interface.
* Concrete subclasses represent geographic entities:
  * `Municipality` → communes
  * `Department` → departments
  * `Region` → regions
  * `Parcel` → cadastral parcels
  * `Section` → cadastral sections
* Each entity declares `API_ENDPOINT`, enabling automatic registration in `EntityRegistry`.

### b) Registry (`registry.py`)

* `EntityRegistry` stores entities by their `API_ENDPOINT`.
* Methods:
  * `register` – add an entity
  * `get` – retrieve an entity by its endpoint
  * `list_entities` – list all registered entities
* Facilitates dynamic linking between entities and API strategies.

### c) Service (`service.py`)

* `GeoService`: high‑level service to query any API via an `ApiStrategy`.
* Methods:
  * `search_entities(entity_class, text)`
  * `fetch_entity_geometry(entity_class, code)`
  * `list_entities(entity_class, **filters)` – generic search using the ``search`` block in the JSON.
  * `list_search(entity_class, **filters)` – uses the ``list_search`` block when available.
  * `get_entity_details(entity_class, code)`

### d) Selectors (`selector.py`)

* `EntitySelector`: typed interface for selecting entities.
* `EntitySelectorImpl`: generic implementation that uses `GeoService` for searches and geometry retrieval.
* Provides strong typing, e.g., an `EntitySelector<Municipality>` always returns `Municipality` objects.

### e) Strategy (`strategy.py`)

* Interface `ApiStrategy` standardizes API calls.
* Abstract methods:
  * `search(endpoint, text)`
  * `fetch_geometry(endpoint, code)`
  * `fetch_details(endpoint, code)`

---

## 3. `api`: Strategy Implementations

### a) `gouvfr.py`

* Implements `GouvFrApiStrategy` for the `geo.api.gouv.fr` API.
* Complete methods with specific formatting for each entity type.
* Error handling via `try/except` and simple logging (`print`).
* Supports:
  * Communes, departments, regions
  * Parcels and sections

### b) `ign.py`

* Implements `IGNApiStrategy`.
* Currently minimal: methods only `print` and return empty structures.
* Needs implementation to query the real IGN API.

---

## 4. Factory: Creating Selectors

### `selector_factory.py`

* `SelectorFactory` provides a simple interface to create typed selectors:

```python
selector = SelectorFactory.create_selector(Municipality, "GOUVFRApiStrategy")
```

* How it works:
  1. Retrieves the API strategy from `STRATEGIES`.
  2. Instantiates `GeoService` with that strategy.
  3. Returns an `EntitySelectorImpl` typed with the given entity class.

---

## 5. Public API (`__init__.py`)

* The `geo_selector` package directly exposes:
  * `core_service` – alias for `GeoService`
  * `selector_factory` – alias for `SelectorFactory`

* Users can easily create a service or selector without navigating sub‑modules.

---

## 6. Strengths

* Clear layered architecture: API ↔ Service ↔ Selector ↔ Entity.
* Strong typing via `Generic[T]`.
* Extensible: adding a new API or entity is straightforward through `ApiStrategy` and `GeoEntity`.
* Factory simplifies selector creation.

---

## 7. Areas for Improvement

1. **IGNApiStrategy**: needs proper implementation.
2. **Logging and error handling**: replace `print` statements with a proper logger.
3. **Unit tests**: currently missing; essential for validating API strategies and entity mapping.
4. **Pagination / limits**: `GouvFrApiStrategy.search` currently limits results to a fixed 10.
5. **Data validation**: optional fields (`commune_code`, `section`, `region_code`, etc.) are now robustly validated via `_ensure_fields` in `core/entities.py`, raising explicit `ValueError` on inconsistencies.

---

## 8. Functional Summary

You have a **framework for selecting geographic entities**.
You can:

```python
from geo_selector import selector_factory
from geo_selector.core.entities import Municipality

selector = selector_factory.create_selector(Municipality, "GOUVFRApiStrategy")
results = selector.select("Paris")
geometry = selector.get_geometry(results[0].code)
details = selector.get_details(results[0].code)
```

The structure is ready for adding more data sources, entity types, and automating geographic workflows.

---

_Documentation generated automatically_