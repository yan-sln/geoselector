# GeoSelector - Module pour plugin QGIS pour la sélection géographique

## Description

GeoSelector est un plugin QGIS développé en Python qui permet la sélection interactive de différentes entités géographiques (communes, départements, régions) via l'API Géo française. L'architecture est basée sur des principes de Programmation Orientée Objet et de Design Patterns pour assurer une haute maintenabilité et extensibilité.
Architecture

## Structure des fichiers

```
geoselector/
├─ core/
│   ├─ __init__.py
│   ├─ entities.py
│   ├─ geo_service.py
│   └─ exceptions.py
├─ selectors/
│   ├─ __init__.py
│   └─ entity_selector.py
├─ feature_selectors/
│   ├─ __init__.py
│   └─ entity_feature_selector.py
├─ utils/
│   ├─ __init__.py
│   └─ geometry_utils.py
├─ config/
│   └─ config.yaml                # configuration centralisée
├─ logging_config.py              # petite fabrique de logger
├─ __init__.py
└─ README.md
```

## Fonctionnalités

* Sélection interactive de communes, départements et régions.
* Récupération automatique des géométries via l'API Géo.
* Intégration native avec QGIS (QgsVectorLayer).
* Sélection interactive de communes, départements et régions.
* Récupération automatique des géométries via l'API Géo.
* Intégration native avec QGIS (QgsVectorLayer).
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

```

## Dépendances
### Dépendances obligatoires

* qgis.core : Pour l'intégration QGIS
* typing_extensions : Pour les types génériques
* requests : Pour les appels HTTP (si nécessaire)

## Diagramme de classes
<img width="2458" height="1169" alt="plantuml V3" src="https://github.com/user-attachments/assets/c54069bc-b140-4d6e-9c39-139dda0d7201" />
