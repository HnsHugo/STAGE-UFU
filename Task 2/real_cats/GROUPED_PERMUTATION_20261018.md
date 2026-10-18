# Importance par permutation de familles — 18 octobre 2026

## Expérience exécutée

Cette expérience mesure la dépendance de la forêt historique à 22 variables envers quatre familles fixées avant le calcul. Elle réajuste uniquement sa configuration historique sur les 52 736 profils d’entraînement, puis travaille sur les 17 579 profils de validation. La médiane d’imputation est apprise sur l’entraînement seulement. Les empreintes des deux sources et des appartenances aux séparations sont vérifiées. Le test réservé n’est ni transformé ni évalué.

L’average precision (AP) de référence, 24,6924526106 %, est reproduite avec tolérance absolue 1e-12. Aucun seuil n’est choisi : l’AP mesure ici le classement des références positives parmi les profils de validation.

Quatre familles couvrent chaque caractéristique exactement une fois : montants/solde (9), compteurs d’activité (7), temps/activité temporelle (4), frais (2). Les listes exactes sont sauvegardées dans le JSON. Chaque famille est déplacée conjointement selon une permutation des lignes, les autres colonnes restant fixes. Après imputation par des statistiques fixes, cette opération conserve les valeurs jointes de la famille, y compris les médianes remplaçant ses valeurs manquantes.

Cinq permutations sont tirées avec numpy.default_rng(42) et réutilisées pour toutes les familles afin de limiter la variabilité de comparaison. Un contrôle déplace les 22 variables ensemble : il conserve le profil joint mais le dissocie de son étiquette. Les 25 AP perturbées, les cinq empreintes de permutation et les versions des bibliothèques sont enregistrées.

## Résultats réels

| Famille perturbée | AP moyenne après permutation | Baisse moyenne d’AP (points) | Écart-type de la baisse (points) |
| --- | ---: | ---: | ---: |
| Montants et solde | 4.28% | 20.41 | 0.47 |
| Compteurs d’activité | 7.88% | 16.82 | 0.77 |
| Durée et activité temporelle | 11.15% | 13.55 | 0.61 |
| Frais | 12.56% | 12.13 | 0.91 |
| Contrôle : toutes les variables ensemble | 1.64% | 23.05 | 0.15 |

Le contrôle global obtient une AP moyenne de 1,64 %, proche de la prévalence positive de validation (1,49 %). Les différences entre ses cinq répétitions sont conservées ; elles ne constituent pas un intervalle de confiance en population.

## Interprétation et limites

Perturber les montants dégrade le plus le classement parmi ces familles prédéfinies. Les compteurs d’activité, les variables temporelles et les frais présentent eux aussi une baisse importante. Ce résultat complète la baseline précédente : le manque seul n’expliquait pas les performances de la forêt.

**Les baisses ne doivent pas être additionnées ni converties en parts de contribution.** Les familles ont des tailles différentes et interagissent ; une information peut être redondante. Le classement des familles n’est donc pas un classement intrinsèque des variables individuelles.

La permutation commune conserve les relations au sein de la famille déplacée, mais peut casser des dépendances entre familles : un ensemble de montants déplacé peut ne plus correspondre aux compteurs ou aux frais de sa nouvelle ligne. La mesure décrit la dépendance du modèle face à cette perturbation, pas une importance causale ni une contribution indépendante. Elle ne remplace pas une ablation avec réentraînement.

Les permutations par ligne ne tiennent pas compte de groupes d’entités/incidents inconnus. Les profils de vie entière restent rétrospectifs et les catégories source ne certifient pas les rôles victime/attaquant. La validation a déjà servi à sélectionner le modèle ; cette étude reste un diagnostic de développement. Le modèle externe à 19 caractéristiques et son seuil de 0,15 sont préservés.

## Reproduire et tester

```bash
python "Task 2/real_cats/grouped_permutation_importance.py" \
  /chemin/Real-CATS \
  "Task 2/real_cats/validation_errors_20261018.json" \
  /chemin/nouveaux_resultats.json
python -m unittest discover -s "Task 2/real_cats" -p 'test*.py'
```

Le résultat réel est `grouped_permutation_20261018.json`. Les 32 tests Real-CATS passent, dont trois nouveaux contrôlant les dépendances conjointes, l’absence de mutation des données, la permutation identité, le rejet de doublons et la couverture du schéma.

## Prochaine unité ML

Comparer une ablation sans la famille des montants à la configuration complète sur entraînement/validation, avec les mêmes paramètres et un seuil fixé avant le calcul. Cette expérience séparera la perturbation d’un modèle déjà ajusté de sa capacité à réapprendre sur les autres familles. Ne pas choisir de paramètres à partir du test réservé ni présenter la validation comme indépendante.
