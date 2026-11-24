# RESEARCH DATA GOVERNANCE

## Scope
This policy applies to literature records, public research-data metadata, analysis notes, code, and research outputs stored in this repository.

## Permitted initial material
- Public bibliographic metadata.
- Lawfully accessible scientific publications and abstracts, subject to their terms.
- Public dataset metadata and data accessed in accordance with repository terms.
- Original analysis code and non-sensitive research notes.
- Synthetic examples created solely to test software behavior.

## Excluded material
- Patient-identifiable information.
- Confidential, proprietary, or access-restricted data without documented permission.
- Private health records or personal genetic information.
- Secrets, access tokens, passwords, API keys, or private credentials.
- Biological samples or experimental records from work lacking appropriate institutional authorization.

## Provenance requirements
For every imported source or dataset, record:
- Originating repository or publisher.
- DOI, accession, or other stable identifier.
- Canonical source URL.
- Retrieval date.
- License or data-use terms, where stated.
- Relevant organism, tissue, stage, assay, and cohort metadata.
- Any transformations performed.
- Reviewer and verification status.

## Data handling
- Keep secrets in local environment variables; never commit .env.
- Minimize the amount of data copied into the repository.
- Prefer metadata and source links over redistributing full-text material.
- Preserve original identifiers and document transformations.
- Keep raw inputs separate from derived outputs.
- Record software versions and analysis parameters for reproducibility.
- Remove accidental secrets or personal information promptly and follow the appropriate incident process.

## Review labels
Use explicit states such as unreviewed, metadata-checked, full-text-reviewed, independently-checked, and excluded. Do not mark a source or claim as verified solely because it was imported by software.

## Oversight
Any future human-subject research, use of sensitive human data, animal research, biological samples, or laboratory activity requires qualified institutional review, appropriate permissions, and supervision before work begins.
