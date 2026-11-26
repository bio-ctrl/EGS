# EGS north star and execution principles

**Status:** Working founder direction, not a finalized legal company statement.

## The life principle

> Big dreams push past what other people view as possible, often because “unrealistic” just means a goal hasn't been done yet by the people around you. You have to dream unrealistic because life is not realistic.

A second personal principle is: **“Get what I want and when I want it.”**

These principles set ambition and urgency. They do not waive the requirement to earn results. Ambition determines the scale of the question; evidence determines what can honestly be claimed.

## The company ambition

EGS is intended to become a generational technology company. The aim is to develop foundational technologies that expand what future generations can build—and, over time, create substantial opportunity and wealth for the people who contribute to and benefit from that progress.

The long-range ambition includes competing in advanced computing and semiconductor infrastructure. That is a direction to work toward, not a statement that EGS currently has a chip, proprietary silicon, customers, revenue, or a competitive advantage over established semiconductor companies.

## Company and project boundaries

- **EGS:** parent-company working identity and long-term mission.
- **ORCUS:** the active computational-architecture discovery research platform in this repository.
- **NEM:** a separate potential platform/product; its scope remains undefined until explicitly established.
- **Ceres:** a separate project and outside the scope of this repository's work.

Do not rename ORCUS to EGS or assign NEM a technical definition by implication.

## Operating principles

1. **Think beyond precedent.** Do not reject a research direction merely because it is unfamiliar or difficult.
2. **Prove every claim.** Distinguish hypothesis, simulation, formal verification, generic synthesis, mapped PPA, FPGA measurements, silicon measurements, and customer validation.
3. **Preserve negative results.** Ties and regressions are evidence. Never hide them to make a benchmark look successful.
4. **Build durable capability.** Prefer reusable tools, testable modules, documented interfaces, reproducible experiments, and clear provenance over one-off demonstrations.
5. **Compete on measured outcomes.** Compare against strong, relevant baselines under equivalent conditions. Do not claim superiority from an isolated metric.
6. **Protect the long game.** Keep working systems intact, isolate experiments on research branches, and do not merge or overwrite protected work without an explicit decision.
7. **Create broad opportunity.** The objective is foundational progress that can support future builders, researchers, engineers, and businesses—not wealth claims detached from real value.

## Current execution sequence

1. Strengthen ORCUS's correctness, experiment provenance, and architecture-search coverage.
2. Expand from Boolean and arithmetic architecture experiments into explicit memory-hierarchy and data-movement models only with measurable workloads and baselines.
3. Validate candidate designs with independent synthesis and formal tools.
4. Progress to documented cell-library mapping, FPGA experiments, and physical implementation only when the preceding evidence justifies it.
5. Treat any future inference-accelerator or memory-first hardware concept as a research hypothesis until controlled measurements establish a real advantage.

## Claims discipline

At the current repository stage, ORCUS is an experimental software research prototype. Passing unit tests, exhaustive checks on small inputs, and Yosys generic-cell comparisons do not establish physical performance, energy efficiency, manufacturing feasibility, novelty, patentability, commercial readiness, or superiority to NVIDIA, AMD, or another vendor.

**The standard:** dream at the scale of the mission; execute at the scale of the evidence.
