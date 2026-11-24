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
- Company identity, GENESIS research foundation, data-governance, and roadmap documentation.

## Known limitations

- The prototype was originally organized around CARDIA/ORIGIN; the interface and data model still require a full product-level review to become a coherent multi-program GENESIS-first workspace.
- Europe PMC search requires network access and has not been fully browser-tested.
- AI synthesis requires a configured compatible provider endpoint and a running Node server. AI output can be incorrect and must be checked against original sources.
- Supabase sync requires a separately provisioned project, schema execution, and user configuration. It supports same-account cross-device sync, not shared team collaboration.
- No production database has been provisioned by this repository.
- No browser-level end-to-end test or external security audit has been completed.
- Abstract extraction produces candidate snippets only; no claim is automatically marked verified.
- No validated evidence-quality scoring exists.
- Existing starter citations remain unreviewed leads until their metadata and source content are checked.
- No formal scientific or clinical validation has been completed.
- CARDIA literature materials are rapid research artifacts, not a systematic review or validated therapeutic program.
- Evidence completeness tests check required metadata; they do not verify source truth or scientific quality.
- No therapeutic discovery, drug candidate, or clinical product has been completed.

## Run and test

Use Node.js 20.6 or newer. Copy .env.example to .env, configure an AI provider only if desired, run npm start, then open http://localhost:4173. Run npm test for unit tests.

## Data safety

Do not enter patient-identifiable information. Export JSON backups because browser-local storage can be cleared. Imported JSON replaces the local workspace after confirmation. AI requests send selected evidence records to the configured external provider only after explicit confirmation. Do not commit .env.

## Remaining milestones

1. Run the automated test suite and verify the resulting GitHub Actions status.
2. Perform a browser-level smoke test of the Research Atlas.
3. Verify source metadata and manually review every imported abstract candidate.
4. Complete the GENESIS literature search and dataset inventory.
5. Benchmark the Research Atlas against a conventional review workflow.
6. Obtain qualified independent scientific critique.
7. Decide whether GENESIS advances, is revised, or is stopped.
8. Consider any experimental research only through qualified institutional oversight and supervision.

Therapeutic discovery and biological validation are scientific programs, not software checkboxes.
