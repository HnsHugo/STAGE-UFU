# Première expérience avec un arbre de décision

## Ce qui est réellement testé

La cible est « parent direct candidat d'une consolidation attribuée au cas » contre « transaction sans attribution ». Ce n'est pas une vérité terrain de vol ou de contrôle par hardware wallet. Les cinq consolidations et les 98 coinbase sont exclues : 493 468 transactions, dont 1 070 candidates.

L'arbre utilise 16 propriétés numériques des transactions. TXID, hauteur, provenance et indicateur coinbase sont exclus. Les réglages sont fixés avant l'entraînement : profondeur 4, minimum 20 observations par feuille, poids de classes équilibrés, random_state 42. Aucun réglage n'a été choisi sur les résultats des tests. La règle de comparaison, elle, avait déjà été observée sur tout le dataset ; elle reste une référence descriptive.

## Résultats calculés le 8 octobre 2026

| Partage | Modèle | Candidates retrouvées | Alertes dans le fond sans attribution | Précision proxy | Rappel proxy |
|---|---|---:|---:|---:|---:|
| Aléatoire, référence avec risque de fuite | Arbre complet | 266 / 267 | 53 | 83,39 % | 99,63 % |
| Aléatoire, référence avec risque de fuite | Arbre sans frais | 267 / 267 | 6048 | 4,23 % | 100 % |
| Chronologique | Arbre complet | 0 / 34 | 139 | 0 % | 0 % |
| Chronologique | Arbre sans frais | 34 / 34 | 15820 | 0,21 % | 100 % |
| Chronologique | Une sortie et frais >=4,95 sat/vB | 34 / 34 | 5953 | 0,57 % | 100 % |

Ces « alertes dans le fond » ne sont pas des vols nouvellement détectés, ni des faux positifs légalement établis. Les métriques portent uniquement sur la cible proxy.

Partage aléatoire stratifié : 370101 observations d'entraînement (803 candidates), 123367 de test (267 candidates). Ce partage peut disperser les membres d'un même collecteur dans les deux ensembles ; son résultat ne doit pas être présenté comme une validation indépendante.

Partage chronologique : entraînement sur hauteurs <960377 (163328 observations, 1036 candidates), test sur hauteurs >=960377 (330140 observations, 34 candidates). Les blocs des deux ensembles ne se recouvrent pas. Il n'est pas établi que les entités ou collecteurs soient indépendants ; ce test ne couvre qu'un petit groupe tardif de candidates et un seul incident.

## Pourquoi le score aléatoire est trompeur

Les 1036 candidates anciennes, sur cinq blocs, ont des frais médians de 30 sat/vB. Les 34 candidates du bloc 960733 ont une médiane de 4,9590 sat/vB. L'arbre chronologique complet sépare principalement les frais autour de 30 : il manque donc toutes les candidates tardives. Ce résultat montre une dépendance à une signature de frais spécifique au premier groupe, sans démontrer une règle générale des vols.

Sans frais, la forme et les montants retrouvent le petit groupe tardif, mais les alertes augmentent à 15820 sur 330106 observations du fond (4,79 %). La généralisation n'est pas établie.

## Reproduire

Depuis Task 2/coldcard, avec les caractéristiques déjà extraites :

```bash
python -m pip install -r requirements.txt
python train_exploratory.py features_output/transactions.csv.gz experiment_output
python -m unittest discover -p test_experiment.py -v
```

Les versions utilisées sont consignées dans metrics.json. Le script vérifie le SHA256 exact du fichier reçu. Le dossier de sortie doit être nouveau. Les arbres exportés en texte décrivent les modèles de chaque partage ; leurs poids ne sont pas des probabilités de vol calibrées. Aucun modèle de production n'est fourni.

## Étape suivante

```bash
python extract_candidate_groups.py blocks parents.json candidate_groups.json
```

Ce script regroupe les candidates par consolidation descendante, fusionne les groupes partageant des adresses de collecte et ceux partageant un parent. Il vérifie la couverture contre parents.json. Les adresses servent uniquement au regroupement et ne sont pas publiées dans le résultat. L'extraction doit être exécutée dans Codespaces, où les blocs complets existent.

Les groupes restent incomplets vis-à-vis des blocs absents et des liens avec le fond. Une validation par groupes, puis des cas externes documentés et des témoins sourcés, seront nécessaires avant de parler de détection de vols.

## Sources méthodologiques

- https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/common_pitfalls.html
- Attribution initiale : https://bitquery.io/investigations/coldcard-wallet-hack
