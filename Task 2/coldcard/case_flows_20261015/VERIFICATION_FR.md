# Vérification du 15 octobre 2026

Cette exécution utilise les instantanés collectés le **14 octobre 2026**. Elle ne constitue pas une nouvelle observation de l'état de la chaîne le 15. Les résultats historiques de `../case_flows_20261014/` et les données brutes ont été conservés.

Le calcul historique a d'abord été reproduit à l'identique : le JSON recalculé est identique octet pour octet à `../case_flows_20261014/case_flows.json`. Après ajout des contrôles, tous les champs préexistants de ce JSON sont également identiques à ceux du nouveau rapport.

## Contrôles exécutés

| Contrôle sur les données réelles | Résultat |
| --- | --- |
| Archive analysée en deux passages | 98 blocs, 493 571 TXID uniques |
| Ancien `parents.json`, reconstitution de chaque ligne | 1 070 lignes identiques ; 1 279 parents absents de l'archive |
| Historique de l'adresse du cours | 507 transactions, pagination terminée et compteurs stables concordants |
| Entrées dépensées comparées aux sorties reçues | 341 outpoints concordants, soit 56 202 666 941 satoshis |
| Transactions communes aux deux formats fournisseur | 505, avec valeurs/adresses de sortie et hash/hauteur/date du bloc concordants |
| Relevés des sorties des cinq consolidations | 5 réponses exploitables datées du 14 octobre, toutes `spent=false` |
| Tests automatisés de flux | 15 tests réussis, sans réseau |

Les sources distinctes des transactions entrantes sont des **adresses d'entrée**, pas des personnes ni des victimes. Les 594,47728031 BTC reçus sur la vie de l'adresse ne sont pas un montant volé démontré. La consolidation retenue consomme 562,02666941 BTC, crée 562,01962301 BTC de sortie et paie 0,00704640 BTC de frais. L'écart de 947 secondes se rapporte aux horodatages de transaction du fournisseur, pas à une durée d'attaque vérifiée.

## Corrections et garanties

Le formatage des montants négatifs a été corrigé : une différence partielle de -1 satoshi s'affiche maintenant `-0.00000001 BTC`. La collecte respecte désormais l'extension : JSON normal pour `.json`, gzip pour `.gz`. Ces corrections ne changent aucun montant du cas présent.

L'analyse refuse désormais un ancien audit parental divergent, un prevout dépensé absent ou différent de la sortie reçue, un ancrage de bloc contradictoire entre fournisseurs, et une destination de relevé de dépense incohérente. La commande `collect-outspends` rend reproductible le relevé des sorties. Elle conserve une erreur de collecte comme une observation inconnue et refuse d'écraser un fichier existant.

Ces contrôles portent sur la cohérence des fichiers et des observations fournisseur. Aucune signature, preuve de Merkle ou chaîne de preuve de travail n'a été vérifiée. Aucun modèle n'a été entraîné.

## Empreintes des entrées

| Fichier | SHA256 |
| --- | --- |
| `blocos(1).tgz` | `679fe208f9a807fdd38e9d64948c73581af3e99ca52fb707ce06937e67bc536d` |
| `parents.json` | `9e47396449d8ba65d7d6978c9e979bdfc3a4c47b3f3dfcb399fb535982c1d779` |
| `coldcard_target_history_20261014.json.gz` | `ee785d7c6116c33cc1578a3dd09722f68f49a2dc295f983fbeb710d93bc11950` |
| `coldcard_seed_outspends_20261014.json` | `db00c8767d7842573883a088d4e42ea6035f568f14bba5e0374772ccc7bd6ff0` |

## Reproduire

Depuis `Task 2/coldcard`, utiliser un dossier de sortie qui n'existe pas encore :

```bash
python analyze_case_flows.py analyze '/chemin/blocos(1).tgz' nouveau_resultat \
  --parents /chemin/parents.json \
  --history /chemin/coldcard_target_history_20261014.json.gz \
  --outspends /chemin/coldcard_seed_outspends_20261014.json
python -m unittest test_case_flows -v
```

Les deux commandes de collecte documentées dans `CASE_FLOWS_FR.md` produisent de nouveaux instantanés. Les conditions publiques peuvent changer ; elles ne remplacent pas les fichiers du 14 nécessaires à la reproduction exacte de ce rapport.
