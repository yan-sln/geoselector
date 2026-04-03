# Systeme d'Exceptions de GeoSelector

## Vue d'ensemble

GeoSelector implemente un système d'exceptions complet basé sur `ApiError` pour gérer les erreurs API de manière structurée et cohérente.

## Classes d'Exception

### ApiError (Classe de base)
- **Description** : Classe de base pour toutes les exceptions liées aux API
- **Attributs** :
  - `message` : Message d'erreur technique
  - `url` : URL de la requête ayant causé l'erreur (optionnel)
  - `error_code` : Code d'erreur spécifique (ex: NETWORK_ERROR)
  - `retryable` : Booléen indiquant si l'erreur peut être retentée

### NetworkError
- **Description** : Erreurs liées au réseau (connexions, timeouts, erreurs HTTP)
- **Retryable** : `True` (peut être retentée)
- **Code** : `NETWORK_ERROR`

### ValidationError  
- **Description** : Erreurs de validation des données (données incorrectes, formats invalides)
- **Retryable** : `False` (ne doit pas être retentée)
- **Code** : `VALIDATION_ERROR`

### ServiceError
- **Description** : Erreurs de service (indisponibilité, erreurs serveur)
- **Retryable** : `True` (peut être retentée)
- **Code** : `SERVICE_UNAVAILABLE`

### TimeoutError
- **Description** : Erreurs de timeout lors des requêtes
- **Retryable** : `True` (peut être retentée)
- **Code** : `TIMEOUT_ERROR`

## Méthodes Utilitaires

### to_user_friendly_message()
- **Description** : Génère un message d'erreur lisible par l'utilisateur
- **Renvoie** : String avec message utilisateur personnalisé selon le type d'erreur

## Mise en Œuvre

### Tests Couvrants

Les tests suivants sont présents dans `tests/test_exceptions.py` :

1. **test_exception_hierarchy** : Vérifie l'héritage correct des classes d'exception
2. **test_user_friendly_messages** : Teste la génération des messages utilisateur
3. **test_exception_creation_variations** : Teste différentes façons de créer des exceptions
4. **test_api_client_exceptions** : Vérifie que ApiClient lève correctement les exceptions
5. **test_service_retry_logic** : Teste le mécanisme de retry dans GeoService
6. **test_selector_exception_handling** : Vérifie la gestion des exceptions par le sélecteur

### Fonctionnalités de Retry

Le système de retry automatique est intégré dans :
- `GeoService` : Les méthodes critiques sont protégées par un mécanisme de retry avec backoff exponentiel
- Configuration par défaut : 3 tentatives max avec délai croissant
- Seules les erreurs `retryable=True` sont retentées

### Messages Utilisateur

Chaque type d'erreur génère un message utilisateur spécifique :
- **NetworkError** : "Erreur de connexion réseau. Veuillez vérifier votre connexion internet et réessayer."
- **ServiceError** : "Le service est temporairement indisponible. Veuillez réessayer dans quelques minutes."
- **TimeoutError** : "La requête a expiré. Veuillez réessayer."
- **ValidationError** : "Une erreur s'est produite. Veuillez réessayer."

## Utilisation dans le Code

```python
from geoselector.core.exceptions import NetworkError, ValidationError, ServiceError

# Lancer une exception
raise NetworkError("Impossible de se connecter", url="http://api.example.com")

# Gérer les exceptions
try:
    # Code susceptible d'erreur
    pass
except NetworkError as e:
    # Gestion spécifique réseau
    user_message = e.to_user_friendly_message()
    logger.error(user_message)
```