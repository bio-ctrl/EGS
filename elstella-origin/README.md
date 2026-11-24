# ELSTELLA & CO. — BIOLOGICAL RESTORATION & THERAPEUTICS

**Scientific foundation:** Systems-Level Biology  
**Company model:** Research-led biotechnology supported by computational infrastructure  
**Research software:** Elstella Intelligence / Research Atlas

## Company sequence

1. **Cellular & Mitochondrial Health** — first division and first research priority.
2. **Muscle & Physical Health** — second planned division.
3. **Brain & Cognitive Health** — third planned division.

These divisions are ordered strategic priorities, not simultaneous drug-development programs.

## Company architecture

- **Elstella Intelligence:** research software for literature organization, public-data metadata, biological context, source provenance, evidence uncertainty, and research questions.
- **Elstella Therapeutics:** long-term proprietary therapeutic-development capability, advanced only with qualified scientific leadership, appropriate institutional oversight, and evidence.

## Operating philosophy adapted from early Eli Lilly history

ELSTELLA is adapting principles, not copying products or branding: begin with a clear medical purpose; build trust through quality and scientific integrity; recruit expertise deliberately; collaborate with academic and industry partners where appropriate; reinvest in research capability; and scale only when evidence and demand justify it.

## First division — Cellular & Mitochondrial Health

Initial work is a high-level scientific landscape and unmet-need assessment:
- Understand cellular energy and mitochondrial biology using authoritative sources.
- Map relevant diseases, existing care, research activity, and clinical-development context.
- Inventory lawfully accessible public datasets and document limitations.
- Identify what is established, uncertain, contested, and not yet understood.
- Obtain qualified independent scientific critique.
- Decide whether a focused research question is justified.

No molecular target, drug candidate, intervention, efficacy, safety, or clinical claim is established.

## Second and third divisions

**Muscle & Physical Health** is preserved as the second planned division. Its future research remit is medical needs involving muscle disease, weakness, and age-related loss of function—not performance-enhancement drug development.

**Brain & Cognitive Health** is preserved as the third planned division. Its future research remit is neurological disease, brain health, and cognitive decline—not cognitive-enhancement drug development.

Neither division begins substantive research until the first division has passed its documented review gate and the company has the qualified expertise and resources to proceed.

## Retained research

- **PROJECT GENESIS:** foundational systems-level research on developmental systems, gene regulation, and biological form.
- **PROJECT CARDIA:** separate exploratory historical research on cardiac remodeling and fibrosis.
- **VYREON:** preliminary concept associated with CARDIA only; not an established candidate or validated therapeutic.
- **PROJECT MITOS:** earlier mitochondrial research-planning material retained as historical work.
- Leigh-specific project documents are discontinued as active strategy.

## Repository map

- `company/founding-charter.md` — mission, principles, company architecture, and stage gates.
- `company/brand-system.md` — company naming and communication rules.
- `company/operating-model.md` — business model and staged division sequence.
- `research/program-portfolio.md` — division order and retained historical work.
- `research/cellular-mitochondrial-health-charter.md` — first division charter.
- `research/cellular-mitochondrial-landscape-framework.md` — literature-led research framework.
- `research/therapeutic-portfolio-strategy.md` — long-term therapeutic strategy.
- `strategy/roadmap.md` — evidence-gated company roadmap.
- `platform/` — Research Atlas software, data dictionary, methods, and architecture.
- `tests/` and `.github/workflows/` — automated software tests and CI.
- `investor/overview.md` — factual early-stage company overview.
- `BUILD-STATUS.md` — implemented features and known limitations.

## Run the Research Atlas

Requirements: Node.js 20.6 or newer.

```bash
cd elstella-origin
npm install
npm test
npm start
```

Then open [http://localhost:4173](http://localhost:4173).

Optional AI-assisted synthesis requires server-side provider configuration. The core application and literature workflow should be usable without AI credentials. Never put provider secrets in browser code or commit a `.env` file.

## Research integrity

- Start with a defined question and credible medical need.
- Map existing research before claiming a gap.
- Use lawfully accessible publications and public research data.
- Record source identifiers, retrieval dates, access terms, and transformations.
- Distinguish study results, author interpretations, and Elstella hypotheses.
- Record uncertainty, contradictory findings, and negative results.
- Do not claim novelty, efficacy, safety, patentability, or clinical relevance without appropriate evidence.
- Human-participant, patient-data, biological-sample, animal, laboratory, experimental, and clinical work requires qualified institutional oversight, permissions, and supervision.

**Founding principle: Evidence before claims.**
