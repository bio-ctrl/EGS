# CARDIA / NEXUS — Feasibility & Novelty Audit 001

**Prepared:** 2026-11-24  
**Status:** Desk-based source and dataset-metadata audit completed; raw expression matrices not reanalysed.  
**Decision:** Original NEXUS framing is not sufficiently differentiated. Narrow or stop before building a computational analysis pipeline.

## Executive result

The original NEXUS thesis proposed a context-aware analysis of spatial cardiac fibroblast states and mechanosensing signals across disease contexts. A first-pass audit found substantial direct prior work:

1. HeartMap already integrates nine human cardiac single-nucleus datasets, over 2.47 million nuclei from 209 individuals, eight anatomical regions and seven disease/healthy states. It reports disease-associated activated fibroblast populations and cross-study signatures.
2. Youness et al. (Genome Medicine, 2025) directly study how location and aetiology shape human cardiac fibroblast activation. They report nine fibroblast states and map them to interstitial, adventitial/vascular and scar regions using a published spatial transcriptomic dataset.
3. Lee et al. (European Heart Journal, 2025) directly integrate histology, clinical context and spatial expression in human cardiomyopathy tissue.

**Conclusion:** The broad idea of context-aware, spatially resolved cardiac fibroblast analysis is already established. Elstella must not describe that broad idea as novel.

A narrower, potentially useful question remains: whether a pre-specified mechanosensing-associated fibroblast program is robust across independent human cohorts and assay platforms after accounting for disease context, anatomical/histological region, cell-composition and platform-specific measurement limitations. This narrower question is still provisional and may also overlap existing work.

## 1. Source and dataset audit

| Resource | What the source establishes | Relevance | Limitation / audit note |
|---|---|---|---|
| HeartMap, SCP3689; Datar et al., Nature Cardiovascular Research (2026) | Integrates nine studies, >2.47M nuclei, 209 individuals, eight cardiac regions and seven disease/healthy states; reports activated fibroblast populations and cross-study disease signatures | Strong single-nucleus reference for disease/context comparisons | Not itself a spatial transcriptomics cohort. It already makes a generic cross-study atlas proposition non-differentiated. |
| GSE298023; Youness et al., Genome Medicine (2025) | Human LV snRNA-seq in non-failing, DCM, ICM and ICM scar tissue; paper reports nine fibroblast states and spatial mapping to interstitial, vascular/adventitial and scar regions | Direct overlap with fibroblast state, aetiology and spatial niche framing | The paper already performs the central state-to-space mapping using a previously published spatial dataset. GEO currently lists 18 samples, while the paper methods describe 20 samples (4 NF + 6 DCM + 5 ICM + 5 ICM-scar). Resolve this discrepancy against supplementary materials before analysis. |
| GSE271676; Lee et al., European Heart Journal (2025) | Spatial GeoMx data from 44 participants, 90 tissue cores and 178 AOIs across cardiomyopathies and histological features | Independent human spatial cohort with fibrosis annotations | Only 14 fibroblast AOIs are listed in the full study table (11 LV, 3 RV); fibroblast segmentation/enrichment was modest and authors state this constrained fibroblast comparisons. This is a major limitation for fibroblast-specific replication. |
| Kuppe et al., Nature (2022), Zenodo 6578047 / CellxGene collection | Processed human myocardial-infarction snRNA-seq, snATAC-seq and Visium spatial data; Zenodo lists 25.4 GB across 25 files | Spatial reference for infarct-zone and border-zone tissue; potential independent cohort for a narrowly defined post-MI analysis | Large downloads and platform/context differences. Importantly, this is the spatial resource used by Youness et al. for state-to-space mapping, so it cannot be counted as an independent replication of that paper's spatial mapping. |

## 2. Direct overlap / novelty stress test

### Claim A: “Cardiac fibroblasts differ by disease context and tissue location.”
**Result: Already directly supported in prior work.** Youness et al. report aetiology- and location-associated fibroblast states and distinguish scar from interstitial fibrosis. Do not present this as Elstella's discovery.

### Claim B: “Spatial transcriptomics can add histological context beyond clinical diagnosis.”
**Result: Already directly investigated.** Lee et al. analyze histology-specific expression in human cardiomyopathy tissue and report that histology-based associations can differ from clinical-phenotype-based analyses.

### Claim C: “A large integrated human cardiac atlas can identify disease-associated fibroblast populations across cohorts.”
**Result: Already demonstrated.** HeartMap provides a large multi-study human cardiac reference and identifies activated fibroblast niches.

### Claim D: “A specific mechanosensing-associated fibroblast program reproducibly localizes across independent human spatial cohorts after strict context and platform controls.”
**Result: Not established by this desk audit.** This is the only part that remains a possible research question. The current audit did not inspect raw expression matrices or run statistical tests. Existing work discusses mechanical cues and fibroblast activation, so novelty is not assumed.

## 3. Feasibility findings

- A useful human single-nucleus reference exists (HeartMap and GSE298023).
- Public spatial resources exist, but they differ in assay (Visium vs GeoMx), disease context, region definitions and resolution.
- GSE271676 includes many AOIs overall but few fibroblast AOIs. The paper itself notes limitations in fibroblast segmentation and comparison.
- GSE298023's published spatial mapping uses a previously published spatial resource; reusing that same resource does not create independent replication.
- Kuppe et al. provide spatial data for human myocardial infarction, but its post-infarction context cannot be pooled indiscriminately with DCM, HCM or end-stage HF.
- The GSE298023 18-versus-20 sample-count discrepancy must be reconciled.
- No raw count matrix has been downloaded, harmonized or analyzed in this audit. No gene-program score, effect size, p-value, replication statistic or biological result is claimed.

**Preliminary feasibility rating:** Conditional / moderate-to-low for a broad multi-context human spatial replication study; potentially workable for a narrow post-MI or platform-comparison pilot if the metadata and sample-level independence are confirmed.

## 4. Recommended revised research question

> **How reproducibly can a pre-specified cardiac fibroblast mechanosensing-associated expression program be detected across independent human cardiac datasets and assay platforms, and how much do disease context, tissue region, cell annotation and platform limitations alter that result?**

This is a methods/reproducibility question—not a new mechanism or therapeutic target.

### Proposed primary comparison
- Discovery/reference: a clearly defined, source-cited fibroblast program from published literature, frozen before outcome inspection.
- Single-nucleus context: HeartMap and/or GSE298023, preserving sample-level and disease-context metadata.
- Spatial context: GSE271676 and Kuppe et al. Visium data, only where cell/region annotation and data quality support the comparison.
- Independent validation: a cohort must be genuinely independent of the discovery analysis. Do not count a reused dataset twice.

### Required safeguards
1. Define the gene program and rationale before analyzing outcome data.
2. Treat patient/sample—not individual nuclei or spots—as the biological replication unit.
3. Keep DCM, ICM scar, ICM non-scar, HCM and control contexts distinct.
4. Preserve original cell and tissue annotations; document harmonization separately.
5. Model or report platform effects rather than treating Visium, GeoMx and snRNA-seq as interchangeable.
6. Use negative controls and sensitivity analyses.
7. Report failed replication and non-assessable comparisons.
8. Have a qualified computational cardiovascular researcher review the protocol and analysis.

## 5. Go / revise / stop decision

**Decision: REVISE. Do not proceed with the original broad NEXUS claim.**

Proceed to a small computational feasibility pilot only if:
- The GSE298023 sample-count discrepancy is resolved.
- Public data files and permitted reuse conditions are confirmed.
- At least two genuinely independent human cohorts support the chosen comparison.
- Fibroblast and spatial annotations are adequate for the pre-specified endpoint.
- The analysis can be performed at sample level with defensible platform handling.

Stop or reframe as a methods note if these conditions fail. Do not claim a novel biological discovery from an atlas re-analysis alone.

## 6. What has actually been tested

**Completed:** Literature/source audit, public dataset identification, study-design review, sample/assay metadata comparison, direct-overlap analysis, and feasibility decision.

**Not completed:** Downloading raw/processed expression matrices, quality control, harmonization, gene-program scoring, differential expression, spatial localization statistics, independent replication, or expert review.

This distinction is mandatory. A literature audit is not computational validation.

## 7. Source references

1. Datar Y, et al. *An integrated cell atlas of 2.4 million cardiac cells across 209 individuals in health and disease.* Nature Cardiovascular Research (2026). https://www.nature.com/articles/s44161-026-00831-5 ; SCP3689: https://singlecell.broadinstitute.org/single_cell/study/SCP3689/an-integrated-cell-atlas-of-2-4-million-cells-across-209-individuals-in-health-and-disease
2. Youness M, et al. *Location and aetiology are determinants of fibroblast activation and heterogeneity in the failing human heart.* Genome Medicine (2025). https://doi.org/10.1186/s13073-025-01580-z ; GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE298023
3. Lee SE, et al. *Spatial transcriptional landscape of human heart failure.* European Heart Journal (2025). https://doi.org/10.1093/eurheartj/ehaf272 ; GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE271676
4. Kuppe C, et al. *Spatial multi-omic map of human myocardial infarction.* Nature (2022). https://doi.org/10.1038/s41586-022-05060-x ; Zenodo: https://doi.org/10.5281/zenodo.6578047

**Integrity statement:** This audit does not establish that the revised question is novel. It identifies the minimum next test needed to decide whether the question deserves computational execution.
