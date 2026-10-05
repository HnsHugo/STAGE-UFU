# Préparer une comparaison hot / cold

Audit du 5 octobre 2026. Données examinées : [address_summary.csv](results/history_20261005/address_summary.csv), version [d8cff427](https://github.com/HnsHugo/STAGE-UFU/commit/d8cff427001d21c0fbe07efd97bf944c8cebe4c7).

## Résultat

La collecte est utilisable pour décrire les transactions observées. Elle ne permet
pas encore une comparaison validée du comportement hot / cold sur une période
commune : les historiques sont tronqués différemment et aucun intervalle commun
de validité des labels n'est établi.

Les 25 transactions Bitfinex hot s'étendent sur 9,73 heures. Les 25 transactions
de ses deux adresses cold s'étendent respectivement sur 55,01 et 251,01 jours.
Ces durées mesurent l'écart entre les dates extrêmes de l'échantillon, pas une
fenêtre d'observation complète. Diviser 25 par ces durées ne donne pas une
fréquence comparable : les fenêtres ont été choisies par le nombre d'événements.

## Couverture par adresse

Dates et durées en UTC. Durée = (newest_observed_utc - oldest_observed_utc) / 86400,
arrondie à deux décimales en jours. Les dates affichées omettent l'heure ;
les durées utilisent les timestamps complets du CSV.

| Entité | Adresse | Label publié | Transactions observées | Dates extrêmes | Écart (jours) | Couverture |
| --- | --- | --- | --- | --- | --- | --- |
| BTC-e.com | `16SbwNa22nBwhLtg6HzWVYFQiUxtNzAUpt` | unknown | 25 | 2016-04-03 → 2016-04-25 | 21.93 | partial |
| Bitfinex | `1Kr6QSydW9bFQG1mXiPNNu6WpJGmUa9i1g` | hot | 25 | 2026-10-04 → 2026-10-05 | 0.41 | partial |
| Bitfinex | `3JZq4atUahhuA9rLhXLMhhTo133J9rF97j` | cold | 25 | 2026-08-07 → 2026-10-01 | 55.01 | partial |
| Bitfinex | `bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97` | cold | 25 | 2025-12-20 → 2026-08-28 | 251.01 | partial |
| Binance | `34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo` | unknown | 25 | 2026-07-03 → 2026-09-19 | 78.22 | partial |
| Binance | `3LYJfcfHPXYJreMsASk2jkn69LWEYKzexb` | unknown | 25 | 2026-02-01 → 2026-08-28 | 208.68 | partial |
| Binance | `3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6` | unknown | 25 | 2026-08-06 → 2026-09-22 | 47.81 | partial |
| Binance | `bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h` | unknown | 25 | 2026-10-05 → 2026-10-05 | 0.02 | partial |
| Change | `bc1q43krjn8qvfydqs9lq8crg26er4c26hkpd2mpw7` | cold | 2 | 2025-01-16 → 2025-09-10 | 236.59 | count_matches_stable_stats |
| Change | `bc1qhsuvec03zslh9qvauksh2wc9hy9za7csxem5ea` | cold | 2 | 2025-03-04 → 2025-04-30 | 57.18 | count_matches_stable_stats |
| Change | `bc1q9rqfux88j6az0wl957u2jdykgw5m5r72hcaclu` | cold | 2 | 2025-03-10 → 2025-05-15 | 65.55 | count_matches_stable_stats |

Les huit historiques partial ne suffisent pas à affirmer qu'une transaction
absente de l'échantillon n'existe pas. Les trois historiques Change ont des
comptages cohérents avec les statistiques stables du fournisseur, ce qui reste
une vérification de cohérence et non un instantané atomique garanti.

## Dates des preuves

| Groupe | Preuve disponible | Usage pour la comparaison |
| --- | --- | --- |
| Bitfinex : 1 hot, 2 cold | Liste officielle versionnée ; intervalle opérationnel non spécifié | Conserver les labels publiés, mais leur application aux transactions de 2026 reste non vérifiée |
| Change : 3 cold | Instantané au 31 mars 2025 à 23:59 UTC | Le label est attesté à cet instant ; sa continuité avant ou après n'est pas établie |
| Binance : 4 unknown | Réserves au 10 novembre 2022 ; absence de label par adresse | Exclure des groupes hot/cold ; ne pas déduire le stockage de l'activité |
| BTC-e : test API | Attribution WalletExplorer, stockage inconnu | Exclure de l'échantillon de recherche |

Sources et limites : [Bitfinex et Binance](data/research_sources_20261005.md),
[Change](data/change_sources_20261005.md), [méthode de collecte](HISTORY.md).
La date reviewed_at_utc est la date de lecture de la source, pas le début de
validité du label. Aucune période calendaire n'est donc sélectionnée comme
« validée hot/cold » dans cet audit.

## Protocole de la prochaine collecte

1. Établir des dates de validité des preuves pour des adresses hot et cold.
   Enregistrer séparément la date du snapshot, l'intervalle attesté s'il existe,
   et les hypothèses. Un snapshot seul ne justifie pas une durée de 30 jours.
2. Fixer une fenêtre commune [début UTC inclus, fin UTC exclue] avant de regarder
   les résultats. Une durée de 30 jours est une proposition exploratoire, à
   adapter aux preuves ; elle n'est pas une période validée à ce stade.
3. Collecter jusqu'à couvrir le début de cette fenêtre ou épuiser l'historique,
   avec un plafond explicite de requêtes. Si le plafond est atteint avant la
   couverture, marquer la fenêtre incomplète et laisser les métriques complètes
   indisponibles. Le collecteur actuel est limité par pages et ne met pas encore
   en œuvre cette collecte par fenêtre.
4. Vérifier les frontières par hauteurs de blocs et dédupliquer les TXID.
   Les timestamps de blocs peuvent être non monotones : un seul timestamp
   ancien rencontré pendant la pagination ne prouve pas à lui seul la couverture.
   Documenter les changements de chaîne entre requêtes.
5. Calculer uniquement pour les fenêtres couvertes les métriques ci-dessous.
   Garder les résultats exploratoires utilisant des labels historiques
   explicitement identifiés comme tels.

| Mesure prévue | Définition |
| --- | --- |
| Nombre de transactions | TXID distincts impliquant l'adresse dans la fenêtre |
| Fréquence quotidienne | Nombre / durée fixe de la fenêtre en jours, y compris les jours sans transaction |
| Entrées / sorties | Somme des valeurs attribuées à cette adresse, en satoshis ; retours inclus |
| Jours actifs | Nombre de dates UTC avec au moins une transaction confirmée |
| Frais médians | Médiane en sat/vB des transactions qui dépensent des fonds de l'adresse ; frais de la transaction entière, pas frais imputés à l'adresse |
| Réceptions seules | Décompte séparé ; leurs frais sont choisis par l'émetteur et ne décrivent pas la politique du destinataire |

Un zéro nécessite une fenêtre couverte : absence d'observation dans un historique
tronqué signifie « indisponible », pas zéro. Une adresse représente seulement
une partie éventuelle d'un wallet. Les petites réceptions non sollicitées
peuvent gonfler l'activité sans traduire une décision de son propriétaire.

## Portée des conclusions

L'échantillon contient dix adresses de recherche : cinq cold, une hot et quatre
unknown. Les trois entités ne constituent pas une population représentative.
La seule adresse hot appartient à Bitfinex ; l'entité et le type de stockage
peuvent donc être confondus. Plusieurs adresses d'une même entité ne sont pas
des observations indépendantes. Présenter d'abord les résultats par adresse et
par entité ; élargir les deux groupes avant toute généralisation.

Tous les labels hardware et illicit restent unknown. Cet audit ne calcule
ni score illicite, ni CPFP, ni durée de détention UTXO. Ces deux dernières
analyses nécessitent des données supplémentaires sur les entrées et sorties.
