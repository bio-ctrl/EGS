# ORCUS Search v2 — Technical Specification

**Status:** Proposed implementation contract  
**Date:** 26 November 2026  
**Target:** Isolated ORCUS research branch; no change to main or Ceres.

## 1. Decision

Search v2 should be an orchestration layer around the existing ORCUS generators, not a rewrite. It must make candidate generation, structural identity, verification, scoring, provenance, and outcomes consistent across experiments.

**Primary deliverable:** one command runs a bounded experiment and emits a complete machine-readable record for every candidate considered, including duplicates, invalids, unverified candidates, losses, timeouts, and candidates skipped by budget.

The first release supports existing bit-vector graphs and arithmetic/compressor generators. It does not claim unrestricted circuit invention, global optimality, physical PPA prediction, or general superiority over Yosys/ABC.

## 2. Current baseline and gaps

The research branch already contains Boolean synthesis, multi-output DAG search, a typed bit-vector graph, adder families, associative/commutative tree enumeration, compressor networks, Verilog export, tests, and Yosys-backed experiments.

Search v2 must address these concrete gaps:

1. The associative generator enumerates permutations and tree shapes eagerly. When the candidate count exceeds its cap, it raises an exception rather than returning a valid partial experiment with a stop reason.
2. Candidate identity is currently tied to enumeration names/topologies. There is no versioned stable structural digest or common provenance envelope.
3. Search reports do not share one candidate-outcome schema across associative, adder, multi-output, and compressor experiments.
4. Verification strength varies. Some checks are exhaustive; larger adder cases sample only the first 256 values per operand. Sampled checks must never be confused with exhaustive or formal proof.
5. Scoring emphasizes structural operation count, depth, and fanout. These are not target-library area, routed delay, power, or energy.
6. No single experiment record ties candidate lineage, proof evidence, synthesis reports, tool versions, runtime, and terminal outcome together.

These are implementation gaps, not evidence that prior results are incorrect. Preserve existing APIs until replacement tests establish compatibility.

## 3. Non-goals

The first release will not:
- Claim complete graph-isomorphism canonicalization for arbitrary DAGs.
- Claim global optimality outside its declared grammar and budget.
- Treat a Pareto frontier as physical optimality.
- Treat generic Yosys cell count as standard-cell area or physical PPA.
- Treat structural depth or switching proxies as measured delay or power.
- Automatically select an accelerator architecture or infer customer value.
- Delete or rewrite existing research reports, generators, or historical results.

## 4. System architecture

Experiment configuration
→ candidate generator
→ candidate stream
→ canonicalizer and registry
→ verification gate
→ structural metrics and optional external evaluators
→ outcome classifier
→ append-only JSONL records and final summary.

Suggested modules, subject to existing repository conventions:
- orcus/search/config.py — validated configuration and budgets.
- orcus/search/candidate.py — candidate envelope and lineage.
- orcus/search/canonical.py — deterministic serialization and supported-form canonicalization.
- orcus/search/registry.py — digest registry and duplicate aliases.
- orcus/search/budget.py — limits and stop reasons.
- orcus/search/verification.py — normalized proof status.
- orcus/search/evaluation.py — structural metrics and external tool adapters.
- orcus/search/report.py — append-only records and summary.
- orcus/search/runner.py — orchestration.

Do not create empty placeholder modules. Implement and test one vertical slice at a time.

## 5. Candidate identity and provenance

Every candidate envelope must include:
- Stable candidate digest.
- Candidate type and workload identifier.
- Canonicalizer version and grammar identifier/version.
- Parent candidate IDs and transformation/generator identifier.
- Deterministic generation index.
- Parameters: width, operand count, signedness, operator, schedule, and relevant constraints.
- Payload hash, source commit, and experiment ID.

Canonicalization must be conservative:
1. Serialize node/operator types, widths, ports, outputs, and edges deterministically.
2. Normalize operand order only for operators whose commutativity is established by the IR semantics.
3. Normalize associative tree forms only where associativity is valid for the exact width, overflow, and signedness semantics.
4. Preserve DAG sharing as a first-class property.
5. Include widths, signedness, constants, and output ordering in identity.
6. Version the algorithm; a version change creates a new identity namespace.
7. If a graph cannot be safely canonicalized, mark identity unsupported. Never guess.

The first implementation may support only the existing typed bit-vector DAG. It must document and test that subset. Do not describe partial canonicalization as general graph isomorphism.

## 6. Deterministic budgets and stopping semantics

Every experiment declares:
- Maximum generated candidates.
- Maximum unique candidates.
- Maximum graph depth, where meaningful.
- Maximum verification runs.
- Maximum synthesis runs.
- Maximum runtime.
- Maximum memory, only if reliably enforceable.

A reached limit ends the relevant stage cleanly and records a stop reason. The report remains valid and parseable after early termination. The runner must not silently drop candidates. Generation should stream where practical instead of materializing a combinatorial search space before discovering that it exceeds a cap.

The same config, source commit, and seed must produce the same candidate order and stopping point, except for explicitly wall-clock-dependent limits. Wall-clock and memory limits are environment-dependent and must be labeled accordingly.

Stop reasons include completed, candidate-budget-exhausted, verification-budget-exhausted, synthesis-budget-exhausted, runtime-budget-exhausted, memory-budget-exhausted, generator-error, and cancelled.

## 7. Verification gate

Normalize verification into these statuses:

| Status | Meaning | Eligible for verified frontier |
|---|---|---:|
| exhaustive-pass | All assignments in the declared finite domain checked | Yes |
| formal-pass | Independent formal/equivalence tool proved the declared property | Yes |
| sampled-pass | Declared sample set passed; not proof of equivalence | No; provisional only |
| not-run | Verification not attempted | No |
| failed | Counterexample or mismatch found | No |
| tool-error | Tool failed or result could not be interpreted | No |

Every record includes method, tool/version, vector count, input domain, proof/log artifact location, and exactly what was established.

A sampled result must never be serialized as an unqualified passed=true. Sampled candidates may be shown as provisional exploration results, but not as verified optimizations.

## 8. Evaluation and objective model

Keep objective dimensions separate. Do not collapse incomparable quantities into one opaque score by default.

**Structural metrics**
- Unique operation/gate count.
- Logic depth.
- Fanout distribution and maximum fanout.
- Input fanout and graph size.
- Generator and evaluation runtime.

**Tool-reported metrics**
- Yosys/ABC generic cell count and cell-type breakdown.
- Sequential cells/registers.
- Memory cells/bits and mux counts, where supported.
- Synthesis runtime, warnings, errors, target library, and mapping status.

**Physical metrics — future adapter only**
- Mapped standard-cell area.
- Critical-path delay and constraints.
- Routed wire metrics/congestion.
- Power, with method and whether measured or estimated.

Every metric carries value, unit, evidence class (structural, tool-reported, modeled, or measured), source tool, and source version where relevant. Never compare modeled and measured values as if they were equivalent.

Pareto rules:
- Objective list and minimize/maximize direction belong in experiment config.
- Missing metrics make candidates incomparable; never replace missing values with zero.
- Only candidates passing the required verification gate enter the verified frontier.
- Preserve all candidates and rank status, including dominated candidates.
- Tie-breaking is deterministic and documented.
- State that the frontier is relative to the generated candidate set, not globally optimal.

## 9. Candidate outcomes

Each candidate receives stage-specific outcomes. Supported values include generated, duplicate, invalid, verification-failed, verification-tool-error, sampled-only, verified, synthesis-failed, synthesis-timeout, evaluated-win, evaluated-tie, evaluated-loss, dominated, and skipped-by-budget.

Stage outcomes must not overwrite one another. A candidate may be verified and later fail synthesis; both facts remain in its record.

## 10. Machine-readable reports

Use append-only JSON Lines for candidate events and one final JSON summary. Include a schema version.

The experiment summary must contain:
- Schema version and stable experiment ID.
- Source commit.
- Grammar and canonicalizer versions.
- Full config and environment/tool versions.
- Counts for generated, unique, duplicate, verified, sampled, failed, wins, ties, and losses.
- Stop reason.
- Verified frontier candidate IDs.
- Limitations and warnings.

Each candidate event must contain:
- Schema version and experiment ID.
- Candidate digest and generation index.
- Candidate type, parent IDs, transformation, and parameters.
- Verification status and method.
- Metrics with units/evidence classes.
- Stage outcomes, duplicate target, and errors.

Validate the schema and document required/optional fields. Do not invent timestamps, source commits, tool versions, or evidence paths when unavailable; represent missing values explicitly with a reason.

## 11. Benchmark protocol

Before each run, define:
- Exact workload and input/output semantics.
- Width, signedness, overflow behavior, operand count, and constraints.
- Reference implementation and source.
- Baseline synthesis flow, tool version, and settings.
- Candidate grammar and search budget.
- Primary metric and tie tolerance.
- Verification requirement.
- Development versus held-out workload split.

Run baseline and candidate through the same flow/settings. Preserve raw reports for every candidate, including ties, losses, timeouts, and failures. Report per-workload deltas and aggregate statistics; never publish only the best candidate.

The existing four-operand, three-bit compressor case is a development case, not sufficient held-out evidence. Add widths and operand counts only after correctness/runtime are controlled. Reserve at least one workload family for held-out evaluation.

## 12. CLI contract

Proposed command:

    python -m orcus search run --config experiments/search_v2_smoke.json --output artifacts/search-v2/

The command must validate config, capture source/environment metadata, generate deterministically within budgets, deduplicate supported forms, verify before verified ranking, evaluate only eligible candidates, and write candidate records plus a final summary even after budget exhaustion.

A budget stop is a valid experiment outcome. Return non-zero for invalid config, unrecoverable infrastructure failure, or an explicitly configured fail-on-candidate-error policy.

A small smoke config belongs in CI. Long research runs should remain opt-in.

## 13. Acceptance matrix

| Area | Required test | Acceptance |
|---|---|---|
| Identity | Same graph across process runs | Same digest |
| Commutativity | Swap supported commutative operands | Same digest |
| Width semantics | Same graph at different widths | Different digest |
| Signedness/overflow | Different declared semantics | Different digest |
| DAG sharing | Shared vs duplicated subgraph | Sharing distinction preserved |
| Unsupported form | Unknown node/operator | Explicit unsupported status |
| Budgets | Candidate cap reached | Valid partial report and exact stop reason |
| Determinism | Repeat same config/seed | Same IDs and ordering |
| Verification | Inject incorrect candidate | Excluded from verified frontier |
| Sampling | Sampled-only run | Never labeled formal/exhaustive |
| Synthesis | Tool missing/fails/times out | Explicit status and diagnostics |
| Pareto | Known metric fixtures | Correct dominance and deterministic ties |
| Reports | Interrupt after event write | Existing JSONL remains parseable |
| Compatibility | Existing generators/tests | No regression or explicit versioning |

## 14. Implementation sequence

**Slice 1 — records and provenance:** typed config, candidate envelope, schema validation, experiment ID, source commit capture, JSONL writer. Test serialization before changing generators.

**Slice 2 — canonical identity and registry:** implement one supported graph type, duplicate aliases, and cross-process determinism. Expand only when semantics are explicit.

**Slice 3 — streaming generation and budgets:** adapt associative generation to yield candidates incrementally. Preserve its current convenience API if needed. Add deterministic budgets and valid partial reports.

**Slice 4 — verification and scoring:** normalize exhaustive/formal/sampled statuses. Prevent sampled-only candidates from entering the verified frontier. Make objective directions and missing metrics explicit.

**Slice 5 — synthesis adapter:** normalize Yosys invocation, version, logs, timeout, cell metrics, and errors. Add a small CI smoke run.

**Slice 6 — broader evaluation:** add widths/operand counts, held-out workloads, strong baselines, and full win/tie/loss distributions.

## 15. Release gates

Search v2 is not ready for a tagged research release until:
- Acceptance tests pass for the supported subset.
- Existing tests and baselines remain reproducible.
- Candidate records are complete and schema-versioned.
- Budget exhaustion produces valid partial reports.
- Verification classes cannot be confused.
- Search coverage and limitations are explicit.
- A clean-checkout reproduction is archived.
- No unsupported PPA, novelty, or competitor-superiority claim is added.

## 16. Strategic relevance to EGS

A search engine is not itself a semiconductor moat. Its potential value is a repeatable capability to discover and validate better implementations for workloads that matter. ORCUS must earn that value through independent results, technology-aware evaluation, and customer-relevant use cases.

NVIDIA and AMD are long-horizon reference points, not the immediate benchmark. The next proof is smaller and harder: on a defined workload, generate a correct candidate that consistently beats a strong baseline under identical tools and constraints, with raw evidence another engineer can reproduce.

**Execution rule:** preserve existing research, implement one tested slice at a time, and let measured outcomes—not ambition or branding—determine the next architectural bet.
