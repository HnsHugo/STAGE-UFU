# First collection of addresses associated with stolen funds

## Objective and provenance

The `theft_seed_registry_20261010.json` registry contains six Bitcoin addresses published by the FBI on 22 August 2023. The release describes them as holding funds from several thefts attributed to TraderTraitor.
Source: https://www.fbi.gov/news/press-releases/fbi-identifies-cryptocurrency-funds-stolen-by-dprk

The recorded role is `reported_stolen_funds_holder`, not victim. The hardware-wallet type and originating case for each address remain unknown. All six addresses belong to the same validation group: the release does not allow them to be assigned to independent cases.

## Reproducible collection

```bash
python collect_theft_seeds.py theft_seed_registry_20261010.json new_collection
python -m unittest discover -p test_theft_collection.py
```

The output directory must be new. The script checks Base58Check checksums, retrieves confirmed transactions using Blockstream's Esplora API, paginates until an empty page, and compares before/after counters against reconstructed amounts and counts of received/spent outputs. Transactions retain their API-provided block heights and hashes.
Documentation: https://github.com/Blockstream/esplora/blob/master/API.md

Stable counters and exhaustive pagination support complete coverage according to this provider. This check is neither cryptographic inclusion verification nor agreement between independent providers. The mempool is excluded. An error or counter discrepancy makes the manifest incomplete. Files have SHA-256 checksums and the manifest references the registry's checksum.

## Use in the future model

These data form a reference collection, not yet a supervised dataset. Attribution concerns addresses at the release date; it does not turn all their historical or later transactions into confirmed thefts. A later dust receipt may be unrelated to the theft.

Future examples need a documented time window, role, case group and features computed only from information known at prediction time. A history retrieved today must not introduce future spending into an example intended to be evaluated in August 2023. Cumulative value received by an address is not automatically the stolen amount; transfers between registry addresses must not be counted multiple times.

Next work: examine movements around the release period, seek other independent cases, and define the target (victim address or stolen-funds holder) before training an address model.
