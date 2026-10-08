# Transition depuis la collecte de wallets vers le cas Coldcard

La collecte précédente (Task 2/part 1) constitue un pilote réutilisable : recherche d'entités, provenance des labels, historiques confirmés, couverture et métriques sur une fenêtre fixe. Elle n'a produit ni prédiction de stockage ni score d'illicéité. Les historiques incomplets restent explicitement signalés ; ils ne doivent pas être transformés en observations nulles.

Pour les nouvelles directives, la priorité devient le dataset local de blocs et un arbre de décision explicable. Les labels de stockage cold/hot du pilote restent séparés des labels relatifs au vol et au hardware wallet. Les résultats de septembre et le cas de juillet/août ne sont pas joints sans justification temporelle.

Le GNN/GCN, SHAP et le PoC d'analyse d'adresses restent des objectifs ultérieurs. La première expérience Coldcard sert à éprouver les labels, les variables et la validation avant d'introduire un modèle plus complexe. L'échec chronologique de l'arbre complet est un résultat expérimental à conserver, pas à masquer par une sélection de scores favorables.

À ce stade : cinq consolidations attribuées par une source externe, 1070 parents candidats retrouvés, caractéristiques extraites pour 493571 transactions, première expérience d'arbre réalisée. Les candidates ne sont pas des vols confirmés et les observations sans attribution ne sont pas des témoins légitimes certifiés.
