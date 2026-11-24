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
- Protocol, data dictionary and benchmark documentation.\n- Europe PMC search and bibliographic metadata import.\n- Abstract sentence candidate extraction with explicit unverified labels.\n- Server-side AI synthesis endpoint with evidence-ID citation constraints and provider credentials kept off the client.\n- Optional Supabase auth and per-account workspace sync adapter.\n- Supabase schema with row-level security.\n- Node built-in test suite and GitHub Actions test workflow.

## Known limitations

- Europe PMC search is implemented; PubMed is still an external shortcut. Europe PMC availability and CORS/network access depend on the user's environment.
- No server database or multi-user synchronization.
- Local browser data does not automatically sync to GitHub.
- No authentication or access-control layer.
- No AI extraction or automated scientific reasoning.
- No validated evidence-quality scoring.
- No formal clinical or scientific validation.
- The five starter citations remain unreviewed leads; verify metadata and source content before relying on them.

## Run

Open `index.html` in a modern browser. The application is static and has no build step or external package dependencies.

## Data safety

Do not enter patient-identifiable information. Export JSON backups because browser-local storage can be cleared. Imported JSON replaces the local workspace after confirmation.

## Next engineering milestones

1. Automated tests for CSV/JSON round trips and record editing.
2. Source metadata verification workflow.
3. Search-log and screening-decision modules.
4. Optional backend only after data model and user requirements are validated.
5. Independent benchmark with qualified reviewers.
