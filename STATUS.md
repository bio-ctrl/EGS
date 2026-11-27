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


## 32. Run #216 completed — unit-test failure — 2026-11-27T04:59:00Z

- Run #216 / ID `45942353836` completed with conclusion `failure`; job `140319281323` failed at step 9, `Run unit tests`. Steps 1–8 succeeded or were cache-skipped. Steps 10–14 were skipped, so no benchmark ran and no artifact was uploaded.
- Direct pull-request API still reports mergeability as `unknown` while recalculating; PR #19 remains open/unmerged. Head remains `b25d9ba616e4e2b5e87ddda2bffeba4e8547ea9d`.
- Exact unit-test failure is not yet known; next retrieve completed job logs and identify whether the positive proof timed out, the Yosys command was unsupported, or the negative test behavior was wrong. Do not alter proof code until logs are inspected.
- No six-variant results, fused PPA, or formal proof pass are available. Milestone #1 remains open; Milestone #2 blocked.


## 33. Run #216 exact formal unit-test failure — 2026-11-27T04:59:30Z

- Retrieved completed job logs for Run #216 `45942353836`, job `140319281323`. The test suite ran 64 tests; 63 passed and the new fused equivalence test errored.
- Exact failure: the positive fused candidate proof timed out after `60.06s` in `_run_equivalence`. The invoked Yosys sequence was:
  `read_verilog reference.v candidate.v; proc; equiv_make reference orcus_fused_partial_product equiv; hierarchy -top equiv; clean -purge; equiv_struct -icells; equiv_simple -v; equiv_status -assert`.
- Exception: `FORMAL_EQUIV_TIMEOUT: Yosys partitioned equivalence exceeded 60s for orcus_fused_partial_product`. The negative tamper subtest was never reached. The new partitioned full-output check therefore does NOT solve the proof wall; no false pass occurred.
- Benchmark step 12 and artifact upload were skipped. No new fused metrics or six-variant table exist. This confirms that simply replacing the monolithic miter with output-bit partitioning is insufficient.
- Next engineering step: decompose the proof compositionally. Independently prove the 4x4 signed Baugh-Wooley product identity (8-bit result) for one lane; then prove the shared 10-bit compressor heap against the sum of symbolic weighted partial-product inputs (no multipliers in that second proof). The composition of those lemmas must imply the complete 10-bit four-lane result. The negative tamper test must target the heap-level proof and be rejected. Keep the original failed attempts recorded.
- PR #19 remains open/unmerged; branch head at the failed run is `b25d9ba616e4e2b5e87ddda2bffeba4e8547ea9d`. Milestone #1 remains open; Milestone #2 blocked. Ceres untouched; NEM separate.


## 34. Compositional proof decomposition implemented — 2026-11-27T04:56:20Z

- After Run #216 showed that output-bit partitioning still timed out at 60.06s, the PR branch was updated with a compositional proof design:
  1. A standalone 4x4 signed Baugh-Wooley lane module (8-bit output) is formally checked against signed multiplication.
  2. A separate 10-bit heap module takes all 64 partial-product bits as unconstrained symbolic inputs. Its compressor network is formally checked against the arithmetic sum of those weighted inputs plus four `10'h390` lane corrections. This second lemma contains no multipliers.
  3. The two lemmas compose: each lane's Baugh-Wooley expansion equals its signed product, and the shared heap equals the sum of all lane expansions, covering the original 32 operand bits and complete 10-bit result.
- The heap proof generator reuses the exact `_fused_partial_product_lines(external_inputs=True)` compressor-generation function used by the fused RTL, preventing a separately hand-coded compressor from drifting from the implementation.
- The negative control now inverts only output bit 0 in the heap implementation and requires the heap equivalence proof to reject it.
- Python-side arithmetic cross-check enumerated all 256 pairs of 4-bit operands and confirmed the Baugh-Wooley 8-bit correction constant `8'h90` matches signed multiplication. This is a secondary local arithmetic check; formal equivalence remains the primary proof gate.
- PR branch code commits: `031ca7fd378c2650cf5c4acb3add4db0eefc4abd` (lane/heap proof generators), `cb7494267f20566b55821538874ff337b072d2e4` (route fused candidate through compositional proof), `408324aed545acc65a25a0ee6a6640a150c3b3d0` (positive proof + one-bit negative test).
- These changes have not yet run in CI. The prior Run #216 remains failed at unit tests; no proof pass or PPA data is claimed. Next: synchronize the latest main STATUS and ancestry to the branch, trigger a new PR CI run, inspect both positive lemmas and the negative tamper result, then benchmark only if all formal tests pass.
- Milestone #1 remains open; Milestone #2 blocked. Ceres untouched; NEM separate.


## 35. PR proof branch synchronized for next CI — 2026-11-27T04:56:42Z

- Synchronized latest main ancestry and STATUS into `research/orcus-fused-int4-mac` with non-force two-parent merge commit `e646fb171fffcba9483c98108f168f7da851cf3a`.
- Parents: prior PR branch head `408324aed545acc65a25a0ee6a6640a150c3b3d0` and main head `d98c691836252141230c66a2ebb1b2df823798da`. Merge tree `2f40a87a9779fda6247aad947a1dcffa47ce3966` includes main's current STATUS blob and preserves the PR branch proof code/tests.
- Branch ref advanced with `force=false` and expected-head check. No PR merge. New branch head: `e646fb171fffcba9483c98108f168f7da851cf3a`.
- Next: verify a fresh automatic PR CI run for this exact head; monitor unit tests first. Do not claim Run #216's failed proof is repaired until the new positive/negative tests pass.


## 36. New compositional-proof CI Run #220 started — 2026-11-27T04:56:54Z

- Fresh automatic PR run confirmed for compositional proof branch head `e646fb171fffcba9483c98108f168f7da851cf3a`: Run #220, ID `45942838109`, event `pull_request`, status `in_progress`, created `2026-11-27T04:56:39Z`.
- PR #19 remains open/unmerged. Direct API reports mergeability `null` / state `unknown` during recalculation; do not infer clean/conflicting state.
- Next: inspect Run #220 job step progress and completed logs. The expected gate is the positive lane lemma, positive symbolic heap lemma, and negative one-bit tamper rejection. Benchmark only runs if the unit-test suite passes.
- No proof pass, fused PPA result, or Milestone #1 closure yet. Milestone #2 (8/16/32 lanes) remains blocked. Ceres untouched; NEM separate.


## 37. Run #220 early progress — 2026-11-27T04:57:04Z

- Run #220 `45942838109`, exact branch head `e646fb171fffcba9483c98108f168f7da851cf3a`, remains `in_progress`. Job `140320786399` has setup/checkout/Python setup completed; apt dependency installation is active. Formal tests and benchmark have not started; no artifact.
- Next: continue polling until the unit-test stage completes; inspect the proof log and negative tamper result before interpreting any benchmark. No proof or PPA result yet.


## 38. Run #220 setup poll — 2026-11-27T04:57:13Z

- Run #220 remains in progress; dependency installation step 4 is still active. Formal tests and benchmark remain pending. No artifacts or metrics.
- No code or workflow changes in this poll. Continue monitoring exact job state; do not infer a proof outcome from setup duration.


## 39. Run #220 failed at unit tests — 2026-11-27T04:57:22Z

- Run #220 `45942838109` has failed at step 9 (`Run unit tests`) after setup and cached OpenSTA verification succeeded. Benchmark and artifact steps were skipped. Job `140320786399`.
- Exact test failure is not yet inspected; fetch completed job logs next. No proof pass, benchmark run, or artifact exists from this run.


## 40. Run #220 heap-lemma failure diagnosis — 2026-11-27T04:57:43Z

- Retrieved completed Run #220 job logs. The new compositional test ran 64 tests in 2.863s; 63 passed and the fused compositional test errored during the symbolic heap lemma.
- Important positive result: the standalone 4x4 signed Baugh-Wooley lane lemma completed successfully; the test advanced into `_run_equivalence` for `orcus_heap_gate`. Thus the lane-level multiplier identity did prove under the partitioned Yosys flow.
- Exact heap failure: `equiv_status -assert` reported `ERROR: Found 37 unproven $equiv cells in 'equiv_status -assert'`. Log shows `equiv_struct -icells` created invalid/unhelpful internal structural matches between the arithmetic reference and compressor gate (e.g. reference add outputs matched to internal `fa_s_*` / `fa_c_*` / PP nodes). This is a structural-partitioning problem, not a demonstrated output counterexample and not a timeout.
- Run #220 benchmark, artifact upload, and smoke verification were skipped. No fused PPA metrics.
- Next: disable `equiv_struct` only for the symbolic heap proof so the tool proves the 10-bit outputs directly with `equiv_simple`, while retaining the successful lane lemma. Run the negative one-bit tamper check with the same output-only heap proof. If output-only SAT does not prove quickly, inspect proof partitions/logs before changing strategy.
- PR #19 remains open/unmerged. Milestone #1 remains open; Milestone #2 blocked. Ceres untouched; NEM separate.


## 41. Heap proof matching refinement — 2026-11-27T04:58:21Z

- PR branch head advanced through `2555c279c270dd1eba9e163dcb5bb41aec98dc08` and `92cc4ea77d066d5576e747ece5b36ef96308c128` to disable `equiv_struct -icells` for the symbolic heap lemma and the negative tamper proof. The lane multiplier lemma retains structural matching because it passed in Run #220.
- Reason: Run #220's heap proof produced 37 unproven equivalence cells after `equiv_struct` made unsuitable internal matches between the arithmetic sum and compressor network. The heap should be compared at its complete 10-bit output only; `equiv_simple -v; equiv_status -assert` is now used there.
- Commit `0fd9465315675ce7042486d01a789c127b3138c0` clarifies the distinct proof sequence in the recorded proof-method string.
- This is a diagnostic refinement only. No CI has yet tested this output-only heap proof. Run #220 remains failed; no benchmark artifact or fused PPA data.
- Next: sync latest main STATUS/ancestry to the PR branch with a non-force merge commit, trigger a fresh run, and inspect the heap proof. Do not assert success until the negative tamper is rejected.


## 42. Heap proof refinement synchronized to PR branch — 2026-11-27T04:58:42Z

- Advanced `research/orcus-fused-int4-mac` to non-force two-parent merge commit `6f9c13eb45bb812eee523a1ea53cc02a01651bd9`.
- Parents: previous PR head `0fd9465315675ce7042486d01a789c127b3138c0` and main head `e54958cbcce4e94ec453383bcfcf64df82a41c7d`. Merge tree `3f6f65e6f61ab29ea2b02f54822d16fc8e1aa967` includes current main STATUS blob and preserves the output-only heap proof change and negative test.
- Branch ref update succeeded with `force=false` and expected-head protection. This is a main-to-PR-branch sync, not a PR merge.
- Next: confirm new automatic PR CI run for head `6f9c13eb45bb812eee523a1ea53cc02a01651bd9`; then inspect whether output-only heap equivalence proves and the tampered output is rejected.


## 43. PR #19 CI Run #224 started — 2026-11-27T04:58:52Z

- Automatic PR Run #224 confirmed: ID `45943017177`, branch head `6f9c13eb45bb812eee523a1ea53cc02a01651bd9`, event `pull_request`, currently `in_progress`.
- PR #19 remains open/unmerged; direct GitHub API reports mergeability `unknown` during recalculation. Base SHA `e54958cbcce4e94ec453383bcfcf64df82a41c7d`.
- Next: monitor Run #224 unit tests and benchmark. Required evidence: lane lemma pass, output-only symbolic heap lemma pass, negative one-bit tamper rejection, then all six variants' formal proof, 512 unique vectors, VCD pin activity, and all four power components.
- No new proof or PPA result yet; Milestone #1 open and Milestone #2 blocked. Ceres untouched; NEM separate.


## 44. Run #224 setup progress — 2026-11-27T04:59:01Z

- Run #224 `45943017177` remains `in_progress` on exact head `6f9c13eb45bb812eee523a1ea53cc02a01651bd9`. Job `140321357589`: setup, checkout, and Python setup passed; apt dependency installation is active. Unit tests and benchmark have not started; no artifact.
- Next: poll the unit-test stage and inspect logs once available. No proof pass or PPA result yet.


## 45. Run #224 cache progress — 2026-11-27T04:59:10Z

- Run #224 remains `in_progress`; apt dependencies succeeded and step 5 (pinned CUDD/OpenSTA cache restore) is active. Unit tests and benchmark remain pending; no artifact.
- No new proof outcome or metrics. Continue monitoring; inspect the formal stage only after it starts/completes.


## 46. Run #224 unit tests started — 2026-11-27T04:59:18Z

- Run #224 setup and cached OpenSTA verification passed; unit-test step 9 is now in progress. Benchmark, artifact, and smoke steps remain pending.
- The new proof sequence under test is: signed 4x4 Baugh-Wooley lane lemma with structural matching; 10-bit symbolic heap lemma with structural matching disabled; one-bit output tamper must fail the same output-only heap proof.
- No test result is available yet. Next: wait for step 9 completion and inspect logs before treating the proof as successful.


## 47. Run #224 unit-test poll — 2026-11-27T04:59:27Z

- Run #224 remains in progress at unit-test step 9. All setup/cache steps passed; benchmark and artifact steps remain pending.
- No unit-test log or subprocess-level proof stage is available from the step summary. The symbolic heap proof may still be running within its 60-second test timeout. No pass/failure inference yet.
- Next: poll for step transition and retrieve logs after completion. No code changes in this poll.


## 48. Run #224 continued formal test poll — 2026-11-27T04:59:36Z

- Run #224 is still `in_progress` at step 9. No test result or artifact is published.
- The configured 60-second per-proof timeout has not yet been confirmed as reached from the available step summary. Do not treat elapsed wall time or an unchanged step as a formal timeout without the job log.
- Next: retrieve completed job logs once step 9 exits; if the output-only heap proof times out, record the exact elapsed time and consider a more strongly decomposed arithmetic proof rather than increasing the timeout blindly.


## 49. Run #224 latest state — 2026-11-27T04:59:53Z

- Latest observed state: Run #224 `45943017177` remains `in_progress` at unit-test step 9. Steps 1–8 succeeded or were skipped from cache. Steps 10–14 remain pending; artifact list empty.
- The exact previous unit-test attempt Run #220 failed because `equiv_struct -icells` left 37 heap equivalence cells unproven. The current Run #224 tests the refined output-only heap proof and one-bit tamper rejection. Its result is not yet available.
- No new proof PASS, negative-test rejection, benchmark artifact, or fused PPA values exist. Keep PR #19 open/unmerged. Milestone #1 remains open; Milestone #2 (8/16/32 lanes) blocked until full four-lane proof and six-variant evidence are complete.
- Next: inspect completed Run #224 logs; if unit tests pass, inspect benchmark output/artifact for all six variants, 512 unique xorshift32 vectors, nonzero VCD annotation, and all four OpenSTA power components. If unit tests fail, preserve exact failure and refine the proof; do not claim a pass.
- Timestamp correction: section timestamps 34–48 were corrected to the actual UTC commit creation times of their corresponding STATUS commits. Earlier displayed 05:xx labels were estimates and were not actual event timestamps.
- Current STATUS update is on main. Ceres untouched; NEM separate; ORCUS v0.2 remains intact.


## 50. Run #224 completed with unit-test failure — 2026-11-27T05:00:49.992Z

- Run #224 / ID `45943017177` completed with conclusion `failure`. Job `140321357589` failed at step 9 (`Run unit tests`). Setup and cached OpenSTA verification succeeded; compile, benchmark, artifact upload, and smoke steps were skipped.
- No artifact is available. Exact unit-test failure has not yet been inspected; next retrieve the completed job logs and identify whether output-only heap equivalence timed out or returned unproven partitions.
- No formal PASS, negative tamper rejection, fused PPA metrics, or six-variant table can be claimed from Run #224. Milestone #1 remains open; Milestone #2 blocked. PR #19 remains open/unmerged.


## 51. Run #224 exact heap-proof timeout — 2026-11-27T05:01:26.329Z

- Retrieved completed job logs for Run #224 `45943017177`, job `140321357589`. The suite ran 64 tests; the fused compositional equivalence test errored and the remaining 63 tests passed.
- The 4x4 Baugh-Wooley lane lemma again completed successfully. The output-only symbolic heap lemma then timed out after `60.06s` with command:
  `read_verilog reference.v candidate.v; proc; equiv_make reference orcus_heap_gate equiv; hierarchy -top equiv; clean -purge; equiv_simple -v; equiv_status -assert`.
- Exact exception: `FORMAL_EQUIV_TIMEOUT: Yosys partitioned equivalence exceeded 60s for orcus_heap_gate; elapsed=60.06s`. Disabling `equiv_struct` removed the false internal matching problem but did not make the full 64-input heap SAT proof tractable.
- Benchmark and artifact steps were skipped; no fused metrics or complete six-variant table. Negative tamper test was not reached.
- Next proof strategy to evaluate: ABC's dedicated combinational equivalence checker (`cec`) on flattened AIGs, or a rigorously compositional compressor-stage proof using local full-adder lemmas. Do not simply increase timeouts or claim equivalence. Preserve both failed Yosys attempts and their exact evidence.
- PR #19 remains open/unmerged; latest branch head at Run #224 is `6f9c13eb45bb812eee523a1ea53cc02a01651bd9`. Milestone #1 open; Milestone #2 blocked. Ceres untouched; NEM separate.


## 52. ABC CEC proof strategy researched — 2026-11-27T05:01:38.776Z

- After Run #224, both full-output Yosys equivalence and output-only heap equivalence have timed out; the lane-only 4x4 lemma passes. No PPA benchmark has run on this branch.
- Reviewed ABC's documented `cec` command, which compares the primary-input/primary-output behavior of two networks and uses a hybrid FRAIG/SAT approach by default. Next strategy: export the full direct-reference and fused candidate designs to AIGER with Yosys, then run ABC `cec` on the two AIGs. Preserve exact PI order/names and require an explicit equivalent verdict; treat inequivalent, unknown, or timeout as failure.
- Add the same one-bit output tamper as a negative CEC control. This is only a proposed next experiment; it has not yet run and no proof claim is made.
- PR #19 remains open/unmerged; branch head from Run #224 `6f9c13eb45bb812eee523a1ea53cc02a01651bd9`. Milestone #1 open; Milestone #2 blocked. Ceres untouched; NEM separate.


## 53. Full-design ABC CEC implementation committed — 2026-11-27T05:02:03.145Z

- PR branch commits `336e8a1465272ff3dd71159bdfd87121c1b93291` and `3088d9538f8b741d431a9bad6601848bb2c40b46` replace the timed-out Yosys SAT/compositional fused proof with Berkeley ABC's dedicated `cec` checker on two full-design AIGER exports.
- For each design, Yosys runs `read_verilog; hierarchy -top; proc; flatten; techmap; opt; aigmap; write_aiger -ascii -symbols`. ABC then runs `cec -T <timeout> reference.aig candidate.aig`. Input and output names/order are kept identical by generating both modules from the same port contract.
- The proof compares complete primary-input/primary-output behavior for the original 32 input bits and all 10 output bits. An affirmative ABC verdict is required; an inequivalent, undecided, missing verdict, process failure, or timeout is fail-closed.
- The negative test now flips output bit 0 in the full fused RTL and requires ABC CEC to report `Networks are NOT EQUIVALENT`. Both positive and negative checks are configured with a 120-second timeout in unit tests; benchmark formal timeout remains 300 seconds.
- This is a new proof strategy under test, not a verified pass. Run #224 remains failed due to the 60.06-second output-only heap SAT timeout; no benchmark artifact or fused PPA data exists. Next: synchronize main STATUS/ancestry to the PR branch and run fresh CI on the ABC CEC implementation.
- Milestone #1 remains open; Milestone #2 (8/16/32 lanes) blocked. PR #19 remains open/unmerged. Ceres untouched; NEM separate.


## 54. ABC CEC branch synchronized — 2026-11-27T05:02:14.908Z

- Advanced `research/orcus-fused-int4-mac` with non-force two-parent merge commit `d8f0c6cc54d81d9bdacad15822eabead8ea9e905`.
- Parents: prior PR branch head `3088d9538f8b741d431a9bad6601848bb2c40b46` and main head `009dd556ec22ba73d75cb3952fdab175a06c6b03`. The merge tree includes main's current STATUS blob and preserves the ABC CEC implementation and negative test.
- Branch ref advanced successfully with `force=false` and expected-head protection. This is a main-to-PR-branch synchronization only; PR #19 remains unmerged.
- Next: confirm a fresh automatic PR workflow run for head `d8f0c6cc54d81d9bdacad15822eabead8ea9e905`, then inspect unit tests. No ABC CEC verdict yet.


## 55. ABC CEC run trigger check — 2026-11-27T05:02:22.035Z

- After branch synchronization to head `d8f0c6cc54d81d9bdacad15822eabead8ea9e905`, `fetch_commit_workflow_runs` returned no PR run at the time of this check.
- Direct PR API still reports mergeability `unknown` while recalculating; base `009dd556ec22ba73d75cb3952fdab175a06c6b03`, head `d8f0c6cc54d81d9bdacad15822eabead8ea9e905`.
- No ABC CEC proof result or CI run ID is confirmed yet. Next: inspect supported Actions run listing for the exact head; if no run exists, diagnose why synchronize did not trigger. Do not claim CI started.


## 56. ABC CEC CI Run #227 discovered — 2026-11-27T05:02:28.824Z

- The Actions run listing confirms automatic PR Run #227, ID `45943382079`, event `pull_request`, head `d8f0c6cc54d81d9bdacad15822eabead8ea9e905`, created `2026-11-27T05:02:16Z`; it is `in_progress`.
- The earlier commit-specific run lookup returned empty before the Actions listing updated. This was a lookup timing delay; the workflow has in fact triggered.
- Next: poll Run #227's job steps; the key gate is the full-design ABC CEC positive proof and one-bit negative test. No result or PPA metrics yet.


## 57. Run #227 setup progress — 2026-11-27T05:02:36.205Z

- Run #227 `45943382079` remains `in_progress` on ABC CEC branch head `d8f0c6cc54d81d9bdacad15822eabead8ea9e905`. Job `140322472966`: setup, checkout, and Python setup passed; dependency installation is active. Unit tests and benchmark remain pending; no artifact.
- Next: poll through unit tests, inspect the ABC CEC verdict and negative tamper test, then benchmark only if both pass.


## 58. Run #227 cache restore progress — 2026-11-27T05:02:43.270Z

- Run #227 `45943382079` remains `in_progress`. Dependency installation completed successfully; cache restore step 5 is active. Formal unit tests, benchmark, and artifact upload remain pending.
- No proof verdict or PPA data exists at this poll. Continue monitoring exact step transitions.


## 59. Run #227 failed at unit tests — 2026-11-27T05:02:50.109Z

- Run #227 `45943382079` completed with conclusion `failure`. Job failed at step 9 (`Run unit tests`); setup/cache/OpenSTA verification passed. Compile, benchmark, artifact, and smoke steps were skipped.
- Exact ABC CEC test failure has not yet been inspected. Next retrieve completed job logs and determine whether AIG export, ABC executable invocation, CEC verdict parsing, or actual equivalence caused the failure.
- No fused proof pass, negative-test rejection, artifact, or PPA metrics from this run.


## 60. Run #227 exact ABC CEC failure — 2026-11-27T05:02:57.989Z

- Retrieved completed Run #227 `45943382079`, job `140322472966` logs. All 63 non-CEC tests passed; the new ABC CEC test errored immediately before any equivalence computation.
- Exact error from ABC: `Wrong input file format. Reading AIG from file has failed.` The export command used Yosys `write_aiger -ascii -symbols` but named the resulting ASCII AIGER file with the binary `.aig` extension. ABC's `cec` reader rejected the format. This is a file-format mismatch, not an equivalence counterexample or proof timeout.
- Benchmark and artifact steps were skipped. No proof pass or PPA result.
- Next: export binary AIGER (remove `-ascii`) while keeping `.aig`, or use an ASCII extension supported by ABC. Re-run the full positive/negative CEC test; require explicit `Networks are equivalent` for the valid design and `Networks are NOT EQUIVALENT` for the one-bit tamper.
- PR #19 remains open/unmerged. Milestone #1 open; Milestone #2 blocked. Ceres untouched; NEM separate.


## 61. ABC AIGER format correction committed — 2026-11-27T05:03:06.944Z

- PR branch commit `604edb03dd9da3793aca591911e84a52428aa105` removes `-ascii` from Yosys `write_aiger`, so the `.aig` files are binary AIGER as expected by ABC's AIG reader.
- This directly addresses Run #227's `Wrong input file format` error. No proof result is claimed until a new CI run confirms the export and CEC verdicts.
- Next: synchronize main STATUS/ancestry to the PR branch with a non-force merge commit, trigger fresh CI, and inspect the positive full-design proof plus negative one-bit tamper test.


## 62. Binary AIGER branch synchronization — 2026-11-27T05:03:19.863Z

- Advanced `research/orcus-fused-int4-mac` to non-force two-parent merge commit `b7a479a03b51ac633963947170186ba7c41afb3a`.
- Parents: previous PR branch head `604edb03dd9da3793aca591911e84a52428aa105` and main head `da4e86b3c125c7522b405c5f899db9a6c6009d02`. Merge tree preserves the binary AIGER export change and includes the current main STATUS blob.
- Branch ref update succeeded with `force=false` and expected-head protection. No PR merge.
- Next: confirm fresh PR CI for head `b7a479a03b51ac633963947170186ba7c41afb3a`; inspect the binary AIGER reader and ABC CEC verdict. No proof pass yet.


## 63. Binary AIGER CI trigger lookup — 2026-11-27T05:03:26.169Z

- Commit-specific workflow lookup for branch head `b7a479a03b51ac633963947170186ba7c41afb3a` returned no PR run at this instant. This lookup can lag; check the Actions run listing before concluding no workflow fired.
- No new test, proof, or benchmark result. The branch change is committed and main STATUS is current through the branch sync record.


## 64. Binary AIGER ABC CEC Run #229 started — 2026-11-27T05:03:33.271Z

- Actions listing confirms automatic PR Run #229, ID `45943490330`, event `pull_request`, exact head `b7a479a03b51ac633963947170186ba7c41afb3a`, created `2026-11-27T05:03:23Z`, currently `in_progress`.
- Next: inspect job steps, then completed logs. Required gate remains full direct-vs-fused ABC CEC PASS and one-bit tamper rejection. No proof or PPA data yet.


## 65. Run #229 setup progress — 2026-11-27T05:03:40.744Z

- Run #229 `45943490330` remains `in_progress` on branch head `b7a479a03b51ac633963947170186ba7c41afb3a`. Job `140322812925`: setup, checkout, and Python setup succeeded; dependency installation is active. Unit tests and benchmark remain pending; no artifact.
- Next: monitor step 9. The critical check is whether ABC reads the binary AIGER files and returns an affirmative full-design equivalence verdict, followed by successful one-bit tamper rejection.
