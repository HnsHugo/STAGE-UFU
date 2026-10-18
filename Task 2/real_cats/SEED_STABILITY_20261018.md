# Stabilité algorithmique sur trois graines — 18 octobre 2026

## Protocole exécuté

Les graines 42, 43 et 44 ont été fixées avant cette expérience, pour la forêt complète à 22 variables et la variante à 13 variables sans la famille des montants. Les mêmes 52 736 lignes d’entraînement et 17 579 de validation sont utilisées. Seul random_state de la forêt change ; les graines du découpage ne changent pas.

Les résultats de la graine 42 sont réutilisés après contrôle des empreintes de sources, des appartenances aux splits, du rapport de référence, des versions de bibliothèques, des caractéristiques, du seuil et des paramètres. Seules quatre nouvelles forêts sont ajustées : deux configurations pour les graines 43 et 44. Les deux imputations sont apprises uniquement sur l’entraînement, puis réutilisées entre graines.

Paramètres inchangés : 100 arbres, profondeur maximale 20, minimum 20 lignes par feuille, max_features=sqrt, poids positifs 3, seuil strict >0,30. Les réserves concernant le nombre effectif de variables candidates par coupure (4 contre 3) restent applicables. Aucun modèle ni aucune graine n’est sélectionné, et le test réservé n’est pas transformé ou évalué.

## Résultats par graine

| Graine | AP complète | AP sans montants | F1 complet | F1 sans montants | Détections complètes / sans montants | Alertes benign complètes / sans montants |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 42 | 24.69% | 25.04% | 30.77% | 28.92% | 72 / 72 | 134 / 164 |
| 43 | 25.04% | 24.86% | 29.67% | 27.85% | 73 / 66 | 157 / 146 |
| 44 | 23.52% | 25.74% | 29.75% | 28.45% | 72 / 69 | 150 / 154 |

## Résumés descriptifs

| Mesure | Complète : moyenne ± écart-type | Sans montants : moyenne ± écart-type |
| --- | ---: | ---: |
| Average precision | 24.42% ± 0.65 points | 25.21% ± 0.38 points |
| Précision | 33.04% ± 1.38 points | 30.86% ± 0.26 points |
| Rappel | 27.61% ± 0.18 points | 26.34% ± 0.93 points |
| F1 | 30.07% ± 0.50 points | 28.41% ± 0.44 points |

Les écarts-types utilisent ddof=0 et décrivent uniquement ces trois graines. Ils ne sont ni des erreurs standards ni des intervalles de confiance de performance en population. Les graines partagent exactement les mêmes données et ne constituent pas trois jeux de test indépendants.

## Interprétation

Le delta d’AP moyen sans montants moins complet est de +0,79 point, mais varie de -0,18 à +2,21 points et change de signe. Il ne démontre pas un gain robuste ou statistiquement significatif. Au seuil commun, le F1 de la variante sans montants est inférieur sur les trois graines ; sa précision est aussi inférieure sur chacune. Ces observations ne justifient pas de remplacer le modèle historique.

Le réentraînement sans montants reste capable de produire un classement proche du modèle complet, en cohérence avec une redondance des informations. Cette conclusion ne constitue pas une contribution causale unique ni une preuve d’indépendance vis-à-vis des sources.

Cette étude porte sur une validation déjà examinée et fixe. Elle ne mesure pas la variabilité du split, des données, des entités ou des incidents. Les catégories source et les profils de vie entière conservent leurs limites de rôle et de temporalité. La forêt externe à 19 caractéristiques et son seuil de 0,15 restent préservés.

## Reproduire et tester

```bash
python "Task 2/real_cats/check_seed_stability.py" \
  /chemin/Real-CATS \
  "Task 2/real_cats/validation_errors_20261018.json" \
  "Task 2/real_cats/monetary_ablation_20261018.json" \
  /chemin/nouveaux_resultats.json
python -m unittest discover -s "Task 2/real_cats" -p 'test*.py'
```

Résultats : `seed_stability_20261018.json`, avec métriques et catégories pour chaque graine, statistiques appariées, versions et provenance des deux caches. Les 39 tests Real-CATS réussissent, dont quatre nouveaux pour la couverture des graines, les différences appariées, la définition de dispersion et le rejet d’un cache au seuil modifié.

## Prochaine unité ML

Introduire une baseline de régression logistique régularisée avec un prétraitement et des paramètres fixés avant exécution, appris sur l’entraînement seulement. Comparer son classement AP sur la validation aux références sauvegardées, sans recherche de seuil ni sélection sur le test réservé. Cette autre famille de modèle apportera plus d’information qu’une prolongation indéfinie de la recherche de graines.
