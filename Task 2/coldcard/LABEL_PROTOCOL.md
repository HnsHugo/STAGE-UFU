# Protocole de constitution du dataset sourcé

## Unités et objectifs séparés

Le pilote actuel travaille sur des transactions. Le futur dataset d'adresses doit définir une période d'observation et une date de disponibilité des labels. Ne pas joindre directement les txIds anonymes d'Elliptic à des TXID de chaîne réels.

Trois questions restent distinctes : une transaction est-elle liée à un cas documenté ; quel rôle joue une adresse dans le cas ; existe-t-il une preuve de contrôle par hardware wallet ? Une victime d'un vol n'est pas une adresse illicite. Un destinataire ultérieur n'est pas automatiquement un auteur conscient du vol.

## Registre proposé

Un enregistrement associe network, subject_type (address/transaction), subject_id, case_id, role (victim/collection/consolidation/onward/unknown), case_relation (source_attributed/graph_candidate/independently_verified/unknown), source_url, evidence_description, source_published_at, observed_from/to, label_available_at, reviewed_at et hardware_control (supported/unknown) avec sa source séparée.

Conserver les observations brutes et les assertions de source séparément. La conformité de format d'un TXID ou d'une adresse ne vérifie pas la véracité d'un label.

## Niveaux d'évidence

1. Référence externe avec TXID/adresse explicitement publié : source_attributed. Conserver les divergences entre texte et données.
2. Lien de financement ou heuristique de regroupement : graph_candidate. Aucun transfert automatique du label matériel ou illicite.
3. Confirmation indépendante du cas et du rôle : independently_verified, en conservant les sources et la justification.
4. Absence de signalement ou manque de source : unknown, jamais négatif certifié.

Les positifs d'un dataset supervisé doivent correspondre à la cible précise retenue. Les négatifs nécessitent une politique documentée de témoins ; le fond inconnu peut servir à une expérience proxy, mais pas à démontrer une précision sur des vols confirmés.

## Chainabuse et ressources du professeur

Chainabuse peut fournir des signalements structurés et des indicateurs de vérification/contributeur de confiance. Préserver catégorie, date du signalement, date de l'événement si connue et rôle exact de l'adresse. La documentation distingue les rapports vérifiés et les rapports non vérifiés. L'accès standard annoncé est limité ; ne pas considérer l'API comme une exportation exhaustive.

Les datasets Haslhofer de ransomware et sextorsion sont des catégories différentes du vol de portefeuille. Les conserver comme cas/catégories distincts, vérifier licence et schéma avant ingestion, puis définir un protocole temporel commun. Ne pas renommer tous ces exemples « bitcoins volés ».

## Évaluation

Réserver des cas/groupes complets hors entraînement. Éviter que victimes, collecteurs et consolidations du même cas se dispersent entre les ensembles. Rapporter la couverture manquante, les métriques par cas et les métriques cumulées. Réserver une évaluation temporelle et des cas externes avant toute conclusion de généralisation.

Les caractéristiques doivent être disponibles au moment où l'outil est supposé décider : exclure les informations de dépenses futures et les signalements ultérieurs des variables prédictives. Les adresses, TXID, case_id et groupes restent des identifiants de provenance/séparation.

## Sources

- https://docs.chainabuse.com/reference/reports-1
- https://docs.chainabuse.com/docs/source-of-information
- https://chainabuse.readme.io/docs/getting-started-2-1
- https://bernhardhaslhofer.info/datasets
- https://scikit-learn.org/stable/modules/cross_validation.html
