# ORIGIN ATLAS — DATA DICTIONARY

## Evidence record

| Field | Meaning | Rule |
|---|---|---|
| id | Unique record identifier | Stable and unique |
| program | ORIGIN, CARDIA or BIOPATH | Controlled vocabulary |
| title | Verified publication title or explicit working label | Mark unverified labels |
| url | DOI, PubMed or publisher URL | Use canonical source where possible |
| identifier | DOI, PMID or other identifier | Verify against source |
| context | Disease / biological context | Do not infer beyond source |
| evidenceClass | Descriptive study type | Not a quality score |
| model | Species, cohort, tissue or experimental model | State missingness |
| cell | Cell population or state | Use source's definition |
| claim | Paraphrased source finding | Must include exact source location |
| location | Page, figure, table, section or result identifier | Required before verified status |
| status | Review workflow state | Do not label verified without review |
| limitations | Limitations, contradictions and caveats | Include source and reviewer notes |

## Hypothesis record

- **id:** unique identifier.
- **program:** research program.
- **title:** concise label.
- **statement:** testable proposition.
- **test:** proposed comparison or observation.
- **falsifier:** result that would weaken or reject the hypothesis.
- **status:** proposed, under review, supported, weakened, rejected or closed.

## Provenance rule

A claim is not considered verified solely because a source URL exists. Verification requires confirming the publication identity, reading the relevant source content, recording the exact location and checking the paraphrase against the source. Important claims should receive a second review.

## Missing data

Use explicit values such as “not reported,” “not applicable” or “not yet extracted.” Do not silently fill missing fields with assumptions.
