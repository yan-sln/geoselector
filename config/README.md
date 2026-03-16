# Ajouter une nouvelle source d'API à `apis.json`

La configuration actuelle regroupe toutes les entités qui partagent la même **URL de base** (`https://data.geopf.fr/wfs/ows`). Cette URL est définie au niveau supérieur du fichier sous la clé "base_url". Lorsque vous devez prendre en charge un service WFS différent, suivez les étapes ci‑dessous :

1. **Ajoutez une nouvelle entrée de niveau supérieur** dans `apis.json`. Incluez le champ `"api_type"` (ex. `"wfs"` ou `"rest"`) pour indiquer le type d'API. Exemple :
   ```json
   {
     "base_url": "https://my.other.service/wfs",
     "api_type": "wfs",
     "common": { ... },
     "entities": { ... }
   }
   ```
   * `common` contains the parameters that are identical for every request to that service (e.g. `SERVICE`, `VERSION`, `REQUEST`, `OUTPUTFORMAT`).
   * `entities` lists the specific objects (region, commune, …) that the service provides.

2. **Copiez le bloc `common`** depuis la configuration existante (ou adaptez‑le si le nouveau service utilise d’autres valeurs par défaut).

3. **Définissez chaque entité** sous `"entities"` :
   - `TYPENAME` – le typename WFS de la couche.
   - Pour chaque opération (`search_by_name`, `search_by_code`, `search`, `list_sections`, `geometry`) indiquez :
     - `PROPERTYNAME` – les champs à retourner.
     - `CQL_FILTER` – une chaîne de modèle où les espaces réservés (ex. `{value}`, `{code_insee}`, `{section}`) seront remplacés à l’exécution.
     - Paramètres supplémentaires optionnels comme `featureId` ou `DISTINCT`.

4. **Le client utilise déjà le `request_builder`**. Il charge la configuration via `load_api_config` et sélectionne le bon builder grâce au champ `api_type`. Aucun changement supplémentaire n’est nécessaire.

5. **Test the new configuration** by calling the selector/factory with the new service identifier and verifying that the generated URLs match the expected WFS queries.

---

### Example – Adding a fictional "myapi" service
```json
{
  "base_url": "https://api.myservice.example/wfs",
    "api_type": "wfs",
    "common": {
    "SERVICE": "WFS",
    "VERSION": "2.0.0",
    "REQUEST": "GetFeature",
    "OUTPUTFORMAT": "application/json"
  },
  "entities": {
    "myentity": {
      "TYPENAME": "MYSCHEMA:myentity",
      "search_by_name": {
        "PROPERTYNAME": "name,id",
        "CQL_FILTER": "name='{value}'"
      },
      "geometry": {
        "PROPERTYNAME": "geom",
        "CQL_FILTER": "id='{value}'"
      }
    }
  }
}
```
Place this block in a separate file (e.g. `config/myapi.json`) or merge it into `apis.json` as another top‑level object.  The client can then select the appropriate configuration by the `base_url` you provide.

---

**Tip:** Keep the field names (`SERVICE`, `VERSION`, `REQUEST`, `OUTPUTFORMAT`, `TYPENAME`, `PROPERTYNAME`, `CQL_FILTER`, `DISTINCT`, `featureId`) exactly as they appear in the existing test scripts to avoid mismatches.
