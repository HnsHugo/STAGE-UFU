# Collecte étendue : septembre 2026

Fenêtre : 1 septembre 2026 00:00 UTC inclus au 1 octobre 2026 00:00 UTC exclu.
Trois adresses sélectionnées avant collecte car les comptages du premier essai
(339, 170, 605 transactions) tenaient sous le plafond de 625 transactions.
Il s'agit d'une sélection par faisabilité, pas d'un échantillon représentatif.
Plafond : 25 pages par adresse. Les JSON conservent les observations normalisées
et les dates/hash des réponses. summary.json rassemble les métriques.

| Entité | Adresse | Stockage publié | Couverture | Transactions septembre | Jours actifs |
| --- | --- | --- | --- | --- | --- |
| Binance | `3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6` | unknown | count_consistent_full_history | 10 | 9 |
| Bitfinex | `bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97` | cold | count_consistent_full_history | 0 | 0 |
| Binance | `3LYJfcfHPXYJreMsASk2jkn69LWEYKzexb` | unknown | count_consistent_full_history | 0 | 0 |

Les labels restent non vérifiés pour septembre 2026. Binance reste unknown ;
aucun stockage n'est déduit des mesures. La cohérence des comptages ne garantit
pas un instantané atomique ni l'absence de reorg. Les métriques portent sur des
adresses, pas des wallets complets. Voir ../../WINDOW.md et ../../COMPARISON.md.

Les checkpoints bruts sont disponibles dans l’archive téléchargeable window_september2026_extended_archive.zip livrée avec ce bilan. Les fichiers Git seuls contiennent les observations normalisées et leur provenance, et ne suffisent pas à reprendre les pages sauvegardées. Extraire l’archive dans un dossier puis relancer avec son input.csv, son manifeste et les mêmes bornes. La reprise reste conditionnée aux statistiques live.
