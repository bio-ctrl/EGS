# EGS — 24-Month Financial Model Framework
**Status:** Planning model; not an audited forecast or approved budget  
**Currency:** USD | **Planning horizon:** 24 months from financing close

## 1. Model rules
This model separates known targets from assumptions. No salary, vendor quote, revenue, customer, grant, or investment commitment has been invented. Populate the input cells only after obtaining real quotes and reviewing the hiring plan.

The $10,000,000 financing objective is aspirational. The model below shows a hypothetical full-close scenario solely to test capital allocation.

## 2. Hypothetical financing allocation

| Use | Share | 24-month envelope |
|---|---:|---:|
| Research and engineering personnel | 45% | $4,500,000 |
| Compute, EDA, and infrastructure | 15% | $1,500,000 |
| Prototype and physical validation | 15% | $1,500,000 |
| Legal, IP, security, governance | 8% | $800,000 |
| Customer discovery and pilots | 7% | $700,000 |
| Facilities and operations | 5% | $500,000 |
| Contingency | 5% | $500,000 |
| **Total** | **100%** | **$10,000,000** |

These are planning envelopes, not quotes. Unspent contingency remains cash; do not spend merely to exhaust an allocation.

## 3. Monthly operating model inputs

Fill these before treating the model as a forecast.

| Input | Value | Evidence required |
|---|---|---|
| Financing close date | [TBD] | Executed documents and cleared funds |
| Opening unrestricted cash | [TBD] | Bank statement / closing statement |
| Number of engineers by role | [TBD] | Approved hiring plan |
| Fully loaded monthly cost per role | [TBD] | Counsel-reviewed compensation and payroll assumptions |
| Compute/EDA monthly spend | [TBD] | Vendor quotes and usage estimate |
| Prototype/validation milestones | [TBD] | Written technical plan and vendor quotes |
| Legal/IP/security spend | [TBD] | Counsel and provider estimates |
| Facilities/insurance/admin | [TBD] | Quotes and lease terms |
| Contracted revenue | $0 until executed | Signed contract and accounting treatment |
| Grants | $0 until awarded | Award letter and restrictions |
| Additional financing | $0 until closed | Executed documents and cleared funds |

## 4. Monthly cash schedule

For each month M01–M24, calculate:

- Opening cash = prior month ending cash.
- Cash inflows = cleared financing + collected customer receipts + awarded grant receipts.
- Cash outflows = payroll + compute/EDA + prototype + legal/IP + customer pilots + facilities + other approved costs.
- Net burn = cash outflows − operating receipts (exclude financing).
- Ending cash = opening cash + cash inflows − cash outflows.
- Runway = ending cash / trailing three-month average net burn, when burn is positive and meaningful.

Do not count a verbal investor indication, unsigned LOI, unawarded grant, or pipeline opportunity as cash.

| Month | Opening cash | Financing received | Customer/grant cash received | Payroll | Compute/EDA | Prototype/validation | Legal/IP | Commercial/pilots | Facilities/admin | Ending cash |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M01 | [input] | [input] | [input] | [input] | [input] | [input] | [input] | [input] | [input] | = opening + inflows − outflows |
| M02 | =M01 ending | [input] | [input] | [input] | [input] | [input] | [input] | [input] | [input] | formula |
| M03–M06 | Roll forward monthly | | | | | | | | | |
| M07–M12 | Roll forward monthly | | | | | | | | | |
| M13–M18 | Roll forward monthly | | | | | | | | | |
| M19–M24 | Roll forward monthly | | | | | | | | | |

## 5. Scenarios

| Scenario | Financing assumption | Operating response |
|---|---|---|
| Downside | No institutional financing closed | Keep fixed costs minimal; prioritize open, reproducible research and low-cost validation; no lease or hiring commitments without cash |
| Staged | Smaller first tranche | Fund only the next technical proof milestone; set measurable release gates for later tranches |
| Target | Hypothetical $10M close | Use approved allocations; hire against milestones; protect validation and contingency budgets |

## 6. Stage gates before spend
1. **Before hiring:** confirm legal employer, payroll, IP assignment, role scope, and cash runway.
2. **Before EDA/vendor commitments:** compare quotes, license scope, export restrictions, and renewal costs.
3. **Before physical implementation:** establish a reproducible baseline, target process/library, and measurable acceptance criteria.
4. **Before facility commitment:** compare leased lab/office options against remote/shared facilities; no landmark campus assumption.
5. **Before commercial pilot:** agree scope, deliverables, data rights, confidentiality, acceptance tests, and IP ownership with counsel.

## 7. Metrics for monthly review
- Unrestricted cash and committed obligations.
- Net burn and runway.
- Headcount and hiring plan variance.
- Cost per verified experiment.
- Candidate generation throughput and verification pass rate.
- Baseline-relative generic synthesis results.
- Physical implementation milestones completed.
- Customer discovery interviews (completed, not merely scheduled).
- Paid evaluations and collected revenue (signed/collected only).

## 8. Model limitations
This is a structured model framework, not a completed numeric forecast. A defensible forecast requires actual quotes, approved compensation assumptions, tax/payroll treatment, insurance, legal costs, vendor license terms, and financing timing. Have an accountant and qualified counsel review it before use.
