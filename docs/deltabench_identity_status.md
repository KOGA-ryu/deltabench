# DeltaBench Identity and Status

## Purpose
DeltaBench is the change-risk sibling to BlueBench.

Core split:
- BlueBench answers: what matters at runtime?
- DeltaBench answers: what changed, why it matters, and what to review or rerun next?

DeltaBench is not a profiler. It is a diff intelligence tool.

## Product Identity
DeltaBench exists to turn code changes into structured risk evidence.

Its job is to reduce the cost of answering:
- what changed?
- which parts of the diff deserve attention first?
- why does this diff matter?
- which runtime investigation should be rerun because of this diff?

It should feel like a compact, deterministic change-review instrument.

## Design Law
DeltaBench follows the same core discipline that makes BlueBench trustworthy:
- evidence first
- derive once
- packet-first downstream consumers
- compact outputs
- deterministic reasoning

Rules:
- evidence contains facts only
- derive computes meaning in one place only
- adapters package or present canonical outputs
- CLI is presentation only
- governance protects semantic ownership and packet budgets

## Canonical Flow
1. Load diff evidence from a base/head comparison.
2. Persist canonical raw diff evidence.
3. Derive change risk, significance, and runtime relevance.
4. Build compact packets.
5. Print or export summaries.

## What DeltaBench Currently Does
Current MVP capabilities:
- canonical git diff ingestion
- changed-file to subsystem mapping
- explicit risk ranking
- blast radius estimate
- review packet generation
- benchmark recommendation packet generation
- compact CLI summaries
- semantic governance
- compression governance
- canonical flow testing

Current CLI:
- `deltabench diff --base <BASE> --head <HEAD>`
- `deltabench review-packet --base <BASE> --head <HEAD>`
- `deltabench benchmark-recommend --base <BASE> --head <HEAD>`

## Canonical Outputs
Current canonical packet surfaces:
- `review_packet`
  - what to review first
  - why it matters
  - confidence
  - low-risk files
- `benchmark_recommendation`
  - which changed files are runtime-relevant
  - why they justify rerunning BlueBench work
  - which runtime probe should be rerun
  - confidence

These packets must stay compact and machine-readable.

## Relationship to BlueBench
DeltaBench does not compute runtime truth.
DeltaBench does not import BlueBench internals.
DeltaBench may recommend runtime investigation, but it does not perform it.

Clean split:
- DeltaBench identifies change risk
- BlueBench measures runtime behavior

Together they support a larger engineering loop:
- change lands
- DeltaBench ranks review and benchmark relevance
- BlueBench verifies runtime impact

## What DeltaBench Is Not
DeltaBench is intentionally not, at this stage:
- a runtime profiler
- a UI product
- a historical intelligence system
- an experiment lab
- a benchmark engine
- a diff summarizer that embeds full patches
- an AI planner with open-ended reasoning

It should not grow sideways into BlueBench.

## Identity Guardrails
DeltaBench should stay:
- deterministic
- compact
- evidence-backed
- packet-first
- loosely coupled to runtime systems

DeltaBench should avoid:
- hidden scoring logic in adapters or CLI
- large narrative summaries
- full diff or patch embedding in packets
- runtime claims without runtime evidence
- tight coupling to BlueBench internals

## Current Status
Status: strong MVP foundation

What is already solid:
- canonical evidence / derive / adapters / reports structure
- compact review packet
- compact benchmark recommendation packet
- semantic producer ownership tests
- compression budget tests
- canonical flow tests

Main current strengths:
- clean architecture early
- explicit governance before packet sprawl
- focused purpose
- low ambiguity about what belongs in the tool

Main current limitations:
- no hotspot overlap yet
- no regression overlap yet
- no historical confidence layer yet
- no benchmark-result ingestion
- no UI
- no richer dependency fan-out model beyond the current simple mapping

## Near-Term Direction
The next good DeltaBench work should deepen change-risk usefulness without breaking identity.

Good next steps:
- hotspot overlap through a clean shared artifact interface
- regression overlap through history artifacts
- benchmark recommendation refinement without importing BlueBench internals
- stronger dependency fan-out mapping if it remains deterministic and inspectable

Bad next steps:
- bolting on runtime measurement logic
- adding a large UI before the packet model matures
- mixing speculative reasoning into derive outputs
- turning the tool into a generic agent planner

## Product Standard
A DeltaBench feature is only a fit if it improves one of these outputs:
- clearer review ordering
- clearer explanation of why a diff matters
- clearer recommendation for what to rerun next
- lower token cost for agents reviewing a change

If a proposed feature does not improve one of those directly, it probably does not belong in the current product.
