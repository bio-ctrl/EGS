# ELSTELLA INTELLIGENCE — PROPOSED ARCHITECTURE

## Product definition

A research-workflow tool for organizing biomedical literature and biological context. The first demonstrator, ORIGIN ATLAS, is a static interface. The architecture below is a proposal, not a claim that these services already exist.

## Core modules

### 1. Source registry
Stores bibliographic metadata, DOI/PMID, source URL, publication type, access status and verification state.

### 2. Evidence extraction
Stores individual claims with source location, quoted or paraphrased support, extraction method, reviewer, date and confidence. Any AI-assisted extraction must remain traceable to the source and require human verification.

### 3. Context model
Represents relationships among disease context, tissue, cell population, cell state, model system, intervention, outcome and time point.

### 4. Evidence quality
Records study design, sample size where available, replication, risk-of-bias assessment, endpoint type and limitations. Do not collapse these into an opaque single score without validation.

### 5. Hypothesis workspace
Links hypotheses to supporting evidence, contradictory evidence, unknowns, assumptions, proposed tests and explicit disconfirmation criteria.

### 6. Review and audit
Tracks changes, reviewer disagreements, source versions and decision history.

## Proposed data entities

- Source
- Study
- Claim
- DiseaseContext
- Tissue
- CellPopulation
- CellState
- ModelSystem
- Intervention
- Outcome
- Limitation
- Hypothesis
- ReviewerAssessment

## Non-functional requirements

- Provenance for every scientific claim.
- Reproducible imports and exports.
- Versioned schemas.
- Clear separation of extracted facts, author interpretation and Elstella hypotheses.
- Privacy-conscious handling of data.
- No patient-identifiable data in the initial prototype.
- Transparent error reporting and human review.

## Initial implementation sequence

1. Static HTML prototype.
2. Structured CSV/JSON evidence store.
3. Local search and filtering.
4. Source metadata verification.
5. Human-reviewed extraction workflow.
6. Benchmark study against a conventional workflow.
7. Only then consider a backend, database or AI-assisted extraction.

## What is not implemented

No live literature API, knowledge graph, AI extraction engine, model inference, clinical decision support or validated evidence-ranking algorithm is currently implemented.
