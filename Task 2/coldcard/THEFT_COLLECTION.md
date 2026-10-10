# Première collecte d'adresses associées à des fonds volés

## Objectif et provenance

Le registre `theft_seed_registry_20261010.json` contient six adresses Bitcoin
publiées par le FBI le 22 août 2023. Le communiqué les décrit comme détenant
des fonds provenant de plusieurs vols attribués à TraderTraitor.
Source : https://www.fbi.gov/news/press-releases/fbi-identifies-cryptocurrency-funds-stolen-by-dprk

Le rôle enregistré est `reported_stolen_funds_holder`, pas victime.
Le type de portefeuille matériel et l'affaire d'origine de chaque adresse
restent inconnus. Les six adresses appartiennent au même groupe de validation :
le communiqué ne permet pas de les répartir entre des affaires indépendantes.

## Collecte reproductible

```bash
python collect_theft_seeds.py theft_seed_registry_20261010.json nouvelle_collecte
python -m unittest discover -p test_theft_collection.py
```

Le dossier de sortie doit être nouveau. Le script vérifie les sommes de contrôle
Base58Check, récupère les transactions confirmées via l'API Esplora de Blockstream,
parcourt les pages jusqu'à une page vide, puis compare les compteurs avant/après
avec les montants et le nombre de sorties reçues/dépensées reconstruits.
Les transactions sont conservées avec leur hauteur et hash de bloc fourni par l'API.
Documentation : https://github.com/Blockstream/esplora/blob/master/API.md

Un compteur stable et une pagination exhaustive justifient une couverture complète
selon ce fournisseur. Ce contrôle n'est pas une vérification cryptographique
d'inclusion ni un accord entre fournisseurs indépendants. Le mempool est exclu.
Une erreur ou une différence de compteurs rend le manifeste incomplet.
Les fichiers ont des empreintes SHA-256 et le manifeste référence celle du registre.

## Usage pour le futur modèle

Les données constituent une collecte de références, pas encore un dataset supervisé.
L'attribution concerne les adresses à la date du communiqué ; elle ne transforme
pas toutes leurs transactions historiques ou ultérieures en vols confirmés.
Une transaction de poussière reçue ultérieurement peut être sans rapport avec le vol.

Les futurs exemples devront avoir une fenêtre temporelle documentée, un rôle,
un groupe d'affaire et des caractéristiques calculées uniquement avec les données
connues à la date de prédiction. Un historique récupéré aujourd'hui ne doit pas
introduire les dépenses futures dans un exemple censé être évalué en août 2023.
Le montant cumulé reçu sur une adresse n'est pas automatiquement le montant volé ;
les transferts entre adresses du registre ne doivent pas être comptés plusieurs fois.

Prochain travail : examiner les mouvements de la période du communiqué, chercher
d'autres affaires indépendantes, puis définir la cible (adresse victime ou détentrice
de fonds volés) avant d'entraîner un modèle d'adresses.
