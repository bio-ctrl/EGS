# PROJECT CARDIA / NEXUS
## Research thesis: reproducibility of spatial cardiac fibroblast mechanosensing signals

**Organization:** ELSTELLA & CO. — Biological Restoration & Therapeutics  
**Program:** PROJECT CARDIA  
**Research initiative:** NEXUS  
**Document status:** Proposed computational research protocol; not executed, peer reviewed, preregistered, or validated  
**Version:** 0.1  
**Prepared:** 2026-11-24

---

## 1. Executive thesis

Elstella will investigate whether published human cardiac datasets can support reproducible, disease-context-aware analysis of fibroblast mechanosensing programs in spatially defined fibrotic tissue regions.

The proposed work is not to build another general cardiac atlas, generate an ungrounded AI target list, or claim a new antifibrotic treatment. It is to test a narrower question:

> **Across independent human cardiac datasets, are fibroblast mechanosensing-associated molecular programs consistently enriched in specific spatial tissue niches and disease contexts, and can those associations be distinguished from cohort, platform, anatomical and cell-composition effects?**

The potential contribution is a transparent, reproducible cross-study analysis that reports both positive and negative results, preserves provenance, and makes uncertainty visible.

**No claim is made that nobody else is investigating this.** The novelty question remains open pending a formal literature, software and intellectual-property landscape review.

## 2. Why this question is worth testing

Cardiac fibrosis is not a single uniform tissue state. Human disease differs by cause, anatomical region, stage and cellular composition. Fibroblast states interact with immune, vascular and myocardial cells, while the mechanical environment can influence stromal-cell behavior.

Recent work makes a generic atlas strategy uncompetitive:

- A 2026 integrated human-heart atlas combined more than 2.4 million nuclei from 209 individuals, eight anatomical regions and multiple healthy/disease states. It reported disease-associated fibroblast populations and cross-study harmonization.
- A 2026 JACC: Basic to Translational Science review describes spatial transcriptomics, single-cell integration and cardiac-specific analytical pitfalls. It identifies cross-patient reproducibility, spatial integration and mechanosensing as important technical/scientific considerations.
- Existing work has already linked cardiac fibroblast states, immune-cell interactions and mechanosensitive pathways to fibrotic remodeling.

NEXUS must therefore answer a question that goes beyond cataloguing cell types: **how robustly can a defined mechanosensing-associated signal be reproduced across independent human cohorts and spatial contexts?**

## 3. Novelty hypothesis — deliberately provisional

**Working hypothesis:** Published human cardiac spatial and single-cell datasets may contain mechanosensing-associated fibroblast signals that are reported inconsistently across studies because disease context, anatomical location, cell-state definitions, assay platform and cohort effects are not handled uniformly.

A reproducible, context-aware cross-cohort analysis may clarify:
1. Which reported associations replicate across independent cohorts.
2. Which associations are specific to a disease context or tissue region.
3. Which findings disappear under alternative cell-state definitions or analytical methods.
4. Where the available human evidence is too sparse or incompatible to support a conclusion.

This is a hypothesis about evidence quality and biological association—not proof of causal mechanism or therapeutic action.

### What would make this meaningfully differentiated?

The contribution would need to demonstrate, against existing atlases and published analyses, at least one of the following:
- A previously unreported, independently replicated association between a clearly defined fibroblast state, spatial niche and mechanosensing-related program.
- A reproducible explanation for why a prominent published association fails to generalize across disease contexts or cohorts.
- A validated analysis workflow that materially improves cross-study reproducibility, uncertainty reporting or expert research decisions compared with existing methods.

If none is demonstrated, Elstella must report that the proposed novelty was not established.

## 4. Research objectives

**Objective A — Dataset feasibility**
- Inventory relevant public human cardiac single-cell, single-nucleus and spatial transcriptomic datasets.
- Record accession, cohort size, disease context, anatomical region, assay, sample metadata, publication, data-use terms and availability.
- Determine whether enough independent cohorts contain compatible metadata for a meaningful comparison.
- Stop or narrow the project if suitable independent datasets are unavailable.

**Objective B — Context-aware evidence map**
- Keep ischemic injury, chronic heart failure, HFpEF and cardiomyopathy contexts distinct.
- Keep infarct, border-zone and remote tissue regions distinct when the source data support those labels.
- Preserve the original authors' cell-state labels and record any harmonized labels separately.
- Distinguish human evidence from animal, in-vitro and engineered-tissue evidence.

**Objective C — Reproducibility analysis**
- Test a pre-specified, literature-derived mechanosensing-associated gene-program definition.
- Evaluate whether the signal is present in independently generated datasets.
- Compare results across reasonable alternative cell annotations and analysis choices.
- Report effect sizes, uncertainty, missingness and between-cohort heterogeneity.
- Use held-out cohorts where possible; do not use the same cohort for both discovery and claimed validation.

**Objective D — Independent review**
- Ask qualified cardiovascular and computational-biology reviewers to assess the protocol, biological interpretation and limitations.
- Preserve disagreements and revise the analysis transparently.
- Do not describe internal review as external validation.

## 5. Proposed computational study design

This is a literature/data-analysis project using appropriately accessible, de-identified public research datasets. It does not require Elstella to collect human samples or conduct laboratory experiments.

### Phase 0 — Feasibility gate
1. Search the literature and public repositories for relevant human cardiac datasets.
2. Verify each dataset's source publication, access conditions and metadata.
3. Create a dataset compatibility matrix.
4. Select only datasets with sufficient provenance and compatible variables.
5. Document exclusions and reasons.

**Stop condition:** If fewer than two genuinely independent, sufficiently compatible human cohorts are available for the primary comparison, do not claim cross-cohort replication. Reframe as a feasibility/methods study or stop.

### Phase 1 — Pre-specification
Before examining comparative results:
- Freeze the primary research question.
- Define disease-context strata.
- Define eligible tissue regions and cell populations.
- Specify the mechanosensing-associated gene-program source and rationale.
- Specify primary outcomes, sensitivity analyses and exclusion rules.
- Record the analysis plan and version.

Do not select gene sets or thresholds after looking for the most favorable result.

### Phase 2 — Analysis
- Use source datasets and their documented processing pipelines where possible.
- Account for patient/sample as the biological unit; do not treat individual cells as independent patients.
- Preserve cohort and platform identifiers.
- Quantify cell-state and spatial associations only where source data support them.
- Compare alternative annotation and normalization choices.
- Separate descriptive associations from causal claims.

### Phase 3 — Independent replication
- Evaluate the pre-specified signal in held-out or otherwise independent cohorts.
- Report failures to replicate.
- Conduct sensitivity analyses for disease mix, anatomical region, assay type and cell-state definition.
- Do not pool incompatible data merely to increase sample size.

### Phase 4 — Interpretation
Classify each result as:
- Replicated association.
- Context-specific association.
- Cohort/platform-sensitive association.
- Not replicated.
- Not assessable with current data.

No category establishes causality or therapeutic efficacy.

## 6. Primary outcomes and success criteria

The primary outcome is **cross-cohort reproducibility of the pre-specified association**, not the number of candidate genes discovered.

Report:
- Direction and magnitude of association in each cohort.
- Between-cohort consistency and uncertainty.
- Sensitivity to cell-state definitions and analysis choices.
- Spatial-context consistency where spatial data are available.
- Missing metadata and dataset limitations.
- Independent reviewer assessment of biological plausibility.

Success requires a pre-specified result that replicates in independent data and survives reasonable sensitivity analyses. Numerical thresholds must be set before outcome inspection with qualified methodological input.

## 7. Falsification and stop criteria

The central hypothesis is weakened or rejected if:
- The proposed association is not observed in independent cohorts.
- The signal is explained by cohort, platform, anatomical sampling or cell-composition differences.
- Results change materially under reasonable annotation or analysis choices.
- Relevant public datasets lack the metadata needed to answer the question.
- Existing publications or tools already provide the same reproducible result.
- Independent reviewers find the interpretation unsupported.

A null result is a valid research outcome. Do not modify the question after seeing the results and present it as the original hypothesis.

## 8. Competitive and prior-art landscape

This is an initial map, not a complete competitor analysis.

| Existing work | What it already contributes | Implication for NEXUS |
|---|---|---|
| HeartMap (2026), integrated atlas of 2.4M nuclei / 209 individuals | Large-scale human cardiac cell atlas and cross-study integration | Do not build another general atlas; benchmark against it |
| 2026 JACC spatial-transcriptomics review | Cardiac-aware spatial workflows, multimodal integration, technical pitfalls and reproducibility recommendations | NEXUS must extend beyond summarizing known workflow advice |
| Human cardiac fibrosis single-cell/spatial studies | Fibroblast heterogeneity and immune–fibroblast interactions | Do not claim these phenomena as new |
| Existing spatial and single-cell analysis software | Cell annotation, spatial analysis, integration and visualization | Benchmark existing tools before building custom software |

### Required prior-art review
Before making any public novelty claim:
1. Search primary literature using a documented search protocol.
2. Search software repositories and method papers for equivalent cross-cohort workflows.
3. Review relevant patents with qualified IP counsel before any commercialization or disclosure strategy.
4. Ask independent experts whether the proposed contribution is already known.
5. Publish a novelty statement that is no broader than the evidence supports.

## 9. Risks and controls

| Risk | Control |
|---|---|
| Too few comparable human datasets | Dataset feasibility gate before analysis |
| Batch effects mistaken for biology | Cohort-aware analysis and independent replication |
| Cell annotations differ between studies | Preserve native labels; document harmonization and sensitivity analyses |
| Spatial data are sparse or incompatible | Separate spatial and non-spatial evidence; do not imply spatial validation where absent |
| Mechanosensing gene set is arbitrary | Pre-specify from cited literature and test alternatives transparently |
| Cell-level pseudoreplication | Use patient/sample-aware statistics |
| Attractive but false AI-generated interpretation | Trace every claim to source data and code; expert review |
| Existing work already solves the problem | Benchmark first; stop or materially differentiate |
| Computational association mistaken for therapeutic proof | Explicitly prohibit efficacy, target-validation and clinical claims |

## 10. Deliverables

1. Dataset inventory and compatibility matrix.
2. Versioned literature search and screening log.
3. Pre-specified analysis protocol.
4. Reproducible code and environment documentation.
5. Cohort-level results with uncertainty and negative findings.
6. Sensitivity-analysis report.
7. Independent-review record.
8. Novelty and competitive assessment.
9. Go / revise / stop decision memo.

## 11. Execution sequence

| Stage | Deliverable | Gate |
|---|---|---|
| 1 | Dataset inventory | Are two or more independent human cohorts genuinely comparable? |
| 2 | Frozen protocol | Are question, gene program and outcomes pre-specified? |
| 3 | First-cohort analysis | Can the workflow run reproducibly? |
| 4 | Independent cohort analysis | Does the result replicate? |
| 5 | Sensitivity and expert review | Is the interpretation robust and useful? |
| 6 | Final decision memo | Is there a defensible research contribution? |

No timeline should be represented as guaranteed until dataset access and technical feasibility are established.

## 12. What this does—and does not—mean for Elstella

If successful, NEXUS could become an early research capability within PROJECT CARDIA and inform a broader Elstella approach to evidence-grounded biological discovery.

It does **not** currently establish:
- A new biological mechanism.
- A validated therapeutic target.
- A drug candidate or medicine.
- Patentable novelty.
- Clinical utility.
- Investor readiness or a funding commitment.

The next credibility milestone is a reproducible result, independent scientific feedback and a defensible explanation of what Elstella contributed that existing research did not.

## 13. Initial source set

1. Datar Y, et al. **An integrated cell atlas of 2.4 million cardiac cells across 209 individuals in health and disease.** *Nature Cardiovascular Research* (2026). https://www.nature.com/articles/s44161-026-00831-5
2. Tao H, et al. **Applying Spatial Transcriptomics to the Human Heart: A Practical Guide for Translational Studies.** *JACC: Basic to Translational Science* (2026). https://www.jacc.org/doi/10.1016/j.jacbts.2026.101730
3. **Dynamic molecular atlas of cardiac fibrosis at single-cell resolution shows CD248 in cardiac fibroblasts orchestrates interactions with immune cells.** *Nature Cardiovascular Research* (2025). https://www.nature.com/articles/s44161-025-00617-1
4. **A large-scale single-nucleus resource reveals a cardiomyocyte-like fibroblast and stage-specific remodeling across cardiomyopathies.** (2026). https://pmc.ncbi.nlm.nih.gov/articles/PMC13465476/

These sources establish the competitive and scientific context; they do not by themselves validate the NEXUS hypothesis.

---

**Decision requested from reviewers:** Is the question sufficiently distinct, feasible with available public human data, and worth testing? What existing study or tool most closely duplicates it? What result would convince you that the proposed contribution is real?
