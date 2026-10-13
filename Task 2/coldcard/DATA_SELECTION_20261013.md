# Données retenues pour la prochaine expérience

## Deux objectifs distincts

1. Apprendre à entraîner et évaluer un modèle d'adresses : benchmark Elliptic++.
2. Détecter des adresses recevant/détenant des fonds volés : corpus d'affaires documentées, encore insuffisant pour une classification supervisée fiable.

Les étiquettes « illicite » d'Elliptic++ ne signifient pas « fonds volés ».
Ces corpus ne doivent pas être fusionnés sans une définition commune de la cible et des caractéristiques.

## Elliptic++ : benchmark pédagogique sélectionné

Source des auteurs : https://github.com/git-disl/EllipticPlusPlus
Publication : https://arxiv.org/abs/2306.06108
Révision inspectée : `08fe6aded83afb97bf5a79a71130f542ca783c2e`.

Le fichier des classes a été téléchargé et son SHA-256 vérifié. Comptage réel :

| Classe originale | Sens fourni par les auteurs | Adresses |
| --- | --- | ---: |
| 1 | Illicite | 14 266 |
| 2 | Licite | 251 088 |
| 3 | Inconnu | 557 588 |

Total : 822 942 adresses distinctes, zéro doublon dans le fichier de classes.
Les 265 354 adresses étiquetées 1/2 peuvent servir au benchmark supervisé.
Les inconnues sont exclues de son évaluation binaire, pas transformées en licites.

Fichiers originaux :
- `wallets_classes.csv` : 30 421 134 octets, SHA-256 `4e5132c99f941666bf1fefd4100a1428d339c9252ec6987909e1adf8eac902f9`.
- `wallets_features.csv` : 606 463 522 octets annoncés par le pointeur Git LFS, SHA-256 attendu `317daca2810c355ddfdb8c0dab34cf11d1aa90567fe975090c7e5a901386eb77`.

L'en-tête des caractéristiques a été effectivement lu : adresse, pas temporel,
activité envoyée/reçue, montants, frais, intervalles en blocs, etc.
Le fichier complet des caractéristiques n'a pas encore été téléchargé ni audité.
Les nombres de lignes, valeurs manquantes et répétitions temporelles devront être vérifiés.
Le dépôt fournit des notebooks pédagogiques de classification et visualisation.

Téléchargement reproductible, avec vérification des empreintes :

```bash
python download_ellipticplusplus.py /tmp/ellipticplusplus
```

Ne pas ajouter les gros CSV à Git. Le téléchargement est fixé à la révision inspectée.
La disponibilité publique ne suffit pas à autoriser une redistribution commerciale :
examiner les conditions des auteurs avant réutilisation dans la future V2.

## Séparation entraînement / validation / test proposée

À confirmer après l'audit du fichier des caractéristiques :
- une adresse ne doit apparaître que dans un seul ensemble, même si elle a plusieurs lignes temporelles ;
- utiliser l'entraînement pour apprendre les règles, la validation pour les choix de paramètres, et conserver le test pour l'évaluation finale ;
- une première séparation par adresse, stratifiée par classe (60/20/20), sert de référence pédagogique ;
- ce découpage ne prouve pas l'indépendance entre entités ou affaires ;
- un test temporel séparé est utile seulement après avoir vérifié que les caractéristiques ne résument pas des événements futurs ; les colonnes de durée totale et dernière apparition exigent une attention particulière ;
- ne pas comparer directement les scores de ce benchmark aux scores du proxy Coldcard : la cible et l'unité d'observation changent.

Aucun ensemble train/test n'a encore été matérialisé : les caractéristiques doivent d'abord être auditées.

## Corpus de vols : références externes

### Groupe FBI, août 2023

Six adresses, 22 transactions distinctes déjà collectées et contrôlées selon
les compteurs de Blockstream. Source et résultats : `theft_seed_registry_20261010.json`
et `theft_history_20261010/`.

Rôle : détenteurs de fonds volés attribués par le FBI, pas adresses victimes.
Un seul groupe de référence, agrégeant plusieurs vols. Pas de six affaires indépendantes.

### Binance, mai 2019 : nouvelle affaire réservée à l'examen externe

Source primaire : https://www.binance.com/en/support/announcement/detail/360028031711
Binance publie la transaction :
`e8b406091959700dbffcff30a60b190133721e5c39e89bb5fe23c5a554ab05ea`.

La transaction a été téléchargée depuis Blockstream et conservée dans
`external_cases/binance_2019_transaction.json` avec sa référence de bloc.
La réponse contient 71 entrées et 44 sorties. Ne pas étiqueter toutes les sorties
comme volées : le communiqué identifie une transaction, pas le rôle de chacune de ses sorties.
Ce cas est réservé comme affaire externe exploratoire avant tout entraînement.
Une attribution documentée des sorties reste nécessaire pour un test d'adresses.

### Bitfinex, août 2016 : piste à compléter

Sources primaires :
- https://www.justice.gov/archives/opa/pr/bitfinex-hacker-and-wife-plead-guilty-money-laundering-conspiracy-involving-billions
- https://www.justice.gov/d9/press-releases/attachments/2022/02/08/statement_of_facts_pacer.pdf

Affaire documentée, mais la pièce judiciaire utilise notamment un préfixe de cluster
« 1CGA4s ». Un préfixe ou un cluster ne suffit pas à établir une liste d'adresses complètes.
Aucune adresse n'est ajoutée sur cette seule base.

## Limites restantes pour l'objectif fonds volés

Il manque encore des affaires supplémentaires avec des rôles d'adresses vérifiables,
des périodes d'observation harmonisées et un groupe de comparaison approprié.
Un signalement absent n'est pas une preuve de légitimité.
Le benchmark Elliptic++ permet de progresser en ML pendant la constitution de ce corpus,
mais ne valide pas un détecteur de bitcoins volés ni de portefeuilles matériels.
