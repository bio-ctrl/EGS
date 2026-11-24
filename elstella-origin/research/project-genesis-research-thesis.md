# PROJECT GENESIS
## Research thesis: genetic regulation, developmental systems, and biological form

**Organization:** ELSTELLA & CO.  
**Program:** PROJECT GENESIS  
**Scientific area:** Evolutionary developmental biology, gene regulation, and systems biology  
**Status:** Proposed computational research direction; not executed, peer reviewed, preregistered, or validated  
**Version:** 0.1  
**Date:** 2026-11-24

---

## 1. Executive thesis

PROJECT GENESIS will investigate how differences in gene regulation and developmental context are associated with variation in cell identity, tissue organization, and organismal form.

The central scientific insight motivating this program is that biological form is not determined by DNA sequence alone. It emerges through interacting regulatory networks, developmental timing, cellular communication, environmental context, and evolutionary history.

A small genetic or regulatory difference can sometimes have a substantial developmental effect, but effects are context-dependent. Most sequence differences do not create a new body plan or a new species.

**Core question:**

> Across published comparative developmental datasets, how consistently are changes in gene-regulatory programs associated with differences in developmental timing, tissue patterning, and organismal form?

This is a descriptive and comparative research question. It does not propose engineering organisms, designing genetic sequences, or experimentally altering development.

## 2. Why this research area matters

A gene's presence is only part of the story. Biological systems also depend on:
- Where a gene is expressed.
- When expression occurs during development.
- Which cells express it.
- How strongly it is expressed.
- Which other regulatory programs are active at the same time.
- How cells interact with surrounding tissues and signals.

Developmental biology studies how cells and tissues organize into functioning structures. Evolutionary developmental biology examines how changes in developmental systems contribute to variation across species.

PROJECT GENESIS will focus on understanding and carefully documenting these relationships from published evidence.

## 3. Research objectives

### Objective A — Build a trustworthy evidence map
- Identify foundational and recent peer-reviewed research in Evo-Devo, developmental gene regulation, morphogenesis, and cell differentiation.
- Record organism, developmental stage, tissue, assay, sample size, publication, and data accession where available.
- Distinguish review articles, observational studies, perturbation studies, and computational predictions.
- Record limitations and conflicting findings.

### Objective B — Inventory public datasets
- Identify lawfully accessible, published developmental transcriptomics and single-cell datasets.
- Record species, tissue, developmental stage, assay type, sample structure, metadata completeness, and reuse conditions.
- Track whether datasets are independent or reuse the same samples.
- Do not treat cells from one specimen as independent organisms.

### Objective C — Map regulatory evidence descriptively
- Summarize published gene-regulatory relationships without designing or recommending genetic modifications.
- Compare how studies define cell identity, developmental stage, tissue region, and phenotype.
- Distinguish direct experimental evidence reported by source authors from inferred or predicted relationships.
- Track reproducibility and uncertainty across independent studies.

### Objective D — Identify a narrow, defensible research question
- Compare the proposed analysis with existing reviews, atlases, databases, and software.
- Ask whether a specific gap remains after this review.
- Define a falsifiable question and pre-specify inclusion criteria before analyzing outcomes.
- Stop or revise the project if existing work already answers the question or data quality is inadequate.

## 4. Initial scope

The first phase is limited to literature review, metadata inventory, and descriptive computational research using published data.

Out of scope:
- Designing or modifying DNA sequences.
- Engineering organisms or attempting to create new traits.
- Recommending gene edits or biological interventions.
- Laboratory protocols or experimental manipulation.
- Claims that computational associations establish causation.
- Claims of a new species, organism, treatment, or biological discovery.

Any future work involving biological samples, human participants, gene editing, or laboratory experimentation would require qualified institutional collaborators, appropriate approvals, and formal oversight.

## 5. Evidence standards

Every reported claim must be traceable to its source.

For each evidence item, record:
1. Citation and persistent identifier.
2. Organism and biological context.
3. Developmental stage and tissue, if applicable.
4. Study design and assay.
5. Sample/specimen count and biological unit.
6. Whether the finding is observed, experimentally supported by the source, or computationally inferred.
7. Independent replication status.
8. Limitations and conflicts.
9. Dataset accession and access conditions, when available.

Do not use a large number of cells as a substitute for a large number of independent specimens. Preserve specimen-level structure.

## 6. Falsifiable success criteria

The initial program succeeds only if it produces:
- A curated, cited literature map.
- A documented inventory of suitable public datasets.
- A transparent account of cohort/specimen overlap and missing metadata.
- A narrow research question not already adequately answered by existing work.
- A reproducible computational report with limitations and negative findings.

The program should be revised or stopped if the literature shows the question is already answered, the datasets are not comparable, or the proposed analysis adds no meaningful value.

## 7. First deliverables

1. `project-genesis-literature-map.md`
2. `project-genesis-dataset-inventory.csv`
3. `project-genesis-gap-assessment.md`
4. A GitHub Actions workflow that validates document structure, source links as recorded metadata, and inventory completeness.
5. A reproducible report distinguishing what is known, uncertain, and not established.

## 8. Current limitations

No raw developmental expression matrices have been analyzed in this program. No novel regulatory mechanism has been identified. No organism, gene sequence, therapeutic, or biological intervention has been designed or validated.

**Current conclusion:** PROJECT GENESIS is a proposed research direction with a broad scientific motivation. Its novelty and feasibility remain to be tested.
