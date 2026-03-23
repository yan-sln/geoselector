# Ajouter une nouvelle source d'API à `apis.json`

## Structure du JSON `apis.json`

Le fichier `apis.json` suit une structure hiérarchique :

```json
{
  "base_url": "<URL du service>",
  "api_type": "wfs",
  "common": {
    "SERVICE": "WFS",
    "VERSION": "2.0.0",
    "REQUEST": "GetFeature",
    "OUTPUTFORMAT": "application/json"
  },
  "entities": {
    "<nom_entité>": {
      "TYPENAME": "<nom_schema:nom_couche>",
      "search_by_name": {
        "PROPERTYNAME": "<champs>",
        "CQL_FILTER": "<filtre>"
      },
      "search_by_code": { … },
      "list_search": { … },
      "geometry": { … }
    }
  }
}
```

- **base_url** : URL de base du service.
- **api_type** : Type d’API.
- **common** : Paramètres communs à toutes les requêtes du service.
- **entities** : Ensemble des entités disponibles. Chaque entité possède :
  - **TYPENAME** : Identifiant de la couche WFS.
  - Un ou plusieurs blocs d’opérations (`search_by_name`, `search_by_code`, `list_search`, `geometry`, …) décrivant les champs retournés (`PROPERTYNAME`) et le filtre (`CQL_FILTER`).

---

## Configuration actuelle du JSON

Le projet utilise la configuration suivante :

- **base_url** : `https://data.geopf.fr/wfs/ows`
- **api_type** : `wfs`
- **common** : `SERVICE=WFS`, `VERSION=2.0.0`, `REQUEST=GetFeature`, `OUTPUTFORMAT=application/json`
- **entities** :
  - Recherche par nom ou code INSEE, puis récupère la géométrie :
    - `region`
    - `departement`
    - `commune`
  - Recherche par liste, puis récupère la géométrie :
    - `arrondissement`
    - `section`
    - `feuille`
    - `parcelle`(géométrie avec `featureId`)
    - `subdivision_fiscale`

---

## Ajouter une nouvelle API et ses entités

1. **Ajoutez une nouvelle entrée de niveau supérieur** dans `apis.json`. Incluez le champ `"api_type"` (ex. `"wfs"` ou `"rest"`). Exemple :
   ```json
   {
     "base_url": "https://my.other.service/wfs",
     "api_type": "rest",
     "common": { … },
     "entities": { … }
   }
   ```
   * `common` contient les paramètres identiques pour chaque requête à ce service.
   * `entities` liste les objets spécifiques fournis par le service.
2. **Copiez le bloc `common`** depuis la configuration existante (ou adaptez‑le si le nouveau service utilise d’autres valeurs par défaut).
3. **Définissez chaque entité** sous la clé `"entities"` :
   - `TYPENAME` – le typename WFS de la couche.
    - Ajoutez les opérations nécessaires (`search_by_name`, `search_by_code`, `list_search`, `geometry`, …) avec leurs champs (`PROPERTYNAME`) et filtres (`CQL_FILTER`).
    - `list_search` utilise les champs `PROPERTYNAME` et le filtre `CQL_FILTER` spécifiques à chaque entité :
      - `arrondissement` : `PROPERTYNAME` = `code_insee,nom_arr,code_arr`, `CQL_FILTER` = `code_insee='{value}'`.
      - `section` : `PROPERTYNAME` = `code_insee,section`, `CQL_FILTER` = `code_insee='{code_insee}'`.
      - `feuille` : `PROPERTYNAME` = `code_insee,section,feuille`, `CQL_FILTER` = `code_insee='{code_insee}' AND section='{section}'`.
      - `subdivision_fiscale` : `PROPERTYNAME` = `gid,idu_parcel,lettre`, `CQL_FILTER` = `idu_parcel='{idu_parcel}'`.
      - `parcelle` (`list_search_parcelle`) : `PROPERTYNAME` = `code_insee,section,numero,idu`, `CQL_FILTER` = `code_insee='{code_insee}' AND section='{section}'`.
4. **Ajoutez l’entité** sous la clé `"entities"` du fichier `apis.json`.
5. **Validez** la configuration avec le script `scripts/validate_config.py` ou en exécutant les tests (`pytest -q`).

---

## Exemple d'API REST

Le même format JSON peut être utilisé pour des API de type REST. La différence principale réside dans le champ `api_type` qui doit être défini à `"rest"` et les paramètres spécifiques aux requêtes REST :

```json
{
  "base_url": "https://api.example.com",
  "api_type": "rest",
  "common": {
    "HEADERS": { "Accept": "application/json" },
    "AUTH": "Bearer <token>"
  },
  "entities": {
    "user": {
      "ENDPOINT": "/users",
      "search_by_name": {
        "METHOD": "GET",
        "QUERY_PARAMS": { "name": "{value}" }
      },
      "detail": {
        "METHOD": "GET",
        "PATH": "/users/{id}"
      }
    }
  }
}
```

- **common** peut contenir des en‑têtes HTTP, des informations d’authentification, etc.
- Chaque entité possède un `ENDPOINT` de base et des opérations décrivant la méthode HTTP, les paramètres de requête ou le chemin.
- **Note :** le support REST est actuellement implémenté comme un placeholder dans `geoselector/core/request_builder.py`.
