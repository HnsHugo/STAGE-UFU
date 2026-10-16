# Task 2 — Analyse de transactions et d'adresses Bitcoin

## État vérifié au 15 octobre 2026

La branche contient les expériences du cas Coldcard, les benchmarks d'adresses et un pilote externe descriptif. Les consignes du support d'Ivan ont été retrouvées : l'exercice 100 + 100 et les questions de flux ont maintenant des scripts, des résultats et des limites explicites.

- [Exigences retrouvées : réalisé, partiel, bloqué](REQUIREMENTS_AUDIT.md)
- [Bilan français pour Ivan](BILAN_FR.md)
- [Démonstration hors ligne et reproduction](DEMO.md)
- [Exercice exact du cours et recherche de candidats](coldcard/COURSE_EXERCISE.md)
- [Flux de l'adresse étudiée et des cinq consolidations](coldcard/case_flows_20261015/CASE_FLOWS_FR.md)
- [Validation groupée du modèle de transactions](coldcard/GROUPED_EXPERIMENT.md)
- [Benchmark Elliptic++](ellipticplusplus/README.md)
- [Benchmark Real-CATS et limites de provenance](real_cats/README.md)
- [Audit des dépendances du pilote externe](real_cats/EXTERNAL_INDEPENDENCE_AUDIT.md)

Le corpus Coldcard compte 493 571 transactions uniques. La reproduction complète des résultats groupés retrouve exactement les métriques sauvegardées. Les onze scores du pilote externe et leurs caractéristiques ont également été reproduits à l'identique, sans modification de la forêt à 19 variables ni du seuil strict de 0,15.

L'exercice de 200 transactions obtient 60/60 sur son petit test lié à la même adresse, mais génère 8 158 alertes sur 492 135 transactions non attribuées inutilisées. Ce résultat illustre la différence entre reconnaître un échantillon et détecter de nouveaux incidents. Les pistes de destinations ne sont pas des vols confirmés.

Les hypothèses de cold storage, d'appareil matériel et d'activité illicite restent distinctes. L'absence de chevauchement d'adresse exacte n'établit pas l'indépendance des transactions ou des entités ; le nouvel audit externe précise les relations observables. Aucun résultat n'est présenté comme une probabilité calibrée de vol.

Les sections suivantes conservent l'historique du premier pilote ; leurs formulations au présent décrivent l'état de cette étape initiale, pas celui de toute la branche actuelle.

## Original research direction (provisional)

The supervisor's remembered keywords are WalletExplorer, hardware-wallet-related
addresses and CPFP flags. The exact scope and the intended meaning of cold vs
hardware wallets still need confirmation. This is a working plan, not an official
assignment or a claim that these behaviours identify illicit activity.

1. Address-to-cluster observations with WalletExplorer (first implementation).
2. Build a sourced cold/hardware-wallet dataset with explicit evidence levels.
3. Extract behavioural features and document competing explanations.
4. Investigate CPFP candidates and fees relative to contemporaneous conditions.
5. Test hypotheses against independently sourced licit/illicit labels.

A hardware wallet is a signing device; cold storage is an operational practice.
An address format does not establish either property. Keep service attribution,
storage classification and illicit labels as separate fields with separate sources.

## Original wallet-pilot progress

Part 1 contains single-address and CSV collection CLIs, sourced input records,
real API snapshots and offline tests for validation, error handling and resume.
The seed table now includes seven first-party research addresses: three Bitfinex
addresses with published hot/cold labels and four historical Binance reserve
addresses with unknown storage. WalletExplorer found all seven but supplied no
service names. These are collection results, not illicit-correlation findings.
It queries an existing clustering service; it does not implement clustering itself.
The wallet-collection pilot implements no hardware/cold classification, CPFP detection or illicit classifier.

## Validation constraint

Task 1 uses the original anonymized Elliptic dataset. Its txId values are dataset
identifiers, not a supplied mapping to on-chain transaction hashes. We cannot join
new on-chain fee/CPFP measurements to those labels without a verified mapping.
Use Elliptic separately for graph/ML baselines and investigate a labeled on-chain
dataset for the new feature hypotheses before promising a correlation analysis.

Source: https://www.kaggle.com/datasets/ellipticco/elliptic-data-set

## Expanded sample

The latest collection is Part 1/results/research_expanded_20261005/results.csv.
There are now 10 research addresses across Bitfinex, Binance and Change, plus one
smoke-test address. Five published cold labels span two entities; only one hot
address is available. Change's storage claim applies to a 2025-03-31 snapshot,
and does not establish an address-specific hardware model. All 11 lookups were
found, but none of the 10 research addresses received a provider service label.
Earlier dated result directories preserve earlier samples.

## First on-chain history collection

Part 1 now includes `collect_history.py`, using at most 25 recent confirmed
transactions per address in the initial run. All 11 addresses succeeded, yielding
206 address/transaction observations. Labels and provenance remain in
address_summary.csv, while transactions.csv supplies dated flows and transaction
fees. See Part 1/HISTORY.md for count-based coverage and non-atomic snapshot limits.
The 14 offline tests cover ingestion, response validation, pagination, amount
attribution, coverage changes and resumable collection. CPFP, holding-time and
illicit inference remain unimplemented.
