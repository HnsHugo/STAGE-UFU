# Validation avec un groupe candidat laissé de côté

## Données et protocole

Le fichier candidate_groups.json fourni par Hugo correspond exactement aux 1070 TXID candidats des caractéristiques et au SHA256 du rapport de parents. Il définit quatre groupes observés, de tailles 341, 491, 34 et 204. La cinquième consolidation source n'a aucun parent retrouvé dans l'archive : elle ne crée pas de cinquième groupe d'apprentissage.

Chaque groupe candidat est réservé au test une fois et entièrement absent de l'entraînement de ce pli. Le fond sans attribution est réparti en quatre ensembles disjoints par SHA256(TXID), sans utiliser le TXID comme variable prédictive. Chaque transaction éligible est donc évaluée une fois hors de son ensemble d'entraînement. Les entités du fond et les relations transitives à travers les blocs absents ne sont toutefois pas connues : il ne s'agit pas d'une indépendance de tous les acteurs blockchain.

Réglages fixés : profondeur 4, minimum 20 lignes par feuille, class_weight balanced, random_state 42. Aucun ajustement aux scores de ces plis. Deux modèles : caractéristiques complètes et caractéristiques sans fee_sat/fee_rate_sat_vb. La règle à 4,95 sat/vB reste une référence descriptive choisie précédemment sur les données.

## Résultats par groupe de test

| Consolidation descendante, début du TXID | Candidates | Retrouvées, arbre complet | Alertes du fond, arbre complet | Retrouvées, sans frais | Alertes du fond, sans frais |
|---|---:|---:|---:|---:|---:|
| 0c6bf853a645 | 341 | 340 | 45 | 341 | 4819 |
| 14edd9ee8445 | 491 | 491 | 911 | 491 | 4845 |
| 38b6dc366fca | 34 | 0 | 47 | 34 | 5951 |
| 4b50d61a3d6e | 204 | 43 | 69 | 43 | 855 |

Les alertes sur les données sans attribution sont des désaccords avec une cible proxy, pas des faux positifs certains ni des vols nouvellement confirmés.

## Résultats cumulés hors pli

| Méthode | Candidates retrouvées | Alertes du fond | Précision proxy | Rappel proxy | F1 proxy |
|---|---:|---:|---:|---:|---:|
| Toujours fond | 0/1070 | 0 | 0 % | 0 % | 0 % |
| Règle une sortie + frais >=4,95 | 1070/1070 | 7231 | 12,89 % | 100 % | 22,84 % |
| Arbre complet | 874/1070 | 1072 | 44,91 % | 81,68 % | 57,96 % |
| Arbre sans frais | 909/1070 | 16470 | 5,23 % | 84,95 % | 9,85 % |

Le rappel moyen donnant le même poids à chaque groupe est 55,20 % pour l'arbre complet, contre un rappel cumulé de 81,68 %. Cette différence reflète les échecs sur les groupes petits : il faut publier les deux, et pas seulement le score dominé par les groupes grands. Le F1 moyen par groupe de l'arbre complet est 43,19 %.

Les scores pondérés des arbres ne sont pas des probabilités calibrées de vol. L'average precision cumulée agrège les scores de quatre arbres distincts ; elle doit être interprétée avec prudence car leurs scores ne sont pas calibrés entre plis. Les résultats individuels sont conservés dans metrics.json.

## Comprendre les différences

Trois groupes ont des frais médians de 30 sat/vB, le groupe de 34 des frais médians de 4,9590. Les montants médians des sorties varient aussi : environ 0,6185 BTC, 0,2510 BTC, 0,0192 BTC et 0,0210 BTC respectivement dans l'ordre du tableau. L'arbre complet dépend fortement des frais et manque le groupe à faibles frais. Le groupe de 204 montre une autre fragilité : le retrait des frais ne rétablit pas son rappel, qui reste 43/204.

Ces différences documentent des comportements de groupes du même cas. Elles ne justifient pas d'attribuer un auteur, un firmware ou un modèle de portefeuille à partir d'une transaction seule.

## Reproduire

Depuis Task 2/coldcard :

```bash
python -m pip install -r requirements.txt
python train_grouped.py features_output/transactions.csv.gz candidate_groups.json features_output/manifest.json grouped_output
python -m unittest discover -p 'test_*.py' -v
```

Le dossier de sortie doit être nouveau. Le fichier de caractéristiques est contrôlé par son SHA256 exact. Les groupes sont vérifiés contre les TXID candidats, les comptes annoncés et la provenance du rapport de parents. Une provenance différente, un candidat manquant ou doublonné provoque un refus avant l'entraînement.

## Conclusion et suite

L'arbre reconnaît une partie des candidats et réduit les alertes par rapport à la règle descriptive, mais ses résultats varient fortement selon le groupe. Le résultat aléatoire antérieur (266/267) était plus favorable et moins indépendant. Même cette validation améliorée reste interne à un incident et à des labels indirects.

La suite utile est la constitution d'un registre de labels sourcés, avec rôle victime/collecte/consolidation, confiance, période et cas. Les adresses victimes ne doivent pas être confondues avec des adresses illicites ; le contrôle par hardware wallet doit rester une propriété indépendante. Une absence de signalement Chainabuse ne constitue pas un label légitime. Des cas externes et des témoins documentés sont nécessaires avant une conclusion générale sur la détection de vols.
