# Audit des parents — 8 octobre 2026

Résultat fourni par Hugo depuis Codespaces : les cinq transactions attribuées par Bitquery ont été retrouvées. Sur 2 349 indices de transactions parentes recherchés, 1 070 ont été retrouvés et 1 279 manquent dans les blocs fournis. Tous les parents retrouvés ont une sortie ; 934 ont une entrée, soit 87,29 %.

Les liens ne prouvent ni le vol, ni le contrôle par un hardware wallet. Les parents restent des candidats avec label inconnu. Les autres transactions ne sont pas des négatifs légitimes certifiés. Les données fournies couvrent 98 blocs sélectionnés, pas un historique complet.

## Extraction dans Codespaces

Depuis `Task 2/coldcard`, après `git pull` :

```bash
python extract_features.py blocks parents.json features_output
```

Le dossier de sortie doit être nouveau. Vérifier `manifest.json` : statut `complete`, 493571 transactions, 5 `source_attributed`, 1070 `direct_parent_candidate`, 492496 `unattributed`. Transmettre `transactions.csv.gz` et `manifest.json` pour poursuivre l'analyse.

Les identifiants, la hauteur du bloc et la relation ne doivent pas être utilisés comme variables du modèle. La relation est une provenance, pas une vérité terrain de vol. Le script extrait des propriétés des transactions confirmées, sans statut de dépense futur. Les valeurs de vsize sont arrondies au supérieur depuis le poids. La coinbase est explicitement distinguée.

L'entraînement attend une stratégie de labels documentée et une séparation des groupes liés entre entraînement et test. Aucune performance de détection n'est encore démontrée.
