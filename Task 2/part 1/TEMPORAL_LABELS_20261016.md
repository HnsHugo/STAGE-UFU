# Preuves temporelles et profils ponctuels — 16 octobre 2026

## Bitfinex : résultat de la vérification directe

L'API GitHub du dépôt officiel renvoie deux révisions de `wallets.txt` dans l'historique accessible jusqu'au commit épinglé :

| Commit | Date de commit enregistrée, UTC | Modification |
| --- | --- | --- |
| `e72eec303c93396bdbc7c4fce6cd99f8e1307551` | 2022-11-11 18:59:13 | Création du fichier |
| `83d06bdb5f5a2ce05d5ba2db5a426dd44c9f5128` | 2022-12-12 22:24:41 | Changement du wallet BSV cold |

Les trois lignes BTC ont été récupérées directement dans **les deux versions** : une hot et deux cold, identiques aux trois adresses du pilote. Le changement de décembre concerne BSV, pas BTC. Les URL, dates et extractions factuelles sont conservées dans `data/storage_temporal_evidence_20261016.json`.

Cela établit des assertions publiées dans deux versions, sans établir un intervalle opérationnel continu. Les dates Git ne sont pas une preuve indépendante de première disponibilité publique ; même une vérification de signature GitHub ne prouve ni propriété d'une adresse ni stockage de ses clés. Aucun début/fin de validité opérationnelle ni horodatage public indépendant n'a été obtenu. **Aucun label n'est étendu à septembre 2026.**

Requête de reproduction :

`https://api.github.com/repos/bitfinexcom/pub/commits?path=wallets.txt&sha=83d06bdb5f5a2ce05d5ba2db5a426dd44c9f5128&per_page=100`

Les fichiers sont accessibles par `https://raw.githubusercontent.com/bitfinexcom/pub/<COMMIT>/wallets.txt`. Cette requête borne l'historique au commit étudié ; elle n'est pas un examen des versions postérieures.

## Recherche indépendante bornée

Une piste officielle BitMEX a été examinée : annonce de réémission des adresses et instantané de réserves. Les deux URL primaires ouvertes ont renvoyé 404 via l'outil de consultation. Les extraits de moteur de recherche ne sont pas acceptés comme preuve de label ou de date. Zéro adresse ajoutée. Cet échec d'accès ne prouve pas l'absence de sources exploitables ; la recherche a été arrêtée pour préserver le budget de session.

## Travail local exécuté : Change au 31 mars 2025

Les trois historiques déjà sauvegardés et complets selon les compteurs fournisseur permettent une reconstruction ponctuelle au `2025-03-31T23:59:00Z`, date du snapshot cold documenté dans `data/change_sources_20261005.md`. Seules les transactions confirmées de date inférieure ou égale au snapshot contribuent aux caractéristiques.

| Adresse, suffixe | Transactions retenues | Reçu (sat) | Dépensé (sat) | Solde reconstruit (sat) |
| --- | ---: | ---: | ---: | ---: |
| `...hkpd2mpw7` | 1 | 457067 | 0 | 457067 |
| `...csxem5ea` | 1 | 89999708 | 0 | 89999708 |
| `...r72hcaclu` | 1 | 2999999395 | 0 | 2999999395 |

Le rapport `results/change_snapshot_profiles_20261016.json` contient les adresses complètes et les empreintes des trois fichiers d'entrée. Il n'utilise pas leur solde actuel, ni leurs dépenses ultérieures pour calculer les caractéristiques. Le temps depuis la dernière transaction observée n'est pas une durée de détention d'UTXO.

La publication du label est documentée au **21 avril 2025**, donc après le snapshot. Son heure précise n'est pas connue et reste null. Cette session réutilise la revue antérieure de la source Change, sans nouvelle authentification. Ce sont des profils **rétrospectifs**, pas un jeu d'entraînement prospectif : la couverture est vérifiée avec des compteurs collectés ultérieurement, et les labels n'étaient pas disponibles à la date reconstruite. Les trois adresses appartiennent à une seule entité attribuée. Aucun classifieur ni métrique prédictive n'est produit.

## Reproduction et tests

Depuis la racine du dépôt :

```bash
python "Task 2/part 1/snapshot_storage_profiles.py" \
  "Task 2/part 1/results/window_september2026/bc1q43krjn8qvfydqs9lq8crg26er4c26hkpd2mpw7.json" \
  "Task 2/part 1/results/window_september2026/bc1qhsuvec03zslh9qvauksh2wc9hy9za7csxem5ea.json" \
  "Task 2/part 1/results/window_september2026/bc1q9rqfux88j6az0wl957u2jdykgw5m5r72hcaclu.json" \
  --snapshot 2025-03-31T23:59:00Z --label-publication-date 2025-04-21 \
  --output /chemin/nouveau_rapport.json
python -m unittest discover -s "Task 2/part 1" -p 'test*.py'
```

Les 32 tests du dossier réussissent, dont quatre nouveaux contrôlant l'exclusion des transactions futures, la borne inclusive, les doublons, la couverture et les fuseaux horaires.

## Reprise

La publication Bitfinex épinglée est désormais vérifiée : ne pas recommencer cette recherche. La prochaine priorité est une source primaire accessible qui associe des adresses hot et cold à une date explicite, pour une autre entité, puis un protocole rétrospectif clairement séparé si les labels ont été publiés après la date décrite. Des snapshots seuls ne justifient pas un mois de labels continus. Conserver le blocage de septembre tant que les preuves restent insuffisantes.
