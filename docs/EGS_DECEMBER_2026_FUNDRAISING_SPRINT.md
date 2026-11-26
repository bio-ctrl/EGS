# EGS — December 2026 Fundraising Sprint

**Target deadline:** 31 December 2026  
**Aspirational raise target:** US$10,000,000  
**Company:** EGS  
**Active research platform:** ORCUS  
**Separate platform concept:** NEM  
**Status:** execution plan; financing is not committed or guaranteed.

> **Technical execution plan:** The detailed 26 November–31 December engineering schedule, PR #13 review gate, ORCUS Search v2 requirements, synthesis/data-movement metrics, FPGA validation protocol, and evidence-room acceptance criteria are maintained in [ORCUS v2 — Five-Week Execution Plan](ORCUS_V2_FIVE_WEEK_EXECUTION_PLAN.md). This document remains the fundraising and commercial-readiness workstream; the technical plan is the source of truth for the engineering sprint.

## The objective

By 31 December 2026, EGS should have a credible, reviewable fundraising package and an active pipeline of qualified conversations. The $10M target is an ambition, not a forecast. The sprint must pursue the target while creating smaller, realistic financing paths—grants, accelerator programs, sponsored research, paid technical evaluations, and staged investment—rather than treating one large check as the only possible outcome.

Because the founder is a minor, a qualified adult representative and startup/securities counsel must be involved before investor solicitation that constitutes an offer, accepting funds, signing agreements, issuing equity, or transferring/licensing IP. This plan is preparation, not legal advice or an offer to sell securities.

## Non-negotiable rules

1. Never invent traction, revenue, customers, pilots, partnerships, endorsements, patents, employees, or investor interest.
2. Separate completed work, current prototypes, hypotheses, and future plans in every document.
3. Do not promise NVIDIA, AMD, or any other company will license technology or provide staff.
4. Do not claim ORCUS is novel or superior based on the current narrow generic-cell experiment.
5. No mass cold outreach, confidential technical disclosure, or fundraising agreement without adult and legal review.
6. Protect the Ceres project and keep the active EGS research work on its research branch until review and explicit approval.

## Investor narrative — working version

**EGS is building an advanced-computing and semiconductor research company focused on discovering, verifying, and evaluating computational architectures.** Its first technical wedge is ORCUS: a research platform for generating candidate digital architectures, checking correctness, and comparing implementations against established baselines.

The present prototype demonstrates a working research workflow, not a market-ready product or a proven industry breakthrough. In one small four-operand, three-bit compressor experiment, nine candidates passed exhaustive checking and Yosys SAT equivalence; two used fewer Yosys generic cells than the direct-arithmetic reference (40 and 41 versus 43), two tied, and five regressed. This is a narrow result. It does not establish physical area, timing, power, energy, silicon readiness, novelty, or general superiority.

EGS's next objective is to expand the candidate-generation space, preserve complete experiment records, validate RTL through stronger tool flows, and obtain independent technical review. Commercial paths to investigate include paid evaluations, sponsored research, joint development, and licensing of specific validated technology if buyer demand and IP review support it.

## The funding case that must be assembled

### 1. Problem and buyer
- Identify one specific engineering problem ORCUS could solve.
- Identify the technical buyer and economic buyer.
- Document how the problem is handled today and what it costs in engineering time, design quality, or compute.
- Interview prospective users; record dated notes and permission to quote.
- Do not treat general enthusiasm as purchasing intent.

### 2. Technical proof
- Complete ORCUS Search v2 with policy-driven candidate generation, deterministic budgets, deduplication, correctness checks, and full reporting.
- Reproduce the current baseline and compressor experiment.
- Extend to additional workloads and widths chosen before experiments.
- Add an ORCUS-to-RTL flow: lint, formal equivalence, synthesis, and physical design only where the required flow/PDK is available.
- Publish tool versions, constraints, scripts, raw results, all regressions, and known limitations.
- Obtain at least one independent review or reproduction attempt if feasible.

### 3. Commercial validation
- Produce a list of target buyer profiles, not a fabricated list of warm leads.
- Conduct discovery interviews through appropriate adult-supported introductions.
- Ask what a buyer would need to evaluate the technology, what integration costs exist, and what measurable outcome would justify a pilot.
- Prepare a narrowly scoped paid-evaluation proposal only after a real use case is identified.
- Treat NVIDIA and AMD as possible future strategic targets, not assumed partners.

### 4. Team and operating plan
- Define the first critical hires/contractors by technical bottleneck and deliverable.
- Obtain realistic compensation and recruiting assumptions.
- Identify compute, EDA, lab, equipment, and external fabrication/packaging requirements.
- Build a monthly 24-month cash model with base, downside, and delayed-fundraising cases.
- Use quotes rather than guessed equipment costs wherever possible.

### 5. Governance and IP
- Establish who created each code, design, document, and invention and whether any third-party or school resources were used.
- Review open-source licenses and dependencies.
- Have counsel review company formation, ownership, contributor assignments, confidentiality, patent strategy, and any license terms.
- Do not assume an idea, repository, or AI-generated concept art is automatically patentable or exclusive.
- Keep confidential information out of public decks and unapproved outreach.

## December sprint calendar

### 25–27 November — foundation
- Freeze a truthful one-page company overview.
- Audit the repository, branch, commit, CI, and reproducibility instructions.
- Create a data-room index and evidence register.
- Define the ORCUS Search v2 experiment specification before implementation.
- Identify adult representative and qualified counsel for company/IP/fundraising review.

**Exit criteria:** one-page overview, evidence register, repository snapshot, technical experiment spec, governance contact plan.

### 28 November–4 December — technical proof and buyer definition
- Implement the next bounded ORCUS search improvement.
- Add tests and deterministic benchmark reporting.
- Run CI and preserve raw reports.
- Select one buyer problem and draft interview questions.
- Build initial customer-profile and investor-profile criteria.

**Exit criteria:** reproducible technical delta, baseline report, one target use case, interview protocol.

### 5–11 December — investor materials
- Draft a concise 10–12 slide investor deck.
- Build a 24-month use-of-funds model with actual role and vendor assumptions.
- Prepare founder/company narrative and a technical appendix.
- Prepare a data room with code, reports, CI evidence, IP inventory, and limitations.
- Obtain adult/counsel review before any fundraising outreach.

**Exit criteria:** deck v1, budget v1, data-room index, legal review path.

### 12–18 December — external validation
- Conduct appropriate buyer discovery conversations.
- Request independent technical feedback/reproduction where feasible.
- Refine the problem statement, use case, and pilot success metrics.
- Identify relevant accelerators, university entrepreneurship programs, grants, and deep-tech investors.
- Send only reviewed, truthful materials through appropriate introductions.

**Exit criteria:** documented feedback, refined deck, prioritized funding pathways, reviewed outreach materials.

### 19–24 December — funding pipeline
- Follow up on qualified conversations.
- Prepare tailored technical briefs for parties with a genuine fit.
- Scope potential paid evaluations or sponsored research only where there is a real buyer problem.
- Update financial scenarios and milestone-linked capital needs.
- Do not imply that conversations are commitments.

**Exit criteria:** conversation tracker, tailored briefs, updated financial model, clear next steps.

### 26–31 December — close the loop
- Complete follow-ups and requested diligence.
- Record actual interest, diligence requests, pass decisions, and next meetings.
- If a financing opportunity advances, have qualified counsel and the adult representative handle legal structure and review.
- If no investment is committed by the deadline, continue the pipeline and pursue staged alternatives; do not sign unsafe or rushed terms just to meet a date.

**Exit criteria:** accurate fundraising status report, January pipeline, next technical milestones, revised runway plan.

## Investor deck — proposed 12-slide structure

1. **EGS:** company identity and mission.
2. **The problem:** a specific, validated computational architecture/design bottleneck.
3. **Why now:** only evidence-backed shifts in compute, chip design, and architecture complexity.
4. **The approach:** ORCUS workflow and architecture-search loop.
5. **What exists today:** prototype modules, reproducible tests, CI, and exact measured results.
6. **The evidence:** candidate counts, correctness results, baseline comparison, regressions, and limitations.
7. **What is hard to copy:** compounding experiment corpus, search methods, verification pipeline, implementation knowledge, and team execution—without claiming impossibility.
8. **Initial customer and use case:** evidence from discovery, or explicitly labeled hypotheses if not yet validated.
9. **Business model:** evaluation, sponsored research, joint development, or licensing hypotheses.
10. **Roadmap:** technical and commercial proof milestones.
11. **Team and governance:** actual people, roles, gaps, and adult/legal oversight; no invented advisors.
12. **The ask:** target capital, milestone-linked use of funds, runway assumptions, and financing structure reviewed by counsel.

## Use-of-funds model — required structure

Do not lock in arbitrary percentages. Build costs from actual assumptions:
- Research and engineering payroll, by role, salary, benefits, start date, and hiring probability.
- Compute, servers, cloud, EDA, and test equipment.
- Prototype, external lab, fabrication, packaging, and board costs where justified.
- Software, security, and infrastructure.
- IP, legal, accounting, insurance, and compliance.
- Facility lease, fit-out, utilities, and security.
- Contingency and reserve.

**Headquarters policy:** the first EGS base should support engineering and research without consuming the capital needed to prove ORCUS. The illustrated landmark campus is a separate long-term capital project, not a near-term $10M construction assumption.

## Funding pathways to pursue in parallel

- Deep-tech and semiconductor-focused venture investors.
- Hardware, EDA, and compute-focused accelerators.
- University-affiliated entrepreneurship and research programs, where eligibility permits.
- Non-dilutive grants and competitions with appropriate eligibility and IP review.
- Sponsored research and paid technical evaluations with real prospective users.
- Strategic investment or joint development only after a specific technical fit is demonstrated.

Every program's eligibility, deadlines, age requirements, and terms must be checked before applying. Do not pay an intermediary who guarantees investment or asks for an upfront fee to unlock capital.

## Evidence register

| Claim | Current status | What would strengthen it |
|---|---|---|
| ORCUS prototype exists | Supported by research branch | Reproducible clean setup and external review |
| Nine compressor candidates passed equivalence | Supported by recorded experiment | Reproduce on fresh environment and broader cases |
| Two candidates used fewer generic cells | Supported in one narrow test | Broader workloads, stronger baselines, mapped/physical data |
| ORCUS beats commercial synthesis tools | Not established | Fair head-to-head tests and independent replication |
| EGS has a licensable breakthrough | Not established | Defined invention, buyer value, IP review, validation |
| NVIDIA/AMD partnership or interest | Not established | Actual documented engagement |
| $10M financing | Target only | Executed financing and received funds |

## Weekly founder dashboard

Track every week:
- Technical: candidates generated, candidates verified, pass/fail counts, baseline deltas, runtime, CI status.
- Product: target use case, user interviews, pilot requirements, integration blockers.
- Fundraising: qualified introductions, meetings held, diligence requests, follow-ups, actual commitments (if any).
- Operations: hiring bottlenecks, quotes received, monthly burn, runway scenarios.
- Governance: IP ownership status, counsel review, approvals.

## Final standard

By 31 December, success means EGS has a truthful investor package, a reproducible technical demonstration, a reviewed financial model, an organized diligence room, and a real next-step funding pipeline. A $10M close is the stretch outcome—not something this plan can guarantee. If a smaller staged commitment or paid technical evaluation is the credible next step, pursue it without misrepresenting it as the full target.
