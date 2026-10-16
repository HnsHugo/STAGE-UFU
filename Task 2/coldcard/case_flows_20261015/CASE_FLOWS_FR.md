# Cas Coldcard : réponses de flux vérifiées

Les rôles ci-dessous décrivent les transactions observées. Les montants ne sont pas une estimation indépendante du montant volé, et les adresses ne prouvent ni identité ni contrôle d'un portefeuille matériel.

## Adresse de l'exercice

`bc1qnk4zh9qcnap2mycp56qjrgza3cc8ylrh8fecp0`

Dans les 98 blocs fournis, 504 transactions alimentent cette adresse : **594.47725695 BTC** au total. La couverture du fichier seul est partielle.

L'historique confirmé collecté le 2026-10-14T23:02:05.172535+00:00 contient **507 transactions**, dont **506 entrantes** et **1 sortante(s)**. Pagination terminée et compteurs stables réconciliés : **594.47728031 BTC reçus**, **562.02666941 BTC en sorties consommées**, solde observé **32.45061090 BTC**. Il s'agit d'une vérification des compteurs du fournisseur, pas d'une preuve cryptographique.

Les transactions entrantes ont **505 adresses d'entrée distinctes** ; 0 emplacements d'entrée sans adresse décodée. Ce nombre n'est pas un nombre de victimes. 2 transactions de cet historique sont absentes des blocs fournis.

Les confirmations des réceptions vont du 2026-07-30T01:36:08+00:00 au 2026-08-19T03:21:08+00:00 (1734300 secondes). Cette durée d'activité complète n'est pas la durée démontrée d'un vol.

Les **341 sorties consommées** correspondent exactement aux sorties reçues : TXID parent, index, adresse, valeur et script lorsque disponible. Les sorties et ancrages de confirmation de **505 transactions** communes ont été comparés entre les deux formats fournisseur. Ces contrôles ne vérifient pas l'inclusion cryptographique dans les blocs.

## Sous-ensemble dépensé dans la consolidation du cas

La transaction `0c6bf853a645b699a3b2cd6d8e3c44cf1a02a16f538df08212a44753f75d9d01` consomme **341 sorties**, avec **341 parents retrouvés sur 341 référencés**. La valeur totale des entrées consommées est **562.02666941 BTC**. La valeur totale des sorties créées est **562.01962301 BTC**, avec **704640 satoshis** de frais.

Les parents retrouvés utilisent **341 adresses d'entrée distinctes**. Les entrées de la consolidation elle-même sont à l'adresse collectrice ; les compter comme adresses sources initiales aurait donné un résultat trompeur.

Du premier parent retrouvé à la consolidation, l'écart des horodatages de transaction du fournisseur est de **947 secondes**. Les horodatages de confirmation des parents couvrent 412 secondes. Ces deux mesures sont distinctes et ne prouvent pas le début réel d'un incident.

## Autres destinations structurelles du cas

Les 5 consolidations retrouvées parmi les 5 transactions attribuées par la source donnent les destinations suivantes. Elles restent des pistes de graphe ; aucune culpabilité n'est déduite.

| Destination | Sortie BTC | Parents retrouvés / demandés | Adresses d'entrée des parents retrouvés |
|---|---:|---:|---:|
| `bc1qq85v2c926eg6pgxhwp6q7lf6cnsz80qs3fcu9r` | 562.01962301 | 341 / 341 | 341 |
| `bc1qx76cae2706qd5q576feh7xq8rfcsjpf2htfhe3` | 398.47573857 | 491 / 491 | 491 |
| `bc1pdl33jtqnausmx2d4r4c6wpnk5are8jz046y3yjkw8fryjel02p7sluu9ce` | 36.01585057 | 34 / 101 | 34 |
| `bc1q8jy96fe5lf8vfugydnte3cguk92gpev7kwtp3q` | 89.62327890 | 204 / 204 | 204 |
| `bc1qtfrwa4j6rmj9rsgspv6a0yjumkg39js2numu75` | 45.90251994 | 0 / 1212 | 0 |

Somme des sorties uniques de ces 5 consolidations : **1132.03701099 BTC**. Il ne faut pas y additionner les dépôts parents : ce serait recompter les mêmes fonds. Parmi 2349 transactions parentes distinctes référencées, 1070 sont disponibles. L'absence des autres empêche un décompte complet des adresses sources.

Les **1070 lignes** du fichier `parents.json` ont été recalculées à partir de l'archive et sont identiques : TXID, bloc, nombres d'entrées/sorties, adresses d'entrée distinctes, indices dépensés et étiquettes inchangées.

## Dépenses ultérieures

5 sorties sur 5 ont une réponse exploitable du fournisseur ; **0 sont indiquées dépensées**. Les dates et les URL exactes de chaque requête figurent dans `case_flows.json`. Une sortie non dépensée ne démontre pas un stockage cold ou matériel. Le solde de l'adresse collectrice et l'état de ces sorties de consolidation sont deux objets différents.

## Portée et reproduction

Les résultats numériques sont calculés à partir des données et accompagnés de leurs SHA256 dans `case_flows.json`. Aucun montant n'est converti en dollars sans date et taux de change. Aucun modèle n'est entraîné ici.

```bash
python analyze_case_flows.py analyze /chemin/blocos.tgz nouveau_resultat \
  --parents /chemin/parents.json \
  --history /chemin/coldcard_target_history_20261014.json.gz \
  --outspends /chemin/coldcard_seed_outspends_20261014.json
```

Les observations publiques peuvent évoluer. Pour une nouvelle collecte (nouveau fichier obligatoire) :

```bash
python analyze_case_flows.py collect nouvelle_histoire.json.gz --max-pages 100
python analyze_case_flows.py collect-outspends nouveau_resultat/case_flows.json nouvelles_sorties.json
```

Source d'attribution : https://bitquery.io/investigations/coldcard-wallet-hack. La vérification des sorties ne confirme pas les allégations de cette source.
