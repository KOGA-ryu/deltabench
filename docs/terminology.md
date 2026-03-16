# DeltaBench Terminology

## diff
Definition:
Canonical raw change evidence for a base/head comparison.

Canonical producer:
`core/diff_loader.py`

Allowed consumers:
`derive/*`, `adapters/*`, `reports/*`

Rule:
Must not be recomputed outside the canonical diff loader.

## subsystem
Definition:
Deterministic path-prefix grouping for changed files.

Canonical producer:
`core/repo_mapper.py`

Allowed consumers:
`derive/*`, `adapters/*`, `reports/*`

Rule:
Must not be recomputed outside the canonical repo mapper.

## risk
Definition:
Explicit change-risk score and ranked primary targets derived from diff facts.

Canonical producer:
`derive/risk_ranker.py`

Allowed consumers:
`derive/*`, `adapters/*`, `reports/*`

Rule:
Must not be recomputed outside the canonical risk ranker.

## blast_radius
Definition:
Estimate of how broadly a change crosses subsystem boundaries.

Canonical producer:
`derive/blast_radius.py`

Allowed consumers:
`derive/*`, `adapters/*`, `reports/*`

Rule:
Must not be recomputed outside the canonical blast radius derive module.

## confidence
Definition:
Deterministic confidence label attached to DeltaBench review or benchmark significance.

Canonical producer:
`derive/change_significance.py`

Allowed consumers:
`adapters/*`, `reports/*`

Rule:
Must not be recomputed outside the canonical significance derive path.

## review_priority
Definition:
Ordered review emphasis derived from risk and diff facts.

Canonical producer:
`derive/review_priority.py`

Allowed consumers:
`adapters/*`, `reports/*`

Rule:
Must not be recomputed outside the canonical review-priority derive module.

## review_packet
Definition:
Compact machine-readable packet describing what to review first and why.

Canonical producer:
`adapters/codex/review_packet.py`

Allowed consumers:
CLI, reports, Codex adapters

Rule:
Must not be recomputed outside the canonical review packet builder.

## primary_risk_targets
Definition:
Highest-priority changed files that deserve review first.

Canonical producer:
`adapters/codex/review_packet.py`

Allowed consumers:
CLI, reports, Codex adapters

Rule:
Must not be recomputed outside the canonical review packet builder.

## low_risk_files
Definition:
Changed files classified as lower-priority review targets for the current diff.

Canonical producer:
`derive/change_significance.py`

Allowed consumers:
`adapters/codex/review_packet.py`, CLI, reports

Rule:
Must not be recomputed outside the canonical change-significance derive module.

## runtime_relevant_targets
Definition:
Changed files that are likely to justify rerunning runtime investigation because they touch runtime-relevant paths.

Canonical producer:
`derive/runtime_relevance.py`

Allowed consumers:
`adapters/codex/benchmark_packet.py`, CLI, reports

Rule:
Must not be recomputed outside the canonical runtime-relevance derive module.

## hotspot_overlap_targets
Definition:
Changed files that overlap prior runtime hotspots either by exact file match or hotspot subsystem match.

Canonical producer:
`derive/hotspot_overlap.py`

Allowed consumers:
`derive/change_significance.py`, CLI, reports

Rule:
Must not be recomputed outside the canonical hotspot-overlap derive module.

## benchmark_recommendation_packet
Definition:
Compact machine-readable packet describing which runtime probes should be rerun because of a diff.

Canonical producer:
`adapters/codex/benchmark_packet.py`

Allowed consumers:
CLI, reports, Codex adapters

Rule:
Must not be recomputed outside the canonical benchmark recommendation packet builder.
