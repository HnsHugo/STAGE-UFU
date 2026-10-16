# Bilan du travail récupéré et sauvegardé

Point de sauvegarde du 16 octobre 2026 UTC (15 octobre au Brésil). Les résultats ci-dessous proviennent des exécutions antérieures conservées. La récupération a uniquement vérifié les fichiers et relancé les tests ; aucune nouvelle expérience n'a été lancée.

## Réalisé et documenté

- Les consignes des pages 97 et 99 du support d'Ivan sont reliées aux livrables dans [l'audit des exigences](REQUIREMENTS_AUDIT.md).
- L'[exercice de 100 paiements et 100 comparaisons](coldcard/COURSE_EXERCISE.md) fournit les dix caractéristiques, la cohorte, l'arbre et les résultats. Les 60 prédictions correctes sur le petit test lié à la même adresse ne démontrent pas une détection indépendante. L'application au reste du corpus produit 8 158 alertes sur 492 135 transactions non attribuées.
- L'[analyse des flux](coldcard/case_flows_20261015/CASE_FLOWS_FR.md) et sa [vérification](coldcard/case_flows_20261015/VERIFICATION_FR.md) conservent les montants, les fenêtres temporelles, la couverture des parents et les relevés datés des cinq consolidations. Les 594,47728031 BTC reçus ne constituent pas un montant volé certifié.
- L'[audit externe](real_cats/EXTERNAL_INDEPENDENCE_AUDIT.md) couvre onze historiques et distingue les dépendances observables. FSF partage deux transactions à nombreux destinataires avec deux adresses d'entraînement. Cela établit un chevauchement de données, sans prouver une propriété commune ni mesurer son effet sur le score.
- La [démonstration hors ligne](DEMO.md), son rapport sauvegardé et les résultats des reproductions antérieures sont conservés. Le modèle externe à 19 caractéristiques et le seuil strict de 0,15 restent inchangés.

## Vérification lors de la récupération

Les six suites disponibles réussissent : **106 tests** (21 collecte, 41 Coldcard, 7 Elliptic++, 6 cas de vol, 22 Real-CATS, 9 démonstration). Le [journal intégral](verification_20261015/recovery_tests_20261016.json) conserve les commandes et leurs sorties. Les historiques bruts et les gros jeux de données restent hors de Git ; leurs empreintes sont documentées.

## Ce qui reste partiel

Les pistes de destinations ne sont pas de nouveaux vols confirmés. Les étiquettes indépendantes de rôle, d'incident et d'entité restent insuffisantes pour évaluer une détection de nouveaux vols. Le classifieur cold nécessite davantage d'entités et des preuves d'usage datées. Les benchmarks sur les catégories des sources, les observations descriptives et la validation indépendante restent distincts.

Pour Ivan : « L'exercice et les calculs de flux sont reproductibles. Le modèle reconnaît certaines caractéristiques du corpus, mais ses alertes ne suffisent pas à attribuer un vol ou un appareil matériel. L'audit révèle aussi des dépendances entre données externes et données d'entraînement ; nous conservons ces limites et les résultats défavorables. »
