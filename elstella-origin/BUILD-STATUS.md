# BUILD STATUS — ELSTELLA INTELLIGENCE / RESEARCH ATLAS

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

## Current strategic role

The Research Atlas is the first product prototype for Elstella Intelligence. It is intended to support Division 01, Cellular & Mitochondrial Health, and later divisions only when activated through their own evidence gates. It is a provenance-first research workspace, not a validated AI discovery engine, clinical decision system, diagnostic product, or drug-design platform.

## Division sequence

1. Cellular & Mitochondrial Health — first research priority.
2. Muscle & Physical Health — second planned division, not active.
3. Brain & Cognitive Health — third planned division, not active.

## Known limitations

- The prototype was originally organized around CARDIA/ORIGIN; the interface and data model still require a full product-level review.
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

Requirements: Node.js 20.6 or newer.

```bash
cd elstella-origin
npm install
npm test
npm start
```

Open http://localhost:4173. Optional AI-assisted synthesis requires server-side provider configuration. The core literature and evidence workflow should not require AI credentials.

## Data safety

Do not enter patient-identifiable information. Export JSON backups because browser-local storage can be cleared. Imported JSON replaces the local workspace after confirmation. AI requests send selected evidence records to the configured external provider only after explicit confirmation. Do not commit .env.

## Remaining milestones

1. Run the automated test suite and verify GitHub Actions.
2. Perform a browser-level smoke test.
3. Complete the Division 01 literature and existing-care landscape.
4. Build a traceable public-dataset inventory.
5. Obtain qualified independent scientific critique.
6. Benchmark the Research Atlas against a conventional research workflow.
7. Decide whether Division 01 advances, is revised, or is stopped.
8. Activate Division 02 and then Division 03 only after their explicit gates.

Therapeutic discovery and biological validation are scientific programs, not software checkboxes.
