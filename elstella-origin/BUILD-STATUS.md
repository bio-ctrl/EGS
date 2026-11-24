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

## Known limitations

- No live PubMed or Europe PMC API integration; database shortcuts open external search pages.
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
