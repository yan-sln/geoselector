# Plan d'implémentation de `IGNApiStrategy`

## Objectif
Fournir une implémentation fonctionnelle de la stratégie d’accès aux données de l’API IGN, capable de :
- rechercher des entités (communes, sections, parcelles) avec pagination et limite configurable,
- récupérer la géométrie d’une entité via le suffixe `/geometry`,
- récupérer les détails d’une entité en conservant le même format que les autres stratégies du projet.

## Étapes détaillées

1. **Analyse de l’API IGN**
   - Identifier les endpoints publics : `communes`, `sections`, `parcelles` (et éventuellement `departements`, `regions`).
   - Vérifier la documentation officielle pour les paramètres de recherche : `q` (texte), `limit`, `page`.
   - Confirmer le format de la réponse JSON pour chaque type d’entité.

2. **Mise à jour du constructeur**
   - Conserver l’appel à `super().__init__(default_limit)`.
   - Ajouter éventuellement un paramètre `base_url` configurable via variable d’environnement (`IGN_API_BASE_URL`).
   - Initialiser un logger dédié (`logger = logging.getLogger(__name__)`).

3. **Implémentation de `search`**
   - Construire l’URL : `url = f"{self.base_url}/{endpoint}"`.
   - Boucle de pagination identique à celle de `GouvFrApiStrategy` :
     - Calculer `overall_limit = self.get_limit(limit)`.
     - Déterminer `per_page = min(self.default_limit, overall_limit - len(results))`.
     - Envoyer la requête avec `self._request("GET", url, params={"q": text, "limit": per_page, "page": current_page})`.
   - Gestion des erreurs : si `_request` renvoie `None`, logger une erreur et sortir de la boucle.
   - Après chaque appel, formater les données avec les fonctions privées `_format_communes`, `_format_sections`, `_format_parcels`.
   - Retourner la liste agrégée.

4. **Implémentation de `fetch_details`**
   - Utiliser `_cached_fetch` (déjà présent dans `ApiStrategy`) :
     ```python
     data = self._cached_fetch(endpoint, code)
     ```
   - Appliquer le formatage approprié selon `endpoint` (similaire à `search`).
   - Retourner le premier élément formaté ou `{}` si vide.

5. **Formatters** (déjà présents mais à valider) :
   - `_format_communes` : extraire `code`, `nom`, `departement.code`, `region.code` (optionnel).
   - `_format_sections` : extraire `id`, `nom`, `commune.code`.
   - `_format_parcels` : extraire `id`, `identifiant`, `commune.code`, `section`.
   - S’assurer que les clés retournées correspondent exactement aux attributs attendus par les classes d’entités (`Municipality`, `Section`, `Parcel`).

6. **Gestion du cache**
   - Aucun changement requis : `ApiStrategy._cached_fetch` gère déjà le cache LRU.
   - Ajouter éventuellement un wrapper `clear_cache` dans `IGNApiStrategy` si besoin.

7. **Enregistrement de la stratégie**
   - Conserver l’appel `register_strategy('ign', IGNApiStrategy)` en bas du fichier.
   - Vérifier que le nom utilisé (`'ign'`) correspond à celui attendu par `SelectorFactory.create_selector` (ex. `api_source='ign'`).

8. **Tests unitaires** (prévision) :
   - Mock des réponses HTTP avec la bibliothèque `responses`.
   - Vérifier que `search` retourne la bonne structure pour chaque endpoint.
   - Vérifier que `fetch_details` formate correctement les données.
   - Tester la pagination (plusieurs pages) et la limite.

9. **Documentation**
   - Mettre à jour le `README.md` avec un exemple d’utilisation de la stratégie IGN.
   - Ajouter un lien vers ce fichier de plan dans la section *Points à améliorer*.

## Checklist (à cocher au fur et à mesure)
- [ ] Analyse des endpoints IGN terminée.
- [ ] Constructeur enrichi avec logger et variable d’environnement.
- [ ] Méthode `search` implémentée avec pagination.
- [ ] Méthode `fetch_details` implémentée et formatée.
- [ ] Formatters validés contre la documentation de l’API.
- [ ] Tests unitaires créés et réussis.
- [ ] Documentation mise à jour.

---

Ce plan fournit une feuille de route claire pour rendre `IGNApiStrategy` pleinement fonctionnelle et alignée avec le reste du projet.
