# EGS — Engineering Status

> **PERMANENT MANDATORY HANDOFF RULE — EVERY ACTION, EVERY SESSION:** "Read `STATUS.md` on `main` first, never fabricate numbers, keep Ceres untouched, and update and commit `STATUS.md` on `main` after EVERY single action, experiment, diagnostic, failure, timeout, or milestone—permanently across every session—so a future AI session with zero chat history can recover the exact state immediately."

**Last updated:** 2026-11-27 04:33:18 UTC  
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
**Current head:** `fb11b4dcfabb92e651759259edb953ff8521dbde` (short SHA: `fb11b4d`)  
**PR state:** open, ready for review, unmerged  
**Last checked:** 2026-11-27 04:33:18 UTC  
**Run #203:** ID `45893609205`, head `561ac0725e34f47413445c582f8b64d2188adfd3`; conclusion `cancelled`; no artifact was uploaded.  
**Fresh PR run:** none observed for current head `fb11b4d` as of 2026-11-27 04:32:50 UTC. A post-update `fetch_commit_workflow_runs` query for exact head `fb11b4dcfabb92e651759259edb953ff8521dbde` returned an empty list. Do not mistake main-branch runs #207–#210 for PR #19 validation.

### Run #203 failure history and diagnosis

Run #203 completed with `cancelled`, not with a failed SAT proof. The runner began setup at 2026-11-26 20:47:50 UTC and logged cancellation at 2026-11-27 02:48:02 UTC, approximately six hours later. The signed INT4 benchmark command began at 20:51:33 UTC. The job therefore reached GitHub Actions' default 360-minute job timeout while the benchmark command was still running. The available log does not identify which internal benchmark stage or which variant consumed the time; do not attribute the timeout to the fused variant's SAT proof without new stage-level evidence.

Before the benchmark command, the following steps passed:
- Pinned CUDD and OpenSTA builds and OpenSTA version verification.
- Unit tests.
- Python compilation.
- Nangate45 Liberty retrieval.

The benchmark step was cancelled; artifact upload and benchmark-target verification were skipped. **No Run #203 SAT results, 512-vector confirmations, VCD annotation counts, generic-cell counts, area, delay, or power results are available.** The fused candidate's win/loss outcome is therefore **NOT DETERMINED**. Do not fill the PR #19 comparison table with estimates or copy v0.2 metrics into PR #19 results.

Run #202 (ID `45892529710`) remains recorded as a prior failed attempt: its unit test incorrectly assumed all variants shared identical multiplier expressions. The test was corrected to distinguish the fused Baugh-Wooley implementation from the product-level reduction baselines. Preserve this failure history.

### Corrective work on the PR branch

Latest branch head `fb11b4d` includes:
- Structured OpenSTA parsing for internal, switching, leakage, and total power, retaining raw Watts values and emitting explicit µW fields.
- Fail-closed checks for a parsed OpenSTA total-power row and nonzero VCD pin-activity annotation.
- A fail-closed check for exactly 512 unique deterministic xorshift32 vectors.
- Unit tests for power-component extraction and rejection of missing VCD annotation.
- Unbuffered per-variant progress logs.
- Per-stage timeouts: Yosys SAT 300 s; generic synthesis 120 s; Nangate45 mapping 120 s; Icarus compilation and simulation 60 s each; OpenSTA 120 s.
- Named timeout errors for formal SAT, generic synthesis, Liberty mapping, Icarus compilation, Icarus simulation, and OpenSTA.
- Separate elapsed-time fields for formal SAT, generic synthesis, Liberty mapping, simulation, OpenSTA, and total per-variant runtime.
- Explicit formal method remains Yosys `miter -equiv -flatten` plus `sat -verify -prove trigger 0`. A timeout is surfaced as a named stage timeout; no alternate proof method has been substituted.

### Workflow trigger investigation and current CI state

The original `.github/workflows/ci.yml` listened to `pull_request` for branches targeting `main`, with no explicit event-type list or `workflow_dispatch`. The PR branch workflow was updated to include `opened`, `synchronize`, `reopened`, and `ready_for_review`, plus `workflow_dispatch` and a 90-minute job timeout. The same trigger/timeout/unbuffered-logging changes were committed to `main` in commit `1205f16f8f74c86f82f718ae8c3fe4f848ff8c64`.

PR #19 was marked ready for review, then closed and reopened to emit a `reopened` event. The latest Actions query still showed no new `pull_request` run for the current head, even after the base-branch trigger fix and close/reopen event. Main-branch runs #207 (ID `45939477100`), #208 (ID `45939552147`), #209 (ID `45939583480`), and #210 (ID `45939612718`) all completed `success`. Run #207 validated the updated main workflow trigger/timeout and unbuffered command. Runs #208 and #209 validated the STATUS-only commits; Run #210 validated the workflow change that adds `paths-ignore: STATUS.md`. All these runs tested `main`, not PR #19, and cannot validate the fused candidate.

The available GitHub integration exposes read operations and rerun operations for existing jobs, but no workflow-dispatch action. Do not claim a manual dispatch occurred. The exact reason the PR event did not create a run remains unconfirmed; do not assert a token limitation or disabled Actions without evidence. Main runs #207–#210 all passed; the last, #210, completed at 2026-11-27 04:23:50 UTC. At 2026-11-27 04:32:50 UTC, the PR branch received two non-RTL workflow-file commits to emit a fresh `synchronize` event: `888c8e4aaacf5dc6e54b0e095dd2d53837b1cbc3` added a comment-only retrigger marker; that first write accidentally doubled the shell line-continuation backslashes in the OpenSTA CMake command. This was immediately corrected in `fb11b4dcfabb92e651759259edb953ff8521dbde`, restoring single backslashes; the latest workflow file was fetched and its continuation was checked. The corrected head is `fb11b4d`. The exact-head PR workflow-run query still returned no runs. The GitHub connector available in this session has no workflow-dispatch action and no branch-merge action, so main could not be merged into the PR branch and no manual dispatch was performed. Next: check Actions UI / event delivery for the new `synchronize` event or manually dispatch `ORCUS CI` against `research/orcus-fused-int4-mac` / exact head `fb11b4dcfabb92e651759259edb953ff8521dbde`. If still absent, inspect repository Actions settings and event delivery before changing RTL or proof logic.

### Required PR #19 closure gates

1. Obtain a fresh CI run against the current PR head `fb11b4d` (`fb11b4dcfabb92e651759259edb953ff8521dbde`); record its run ID and exact head SHA.
2. Use unbuffered stage logs to record exact wall-clock times for Yosys SAT, generic synthesis, Nangate45 mapping, Icarus simulation, and OpenSTA for each of the six variants.
3. If fused formal SAT reaches the 300-second timeout, preserve the timeout and solver logs. Investigate the bit-blasted multiplier/bit-heap proof bottleneck; compare an explicitly documented alternative such as partitioned equivalence or ABC `cec` only after validating its exact semantics. Do not silently relabel a timeout as a proof pass.
4. Inspect the uploaded artifact and raw OpenSTA reports for all six variants.
5. Verify Yosys SAT equivalence for all six variants, exactly 512 unique fixed-seed xorshift32 vectors per variant, and nonzero clean VCD pin-activity annotation for every OpenSTA run.
6. Populate the exact comparison table only from the artifact: Variant, Yosys SAT / Proof, Generic cells, Nangate45 area, OpenSTA delay (ns), Internal (µW), Switching (µW), Leakage (µW), Total (µW).
7. Compare fused Baugh-Wooley with direct expression and two-stage carry-save. Record whether it wins or loses on this workload, including trade-offs; do not generalize beyond the measured configuration.
8. Keep PR #19 unmerged until all evidence is reviewed. Merge only with explicit authorization.

### Milestone #2 — scale signed INT4 dot products

After PR #19 has a complete, reviewed four-lane result, generalize to:
- 8 lanes: 11-bit signed accumulator.
- 16 lanes: 12-bit signed accumulator.
- 32 lanes: 13-bit signed accumulator.

For each width, compare direct expression, multi-stage carry-save, and fused Baugh-Wooley multi-lane compression. Require formal equivalence for every candidate, deterministic 512-vector xorshift32 activity, nonzero VCD annotation, raw artifacts, and per-stage timing. Record generic cells, Nangate45 area, OpenSTA delay, internal/switching/leakage/total power, tool versions, constraints, and proof method separately for each lane count. Keep all Nangate45 results labelled as pre-layout research-library estimates without routed parasitics, not silicon PPA. Preserve the v0.2 four-lane baseline as the fixed historical reference.

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


## 7. Session handoff — 2026-11-27 04:33:18 UTC

- Read this `STATUS.md` from `main` before any repository action in this session.
- PR #19 remains open, ready for review, unmerged; latest verified head is `fb11b4dcfabb92e651759259edb953ff8521dbde`.
- Branch update commits: `888c8e4aaacf5dc6e54b0e095dd2d53837b1cbc3` (comment-only CI retrigger marker; its first write accidentally doubled CMake continuation slashes) and `fb11b4dcfabb92e651759259edb953ff8521dbde` (immediate correction restoring the original single-backslash shell continuations). No RTL or benchmark code was intentionally changed by these commits.
- The exact-head PR workflow-run query after the corrected update returned zero runs. A final verification at 2026-11-27 04:33:18 UTC confirmed `STATUS.md` on `main` contains the exact current PR head; PR #19 remains open/unmerged with `mergeable=false`; the workflow file contains the restored single-backslash CMake continuations; and the exact-head run query remains empty. No new CI run ID, stage timings, artifact, SAT outcome, vector count, VCD annotation count, area, delay, or power result is available. PR #19 technical outcome remains NOT DETERMINED.
- The PR's `mergeable` field was `false` at the last metadata read. Do not merge.
- No merge of `main` into the PR branch was performed: the available connector did not expose a branch-merge action. No workflow dispatch was performed: the available connector did not expose a workflow-dispatch action. The `synchronize` event was emitted by the two branch commits above, but no run was visible in the immediate exact-head query.
- Next action: inspect GitHub Actions UI/event delivery for the `synchronize` event or manually dispatch the workflow on the exact branch head. Then inspect run logs/artifact and complete all six-variant evidence gates. Keep Ceres untouched; NEM separate; preserve ORCUS v0.2.


## 8. Session handoff — 2026-11-27T04:37:14Z

- Read this file on `main` before all repository work in this session.
- Current `main` head at diagnostic start: `cae8f177792e4f7380ec8b8394a19032139a77d4`; PR #19 head: `fb11b4dcfabb92e651759259edb953ff8521dbde`.
- PR #19 remains open and unmerged; GitHub reports `mergeable=false`. The exact-head PR-run lookup returned no runs for `fb11b4d`; branch Actions history showed only earlier runs #202 (failed) and #203 (cancelled). No `workflow_dispatch` run was found.
- Compared `main` and PR branch from common merge base `88336a8f5205744ce24efd182a5f683c2fa73373`: `main` is 10 commits ahead of the merge base; the PR branch is 30 commits ahead. The only changed-file blob differences among the PR's changed paths are `.github/workflows/ci.yml`, `benchmarks/signed_int4_dot_product.py`, and `tests/test_signed_int4_dot_product.py`. `STATUS.md` exists on main and not on the PR branch.
- The workflow file on main contains `paths-ignore: STATUS.md`; the PR branch contains the same PR trigger list, manual dispatch trigger, 90-minute job timeout, unbuffered benchmark command, and restored CMake continuations, but lacks the main-only `paths-ignore` and retains a comment-only retrigger marker.
- The main benchmark is the five-variant v0.2 baseline; the PR benchmark is the six-variant extension including `fused_partial_product`, parser checks, and bounded stage timeouts. The PR test file includes fused-candidate and parser tests; do not overwrite either PR file with the older main version.
- The `orcus/*.py` and other shared test files inspected have identical blob SHAs on main and the PR branch. No Ceres paths or content were accessed.
- Diagnosis: mergeability is false and there are overlapping edits in the three files above; GitHub's metadata alone does not establish which hunk(s) are actual conflict markers. Planned resolution is a non-force merge commit using main as first parent, retaining PR-branch benchmark/test blobs and taking main's workflow blob, with all unchanged shared blobs and main's STATUS.md preserved. Then advance the PR branch with a fast-forward update and check whether GitHub reports mergeable true / dispatches synchronize CI. No PR branch mutation has yet been made in this diagnostic batch.
- No new benchmark run, artifact, SAT proof, vector confirmation, VCD annotation, stage timing, or PR #19 PPA result exists. Keep PR #19 unmerged pending evidence and explicit authorization. Preserve ORCUS v0.2 and keep Ceres untouched; NEM remains separate.


## 9. Session handoff — 2026-11-27T04:37:58Z

- PR #19 merge conflict resolution completed without force-pushing. A two-parent merge commit was created with PR head as first parent and the then-current main head as second parent. Merge commit: `29afabf84e82203bd350ed4ca233bde0d3bde2e1`; parents: PR head `fb11b4dcfabb92e651759259edb953ff8521dbde` and main `9a0f98563e01d1ee5de472cc9c7cbd72b2f2f37e`. The branch ref was advanced with expected-head protection and non-force update.
- The merge tree retained main's `.github/workflows/ci.yml` (including `paths-ignore: STATUS.md`), retained the PR branch's six-variant benchmark blob `a71b58bde71defc46a39dcc0666be8e55fba359b` and fused/parser test blob `b07462705ccd2f898dd123d0b7ffabc01387da8c`, and retained main's `STATUS.md`. Other common ORCUS source/test blobs were identical on both sides.
- GitHub now reports PR #19 `mergeable=true`, open, unmerged, with base SHA `9a0f98563e01d1ee5de472cc9c7cbd72b2f2f37e` and head SHA `29afabf84e82203bd350ed4ca233bde0d3bde2e1`. The PR diff now contains only the two intended benchmark/test files; the workflow diff is resolved.
- Automatic `pull_request` synchronize CI started: Run #211, ID `45941055820`, exact head `29afabf84e82203bd350ed4ca233bde0d3bde2e1`, created at 2026-11-27 04:37:44 UTC. At this handoff it is `in_progress`; no artifact or stage results have yet been confirmed. This is an automatic PR run, not a workflow_dispatch run.
- Exact next action: inspect Run #211 jobs/step timings and logs while it runs; after completion inspect the artifact and verify all six variants' SAT proof, 512 unique vectors, nonzero VCD annotation, and all four OpenSTA power components. Record only artifact-backed metrics. Keep PR #19 unmerged until review and explicit authorization. Ceres remains untouched; NEM remains separate; ORCUS v0.2 remains the fixed verified baseline.


## 10. CI progress — 2026-11-27T04:38:13Z

- Run #211 / ID `45941055820` remains `in_progress` on exact PR head `29afabf84e82203bd350ed4ca233bde0d3bde2e1` (started 2026-11-27 04:37:44 UTC).
- Job `test` ID `140315208458` is running. Set up job, checkout, and Python setup completed successfully. Dependency installation was still `in_progress` at the latest step query; cache, CUDD/OpenSTA build, unit tests, compile, Liberty fetch, benchmark, artifact upload, and smoke verification had not yet started. Artifact list was empty at this point.
- Workflow job-log download was attempted but GitHub returned BlobNotFound while the job was still running; no stage log/timing is available from that request. This is a log-availability limitation, not a benchmark failure.
- Next: poll Run #211, retrieve job logs after completion, inspect uploaded artifact, and record exact per-stage results. Do not infer benchmark outcome from setup progress.


## 11. CI progress — 2026-11-27T04:38:22Z

- Run #211 / ID `45941055820` is still `in_progress` on head `29afabf84e82203bd350ed4ca233bde0d3bde2e1`.
- Completed successfully: dependency installation; EDA cache lookup; cached OpenSTA verification; unit tests; Python compile; Nangate45 Liberty download. CUDD and OpenSTA build steps were skipped because the pinned build cache hit.
- Benchmark step `Run signed INT4 dot-product reduction benchmark` (step 12) is currently `in_progress`. Artifact upload and benchmark smoke verification remain pending. No SAT outcome, per-variant stage timing, benchmark artifact, vector/VCD confirmation, or PPA metric is available yet.
- Next: continue polling Run #211; inspect job logs and artifact once available. Do not call the running benchmark a pass.


## 12. CI progress — 2026-11-27T04:38:37Z

- Latest Run #211 poll: run `45941055820` remains `in_progress`; job `140315208458` remains active in benchmark step 12, `Run signed INT4 dot-product reduction benchmark`. Steps 1–11 are successful or cache-skipped as recorded above. Steps 13–14 (artifact upload and smoke verification) remain pending.
- Repeated job-log retrieval still returns GitHub `BlobNotFound` while the job is running. No per-variant logs or stage timings can yet be inspected. Artifact listing remains empty while the benchmark is active.
- No formal proof result, 512-vector count, VCD pin annotation, generic-cell count, Nangate45 area, delay, or power result is available at this timestamp. The run is neither a pass nor a failure yet.
- Next: wait for Run #211 completion, then retrieve the completed job logs and artifact; if and only if fused SAT times out at its configured 300-second limit, investigate the exact solver logs and implement a separately documented structural-equivalence strategy. Keep PR #19 open/unmerged pending verified results and explicit authorization.


## 13. CI poll — 2026-11-27T04:38:47Z

- Rechecked Run #211 / `45941055820`: still `in_progress`, exact head `29afabf84e82203bd350ed4ca233bde0d3bde2e1`. Benchmark step 12 remains active; steps 13–14 remain pending; no artifact is published yet. No stage timings or six-variant measurements are available. This poll does not change the technical conclusion: PR #19 benchmark remains pending / NOT DETERMINED.
- Next: retrieve completed logs and artifact after run completion; keep PR #19 open and unmerged until the evidence gates are reviewed.


## 14. Run #211 inspection — 2026-11-27T04:41:51Z

- Inspected workflow run #211 / ID `45941055820` again. It is still `in_progress` on exact head `29afabf84e82203bd350ed4ca233bde0d3bde2e1`; job `140315208458` remains in progress at benchmark step 12, `Run signed INT4 dot-product reduction benchmark`. Steps 1–11 are completed successfully or skipped on cache hit; steps 13–14 remain pending.
- Artifact list is still empty. No completed job logs or stage timing report are available. No SAT proof results, vector uniqueness results, VCD activity counts, generic cells, Nangate45 area, delay, or power metrics can be verified yet. Run #211 outcome remains pending, not pass/fail.
- PR #19 remains open and unmerged. A fresh PR metadata read currently reports `mergeable=false` despite the merge commit having previously reported `true`; this status may be recalculating or may reflect the base moving as STATUS commits are added. Do not assume it is mergeable until rechecked after CI completes. The exact PR head remains `29afabf84e82203bd350ed4ca233bde0d3bde2e1`.
- No code or PR branch changes were made during this inspection. No solver fix was applied because no SAT timeout/failure has been observed. No Milestone #1 closure or Milestone #2 scaling work is authorized by the available evidence yet.
- Next: poll Run #211 and PR mergeability. After run completion, retrieve logs and artifact, validate all six variants, and only then decide whether a proof-method change is needed. Keep PR #19 open/unmerged pending evidence and explicit authorization. Ceres remains untouched; NEM separate; ORCUS v0.2 fixed baseline intact.


## 15. Run #211 poll — 2026-11-27T04:42:04Z

- Second poll after the previous handoff confirms Run #211 `45941055820` is still `in_progress` on head `29afabf84e82203bd350ed4ca233bde0d3bde2e1`. Benchmark step 12 remains active; artifact upload and benchmark-target verification remain pending. Artifact list remains empty.
- PR #19 remains open/unmerged; metadata still reports `mergeable=false` at this poll. Base SHA is `9a0f98563e01d1ee5de472cc9c7cbd72b2f2f37e`; head SHA is unchanged. Do not merge or assume mergeability.
- No benchmark outcome, stage timings, artifact, formal proof result, vector/VCD evidence, or PPA metrics have been produced in the observed responses. Exact next action: continue polling until the run completes, then retrieve completed logs and artifact. If the run fails, identify the precise failing step and log before deciding on a repair. Milestone #1 remains open; do not begin 8/16/32-lane implementation before four-lane evidence is closed.


## 16. Run #211 final audit — 2026-11-27T04:43:23Z

- Run #211 / ID `45941055820` completed with conclusion `failure` at 2026-11-27T04:43:23Z. It was an automatic `pull_request` run on PR #19, merge ref commit `7a57c217eb94470a7d5b0af59530c12fdcc3494a`, representing PR head `29afabf84e82203bd350ed4ca233bde0d3bde2e1` merged with base `9a0f98563e01d1ee5de472cc9c7cbd72b2f2f37e`. Job ID: `140315208458`.
- Setup, checkout, Python, dependencies, cached OpenSTA verification, unit tests, Python compilation, and Nangate45 Liberty download all completed successfully. All 63 unit tests passed in 0.946 seconds.
- Benchmark step 12 failed; artifact upload (step 13) and benchmark-target verification (step 14) were skipped. Artifact query returned an empty list. No benchmark JSON artifact or complete raw OpenSTA reports were produced.
- Exact failure: fused candidate `orcus_fused_partial_product` entered Yosys formal SAT at 2026-11-27T04:38:15.3939954Z and exceeded the configured 300-second timeout. Python reported `subprocess.TimeoutExpired` at 2026-11-27T04:43:15.5119878Z and raised `FORMAL_TIMEOUT` with elapsed `300.10s`. Exact proof command: `read_verilog candidate.v reference.v; proc; miter -equiv -flatten reference orcus_fused_partial_product m; sat -verify -prove trigger 0 m`. This is a solver timeout, not a counterexample and not a proof pass.
- The first five variants completed all stages. Log-recorded formal / generic synthesis / Nangate45 mapping / simulation durations were:
  - direct: 0.03 / 0.14 / 0.32 / 0.04 s; complete 0.69 s; 512 unique vectors; 259 annotated pins; 522 generic cells; area 574.56; delay 0.95 ns; total power 105.0206 µW.
  - left_deep: 0.03 / 0.14 / 0.31 / 0.04 s; complete 0.66 s; 512 unique vectors; 259 annotated pins; 522 generic cells; area 574.56; delay 0.95 ns; total power 105.0206 µW.
  - balanced_01_23: 0.04 / 0.15 / 0.31 / 0.04 s; complete 0.67 s; 512 unique vectors; 259 annotated pins; 522 generic cells; area 575.89; delay 1.00 ns; total power 104.8923 µW.
  - balanced_02_13: 0.11 / 0.15 / 0.30 / 0.04 s; complete 0.73 s; 512 unique vectors; 259 annotated pins; 522 generic cells; area 574.56; delay 1.00 ns; total power 104.9567 µW.
  - carry_save: 0.07 / 0.15 / 0.28 / 0.04 s; complete 0.67 s; 512 unique vectors; 268 annotated pins; 441 generic cells; area 460.712; delay 0.89 ns; total power 84.60975 µW.
- The first five Run #211 measurements match the previously verified v0.2 values. This run's job log exposes total power, not the four individual power components in a saved artifact; do not claim the Run #211 artifact independently verified internal/switching/leakage values. The fused candidate has no synthesis, simulation, OpenSTA, or PPA measurements because it timed out before those stages.
- Result: **fused Baugh-Wooley win/loss is NOT DETERMINED**. It cannot be compared against carry-save from this run. No six-variant table can honestly be completed. Do not close Milestone #1 or begin Milestone #2.
- PR #19 remains open and unmerged. Current metadata reports `mergeable=false`; base SHA `9a0f98563e01d1ee5de472cc9c7cbd72b2f2f37e`, head SHA `29afabf84e82203bd350ed4ca233bde0d3bde2e1`. No branch code change, solver substitution, PR merge, or milestone closure was made during this audit.
- Next engineering action: design and validate a proof decomposition for the fused arithmetic, preserving the current SAT timeout and failure history. Candidate approaches to evaluate include equivalence partitioning with independently justified cutpoints, Yosys `equiv_*` passes where structural correspondence exists, or ABC `cec`; do not assume any is equivalent or fast without running it on the exact generated RTL. Keep the original Yosys miter/SAT proof as a recorded baseline. Any alternative must prove the full 10-bit output against the direct signed-INT4 reference, not merely prove isolated compressor equations or a subset of lanes. Run a fresh CI after a verified proof implementation.
- Research limits remain unchanged: Nangate45 estimates are pre-layout and have no routed parasitics; they are not silicon PPA. Preserve ORCUS v0.2 as fixed baseline. Keep Ceres untouched and NEM separate.


## 17. STATUS write verification — 2026-11-27T04:43:40Z

- Verified the Run #211 audit entry is present on `main`; current STATUS.md blob SHA is `ccf9dafef36d21186a85daa55ec39edf5fd54de2`, written by commit `7a9a0f9e2ef578bcf75165a654dd69c8137cf9d4`.
- Rechecked PR #19 after the STATUS update: it remains open, unmerged, and `mergeable=false`; base `9a0f98563e01d1ee5de472cc9c7cbd72b2f2f37e`, head `29afabf84e82203bd350ed4ca233bde0d3bde2e1`. Do not merge or close Milestone #1.
- No additional benchmark or proof attempt was performed in this verification.


## 18. Formal proof implementation attempt — 2026-11-27T04:45:00Z

- On PR #19 branch `research/orcus-fused-int4-mac`, commit `53e8887f9df4cd30326be036d2ea606eaa9daa40` changes the formal gate in `benchmarks/signed_int4_dot_product.py` from the monolithic `miter -equiv -flatten; sat -verify -prove trigger 0` command to a Yosys partitioned equivalence sequence:
  `read_verilog reference candidate; proc; equiv_make reference candidate equiv; hierarchy -top equiv; clean -purge; equiv_struct -icells; equiv_simple -v; equiv_status -assert`.
- New helper `_run_equivalence` uses the fail-closed `equiv_status -assert`, returns explicit method and elapsed proof time, and raises on command failure or timeout. The 300-second formal timeout remains the outer cap. This sequence is an implementation under test, not yet a verified proof result.
- The next required change is the negative one-bit output-tamper unit test. After that, run unit tests and CI. Do not claim full equivalence or a fused PPA result until the actual run proves it.
- PR #19 branch head is now `53e8887f9df4cd30326be036d2ea606eaa9daa40`. Main STATUS update commit will be recorded after this write.
- Milestone #1 remains open. Milestone #2 (8/16/32 lanes) is blocked pending complete four-lane proof and benchmark evidence. Ceres remains untouched; NEM remains separate.


## 19. Negative equivalence test added — 2026-11-27T04:46:00Z

- PR #19 branch `research/orcus-fused-int4-mac` now includes commit `4777754c2410e0250568e2c7d2efd2e4d552f13b`, adding a unit test that runs the new partitioned Yosys equivalence flow on the fused candidate and then repeats it on an intentionally corrupted candidate whose final 10-bit result is XORed with `10'b0000000001`.
- The test requires the correct candidate to prove and requires the one-bit-tampered candidate to raise an equivalence failure. This is the requested negative test; it has been committed but has NOT yet executed in CI.
- Test timeout is 60 seconds per proof invocation. Full output equivalence remains the intended formal gate; no 2^32 exhaustive simulation is attempted.
- Current PR branch head: `4777754c2410e0250568e2c7d2efd2e4d552f13b`. No CI result is yet confirmed. Next: run/review unit tests and inspect the new proof command's behavior, including that the negative test rejects the tampered output.
- Milestone #1 remains open; no PPA comparison for fused Baugh-Wooley is available. Ceres untouched; NEM separate.


## 20. PR branch STATUS synchronization — 2026-11-27T04:50:10Z

- Copied the exact current `main:STATUS.md` content (blob `18da1cc406d18491bd483639dda10c6c18aa73b2`) onto `research/orcus-fused-int4-mac`. Branch sync commit: `ccc409f8b76cad0d088b589d7834f9b017dc77a6`. This preserves the complete audit history and makes the branch's STATUS file content identical to main at the time of sync.
- PR #19 now points to head `ccc409f8b76cad0d088b589d7834f9b017dc77a6`; GitHub metadata still reports `mergeable=false` (may be recalculating; not yet resolved). Base ref is main. PR remains open/unmerged.
- `fetch_commit_workflow_runs` for this new head returned no PR-triggered run at the time checked. No CI run ID is confirmed yet. Do not claim the workflow was triggered.
- Next: inspect PR mergeability and Actions run list for the exact head. If no run starts, diagnose the base/head divergence and resolve it with a non-force merge commit, preserving PR code and current main STATUS. Do not merge PR #19 into main.
- Proof implementation and one-bit negative test are committed on the PR branch but remain unexecuted. No proof or PPA claim is made. Milestone #1 remains open; Milestone #2 blocked. Ceres untouched; NEM separate.


## 21. GitHub Actions query limitation — 2026-11-27T04:50:30Z

- Attempted to query the Actions runs collection with a `head_sha` query parameter; the GitHub connector rejected that URL as unsupported (HTTP 400). No run data was retrieved by that request. This is a connector endpoint limitation, not evidence that GitHub Actions itself failed.
- No code or branch refs were changed by this failed diagnostic. PR #19 remains open/unmerged; proof implementation and negative test remain unexecuted.
- Next: use the supported workflow-run lookup by commit SHA and PR metadata/compare endpoints, then update this status with the exact run or mergeability diagnosis.


## 22. PR mergeability metadata diagnostic — 2026-11-27T04:51:00Z

- Direct pull-request API read reports `mergeable=null` and `mergeable_state=unknown` while GitHub recalculates; the simplified PR wrapper had previously reported `mergeable=false`. Treat mergeability as UNKNOWN, not confirmed false or true.
- Current main head is `878f2cd2a40071742e97d27c19e2c3e95cf7b00f`; PR branch head is `ccc409f8b76cad0d088b589d7834f9b017dc77a6`. The PR's reported base SHA remains `9a0f98563e01d1ee5de472cc9c7cbd72b2f2f37e`, so the PR branch does not yet contain the latest main commit ancestry.
- The current branch STATUS content predates main's latest audit entries. Next: synchronize the latest STATUS content and create a non-force two-parent merge commit with current main as a parent, preserving the PR branch's benchmark/tests and the main STATUS file. This is branch synchronization only, not merging PR #19 into main.
- No CI run is confirmed yet. Ceres remains untouched; NEM separate.


## 23. Branch STATUS refresh — 2026-11-27T04:52:00Z

- Refreshed `research/orcus-fused-int4-mac:STATUS.md` to the latest main audit content. Branch sync commit: `8d03410c25779dbff32ac000e5d0871f6b342929`; resulting STATUS blob `c81cb607f35fa229155bd0b3c43ede75f271d590`.
- This is a content refresh only; it does not yet establish main ancestry. Next: create a non-force two-parent branch synchronization commit using the current main head as a parent and the PR branch tree, with main's latest STATUS blob incorporated. Then recheck mergeability and workflow dispatch.
- No CI run or proof result yet. PR #19 remains open/unmerged; Milestone #1 remains open.


## 24. Non-force main synchronization merge — 2026-11-27T04:53:00Z

- Advanced `research/orcus-fused-int4-mac` with a non-force two-parent merge commit `b25d9ba616e4e2b5e87ddda2bffeba4e8547ea9d`. Parents: previous PR branch head `8d03410c25779dbff32ac000e5d0871f6b342929` and current main head `d0767836cf95ace97e7789909a93a3108dedcfb6`. The merge tree preserves the PR branch's code/tests and includes the exact main STATUS blob `4f666fdb90af1cd8b1bd54eedd137f6e05e71f9e`.
- Branch ref update succeeded with expected-head protection and `force=false`; no force-push occurred. This is a merge of main into the experiment branch only. PR #19 has NOT been merged into main.
- Next: poll PR mergeability and Actions for the new branch head `b25d9ba616e4e2b5e87ddda2bffeba4e8547ea9d`. No new run or test result is confirmed yet. The proof flow and negative tamper test remain pending execution.


## 25. PR #19 CI Run #216 started — 2026-11-27T04:54:00Z

- New automatic `pull_request` workflow Run #216: ID `45942353836`, run URL `https://github.com/bio-ctrl/EGS/actions/runs/45942353836`, exact head `b25d9ba616e4e2b5e87ddda2bffeba4e8547ea9d`, branch `research/orcus-fused-int4-mac`, created/started at `2026-11-27T04:51:28Z`. It is currently `in_progress`.
- The run was triggered by the non-force branch synchronization merge commit `b25d9ba616e4e2b5e87ddda2bffeba4e8547ea9d`; the run's base SHA is `d0767836cf95ace97e7789909a93a3108dedcfb6`. This confirms the PR synchronize workflow has fired.
- PR #19 remains open and unmerged. Simplified metadata still reports `mergeable=false`, but direct API reported `mergeable=null` / `mergeable_state=unknown` while recalculating; do not treat this as a confirmed merge conflict or a clean merge.
- Run #216 has no verified completion, job-stage outcome, artifact, proof result, or PPA measurements yet. Next: poll run/jobs; after completion inspect logs and artifact, including the new positive/negative formal unit test. No solver proof pass or fused performance claim is made.
- Main status was updated on main only; PR branch code and NEM/Ceres boundaries remain unchanged. Milestone #1 remains open; Milestone #2 (8/16/32 lanes) remains blocked pending complete four-lane evidence.


## 26. Run #216 early poll and code-path review — 2026-11-27T04:55:00Z

- Run #216 `45942353836` remains `in_progress` on head `b25d9ba616e4e2b5e87ddda2bffeba4e8547ea9d`. Job `140319281323` has completed setup, checkout, and Python setup; dependency installation is in progress. Unit tests, formal proof, benchmark, and artifact upload have not started. Artifact list is empty.
- Reviewed the committed proof helper and its integration into `_run_yosys`: proof result/method/log are carried into each variant result; synthesis and mapping still execute only after formal proof returns. No obvious stale `proof.stdout` references remain in the returned result assembly.
- This is a source review only, not execution of the new proof. The 60-second positive/negative unit-test timeout and 300-second benchmark proof timeout are still unvalidated.
- Next: poll Run #216. If unit tests fail, inspect the exact Yosys command/output and correct the proof/test implementation on the PR branch; do not claim equivalence or fused PPA until both the positive and tamper-negative checks pass.
- PR #19 remains open/unmerged. No new stage timings or six-variant data yet. Milestone #1 remains open; Milestone #2 remains blocked. Ceres untouched; NEM separate.


## 27. Run #216 unit-test stage — 2026-11-27T04:56:00Z

- Run #216 / `45942353836` remains `in_progress`; job `140319281323` is now executing step 9, `Run unit tests`.
- Steps 1–5 and 8 completed successfully; CUDD/OpenSTA source-build steps 6–7 were skipped on cache hit. Python compile, Liberty fetch, benchmark, artifact upload, and smoke verification remain pending.
- No unit-test result has been returned yet; no formal proof result, benchmark metrics, or artifact exists at this poll. Next: retrieve job logs after unit tests/benchmark progress or completion. No code change made during this poll.


## 28. Run #216 unit-test poll — 2026-11-27T04:56:30Z

- Second poll confirms Run #216 remains `in_progress`, with unit-test step 9 still active. Steps 1–8 remain successful/cache-skipped; steps 10–14 are pending. No artifact is published.
- The new formal unit test performs two separate equivalence attempts (correct fused RTL and a one-bit-tampered copy), each capped at 60 seconds. The live step status does not expose which invocation is running or its result. Do not infer success or timeout until logs are available.
- No code changes or new benchmark evidence from this poll. Next: wait for step 9 to finish, then inspect the exact unit-test log before interpreting the benchmark.


## 29. Run #216 live-log retrieval limitation — 2026-11-27T04:57:00Z

- Attempted to retrieve job `140319281323` logs while Run #216 is still executing. GitHub returned `BlobNotFound` (404) at `2026-11-27T04:52:32.2531857Z`. As in Run #211, this indicates the log bundle is not yet available through the endpoint; it is not a test failure.
- Run #216 remains last observed `in_progress` at unit-test step 9. No test output, formal result, artifact, or benchmark metrics are yet available.
- Next: poll step 9 and fetch logs again only after job/run completion. Do not change proof code based on this unavailable log response.


## 30. Run #216 continued poll — 2026-11-27T04:58:00Z

- Latest run/job/artifact poll: Run #216 `45942353836` remains `in_progress`; job `140319281323` remains at unit-test step 9. The API's run `updated_at` has not advanced from `04:51:32Z`; artifact list is still empty.
- No test outcome can be established while the step remains active and its log bundle is unavailable. The positive proof may be consuming its 60-second cap or the unit test process may be stalled; this is not yet distinguishable from step status alone.
- No proof pass, negative-test rejection, benchmark completion, or fused PPA numbers are verified. Next: wait for the job to transition, then inspect the completed logs and any artifact. Preserve the current proof implementation until the exact result is known.


## 31. Run #216 still at unit-test stage — 2026-11-27T04:58:30Z

- Run `45942353836` remains in progress. Job `140319281323` remains at step 9 (unit tests); steps 10–14 have not started. Artifact list remains empty.
- This repeated poll provides no new test output. The proof test may still be within its configured 60-second timeout, but the job API does not expose subprocess-level progress. Do not call it a pass or a timeout without the log/conclusion.
- Next: wait for the job state transition; after completion retrieve logs and artifact. No code changes in this poll.
