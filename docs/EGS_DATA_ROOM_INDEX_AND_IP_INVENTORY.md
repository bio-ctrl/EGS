# EGS — Diligence Data Room Index and IP Inventory
**Status:** Internal checklist | **Owner:** To be assigned | **Last updated:** 25 November 2026

This index describes what should exist in a controlled diligence room. It does not assert that missing records exist. Keep confidential source code, credentials, personal data, and invention-enabling details out of any external room until disclosure is approved.

## A. Company and governance
| Item | Status | Required evidence |
|---|---|---|
| Legal entity formation documents | Not confirmed | Filed formation documents |
| Ownership/cap table | Not prepared | Counsel-reviewed capitalization table |
| Founder/guardian authority and approvals | Required | Appropriate written approvals |
| Board/advisor consents | Not confirmed | Signed consents, if applicable |
| Tax and accounting setup | Not confirmed | Professional records |
| Insurance | Not confirmed | Policy documents |
| Material contracts | None confirmed here | Executed copies or explicit none |

## B. Intellectual property
| Item | Status | Action |
|---|---|---|
| Repository provenance | Partial | Preserve commit history and document origins |
| Founder-created code inventory | To complete | Map files/modules to authors and dates |
| Third-party dependencies | To audit | Generate SBOM and review licenses |
| External contributions | To audit | Identify contributors and contribution terms |
| Prior employer/school obligations | To review | Counsel review; do not assume ownership |
| Invention disclosures | Not prepared | Document concepts, dates, contributors, evidence |
| Patent/trade-secret strategy | Not decided | Qualified IP counsel review |
| Trademark/domain ownership | Not confirmed | Verify registrant and rights |
| Confidentiality agreements | Not confirmed | Counsel-approved forms before sharing secrets |

### IP inventory template
For each material module or invention, record:
- Identifier and title.
- Repository path and commit range.
- Contributors and their relationship to EGS.
- Creation date and evidence.
- Third-party libraries, datasets, or tools used.
- License/contract obligations.
- Whether public disclosure has occurred.
- Confidentiality classification.
- Counsel review and ownership conclusion.

## C. Technical evidence
| Item | Status | Location / next action |
|---|---|---|
| Joint multi-output search | Exists | `orcus/joint_search.py`, tests and benchmark |
| Adder architectures | Exists | `orcus/adder_architectures.py` |
| Bit-vector IR | Exists | `orcus/bitvector.py` |
| Adder search | Exists | `orcus/adder_search.py` |
| Associative architecture search | Exists | `orcus/architecture_search.py` |
| Compressor networks | Exists | `orcus/compressor.py` |
| Compressor benchmark report | Exists | `docs/COMPRESSOR_NETWORK_EXPERIMENT.md` |
| CI logs and artifacts | Partial | Attach exact run IDs, commit SHAs, and reports |
| Independent reproduction | Not completed | Arrange independent run |
| Physical PPA | Not completed | Requires target library, constraints, placement/routing and reports |
| FPGA demonstration | Not completed | Define board, workload, acceptance tests |
| Silicon fabrication | Not completed | Not performed |

## D. Commercial evidence
- Customer interview notes (with permission and privacy controls).
- Problem statements and measurable acceptance criteria.
- Paid pilot proposals and executed contracts, if any.
- Revenue ledger and invoices, if any.
- Design-partner permissions and reference approvals.
- Competitive analysis with dated sources.
- No pipeline entry should be represented as a customer or partner.

## E. Fundraising evidence
- Approved investor deck.
- Current financial model and assumptions.
- Funding pipeline with source, fit, eligibility, date checked, and next action.
- All investor communications and meeting notes.
- Executed term sheets and financing documents, if any.
- Bank evidence for cleared funds.
- Do not record verbal interest as committed capital.

## F. Data-room access controls
1. Create separate public, investor-screened, and counsel-only folders.
2. Use least-privilege, named access and expiration dates.
3. Keep credentials, signing keys, private personal information, and unrestricted source code out of the general investor room.
4. Watermark sensitive PDFs where appropriate.
5. Maintain an access log and remove access when diligence ends.
6. Share only after appropriate adult and legal review.

## G. Readiness gate
No external diligence room is ready until entity/ownership status, IP provenance, dependency licenses, technical evidence, and disclosure permissions have been reviewed. Missing items must be labeled missing—not silently omitted or implied complete.
