# VYREON — Research Gate 001
## CARDIA therapeutic hypothesis qualification plan

**Program:** Project CARDIA  
**Working concept name:** VYREON / CARDIA-01  
**Stage:** Research concept only; no drug candidate, molecule, target, formulation, efficacy, or safety profile has been established.  
**Document status:** Prospective analysis plan. Not a completed analysis, systematic review, registered protocol, or experimental study.

---

## 1. Decision this research gate must answer

Does published human cardiac data support a reproducible, disease-context-specific fibroblast state or expression program associated with ischemic myocardial scarring, sufficiently robust to justify further therapeutic hypothesis development?

This is a research-prioritization question. It is **not** a claim that a particular intervention can reverse fibrosis.

### Primary question

Across independent human cardiac datasets, are pre-specified fibroblast-associated signals related to ischemic scar/remodeling reproducible after accounting for cohort, tissue region, assay platform, cell annotation, and sample composition?

### Null / stop position

If the signal is not reproducible, cannot be separated from technical or sampling effects, or is already fully explained by existing work, Elstella must revise or stop this specific hypothesis. A negative result is a valid deliverable.

---

## 2. Why this gate comes before target selection

Cardiac fibrosis is not one uniform biological state. Disease cause, anatomical region, timing, cellular composition, and measurement platform can change the observed signal. A therapeutic concept built around an assumed target before checking those differences risks being scientifically arbitrary.

VYREON therefore has no nominated molecular target at this stage. No compound structure, sequence, dose, formulation, route of administration, or synthesis proposal is specified.

---

## 3. Candidate public data resources

These are candidate sources for feasibility review, not confirmation that all required files are available, compatible, or suitable.

| Resource | Potential role | Critical limitation to resolve |
|---|---|---|
| GSE298023 | Human failing-heart cohort with disease and tissue-context information; assess whether ischemic scar and comparator groups can be separated reliably | Reconcile GEO sample metadata with the paper and supplements; verify processed matrix availability, sample-level labels, and independent biological units |
| GSE271676 | Spatial transcriptional dataset for cross-platform/context assessment | Determine whether fibroblast-enriched spatial observations are sufficient; spatial regions/AOIs are not automatically independent patients |
| HeartMap / SCP3689 | Broader human heart cell-atlas reference and external context | Large, heterogeneous integrated resource; determine which underlying cohorts overlap with other sources before calling it independent validation |
| Kuppe et al. 2022 spatial MI resource | Historical spatial reference for myocardial infarction | Do not count a dataset reused by a later publication as independent replication |

### Source links

- GSE298023: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE298023
- GSE271676: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE271676
- HeartMap / SCP3689: https://singlecell.broadinstitute.org/single_cell/study/SCP3689/an-integrated-cell-atlas-of-2-4-million-cells-across-209-individuals-in-health-and-disease
- Kuppe et al. 2022: https://doi.org/10.1038/s41586-022-05060-x
- Youness et al. 2025: https://doi.org/10.1186/s13073-025-01580-z
- Lee et al. 2025: https://doi.org/10.1093/eurheartj/ehaf272

Before analysis, record access date, accession version, paper version, file name, file size, checksum where possible, license/usage terms, and exact sample-to-donor mapping. Resolve cohort overlap explicitly.

---

## 4. Pre-analysis lock

Do not inspect comparative outcomes and then invent a signature to fit them.

Before running a biological comparison, create and review a dated analysis specification containing:

1. Exact disease contrast and tissue context.
2. Inclusion and exclusion rules at the donor/sample level.
3. Cell annotation rules and uncertainty labels.
4. A literature-derived candidate signature with every feature linked to a source and rationale.
5. A primary outcome and a small number of secondary outcomes.
6. Confounders and sensitivity analyses.
7. Rules for missing data and platform incompatibility.
8. A plan for independent replication.
9. A record of all deviations from the specification.

The candidate signature must be selected from published evidence before examining the held-out validation result. Do not select genes or thresholds because they produce a preferred result.

---

## 5. Analysis principles

The computational analysis should be performed by appropriately qualified collaborators using lawful, public, de-identified research data.

- Treat the donor/patient as the biological unit wherever donor-level data are available. Cells, nuclei, image regions, and assay areas from one donor are not independent patients.
- Preserve the distinction between discovery and independent validation cohorts.
- Do not merge cohorts blindly. Document platform, tissue region, disease etiology, processing, annotation, and batch differences.
- Use sample-level summaries or appropriate models that account for within-donor clustering.
- Report effect estimates, uncertainty intervals, sample counts, missingness, and sensitivity analyses—not only p-values.
- Keep human tissue, animal models, and in-vitro models distinct. They answer different questions.
- Report negative and contradictory findings.
- Maintain a traceable path from each reported result to source dataset, file, sample metadata, code version, and analysis configuration.

This plan does not prescribe laboratory procedures or experimental drug testing.

---

## 6. Outcomes and decision rules

### Advance to therapeutic hypothesis development only if

- Sample identities, donor mapping, and disease labels are sufficiently reliable.
- The pre-specified signal is measurable in more than one suitable human dataset.
- Direction and interpretation are reasonably consistent across independent cohorts or the reasons for disagreement are explainable.
- Results are not driven solely by one cohort, one platform, one tissue region, or a small number of donors.
- The signal adds a meaningful, defensible research insight beyond what the cited publications already report.
- An independent cardiovascular researcher considers the result biologically interpretable.

### Revise if

- A signal appears context-specific but the available cohorts differ materially.
- Metadata are incomplete but can be resolved from supplements or source investigators.
- The proposed signature is too broad or cell annotation is uncertain.
- The analysis is technically feasible but independent validation is underpowered.

### Stop this hypothesis if

- No reproducible signal is found.
- Apparent differences are explained by cohort, region, platform, cell composition, or annotation artifacts.
- The available datasets are not independent enough to support replication.
- Existing publications already establish the proposed result and no meaningful new question remains.
- Results cannot be independently reproduced.

No outcome from this computational gate alone establishes causality, therapeutic actionability, safety, or clinical benefit.

---

## 7. VYREON development boundary

VYREON is currently a **therapeutic concept label** attached to a research question. It is not a drug candidate.

A future candidate nomination would require, at minimum:

- A validated disease-relevant biological mechanism.
- A specific target or intervention rationale supported by evidence.
- A defensible differentiation and intellectual-property assessment.
- Qualified expert review.
- Appropriate institutional oversight and supervised experimental evidence.
- Independent assessment of safety, selectivity, and translational relevance.

No target, molecule, formulation, dosing, or manufacturing claim should be added merely to make the concept appear more advanced.

---

## 8. Required deliverables for Research Gate 001

1. Dataset inventory with source URLs, access dates, file metadata, checksums, and donor/sample mapping status.
2. Cohort-overlap and independence assessment.
3. Locked analysis specification and signature provenance table.
4. Reproducible, version-controlled analysis code and environment record.
5. Results report including negative findings and sensitivity analyses.
6. Independent reviewer comments and documented responses.
7. A signed decision: advance, revise, or stop.

### Current status

**Not started at matrix level.** The prior NEXUS work was a literature and metadata feasibility audit. No raw expression matrix has yet been downloaded or analyzed for this gate. This document defines the next test; it does not report a result.

---

## 9. Scientific integrity statement

Elstella makes no claim that VYREON works, that it has discovered a drug, that its proposed research direction is novel, or that it can treat or reverse cardiac fibrosis. The only present claim is that Elstella has defined a testable research question and a falsifiable plan for evaluating whether further work is justified.
