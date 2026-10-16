# Éligibilité du jeu hot/cold — 16 octobre 2026

L'exigence du support d'Ivan (p.99 : dataset d'adresses cold et classifieur) reste partielle. Cette unité ajoute un contrôle exécutable des données déjà collectées, sans collecte réseau, réentraînement ou nouvelle attribution.

## Résultat exécuté

Les deux collections de septembre sont consolidées par adresse, sans additionner leurs observations. Sur onze adresses, dix sont de recherche : cinq labels publiés cold, un hot, quatre unknown. Six adresses de recherche ont une fenêtre complète selon les compteurs fournisseur, dont quatre cold et deux unknown. La seule adresse hot reste incomplète. **Zéro adresse est éligible**, car aucune ne possède de preuve explicite de validité du label sur toute la fenêtre de septembre 2026.

Une fenêtre complète contenant zéro transaction conserve ce zéro. Un historique tronqué conserve une mesure indisponible. Une adresse unknown n'est pas ajoutée à une classe négative. Le statut `not_ready` est un résultat de contrôle des entrées, pas une performance prédictive.

## Règles et limites

Le script vérifie les empreintes des entrées, l'identité des adresses et des métadonnées, l'égalité des fenêtres et l'absence de conflits entre collections. Il sélectionne une observation complète lorsqu'elle existe. Il ne fusionne pas les comptes de pages ou de transactions et ne recalcule pas les caractéristiques historiques.

Un label futur ne peut être accepté qu'avec un statut revu `verified` et une structure explicite `storage_label_evidence` contenant `source_url`, `valid_from_utc`, `valid_until_utc_exclusive` et `published_at_utc`. L'intervalle doit couvrir la fenêtre entière et la publication être disponible au plus tard à sa fin. `reviewed_at_utc` ne remplace aucune de ces dates. Ce schéma est préparé ; aucune preuve de ce type n'a été ajoutée aux données actuelles. Le script vérifie les métadonnées fournies, sans authentifier leur source ni établir leur vérité.

Même des observations éligibles exigeraient une revue des groupes d'entités/incidents et un protocole entraînement/validation/test distinct avant toute expérience. Les noms d'entités sont des attributions de source. Les compteurs fournisseur ne sont pas des preuves cryptographiques ; l'activité d'une adresse n'est pas celle d'un wallet complet. Aucun label hardware ou illicite n'est déduit.

## Anomalie de reproductibilité documentée

L'empreinte du `input.csv` de la collection initiale correspond exactement au manifeste. Celle de la collection étendue ne correspond pas aux octets Git actuels : elle correspond exactement après reconstruction LF vers CRLF. Le rapport conserve l'empreinte des octets réellement lus et ce mode de correspondance séparément. Aucune modification des entrées historiques n'a été faite. Une différence de contenu autre que ce changement précis des fins de ligne est rejetée.

## Reproduire

Depuis la racine, choisir un nouveau fichier de sortie :

```bash
python "Task 2/part 1/audit_storage_readiness.py" \
  "Task 2/part 1/results/window_september2026" \
  "Task 2/part 1/results/window_september2026_extended" \
  --output /chemin/nouveau_storage_readiness.json
python -m unittest discover -s "Task 2/part 1" -p 'test*.py'
```

Le résultat réel est `results/storage_readiness_20261016.json`. Les 28 tests de ce dossier réussissent, dont sept nouveaux contrôlant les zéros tronqués, les classes inconnues, les tests API, la disponibilité temporelle, les preuves manquantes et les empreintes avec fins de ligne.

## Prochaine unité

Établir des preuves datées de hot et cold pour plusieurs entités avant de fixer une nouvelle fenêtre. Vérifier en priorité si la publication Bitfinex épinglée fournit une date et une période opérationnelle réellement défendables ; une date de commit seule ne prouve pas la continuité d'usage. Sans preuve suffisante, conserver le blocage et chercher une source indépendante précise. Ne pas entraîner sur septembre avec les labels historiques actuels.

## Suite exécutée le 16 octobre

La [vérification temporelle Bitfinex et les profils ponctuels Change](TEMPORAL_LABELS_20261016.md) précisent les dates Git retrouvées, les limites et le travail rétrospectif réalisé. Aucune éligibilité de septembre n’a été ajoutée.
