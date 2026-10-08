# Task 2 — étude du cas Coldcard et première expérience ML

Ce dossier contient un pipeline reproductible d'analyse des blocs fournis par le professeur. Le premier objectif est une expérience explicable avec un arbre de décision ; la détection générale de vols et l'identification du matériel ne sont pas encore démontrées.

## État actuel

- 98 blocs JSON sélectionnés, 493571 transactions uniques ; 98 coinbase.
- 5 transactions présentes attribuées au cas par une enquête externe.
- 1070 parents directs retrouvés sur 2349 recherchés ; les autres restent hors couverture.
- 4 groupes de parents observés : 491, 341, 204 et 34.
- Caractéristiques extraites et contrôlées ; expériences aléatoire, chronologique et par groupe exécutées.
- 19 tests sur les séparations, les métriques, la fusion des groupes et la provenance.

Les mots « candidate » et « attribuée par la source » décrivent la provenance. Ils ne remplacent pas une vérification indépendante d'un vol ou d'un hardware wallet. Les transactions sans attribution restent inconnues.

## Lire les résultats

- PARENT_AUDIT.md : couverture des liens de financement.
- FEATURE_ANALYSIS.md : contrôles et différences descriptives.
- EXPERIMENT.md : le score aléatoire élevé et l'échec sur les candidates plus tardives.
- GROUPED_EXPERIMENT.md : évaluation avec chaque groupe candidat tenu hors entraînement.
- TRANSITION.md : clôture du pilote précédent et nouvelle priorité.
- LABEL_PROTOCOL.md : règles pour constituer les labels du prochain dataset.

## Installation

Utiliser Python 3.12 et installer les dépendances depuis ce dossier :

```bash
python -m pip install -r requirements.txt
```

Garder les blocs bruts hors Git, dans blocks/ ; conserver une copie de l'archive originale. L'extracteur accepte les 98 fichiers sans extension, nommés par hash. L'archive originale est également acceptée par l'audit.

## Pipeline complet

Les commandes suivantes sont à lancer depuis Task 2/coldcard. Choisir de nouveaux noms de sortie si une extraction ou expérience a déjà été lancée : les scripts refusent les dossiers de sortie existants.

```bash
python audit_coldcard_parents.py blocks > parents.json
python extract_features.py blocks parents.json features_output
python extract_candidate_groups.py blocks parents.json candidate_groups.json
python audit_dataset.py features_output/transactions.csv.gz features_output/manifest.json candidate_groups.json
python train_exploratory.py features_output/transactions.csv.gz experiment_output
python train_grouped.py features_output/transactions.csv.gz candidate_groups.json features_output/manifest.json grouped_output
python -m unittest discover -p 'test_*.py' -v
```

Vérifier status complete dans features_output/manifest.json avant entraînement. Les entraîneurs reproduisent cette version exacte du pilote et contrôlent le SHA256 du CSV compressé ; un nouveau dataset nécessite une nouvelle version documentée du protocole et de son empreinte.

Les arbres sont exportés en texte pour inspection et les métriques en JSON. Aucun modèle de production ni probabilité de vol calibrée n'est publié.

## Résultat à retenir

L'arbre complet retrouve 874/1070 candidates cumulées en validation par groupe et produit 1072 alertes sur le fond. Il échoue entièrement sur un groupe et ne retrouve que 43/204 dans un autre. Son rappel moyen par groupe est 55,20 %. Ce résultat justifie un travail sur la diversité des cas et les labels avant d'introduire un modèle plus complexe.

## Modèle de recherche exporté

Un arbre final, entraîné sur toutes les observations éligibles après les expériences, est disponible dans grouped_results_20261008/research_proxy_model.json. Ce fichier JSON ne contient pas de code exécutable ni de pickle. Ses scores sont des proportions pondérées de feuille, pas des probabilités calibrées de vol. Il n'a pas de score de validation propre : les métriques des arbres par pli ne sont pas celles de cet artefact final.

Pour l'appliquer à un autre CSV ayant les mêmes caractéristiques et des TXID :

```bash
python proxy_model.py score grouped_results_20261008/research_proxy_model.json autres_caracteristiques.csv.gz scores_recherche.csv.gz
```

La sortie emploie research_candidate_score et research_candidate_like, avec la mention similar_to_training_candidates_not_confirmed_theft. Ne pas utiliser cette sortie comme liste de criminels ou preuve de contrôle matériel. Les données hors distribution nécessitent une validation externe.
