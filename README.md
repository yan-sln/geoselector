# GeoSelector

## 1. **Architecture générale**

Le dépôt est organisé en trois grands modules principaux :

```
geo_selector/
├── api/          # Adaptateurs pour différentes APIs géographiques
├── core/         # Logique centrale et entités
└── factory/      # Factories pour créer des sélecteurs d'entités
```

* **`api`** : contient les implémentations concrètes des stratégies d’accès aux données géographiques (Gouv.fr et IGN).
* **`core`** : cœur du système, avec les entités, les services, les sélecteurs, et le registre d’entités.
* **`factory`** : permet de créer facilement des selectors typés, avec une API et une stratégie donnée.

---

## 2. **`core` : cœur fonctionnel**

### a) **Entities (`entities.py`)**

* Définit la classe abstraite `GeoEntity` avec une interface `from_dict`.
* Les sous-classes concrètes représentent des entités géographiques :

  * `Municipality` → communes
  * `Department` → départements
  * `Region` → régions
  * `Parcel` → parcelles cadastrales
  * `Section` → sections cadastrales
* Chaque entité déclare `API_ENDPOINT`, ce qui permet de l’enregistrer automatiquement dans `EntityRegistry`.

### b) **Registry (`registry.py`)**

* `EntityRegistry` stocke les entités par leur `API_ENDPOINT`.
* Méthodes :

  * `register` → ajouter une entité
  * `get` → récupérer une entité via son endpoint
  * `list_entities` → lister toutes les entités enregistrées
* Sert à relier dynamiquement les entités aux stratégies API.

### c) **Service (`service.py`)**

* `GeoService` : abstraction pour interroger n’importe quelle API via une `ApiStrategy`.
* Méthodes :

  * `search_entities(entity_class, text)`
  * `fetch_entity_geometry(entity_class, code)`
  * `get_entity_details(entity_class, code)`

### d) **Selectors (`selector.py`)**

* `EntitySelector` : interface typée pour sélectionner des entités.
* `EntitySelectorImpl` : implémentation générique qui utilise `GeoService` pour exécuter les recherches et récupérer géométrie/détails.
* Permet un typage fort : par exemple un `EntitySelector<Municipality>` renvoie toujours des objets `Municipality`.

### e) **Strategy (`strategy.py`)**

* Interface `ApiStrategy` pour standardiser les appels API.
* Les méthodes abstraites sont :

  * `search(endpoint, text)`
  * `fetch_geometry(endpoint, code)`
  * `fetch_details(endpoint, code)`

---

## 3. **`api` : implémentation des stratégies**

### a) **`gouvfr.py`**

* Implémente `GouvFrApiStrategy` pour l’API `geo.api.gouv.fr`.
* Méthodes complètes avec formatage spécifique pour chaque type d’entité.
* Gestion des erreurs via `try/except` et logs simples (`print`).
* Supporte :

  * Communes, départements, régions
  * Parcelles et sections cadastrales

### b) **`ign.py`**

* Implémente `IGNApiStrategy`.
* Actuellement minimaliste : toutes les méthodes font juste un `print` et renvoient des structures vides.
* À compléter pour interroger l’API IGN réelle.

---

## 4. **`factory` : création des selectors**

### `selector_factory.py`

* `SelectorFactory` fournit une interface simple pour créer des sélecteurs typés :

```python
selector = SelectorFactory.create_selector(Municipality, "GOUVFRApiStrategy")
```

* Fonctionnement :

  1. Récupère la stratégie API dans `STRATEGIES`.
  2. Instancie `GeoService` avec cette stratégie.
  3. Retourne un `EntitySelectorImpl` typé avec la classe d’entité donnée.

---

## 5. **Exposition publique (`__init__.py`)**

* Le package `geo_selector` expose directement :

  ```python
  core_service       # alias GeoService
  selector_factory   # alias SelectorFactory
  ```
* Les utilisateurs peuvent donc créer un service ou un selector facilement sans naviguer dans les sous-modules.

---

## 6. **Points forts**

* Architecture claire en **couches** : API ↔ Service ↔ Selector ↔ Entité.
* Typage fort grâce à `Generic[T]`.
* Extensible : ajouter une nouvelle API ou entité se fait facilement via `ApiStrategy` et `GeoEntity`.
* Factory simplifie la création de selectors.

---

## 7. **Points à améliorer**

1. **IGNApiStrategy** : à implémenter correctement.
2. **Logging et erreurs** : remplacer les `print` par un vrai `logger`.
3. **Tests unitaires** : pas visibles ici, mais cruciaux pour valider les stratégies API et le mapping des entités.
4. **Pagination / limites** : `GouvFrApiStrategy.search` limite actuellement à 10 résultats fixes.
5. **Validation des données** : certains champs optionnels (`commune_code`, `section`) pourraient avoir des validations plus robustes.

---

## 8. **Résumé fonctionnel**

* Tu as un **framework de sélection d’entités géographiques**.
* On peut faire :

```python
from geo_selector import selector_factory
from geo_selector.core.entities import Municipality

selector = selector_factory.create_selector(Municipality, "GOUVFRApiStrategy")
results = selector.select("Paris")
geometry = selector.get_geometry(results[0].code)
details = selector.get_details(results[0].code)
```

* La structure est prête pour ajouter d’autres sources de données, d’autres types d’entités, et pour automatiser des workflows géographiques.

---
_Documentation générée automatiquement_