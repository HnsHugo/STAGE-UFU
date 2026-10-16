# Exercice du support d'Ivan : 100 transactions + 100 comparaisons

Source primaire : `aula4.pdf`, Ivan Sendin, 24 septembre 2026, pages 97 et 99, fourni par Hugo. Le support désigne l'adresse `bc1qnk4zh9qcnap2mycp56qjrgza3cc8ylrh8fecp0`, dix caractéristiques et un arbre de décision. Il demande ensuite d'évaluer le classifieur et de chercher d'autres destinations. Le code et les résultats ci-dessous complètent cet exercice sans remplacer les expériences groupées existantes.

## Protocole exécuté

Les 98 blocs contiennent 493 571 transactions uniques, dont 504 paient l'adresse du cours. La cohorte contient 100 de ces paiements, sélectionnés par un classement SHA256 déterministe des TXID avec une graine 42, et 100 transactions non attribuées sélectionnées de la même manière dans les mêmes blocs, avec les mêmes effectifs par bloc. Les autres parents candidats, les cinq consolidations attribuées et les coinbase sont exclus du groupe de comparaison.

Les caractéristiques reprennent `size`, `weight`, `fee`, somme/minimum/maximum/moyenne/écart-type des valeurs, nombre d'entrées et de sorties. Nous interprétons les valeurs `v` comme celles des sorties, en satoshis ; le support ne définit pas explicitement `v`. L'écart-type est celui de la population (`ddof=0`). Adresse, TXID, bloc et étiquette ne sont pas des variables du modèle.

La séparation stratifiée fixe conserve 70 + 70 transactions pour l'apprentissage et 30 + 30 pour le test descriptif. Les paramètres choisis avant l'exécution sont profondeur 4, minimum 5 lignes par feuille et graine 42. Ils sont des choix d'implémentation, pas des consignes du support. Aucun réglage n'a été effectué à partir du résultat.

## Résultat et explication

| Test descriptif de 60 transactions | Nombre |
| --- | ---: |
| Paiements vers l'adresse retrouvés | 30 / 30 |
| Comparaisons non alertées | 30 / 30 |
| Erreurs observées dans cet échantillon | 0 |

Le comportement de classification appris se résume à **frais supérieurs à 2 815 satoshis**. La branche des frais inférieurs contient un découpage supplémentaire, mais ses deux feuilles prédisent la comparaison. Un total de frais n'est pas un taux de frais ; il dépend aussi de la taille de la transaction. Cette séparation décrit l'échantillon et ne caractérise pas un vol ou un appareil hardware.

Les ensembles partagent la même adresse et le même incident, et sont appariés sur les mêmes blocs. La prévalence artificielle de 50 % ne représente pas la blockchain. Les scores de 100 % ne sont donc pas une validation indépendante. La validation groupée historique reste plus informative : elle retrouve 874/1 070 candidats, avec 1 072 alertes de fond et un rappel moyen par groupe de 55,20 %.

## Recherche de destinations à examiner

L'arbre figé de cet exercice a été appliqué à **492 135 transactions non attribuées inutilisées**. Il en alerte **8 158**, dont les sorties désignent **79 413 adresses distinctes**. Le rapport conserve les vingt destinations apparaissant dans le plus grand nombre de transactions alertées, ainsi que trois TXID exemples au plus par destination.

Ce nombre d'adresses vient notamment des transactions à nombreuses sorties. Une alerte concerne une transaction ; elle ne désigne pas automatiquement toutes ses sorties comme malveillantes. Les montants agrégés sont des flux bruts de sorties, pas des soldes ou des montants volés. Aucune des vingt destinations n'est promue en nouvel incident confirmé. Le résultat répond à la recherche de candidats, mais montre surtout le besoin d'une vérification indépendante du rôle de chaque adresse.

Une revue complémentaire du 15 octobre compare les vingt pistes au registre du pilote initial et recherche des sources publiques pour les trois premières. La deuxième, `bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h`, était déjà une référence historique de Binance. La publication du compte officiel [Binance Blog, Our Commitment To Transparency](https://www.binance.com/en/square/post/51094) la cite dans un état des portefeuilles du 10 novembre 2022. Elle ne démontre ni son propriétaire actuel, ni son statut hot/cold individuel, ni l'origine de chaque paiement. Ce n'est donc pas une nouvelle adresse de vol découverte. Les autres pistes restent non résolues ; les résultats de recherche non corroborés n'ont pas été convertis en étiquettes. Le détail et les limites de cette revue bornée sont conservés dans `candidate_review_20261015.json`.

## Reproduction

Depuis `Task 2/coldcard`, avec un nouveau dossier de sortie :

```bash
python course_baseline.py /chemin/blocos.tgz /chemin/parents.json nouveau_resultat
python -m unittest discover -p 'test_course_baseline.py'
```

`course_results_20261014/` contient la cohorte de 200 lignes avec sa séparation, l'arbre lisible et le rapport avec les empreintes des entrées, les paramètres et les limites. Les trois tests vérifient les unités et l'écart-type, l'appariement par bloc indépendant de l'ordre de lecture, et le refus d'une comparaison insuffisante.
