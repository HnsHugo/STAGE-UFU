# Diagnostic des erreurs de validation Real-CATS — 18 octobre 2026

## Expérience exécutée

Le diagnostic reproduit la forêt historique du benchmark à **22 caractéristiques**, poids de classe positive 3, 100 arbres, profondeur maximale 20, minimum 20 observations par feuille, max_features=sqrt et seed 42. Le seuil historique reste strictement supérieur à 0,30. Ce modèle est distinct de la forêt externe figée à 19 caractéristiques et seuil 0,15, qui n’est ni modifiée ni exécutée.

Les sources BB.tsv et CB.tsv sont vérifiées par leurs empreintes originales. Les mêmes adresses et séparations sont reconstruites : 52 736 lignes d’entraînement et 17 579 de validation. L’imputation médiane est apprise uniquement sur l’entraînement. Seuls les paramètres déjà sauvegardés sont réajustés, car aucun modèle ajusté historique n’était exporté. Les caractéristiques et prédictions du test réservé ne sont pas transformées ni calculées.

Avant le diagnostic, les huit métriques de validation sont comparées aux valeurs historiques avec une tolérance absolue de 1e-12. La reproduction réussit : précision 34,95 %, rappel 27,48 %, F1 30,77 %, average precision 24,69 %. La matrice est TP=72, FN=190, FP=134, TN=17 183, relativement aux catégories de la source.

## Catégories et valeurs manquantes avant imputation

| Catégorie source | Profil | Effectif | Alertes | Taux d’alerte |
| --- | --- | ---: | ---: | ---: |
| benign | Tous | 17317 | 134 | 0.77% |
| benign | Aucune valeur manquante | 14501 | 131 | 0.90% |
| benign | Au moins une valeur manquante | 2816 | 3 | 0.11% |
| Hack | Tous | 142 | 33 | 23.24% |
| Hack | Aucune valeur manquante | 141 | 33 | 23.40% |
| Hack | Au moins une valeur manquante | 1 | 0 | 0.00% |
| Theft | Tous | 120 | 39 | 32.50% |
| Theft | Aucune valeur manquante | 118 | 39 | 33.05% |
| Theft | Au moins une valeur manquante | 2 | 0 | 0.00% |

Pour Hack et Theft, le taux d’alerte est le rappel de la catégorie ; pour benign, c’est le taux de désaccord avec son étiquette négative. Les lignes « Tous » recouvrent les deux sous-groupes : ne pas additionner les trois lignes.

## Résultats scientifiques et limites

**187 des 190 omissions concernent des profils sans valeur manquante.** Ajouter uniquement des indicateurs de manque ne peut donc pas être présenté comme une correction démontrée du problème de rappel. Les trois profils positifs incomplets sont tous manqués, mais cet effectif est trop faible pour généraliser.

Le manque est beaucoup plus fréquent dans la catégorie benign (2 816/17 317) que dans les références Hack/Theft (3/262). Cette association peut refléter les comportements, les définitions de caractéristiques ou la collecte des sources ; le diagnostic ne distingue pas ces explications. Elle motive une baseline de manque seul pour évaluer un éventuel raccourci de source, sans conclure que le manque cause les erreurs.

Le JSON conserve aussi, pour chaque caractéristique et chaque résultat TP/FN/FP/TN, le nombre de cellules manquantes avant imputation. Il ne publie ni liste d’adresses accusées ni score individuel. Les motifs de manque et les taux sont descriptifs, sans test de causalité, attribution SHAP ou estimation de performance en population.

La validation a déjà servi au choix historique du modèle et du seuil. Ce diagnostic n’est donc pas une nouvelle évaluation indépendante. Les groupes d’entités/incidents restent inconnus, les catégories de source ne vérifient pas les rôles victime/attaquant, et les profils de vie entière restent rétrospectifs. Aucun seuil ni hyperparamètre n’est sélectionné sur ces résultats.

## Reproduction et contrôles

Depuis la racine du dépôt, avec les dépendances de `real_cats/requirements.txt` et un chemin de sortie neuf :

```bash
python "Task 2/real_cats/analyze_validation_errors.py" \
  /chemin/Real-CATS \
  "Task 2/real_cats/results_20261013/metrics.json" \
  /chemin/nouveau_diagnostic.json
python -m unittest discover -s "Task 2/real_cats" -p 'test*.py'
```

Le résultat exécuté est `validation_errors_20261018.json`. Il contient les versions de bibliothèques, les paramètres, les caractéristiques et les empreintes des sources, du rapport historique et des appartenances entraînement/validation. Les 25 tests Real-CATS réussissent, dont trois nouveaux sur la cohérence des sous-groupes, les catégories absentes et les entrées invalides.

## Prochaine unité ML

Comparer une baseline fondée uniquement sur les indicateurs de manque aux baselines constantes, sur entraînement/validation uniquement et avec configuration fixée avant exécution. Ce diagnostic de raccourcis de source doit conserver toutes ses métriques, sans ajuster le modèle externe ou utiliser le test réservé.
