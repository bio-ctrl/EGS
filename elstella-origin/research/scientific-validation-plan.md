# PROJECT CARDIA — SCIENTIFIC VALIDATION PLAN

**Prepared:** 2026-11-24  
**Status:** Protocol-ready draft; not executed; not registered.  
**Scope:** Computational/literature validation of a research-workflow hypothesis. This is not biological validation of a therapeutic.

## 1. Claims under evaluation

### Platform hypothesis

A structured evidence framework that preserves disease context, fibroblast state, model system, time point, endpoint and evidence provenance may improve the accuracy, reproducibility and usefulness of cardiac-fibrosis evidence mapping compared with a conventional spreadsheet-based workflow.

### Scientific hypothesis to map, not assume

Cardiac fibrosis findings are heterogeneous across disease context, cell state, tissue location and disease stage. The review will test how consistently primary evidence supports this statement and where it fails.

### Explicit non-claims

This project has not discovered a therapeutic, validated a molecular target, demonstrated efficacy, established clinical utility or shown superiority over existing research tools.

## 2. Primary objectives

1. Build a reproducible search and screening record.
2. Create a source-verified evidence set for a pre-defined cardiac-fibrosis question.
3. Measure extraction accuracy and provenance completeness.
4. Compare ORIGIN ATLAS with a conventional review workflow.
5. Obtain independent review by qualified cardiovascular researchers.
6. Make a pre-specified go / revise / stop decision.

## 3. Review protocol execution

Databases: PubMed and Europe PMC. Search date, exact query, filters, result count, export file and deduplication decisions must be recorded for every run.

Starting concept query:

`("cardiac fibrosis" OR "myocardial fibrosis" OR "cardiac remodeling") AND (fibroblast OR myofibroblast OR "immune-fibroblast" OR "extracellular matrix")`

This is a starting query, not a validated exhaustive search. Refine with a librarian or experienced reviewer. Keep HFpEF, post-myocardial-infarction remodeling, pressure-overload disease and atrial fibrosis separately identifiable.

### Inclusion

- Primary peer-reviewed studies with identifiable cardiac relevance.
- Human tissue, human cell systems, engineered tissue, animal models and relevant translational studies, each tagged by model class.
- Reviews for background and citation chaining, but not mixed into primary-study counts.

### Exclusion / separate classification

- Non-cardiac fibrosis without a clear cardiac comparison.
- Records with unverified bibliographic identity.
- Editorials and opinion pieces from primary evidence synthesis.
- Preprints and conference abstracts retained in a separate evidence stratum.

## 4. Required extraction fields

Publication identity; DOI/PMID; authors; year; publication type; disease context; cohort/species; tissue/location; cell population/state; model system; study design; method; exposure/intervention; comparator; endpoint; time point; result; exact source location (page/figure/table/section); limitations; funding/conflicts; reviewer; extraction date; verification state.

Every extracted claim must link to a source and exact location. Distinguish:
- Directly reported result.
- Authors' interpretation.
- Elstella interpretation.
- Hypothesis generated for future testing.

Do not infer causality from association. Do not combine results across incompatible disease contexts without justification.

## 5. Independent review and quality controls

- Two reviewers independently screen and extract a pre-specified subset.
- Preserve disagreements before adjudication.
- Use a qualified adjudicator for disagreements.
- Keep a versioned decision log.
- Record missing information as missing; never fill it with guesses.
- Use study-design-appropriate risk-of-bias tools selected with a qualified reviewer.
- Do not invent a single opaque "evidence score."

## 6. Platform benchmark

**Control:** Conventional spreadsheet/document workflow.  
**Intervention:** ORIGIN ATLAS.  
**Same inputs:** Identical source set, protocol, extraction fields and reviewer instructions.

Pre-specify outcomes:
- Field-level accuracy against an adjudicated reference.
- Provenance completeness.
- Inter-reviewer agreement.
- Time per paper and time per completed map.
- Correct identification of contradictory findings and context differences.
- Unsupported-claim rate.
- Expert-rated usefulness.

Counterbalance workflow order where feasible. Report all outcomes, including null or negative results.

### Go / revise / stop

- **Go:** Reproducible improvement in at least one preselected primary outcome without worsening unsupported-claim rate or provenance.
- **Revise:** Useful workflow but no clear accuracy or efficiency improvement; narrow the use case and repeat.
- **Stop:** No meaningful improvement, worse accuracy, weak reproducibility or experts find no decision value.

No numerical threshold should be chosen after seeing results. Set thresholds with reviewers before data collection.

## 7. Therapeutic-development evidence gates

These are separate from the platform benchmark.

| Gate | Required evidence | Current status |
|---|---|---|
| T0 — Disease context | Precisely defined indication and patient population | Not selected |
| T1 — Mechanism | Primary evidence supporting causal relevance in that context | Literature mapping incomplete |
| T2 — Target rationale | Selectivity, biological role, counter-evidence and safety concerns assessed | Not established |
| T3 — Candidate concept | Specific intervention concept with novelty and IP landscape review | Not proposed |
| T4 — Experimental validation | Qualified, supervised experiments with controls and reproducible results | Not performed |
| T5 — Preclinical translation | Appropriate safety, exposure, efficacy and model relevance | Not performed |
| T6 — Clinical development | Regulated human research and clinical outcome evidence | Not performed |

No gate is passed by writing code or generating an AI summary. Any future wet-lab or human-related work requires qualified institutional supervision, appropriate approvals and safety oversight.

## 8. Falsification conditions

The platform hypothesis is weakened or rejected if:
- Existing tools achieve equivalent traceability and context preservation.
- Experts see no decision improvement.
- Context/cell/model classifications are unreliable.
- The framework increases unsupported claims or false confidence.
- The benchmark cannot be reproduced by an independent team.

The biological heterogeneity hypothesis must be revised if primary evidence does not support consistent context- or state-dependent differences, or if findings fail replication.

## 9. Current conclusion

**Scientific validation: not completed.** The validation plan is now specified at the protocol level. Execution requires a verified source set, independent reviewers and a completed benchmark.

**Therapeutic discovery: not completed.** The literature landscape identifies competing research and translational gaps but does not nominate an Elstella drug candidate. Biological efficacy cannot be established from literature synthesis or software alone.
