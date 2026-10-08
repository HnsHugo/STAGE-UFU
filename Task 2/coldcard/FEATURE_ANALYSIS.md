# Analyse des caractéristiques — 8 octobre 2026

## Validation

Extraction fournie par Hugo depuis Codespaces. Manifest complete : 493 571 observations et 493 571 TXID uniques, aucun doublon. Les 98 coinbase sont distinguées. Pour toutes les autres transactions, somme des entrées − somme des sorties = frais annoncés.

SHA256 de transactions.csv.gz : `158788226288dce22bfd5ea20deab1b72551c5d0c32bdb547e113c83273841b4`.

| Groupe de provenance | Nombre | Médiane des sorties | Frais médians sat/vB |
|---|---:|---:|---:|
| Attribuées par la source | 5 | 1 | 5,0092 |
| Parents directs candidats | 1070 | 1 | 30 |
| Sans attribution | 492496 | 2 | 0,4429 |

Les frais médians excluent les coinbase. Les candidats ne sont pas des vols confirmés ; les sans attribution ne sont pas des transactions légitimes certifiées.

## Concentration et règles descriptives

Les candidats occupent six blocs : 960183 (204), 960185 (491), 960188 (63), 960189 (110), 960190 (168), 960733 (34). Ils ne constituent pas 1070 cas indépendants.

Toutes les candidates ont une sortie ; 934 ont une entrée et une sortie. Le groupe sans attribution contient également 54 510 transactions à une sortie, dont 39 493 avec une entrée. Cette forme est insuffisante pour conclure à un vol.

La règle descriptive « une sortie et frais >= 4,95 sat/vB » sélectionne 1070 candidates, mais aussi 7231 transactions sans attribution et 3 des 5 consolidations attribuées. Le seuil a été choisi après observation : ces nombres sont descriptifs, pas une évaluation hors échantillon. Les 7231 ne peuvent être déclarées ni faux positifs certains, ni nouveaux vols.

## Protocole pour l'arbre de décision

Un premier arbre pourra chercher à distinguer les parents candidats du fond sans attribution : sa cible devra être explicitement nommée relation au cas, pas vol confirmé ou hardware wallet. Les cinq consolidations constituent un rôle distinct, à ne pas mélanger automatiquement aux transactions de collecte.

Avant de présenter une performance : compléter les groupes de provenance (consolidation descendante, collecteur, composante liée), garder les groupes liés hors des deux ensembles simultanément, réserver le test avant de régler les hyperparamètres, exclure TXID/hauteur/relation des variables prédictives et rapporter précision/rappel/F1 comme métriques de la cible proxy. Le regroupement par bloc seul ne garantit pas l'indépendance des collecteurs.

Un arbre qui reproduit ce cas ne prouve pas la détection de nouveaux vols. Une validation externe avec des cas documentés et des témoins sourcés restera nécessaire. Aucune performance de modèle entraîné n'est annoncée dans ce rapport.
