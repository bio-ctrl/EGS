# EGS — Investor Presentation Draft
**Status:** Working draft | **As of:** 25 November 2026  
**Confidentiality:** Internal planning document. Do not distribute until reviewed by an appropriate adult, company counsel, and technical reviewers.

> This deck is a truthful starting point, not a claim that EGS has raised capital, secured customers, fabricated silicon, or demonstrated physical PPA advantages. Replace every bracketed item with verified information before external use.

---

## Slide 1 — EGS
### Building a research engine for computational architecture discovery
EGS is developing tools to generate, evaluate, verify, and compare computational architectures, with a long-term ambition to translate validated discoveries into valuable computing and semiconductor technology.

**Current platform direction:** ORCUS  
**Other product exploration:** NEM (separate from ORCUS; not the parent company)  
**Parent-company name:** EGS (working name; not a finalized legal entity)

[Founder name and approved biography — insert only after legal review]

## Slide 2 — The problem
Computing systems are constrained by trade-offs among performance, area, power, energy, verification complexity, and implementation cost.

Architecture choices are often explored within established design patterns and tool flows. Finding better structures requires:
- generating meaningful candidate architectures;
- proving functional correctness;
- comparing candidates against fair baselines;
- measuring implementation outcomes under realistic constraints.

**Claim boundary:** EGS has not yet demonstrated that its current prototype beats commercial EDA flows or produces better physical silicon.

## Slide 3 — Our approach
ORCUS is being developed as an experimental architecture-search system:
1. Represent computational functions in typed intermediate forms.
2. Generate alternative architectures and decompositions.
3. Evaluate structural metrics.
4. Verify equivalence through exhaustive checks and formal tools where applicable.
5. Synthesize candidates and preserve reproducible benchmark results.
6. Progress toward physical implementation only after robust digital evidence.

## Slide 4 — What exists today
The repository contains:
- multi-output joint logic search;
- explicit ripple-carry, Kogge–Stone, and Sklansky adder generators;
- typed bit-vector/dataflow representation;
- bounded associative architecture enumeration;
- multi-operand compressor-network experiments;
- tests, benchmark scripts, Verilog emission, and technical documentation.

Repository: https://github.com/bio-ctrl/EGS  
Research branch: `research/joint-multioutput-search-v1`

## Slide 5 — Evidence to date
**Compressor-network experiment (Yosys 0.52, small unsigned arithmetic case):**
- 9 candidate configurations evaluated.
- All 9 passed the reported exhaustive/equivalence checks.
- Generic-cell reference: 43.
- Best candidate: 40 generic cells.
- Second-best candidate: 41 generic cells.
- Remaining candidates tied or used more cells.

**Other reported experiments:**
- Joint multi-output search: 2/5 cases improved structurally; 3/5 tied; generic-cell count tied in all five.
- Associative search: 15 topologies generated and verified for the tested case; all tied at 12 generic cells.

**Limitations:** These are narrow generic-synthesis results. They are not standard-cell area, routed timing, power, energy, physical PPA, FPGA results, silicon measurements, or proof of novelty. Search is bounded and current compressor family is fixed and small.

## Slide 6 — Why the work could matter
If expanded and validated, architecture-search infrastructure could help explore trade-offs that are difficult to evaluate manually:
- area versus logic depth;
- fanout and wiring pressure;
- sharing across outputs;
- arithmetic decomposition;
- implementation-aware architecture selection.

Potential value must be established through customer-defined workloads and measured improvements. No defensibility or moat should be claimed solely from the current prototype.

## Slide 7 — Development roadmap
**Phase A — Search quality**
- Generalize compressor schedule generation beyond the current fixed nine configurations.
- Add deterministic search budgets, deduplication, and candidate provenance.
- Expand independent baselines and benchmark suites.

**Phase B — Verification and synthesis**
- Strengthen formal equivalence coverage.
- Run reproducible synthesis across a broader workload suite.
- Track area, depth, fanout, runtime, and failed candidates.

**Phase C — Physical validation**
- Select suitable open or licensed implementation flows.
- Establish technology/library constraints.
- Run placement, routing, timing, and power estimation.
- Compare against identical baseline flows.

**Phase D — External evaluation**
- Obtain independent technical review.
- Conduct carefully scoped design-partner evaluations.
- Explore licensing or joint-development only after evidence and IP review.

## Slide 8 — Commercial hypotheses
Potential models to test—not established revenue streams:
- paid technical evaluations on customer-selected workloads;
- research collaboration or sponsored development;
- software/tool licensing;
- architecture IP licensing;
- joint development with semiconductor or systems companies.

First validation question: which measurable customer problem is expensive enough that a better architecture-search workflow would justify a paid evaluation?

## Slide 9 — Competitive landscape and differentiation
Relevant comparison categories include established EDA synthesis/optimization tools, academic architecture-search methods, in-house semiconductor design teams, and specialized IP providers.

EGS must benchmark against the tools and workflows customers actually use. Differentiation is not yet established. The intended differentiation is a reproducible generate–verify–measure loop with an expanding evidence corpus.

[Insert competitor matrix after named competitors and product capabilities are verified.]

## Slide 10 — Team and governance
**Founder:** [Insert verified background, age-appropriate role description, and relevant accomplishments.]  
**Technical advisors:** [None confirmed / insert only with permission.]  
**Employees and contractors:** [Insert verified status.]

Because the founder is a minor, formation, equity, investment, IP assignment, employment, licensing, and binding contracts require appropriate adult involvement and qualified legal advice. Do not imply a board, advisors, employees, or legal entity exists unless confirmed.

## Slide 11 — Financing objective and use of funds
**Aspirational financing objective:** up to $10 million by 31 December 2026. This is a target, not a forecast, commitment, or evidence of investor interest.

Illustrative allocation for a hypothetical $10 million financing (planning assumptions only; not quotes or approved budget):
| Category | Illustrative share | Illustrative amount |
|---|---:|---:|
| Engineering and research personnel | 45% | $4.50M |
| Compute, EDA, and technical infrastructure | 15% | $1.50M |
| Prototype, FPGA, and physical validation | 15% | $1.50M |
| IP, legal, security, and governance | 8% | $0.80M |
| Customer discovery and commercial pilots | 7% | $0.70M |
| Facilities and operations | 5% | $0.50M |
| Contingency | 5% | $0.50M |
| **Total** | **100%** | **$10.00M** |

Actual budget must be rebuilt from hiring plan, vendor quotes, facility strategy, financing instrument, and runway assumptions. A large landmark HQ is not a first-priority use of research capital.

## Slide 12 — The request
EGS is seeking qualified conversations with deep-tech investors, semiconductor experts, research institutions, and potential design partners to evaluate:
- technical thesis and benchmark methodology;
- a staged, evidence-based development plan;
- the right financing structure and governance;
- customer-defined evaluation opportunities.

**No investment commitment, partnership, customer, or revenue is represented as secured.**

### Required before external circulation
- [ ] Legal review of company identity, founder status, IP ownership, and fundraising permissions.
- [ ] Technical review of every result and reproducibility artifact.
- [ ] Replace placeholders with verified team and entity information.
- [ ] Add a dated benchmark appendix and baseline methodology.
- [ ] Validate all market and competitor claims with cited sources.
- [ ] Confirm the proposed financing instrument and permitted outreach process.
- [ ] Remove confidential implementation details not approved for disclosure.
