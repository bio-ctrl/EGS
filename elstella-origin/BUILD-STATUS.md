# BUILD STATUS — ELSTELLA RESEARCH ATLAS

## Implemented in the existing prototype

- Interactive tab navigation.
- Seeded starter bibliography marked unreviewed.
- Evidence record creation and editing.
- Search across evidence records.
- Hypothesis register and hypothesis creation.
- Browser-local persistence using localStorage.
- CSV evidence export.
- JSON workspace backup and import.
- Reset of local workspace with confirmation.
- Literature search and bibliographic metadata import through Europe PMC.
- Abstract sentence candidate extraction with explicit unverified labels.
- Server-side AI synthesis endpoint with evidence-ID citation constraints and provider credentials kept off the client.
- Optional Supabase authentication and per-account workspace sync adapter.
- Supabase schema with row-level security.
- Evidence metadata completeness gate with unit tests.
- Node built-in test suite and GitHub Actions workflow.
- Company identity, therapeutic strategy, MITOS research charter, data-governance, and roadmap documentation.

## Current strategic role

The Research Atlas is intended to support Elstella Intelligence: a provenance-first research workspace for organizing literature, public-data metadata, disease context, hypotheses, and evidence status. It is not a validated AI discovery engine, clinical decision system, or drug-design platform.

PROJECT MITOS is the initial literature-led research priority. The therapeutic portfolio also identifies neuromuscular/muscle medicine and kidney/organ restoration as future areas. These are not active drug-development programs.

## Known limitations

- The prototype was originally organized around CARDIA/ORIGIN; the interface and data model still require a full product-level review to become a coherent multi-program workspace.
- Starter records remain unreviewed leads until metadata and source content are checked.
- Europe PMC search requires network access and has not been fully browser-tested.
- AI synthesis requires a configured compatible provider endpoint and a running Node server. AI output can be incorrect and must be checked against original sources.
- Supabase sync requires a separately provisioned project, schema execution, and user configuration. It supports same-account cross-device sync, not shared team collaboration.
- No production database has been provisioned by this repository.
- No browser-level end-to-end test or external security audit has been completed.
- Abstract extraction produces candidate snippets only; no claim is automatically marked verified.
- No validated evidence-quality scoring exists.
- No formal scientific or clinical validation has been completed.
- Existing CARDIA literature materials are rapid research artifacts, not a systematic review or validated therapeutic program.
- Evidence completeness tests check required metadata; they do not verify source truth or scientific quality.
- No therapeutic discovery, drug candidate, or clinical product has been completed.

## Run and test

Use Node.js 20.6 or newer. Copy .env.example to .env, configure an AI provider only if desired, run npm start, then open http://localhost:4173. Run npm test for unit tests.

## Data safety

Do not enter patient-identifiable information. Export JSON backups because browser-local storage can be cleared. Imported JSON replaces the local workspace after confirmation. AI requests send selected evidence records to the configured external provider only after explicit confirmation. Do not commit .env.

## Remaining milestones

1. Run the automated test suite and verify the resulting GitHub Actions status.
2. Perform a browser-level smoke test of the Research Atlas.
3. Complete the PROJECT MITOS literature and existing-treatment landscape.
4. Build a traceable public-dataset inventory.
5. Compare candidate disease areas using transparent unmet-need and feasibility criteria.
6. Obtain qualified independent scientific critique.
7. Benchmark the Research Atlas against a conventional research workflow.
8. Decide whether MITOS advances, is revised, or is stopped.

Therapeutic discovery and biological validation are scientific programs, not software checkboxes.
