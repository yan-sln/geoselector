# Explication du fichier `apis.json`

Le fichier **[`config/apis.json`](config/apis.json:1)** décrit la configuration des appels aux services WFS (Web Feature Service) utilisés par le projet *geoselector*. Il regroupe :

1. **`base_url`** – URL de base du service.
2. **`api_type`** – Type d'API (ici `wfs`).
3. **`common`** – Paramètres communs à toutes les requêtes (service, version, type de requête, format de sortie).
4. **`entities`** – Un dictionnaire où chaque clé représente une entité géographique (region, departement, commune, …) et la valeur décrit comment interroger cette entité.

## Structure générale
```json
{
  "base_url": "https://data.geopf.fr/wfs/ows",
  "api_type": "wfs",
  "common": { ... },
  "entities": { ... }
}
```

### `common`
Contient les paramètres qui seront **fusionnés** avec les paramètres spécifiques de chaque entité :
```json
"common": {
  "SERVICE": "WFS",
  "VERSION": "2.0.0",
  "REQUEST": "GetFeature",
  "OUTPUTFORMAT": "application/json"
}
```

## `entities`
Chaque entité possède :
* **`TYPENAME`** – Nom complet de la couche WFS.
* Un ou plusieurs blocs d'opération :
  * `search_by_name` – Recherche à partir du nom.
  * `search_by_code` – Recherche à partir du code INSEE.
  * `list_search` – Recherche d'une liste d'objets enfants (ex. arrondissements d'une commune).
  * `geometry` – Récupération de la géométrie du feature.

### Important : toutes les opérations ne sont pas disponibles pour toutes les entités
- **`region`, `departement`, `commune`** : disposent de `search_by_name`, `search_by_code` **et** `geometry`.
- **`arrondissement`, `section`, `feuille`, `parcelle`, `subdivision_fiscale`** : n'ont **pas** `search_by_name`/`search_by_code`. Elles offrent **`list_search`** (pour obtenir la liste des sous‑objets) et `geometry`.

En d’autres termes, chaque entité possède **soit** les deux blocs de recherche (`search_by_name` + `search_by_code`) **soit** le bloc `list_search`. Le bloc `geometry` est présent pour toutes les entités afin de récupérer la forme géographique.

## Exemple de blocs
### Recherche par nom – `region`
```json
"search_by_name": {
  "PROPERTYNAME": "nom_officiel,code_insee",
  "CQL_FILTER": "nom_officiel='{value}'"
}
```
* `PROPERTYNAME` indique les attributs à retourner.
* `CQL_FILTER` utilise le placeholder `{value}` qui sera remplacé par le nom fourni par l’appelant.

### Recherche de liste – `arrondissement`
```json
"list_search": {
  "PROPERTYNAME": "code_insee,nom_arr,code_arr",
  "CQL_FILTER": "code_insee='{value}'"
}
```
Ici, `{value}` correspond au code INSEE de la commune parent.

### Géométrie – `parcelle`
```json
"geometry": {
  "PROPERTYNAME": "geom",
  "featureId": "{feature_id}"
}
```
Pour les parcelles, la géométrie est obtenue via le `featureId` plutôt que par un filtre CQL.

## Place‑holders
Les chaînes entre accolades (`{placeholder}`) sont remplacées dynamiquement par le code Python :
* `{value}` – valeur générique (nom ou code).
* `{code_insee}` – code INSEE de l’entité.
* `{section}`, `{feuille}`, `{feature_id}`, `{idu_parcel}` – identifiants spécifiques aux objets cadastraux.

Ces placeholders permettent de réutiliser la même définition JSON pour de nombreuses requêtes sans coder en dur les valeurs.

## Utilisation dans le code
1. **Chargement** : `core/config.py` lit `config/apis.json`.
2. **Sélection** : le service (`core/service.py`) choisit l’entité et l’opération souhaitées.
3. **Construction** : `core/request_builder.py` combine `common`, le bloc d’opération et `base_url`, puis remplace les placeholders.
4. **Envoi** : `core/api_client.py` effectue la requête HTTP vers le WFS.

---

Ce fichier `explication_json.md` résume donc la structure du JSON, les différences d’opérations entre les entités, et le mécanisme d’interpolation utilisé par le projet.
