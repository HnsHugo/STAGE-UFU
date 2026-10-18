# Baselines de manque seul — 18 octobre 2026

## Hypothèse et protocole fixé

Le diagnostic précédent a montré une fréquence de valeurs manquantes différente selon les catégories de source. Cette expérience vérifie le pouvoir de classement de ces indicateurs seuls, sans chercher à améliorer le modèle existant.

Le corpus vérifié par SHA256, les 52 736 observations d’entraînement et les 17 579 observations de validation sont identiques au diagnostic précédent ; leurs empreintes d’appartenance sont contrôlées. Aucun contenu prédictif du test réservé n’est transformé ou évalué.

Les 22 variables numériques originales sont remplacées chacune par un indicateur binaire : 1 si manquante, non numérique ou non finie, 0 sinon. Les valeurs numériques elles-mêmes ne sont jamais fournies aux modèles. Aucune imputation n’est nécessaire.

Trois baselines prédéfinies : score constant égal à la prévalence d’entraînement ; arbre de profondeur maximale 2 et minimum 20 observations par feuille sans pondération ; même arbre avec poids équilibrés calculés sur l’entraînement. Seed 42, coupures apprises sur l’entraînement seulement. Toutes utilisent le seuil strict >0,5. Aucun modèle, seuil ou hyperparamètre n’est sélectionné à partir de cette validation.

## Résultats exécutés

| Modèle | Average precision | Précision | Rappel | F1 | Références positives détectées | Alertes sur catégorie benign |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Score constant | 1.49% | 0.00% | 0.00% | 0.00% | 0/262 | 0 |
| Manque seul, sans pondération | 1.75% | 0.00% | 0.00% | 0.00% | 0/262 | 0 |
| Manque seul, poids équilibrés | 1.75% | 1.75% | 98.85% | 3.45% | 259/262 | 14501 |
| Forêt numérique historique, seuil 0,30 | 24.69% | 34.95% | 27.48% | 30.77% | 72/262 | 134 |

La comparaison des points de fonctionnement doit tenir compte des seuils et pondérations différents : 0,5 pour les nouvelles baselines, 0,30 précédemment sélectionné pour la forêt. L’average precision compare le classement sans choisir un nouveau seuil. Le score constant obtient la prévalence positive de validation, comme attendu.

## Interprétation

Le manque seul améliore légèrement le classement par rapport au score constant, mais ne reproduit pas les performances de la forêt numérique. Aucun effet causal de collecte ou de source n’est établi.

Deux motifs de manque sont observés dans l’entraînement et la validation, sans motif inédit en validation. Dans le diagnostic de validation, toutes les cellules absentes concernent max_sent_amount et min_sent_amount. Les deux arbres utilisent une seule coupure sur missing__max_sent_amount ; les règles sont sauvegardées intégralement dans le JSON. Avec pondération équilibrée, l’absence de manque produit une alerte et le manque produit une absence d’alerte. Sans pondération, les deux feuilles prédisent la classe négative au seuil fixé, tout en donnant deux scores de classement distincts.

Ces absences peuvent traduire une absence d’activité d’envoi, une définition de variable ou la collecte. Leur cause n’a pas été vérifiée. La présence simultanée des deux indicateurs empêche d’attribuer à un seul un effet indépendant.

Les poids équilibrés alertent 14 760 profils, dont 14 501 de catégorie benign : un rappel très élevé ne démontre pas un détecteur utile. Les catégories sont celles de Real-CATS, sans preuve indépendante de rôles victime/attaquant. Les relations d’entités/incidents restent inconnues, les profils sont rétrospectifs, et les scores ne sont pas des probabilités calibrées de vol.

Cette étude utilise une validation déjà inspectée ; elle reste un diagnostic de développement. Aucun gain en généralisation externe ni absence de biais de source ne sont démontrés. La forêt historique n’est pas réentraînée dans cette unité et le modèle externe figé reste intact.

## Reproduction et tests

```bash
python "Task 2/real_cats/compare_missingness_baselines.py" \
  /chemin/Real-CATS \
  "Task 2/real_cats/validation_errors_20261018.json" \
  /chemin/nouveaux_resultats.json
python -m unittest discover -s "Task 2/real_cats" -p 'test*.py'
```

Résultat sauvegardé : `missingness_baselines_20261018.json`. Le script refuse d’écraser un résultat existant. Les 29 tests Real-CATS passent, dont quatre nouveaux vérifiant la suppression des valeurs, la conversion des valeurs non finies, la baseline constante et la borne stricte du seuil.

## Prochaine unité ML

Étudier l’importance par permutation des familles de caractéristiques de la forêt numérique historique, sur validation uniquement, avec score average precision, seed et répétitions fixés avant exécution. Regrouper les variables fortement liées avant de permuter pour limiter les combinaisons artificielles ; documenter qu’une importance de permutation n’est pas une explication causale. Ne pas sélectionner de nouveaux paramètres sur le test réservé.
