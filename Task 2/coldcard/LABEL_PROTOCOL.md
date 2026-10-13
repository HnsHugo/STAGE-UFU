# Protocol for constructing a sourced dataset

## Separate units and objectives

The current pilot operates on transactions. The future address dataset must define an observation period and a label-availability date. Do not directly join Elliptic's anonymous txIds to actual on-chain TXIDs.

Three questions remain distinct: is a transaction related to a documented case; what role does an address play in that case; is there evidence of hardware-wallet control? A theft victim is not an illicit address. A later recipient is not automatically a party knowingly involved in theft.

## Proposed registry

A record associates network, subject_type (address/transaction), subject_id, case_id, role (victim/collection/consolidation/onward/unknown), case_relation (source_attributed/graph_candidate/independently_verified/unknown), source_url, evidence_description, source_published_at, observed_from/to, label_available_at, reviewed_at and hardware_control (supported/unknown), with a separate source for the latter.

Keep raw observations and source assertions separate. Valid TXID or address formatting does not verify a label's truth.

## Evidence levels

1. External reference explicitly publishing a TXID/address: source_attributed. Retain discrepancies between the text and the data.
2. Funding relationship or grouping heuristic: graph_candidate. Do not automatically transfer hardware or illicit labels.
3. Independent confirmation of the case and role: independently_verified, retaining sources and justification.
4. No report or missing source: unknown, never a certified negative.

Positives in a supervised dataset must match the precise target selected. Negatives require a documented control-selection policy; unknown background can support a proxy experiment, but cannot demonstrate precision on confirmed thefts.

## Chainabuse and the professor's resources

Chainabuse can supply structured reports and verified/trusted-contributor indicators. Preserve category, report date, event date if known, and the address's exact role. Documentation distinguishes verified from unverified reports. Advertised standard access is limited; do not treat the API as an exhaustive export.

Haslhofer's ransomware and sextortion datasets concern categories distinct from wallet theft. Keep them as separate cases/categories, check their licenses and schemas before ingestion, and then define a shared temporal protocol. Do not rename all these examples “stolen bitcoin.”

## Evaluation

Hold complete cases/groups out of training. Prevent victims, collectors and consolidations from the same case from being scattered across sets. Report missing coverage, per-case metrics and pooled metrics. Reserve temporal evaluation and external cases before claiming generalization.

Features must be available when the tool is supposed to decide: exclude future spending information and later reports from predictive variables. Addresses, TXIDs, case_id and groups remain provenance/split identifiers.

## Sources

- https://docs.chainabuse.com/reference/reports-1
- https://docs.chainabuse.com/docs/source-of-information
- https://chainabuse.readme.io/docs/getting-started-2-1
- https://bernhardhaslhofer.info/datasets
- https://scikit-learn.org/stable/modules/cross_validation.html
