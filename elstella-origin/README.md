# ELSTELLA & CO. — BIOLOGICAL RESTORATION & THERAPEUTICS

**Scientific foundation:** Systems-Level Biology  
**Flagship research program:** PROJECT GENESIS  
**Research software:** Elstella Research Atlas

Elstella is an early-stage research initiative exploring how biological systems develop, maintain function, and change across development, evolution, and disease. Its long-term ambition is to connect systems-level biological understanding with computational research and, only where justified by evidence, responsibly developed therapeutics.

## What is active now

- **PROJECT GENESIS:** the initial flagship research program. It studies published evidence about developmental systems, gene regulation, and biological form.
- **Elstella Research Atlas:** a prototype workspace for organizing literature, source provenance, research questions, and evidence status.
- **PROJECT CARDIA:** a separate exploratory literature track on cardiac remodeling and fibrosis. It is not the flagship program.

## Current status

This repository contains early research documentation and a software prototype. It is not a validated scientific discovery, medical device, diagnostic, drug candidate, therapeutic product, or clinical program. No therapeutic efficacy or clinical benefit is claimed. The existence of a research plan does not mean that the proposed research has been completed.

## Repository map

- company/founding-charter.md — mission, scientific foundation, operating principles, and stage gates.
- company/brand-system.md — company naming and communication rules.
- company/operating-model.md — research-first operating thesis and resource discipline.
- research/project-genesis-research-thesis.md — initial GENESIS thesis.
- research/project-genesis-initial-charter.md — GENESIS scope and advance/revise/stop criteria.
- research/project-genesis-methodology.md — literature and public-data research method.
- research/program-portfolio.md — active, separate, and future research tracks.
- research/genesis-source-register-template.csv — blank source inventory template.
- research/genesis-dataset-inventory-template.csv — blank public-dataset metadata template.
- governance/claims-and-safety.md — scientific integrity and research boundaries.
- governance/data-governance.md — data provenance, handling, and oversight rules.
- strategy/roadmap.md — evidence-gated development roadmap.
- platform/ — research software, data dictionary, methods, and architecture.
- tests/ and .github/workflows/ — automated software tests and CI.
- investor/overview.md — factual early-stage company overview.

## Run the Research Atlas

Use Node.js 20.6 or newer. Copy .env.example to .env, configure optional server-side AI provider variables only if needed, then run npm start. Open http://localhost:4173. Run automated tests with npm test.

No production database or AI provider is provisioned by this repository. Never commit .env or place provider secrets in browser code.

## Research integrity

- Begin with a precise, falsifiable question.
- Use lawfully accessible publications and appropriately accessible public research data.
- Record source identifiers, retrieval dates, access terms, and transformations.
- Distinguish direct study results from author interpretations and Elstella hypotheses.
- Separate association from causation.
- Record negative findings, contradictions, uncertainty, and model limitations.
- Do not claim novelty, efficacy, safety, or clinical relevance without independent evidence.
- Any future work involving human participants, sensitive data, biological samples, animals, or laboratory activity requires qualified institutional oversight, permissions, and supervision.

## Immediate priority

Complete the PROJECT GENESIS literature map and public-dataset inventory. Establish whether a narrow, reproducible question survives a novelty and feasibility review before expanding the research portfolio or building additional infrastructure.

**Founding principle: Evidence before claims.**
