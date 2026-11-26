# EGS — Investor Readiness & Technical Proof Plan

**Parent company:** EGS  
**Research platform:** ORCUS  
**Separate platform concept:** NEM  
**Document status:** working investor-preparation draft  
**Evidence boundary:** this document distinguishes completed research results from proposed work. It is not an offer to sell securities, a forecast, or a claim that funding or commercial agreements exist.

## 1. Company thesis

EGS is being developed as an advanced-computing and semiconductor research company. Its long-term thesis is that better computational architectures can be discovered, verified, and translated into useful hardware designs.

The initial wedge is deliberately narrower: build a reproducible architecture-search and verification workflow that explores candidate digital datapaths, proves functional correctness, and measures implementation trade-offs against credible baselines.

EGS should earn the right to expand into additional computing and semiconductor research areas through demonstrated technical results—not by presenting a broad list of ambitions as existing products.

## 2. Product and research portfolio

### ORCUS — architecture discovery

ORCUS is the first active research platform. It explores Boolean and bit-vector representations, candidate architecture generation, equivalence checking, and synthesis-based evaluation.

**Current evidence**
- Multi-output joint search, adder architecture generation, typed bit-vector IR, bounded associative topology search, and a multi-operand compressor experiment exist in the research codebase.
- In the documented four-operand, three-bit compressor experiment, nine candidate combinations were checked. All nine passed exhaustive functional checking and Yosys SAT equivalence.
- Two candidates used fewer Yosys generic cells than the direct-arithmetic reference (40 and 41 versus 43); two tied and five regressed.
- The result is narrow and small-scale. It is not a physical area, routed timing, power, energy, fabrication, or commercial advantage result.
- The current compressor experiment searches a fixed nine-combination family. It is not yet a broad architecture-discovery engine.

**Next proof milestone**
Generate compressor schedules from explicit policies, search a documented candidate budget, deduplicate candidates, verify every retained candidate, and publish all wins, ties, regressions, runtimes, and tool versions.

### NEM — separate platform thesis

NEM is a separate potential platform, not an ORCUS alias. No validated NEM architecture or implementation is claimed yet. Before implementation, EGS must define a distinct workload, execution model, falsifiable hypothesis, baseline, and measurable success criterion.

### EGS Silicon — hardware translation

The near-term objective is a reproducible RTL-to-physical-design demonstration using an appropriate open toolchain and process design kit where available. EGS does not currently claim a designed, taped-out, or fabricated chip.

### AI/HPC and advanced semiconductor research

These are expansion directions, not current products. Each must begin with a single well-defined workload or engineering question, a credible baseline, controlled measurement conditions, and reproducible results.

## 3. Why this could become defensible

EGS should not claim that an idea or codebase is impossible to copy. A durable advantage must be built from multiple reinforcing assets:

1. **Search corpus:** a growing, versioned dataset of generated candidates, equivalence outcomes, synthesis results, and failure cases.
2. **Verification pipeline:** correctness checks integrated into candidate generation so invalid candidates cannot be promoted by performance scoring.
3. **Evaluation discipline:** identical constraints, tool versions, workloads, and baseline procedures across experiments.
4. **Search methods:** documented algorithmic improvements that produce better candidate coverage or quality under a fixed compute budget.
5. **Implementation knowledge:** accumulated insight connecting abstract architecture metrics to mapped and physically implemented results.
6. **IP strategy:** counsel-reviewed decisions about what to publish, keep confidential, or potentially protect. No patentability or freedom-to-operate claim is made here.
7. **Execution speed:** a team capable of repeatedly turning research hypotheses into independently reproducible demonstrations.

The moat is the compounding system—data, methods, verification, implementation evidence, and people—not secrecy alone.

## 4. Investor proof milestones

### Gate A — reproducible ORCUS Search v2
- Policy-driven schedule generation beyond the fixed nine candidates.
- Deterministic seeds, explicit candidate budgets, and stable stopping rules.
- Structural deduplication.
- Exhaustive or formal equivalence for every scored candidate.
- Complete JSON/CSV results, including failures and regressions.
- Baselines selected before running the experiment.
- One-command reproduction and CI.

### Gate B — credible hardware evaluation
- Export candidate RTL.
- Lint and formal equivalence.
- Synthesis with documented constraints and tool versions.
- Where a suitable open PDK/flow is available, placement and routing.
- Report mapped area, timing, and power only when the relevant flow actually measures them.
- Compare against established baselines under identical conditions.

### Gate C — independent technical review
- Have external hardware-design researchers or engineers reproduce selected results.
- Record discrepancies and resolve them.
- Obtain written feedback on technical significance and practical relevance.
- Do not describe informal interest as a partnership or endorsement.

### Gate D — commercial discovery
- Identify one buyer problem where the measured result matters.
- Interview potential users and technical buyers.
- Establish integration requirements, switching costs, and procurement constraints.
- Seek a paid evaluation, sponsored research project, or narrowly scoped pilot before assuming a multimillion-dollar license is plausible.

## 5. Commercial model hypotheses

Potential models to validate—not existing revenue:
- Enterprise license for an architecture-search or verification workflow.
- Paid evaluation or proof-of-concept with a semiconductor, EDA, compute, or hardware company.
- Sponsored research or joint development with clear ownership and publication terms.
- Licensing of a specific protectable method or design, if legal review and buyer validation support it.

A large company such as NVIDIA or AMD is a possible future target customer or partner, not a committed prospect. EGS must first produce a result that is valuable to a specific engineering team. Do not assume a buyer will pay millions, provide employees, or fund a campus.

## 6. Proposed 12–24 month operating plan

This is a planning framework; timing and cost must be validated against hiring, tool access, compute requirements, and actual fundraising terms.

| Workstream | First 6 months | Months 7–12 | Months 13–24 |
|---|---|---|---|
| ORCUS | Search v2, full reports, formal checks | Broader workloads and stronger baselines | Independent replication and productization |
| Hardware flow | RTL export, lint, synthesis | Open-flow physical design | More workloads and implementation studies |
| NEM | Define separate thesis and workload | Build reference prototype if justified | Validate against relevant baselines |
| Commercial | Buyer discovery | Technical evaluations and pilot proposals | Convert validated pilots into contracts |
| Team | Core research/engineering capacity | Add specialists against bottlenecks | Expand only where milestones justify |
| Facilities | Use existing labs/leased space | Expand based on equipment and team needs | Evaluate dedicated campus phases |

## 7. Use-of-funds framework

No fixed allocation should be represented as final until a real operating plan, hiring plan, vendor quotes, and financing structure exist. For a hypothetical $10 million financing, the board-level budget should be built from:
- Fully loaded compensation and recruiting by role and start date.
- Compute, development systems, EDA licenses, and test equipment.
- Cloud and infrastructure costs.
- Prototype, fabrication, packaging, and external lab costs where applicable.
- Legal, IP, accounting, insurance, and compliance.
- Facility lease, fit-out, utilities, and security.
- Contingency and runway reserve.

**Headquarters rule:** begin with a functional leased or modestly fitted-out EGS research base. Treat the large illustrated campus as a later capital project with separate site, design, permitting, construction, and operating budgets. Do not let a prestige building consume the capital needed to prove the technology.

## 8. Investor data-room checklist

### Company and governance
- Company formation and ownership records, reviewed by qualified counsel.
- Founder and contributor IP assignments.
- Cap table and any existing promises, grants, or obligations.
- Adult/guardian and legal-counsel plan for any agreements while the founder is a minor.
- Board/advisor roles and conflict disclosures.

### Technical
- Repository access and branch/commit identifiers.
- Architecture and system diagrams.
- Reproduction instructions and CI results.
- Raw benchmark outputs and complete reports.
- Baseline provenance and tool versions.
- Formal-equivalence evidence.
- Known limitations, failed experiments, and next milestones.
- Independent review when obtained.

### Commercial
- Defined customer profile and engineering pain point.
- Interview notes and evidence of demand.
- Pilot scope, success metrics, and integration requirements.
- Pricing hypotheses clearly labeled as hypotheses.
- No fabricated letters of intent, customer names, endorsements, revenue, or partnerships.

### Financial and operations
- 24-month model with hiring assumptions and monthly cash runway.
- Vendor quotes and equipment requirements.
- Milestone-linked use of funds.
- Scenario analysis for slower fundraising or delayed technical progress.
- Facility plan separated from core R&D spending.

## 9. Claims policy for every investor document

Allowed:
- “EGS is developing…”
- “The prototype demonstrated… under the specified experiment.”
- “The next milestone is…”
- “We are evaluating potential applications in…”

Not allowed without evidence:
- “Proprietary breakthrough” or “un-copyable technology.”
- “Outperforms NVIDIA/AMD” without fair, comparable testing.
- “Physical PPA improvement” based only on generic-cell counts.
- “Patent protected” without an issued patent or accurately described application status.
- “Partnered with,” “endorsed by,” or “licensed to” a company without an executed agreement.
- “Chip,” “silicon,” or “fabrication-ready” claims implying hardware exists when only simulation or RTL exists.

## 10. Immediate execution priorities

1. Complete ORCUS Search v2 and preserve all candidate outcomes.
2. Build the ORCUS-to-RTL validation flow.
3. Produce a clean technical demo package that an external engineer can reproduce.
4. Write a concise investor deck from measured results, not aspirational claims.
5. Build a 24-month budget from actual role costs, quotes, and milestones.
6. Begin qualified adult/legal support for company formation, IP ownership, and any financing process.

**Fundraising objective:** finance the next proof milestones and build an enduring EGS research organization. The $10 million target is an aspiration until an actual financing is signed and funds are received.
