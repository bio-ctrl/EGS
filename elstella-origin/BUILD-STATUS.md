# BUILD STATUS — ORIGIN ATLAS

## Implemented in this branch

- Interactive tab navigation.
- Seeded starter bibliography marked unreviewed.
- Evidence record creation and editing.
- Search across evidence records.
- Hypothesis register and hypothesis creation.
- Browser-local persistence using localStorage.
- CSV evidence export.
- JSON workspace backup and import.
- Reset of local workspace with confirmation.
- Protocol, data dictionary and benchmark documentation.
- CARDIA therapeutic landscape rapid map and scientific validation protocol.
- Evidence metadata completeness gate with unit tests.
- Europe PMC literature search and bibliographic metadata import.
- Abstract sentence candidate extraction with explicit unverified labels.
- Server-side AI synthesis endpoint with evidence-ID citation constraints and provider credentials kept off the client.
- Optional Supabase authentication and per-account workspace sync adapter.
- Supabase schema with row-level security.
- Node built-in test suite and repository-level GitHub Actions workflow.

## Known limitations

- Europe PMC search requires network access and has not been tested against the live service in a browser.
- PubMed remains an external search shortcut.
- AI synthesis requires a configured compatible provider endpoint and a running Node server. AI output can be incorrect and must be source-checked.
- Supabase sync requires a separately provisioned project, schema execution and user configuration. It supports same-account cross-device sync, not shared team collaboration.
- No production database has been provisioned by this repository.
- No browser-level end-to-end test or external security audit has been completed.
- Abstract extraction produces candidate snippets only; no claim is automatically marked verified.
- No validated evidence-quality scoring exists.
- The five starter citations remain unreviewed leads; verify metadata and source content before relying on them.
- No formal scientific or clinical validation has been completed.
- CARDIA literature map is rapid and non-exhaustive; it is not a systematic review or a target nomination.
- Evidence completeness tests only check required metadata; they do not verify source truth or scientific quality.
- No therapeutic discovery or drug candidate has been completed.
- A 2026 preclinical cardiac-fibrosis compound report is documented as competing literature, not as an Elstella discovery.

## Run and test

Use Node.js 20.6 or newer. Copy `.env.example` to `.env`, configure an AI provider if desired, run `npm start`, then open `http://localhost:4173`. Run `npm test` for unit tests. Directly opening `index.html` supports the local UI but not the server-side AI endpoint.

## Data safety

Do not enter patient-identifiable information. Export JSON backups because browser-local storage can be cleared. Imported JSON replaces the local workspace after confirmation. AI requests send selected evidence records to the configured external provider only after an explicit confirmation. Do not commit `.env`.

## Remaining milestones

1. Obtain a successful GitHub Actions test run and perform a browser-level smoke test.
2. Configure and test an AI provider endpoint without exposing credentials.
3. Provision Supabase and test signup, row-level security, upsert and cross-device restore.
4. Add search-log and formal screening-decision modules.
5. Verify source metadata and manually review every abstract candidate.
6. Conduct an independent benchmark with qualified reviewers.
7. Execute the review protocol, independently verify extracted claims and complete the platform benchmark.
8. Obtain qualified expert review before proposing any supervised experimental research. Therapeutic discovery and biological validation are research activities, not software checkboxes.
