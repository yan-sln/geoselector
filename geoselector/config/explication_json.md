# Explanation of the `apis.json` file

The **[`config/apis.json`](config/apis.json:1)** defines the configuration for calls to the WFS (Web Feature Service) used by the *geoselector* project. It contains:

1. **`base_url`** – Base URL of the service.
2. **`api_type`** – Type of API (here `wfs`).
3. **`common`** – Parameters common to all requests (service, version, request type, output format).
4. **`entities`** – A dictionary where each key represents a geographic entity (region, department, commune, …) and the value describes how to query that entity.

## General Structure
```json
{
  "base_url": "https://data.geopf.fr/wfs/ows",
  "api_type": "wfs",
  "common": { ... },
  "entities": { ... }
}
```

### `common`
Contains parameters that will be **merged** with the specific parameters of each entity:
```json
"common": {
  "SERVICE": "WFS",
  "VERSION": "2.0.0",
  "REQUEST": "GetFeature",
  "OUTPUTFORMAT": "application/json"
}
```

## `entities`
Each entity includes:
- **`TYPENAME`** – Full name of the WFS layer.
- One or more operation blocks:
  - `search_by_name` – Search by name.
  - `search_by_code` – Search by INSEE code.
  - `list_search` – List child objects (e.g., districts of a municipality).
  - `geometry` – Retrieve the geometry of a feature.

### Important: not all operations are available for every entity
- **`region`, `department`, `commune`** – have `search_by_name`, `search_by_code` **and** `geometry`.
- **`arrondissement`, `section`, `feuille`, `parcelle`, `subdivision_fiscale`** – do **not** have `search_by_name`/`search_by_code`. They provide **`list_search`** (to obtain a list of sub‑objects) and `geometry`.

In other words, each entity either has the two search blocks (`search_by_name` + `search_by_code`) **or** the `list_search` block. The `geometry` block is present for all entities to fetch the geographic shape.

## Example blocks
### Name search – `region`
```json
"search_by_name": {
  "PROPERTYNAME": "nom_officiel,code_insee",
  "CQL_FILTER": "nom_officiel='{value}'"
}
```
- `PROPERTYNAME` indicates the attributes to return.
- `CQL_FILTER` uses the placeholder `{value}` which will be replaced by the name provided by the caller.

### List search – `arrondissement`
```json
"list_search": {
  "PROPERTYNAME": "code_insee,nom_arr,code_arr",
  "CQL_FILTER": "code_insee='{value}'"
}
```
Here, `{value}` corresponds to the INSEE code of the parent municipality.

### Geometry – `parcelle`
```json
"geometry": {
  "PROPERTYNAME": "geom",
  "featureId": "{feature_id}"
}
```
For parcels, geometry is obtained via the `featureId` rather than a CQL filter.

## Place‑holders
Strings wrapped in curly braces (`{placeholder}`) are dynamically replaced by the Python code:
- `{value}` – generic value (name or code).
- `{code_insee}` – INSEE code of the entity.
- `{section}`, `{feuille}`, `{feature_id}`, `{idu_parcel}` – specific identifiers for cadastral objects.

These placeholders allow reusing the same JSON definition for many queries without hard‑coding values.

## Usage in the code
1. **Loading** – `core/config.py` reads `config/apis.json`.
2. **Selection** – the service (`core/service.py`) chooses the entity and operation.
3. **Construction** – `core/request_builder.py` combines the `common` section, the operation block, and `base_url`, then replaces placeholders.
4. **Sending** – `core/api_client.py` performs the HTTP request to the WFS.

---

This file summarizes the JSON structure, the differences in operations between entities, and the interpolation mechanism used by the project.
