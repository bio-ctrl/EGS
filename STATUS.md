# EGS — Engineering Status

> **MANDATORY HANDOFF RULE FOR EVERY FUTURE AI SESSION:** "Read this file first, never fabricate numbers, keep Ceres untouched, and update `STATUS.md` on `main` after every major milestone."

**Last updated:** 2026-11-27  
**Repository:** `bio-ctrl/EGS`  
**Status scope:** Parent-company mission, project boundaries, verified engineering evidence, and active research queue.

---

## 1. Mission and operating philosophy

**EGS is the parent company.** The mission is to build a major advanced-computing and semiconductor company capable of competing in the same broad industry landscape as Nvidia and AMD. The long-term ambition is a vertically capable technology company: develop exceptional computing architectures and products first, then expand into the infrastructure required to make those products matter.

This is an ambition and direction, not a claim of present capability, market position, or validated commercial advantage. Engineering evidence must lead the claims.

**Founder philosophy / mottos:**

> "Big dreams push past what other people view as possible, often because 'unrealistic' just means a goal hasn't been done yet by the people around you. You have to dream unrealistic because life is not realistic"

> "Get what I want and when I want it"

Operating principles:
- Be ambitious about the destination and exacting about the evidence.
- Build real technology; do not substitute branding, websites, or fundraising language for engineering progress.
- Prefer reproducible experiments, explicit baselines, formal correctness checks, and honest negative results.
- Never describe pre-layout estimates as measured silicon performance or FPGA place-and-route results as ASIC results.
- Preserve all project boundaries and repository history. Avoid destructive changes.

## 2. Project boundaries — do not conflate

| Name | Role | Boundary |
|---|---|---|
| **EGS** | Parent company | The company-level mission and long-term advanced-computing / semiconductor ambition. |
| **ORCUS** | Active architecture-discovery and hardware platform | The engineering and research platform for exploring, validating, and evaluating computational architectures and hardware building blocks. |
| **NEM** | Separate project / possible product | Keep distinct from EGS and ORCUS. Do not assume it is the same product or platform. |
| **Ceres** | Separate project | **Never touch, modify, merge, rename, or mix Ceres with EGS or ORCUS.** No Ceres files, code, branches, or product assumptions belong in this work. |

All work described below is for EGS/ORCUS only. Ceres is explicitly out of scope.

## 3. Verified engineering baseline — ORCUS v0.2 on `main`

**Baseline merge commit:** `3fcf0024d621db90ac913d9671c1f60d8588c5d9` (short SHA: `3fcf002`)  
**Source PR:** #18  
**CI run:** #201, run ID `45892526069`  
**Benchmark artifact:** `orcus-signed-int4-dot-product` (artifact ID `15152386967`)  
**Benchmark head:** `1dc2492f4d481db7e23d3587dd5120d95da91181`  
**Verification:** all five variants passed Yosys SAT equivalence; each was simulated with 512 unique fixed-seed xorshift32 vectors; VCD activity was annotated in OpenSTA.

### Workload and measurement limits

Four-lane signed INT4 dot-product accumulation:

`y = a_0 b_0 + a_1 b_1 + a_2 b_2 + a_3 b_3`

The accumulator is 10-bit signed. The five tested reduction variants were evaluated using the same signed multiplier expressions and sign extension. Nangate45 is an open research standard-cell library, **not** a foundry PDK or manufacturable process. Area, delay, and power are **pre-layout library-based estimates without routed parasitics**. Power is estimated by OpenSTA Liberty power models with deterministic RTL VCD activity; it is not silicon measurement. The 512-vector stimulus is reproducible, not a claim of exhaustive workload coverage.

### Exact Run #201 results

| Variant | Yosys SAT | Generic cells | Nangate45 area | OpenSTA delay (ns) | Internal (µW) | Switching (µW) | Leakage (µW) | Total (µW) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Direct expression | PASS | 522 | 574.56 | 0.95 | 47.88638 | 43.71745 | 13.41678 | 105.02060 |
| Left-deep | PASS | 522 | 574.56 | 0.95 | 47.88638 | 43.71745 | 13.41678 | 105.02060 |
| Balanced 01/23 | PASS | 522 | 575.89 | 1.00 | 47.84778 | 43.61467 | 13.42982 | 104.89230 |
| Balanced 02/13 | PASS | 522 | 574.56 | 1.00 | 47.83237 | 43.72201 | 13.40231 | 104.95670 |
| Two-stage carry-save | PASS | 441 | 460.712 | 0.89 | 39.53044 | 34.28274 | 10.79658 | 84.60975 |

**Verified v0.2 result:** On this four-lane workload, two-stage carry-save reduced Nangate45 mapped area by **19.8%** (460.712 vs 574.56), OpenSTA critical-path delay by **6.3%** (0.89 ns vs 0.95 ns), and VCD-annotated total power estimate by **19.4%** (84.60975 vs 105.02060 µW), relative to the direct-expression baseline. It also reduced generic cell count from 522 to 441. All five variants passed Yosys SAT equivalence.

These are results for this specific benchmark and flow. They do not establish a general advantage across other widths, workloads, libraries, devices, or physical implementations.

## 4. Active experiment — PR #19: fused Baugh-Wooley multi-lane compressor

**PR:** [#19 — Experiment: fused four-lane signed INT4 partial-product compressor](https://github.com/bio-ctrl/EGS/pull/19)  
**Branch:** `research/orcus-fused-int4-mac`  
**Current head:** `80cf57c562993305a3f98b8d26292d484c7b682c` (short SHA: `80cf57c`)  
**PR state:** open, draft, unmerged  
**CI Run #203:** ID `45893609205`, head `561ac0725e34f47413445c582f8b64d2188adfd3`; conclusion `cancelled`; no artifact was uploaded.

### Run #203 failure history and diagnosis

Run #203 completed with `cancelled`, not with a failed SAT proof. The runner began setup at 2026-11-26 20:47:50 UTC and logged cancellation at 2026-11-27 02:48:02 UTC, approximately six hours later. The signed INT4 benchmark command began at 20:51:33 UTC. The job therefore reached GitHub Actions' default 360-minute job timeout while the benchmark command was still running. The available log does not identify which internal benchmark stage or which variant consumed the time; do not attribute the timeout to the fused variant's SAT proof without new stage-level evidence.

Before the benchmark command, the following steps passed:
- Pinned CUDD and OpenSTA builds and OpenSTA version verification.
- Unit tests.
- Python compilation.
- Nangate45 Liberty retrieval.

The benchmark step was cancelled; artifact upload and benchmark-target verification were skipped. **No Run #203 SAT results, 512-vector confirmations, VCD annotation counts, generic-cell counts, area, delay, or power results are available.** The fused candidate's win/loss outcome is therefore **NOT DETERMINED**. Do not fill the PR #19 comparison table with estimates or copy v0.2 metrics into PR #19 results.

Run #202 (ID `45892529710`) remains recorded as a prior failed attempt: its unit test incorrectly assumed all variants shared identical multiplier expressions. The test was corrected to distinguish the fused Baugh-Wooley implementation from the product-level reduction baselines. Preserve this failure history.

### Corrective work committed to the PR branch

The branch now contains:
- A structured OpenSTA parser for internal, switching, leakage, and total power. It retains raw Watts values and emits explicit µW fields.
- A fail-closed check for a parsed OpenSTA total-power row and nonzero VCD pin-activity annotation.
- A fail-closed check that the deterministic xorshift32 stimulus contains exactly 512 unique vectors.
- Unit tests for all four power components and rejection of missing VCD annotation.
- Per-variant, per-stage progress logging for Yosys SAT/synthesis, simulation, and OpenSTA; CI invokes Python unbuffered so the last completed stage is visible in logs.

Relevant branch commits include parser correction `ff07eefa`, parser tests `cd52b71e`, stage logging `cd6ea2f5`, and unbuffered CI logging `80cf57c5`. The latest branch head is `80cf57c5`. These code changes have **not yet passed a new CI run**. Reopening PR #19 did not produce a new Actions run in the latest check.

### Required PR #19 closure gates

1. Obtain a fresh CI run on the current branch head. If the benchmark again approaches the six-hour job limit, use the new progress logs to identify the exact variant and stage; then reduce or partition that work rather than claiming an unobserved failure cause.
2. Inspect the uploaded artifact and raw OpenSTA reports for all six variants.
3. Verify Yosys SAT equivalence for all six variants, exactly 512 unique fixed-seed xorshift32 vectors per variant, and nonzero clean VCD pin-activity annotation for every OpenSTA run.
4. Populate the exact comparison table only from the artifact: Variant, Yosys SAT, Generic cells, Nangate45 area, OpenSTA delay, Internal µW, Switching µW, Leakage µW, Total µW.
5. Compare fused Baugh-Wooley with the direct-expression baseline and existing two-stage carry-save baseline. Record whether it wins or loses on this workload, including any trade-offs; do not generalize beyond the measured configuration.
6. Keep PR #19 open and unmerged until all evidence is reviewed. Do not merge without explicit authorization.

### Milestone #2 — scale signed INT4 dot products

After PR #19 has a complete, reviewed four-lane result, generalize the workload to 8, 16, and 32 lanes:
- Use 11-bit, 12-bit, and 13-bit signed accumulators respectively.
- Compare direct-expression, multi-stage carry-save, and fused Baugh-Wooley multi-lane compression.
- Require formal equivalence for every candidate and retain reproducible 512-vector xorshift32 activity per configuration.
- Record generic cells, Nangate45 area, OpenSTA delay, internal/switching/leakage/total power, tool versions, constraints, and raw artifacts separately for each lane count.
- Keep all Nangate45 results labelled as pre-layout research-library estimates without routed parasitics, not silicon PPA.
- Preserve the v0.2 four-lane baseline as the fixed reference; do not overwrite or silently rebase its historical measurements.

## 5. Engineering roadmap

Work in this order, with each milestone backed by committed source, tests, CI, and raw artifacts:

1. **Close PR #19.** Complete the six-variant four-lane comparison, verify formal SAT for every variant, inspect raw OpenSTA reports and power components, correct parser gaps if needed, and preserve the outcome whether fused Baugh-Wooley wins or loses.
2. **Scale signed INT4 dot products.** Generalize the benchmark to 8, 16, and 32 lanes. Use exact signed accumulator widths: 11 bits for 8 lanes, 12 bits for 16 lanes, and 13 bits for 32 lanes. Compare the direct expression against multi-stage carry-save and fused Baugh-Wooley partial-product compression. Require equivalent formal proof for every candidate; if proof strategy changes at larger widths, document the precise method and its limits. Keep identical constraints and reproducible 512-vector xorshift32 activity for comparable measurements.
3. **Run open-source FPGA validation.** Build an automated Ubuntu CI flow using Yosys FPGA synthesis (appropriate supported family such as iCE40, ECP5, or Xilinx) and nextpnr. Compare 4-, 8-, and 16-lane direct baselines against the best formally verified ORCUS reduction architecture. Report device/part, tool versions, constraints, LUTs, carry resources/chains where exposed by the tool, registers/flip-flops, and post-route Fmax. Label each result by FPGA family and exact target. Do not call synthesis-only estimates place-and-route proof.
4. **Build an EGS MAC + local-memory inference tile.** Integrate the selected, verified MAC/reduction architecture with a defined local-memory subsystem. Establish interface contracts, memory organization, supported data types, latency/throughput targets, verification strategy, and reproducible synthesis/implementation benchmarks before making performance claims.

## 6. Evidence and repository rules

- **Never fabricate numbers.** If a metric is missing, say `not measured` or `not available`.
- Formal SAT equivalence is mandatory for every variant before it is described as verified. Distinguish proof success from simulation coverage.
- Keep raw CI artifacts and logs for every reported result. Record commit SHA, workflow run ID, tool versions, library/device, constraints, and stimulus details.
- Keep generic cell counts, Nangate45 mapped area, OpenSTA timing/power, and FPGA place-and-route results as separate metric classes.
- Nangate45 figures are pre-layout research-library estimates, not silicon PPA.
- FPGA resource and Fmax claims require a completed device-specific nextpnr place-and-route run; record the exact FPGA target and tool version.
- Do not compare results across different constraints, libraries, devices, or activity profiles as if they were controlled experiments.
- Keep experimental branches separate from `main` until review and verification are complete. Do not merge a PR unless the requested verification gates pass.
- Preserve Ceres unchanged and independent at all times.
- Update this file on `main` after every major engineering milestone, using exact verified values and clearly dated pending states.
