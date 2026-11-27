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


## 66. Run #229 second setup poll — 2026-11-27T05:03:49.064Z

- Run #229 `45943490330` is still `in_progress`; step 4 (apt dependency installation) remains active. Steps 5–8 and unit-test step 9 have not completed/started. No artifact.
- No ABC CEC verdict, negative tamper result, or benchmark evidence yet. No code change in this poll.
- Next: continue monitoring; once unit tests complete, inspect full job logs. If the run is still active at handoff, leave it explicitly marked in progress rather than assuming outcome.


## 67. Run #229 unit-test stage active — 2026-11-27T05:03:56.860Z

- Run #229 `45943490330` remains `in_progress`. Setup, dependencies, cache restore, and OpenSTA verification passed; unit-test step 9 is now active. Benchmark and artifact steps remain pending; artifact list is empty.
- No CEC verdict or negative-test result is available yet. Next: retrieve logs after step 9 completes; do not report proof pass based only on step start.


## 68. Run #229 latest poll — 2026-11-27T05:04:04.254Z

- Run #229 `45943490330` remains `in_progress` at unit-test step 9. Steps 1–8 succeeded or were skipped on cache hit; steps 10–14 remain pending. No artifact is available.
- The binary AIGER export/ABC CEC test has not yet reported a result. No six-variant benchmark has run.
- Next: inspect the completed job log once step 9 exits. If it passes, inspect the benchmark artifact and all formal/activity/STA fields. If it fails, preserve exact error and fix the exporter/CEC integration. Do not claim a proof or close Milestone #1 until evidence exists.


## 69. Run #229 final audit — 2026-11-27T05:10:52.319Z

- Read the current `main` STATUS before repository work. Current `main` head before this update: `9e9bbd8a7efd86861d33d87b5f0ff52af3bc6ac4`; STATUS blob: `a3b06e0cbd401d7918004a2ab45aad776b3a9585`.
- Run #229 / ID `45943490330` completed with conclusion `failure` on exact PR head `b7a479a03b51ac633963947170186ba7c41afb3a`. Job `140322812925` failed at step 9 (`Run unit tests`). Steps 1–8 passed or were skipped on cache hit. Steps 10–14, including compile, Liberty fetch, benchmark, artifact upload, and smoke verification, were skipped.
- Full job logs show 64 unit tests: 63 passed and `test_fused_abc_cec_proves_full_output_and_rejects_one_bit_tamper` errored. Both Yosys AIGER exports completed sufficiently for ABC to start; the previous binary-vs-ASCII AIGER reader error did not recur.
- Exact failing command: `/usr/bin/yosys-abc -c 'cec -T 120 "/tmp/orcus-abc-cec-nnrodfcu/reference.aig" "/tmp/orcus-abc-cec-nnrodfcu/candidate.aig"'`. Python raised `subprocess.TimeoutExpired` after its 130-second outer timeout. The wrapper reported `ABC_CEC_TIMEOUT: ABC cec exceeded 120s for orcus_fused_partial_product; elapsed=130.39s.` The test ran for 132.010s. This is a proof-complexity timeout, not an AIGER file-format error and not an inequivalence counterexample.
- Positive full-design ABC CEC did not return an affirmative verdict. The negative one-bit tamper control was not reached. Benchmark did not start. Run #229 has no artifacts. There are no Run #229 six-variant formal results, vector/uniqueness counts, VCD annotation counts, generic-cell counts, Nangate45 area, OpenSTA delay, raw power components, or stage timings.
- Do not populate a fused comparison row or claim fused Baugh-Wooley wins/loses. The only established comparator remains the historical two-stage carry-save baseline: 460.712 Nangate45 area units, 0.89 ns OpenSTA delay, and 84.60975 µW total estimated power from Run #201. These remain pre-layout research-library estimates without routed parasitics.
- PR #19 remains open and unmerged; current head remains `b7a479a03b51ac633963947170186ba7c41afb3a`. Latest PR metadata reports `mergeable=false`; do not merge. Milestone #1 remains OPEN; Milestone #2 is BLOCKED.
- Diagnostic inspection of the PR source confirms the AIGER export is binary (the `-ascii` flag is absent) and ABC reaches the `cec` command. The stored `proof_method` description still incorrectly says `write_aiger -ascii -symbols`; correct that metadata when the proof implementation is next changed. The exact current blocker is that a monolithic 32-input/10-output CEC proof of the complete reference and fused multiplier/heap design exceeds the 120-second configured ABC limit.
- Next actions: (1) preserve Run #229 logs and failure history; (2) replace the monolithic proof attempt only with a sound compositional proof strategy that proves the 4x4 signed Baugh-Wooley lane identity and each 3:2 compressor's weighted-sum invariant, with a mechanically checked reduction graph/heap invariant tying the local lemmas to the final 10-bit result; (3) add a negative tamper control at the relevant proof boundary; (4) correct proof-method metadata to describe binary AIGER only if retaining that path; (5) run unit tests and trigger a new PR CI via a branch commit; (6) only after all proof gates pass, benchmark all six variants and inspect 512 unique xorshift32 vectors, nonzero VCD pin annotation, raw OpenSTA reports, stage timings, and all power components; (7) then sync STATUS ancestry to the PR branch as needed and review Milestone #1. Milestone #2 remains 8-lane/11-bit, 16-lane/12-bit, and 32-lane/13-bit signed INT4 dot-product scaling, comparing direct, multi-stage carry-save, and fused Baugh-Wooley under equivalent proof and benchmark controls.
- Ceres remains out of scope and untouched; NEM remains distinct. ORCUS v0.2 baseline commit `3fcf0024d621db90ac913d9671c1f60d8588c5d9` remains the historical reference.


## 70. Compositional-proof design audit — 2026-11-27T05:14:18.788Z

- Read `STATUS.md` on `main` before repository inspection. At audit start, `main` was `6e7befdc6dc5e0d01d990320b95f99801fcab268`; current PR #19 branch head is `b7a479a03b51ac633963947170186ba7c41afb3a`; PR remains open, unmerged, and GitHub reports `mergeable=false`.
- Inspected the exact branch benchmark generator and tests. The fused RTL generator creates four-lane Baugh-Wooley complemented cross-sign partial products, inserts four constant bits per lane at columns 4, 7, 8, and 9 (10-bit bias `0x390)), greedily reduces columns using explicit XOR/majority full-adder equations, then emits a final 10-bit `fused_row0 + fused_row1` adder.
- Existing lane-only helper separately uses the 8-bit Baugh-Wooley correction `0x90`. Do not conflate that 8-bit identity with the actual 10-bit heap bias `0x390`; formalize the exact generated 10-bit weighted sum and sign-extension semantics. The current monolithic ABC proof-method metadata also still incorrectly says `write_aiger -ascii -symbols` although binary export is used.
- Mathematical requirements refined: full-adder invariant is `2*c_out + s = x0+x1+x2`; half-adder invariant is `2*c_out+s=x0+x1`. The final carry-propagate adder requires its own modulo-`2^10` arithmetic equivalence proof; it is not the same compressor primitive invariant. A proof must account for dropped carry at the top column as modulo-width truncation, not silently discard an unconstrained signal.
- A correct compositional proof needs: (A) SAT proof of the exact lane-level Baugh-Wooley encoding at the actual heap width/bias; (B) SAT proofs of exact full-adder and half-adder RTL plus final-adder arithmetic; (C) a deterministic graph/weight audit that proves every generated bit has exactly one source/use, correct column weight, correct carry destination, and correct final-row membership. The generator and audit must share an explicit typed heap representation or independently parse emitted RTL; source substring checks alone are insufficient. Negative tests must mutate polarity, compressor carry destination, and final output bit and demonstrate rejection.
- The user-provided expectation that this necessarily runs in under one second and effortlessly scales to 8/16/32 lanes is unverified. Runtime and scaling must be measured in CI; do not promise them. Also, the proposed `2*c_out+s` formula must distinguish a one-bit carry from a carry already shifted into the next column.
- No branch files were modified in this audit. No new CI run was triggered. No proof result, artifact, stage timing, or new PPA data exists. Milestone #1 remains open; Milestone #2 remains blocked. Preserve Run #229's 120-second ABC CEC timeout history.
- Next: implement typed heap generation plus independently checkable connectivity/weight accounting; add Yosys `sat -verify` lane, FA, HA, and final-adder lemmas; add polarity/carry-weight/output tamper tests; run focused tests before full CI; then benchmark only after all proof gates pass. Keep PR #19 unmerged pending reviewed evidence. Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact.


## 71. Compositional proof implementation handoff — 2026-11-27T05:14:57.436Z

- Re-read current `main` STATUS before any further repository operation. Previous main STATUS commit: `a8be3df1de89af25ec8e81d1582c40efce77d42e`.
- Reconfirmed PR #19 remains open/unmerged, head `b7a479a03b51ac633963947170186ba7c41afb3a`, GitHub `mergeable=false`. The PR branch still contains the monolithic ABC CEC implementation that timed out in Run #229; no follow-up run is confirmed.
- The compositional proof implementation has NOT yet been committed. No claim is made that Lemma A/B/C or any negative tamper test has passed. No CI run has been triggered and no new benchmark artifact or PPA table exists.
- Reason for stopping before source mutation: the requested Part C must verify the actual generated heap's graph, not merely assert substrings or repeat the generator's assumptions. A safe implementation must first introduce an explicit typed bit-heap/compressor representation, generate the RTL from it, independently audit the emitted connectivity and weights, and include a proof of the final modulo-1024 adder. The existing RTL generator currently emits inline XOR/majority expressions without explicit reusable FA/HA module instances; a test that claims to prove exact compressor RTL without refactoring that representation would be misleading. Keep the existing PR implementation intact until that refactor and tests are ready together.
- Verified arithmetic convention: each signed 4x4 lane's complemented cross-sign Baugh-Wooley partial products use a 10-bit correction of `0x390` (equivalent to `0x90` modulo 256 in the 8-bit product identity). The actual fused heap is modulo 1024. The FA/HA local identities are respectively `2*c+s=x0+x1+x2` and `2*c+s=x0+x1`; final CPA correctness is a separate modulo-1024 proof. Top-column carry truncation must be explicitly represented as modulo-width arithmetic.
- Next concrete implementation sequence: (1) add typed bit-heap node/column/compressor records and a deterministic reduction schedule; (2) generate the fused RTL and a machine-readable graph manifest from that representation; (3) add Yosys SAT proof harnesses for 4x4 lane bias identity, exact FA and HA equations, and the 10-bit final adder; (4) independently parse emitted RTL/manifest and reject wrong source polarity, wrong carry column, duplicate/dangling nodes, and final output wiring errors; (5) add polarity, carry-weight, and output-bit tamper tests; (6) run local/CI proof suite and measure runtime; (7) only after proof gates pass, sync STATUS to branch and trigger benchmark CI. Do not claim sub-second runtime or scaling until measured. Milestone #1 remains open; Milestone #2 (8/11-bit, 16/12-bit, 32/13-bit) blocked.
- No PR branch files were changed in this turn; no PR branch commit or CI run ID exists. Ceres was not accessed; NEM remains distinct; ORCUS v0.2 baseline remains intact.


## 72. Requested typed-heap implementation — repository preflight — 2026-11-27T05:16:42.668Z

- Read current `main` STATUS first. Current main head is `6c51efbe83168b52fd29d5e59aa5053172e711ce`; STATUS blob is `0a9ca4acf23e9bd3846804c843d2e4686225081d`. PR #19 head remains `b7a479a03b51ac633963947170186ba7c41afb3a`; PR open/unmerged and GitHub reports `mergeable=false`.
- Inspected the complete fused generator entry points and unit tests. The existing fused reduction is an inline FA-only greedy heap (no HA node) with lane partial products, four 10-bit correction bits per lane (0x390 per lane), and a 10-bit final row adder. Existing formal test still uses monolithic ABC CEC and timed out in Run #229.
- Implementation will be additive and fail-closed: a typed deterministic heap representation, generated RTL/manifest, independent manifest/RTL audit, SAT harnesses, and three negative tamper cases. Any proof or CI outcome will be reported only after execution. No branch files changed and no CI run triggered at this preflight point.
- Do not claim `mergeable=true` merely by syncing STATUS; GitHub computes mergeability and the PR base/head ancestry may also need synchronization. No merge authorization has been given.
- Ceres was not accessed. NEM remains distinct. ORCUS v0.2 baseline remains intact.


## 73. Typed heap implementation committed to PR #19 — 2026-11-27T05:21:46.973Z

- PR #19 branch commit: `01d30e739b5030481313022a5d485c1b6a4d82d8`; branch `research/orcus-fused-int4-mac` advanced from `b7a479a03b51ac633963947170186ba7c41afb3a` using a non-force, expected-head-protected update. Files changed: new `orcus/typed_heap.py`; integrated fused RTL generator and proof flow in `benchmarks/signed_int4_dot_product.py`; replaced monolithic CEC unit test with compositional SAT and three negative tamper tests in `tests/test_signed_int4_dot_product.py`.
- Implementation includes typed initial weighted bits (partial products and per-lane bias bits), deterministic 3:2 compressor nodes, two final rows, explicit top-column carry truncation modulo 2^10, generated RTL and JSON-serializable graph manifest. Benchmark artifact now records the manifest and individual SAT lemma timings.
- Compositional proof harness includes: 10-bit signed Baugh-Wooley lane identity SAT lemma using bias 0x390; full-adder weighted-sum SAT lemma; half-adder weighted-sum SAT lemma; 10-bit modulo CPA SAT lemma; independent RTL/graph audit; tamper tests for partial-product polarity, compressor carry weight, and output assignment.
- **Not yet verified:** no local Yosys or Python test execution was performed in this repository write action. No proof runtime is measured yet. No CI run ID, stage timings, or benchmark artifact is confirmed. Do not claim the SAT lemmas or negative tests pass until CI logs confirm them.
- Next: sync current main STATUS ancestry/blob onto the PR branch with a non-force two-parent merge commit, confirm PR mergeability after GitHub recalculates, then inspect the new synchronize-triggered CI run. If tests fail, preserve logs and fix the exact failure. Benchmark is permitted only after proof and unit tests pass. Milestone #1 remains open; Milestone #2 blocked.
- Ceres untouched; NEM distinct; ORCUS v0.2 baseline unchanged.


## 74. PR #19 STATUS ancestry synchronized — 2026-11-27T05:22:12.973Z

- Synced current `main` STATUS blob `55dd9d70540190e4b7db13102ca46e3421bdc2f5` and `main` ancestry commit `547f20c063ec60905f8fcaf60c65774f0e552500` into `research/orcus-fused-int4-mac` with non-force two-parent merge commit `6d11c50eadcf36d56b756578d505d75248791130`.
- Merge parents: PR implementation commit `01d30e739b5030481313022a5d485c1b6a4d82d8` first, main `547f20c063ec60905f8fcaf60c65774f0e552500` second. Branch ref update succeeded with `force=false` and expected-head protection. No PR merge.
- This sync is intended to restore ancestry and current STATUS on the branch; it does not guarantee GitHub's computed `mergeable` field is true. Verify PR metadata after GitHub recalculates.
- No new CI result is confirmed at this exact step. Next: inspect PR #19 metadata and Actions runs for exact new branch head `6d11c50eadcf36d56b756578d505d75248791130`; monitor unit tests and compositional proof. No proof runtime or benchmark result is yet established.
- Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact.


## 75. Compositional proof CI Run #231 started — 2026-11-27T05:22:30.197Z

- PR #19 current head: `6d11c50eadcf36d56b756578d505d75248791130`; base/main: `547f20c063ec60905f8fcaf60c65774f0e552500`. GitHub PR metadata after synchronization still reports `mergeable=false`; do not claim it is mergeable. PR remains open and unmerged.
- Automatic PR workflow Run #231, ID `45945384577`, event `pull_request`, was discovered for exact head `6d11c50eadcf36d56b756578d505d75248791130`; status `in_progress`. Job `140328775094`: setup, checkout, and Python setup succeeded; dependency installation step 4 is active. Unit tests (step 9), compile, benchmark, artifact upload, and smoke verification are pending.
- The branch includes typed heap generator, manifest, compositional SAT harness, and polarity/carry-weight/output tamper tests, but no test or proof result is confirmed yet. Do not report a runtime or formal pass until the job logs establish it.
- Next: poll Run #231. If unit tests pass, inspect all four SAT lemma outputs and tamper rejections; then allow six-variant benchmark to run and inspect artifact/raw reports. If failure occurs, retrieve exact logs and record diagnosis. Milestone #1 remains open; Milestone #2 blocked.
- Ceres untouched; NEM distinct; ORCUS v0.2 baseline unchanged.


## 76. Run #231 dependency/cache progress — 2026-11-27T05:22:42.406Z

- Run #231 `45945384577`, job `140328775094`, exact head `6d11c50eadcf36d56b756578d505d75248791130` remains `in_progress`. Dependency installation completed successfully; cache restore step 5 is active. Steps 6–14, including unit tests and the compositional proof suite, have not yet completed.
- PR #19 metadata still reports `mergeable=false` after the ancestry sync. It remains open/unmerged. Do not represent STATUS sync as proof that mergeability is true.
- No SAT result, tamper-test result, proof runtime, benchmark stage timing, artifact, or PPA data is available at this poll.
- Next: continue polling Run #231 and inspect the unit-test logs as soon as step 9 completes. Ceres untouched; NEM distinct; baseline intact.


## 77. Run #231 unit-test failure — 2026-11-27T05:23:26.832Z

- Run #231 `45945384577`, job `140328775094`, exact branch head `6d11c50eadcf36d56b756578d505d75248791130` failed at unit-test step 9. Dependency/cache/OpenSTA verification passed. Python compilation, Nangate45 fetch, benchmark, artifact upload, and smoke verification were skipped.
- Full logs show 67 tests: 64 passed, 2 failed, 1 errored. The compositional audit exposed a manifest schema bug: the generator placed compressor-output records in `initial_bits` as well as recording them as compressor nodes. The auditor correctly rejected the unexpected `compressor_sum` kind before running SAT lemmas. Consequently the carry-weight and output-tamper tests also failed early for that same schema issue; the partial-product polarity tamper test passed.
- No SAT lemma ran to completion; no proof runtime, benchmark stage timing, artifact, or PPA data exists. This is a software/manifest classification defect, not evidence of arithmetic inequivalence.
- Next: fix manifest serialization so `initial_bits` contains only partial-product and constant-bias sources; compressor sum/carry nodes remain exclusively in compressor records. Strengthen the audit to require the exact expected initial PP/bias ID set. Re-run unit tests in fresh CI and inspect all four SAT lemma verdicts and all three negative tests. Do not start/claim benchmark results until the proof suite passes.
- PR #19 remains open/unmerged; latest known GitHub metadata still `mergeable=false`. Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact. Milestone #1 open; Milestone #2 blocked.


## 78. Typed heap manifest classification fix committed — 2026-11-27T05:23:57.502Z

- Fixed the Run #231 manifest schema defect on PR branch with commit `668122146ed2c546d0f47dc8ff53e3d2ba750d80` (parent `6d11c50eadcf36d56b756578d505d75248791130`). `initial_bits` now serializes only partial-product and constant-bias source nodes; compressor sum/carry outputs remain represented in compressor records. The independent audit now also requires the exact complete expected source-bit ID set for all lanes.
- This fix addresses the observed `unexpected initial bit kind: compressor_sum` error. It is not yet verified by tests. Run #231 remains failed and historical; no rerun result is yet confirmed. No SAT lemma or benchmark has completed.
- Next: sync latest main STATUS/ancestry to the branch and inspect the synchronize-triggered CI run for the new head. Confirm that the four SAT lemmas run and the three tamper tests reject the modified designs. If another failure appears, preserve exact logs and fix only the demonstrated issue. No runtime claim until measured.
- PR #19 remains open/unmerged. Latest mergeability state from before this fix was `false`; recheck after sync. Ceres untouched; NEM distinct; baseline intact. Milestone #1 open; Milestone #2 blocked.


## 79. PR #19 branch resynchronized after Run #231 fix — 2026-11-27T05:24:21.802Z

- Synced latest `main` STATUS blob from `dac135dea73743d306c8c37d5720e3abe10265f5` and main ancestry `dac135dea73743d306c8c37d5720e3abe10265f5` into PR branch using non-force two-parent merge commit `1b2c502e056009f922d47bcab4c0b21f089c8107`.
- Merge parents: branch fix commit `668122146ed2c546d0f47dc8ff53e3d2ba750d80` first, main `dac135dea73743d306c8c37d5720e3abe10265f5` second. Branch ref update succeeded with expected-head protection and `force=false`.
- This new branch head should trigger PR CI. Run #231 `45945384577` remains failed on prior head `6d11c50eadcf36d56b756578d505d75248791130`; it is preserved as history. No proof pass or benchmark result is claimed.
- Next: inspect PR metadata and Actions listing for exact head `1b2c502e056009f922d47bcab4c0b21f089c8107`; monitor tests and proof logs. Ceres untouched; NEM separate; ORCUS v0.2 baseline intact.


## 80. Compositional proof CI Run #233 started — 2026-11-27T05:24:38.223Z

- Automatic PR Run #233, ID `45945601986`, is confirmed for exact branch head `1b2c502e056009f922d47bcab4c0b21f089c8107`; event `pull_request`; status `in_progress`. Job `140329457878`: setup, checkout, Python setup succeeded; dependency installation step 4 active. Unit tests and benchmark pending.
- PR #19 remains open/unmerged. GitHub still reports `mergeable=false` after both ancestry/STATUS syncs; this is a reported state, not to be overridden or described as true.
- Run #231 failure `45945384577` is preserved. Its fix is committed in `668122146ed2c546d0f47dc8ff53e3d2ba750d80`; Run #233 is the first CI run on the corrected source-node manifest and current main STATUS ancestry.
- No SAT proof result, tamper-test result, runtime, benchmark artifact, stage timing, or PPA result exists yet. Next: poll Run #233; inspect full unit-test output and proceed to benchmark only if tests pass.
- Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact. Milestone #1 open; Milestone #2 blocked.


## 81. Run #233 dependency installation still active — 2026-11-27T05:24:49.448Z

- Run #233 `45945601986`, job `140329457878`, exact head `1b2c502e056009f922d47bcab4c0b21f089c8107` remains `in_progress`. Setup/checkout/Python setup succeeded; dependency installation step 4 remains active. No test or benchmark step has run yet.
- No new proof, tamper-test, runtime, artifact, or PPA evidence. Continue polling; Run #231's manifest classification failure remains historical and unchanged.


## 82. Run #233 second unit-test failure — 2026-11-27T05:25:17.854Z

- Run #233 `45945601986`, job `140329457878`, exact head `1b2c502e056009f922d47bcab4c0b21f089c8107` failed at unit-test step 9. Setup, dependencies/cache, and OpenSTA verification passed. Compile, benchmark, artifact upload, and smoke steps were skipped.
- Logs show 67 tests: 65 passed, 1 failed, 1 errored. The polarity and carry-weight tamper tests passed. The compositional audit errored at `full-adder sum equation mismatch: fa_24`; the output-tamper test failed early at the same audit check, before reaching its intended CPA-output assertion. The prior source-node classification error is fixed.
- No SAT lemma completed; the failure occurs in graph/RTL audit before SAT invocation. No proof runtime, benchmark artifact, stage timing, or PPA data exists.
- Next: inspect the exact emitted FA declaration and manifest operand order around `fa_24`; reconcile the auditor's parsed RTL expressions with the generator's emitted expression representation. Keep audit fail-closed. Then rerun all tests. Do not relax the check or skip the failing node.
- PR #19 remains open/unmerged; latest mergeability remains `false`. Run #231 and #233 failures are preserved. Ceres untouched; NEM distinct; baseline intact. Milestone #1 open; Milestone #2 blocked.


## 83. RTL audit tokenization fix committed — 2026-11-27T05:25:57.046Z

- Corrected the second Run #233 audit defect on PR branch commit `ebb0c82601715fcb2a0425231fcbf7948736279f` (parent `1b2c502e056009f922d47bcab4c0b21f089c8107`). The auditor now maps typed constant-bias source IDs to the literal `1'b1` when comparing emitted FA sum/carry expressions and final-row wiring; signal-backed bits retain their declared wire names.
- This directly addresses `full-adder sum equation mismatch: fa_24`, where the generator emitted constant input expressions but the auditor compared typed manifest IDs as if they were RTL identifiers. It also fixes the latent undefined `rtl_expr` reference in final-row checking.
- Run #233 `45945601986` remains failed on its earlier head; 65/67 tests passed, with the compositional audit and output-tamper test blocked by the same audit-token mismatch. The polarity and carry-weight tamper tests passed. No SAT lemma ran and no benchmark/artifact exists.
- Next: synchronize latest main STATUS onto the PR branch and inspect the next CI run. Require all four SAT lemmas, full graph audit, and all three tamper tests to pass before benchmarking. No proof runtime or scaling claim until measured.
- PR #19 remains open/unmerged; last metadata `mergeable=false`. Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact. Milestone #1 open; Milestone #2 blocked.


## 84. PR #19 resynchronized after RTL audit fix — 2026-11-27T05:26:19.579Z

- Synced current main STATUS blob from `3bc16f01d189d6fc117eccc94ad1f32edd10cedf` and main ancestry into PR branch using non-force two-parent merge commit `60d551fa4512f3367e8c1d748f2abecd3c6f932e`.
- Parents: corrected branch commit `ebb0c82601715fcb2a0425231fcbf7948736279f` first; main `3bc16f01d189d6fc117eccc94ad1f32edd10cedf` second. Expected-head-protected branch update succeeded; no PR merge.
- This branch head should trigger a new PR workflow. Run #233 remains failed on prior head `1b2c502e056009f922d47bcab4c0b21f089c8107`; preserved. No SAT proof result or benchmark evidence yet.
- Next: check exact-head Actions listing and poll the new run. PR #19 remains open/unmerged. Ceres untouched; NEM distinct; baseline intact.


## 85. Corrected RTL audit CI Run #235 started — 2026-11-27T05:26:36.410Z

- Actions run listing confirms automatic PR Run #235, ID `45945802919`, exact head `60d551fa4512f3367e8c1d748f2abecd3c6f932e`, event `pull_request`, created `2026-11-27T05:26:16Z`, status `in_progress`. The commit-specific run lookup was stale/empty; repository Actions listing confirms the run.
- PR #19 remains open/unmerged; GitHub still reports `mergeable=false`. Do not claim it is mergeable.
- Run #233 `45945601986` failed due to constant-bias RTL token mismatch in FA expression audit; corrected in branch commit `ebb0c82601715fcb2a0425231fcbf7948736279f`, synchronized in head `60d551fa4512f3367e8c1d748f2abecd3c6f932e`.
- Next: poll Run #235 and inspect unit tests, all four SAT lemmas, three negative tamper tests, then benchmark only if all pass. No proof runtime or benchmark evidence yet.
- Ceres untouched; NEM distinct; baseline intact. Milestone #1 open; Milestone #2 blocked.


## 86. Run #235 setup progress — 2026-11-27T05:26:47.136Z

- Run #235 `45945802919`, job `140330080622`, exact head `60d551fa4512f3367e8c1d748f2abecd3c6f932e` remains `in_progress`. Setup, checkout, and Python setup passed; dependency installation step 4 is active. Unit tests, SAT lemmas, benchmark, and artifact steps remain pending.
- No new formal or negative-tamper result; no runtime or PPA metrics. Continue polling. PR #19 mergeability remains reported false.


## 87. Run #235 unit tests active — 2026-11-27T05:26:57.832Z

- Run #235 `45945802919`, job `140330080622`, exact head `60d551fa4512f3367e8c1d748f2abecd3c6f932e` remains `in_progress`. Dependency installation, cache restore, and OpenSTA verification passed; unit-test step 9 is active. Python compilation, benchmark, artifact upload, and smoke check remain pending.
- No SAT lemma verdict or tamper-test outcome is confirmed until step 9 completes. No proof runtime or PPA metrics yet.


## 88. Run #235 final audit failure — 2026-11-27T05:27:18.867Z

- Run #235 `45945802919`, job `140330080622`, exact head `60d551fa4512f3367e8c1d748f2abecd3c6f932e` failed at unit-test step 9. Setup/dependencies/cache/OpenSTA verification passed; compile, benchmark, artifact, and smoke steps were skipped.
- Logs show 67 tests: 65 passed, 1 failed, 1 errored. The prior FA constant-token mismatch is fixed; partial-product polarity and compressor carry-weight tamper tests pass. The compositional audit now fails when checking `fused_row0`; output-tamper test also fails early at the same point.
- Exact cause from source inspection: the independent RTL declaration parser matches scalar `wire name = ...` declarations but not vector declarations such as `wire [9:0] fused_row0 = ...`. Thus the row vector is absent from the parsed declaration map. This is an audit parser coverage bug, not a SAT counterexample. No SAT lemma has run; no proof runtime or benchmark data exists.
- Next: extend the declaration parser to accept optional packed-width declarations and retain exact RHS checking. Re-run all tests. Keep the output-tamper test expected to reach and reject the altered CPA assignment, not fail earlier.
- PR #19 remains open/unmerged; last GitHub mergeability state `false`. Ceres untouched; NEM distinct; baseline intact. Milestone #1 open; Milestone #2 blocked.


## 89. Packed-wire RTL audit parser correction committed — 2026-11-27T05:28:10.077Z

- Corrected the Run #235 vector declaration parser on PR branch commit `ef85ed7de100b24d6e1fbd881ac48d2a5b615681` (parent `fa9f8f8db3b28d413176c23026d93054de5103be`). The parser now recognizes both scalar `wire name = ...` and packed vector `wire [N:0] name = ...` declarations, preserving exact RHS matching for final rows.
- An intermediate branch commit `fa9f8f8db3b28d413176c23026d93054de5103be` was created with an unchanged blob because the first regex replacement did not match; it made no source-content change. The corrected implementation is in `ef85ed7`.
- Run #235 `45945802919` failed before SAT because the audit parser omitted packed row declarations. Polarity and carry-weight tamper tests passed; output-tamper test was blocked by the same parser gap. No SAT lemma, benchmark, artifact, runtime, or PPA result yet.
- Next: sync latest main STATUS and ancestry to branch; inspect next CI run. Require all tests and four SAT lemmas to pass before benchmark. PR #19 open/unmerged; last mergeability false. Ceres untouched; NEM distinct; baseline intact.


## 90. PR #19 resynchronized after packed-wire parser correction — 2026-11-27T05:28:34.039Z

- Synced latest main STATUS blob from `732b00d62b86fb48e086d14aa912aa2abb0f6e01` and main ancestry into branch using non-force two-parent merge commit `0b24e86bedfab9c63a72d1d724562b1e0fa3237f`.
- Merge parents: corrected source commit `ef85ed7de100b24d6e1fbd881ac48d2a5b615681` first; main `732b00d62b86fb48e086d14aa912aa2abb0f6e01` second. Branch update succeeded with expected-head protection and `force=false`.
- New branch head should trigger another PR CI run. Run #235 `45945802919` remains failed on the prior head; no SAT lemma or benchmark result was produced.
- Next: inspect Actions run listing for exact head `0b24e86bedfab9c63a72d1d724562b1e0fa3237f`; monitor unit tests and proof. PR #19 remains open/unmerged. Ceres untouched; NEM separate; baseline intact.


## 91. Packed-wire parser CI Run #238 started — 2026-11-27T05:28:46.416Z

- Actions run listing confirms automatic PR Run #238, ID `45946018320`, exact head `0b24e86bedfab9c63a72d1d724562b1e0fa3237f`, created `2026-11-27T05:28:31Z`, status `in_progress`.
- This run includes the packed vector declaration parser fix and latest main STATUS ancestry. Run #235 `45945802919` remains failed on previous head. No new test/proof result or benchmark evidence yet.
- Next: poll Run #238, verify all three tamper tests and four SAT lemmas, then proceed to benchmark only if unit tests pass. PR #19 remains open/unmerged; no merge authorization.


## 92. Run #238 dependency stage active — 2026-11-27T05:28:56.566Z

- Run #238 `45946018320`, job `140330785714`, exact head `0b24e86bedfab9c63a72d1d724562b1e0fa3237f` is `in_progress`. Setup, checkout, and Python setup passed; dependency installation step 4 active. Unit tests, SAT lemmas, and benchmark pending.
- No new formal result, runtime, artifact, or PPA evidence. Continue polling; preserve all earlier failed runs.


## 93. Run #238 second dependency poll — 2026-11-27T05:29:06.717Z

- Run #238 `45946018320`, job `140330785714`, remains `in_progress`; dependency installation step 4 is still active. No unit tests or proof lemmas have started. No new benchmark or artifact evidence.


## 94. Run #238 dependency cache restore active — 2026-11-27T05:29:16.015Z

- Run #238 `45946018320`, job `140330785714`: dependency installation completed successfully; cache restore step 5 is active. Unit tests and all later stages remain pending. No proof result or benchmark data.


## 95. Run #238 proof tests PASS; benchmark failed — 2026-11-27T05:29:29.059Z

- Run #238 `45946018320`, job `140330785714`, exact head `0b24e86bedfab9c63a72d1d724562b1e0fa3237f`: unit-test step 9 succeeded; Python compilation step 10 succeeded; Liberty fetch step 11 succeeded. Benchmark step 12 failed. Artifact upload and smoke verification were skipped.
- The three negative tamper tests and compositional proof unit test passed at the unit-test stage; exact SAT lemma verdicts/timings and the benchmark failure cause require log inspection before stating them. Do not infer PPA data from test success.
- Next: retrieve full Run #238 logs, identify exact benchmark-stage failure. If proof lemmas passed, record their timings; then fix only the demonstrated benchmark integration issue and rerun. No six-variant artifact or PPA result is confirmed yet.
- PR #19 remains open/unmerged; no merge authorization. Ceres untouched; NEM distinct; baseline intact. Milestone #1 remains open until the full benchmark artifact is validated.


## 96. Run #238 compositional SAT/tests PASS; script import failure — 2026-11-27T05:30:03.805Z

- Full Run #238 `45946018320`, job `140330785714`, exact head `0b24e86bedfab9c63a72d1d724562b1e0fa3237f` logs confirm all 67 unit tests passed, including `test_compositional_sat_proofs_and_heap_audit` and all three negative tamper tests (partial-product polarity, compressor carry weight, output bit). Python `compileall` also passed. The compositional proof unit test completed successfully; its observed test interval was approximately 0.075 s (from log timestamps), which includes audit and all four SAT lemmas. Exact per-lemma timings were not emitted in the unit-test log and remain to be recorded from the benchmark artifact.
- Benchmark step failed immediately before entering the benchmark: `ModuleNotFoundError: No module named 'orcus'` at `benchmarks/signed_int4_dot_product.py:20`. Running a file directly sets `sys.path[0]` to the `benchmarks` directory, so the repository-root namespace package `orcus` is not importable in that execution mode. This is a Python import-path integration issue, not a proof failure.
- Artifact upload and smoke verification were skipped. No six-variant synthesis, VCD, Nangate45, OpenSTA, stage timing, or PPA data exists from Run #238.
- Next: fix script execution import path robustly (add repository root to `sys.path` before importing `orcus.typed_heap`, or relocate the module under benchmarks with proper package/script import handling), rerun CI, capture exact lemma runtimes in artifact, and complete six-variant benchmark. Milestone #1 remains open pending artifact review.
- PR #19 remains open/unmerged. Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact.


## 97. Benchmark import-path fix committed — 2026-11-27T05:30:33.904Z

- Fixed direct-script import resolution on PR branch commit `1207088254ff02d24e8bcaf28e68379400153564` (parent `0b24e86bedfab9c63a72d1d724562b1e0fa3237f`). The benchmark script now adds the repository root (derived from `Path(__file__)`) to `sys.path` before importing `orcus.typed_heap`, so both package-based unit tests and direct CI script execution can resolve the module.
- Run #238 confirmed 67/67 unit tests pass, including all four compositional SAT lemmas and all three negative tamper tests. The compositional test interval from log timestamps was approximately 0.075 s including audit and SAT proofs; exact per-lemma timings were not logged. The benchmark itself failed at import before any benchmark stage ran.
- No Run #238 artifact, six-variant metrics, stage timings, VCD, or OpenSTA data. Next: sync latest main STATUS to branch, inspect fresh CI, then collect proof timings and benchmark artifact. No milestone closure yet.
- PR #19 remains open/unmerged; Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact.


## 98. PR #19 resynchronized after benchmark import fix — 2026-11-27T05:30:57.359Z

- Synced main STATUS blob from `a154f6bf770d9cfaf6b443ef829e589ff247f210` and main ancestry into PR branch with non-force two-parent merge commit `84635f54bdb885f6825d28c087687916d1072411`.
- Merge parents: benchmark import fix `1207088254ff02d24e8bcaf28e68379400153564` first; main `a154f6bf770d9cfaf6b443ef829e589ff247f210` second. Branch update succeeded with expected-head protection.
- New branch head should trigger PR CI. Run #238 remains failed at benchmark import; its unit tests and compositional proof suite passed. No six-variant artifact exists yet.
- Next: verify new run for exact head `84635f54bdb885f6825d28c087687916d1072411`; monitor benchmark and inspect artifact. PR #19 remains open/unmerged; Ceres untouched; NEM separate.


## 99. Benchmark import fix CI Run #240 started — 2026-11-27T05:31:12.048Z

- Automatic PR Run #240, ID `45946252250`, confirmed for exact head `84635f54bdb885f6825d28c087687916d1072411`; created `2026-11-27T05:30:55Z`; status `in_progress`.
- PR #19 remains open/unmerged; GitHub metadata still reports `mergeable=false`. STATUS sync and branch ancestry have not made GitHub report true mergeability.
- Run #238 unit tests and compositional SAT proof test passed; benchmark failed only because direct script could not import `orcus`. Run #240 includes repository-root import-path correction. No new result yet.
- Next: poll Run #240; verify unit tests, benchmark execution, artifact upload, six variants, 512 unique vectors, VCD annotation, raw OpenSTA data, and measured proof timings. Milestone #1 remains open.


## 100. Run #240 setup progress — 2026-11-27T05:31:23.556Z

- Run #240 `45946252250`, job `140331518211`, exact head `84635f54bdb885f6825d28c087687916d1072411` is `in_progress`. Setup, checkout, Python setup passed; dependency installation step 4 active. Unit tests and benchmark pending.
- No new proof runtime, artifact, or PPA evidence. Continue monitoring.


## 101. Run #240 dependency install poll — 2026-11-27T05:31:33.699Z

- Run #240 `45946252250`, job `140331518211`, remains `in_progress`; dependency installation step 4 is still active. Unit tests and benchmark have not started. No new evidence.


## 102. Run #240 benchmark stage active — 2026-11-27T05:31:45.061Z

- Run #240 `45946252250`, job `140331518211`, exact head `84635f54bdb885f6825d28c087687916d1072411`: setup/dependencies/cache/OpenSTA verification passed; all unit tests passed; Python compileall passed; Nangate45 Liberty fetch passed. Benchmark step 12 is now `in_progress`; artifact upload and smoke verification pending.
- This is the first run to reach the benchmark after the typed heap proof unit test passed and the script import-path fix landed. No benchmark metrics/artifact are available until the stage completes.


## 103. Run #240 baseline equivalence failure — 2026-11-27T05:32:14.624Z

- Run #240 `45946252250`, job `140331518211`, exact head `84635f54bdb885f6825d28c087687916d1072411` failed during benchmark step 12, before the fused variant was reached. Unit tests (67/67), compileall, and Liberty retrieval passed.
- Benchmark progression: direct variant passed formal, generic synthesis, mapping, 512/512 unique vectors, VCD/OpenSTA (area 574.56, delay 0.95 ns, total power 105.0206 µW; 259 annotated pins); left-deep variant passed the same stages (area 574.56, delay 0.95 ns, total power 105.0206 µW; 259 annotated pins). The run then failed formal verification for `balanced_01_23`.
- Exact Yosys failure: `equiv_status -assert` reported 28 unproven equivalence cells after `equiv_struct -icells` structurally matched inappropriate internal nodes (log examples matched gold adder output bits to `p0_gold[7]`). This is an internal partition/cutpoint matching failure in the baseline variant, not a fused Baugh-Wooley counterexample. No fused benchmark or artifact was produced; no artifact upload.
- The compositional proof test did pass in the unit suite. Its log interval was approximately 0.0756 s (from timestamps 05:29:12.4003378Z to 05:29:12.4759235Z), including four Yosys SAT lemmas and graph audit. This is a unit-test wall interval, not a per-lemma runtime breakdown. The three tamper tests all passed.
- Next: inspect the baseline equivalence flow and remove/avoid unsafe structural matching for the product-level variants (e.g. test `equiv_simple` without `equiv_struct` or use a sound full-output miter); preserve fail-closed behavior. Then rerun CI. Do not change the fused proof or declare benchmark complete based on the two early variants.
- PR #19 remains open/unmerged; GitHub last reported `mergeable=false`. Milestone #1 open; Milestone #2 blocked. Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact.


## 104. Baseline equivalence cutpoint fix committed — 2026-11-27T05:32:51.959Z

- Changed the non-fused product-level variants to run Yosys `equiv_make` + `equiv_simple` + `equiv_status -assert` without `equiv_struct -icells` on PR branch commit `412efcd85f857e231dd76d78354d827a9a35dcdc` (parent `84635f54bdb885f6825d28c087687916d1072411`). This avoids the unsafe structural internal cutpoint matches observed in Run #240 for balanced_01_23. It retains full-output fail-closed equivalence checking; no proof is assumed until CI verifies it.
- Run #240 `45946252250` remains failed before fused variant. Direct and left-deep early metrics recorded in section 103. Compositional proof unit test and all tamper tests passed; benchmark artifact absent.
- Next: sync current main STATUS to branch and trigger fresh CI. Verify non-structural baseline formal for all first five variants, then fused compositional SAT/audit, then six-variant PPA artifact. No claim of milestone completion yet.
- PR #19 open/unmerged; Ceres untouched; NEM distinct; baseline intact.


## 105. PR #19 resynchronized after baseline proof adjustment — 2026-11-27T05:33:16.547Z

- Synced main STATUS blob from `03cf8e6b5703dfa8b8975b6b61f9ccaf782a859e` and main ancestry into branch with non-force two-parent merge commit `af312625e5ec34b01dc2df227ec3dc6261ff6ef3`.
- Merge parents: non-structural baseline equivalence change `412efcd85f857e231dd76d78354d827a9a35dcdc` first; main `03cf8e6b5703dfa8b8975b6b61f9ccaf782a859e` second. Branch ref update succeeded with expected-head protection.
- New branch head should trigger PR CI. Run #240 remains failed on prior head; preserved. No fused benchmark artifact yet.
- Next: verify new run and validate the non-structural equivalence method for all five baselines and the compositional proof for fused. PR #19 remains open/unmerged.


## 106. Baseline proof adjustment CI Run #242 started — 2026-11-27T05:33:29.455Z

- Automatic PR Run #242, ID `45946483363`, confirmed for exact head `af312625e5ec34b01dc2df227ec3dc6261ff6ef3`; created `2026-11-27T05:33:13Z`; status `in_progress`.
- This run includes non-structural equivalence for the five product-level baselines and the compositional fused proof. No results yet; prior Run #240 failure preserved.
- Next: monitor unit tests, all baseline formal checks, fused compositional SAT, and benchmark artifact. PR #19 remains open/unmerged.


## 107. Run #242 setup progress — 2026-11-27T05:33:42.713Z

- Run #242 `45946483363`, job `140332240921`, exact head `af312625e5ec34b01dc2df227ec3dc6261ff6ef3` remains `in_progress`. Setup, checkout, Python setup passed; dependency installation step 4 active. No unit-test or benchmark result yet.


## 108. Run #242 benchmark active — 2026-11-27T05:33:56.613Z

- Run #242 `45946483363`, job `140332240921`, exact head `af312625e5ec34b01dc2df227ec3dc6261ff6ef3`: setup/dependencies/cache/OpenSTA verification passed; unit tests passed; Python compileall passed; Liberty fetch passed. Benchmark step 12 is active. Artifact upload and smoke check pending.
- No new metrics/artifact yet. The changed non-structural baseline proof path has passed the unit suite; the six-variant benchmark is the next evidence gate.


## 109. Run #242 benchmark and CI succeeded — 2026-11-27T05:34:15.733Z

- Run #242 `45946483363`, job `140332240921`, exact head `af312625e5ec34b01dc2df227ec3dc6261ff6ef3` completed successfully. Unit tests, Python compileall, Liberty fetch, six-variant benchmark, artifact upload, and benchmark smoke verification all passed.
- This is the first successful end-to-end CI after typed heap integration, script import correction, and non-structural baseline proof correction. Artifact and full logs still need inspection before recording per-variant proof timings, vector/VCD evidence, raw OpenSTA components, and final metrics.
- Next: fetch and inspect artifact ZIP and complete job logs. Confirm all six variants' proof methods/results, 512 unique vectors, nonzero annotation counts, stage timings, and complete area/delay/power table. Do not close Milestone #1 until the artifact itself is validated.
- PR #19 remains open/unmerged. Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact.


## 110. Run #242 artifact audited — six-variant results verified — 2026-11-27T05:36:52.412Z

- Read main STATUS before this audit. Run #242 ID `45946483363`, job `140332240921`, head `af312625e5ec34b01dc2df227ec3dc6261ff6ef3` completed success. Artifact `orcus-signed-int4-dot-product`, ID `15174982131`, size 11,828 bytes, SHA-256 `3c766caabafd71763aa4f225f9b330405b2379e01e58ea2ef764abf63d5ebd5a`, downloaded and parsed from `orcus-int4-dot-product.json`.
- All six variants report `formal-pass`, exactly 512 vectors and 512 unique vectors, VCD bit toggles >0, OpenSTA status completed, positive annotation count, and a raw report with a Total power row. Raw report Watts values match the structured µW fields.

### Verified six-variant comparison (Run #242)

| Variant | Proof method & result | Generic cells | Nangate45 area | OpenSTA delay (ns) | Internal (µW) | Switching (µW) | Leakage (µW) | Total (µW) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Direct | Yosys `equiv_make/equiv_simple/equiv_status -assert` PASS | 522 | 574.56 | 0.95 | 47.88638 | 43.71745 | 13.41678 | 105.02060 |
| Left-deep | Yosys `equiv_make/equiv_simple/equiv_status -assert` PASS | 522 | 574.56 | 0.95 | 47.88638 | 43.71745 | 13.41678 | 105.02060 |
| Balanced 01/23 | Yosys `equiv_make/equiv_simple/equiv_status -assert` PASS | 522 | 575.89 | 1.00 | 47.84778 | 43.61467 | 13.42982 | 104.89230 |
| Balanced 02/13 | Yosys `equiv_make/equiv_simple/equiv_status -assert` PASS | 522 | 574.56 | 1.00 | 47.83237 | 43.72201 | 13.40231 | 104.95670 |
| Two-stage carry-save | Yosys `equiv_make/equiv_simple/equiv_status -assert` PASS | 441 | 460.712 | 0.89 | 39.53044 | 34.28274 | 10.79658 | 84.60975 |
| Fused Baugh-Wooley | Four Yosys SAT lemmas + typed heap audit PASS | 395 | 414.694 | 1.07 | 34.66065 | 30.57532 | 9.737028 | 74.97300 |

- Fused Baugh-Wooley vs two-stage carry-save: generic cells -10.43%; Nangate45 area -9.99%; delay **+20.22% slower** (1.07 vs 0.89 ns); internal power -12.32%; switching power -10.81%; leakage -9.81%; total power -11.39%. Conclusion: fused Baugh-Wooley wins on mapped area, generic cells, and estimated power, but loses on critical-path delay. This is a trade-off, not an across-the-board win.
- All results are pre-layout Nangate45 research-library estimates without routed parasitics; not silicon PPA or FPGA results.

### Compositional proof evidence

- Fused formal stage total: 0.084973196 s. SAT lemmas: 10-bit Baugh-Wooley lane identity 0.049390187 s PASS; full-adder weighted-sum invariant 0.012656306 s PASS; half-adder weighted-sum invariant 0.010222454 s PASS; final 10-bit modulo CPA 0.010578794 s PASS. Independent graph audit 0.000808579 s PASS.
- Fused manifest: schema `orcus-typed-bit-heap-v1`; 4 lanes; 80 initial bits (64 partial products + 16 bias bits); 62 full-adder nodes; 3 top-column carries explicitly truncated modulo 2^10; two final rows. **No half-adder nodes were instantiated in this reduction graph**; the half-adder primitive equation was formally proven as a reusable lemma. This distinction must remain explicit.
- All three negative tamper unit tests passed: Baugh-Wooley partial-product polarity flip rejected; compressor carry-weight misroute rejected; final output-bit flip rejected. Unit suite 67/67 passed; Python compileall passed; benchmark smoke check passed.

### Stage timings (seconds)

| Variant | Formal | Generic synth | Nangate45 map | Simulation | OpenSTA | Total |
|---|---:|---:|---:|---:|---:|---:|
| Direct | 0.040025 | 0.279115 | 0.612835 | 0.065926 | 0.311177 | 1.313782 |
| Left-deep | 0.043948 | 0.270443 | 0.605340 | 0.067915 | 0.250756 | 1.242482 |
| Balanced 01/23 | 0.041219 | 0.268807 | 0.596766 | 0.066628 | 0.249609 | 1.227115 |
| Balanced 02/13 | 0.088969 | 0.268592 | 0.579151 | 0.066791 | 0.250899 | 1.258457 |
| Carry-save | 0.059779 | 0.268403 | 0.541890 | 0.071516 | 0.253682 | 1.199356 |
| Fused Baugh-Wooley | 0.084973 | 0.481899 | 0.766629 | 0.132259 | 0.250368 | 1.720107 |

- VCD toggle totals / OpenSTA annotated pins: direct 39,190 / 259; left-deep 44,381 / 259; balanced 01/23 44,347 / 259; balanced 02/13 44,230 / 259; carry-save 48,552 / 268; fused 61,859 / 292. Each variant: 512/512 unique xorshift32 vectors.
- Raw OpenSTA report inspection confirmed the per-variant Total row and annotated pin count; all four raw power components agree with artifact fields.

### Current disposition and next work

- Four-lane compositional proof and six-variant benchmark are now evidenced for this Run #242 source. However, before formally closing Milestone #1, decide whether the graph should instantiate at least one half-adder node (currently the half-adder primitive is proven but graph uses 62 FAs and zero HAs). If no HA is needed by the chosen reduction schedule, retain this as an explicit documented design choice rather than imply HA node coverage.
- PR #19 remains open and unmerged. Latest prior GitHub metadata still reported `mergeable=false`; recheck after syncing current STATUS/ancestry. Do not merge without explicit user authorization.
- Milestone #2 remains gated on reviewing/closing Milestone #1. Next scaling: 8 lanes / 11-bit, 16 lanes / 12-bit, 32 lanes / 13-bit; compare direct, multi-stage carry-save, and fused Baugh-Wooley with compositional proof, 512 unique vectors, nonzero VCD annotation, raw OpenSTA and per-stage timing.
- Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact.


## 111. Half-adder graph enhancement attempt — no branch mutation — 2026-11-27T05:37:50.211Z

- After auditing Run #242, identified a remaining spec nuance: the fused heap manifest currently contains 62 full-adder nodes and zero instantiated half-adder nodes, although the half-adder primitive SAT lemma passes. Planned to instantiate one explicit low-column HA node to fully exercise both typed node kinds.
- The GitHub write orchestration returned a remote protocol disconnect before a branch update was confirmed. Re-read the PR branch ref and `orcus/typed_heap.py`: branch remains `af312625e5ec34b01dc2df227ec3dc6261ff6ef3`; no HA source changes landed. No new CI run was triggered. Run #242 artifact and metrics remain valid for that exact source head.
- Next: retry the HA-node patch in smaller, independently confirmed operations, then rerun tests and benchmark if implemented. Do not describe the current graph as containing HA nodes. PR #19 remains open/unmerged; Ceres untouched; NEM distinct.


## 112. Explicit half-adder graph node committed — 2026-11-27T05:38:51.102Z

- Added an actual 2:2 half-adder node to the typed heap on PR branch commit `df08d3a0259817204a7d7ca348d06a65f5edef2e` (parent `af312625e5ec34b01dc2df227ec3dc6261ff6ef3`). The deterministic schedule compresses the two remaining low-column bits with `ha_s_0 = a ^ b` and `ha_c_0 = a & b`, routing carry to column 1. The audit now parses and validates both FA and HA node arities/equations; unit test asserts an HA node exists.
- This preserves the weighted sum exactly and leaves modulo top-column truncation unchanged. The half-adder primitive SAT lemma already passed in Run #242; however, this graph change has not yet been tested or benchmarked. Run #242 artifact applies to the prior source head and must not be represented as measurements for this changed graph.
- Next: sync latest main STATUS/ancestry to branch, run CI, verify the HA graph node and all tamper tests, then audit the new six-variant artifact. If all proof/benchmark gates pass, update the final comparison using the new source head. Prior Run #242 remains a valid historical result for its own head.
- PR #19 remains open/unmerged. Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact.


## 113. PR #19 resynchronized after explicit HA node — 2026-11-27T05:39:21.659Z

- Synced latest main STATUS blob and ancestry from `81ff20e9123cf4d48ea2746f5885172e1e832632` into PR branch using non-force two-parent merge commit `70949ed253e849453aaa0542d6f102a0130b81de`.
- Merge parents: HA-node source commit `df08d3a0259817204a7d7ca348d06a65f5edef2e` first, main `81ff20e9123cf4d48ea2746f5885172e1e832632` second. Expected-head-protected update succeeded.
- This new branch head should trigger CI for the explicit FA+HA graph. Run #242 remains the historical six-variant result for its previous source head; new HA-graph results are pending.
- Next: inspect Actions listing for exact head `70949ed253e849453aaa0542d6f102a0130b81de`; verify SAT lemmas, graph audit, three tamper tests, and fresh benchmark. PR #19 remains open/unmerged.


## 114. Explicit FA+HA graph CI Run #244 started — 2026-11-27T05:39:41.772Z

- Automatic PR Run #244, ID `45947084195`, confirmed for exact branch head `70949ed253e849453aaa0542d6f102a0130b81de`; created `2026-11-27T05:39:16Z`; status `in_progress`.
- PR #19 remains open/unmerged; GitHub still reports `mergeable=false` after the latest STATUS ancestry sync. No merge.
- This run validates the explicit half-adder graph node added after Run #242. No result or metrics for the changed source yet.
- Next: monitor unit tests and benchmark; if successful, inspect the new manifest HA count, all proof lemmas, tamper tests, and full artifact.


## 115. Run #244 unit tests passed; benchmark active — 2026-11-27T05:39:59.337Z

- Run #244 `45947084195`, job `140334145107`, exact head `70949ed253e849453aaa0542d6f102a0130b81de`: dependency/cache/OpenSTA checks passed; unit tests passed; Python compileall passed; Liberty fetch passed. Benchmark step 12 is active; artifact upload and smoke verification pending.
- This confirms the new test asserting an actual half-adder node is present passes in CI. Full benchmark/proof timings and HA-node artifact inspection remain pending.


## 116. Run #244 full CI succeeded — artifact audit pending — 2026-11-27T05:40:17.148Z

- Run #244 `45947084195`, job `140334145107`, exact head `70949ed253e849453aaa0542d6f102a0130b81de` completed success. Unit tests, compileall, Liberty fetch, benchmark, artifact upload, and smoke verification all passed.
- This is the first end-to-end CI for the typed graph with an actual HA node. Artifact ID, proof timings, six-variant table, vector/VCD and raw OpenSTA checks are pending inspection.
- Next: fetch artifact and complete job logs; verify HA node count and all proof/measurement evidence. Do not close Milestone #1 before that audit.


## 117. Run #244 final artifact audit — typed FA+HA graph verified — 2026-11-27T05:41:41.603Z

- Run #244 ID `45947084195`, job `140334145107`, exact source head `70949ed253e849453aaa0542d6f102a0130b81de` completed success. Unit tests, compileall, benchmark, artifact upload, and smoke verification all passed.
- Artifact `orcus-signed-int4-dot-product`, ID `15175157667`, size 11,862 bytes, SHA-256 `fe7c1d91565bf32efb765deda7362ed839563dbdc84cc7101dba8c692ec952ae`. Downloaded ZIP `orcus-run244.zip`; parsed `orcus-int4-dot-product.json`; inspected all six raw OpenSTA reports.
- All six variants: formal `formal-pass`; 512 vectors / 512 unique vectors; nonzero VCD bit toggles; OpenSTA status completed; raw report Total row present; raw report annotation count matches structured count; raw Watts components agree with µW fields.

### Run #244 six-variant comparison

| Variant | Proof method & result | Generic cells | Nangate45 area | OpenSTA delay (ns) | Internal (µW) | Switching (µW) | Leakage (µW) | Total (µW) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Direct | Yosys `equiv_make/equiv_simple/equiv_status -assert` PASS | 522 | 574.56 | 0.95 | 47.88638 | 43.71745 | 13.41678 | 105.02060 |
| Left-deep | Yosys `equiv_make/equiv_simple/equiv_status -assert` PASS | 522 | 574.56 | 0.95 | 47.88638 | 43.71745 | 13.41678 | 105.02060 |
| Balanced 01/23 | Yosys `equiv_make/equiv_simple/equiv_status -assert` PASS | 522 | 575.89 | 1.00 | 47.84778 | 43.61467 | 13.42982 | 104.89230 |
| Balanced 02/13 | Yosys `equiv_make/equiv_simple/equiv_status -assert` PASS | 522 | 574.56 | 1.00 | 47.83237 | 43.72201 | 13.40231 | 104.95670 |
| Two-stage carry-save | Yosys `equiv_make/equiv_simple/equiv_status -assert` PASS | 441 | 460.712 | 0.89 | 39.53044 | 34.28274 | 10.79658 | 84.60975 |
| Fused Baugh-Wooley | Four Yosys SAT lemmas + independent typed heap audit PASS | 394 | 413.896 | 1.13 | 34.83456 | 29.71045 | 9.696306 | 74.24132 |

- Fused Baugh-Wooley vs two-stage carry-save: generic cells -10.66%; area -10.16%; delay **26.97% slower** (1.13 vs 0.89 ns); internal power -11.88%; switching -13.34%; leakage -10.19%; total power -12.25%. It wins area and estimated power, loses critical-path delay. This is a workload-specific trade-off, not an across-the-board win.
- All area/delay/power results are pre-layout Nangate45 research-library estimates without routed parasitics; not silicon PPA or FPGA measurements.

### Compositional proof and typed heap details

- Fused formal stage: 0.068571907 s total. SAT lemmas: exact 10-bit signed Baugh-Wooley lane identity 0.039270713 s PASS; full-adder weighted-sum invariant 0.010122810 s PASS; half-adder weighted-sum invariant 0.008943286 s PASS; final 10-bit modulo CPA equivalence 0.008460941 s PASS. Independent graph audit 0.000673071 s PASS.
- Manifest: `orcus-typed-bit-heap-v1`; 4 lanes; 80 initial bits (64 partial products + 16 per-lane bias bits); 62 full-adder nodes + 1 half-adder node; 63 total compressor nodes; 2 final rows; 3 top-column carries explicitly truncated modulo 2^10. The HA is instantiated at column 0 and its carry routes to column 1. The 10-bit per-lane bias is `0x390` (8-bit correction `0x90` plus sign-extension contribution at bits 8 and 9).
- Negative tamper tests all passed: flipped Baugh-Wooley partial-product polarity rejected; misrouted compressor carry column rejected; flipped final output bit rejected. Unit suite 67/67 passed; compileall passed.

### Run #244 stage timings (seconds)

| Variant | Formal | Generic synth | Nangate45 map | Simulation | OpenSTA | Total |
|---|---:|---:|---:|---:|---:|---:|
| Direct | 0.032438 | 0.217430 | 0.494439 | 0.052277 | 0.233670 | 1.034568 |
| Left-deep | 0.031868 | 0.210467 | 0.496385 | 0.058431 | 0.195916 | 0.996746 |
| Balanced 01/23 | 0.033843 | 0.211095 | 0.492675 | 0.053144 | 0.197908 | 0.992389 |
| Balanced 02/13 | 0.074006 | 0.211755 | 0.471458 | 0.053551 | 0.197061 | 1.011561 |
| Carry-save | 0.049131 | 0.207786 | 0.438861 | 0.057318 | 0.194496 | 0.951315 |
| Fused Baugh-Wooley | 0.068572 | 0.372322 | 0.607777 | 0.102236 | 0.197589 | 1.352221 |

- VCD toggle totals / annotated pins: direct 39,190 / 259; left-deep 44,381 / 259; balanced 01/23 44,347 / 259; balanced 02/13 44,230 / 259; carry-save 48,552 / 268; fused 62,096 / 284. All are 512/512 unique xorshift32 vectors.

### Milestone status

- The eight requested implementation elements are now implemented and verified for the four-lane design: typed weighted heap including FA and HA nodes; RTL + machine-readable manifest; lane identity SAT; FA/HA SAT; modulo CPA SAT; independent weight/fanout/dangling/top-truncation audit; three negative tamper tests; branch STATUS sync and CI trigger.
- Milestone #1 technical evidence is complete for Run #244. PR #19 remains open/unmerged pending review and explicit merge authorization. Latest GitHub metadata before the next sync still reported `mergeable=false`; recheck after syncing the latest main STATUS/ancestry.
- Milestone #2 can now be planned/started after PR #19 review: 8 lanes/11-bit accumulator, 16 lanes/12-bit, 32 lanes/13-bit; compare direct, multi-stage carry-save, and fused Baugh-Wooley with formal proofs, deterministic 512 unique vectors, VCD annotation, raw OpenSTA, and stage timings. Do not assume sub-second proof at larger widths; measure it.
- Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact.


## 118. Final Run #244 evidence synchronized to PR branch — 2026-11-27T05:42:13.125Z

- Synced final main STATUS blob from `c0e153e2cb7e24c9ca90344528711287e8b5164c` and main ancestry into PR branch using non-force two-parent merge commit `50afab04361308c74254d5466e0d6c0b1638ffae`.
- Merge parents: verified FA+HA implementation source `df08d3a0259817204a7d7ca348d06a65f5edef2e` first; main `c0e153e2cb7e24c9ca90344528711287e8b5164c` second. Expected-head-protected update succeeded.
- The synced branch now contains the Run #244 final artifact audit and full six-variant comparison in STATUS. This STATUS-only merge may trigger another PR workflow; Run #244 remains the verified implementation/benchmark run for the pre-sync source tree.
- Next: recheck PR #19 mergeability and latest branch head. Do not merge without explicit authorization. Milestone #1 technical evidence complete; Milestone #2 planning may proceed, with scaling proof runtimes measured rather than assumed.


## 119. Final PR #19 mergeability and CI confirmation — 2026-11-27T05:43:33.068Z

- Raw GitHub PR API for PR #19 reports `mergeable=true`, `mergeable_state=clean`, base `c0e153e2cb7e24c9ca90344528711287e8b5164c`, head `50afab04361308c74254d5466e0d6c0b1638ffae`. The simplified PR metadata wrapper had returned stale `false`; raw API is authoritative and shows clean/mergeable. PR remains open and unmerged.
- STATUS/ancestry sync commit `50afab04361308c74254d5466e0d6c0b1638ffae` triggered Run #245, ID `45947359445`, exact head `50afab04361308c74254d5466e0d6c0b1638ffae`; Run #245 completed success. All 14 workflow steps including unit tests, compileall, benchmark, artifact upload, and smoke verification passed.
- Run #244 artifact remains the fully audited measurement source for the FA+HA graph. Run #245 is the post-sync CI confirmation. No PR merge was performed; explicit user authorization is still required.
- Milestone #1 four-lane proof and benchmark evidence complete. Milestone #2 may proceed as a separate scaling research milestone: 8 lanes/11-bit accumulator, 16 lanes/12-bit, 32 lanes/13-bit. Revalidate formal lemmas and graph invariants at each width; benchmark actual runtimes rather than assume they stay sub-second. Compare direct, multi-stage carry-save, and fused Baugh-Wooley.
- Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact.


## 120. Final mergeability recheck — 2026-11-27T05:44:18.228Z

- Rechecked raw GitHub API after a transient `mergeable=null / mergeable_state=unknown` response. Latest raw PR #19 response now reports `mergeable=true`, `mergeable_state=clean`, head `50afab04361308c74254d5466e0d6c0b1638ffae`; main ref at this check was `559863dd99d3ca2067a6d7e1fc79567909bd7e1e`. PR remains open/unmerged.
- Run #245 `45947359445` completed success on the exact synced branch head and uploaded artifact ID `15174839413`. Run #244 `45947084195` artifact ID `15175157667` remains the fully audited evidence source for the actual FA+HA implementation; its complete six-variant metrics and raw OpenSTA reports are recorded in section 117.
- Final four-lane Milestone #1 evidence is complete. No merge performed. Next work is Milestone #2 scaling (8/11-bit, 16/12-bit, 32/13-bit) as a separate research phase, after explicit authorization to proceed if repository work is to be started.
- Ceres untouched; NEM distinct; ORCUS v0.2 baseline intact.


## 121. PR #19 pre-merge inspection tool-schema failure — 2026-11-27T05:49:12.484Z

- Attempted pre-merge comparison/diff inspection. The compare API request was accepted, but the diff wrapper rejected the argument key `repository_full_name`; its actual schema requires `repo_full_name`. No repository mutation or merge occurred.
- Main remains `331693af60e2535867a12e620eb14057eee8b43a`; PR #19 remains open at `50afab04361308c74254d5466e0d6c0b1638ffae`. Retry inspection using the exact schema, then merge only after confirming base/head relationship and current clean state.


## 122. PR #19 pre-merge comparison endpoint rejected — 2026-11-27T05:49:28.017Z

- Retried PR diff with the correct `repo_full_name` argument. GitHub connector rejected one of the concurrent fetch requests as an unsupported public endpoint (HTTP 400); no diff was obtained and no repository mutation occurred.
- Main is now at the status-only commit `3dec130b508de87a9a7b7d59ec79e129b9467964`; PR #19 branch head remains `50afab04361308c74254d5466e0d6c0b1638ffae`. Continue with supported PR metadata/patch tools and compare API endpoint if accessible; do not infer merge-base cleanliness from earlier metadata alone.


## 123. PR #19 merge preflight — 2026-11-27T05:49:53.856Z

- Read current main STATUS first. Current main `73163fa034bd8e9bfd193dc0fa1a8612035d299a`; PR branch `50afab04361308c74254d5466e0d6c0b1638ffae`; PR #19 open/unmerged. The PR patch changes exactly three files: `benchmarks/signed_int4_dot_product.py`, new `orcus/typed_heap.py`, and `tests/test_signed_int4_dot_product.py`; no Ceres paths appear.
- PR metadata reports mergeable false because main has advanced with STATUS-only commits. The branch's STATUS is stale relative to main. Next step: construct a non-force two-parent sync commit with latest main as second parent and latest main STATUS blob in the branch tree, then recheck mergeability and CI before merging.
- Patch inspection confirms the current fused generator is parameterized only by a `lanes` argument at generation level but hardcodes 10-bit width and its proof/benchmark harness is four-lane-specific. Milestone #2 must separately derive accumulator width and prove generalized lane scaling; do not assume simply changing the lane count is sufficient.
- No merge or Milestone #2 implementation has occurred yet. Ceres remains untouched; NEM distinct.


## 124. PR #19 branch synced to latest main ancestry — 2026-11-27T05:50:20.790Z

- Synced current main `696f169d437a0997892e8cadc084ce439426fb85` and its latest STATUS blob into PR branch using a non-force two-parent commit `934e94addbda390ab56571eeca565d75dbd0fcc6`.
- Parents: original PR branch head `50afab04361308c74254d5466e0d6c0b1638ffae` first; main `696f169d437a0997892e8cadc084ce439426fb85` second. Ref update succeeded with expected-head protection. No source changes were made in this sync.
- Next: check raw PR metadata and exact-head CI. If clean and green, merge PR #19 with expected head `934e94addbda390ab56571eeca565d75dbd0fcc6`, then verify merge commit and update STATUS.


## 125. PR #19 resync CI Run #246 started — 2026-11-27T05:50:44.164Z

- Non-force ancestry/STATUS sync commit `934e94addbda390ab56571eeca565d75dbd0fcc6` triggered PR Run #246, ID `45948158005`, exact head `934e94addbda390ab56571eeca565d75dbd0fcc6`; created `2026-11-27T05:50:17Z`; status `in_progress`.
- PR #19 is open/unmerged. Raw API currently reports `mergeable=null`, `mergeable_state=unknown` while GitHub recalculates; base `696f169d437a0997892e8cadc084ce439426fb85`, head as above.
- Wait for exact-head CI and mergeability calculation before merging PR #19. No Milestone #2 branch yet.


## 126. PR #19 Run #246 dependency build active — 2026-11-27T05:51:01.910Z

- Run #246 `45948158005`, job `140337533817`, exact head `934e94addbda390ab56571eeca565d75dbd0fcc6`: checkout and Python setup passed; dependency installation/build stage is active. Unit tests, compileall, Liberty fetch, benchmark, artifact upload, and smoke verification remain pending.
- No merge yet. Continue monitoring exact-head CI and then recheck raw PR mergeability. PR #19 remains open/unmerged.


## 127. PR #19 Run #246 tests passed; benchmark active — 2026-11-27T05:51:17.913Z

- Run #246 `45948158005`, job `140337533817`, exact head `934e94addbda390ab56571eeca565d75dbd0fcc6`: dependency setup/cache/OpenSTA verification passed; all unit tests passed; compileall passed; Nangate45 Liberty fetch passed. Benchmark step 12 is currently running; artifact upload and final smoke verification pending.
- GitHub PR mergeability remains temporarily `null/unknown` during recalculation. Do not merge until the exact-head workflow completes and PR API reports clean/mergeable.


## 128. PR #19 Run #246 completed successfully — 2026-11-27T05:51:39.110Z

- Run #246 ID `45948158005`, job `140337533817`, exact head `934e94addbda390ab56571eeca565d75dbd0fcc6` completed with conclusion `success`. All 14 substantive workflow steps passed, including unit tests, compileall, Liberty fetch, benchmark, artifact upload, and smoke verification.
- PR #19 raw API still temporarily reports `mergeable=null`, `mergeable_state=unknown`; base `696f169d437a0997892e8cadc084ce439426fb85`, head `934e94addbda390ab56571eeca565d75dbd0fcc6`. No merge attempted while GitHub recalculates. Next: inspect final artifact and recheck mergeability, then merge using expected head.


## 129. PR #19 Run #246 artifact recorded — 2026-11-27T05:51:59.586Z

- Run #246 `45948158005` artifact `orcus-signed-int4-dot-product`, artifact ID `15175189288`, size 11,859 bytes, SHA-256 `2ec1e8e4ca8851f578a5f3a4f43d0c9170e71994fc43dde1fc50e4b21b491ca5`. Artifact belongs to exact branch head `934e94addbda390ab56571eeca565d75dbd0fcc6`.
- Run #246 completed success; all workflow stages passed. This revalidates PR #19 branch after main ancestry/STATUS sync. The artifact has not been downloaded/parsed in this turn; previous fully parsed Run #244 artifact remains detailed in section 117.
- Raw PR API continues to return `mergeable=null / unknown` despite CI success. The PR is explicitly authorized by the user for merge. Next attempt GitHub merge endpoint with expected head; if GitHub refuses, preserve the failure and resolve the reported blocker rather than bypass protections.


## 130. Milestone #1 closed — PR #19 merged as ORCUS v0.3 — 2026-11-27T05:52:22.009Z

- GitHub merge endpoint succeeded for PR #19 using merge commit method and expected head `934e94addbda390ab56571eeca565d75dbd0fcc6`.
- Merge commit SHA: `35207adff3371fcadae68cbaa58181267c361359`. PR #19 is merged. This closes Milestone #1 and locks the verified four-lane typed fused Baugh-Wooley implementation into main as ORCUS v0.3.
- Run #246 `45948158005` passed on the exact pre-merge PR head; artifact ID `15175189288`. Earlier full six-variant artifact audit and compositional proof details remain recorded in section 117. Main status must now be fetched again after this commit; next action is to create Milestone #2 branch from the merged main head and implement 8/16/32 lane scaling.
- No Ceres files or branches were accessed. NEM remains distinct. ORCUS v0.2 baseline remains in history.


## 131. Milestone #2 repository discovery path miss — 2026-11-27T05:52:45.769Z

- After PR #19 merge, attempted to fetch the presumed workflow path `.github/workflows/orcus-signed-int4-dot-product.yml`; GitHub returned 404. No repository mutation occurred. Do not assume that workflow filename exists.
- Retry by listing the merged commit tree and inspect actual workflow paths before reading source files. Current known merge commit `35207adff3371fcadae68cbaa58181267c361359`; latest main status commit is `858247089e72e4c34ff273e81ed0f475303255d9`.


## 132. Milestone #2 source audit — parameterization gaps confirmed — 2026-11-27T05:53:37.296Z

- Re-read latest main STATUS and inspected merged ORCUS v0.3 tree. Actual workflow is `.github/workflows/ci.yml`; no separate signed-INT4 workflow exists.
- Confirmed current `orcus/typed_heap.py` is not yet lane-scalable: it hardcodes width 10, per-lane 10-bit bias `0x390`, 10-bit CPA, and the four-lane proof invocation `generate_fused_heap(4)`. Current benchmark `benchmarks/signed_int4_dot_product.py` hardcodes `LANES=4`, output width 10, and direct/carry-save trees with four named lanes. Tests explicitly assert all variants are 10-bit and the fused heap uses 4 lanes.
- Therefore Milestone #2 requires a separate parameterized implementation across width, proof harness, RTL baselines, vector generator, and report schema—not just passing a larger lane count. Need derive/validate exact W-bit Baugh-Wooley bias and signed extension for W=11/12/13 before coding. No Milestone #2 source changes yet.
- Main at audit time `1e8cca159413d9f0d26bf9502132397eff4602c6`; STATUS blob `aed8b8c6181e1e0e88e020f08920da6657c62caa`. Ceres untouched; NEM distinct.


## 133. Milestone #2 branch creation API limitation — 2026-11-27T05:53:57.032Z

- Attempted to create `research/orcus-int4-lane-scaling` by calling the Git ref update endpoint with a new branch name. GitHub returned HTTP 422 `Reference does not exist`; update_ref only updates existing refs and did not create the branch.
- No branch was created and no source changes occurred. Next: discover the dedicated create-reference action/schema, then create the branch at the latest main head using that action.


## 134. Dedicated branch-creation action discovered — 2026-11-27T05:54:17.976Z

- Discovered the repository connector's dedicated `create_branch` action. It requires `repository_full_name`, `branch_name`, and exactly one of `sha` or `base_ref`. The prior `update_ref` failure was expected because the branch did not exist.
- No branch or source changes yet. Next create `research/orcus-int4-lane-scaling` from latest main SHA, then inspect `.github/workflows/ci.yml` and parameterize the generator and benchmark.


## 135. Milestone #2 branch created — 2026-11-27T05:54:33.152Z

- Created `research/orcus-int4-lane-scaling` from main commit `d4a183525304ca1fe3a2912625925591d6e6201d` using the dedicated create-branch action.
- Branch currently contains only the merged ORCUS v0.3 baseline plus STATUS history; no scaling implementation committed yet. Next inspect CI workflow and exact source APIs, derive width-dependent Baugh-Wooley bias mathematically, then implement lane-parametric generators and tests.


## 137. Lane-scaling status-log formatting retry — 2026-11-27T05:56:15.805Z

- Attempted to append the source-audit/branch-sync record, but the JavaScript tool payload failed to parse before any GitHub write. No repository state changed. Retry with a simpler literal string and no mathematical escape sequences.

## 138. Lane-scaling branch synchronized and source audit complete — 2026-11-27T05:56:29.227Z

- Synced main 8a3e2c675363c09b9d3fcb82b316504db59a7c52 and its current STATUS blob into research/orcus-int4-lane-scaling via non-force two-parent commit 71fd77fb68aa4b900ed3c948604dd518847f12cd; expected-head update succeeded.
- Inspected .github/workflows/ci.yml: one ORCUS CI workflow runs unit tests, compileall, fetches Nangate45 Liberty, runs the signed INT4 benchmark with required tools and physical analysis, uploads artifact, and smoke-tests ORCUS.
- Scaling implementation plan: add separate orcus/lane_scaling.py and benchmarks/int4_lane_scaling.py to preserve the verified four-lane baseline. Target widths are W=11,12,13 for 8,16,32 lanes. Mathematical derivation: the complemented Baugh-Wooley partial-product matrix plus 0x90 equals signed product plus 2^8; therefore its W-bit sign-extended representation uses per-lane bias 2^W-112, specifically 0x790, 0xF90, and 0x1F90 for W=11,12,13. Prove this identity by SAT at each width.
- Compare direct, multi-stage carry-save, fused linear-column, and fused Dadda-scheduled variants. Retain the linear baseline. Each width requires lane identity SAT, FA/HA invariants, modulo-W CPA lemma, independent graph audit, Yosys equivalence for direct/carry-save, 512 unique deterministic vectors, VCD activity, Nangate45 mapping, OpenSTA timing/power, and stage timings. No scaling implementation committed yet.
- Ceres untouched; NEM distinct; ORCUS v0.3 is on main via PR #19 merge commit 35207adff3371fcadae68cbaa58181267c361359.

## 139. Parameterized scaling generator drafted — 2026-11-27T06:00:01.194Z

- Created an uncommitted Git blob for new module orcus/lane_scaling.py, blob SHA f40dd622f18301dbc03c1b7fb60dd97780745b41 (23,056 bytes). It implements supported lane targets 8/16/32; accumulator widths 11/12/13; derived per-lane bias 2^W-112; typed weighted heap; linear and Dadda compressor schedules; independent RTL/manifest graph audit; SAT lemmas for lane identity, FA, HA, and modulo-W CPA; Yosys equivalence helper for direct/CSA; and tamper helpers.
- No branch commit yet and no CI evidence. Next add scaling benchmark pipeline and tests, inspect implementation carefully, then commit to the research branch.

## 140. Scaling benchmark draft tool-payload syntax failure — 2026-11-27T06:01:19.033Z

- Attempted to create benchmarks/int4_lane_scaling.py, but the JavaScript payload failed to parse at the Verilog timescale directive because its backtick terminated the surrounding template literal. No GitHub blob or repository change was created.
- Retry with the Verilog timescale directive assembled without a literal backtick in the template string; then continue tests and workflow integration.

## 141. Scaling benchmark pipeline drafted — 2026-11-27T06:02:38.189Z

- Created uncommitted benchmark blob benchmarks/int4_lane_scaling.py, SHA 7c3ff788061b2d76794b963650b980c101c9d287 (12,855 bytes). It defines the 12-run matrix: 8/16/32 lanes × Direct / multi-stage carry-save / fused linear / fused Dadda; each run performs formal proof, generic synthesis, Nangate45 mapping, 512 unique xorshift32 vectors with simulation assertions, VCD toggle checks, OpenSTA timing and four-component power, and stage timing capture.
- Code review caught one packaging issue before commit: script must add repository root to sys.path before importing orcus.lane_scaling when invoked as a script from benchmarks/. Fix this before committing.
- No source commit or CI run yet. Ceres untouched; NEM distinct.

## 142. Scaling benchmark import-path fix drafted — 2026-11-27T06:02:57.708Z

- Retrieved benchmark draft blob 7c3ff788061b2d76794b963650b980c101c9d287, inserted repository-root sys.path setup before importing orcus, and created corrected blob 3752360638a608849239624bb2f70d3b98441caf (12,928 bytes).
- Corrected blob remains uncommitted. Next add focused tests for accumulator-width/bias derivation, graph audit at both schedules and all scales, tamper rejection, SAT lemmas, and Yosys direct/CSA equivalence.

## 143. Local arithmetic spot-check tool unavailable — 2026-11-27T06:04:51.534Z

- Attempted an independent Python truth-table spot check of the derived width-dependent Baugh-Wooley bias; the Python execution environment reset before running the script, so no result is claimed.
- The mathematical derivation remains: signed product = complemented-sign Baugh-Wooley weighted matrix - 112; therefore add 2^W-112 to represent the signed product modulo 2^W. The CI SAT lemma is the required verification gate for each target width.

## 144. Dadda stage-height correction drafted — 2026-11-27T06:05:30.809Z

- Reviewed the Dadda scheduler and corrected a substantive stage-height accounting bug: each stage must count both unconsumed work bits and sum outputs emitted into the next-stage column when enforcing its target height. New generator blob 231fdcb83bb418d606a3e759a8499f5013ebd4e4 includes that correction and retains separate stage buffers so sum outputs are not recursively recompressed in the same stage.
- This is an uncommitted draft. The Dadda schedule must still pass independent graph audits and CI tests before any delay comparison is reported.

## 145. CI workflow/test blob assembly variable error — 2026-11-27T06:06:05.906Z

- Attempted to create the lane-scaling test file and add the scaling benchmark/artifact steps to .github/workflows/ci.yml. The orchestration script referenced an undefined variable name while assembling the workflow patch, so execution stopped before either blob was created.
- No branch or source changes occurred. Retry the workflow insertion with the correct variable and then create both blobs.

## 146. Scaling tests and CI integration drafted — 2026-11-27T06:06:40.690Z

- Created uncommitted test blob tests/test_lane_scaling.py, SHA 7a66b82fe04a42b02c66bdc939b1c46e853579a2 (4,421 bytes). It covers exact 8/11, 16/12, 32/13 width/bias contracts; linear/Dadda graph audits; three negative tamper cases at all targets; 512 unique deterministic vectors; all six fused schedule/scale compositional SAT proofs; and direct/carry-save Yosys equivalence at all targets.
- Created uncommitted CI workflow blob .github/workflows/ci.yml, SHA 661175946b8b69f2324badd21eb544c1b7bd81a2 (3,998 bytes), adding required-tools/physical scaling benchmark execution and artifact upload.
- Source and tests remain uncommitted. Next assemble these blobs with corrected generator and benchmark into one non-destructive branch commit, sync main STATUS, then run PR CI.

## 147. Scaling implementation branch STATUS synchronized — 2026-11-27T06:07:11.024Z

- Synced main a667496d04a199db77a926dcaf921f65c7ba1d45 and latest STATUS into research/orcus-int4-lane-scaling via non-force two-parent commit cba32af72897fa20ca15eec3aa906353b0ea9b52. Parent order: prior branch head 71fd77fb68aa4b900ed3c948604dd518847f12cd first; main a667496d04a199db77a926dcaf921f65c7ba1d45 second. Expected-head update succeeded.
- Next create a single implementation commit adding lane_scaling.py, scaling benchmark, tests, and CI step. Then inspect exact branch files and CI logs; no measurement values should be filled until the new artifact is audited.

## 148. Milestone #2 initial implementation committed — 2026-11-27T06:07:44.154Z

- Committed scaling implementation on research/orcus-int4-lane-scaling: fbe204f3593bc45cb1342f2f440db1ac13f4a7b1 (parent cba32af72897fa20ca15eec3aa906353b0ea9b52).
- Added orcus/lane_scaling.py: target lane contracts 8/16/32 -> 11/12/13-bit accumulators; width-dependent Baugh-Wooley bias; typed heap generator with linear and staged Dadda reduction; independent RTL/manifest audit; SAT lane/FA/HA/CPA lemmas; direct/CSA Yosys equivalence; negative tamper helpers.
- Added benchmarks/int4_lane_scaling.py: 12-configuration benchmark matrix (3 lane counts × 4 architectures), formal proof, generic synthesis, Nangate45 mapping, deterministic 512 unique xorshift32 vectors with per-vector expected-value assertions, VCD activity, OpenSTA timing and internal/switching/leakage/total power, and stage timing capture.
- Added tests/test_lane_scaling.py covering target widths/bias, six graph audits, negative tamper cases, vector uniqueness, six fused compositional proof configurations, and six direct/CSA equivalence configurations.
- Updated .github/workflows/ci.yml to run the scaling benchmark in required physical mode and upload artifact orcus-int4-lane-scaling.
- This commit has not yet been CI-tested. Potential failures must be recorded precisely; no PPA or formal timing results for 8/16/32 are available yet. Next create PR, monitor CI, fix any failures, and audit the artifact before reporting comparisons.

## 149. Lane-scaling implementation branch synchronized to latest main — 2026-11-27T06:08:50.241Z

- Synced main cfda9ee95121292132322a86f6529aebb2633281 and current STATUS blob into research/orcus-int4-lane-scaling via non-force two-parent commit f6144e9e5e10bab4d2bb5b2c9b0df232764571b8. Expected-head update succeeded.
- Verified branch contains the 25,539-byte parameterized generator, 12,928-byte scaling benchmark with repository-root import path, six-test suite, and CI scaling benchmark/artifact steps.
- Next create the Milestone #2 pull request from research/orcus-int4-lane-scaling into main. CI has not run on this branch yet. No measured 8/16/32-lane results exist.

## 150. Milestone #2 PR creation payload syntax failure — 2026-11-27T06:09:10.223Z

- Attempted to create the lane-scaling PR. The JavaScript payload failed to parse because the body string included malformed backtick concatenation. No PR was created and no repository state changed.
- Retry with a plain quoted PR body and verify the resulting PR number/head.

## 151. Milestone #2 PR #20 opened — CI pending — 2026-11-27T06:09:34.644Z

- Opened PR #20: https://github.com/bio-ctrl/EGS/pull/20
- Title: ORCUS Milestone 2: 8/16/32-lane INT4 architecture scaling.
- Head branch research/orcus-int4-lane-scaling at f6144e9e5e10bab4d2bb5b2c9b0df232764571b8; base main at 6cd44f34f36b0945680c279a87a4d8737daf33aa.
- PR #20 is open. Initial GitHub metadata reports mergeable=false; this may reflect recalculation or base/branch status divergence. CI Run ID not yet retrieved. No scaling results or proof timings yet.
- Next: inspect raw PR metadata and exact-head workflow runs, monitor tests and benchmark, then fix failures and audit artifact. Do not merge PR #20 without separate explicit authorization.

## 152. Milestone #2 CI Run #248 started — 2026-11-27T06:09:54.198Z

- PR #20 automatic workflow Run #248, ID 45950053878, exact head f6144e9e5e10bab4d2bb5b2c9b0df232764571b8; created 2026-11-27T06:09:28Z; status in_progress.
- Raw PR API reports mergeable=null / mergeable_state=unknown while GitHub recalculates. No result yet.
- Next inspect job steps/logs, particularly the new all-scale unit tests and the 12-configuration physical benchmark. Artifact and measured data are pending.

## 153. Run #248 unit tests active — 2026-11-27T06:10:10.010Z

- Run #248 45950053878, job 140343567995, exact head f6144e9e5e10bab4d2bb5b2c9b0df232764571b8: dependency setup and OpenSTA verification passed; unit test step 9 is running. Compileall, Liberty fetch, existing four-lane benchmark, new 8/16/32 scaling benchmark, artifact uploads, and smoke check remain pending.

## 154. Run #248 live job-log retrieval unavailable — 2026-11-27T06:10:27.396Z

- Attempted to retrieve job logs while unit tests were still running. GitHub returned HTTP 404 BlobNotFound for the live log blob; no test result was inferred. No repository mutation occurred.
- Continue polling the job-step endpoint; retrieve complete logs after the step/run completes. Run #248 remains the active exact-head CI run unless a later status says otherwise.

## 155. Run #248 remains in formal/unit-test stage — 2026-11-27T06:10:42.220Z

- Re-polled Run #248 job 140343567995. Dependency and OpenSTA checks remain passed; unit test step 9 is still in_progress. No failure or completion has been reported. Remaining benchmark steps have not started.

## 156. Run #248 formal test stage still running — 2026-11-27T06:10:58.602Z

- Run #248 remains in_progress with unit test step 9 active; setup steps 1–8 succeeded. No conclusion yet. The expected duration includes six scaled fused compositional proof configurations and six direct/carry-save equivalence configurations, so do not treat the elapsed time alone as a timeout.

## 157. Run #248 live logs still unavailable — 2026-11-27T06:11:22.352Z

- Second attempt to fetch job 140343567995 logs while step 9 is active returned HTTP 404 BlobNotFound. The job-step endpoint remains the available source of progress; no test outcome inferred.

## 158. Independent Dadda stage-height algorithm spot-check — 2026-11-27T06:12:12.664Z

- Ran an isolated Python simulation of the staged Dadda height-reduction recurrence for 8/11, 16/12, and 32/13 targets. All three schedules reached a maximum final column height <=2. Target-height sequences begin 8 lanes: 28,19,13,9; 16 lanes: 63,42,28,19; 32 lanes: 94,63,42,28 (full target arrays are generated algorithmically).
- This validates the height recurrence only; it is not a RTL graph audit, SAT proof, or measured critical-path result. Run #248 unit tests remain in progress.

## 159. Run #248 remains in unit tests — 2026-11-27T06:12:37.744Z

- Latest job query still shows Run #248 job 140343567995, step 9 (unit tests) in_progress; setup and OpenSTA checks passed. No benchmark stage has started and no pass/fail conclusion exists. Continue monitoring; do not publish PPA or proof timing estimates from this pending run.
