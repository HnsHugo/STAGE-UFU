# Baselines univariées sur les groupes Coldcard — 16 octobre 2026

## Hypothèse et protocole

L’arbre historique exploite fortement les frais. Cette expérience mesure ce qu’apportent trois baselines interprétables à une seule coupure : taux de frais, nombre de sorties et montant total des sorties. Les trois variables et hyperparamètres ont été fixés avant cette exécution. Toutes les baselines sont publiées ; aucune n’est sélectionnée sur les résultats.

Les 493 468 transactions éligibles et les quatre groupes de candidats sont identiques à l’expérience historique : 1 070 candidats, 492 398 transactions non attribuées. Chaque groupe candidat est entièrement exclu de l’entraînement de son pli ; le fond est réparti par le même hash TXID. Chaque ligne est prédite une seule fois hors entraînement. Le rapport conserve les empreintes du corpus, du fichier de groupes, des métriques historiques et des affectations aux plis.

Chaque modèle est un arbre de profondeur 1, minimum 20 observations par feuille, poids de classes équilibrés appris sur l’entraînement, seed 42. La coupure est ajustée uniquement sur les trois autres groupes et leur fond d’entraînement. La classe prédite est celle de sklearn, sans seuil ajusté après inspection. Aucun jeu de validation n’est utilisé pour sélectionner des paramètres : cette comparaison entièrement prédéfinie ne fait aucune sélection. Les groupes étant déjà inspectés auparavant, il s’agit d’un diagnostic de développement, pas d’un nouveau test réservé.

## Résultats réellement exécutés

| Méthode | Candidats retrouvés | Alertes sur fond inconnu | Précision proxy | Rappel proxy | F1 proxy | Rappel moyen des groupes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Taux de frais seul | 1036/1070 | 7878 | 11.62% | 96.82% | 20.75% | 75.00% |
| Nombre de sorties seul | 1070/1070 | 54510 | 1.93% | 100.00% | 3.78% | 100.00% |
| Montant des sorties seul | 892/1070 | 64571 | 1.36% | 83.36% | 2.68% | 67.77% |
| Arbre historique complet, sans réentraînement | 874/1070 | 1072 | 44.91% | 81.68% | 57.96% | 55,20 % |

## Détail par groupe réservé

| Groupe, préfixe | Candidats | Frais seuls : retrouvés / alertes | Sorties seules : retrouvés / alertes | Montants seuls : retrouvés / alertes |
| --- | ---: | ---: | ---: | ---: |
| 0c6bf853a645 | 341 | 341 / 410 | 341 / 13677 | 341 / 19928 |
| 14edd9ee8445 | 491 | 491 / 6539 | 491 / 13604 | 491 / 20171 |
| 38b6dc366fca | 34 | 0 / 425 | 34 / 13531 | 17 / 16044 |
| 4b50d61a3d6e | 204 | 204 / 504 | 204 / 13698 | 43 / 8428 |

## Interprétation et limites

Le modèle historique réduit les alertes par rapport à chacune des baselines, mais son rappel global et son rappel moyen par groupe sont inférieurs à ceux des frais seuls. La baseline de nombre de sorties retrouve tous les candidats au prix de 54 510 alertes : le rappel seul ne suffit donc pas à juger la qualité. Une amélioration sur F1 peut masquer des groupes moins bien couverts.

Le taux de frais seul manque le groupe de 34 candidats. Les règles exactes par pli sont sauvegardées dans le JSON. Cela documente une dépendance aux régimes de frais ; cela n’identifie ni appareil, ni propriétaire, ni vol. Les alertes sur le fond inconnu ne sont pas des faux positifs certifiés. Les métriques restent celles d’une relation candidate à un cas unique.

Les groupes candidats ne sont pas des incidents externes indépendants. Les liens entre entités du fond et les transactions absentes restent inconnus. Aucune séparation chronologique n’est imposée : ces données rétrospectives n’établissent pas une détection en temps réel. Aucun intervalle de confiance calculé en traitant chaque transaction comme indépendante n’est ajouté. Les modèles et résultats historiques, ainsi que la forêt externe figée, sont préservés.

## Reproduire et tester

Depuis la racine, avec les dépendances Coldcard et un fichier de sortie neuf :

```bash
python "Task 2/coldcard/compare_grouped_baselines.py" \
  /chemin/transactions.csv.gz /chemin/candidate_groups.json /chemin/manifest.json \
  "Task 2/coldcard/grouped_results_20261008/metrics.json" \
  /chemin/nouveaux_resultats.json
python -m unittest discover -s "Task 2/coldcard" -p 'test*.py'
```

Le résultat de cette exécution est `grouped_baselines_20261016.json`. Les 45 tests Coldcard réussissent, dont quatre nouveaux sur les seuils appris hors test, les variables constantes, les valeurs non finies et les métriques en présence d’un fort déséquilibre.

## Prochaine unité ML

Analyser les erreurs de validation Real-CATS par catégorie et motif de valeurs manquantes, sans modifier le modèle externe ni régler de paramètres sur le test réservé déjà inspecté. Si un modèle doit être réajusté pour obtenir les prédictions de validation, reproduire uniquement les paramètres et le split figés ; conserver ce diagnostic dans une nouvelle expérience.
