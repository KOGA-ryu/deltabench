# DeltaBench Design

## Purpose
DeltaBench is the change-risk sibling to BlueBench.

Core split:
- BlueBench: what matters at runtime?
- DeltaBench: what matters in the change set?

## Core Loop
1. Load a diff from a base/head pair.
2. Write canonical raw diff evidence.
3. Derive risk ranking and review priority.
4. Emit a compact review packet and summary.

## Evidence Model
Raw evidence includes facts only:
- schema version
- diff id
- base/head identifiers
- changed files
- file status
- additions
- deletions
- mapped subsystem

## Derive Model
Derived outputs are computed once and reused everywhere:
- risk score
- blast radius estimate
- boundary crossing count
- review priority
- confidence label
- summary lines

## Packet Model
The MVP packet is `review_packet`.

It answers:
- primary review targets
- why they matter
- confidence
- suggested files or subsystems

## Not Built Yet
- BlueBench hotspot overlap
- regression overlap
- benchmark recommendation packet
- UI
- historical intelligence beyond placeholders
- experiment orchestration
