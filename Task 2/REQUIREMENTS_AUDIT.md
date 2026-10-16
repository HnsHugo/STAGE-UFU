# Exigences retrouvées et état de la Task 2

Audit du 15 octobre 2026. La source primaire retrouvée est le support `aula4.pdf`, Ivan Sendin, FACOM/UFU, daté du 24 septembre 2026, 99 pages, fourni par Hugo. Les pages 97 et 99 précisent l'exercice Coldcard. Le fichier original reste conservé séparément ; les références de pages ci-dessous permettent de vérifier le périmètre sans republier le support complet.

Les messages rapportés du 8 octobre ajoutent une priorité d'entraînement/validation sur les blocs fournis, puis un jeu d'adresses liées à des vols. Cette priorité est cohérente avec le support. Aucun énoncé distinct signé fixant une métrique minimale, une architecture ou une échéance n'a été retrouvé. Les anciens plans proposés par l'assistant ne constituent pas des exigences du professeur.

| Demande et provenance | Travail vérifié | État et limite |
| --- | --- | --- |
| P.97 : récupérer les transactions payant `bc1qnk...ecp0` | 504 paiements dans les blocs ; historique fournisseur complet de 507 transactions, dont 506 entrantes | Réalisé ; les deux paiements supplémentaires sont hors du corpus de blocs |
| P.97 : caractéristiques size, weight, fee, statistiques des valeurs, nombres d'entrées/sorties | Dix caractéristiques dans `coldcard/course_baseline.py` | Réalisé ; `v` interprété comme les valeurs des sorties, car la diapositive ne le définit pas explicitement |
| P.97 : 100 transactions du cas, 100 autres, arbre de décision | Cohorte déterministe de 200 transactions, séparation 140/60, arbre et prédictions exécutés | Réalisé comme exercice de relation à une adresse ; les comparaisons restent non attribuées |
| P.99 : combien a été volé ? | Flux reçus, sous-ensemble consolidé et frais calculés dans `case_flows_20261015/` | Flux mesurés ; aucun montant volé total indépendamment certifié |
| P.99 : combien d'adresses sources ? | Adresses des entrées comptées, avec couverture et valeurs manquantes | Réalisé comme nombre d'adresses observées, pas comme nombre de victimes |
| P.99 : pendant combien de temps ? | Période complète des réceptions, fenêtre des parents et intervalle jusqu'à la consolidation | Réalisé ; timestamps fournisseur et confirmations distingués du début réel de l'incident |
| P.99 : comment les fonds sont-ils dépensés ? | Dépense de la collectrice, cinq consolidations, contrôles datés des sorties | Réalisé au premier niveau observable ; cinq sorties indiquées non dépensées lors du relevé |
| P.99 : le classifieur est-il bon ? | Exercice simple, expériences aléatoire/chronologique et validation par groupe ; anciens résultats reproduits | Réalisé ; score simple trop favorable, forte dépendance aux frais, échec sur un groupe |
| P.99 : trouver d'autres destinations et vérifier leur qualité | Application de l'arbre simple à 492 135 transactions inutilisées, 8 158 alertes, vingt destinations à examiner ; suivi des consolidations | Recherche exécutée ; aucune nouvelle destination confirmée comme liée à un vol |
| P.99 : dataset d'adresses cold et classifieur | Pilote de collecte et [contrôle d’éligibilité daté](part%201/STORAGE_READINESS.md) : six fenêtres complètes, zéro adresse éligible | Partiel : trop peu d'entités/contre-exemples fiables ; cold storage et appareil hardware restent distincts |
| Suite rapportée : modèle sur adresses liées à des vols | Benchmarks Elliptic++ et Real-CATS ; pilote externe FBI/Binance/BTCPay/EFF/FSF | Benchmarks et scores descriptifs exécutés ; validation indépendante de détection de vol encore insuffisante |

## Vérification de l'indépendance

Le contrôle d'adresse exacte n'est qu'une première vérification. Le nouvel audit examine aussi les transactions, les liens parent-enfant et les co-adresses observées. Il ne permet pas d'identifier automatiquement les propriétaires. Les onze adresses du pilote ne forment pas onze incidents indépendants. Les limites révélées sont conservées même lorsqu'elles rendent l'évaluation moins favorable.

## Extensions et points à clarifier

CPFP et WalletExplorer appartiennent au plan initial conservé dans le dépôt. La recherche CPFP n'est pas une obligation explicite dans les pages 97 et 99 retrouvées ; aucune conclusion CPFP n'est déduite d'un taux de frais élevé. GNN/GCN, SHAP et l'interface font partie du projet de stage plus large, et n'ont pas été ajoutés à cet exercice au détriment de sa validation.

Pour transformer les expériences en détecteur de nouveaux vols, les éléments manquants sont surtout des étiquettes de rôle et d'incident vérifiables, une comparaison indépendante et une politique temporelle homogène. Pour un classifieur cold, il faut préciser la propriété visée et obtenir des preuves d'usage associées à des périodes et à davantage d'entités. Un changement de seuil ou un modèle plus complexe ne remplace pas ces données.

## Navigation

- [Exercice du cours et recherche de candidats](coldcard/COURSE_EXERCISE.md)
- [Réponses sur les flux](coldcard/case_flows_20261015/CASE_FLOWS_FR.md)
- [Validation groupée historique](coldcard/GROUPED_EXPERIMENT.md)
- [Démonstration hors ligne](DEMO.md)
- [Résumé à présenter à Ivan](BILAN_FR.md)
