# ELSTELLA & CO. — PROJECT ORIGIN

**Biological Restoration & Therapeutics**  
**Founding scientific initiative:** PROJECT ORIGIN  
**Initial research program:** PROJECT CARDIA  
**Research workspace:** ORIGIN ATLAS

> Elstella investigates how biological systems become dysfunctional and develops computational and therapeutic technologies intended to restore healthy biological function.

## What this repository is

This is the founding research workspace for Elstella. It separates the company's long-term ambition from what has actually been demonstrated today.

- **Elstella Intelligence** is the proposed computational research platform.
- **ORIGIN ATLAS** is an interactive, local-first evidence and hypothesis workspace.
- **PROJECT CARDIA** is the initial research program focused on cardiac fibrosis.
- **PROJECT BIOPATH** is an exploratory literature program on biological transport principles and nature-inspired therapeutic delivery.

## Current status — read this first

This repository contains an early software and research prototype. It is **not** a validated scientific discovery, medical device, diagnostic, drug candidate or therapeutic product. Starter citations are unreviewed leads. No claim of novelty, efficacy, clinical utility or superiority over existing tools is made.

## Repository map

- `company/founding-charter.md` — identity, mission, scope and operating principles.
- `research/project-origin.md` — central research agenda.
- `research/project-cardia.md` — initial cardiac fibrosis research question and falsification criteria.
- `research/project-biopath.md` — exploratory nature-inspired delivery research.
- `research/review-protocol.md` — draft CARDIA review protocol; not registered or executed.
- `research/scientific-validation-plan.md` — validation gates, benchmark design and falsification criteria.
- `research/cardia-therapeutic-landscape.md` — rapid literature map of existing mechanisms, candidate approaches and translational gaps; not a systematic review.
- `research/evidence-register.csv` — starter bibliography, not completed evidence extraction.
- `research/hypothesis-register.csv` — initial proposed hypotheses.
- `platform/architecture.md` — proposed technical architecture.
- `platform/methodology.md` — evidence review methodology.
- `platform/data-dictionary.md` — field definitions and provenance rules.
- `platform/evidence-completeness.js` — metadata completeness gate; does not verify scientific truth.
- `platform/benchmark-plan.md` — proposed comparison against a conventional review workflow.
- `platform/research-engine.js` — Europe PMC search, metadata conversion and abstract candidate extraction.
- `platform/ai-contract.js` and `server.js` — evidence-grounded AI synthesis contract and local server endpoint.
- `platform/shared-workspace.js` and `supabase/schema.sql` — optional authenticated per-account cloud sync.
- `governance/claims-and-safety.md` — scientific integrity and research boundaries.
- `investor/overview.md` — factual early-stage company overview.
- `BUILD-STATUS.md` — implemented features and known limitations.
- `index.html` — ORIGIN ATLAS application.

## Run ORIGIN ATLAS

Use Node.js 20.6 or newer. Copy `.env.example` to `.env`, configure the AI provider variables on the server if AI synthesis is needed, then run:

```bash
npm start
```

Open `http://localhost:4173`. Run automated tests with:

```bash
npm test
```

The static page can be opened directly, but the server is required for the AI synthesis endpoint. No third-party npm dependencies are required.

## Implemented capabilities

- Create, edit, search, export and back up evidence records.
- Maintain a hypothesis register.
- Search Europe PMC and import bibliographic metadata and abstracts.
- Extract candidate abstract sentences for objective, methods, reported-result and limitation review.
- Send selected local evidence records to a configured server-side AI provider for evidence-grounded synthesis.
- Optionally sync a workspace to Supabase for the same authenticated account across devices.

**Extraction boundary:** imported metadata and abstract passages are unverified candidates. They are not verified scientific claims. Read the original publication, record exact source locations and have important claims independently reviewed.

## Integrations and setup

### AI-assisted synthesis

Copy `.env.example` to `.env` and set `AI_API_URL`, `AI_API_KEY`, and `AI_MODEL` for an OpenAI-compatible chat-completions endpoint. The API key stays on the Node server. Never put a provider secret in browser code or commit `.env`. The interface asks for confirmation before sending up to 30 records to the configured external provider.

The assistant is a synthesis aid, not an autonomous scientific discovery system. Its output may be wrong and must be checked against the original sources. Do not send patient-identifiable or confidential information.

### Shared workspace

Create a Supabase project, run `supabase/schema.sql` in its SQL editor, and configure the project URL plus public anon key in the Research engine tab. The schema uses row-level security so each signed-in account accesses only its own row. No database is provisioned by this repository. This supports same-account cross-device sync; it is not team collaboration or multi-user shared editing.

Never use a Supabase `service_role` key in the browser.

### Literature extraction

Europe PMC search imports publication metadata and abstract text. Sentence-level candidates are suggestions only. Verify bibliographic details and review the original publication before entering any verified claim.

## First execution milestones

1. Verify every starter source's bibliographic metadata and obtain lawful full-text access.
2. Run and document the search strategy in the review protocol.
3. Screen sources against pre-defined eligibility criteria.
4. Extract source-backed findings, model systems, cell populations, contexts and limitations.
5. Have a qualified second reviewer independently check a sample of extractions.
6. Benchmark ORIGIN ATLAS against a conventional literature-review workflow.
7. Ask qualified cardiovascular researchers whether the structured map changes any research decisions.
8. Revise or stop the platform hypothesis based on results.

## CARDIA validation status

The therapeutic landscape and validation plan are drafted. They are literature-mapping and protocol artifacts, not completed scientific validation or therapeutic discovery. See `research/scientific-validation-plan.md` and `research/cardia-therapeutic-landscape.md`.

## Founding principle

Build evidence before claims. Build a useful research instrument before calling it a platform. Build a defensible therapeutic program only after the biology and evidence justify it.
