# EGS — Five-Week ORCUS Execution Plan

**Execution window:** 26 November–31 December 2026  
**Parent company:** EGS  
**Active research platform:** ORCUS  
**Baseline:** ORCUS v0.1.0 research prototype  
**Working research branch at plan creation:** `research/joint-multioutput-search-v1`  
**Related pull request:** [#13 — Add bounded joint multi-output architecture search](https://github.com/bio-ctrl/EGS/pull/13)  
**Status:** execution plan; milestones are targets, not completed work.

## Mission and operating standard

EGS's long-term ambition is to become a foundational computing and semiconductor company. The immediate job is narrower: turn ORCUS into a reproducible architecture-search and hardware-evaluation workflow whose claims survive independent inspection.

The operating philosophy is to think beyond what is currently familiar while proving every technical claim with evidence. Ambition does not waive engineering standards. Do not manufacture results, hide regressions, conflate simulation with hardware, or prioritize cosmetic materials over technical proof.

## 1. Current verified baseline

The following is the repository snapshot inspected when this plan was written. Recheck branch heads, PR state, and CI before acting because GitHub state can change.

### Repository and PR snapshot

- Repository: `bio-ctrl/EGS`.
- PR #13 is open and marked draft, targeting `main` from `research/joint-multioutput-search-v1`.
- The inspected PR head was `a81bd2f3aa05b7870efae71be9abb084e1a3bdd7`; the inspected `main` base was `88336a8f5205744ce24efd182a5f683c2fa73373`.
- At inspection, the branch comparison reported 100 commits ahead and 0 behind.
- The latest inspected PR-triggered ORCUS CI run was run #170 and completed successfully. Its job included unit tests, Python compilation, benchmark target checks, joint-search, bit-vector, adder, associative architecture, and compressor-network experiments.
- No PR reviews or inline review threads were present at inspection.
- No merge was performed as part of preparing this plan.

**PR handling rule:** review the complete diff, changed-file list, commit history, workflow status, and repository protection rules before merging. Do not merge solely to clear a queue. Preserve the research branch until the merge is verified. Do not force-update `main`, delete the branch prematurely, or modify Ceres.

### Existing ORCUS capabilities

The research branch contains a Boolean synthesis engine, circuit and multi-output DAG representations, structural common-subexpression handling, width-aware bit-vector IR, ripple/Kogge–Stone/Sklansky adder generators, bounded associative topology search, Wallace/Dadda-family compressor-network generation, Verilog export, exhaustive checks for tractable workloads, Yosys SAT/equivalence and generic-cell synthesis experiments, benchmark runners, tests, and GitHub Actions CI.

The current `orcus/architecture_search.py` already enumerates labeled binary-tree topologies for selected associative/commutative operators. Search v2 should extend this existing work rather than rewrite it without evidence.

### Existing experimental evidence and limits

1. **Multi-output joint search:** five cases; structural DAG gate count improved in two, tied in three, and regressed in none. Yosys generic-cell count tied the baseline in all five.
2. **Associative architecture search:** 15 candidate topologies passed the recorded exhaustive checks and Yosys SAT equivalence checks; all mapped to the same 12 generic cells as the direct-expression baseline.
3. **Compressor-network experiment:** nine candidates for four unsigned 3-bit operands; all passed exhaustive checking and recorded Yosys SAT equivalence. Wallace + ripple used 40 generic cells versus 43 for the direct-arithmetic reference; reversed Wallace + ripple used 41; two candidates tied and five regressed.

These are narrow, small-workload generic-synthesis observations. They do not establish standard-cell area, routed timing, power, energy, FPGA advantage, silicon performance, algorithmic novelty, customer value, or commercial superiority.

## 2. Five-week delivery schedule

### Week 1 — 26 November–2 December: stabilize the baseline

**Objectives**
- Resolve the status and disposition of PR #13 through review, not haste.
- Preserve the existing research state and make a reproducible baseline snapshot.
- Freeze benchmark definitions and baseline outputs before Search v2 changes.

**Tasks**
1. Re-fetch PR #13, branch heads, full diff, changed files, checks, reviews, and repository rules.
2. Review the 100-commit comparison as a whole; identify unrelated or risky changes and any generated artifacts that should not be merged.
3. Decide whether PR #13 can be safely merged as one reviewed unit or should be split. Record the rationale.
4. Preserve the current research branch and tag or otherwise identify the exact baseline commit.
5. Re-run the existing unit tests and benchmark commands from a clean checkout; archive raw output, tool versions, commit SHA, and environment details.
6. Write a Search v2 specification before implementation: grammar, candidate identity, budget semantics, metrics, proof requirements, and benchmark suite.
7. Record available hardware resources and identify whether a suitable FPGA board and vendor/open toolchain are actually accessible.

**Exit criteria**
- PR disposition documented; no unreviewed force push or destructive branch operation.
- Baseline can be reproduced from a clean checkout.
- Benchmark inputs, baselines, commands, and tool versions are recorded.
- Search v2 design specification is reviewed and versioned.
- FPGA access is confirmed or explicitly marked as a blocking dependency.

### Week 2 — 3–9 December: ORCUS Search v2

**Objectives**
- Generalize compositional candidate generation.
- Make candidate identity deterministic and remove structurally duplicate candidates before expensive evaluation.
- Make search limits explicit and reproducible.

**Required capabilities**
1. **Compositional grammar:** define legal operators, operand widths, graph composition rules, and constraints. Support generation of candidate subgraphs and multi-output DAGs where the IR permits them. State clearly which equivalence classes the grammar does and does not cover.
2. **Canonical structural identity:** create a stable canonical serialization/hash for supported graph forms. Account for commutative operand ordering and graph sharing. Do not claim full graph-isomorphism canonicalization unless the implementation and tests establish it.
3. **Deduplication:** deduplicate before formal proof and synthesis. Preserve the canonical candidate and record duplicate aliases and their provenance.
4. **Deterministic budgets:** enforce candidate, depth, wall-clock, memory, and expensive-tool-call budgets. A budget stop must produce a valid partial report with an explicit stopping reason, not silently discard work or raise an opaque failure.
5. **Reproducibility:** record seed, generator version, grammar version, search parameters, source commit, and deterministic ordering.
6. **Candidate lineage:** record parent candidates, applied transformations, generation parameters, and candidate hashes.
7. **Complete outcomes:** record win, tie, loss, invalid candidate, proof failure, synthesis failure, timeout, skipped, and budget-exhausted states.
8. **Verification gate:** no candidate is ranked as a valid optimization unless it passes the required functional or formal verification stage.

**Tests**
- Canonical identity is stable across process runs.
- Equivalent commutative representations canonicalize identically where supported.
- Distinct non-equivalent structures do not collapse in test fixtures.
- DAG sharing is represented consistently.
- Budgets stop deterministically and produce complete partial reports.
- Repeated runs with the same inputs and seed produce the same candidate identities and ordering.
- Invalid candidates cannot enter the scored frontier.

**Exit criteria**
- One command runs a bounded Search v2 experiment.
- Tests cover canonicalization, deduplication, budget exhaustion, provenance, and deterministic output.
- Every generated candidate has a machine-readable outcome record.

### Week 3 — 10–16 December: synthesis-aware and data-movement metrics

**Objectives**
- Extend the Yosys evaluation pipeline beyond a single generic-cell count.
- Separate actual tool-reported quantities from structural proxies and analytical estimates.
- Establish a falsifiable memory-locality experiment specification.

**Synthesis metrics to capture where supported by the selected Yosys flow**
- Total generic cells and cell-type breakdown.
- Sequential cell and register counts, with cell types.
- Inferred memories, memory bits, and memory-related cells before/after relevant memory passes.
- Multiplexer, buffer, and logic cell counts where reported.
- Logic depth or a clearly documented structural depth metric.
- Fanout distribution and maximum fanout.
- Synthesis runtime, warnings, and failures.

Do not infer physical wire length, routed congestion, clock power, or physical area from generic synthesis output.

**Data-movement model**
For each workload, define and record:
- Input and output bytes.
- Intermediate values and their widths.
- Number of reads and writes at each modeled storage level.
- Reuse distance or reuse count where meaningful.
- Estimated bytes transferred under explicitly stated assumptions.
- Storage capacity and access assumptions.
- Arithmetic operations and operational intensity.

Label these as workload-model estimates unless measured by a real profiler or hardware counter. Do not present a data-movement proxy as measured bandwidth or energy.

**Memory-first inference hypothesis**
Treat memory-first inference as a research hypothesis, not an existing EGS advantage. Select one small, representative inference or matrix workload, define precision and correctness, choose a conventional baseline, and pre-register the measurements. Compare locality/data reuse under identical workload and device conditions. If no suitable hardware profiler or device exists, limit conclusions to software-model results.

**Exit criteria**
- Yosys reports preserve raw logs and structured metrics.
- Register and memory metrics are tested against known small RTL fixtures.
- Every metric has a definition, unit, source, and evidence class: measured, tool-reported, structurally derived, or modeled.
- A memory-first experiment spec defines workload, baseline, controls, and falsifiable success criteria.

### Week 4 — 17–23 December: first FPGA validation

**Objective**
Run one genuine FPGA implementation and hardware validation, provided board and tool access are confirmed.

**Candidate demonstration**
Use a verified ORCUS-generated arithmetic datapath, such as the multi-operand compressor-network workload, against a conventional reference implementation. The two designs must use identical input/output behavior, widths, clock constraints, device, tool settings, and test conditions.

**Required sequence**
1. Confirm exact FPGA board, part number, toolchain/version, licensing, and access.
2. Freeze the RTL and testbench commit.
3. Simulate both implementations and verify equivalence.
4. Synthesize and implement both under identical constraints.
5. Preserve full build logs and implementation reports.
6. Program the device and run deterministic input/output tests if physical board access is available.
7. Record resource use: LUTs or equivalent logic, flip-flops, BRAM, DSP blocks, and other relevant resources.
8. Record clock constraint, achieved frequency, critical-path slack, and timing-analysis status.
9. Measure latency and throughput using a documented protocol.
10. Measure board power only with suitable instrumentation and a documented method. If using a vendor estimate, label it as an estimate and retain the report.

**Evidence labels**
- RTL simulation is simulation.
- FPGA synthesis/implementation reports are FPGA implementation estimates.
- Board execution is hardware validation.
- Board power instrumentation is measured power only if the instrument and method are documented.
- FPGA results are not ASIC PPA and do not establish silicon behavior.

**Fallback if no board is accessible**
Do not call simulation an FPGA demonstration. Complete a reproducible FPGA synthesis/implementation flow only if a valid target and toolchain are available, label it as implementation-only, and move board validation to a later milestone. Record the blocker and the next concrete access requirement.

**Exit criteria**
- Baseline and candidate are functionally equivalent.
- Full build and timing reports are archived.
- Resource and timing results are reported with device/tool/constraint context.
- If a board is available, hardware input/output validation is archived.
- No unsupported ASIC, silicon, or physical-PPA claim is made.

### Week 5 — 24–31 December: evidence freeze and data room

**Objectives**
- Freeze reproducible technical artifacts.
- Organize the data room around verified claims.
- Prepare a truthful funding and outreach package.

**Technical data-room contents**
- ORCUS source commit and release identifier.
- Environment and installation instructions.
- Search v2 grammar, budget, canonicalization, and provenance specification.
- Benchmark suite, workload definitions, and baseline provenance.
- Raw JSON/JSONL results for every candidate and every outcome.
- Formal/equivalence scripts and proof logs.
- Yosys scripts, version information, raw synthesis reports, and warnings.
- FPGA RTL, constraints, build scripts, implementation reports, and hardware test results if obtained.
- Metric definitions and evidence labels.
- Failed experiments, regressions, timeouts, known limitations, and reproduction instructions.
- IP/dependency inventory and ownership questions for qualified review.

**Investor package**
- Update the technical overview and investor deck only from frozen evidence.
- Distinguish prototype capabilities, measured results, hypotheses, and roadmap.
- Include the narrow compressor result with workload and limitations, not as a generalized hardware advantage.
- Update the financial model from actual role, vendor, tool, equipment, and lab assumptions.
- Track qualified introductions, meetings, diligence requests, follow-ups, and actual commitments separately.
- No invented customers, partnerships, revenue, endorsements, IP protection, or investor interest.

The December fundraising sprint has an aspirational US$10 million target. It is not a forecast, committed capital, or a guaranteed outcome. The purpose of the technical sprint is to improve the quality of evidence available for financing discussions, not to promise that financing will close by the deadline.

Because the founder is a minor, company formation, securities-related solicitation, equity, financing agreements, IP assignments, licensing, and other binding company arrangements require appropriate adult involvement and qualified legal counsel. This plan is not legal advice or an offer to sell securities.

**Exit criteria**
- Data room index points to versioned source evidence.
- Key benchmark claims can be reproduced from archived artifacts.
- Investor materials match the evidence register.
- Funding pipeline records actual status without implying commitments.
- January 2027 technical and commercial next steps are documented.

## 3. Cross-cutting technical design requirements

### Experiment record schema

Every candidate should have, at minimum:
- Experiment ID and timestamp.
- Repository commit SHA and source hash.
- Generator, grammar, and canonicalization versions.
- Workload ID, operand count, width, signedness, and interface.
- Baseline definition and provenance.
- Search seed and all budget parameters.
- Candidate canonical hash and lineage.
- Verification method, status, vectors checked, and proof artifact location.
- Synthesis tool/version, settings, constraints, and raw report location.
- Metrics with units and evidence classification.
- Runtime and resource consumption.
- Outcome classification and reason.
- Deviations, warnings, failures, and notes.

### Benchmark integrity

- Define primary metrics and benchmark cases before broad search.
- Separate development cases from held-out evaluation cases.
- Compare against strong baselines under identical conditions.
- Preserve all generated candidates and all outcomes.
- Report per-case results, aggregate summaries, medians/spread where meaningful, and runtime.
- Never tune the candidate carefully while leaving the baseline weak or under-specified.
- A generic-cell reduction is not a physical area reduction.
- A lower operation count is not proof of lower latency or energy.
- A switching proxy is not power.
- A modeled memory-traffic estimate is not measured bandwidth.

## 4. Critical dependencies and decision gates

| Dependency | Required decision | If unavailable |
|---|---|---|
| PR #13 review | Complete diff and branch review before merge | Keep branch isolated; do not force merge |
| Clean baseline | Reproduction from pinned commit | Fix reproducibility before claiming progress |
| Yosys flow | Pin version and scripts | Report missing metrics rather than inventing them |
| FPGA board | Confirm device and physical access | Mark hardware validation blocked; do not relabel simulation |
| FPGA toolchain | Confirm version, license, and target support | Use only a documented available flow |
| Power instrumentation | Confirm instrument and method | Omit measured power; label estimates accurately |
| Legal/IP review | Adult representative and qualified counsel | Prepare documents only; do not execute binding transactions |

## 5. Weekly operating dashboard

Track these numbers every week:
- Candidates generated, deduplicated, verified, and synthesized.
- Wins, ties, losses, invalids, proof failures, synthesis failures, and timeouts.
- Search runtime, memory use, and budget utilization.
- Correctness/CI status.
- Per-workload baseline deltas.
- FPGA implementation status, resources, timing, and hardware test status.
- Data-room artifact completeness.
- Customer discovery conversations and documented feedback.
- Qualified investor introductions, meetings, diligence requests, and actual commitments.
- Outstanding blockers, owners, and due dates.

## 6. Definition of success on 31 December

A successful sprint means:
1. PR #13 has a documented, safe disposition and the research baseline is preserved.
2. ORCUS Search v2 has generalized, bounded, deterministic generation with structural identity, deduplication, provenance, verification gates, and complete outcome logs.
3. Broader benchmark results include wins, ties, regressions, and failures.
4. Yosys reports include supported register and memory metrics, while data-movement estimates are clearly labeled.
5. A real FPGA validation is completed if board/tool access permits; otherwise, the blocker and implementation-only evidence are explicitly documented.
6. The technical data room contains versioned, reproducible artifacts.
7. Investor materials make only claims supported by the evidence.

A breakthrough, physical ASIC PPA advantage, a $10 million financing close, and silicon validation are not guaranteed deliverables for this five-week window. They remain future outcomes to earn through further research, validation, customer evidence, and execution.

## 7. Project boundaries

- **EGS** is the parent-company identity and mission.
- **ORCUS** is the active computational-architecture discovery and synthesis research platform.
- **NEM** is a separate platform concept and must retain a distinct technical thesis.
- **Ceres** is a separate project. Do not modify it, merge its work into ORCUS, or use it as a dependency for this sprint.

The immediate priority is ORCUS evidence. Do not substitute branding, speculative product claims, or headquarters concepts for technical progress.
