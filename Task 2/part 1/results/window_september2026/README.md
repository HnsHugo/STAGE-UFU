# Essai : activité en septembre 2026

Fenêtre UTC : 2026-09-01 00:00 inclus à 2026-10-01 00:00 exclu.
Collecte réelle du 5 octobre 2026 avec collect_window.py, max-pages=1
(au plus 25 transactions par adresse). Le manifeste et input.csv fixent
les paramètres et les sources. Les JSON conservent les observations et
la provenance de chaque requête.

Résultat : 11 adresses, 0 erreurs de collecte, 3 adresses avec
métriques fondées sur un historique aux comptages cohérents et 8
adresses dont la couverture reste non vérifiée.

| Entité | Adresse | Label publié | Couverture | Transactions de septembre observées | Nombre complet calculable |
| --- | --- | --- | --- | --- | --- |
| BTC-e.com | `16SbwNa22nBwhLtg6HzWVYFQiUxtNzAUpt` | unknown | unverified | 0 | indisponible |
| Bitfinex | `1Kr6QSydW9bFQG1mXiPNNu6WpJGmUa9i1g` | hot | unverified | 0 | indisponible |
| Binance | `34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo` | unknown | unverified | 6 | indisponible |
| Bitfinex | `3JZq4atUahhuA9rLhXLMhhTo133J9rF97j` | cold | unverified | 18 | indisponible |
| Binance | `3LYJfcfHPXYJreMsASk2jkn69LWEYKzexb` | unknown | unverified | 0 | indisponible |
| Binance | `3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6` | unknown | unverified | 10 | indisponible |
| Change | `bc1q43krjn8qvfydqs9lq8crg26er4c26hkpd2mpw7` | cold | count_consistent_full_history | 0 | 0 |
| Change | `bc1q9rqfux88j6az0wl957u2jdykgw5m5r72hcaclu` | cold | count_consistent_full_history | 0 | 0 |
| Bitfinex | `bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97` | cold | unverified | 0 | indisponible |
| Change | `bc1qhsuvec03zslh9qvauksh2wc9hy9za7csxem5ea` | cold | count_consistent_full_history | 0 | 0 |
| Binance | `bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h` | unknown | unverified | 0 | indisponible |

Une valeur observée n'est pas un nombre complet lorsque la couverture est
non vérifiée. En particulier, zéro observation dans un historique tronqué
ne prouve pas l'inactivité. La cohérence des comptages du fournisseur n'est
pas une garantie d'instantané atomique ni une protection contre les reorgs.

Les labels de stockage ne sont pas validés pour septembre 2026. Les résultats
ne constituent donc pas une comparaison hot/cold validée et aucune prédiction
de stockage n'a été ajoutée. Les adresses Change sont documentées cold au
31 mars 2025 seulement ; un résultat ultérieur ne prolonge pas cette preuve.

La prochaine amélioration nécessaire est la collecte ciblée d'une fenêtre,
avec vérification de couverture par blocs, plutôt qu'exiger tout l'historique.
Un simple accroissement du plafond ne garantit pas de couvrir les adresses très
actives. Les statistiques complètes manquantes restent null dans les JSON.
