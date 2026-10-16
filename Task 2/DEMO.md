# Démonstration reproductible de la Task 2

La démonstration lit les artefacts sauvegardés et applique l'arbre Coldcard exporté. Elle ne fait aucune requête réseau et n'entraîne aucun modèle. `verified` concerne uniquement le contrôle nommé ; les vérifications manquantes et les limites non vérifiables sont affichées séparément.

## Démonstration courte

Depuis la racine du dépôt :

```bash
python "Task 2/run_demo.py"
```

La bibliothèque standard suffit pour contrôler les empreintes des artefacts, la structure de l'arbre et les scores externes sauvegardés. Avec les dépendances de recherche installées, les caractéristiques des historiques présents sont également recalculées. Le programme indique les données volumineuses absentes et n'invente pas leur validation.

## Démonstration complète

Avec Python 3.12 et les dépendances fixées dans `coldcard/requirements.txt` :

```bash
python -m pip install -r "Task 2/coldcard/requirements.txt"
python "Task 2/run_demo.py" \
  --data-dir /chemin/donnees_coldcard \
  --history-dir /chemin/historiques_supplementaires \
  --real-cats-source /chemin/Real-CATS \
  --output /chemin/nouveau_rapport.json
```

`donnees_coldcard` doit contenir `transactions.csv.gz` dans sa version vérifiée. Le dossier d'historiques supplémentaires doit contenir notamment `fsf_history_20261014.json.gz` ; l'option peut être répétée. Les dix autres historiques sont déjà dans le dépôt. Le dossier Real-CATS contient `BB.tsv` et `CB.tsv` à la révision documentée. Les empreintes sont contrôlées avant toute déclaration de succès.

Le rapport refuse d'écraser un fichier existant. Une erreur de schéma, une empreinte différente ou un résultat incohérent produit un statut `failed` et un code de sortie non nul. L'absence d'un fichier produit `missing`, et une vérification hors du périmètre produit `unchecked`.

## Exécution vérifiée

`verification_20261015/demo.json` conserve l'exécution complète : 493 571 lignes vérifiées, 493 468 transactions éligibles rejouées avec l'arbre sauvegardé, onze historiques réconciliés et leurs dix-neuf caractéristiques recalculées. Ce rejeu sur les propres données d'apprentissage de l'arbre n'est pas une mesure de généralisation.

La démonstration affiche les onze scores externes et vérifie la règle stricte `score > 0.15`. Elle ne recalcule pas l'inférence de la forêt. Une reproduction distincte de la forêt et des expériences groupées a été exécutée et conservée dans [le dossier de vérification](verification_20261015/README.md) ; elle ne fait pas partie de cette commande de démonstration.

La vérification d'adresse exacte de cette commande ne couvre pas les dépendances de transactions ou d'entités. Consulter aussi l'audit de chevauchement externe. Aucune vérification ne certifie la vérité des étiquettes ou une probabilité de vol.

## Montrer à Ivan

1. Ouvrir `coldcard/course_results_20261014/tree.txt` : l'arbre simple s'appuie surtout sur les frais.
2. Comparer son résultat sur les 60 transactions réservées avec les 8 158 alertes obtenues dans le reste du corpus.
3. Montrer `coldcard/GROUPED_EXPERIMENT.md` pour expliquer les échecs sur les groupes différents.
4. Lire les réponses de flux et leurs limites dans `coldcard/case_flows_20261015/CASE_FLOWS_FR.md`.
5. Exécuter la commande ci-dessus pour montrer les contrôles, les caractéristiques et les scores figés.

```bash
python -m unittest discover -s "Task 2" -p 'test_demo.py'
```
