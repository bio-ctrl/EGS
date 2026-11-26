# EGS Technology Demonstration Roadmap

**Status:** planning document  
**Parent company:** EGS  
**Research platform:** ORCUS  
**Other platform concept:** NEM  
**Scope:** research prototypes and reproducible demonstrations; not product or silicon-readiness claims.

## Operating rules

1. Every demo must have a defined problem, input workload, baseline, metric, and reproducible run command.
2. Correctness comes before performance. Use exhaustive checks where feasible and formal equivalence for larger hardware designs.
3. Report wins, ties, regressions, runtime, tool versions, and limitations. Never report only the best candidate.
4. Separate structural estimates and generic synthesis statistics from mapped standard-cell area, routed timing, power, and energy.
5. Do not claim novelty, superiority, fabrication readiness, or commercial advantage without evidence.
6. Keep research isolated on feature branches and preserve the existing Ceres project.

## Division 1 — ORCUS: computational architecture discovery

**Current state:** an experimental Python research codebase with Boolean/DAG search, a typed bit-vector IR, adder-family generation, bounded associative topology search, and a nine-candidate multi-operand compressor experiment.

**Existing evidence:** the four-operand, three-bit compressor experiment checked nine candidates; all nine passed exhaustive functional checking and Yosys SAT equivalence. Two candidates used fewer Yosys generic cells than the direct-arithmetic reference (40 and 41 versus 43); two tied and five regressed. This is a narrow generic-cell result, not physical PPA or proof of novelty.

**Next demo — ORCUS Search v2**
- Generate compressor schedules from policies rather than selecting only the existing fixed Wallace/Dadda/reversed-Wallace set.
- Use deterministic bounded search (documented seed, candidate budget, and stopping rule).
- Deduplicate structurally equivalent candidates.
- Verify every retained candidate; reject incorrect candidates before scoring.
- Compare against direct arithmetic and established compressor/adder baselines.
- Emit machine-readable JSON plus a human-readable report containing every candidate, including ties and regressions.

**Acceptance:** one command reproduces the full experiment; tests cover schedule generation and edge cases; Yosys equivalence passes; reports include runtime and tool versions; no physical-PPA claim.

## Division 2 — NEM: next-generation computing research

**Current state:** concept name only in this roadmap; no validated NEM architecture or implementation is being claimed.

**First demo gate:** define one target workload and one falsifiable hypothesis before coding. Specify the execution model, data representation, memory model, baseline implementation, and metrics. Build a software simulator/reference model first; only then consider RTL.

**Acceptance:** the workload, baseline, and success metric are fixed in writing; reference outputs are tested; benchmark inputs and results are reproducible. NEM must have a distinct technical thesis from ORCUS rather than being a renamed ORCUS demo.

## Division 3 — EGS Silicon: hardware and chip-design research

**Current state:** no EGS-designed chip, tapeout, or fabricated silicon is claimed.

**First demo:** take a verified ORCUS-generated design through a documented RTL flow: lint, formal equivalence, synthesis, and (when a suitable open flow and PDK are available) placement/routing.

**Acceptance:** publish RTL, constraints, tool versions, scripts, logs, and measured reports. Clearly label generic-cell, mapped-cell, and physical results. No fabricated-silicon claims without a tapeout and silicon measurements.

## Division 4 — AI and high-performance computing

**Current state:** a research direction, not an implemented EGS product.

**First demo gate:** choose one concrete workload (for example, matrix multiplication or a defined inference kernel), then establish a trusted CPU/GPU baseline and a reproducible measurement protocol.

**Acceptance:** identical inputs and precision, warm-up and repeated runs, throughput and latency distributions, memory use, hardware/software details, and correctness checks. Do not claim superiority from incomparable devices or workloads.

## Division 5 — Advanced semiconductor research

**Current state:** a research direction, not a fabrication capability.

**First demo gate:** choose one tractable, measurable subproblem such as RTL architecture trade-offs, memory hierarchy, interconnect modeling, or an open-PDK physical-design experiment.

**Acceptance:** public or otherwise documented assumptions, reproducible scripts, baseline comparison, and explicit separation between simulation, synthesis, physical design, and fabricated hardware.

## Demo portfolio order

1. **ORCUS Search v2:** extend the existing validated codebase; highest immediate continuity.
2. **ORCUS-to-RTL flow:** connect architecture search to a verifiable hardware-design pipeline.
3. **NEM workload prototype:** only after its independent technical hypothesis is written.
4. **AI/HPC benchmark:** after selecting a workload and comparable baseline.
5. **Semiconductor research experiment:** after selecting an open, reproducible flow and target question.

## Required demo package

Each demo must include:
- README with the exact research question and one-command reproduction.
- Source code and automated tests.
- Baseline implementation and baseline provenance.
- Machine-readable raw results (JSON/CSV).
- A concise report with methodology, results, regressions, and limitations.
- CI that runs correctness checks and a bounded smoke benchmark.

## Funding and campus discipline

The EGS headquarters concept is a long-term company vision, not evidence of current operating capacity. Research demonstrations should establish technical credibility before campus construction or large fixed operating commitments. Any fundraising or company legal arrangements while the founder is a minor require appropriate adult involvement and qualified legal counsel.
