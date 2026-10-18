# Ablation de la famille des montants — 18 octobre 2026

## Hypothèse et protocole

La permutation précédente faisait fortement baisser l’AP en déplaçant les montants sans réentraîner le modèle. Cette expérience distincte retire les neuf variables de la famille monetary et réentraîne la même configuration pour vérifier si les autres informations peuvent compenser ce retrait.

Les sources sont vérifiées par SHA256, les appartenances entraînement/validation sont identiques au diagnostic précédent : 52 736 / 17 579 adresses. La forêt conserve 100 arbres, profondeur maximale 20, minimum 20 observations par feuille, max_features=sqrt, poids positifs 3 et seed 42. Le seuil est fixé à score strictement supérieur à 0,30, sans recherche de seuil. Les médianes sont apprises uniquement sur les colonnes retenues de l’entraînement. Les 13 variables restantes ne contiennent aucune cellule manquante sur entraînement/validation.

Les montants retirés sont le solde, les totaux reçus/envoyés, les extrema reçus/envoyés et les variances de montants. Les frais restent présents : ce n’est pas un retrait de toute information financière. Les listes complètes, paramètres, versions et empreintes sont sauvegardés dans `monetary_ablation_20261018.json`.

## Résultats de validation exécutés

| Mesure | Forêt complète historique, sans nouvel ajustement | Sans famille des montants, réentraînée |
| --- | ---: | ---: |
| Average precision | 24.69% | 25.04% |
| Précision | 34.95% | 30.51% |
| Rappel | 27.48% | 27.48% |
| F1 | 30.77% | 28.92% |
| Références positives détectées | 72 | 72 |
| Références positives manquées | 190 | 190 |
| Alertes sur catégorie benign | 134 | 164 |

| Catégorie positive | Détections historiques | Détections sans montants |
| --- | ---: | ---: |
| Hack | 33/142 | 24/142 |
| Theft | 39/120 | 48/120 |

## Interprétation

L’AP sans montants atteint 25,04 %, soit +0,35 point par rapport à la référence de 24,69 %. Cette petite différence sur une seule graine et une seule validation ne démontre pas une amélioration statistique ou une meilleure généralisation.

Au seuil fixé, la précision et le F1 baissent ; 30 alertes supplémentaires apparaissent sur la catégorie benign. Le total de 72 détections reste identique, mais la répartition Hack/Theft change. Un même total ne garantit donc pas la détection des mêmes profils ; aucun chevauchement individuel n’est inféré des seuls agrégats.

**Permutation et ablation répondent à des questions différentes.** L’ancienne forêt dépend des montants dans ses règles apprises (AP 4,28 % après permutation), mais une nouvelle forêt peut exploiter les autres familles une fois les montants retirés. La forte importance par permutation n’établit pas que cette famille est irremplaçable après réentraînement.

## Limites

Le paramètre max_features=sqrt reste identique, mais le nombre effectif de variables candidates par coupure passe de 4 pour 22 variables à 3 pour 13. Le retrait change donc aussi les interactions et la diversification des arbres ; la comparaison ne mesure pas une contribution causale unique des montants.

L’hypothèse d’ablation provient d’une validation déjà examinée : diagnostic de développement, pas nouvelle évaluation indépendante. Aucun modèle gagnant, seuil ou hyperparamètre n’est choisi. Le test réservé n’est ni transformé ni évalué, et le modèle externe figé n’est pas modifié. Les limites des catégories de source, des groupes d’entités/incidents inconnus et des profils rétrospectifs restent applicables.

## Reproduction et tests

```bash
python "Task 2/real_cats/ablate_monetary_features.py" \
  /chemin/Real-CATS \
  "Task 2/real_cats/validation_errors_20261018.json" \
  /chemin/nouveaux_resultats.json
python -m unittest discover -s "Task 2/real_cats" -p 'test*.py'
```

Les 35 tests Real-CATS réussissent, dont trois nouveaux vérifiant le retrait exact de la famille, la conservation du schéma initial, le rejet de variables inconnues et les décomptes par catégorie. Les matrices de confusion sont réconciliées avec les 262 références positives et 17 317 profils de catégorie benign de validation.

## Prochaine unité ML

Comparer la stabilité des deux configurations sur les graines prédéfinies 42, 43 et 44, avec split et seuil inchangés et sans choisir une graine gagnante. Réutiliser les résultats de la graine 42 déjà sauvegardés lorsque leur provenance concorde. Cette vérification de stabilité algorithmique ne remplacera pas une validation indépendante par entités/incidents.
