# GeoSelector - Module pour plugin QGIS pour la sélection géographique

## Description

GeoSelector est un plugin QGIS développé en Python qui permet la sélection interactive de différentes entités géographiques (communes, départements, régions) via l'API Géo française. L'architecture est basée sur des principes de Programmation Orientée Objet et de Design Patterns pour assurer une haute maintenabilité et extensibilité.
Architecture

## Structure des fichiers

```
geoselector/
├── __init__.py
├── core/
│   ├── geo_entity.py          # Entités géospatiales
│   ├── geo_service.py         # Service API Géo
│   ├── base_selector.py       # Classes abstraites
│   └── selector_factory.py    # Factory pattern
├── selectors/
│   ├── municipality_selector.py  # Sélecteur de communes
│   ├── department_selector.py    # Sélecteur de départements
│   └── region_selector.py        # Sélecteur de régions
├── feature_selectors/
│   ├── municipality_feature_selector.py
│   ├── department_feature_selector.py
│   └── region_feature_selector.py
└── utils/
    └── geometry_utils.py      # Utilitaires géométriques
```

## Principes de conception appliqués

Respect des principes de design orienté objet (SOLID).

## Fonctionnalités

* Sélection interactive de communes, départements et régions
* Récupération automatique des géométries via l'API Géo
* Intégration native avec QGIS (QgsVectorLayer)
* Support de l'architecture modulaire et extensible

## Prérequis

* QGIS 3.x
* Python 3.8+
* Packages requis : qgis.core, typing_extensions

## Installation
```
# Cloner le dépôt
git clone https://github.com/yan-sln/geoselector.git
cd geoselector

# Installer dans QGIS
# Via le gestionnaire de plugins QGIS
# Ou en copiant le dossier dans le répertoire des plugins QGIS
```

## Utilisation
### Exemple basique
```
from geoselector import (
    GeoDataService, 
    MunicipalitySelector,
    MunicipalityFeatureSelector
)

# Création des objets
service = GeoDataService()
municipality_selector = MunicipalitySelector(service)
feature_selector = MunicipalityFeatureSelector(municipality_selector)

# Sélection d'une commune
selected_municipality = municipality_selector.select("Dijon")
geometry = municipality_selector.load_geometry(selected_municipality.code)

# Sélection dans QGIS
feature = feature_selector.selectMunicipalityFeature()
```
### Ajout d'une nouvelle entité

Pour ajouter une nouvelle entité (ex: ville) :

1. Créer une classe City dans geo_entity.py
2. Ajouter la méthode searchCities() dans GeoDataService
3. Créer CitySelector.py et CityFeatureSelector.py dans les dossiers appropriés

## Dépendances
### Dépendances obligatoires

* qgis.core : Pour l'intégration QGIS
* typing_extensions : Pour les types génériques
* requests : Pour les appels HTTP (si nécessaire)

## Diagramme de classes
![UML_selector](https://github.com/user-attachments/assets/80f10f2c-3707-4abf-9785-f25b70c8606b)
