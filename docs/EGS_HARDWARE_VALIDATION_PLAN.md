# EGS — Hardware Validation and PPA Evidence Plan
**Status:** Planned; no physical hardware validation completed  
**Purpose:** Define the evidence required to move from generic synthesis experiments toward credible implementation claims.

## 1. Current baseline
Existing work includes Verilog generation, exhaustive checks for selected small cases, Yosys SAT/equivalence experiments, and generic-cell synthesis. These results do not establish physical area, routed timing, power, energy, FPGA performance, or silicon behavior.

## 2. Validation ladder
### Gate 0 — Reproducible digital baseline
- Pin tool versions, source commit, constraints, scripts, and seeds.
- Store all candidate outputs, including failed candidates.
- Re-run reference and candidate from clean checkout.
- Require functional equivalence and preserve proof logs.
- Acceptance: independent reproduction of reported generic synthesis result.

### Gate 1 — Broader synthesis suite
- Select representative arithmetic and logic workloads.
- Define baseline architectures before running search.
- Use identical widths, signedness, interfaces, constraints, and tool settings.
- Track cell counts, logic depth, fanout, runtime, and proof status.
- Report wins, ties, losses, and timeouts.
- Acceptance: repeatable aggregate results, not one cherry-picked example.

### Gate 2 — Technology-mapped synthesis
- Select a legally available target standard-cell library and process corner.
- Document library source, license, voltage, temperature, and timing constraints.
- Run identical mapping flows for baseline and candidates.
- Report mapped cell area and timing estimates.
- Acceptance: reproducible mapped results with complete constraints and scripts.

### Gate 3 — Physical implementation
- Use an appropriate placement-and-routing flow and technology collateral.
- Record floorplan, utilization, clock assumptions, routing settings, parasitic extraction, and tool versions.
- Compare baseline and candidate under identical conditions.
- Report post-route timing, area, congestion, wire length, and power estimates where supported.
- Acceptance: repeatable post-route comparison with complete artifacts.

### Gate 4 — FPGA prototype (optional, workload-dependent)
- Select a board and target device based on a real workload.
- Measure resource utilization, clock frequency, throughput, latency, and power only with appropriate instrumentation.
- Compare identical implementations and preserve build artifacts.
- Do not treat FPGA results as ASIC PPA.

### Gate 5 — Silicon (long-term)
- Requires a mature design, verification, DFT, physical design, foundry access, packaging, and test plan.
- Use external engineering and manufacturing partners under reviewed agreements.
- No silicon tapeout or fabrication is currently claimed.

## 3. Required benchmark record
For every experiment record:
- experiment ID and timestamp;
- repository commit SHA;
- source and generated RTL hashes;
- workload, width, signedness, and interface;
- baseline definition and why it is fair;
- tool versions and configuration;
- formal/exhaustive proof method and result;
- synthesis and physical constraints;
- metrics and units;
- runtime and resource budget;
- logs, reports, and artifact locations;
- failures and deviations.

## 4. Anti-cherry-picking policy
- Pre-register benchmark suite and primary metrics before broad search.
- Keep all candidates and all outcomes.
- Separate training/development cases from held-out evaluation cases.
- Compare against strong, current baselines.
- Report median, spread, and per-case results.
- Do not tune the baseline less carefully than the candidate.
- Treat generic-cell counts as a proxy only, never as physical PPA.

## 5. First 90-day technical sequence
1. Reproduce existing nine-candidate compressor result from a clean checkout.
2. Generalize candidate schedule generation with deterministic seeds and budgets.
3. Add deduplication and candidate provenance.
4. Expand arithmetic workloads and held-out cases.
5. Strengthen formal proof coverage.
6. Establish one legal technology-mapped flow.
7. Select one physical-design path and obtain tool/library access.
8. Publish a complete benchmark report with negative results.

## 6. Claims policy
Until Gates 2–3 are completed, do not claim standard-cell area advantage, routed timing improvement, power/energy savings, or physical PPA superiority. Until Gate 5, do not claim silicon validation.
