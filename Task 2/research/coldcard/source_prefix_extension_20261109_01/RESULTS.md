# Résultats du 9 novembre 2026 — extension de couverture

Le lot de 20 comparaisons Coldcard est finalisé : **4 nouveaux préfixes
complets et 16 préfixes encore incomplets à la limite de 32 pages**.
Les nouveaux IDs sont `comparison_0010`, `comparison_0013`, `comparison_0035`
et `comparison_0093` : 26, 21, 31 et 25 pages, page terminale vide incluse.
Un préfixe complet couvre les transactions confirmées strictement antérieures
au bloc de référence ; cela ne certifie pas tout l'historique courant.

| Cohorte fixée | Sources sélectionnées | Vecteurs exploitables | Préfixes incomplets |
|---|---:|---:|---:|
| Coldcard | 1 500 | 1 382 (500 cas + 882 comparaisons) | 118 |
| CryptoBilis | 366 | 329 (122 cas + 207 comparaisons) | 37 |
| Total | 1 866 | 1 711 | 155 |

## Collecte et audit

L'unique GET normal du compteur a répondu HTTP200. Les **316 nouvelles
requêtes** ont toutes répondu HTTP200 : 295 nouvelles pages, 20 vérifications
de statut de référence et le compteur. Les 340 anciennes réponses réussies
ont été réutilisées après vérification des empreintes et des curseurs.
Le compteur de 656 dans les exports désigne les marqueurs de réponses, dont
340 réutilisés hors réseau ; il ne signifie pas 656 nouvelles requêtes.
Deux workers, une requête globale par seconde, timeout 15 s, aucun retry
interne et aucun changement de route, fournisseur ou TLS. Aucun refus ni erreur.

L'audit vérifie les 656 réponses, réassemble et réextrait les 20 queues brutes,
vérifie la référence, la clôture des financements et l'épuisement de pagination,
puis recompte indépendamment les 14 variables des quatre nouveaux vecteurs.
La nouvelle vue schema-v2 préserve exactement les 1 378 anciens vecteurs et
toutes les lignes non sélectionnées. Labels inconnus et cutoff sont conservés.
Une seconde vérification indépendante rapproche les exports et les comptes.

Les statuts d'historique courant Coldcard restent **500 cas complets, 864
comparaisons complètes et 136 incomplètes**. CryptoBilis n'a pas fait l'objet
d'une collecte de tout l'historique courant. Les anciens résultats et marqueurs
sont conservés. L'archive privée vérifiée sauvegarde 4 419 fichiers, sans
publication des caches sur GitHub. Bail libéré, automatisation désactivée.

Le [point de reprise](resume_checkpoint.json) ferme ce lot : aucun ID réseau
à retenter dans cette passe. Il distingue les 16 préfixes désormais bornés à
32 pages des 102 autres Coldcard encore au résultat de la borne précédente,
et des 37 CryptoBilis. Aucune adresse n'est remplacée.

## Lien avec les expériences

L'expérience figée [CryptoBilis → Coldcard](../../external_cases/cryptobilis_to_coldcard_20261109/RESULTS.md)
utilise le jeu précédent, avant ces quatre ajouts : entraînement sur 329
CryptoBilis ; test sur 1 066 Coldcard éligibles (499 cas + 567 comparaisons),
312 vecteurs Coldcard mis à l'écart par les composantes liées et 122 non scorés.
Un seul fit fixé avant entraînement : TP 499, TN 478, FP 89, FN 0 ; précision
0,848639, rappel 1,000000, **F1 0,918123** et AP 0,937248. L'inactivité seule
classe mieux en AP (0,955619). C'est une expérience rétrospective à rebours
du temps sur l'appartenance aux sources, pas une validation de vol ou de matériel.

Le résultat Coldcard → CryptoBilis reste **F1 0,629834** sur 275 vecteurs
éligibles (122 cas + 153 comparaisons). Populations et modèles diffèrent :
les deux F1 ne sont pas une comparaison appariée. Ces quatre nouveaux vecteurs
ne changent aucun de ces scores et ne déclenchent aucun réentraînement.

Prochaine unité : récupérer hors réseau les preuves Coldcard déjà sauvegardées,
puis préparer une nouvelle extension bornée sur les IDs encore incomplets.
Refaire l'audit des chevauchements avant tout modèle sur la nouvelle vue.
Le troisième incident reste à sélectionner et figer pour le test de l'entraînement
mixte. Les graphes et le deep learning constituent ensuite l'axe principal ;
l'hypothèse de migration vers des exchanges demandera une étude pré/post distincte.
