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
- `research/evidence-register.csv` — starter bibliography, not completed evidence extraction.
- `research/hypothesis-register.csv` — initial proposed hypotheses.
- `platform/architecture.md` — proposed technical architecture.
- `platform/methodology.md` — evidence review methodology.
- `platform/data-dictionary.md` — field definitions and provenance rules.
- `platform/benchmark-plan.md` — proposed comparison against a conventional review workflow.
- `governance/claims-and-safety.md` — scientific integrity and research boundaries.
- `investor/overview.md` — factual early-stage company overview.
- `BUILD-STATUS.md` — implemented features and known limitations.
- `index.html` — ORIGIN ATLAS application.

## Run ORIGIN ATLAS

Use Node.js 20 or newer. Copy `.env.example` to `.env`, configure the AI provider variables on the server if AI synthesis is needed, then run `npm start` and open `http://localhost:4173`. Run `npm test` for automated unit tests. The static page can still be opened directly, but the server is required for AI synthesis.

The current application supports:
- creating and editing evidence records;
- searching the evidence register;
- adding research hypotheses;
- saving edits in browser-local storage;
- exporting evidence as CSV;
- backing up and restoring the workspace as JSON;\n- searching Europe PMC and importing bibliographic metadata;\n- extracting candidate abstract passages with explicit unverified status;\n- AI-assisted evidence synthesis through a server-side, OpenAI-compatible chat endpoint (requires server credentials);\n- optional Supabase account sync with row-level security (requires a separately created Supabase project and schema setup).

**Important:** Local browser data does not automatically sync to GitHub or another device. Export JSON backups regularly. The application includes a Europe PMC metadata/abstract importer, a server-side AI synthesis endpoint, and an optional per-account Supabase sync adapter. These integrations require configuration and have not been deployed or independently security-audited. Supabase sync is same-account cross-device sync, not shared team collaboration. The AI model is an assistant for synthesis, not an autonomous scientific discovery system.

## Integrations and setup\n\n- AI: copy `.env.example` to `.env` and set `AI_API_URL`, `AI_API_KEY`, and `AI_MODEL` for an OpenAI-compatible chat-completions endpoint. The API key stays on the Node server. Never place a provider secret in browser code or commit `.env`.\n- Shared workspace: create a Supabase project, run `supabase/schema.sql`, and configure the project URL plus public anon key in the Research engine tab. The schema uses row-level security so each signed-in account accesses only its own row. No database is provisioned by this repository.\n- Literature extraction: Europe PMC search imports publication metadata and abstract text; sentence-level candidates are suggestions only. Review the original publication before entering any verified claim.\n\n## First execution milestones

1. Verify every starter source's bibliographic metadata and obtain lawful full-text access.
2. Run and document the search strategy in the review protocol.
3. Screen sources against pre-defined eligibility criteria.
4. Extract source-backed findings, model systems, cell populations, contexts and limitations.
5. Have a qualified second reviewer independently check a sample of extractions.
6. Benchmark ORIGIN ATLAS against a conventional literature-review workflow.
7. Ask qualified cardiovascular researchers whether the structured map changes any research decisions.
8. Revise or stop the platform hypothesis based on results.

## Founding principle

Build evidence before claims. Build a useful research instrument before calling it a platform. Build a defensible therapeutic program only after the biology and evidence justify it.
