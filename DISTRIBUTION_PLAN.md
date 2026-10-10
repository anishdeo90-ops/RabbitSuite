# Hire Rabbits: job-posting-led distribution plan

**Working market:** India. **Research date:** 10 October 2026. **Status:** discovery plan and small live pilot, not a validated sales playbook.

## Thesis and guardrail

Hiring for operational roles reveals *work a company needs done*. A job description can show the systems, handoffs, reports, and exception handling that matter to that company. It does **not** prove that its systems are bad, that the role should be replaced, or that the company wants to buy software. Growth, seasonality, attrition, and compliance can all create the same opening. Use the posting to form a specific question, then validate it in discovery.

The offer is to help a team run a workflow with less duplicate entry and better visibility while people retain approval and judgment. Do not lead with “AI can replace your executives.” Hire Rabbits currently combines ERPNext, HRMS, India Payroll, CRM, Helpdesk, and Telephony in one Frappe site; the local architecture and demo data are useful for discovery, but any customer-facing claim about integrations, automation, security, or production readiness must be demonstrated in that workflow first. See [ARCHITECTURE.md](ARCHITECTURE.md).

## 1. Who to pursue first

Start with India-based companies of roughly **25–500 people** hiring for repeatable, cross-team operations. Prefer a direct employer posting from the last 30 days with a detailed JD, a real company site, and a named workflow owner. The highest-fit initial verticals are light manufacturing/EV components, consumer brands, multi-location retail or clinics, and services firms with substantial HR or support operations. This is a testable ICP, not a claim that every such firm is a buyer.

| Segment | Job-description signals | Likely buyer | First workflow to demonstrate |
| --- | --- | --- | --- |
| Inventory, stores, procurement | GRN, stock reconciliation, transfers, shortages, slow stock, BOM, Excel/MIS, purchase-to-receipt handoff | COO, head of operations, supply-chain or plant lead | Receipt → stock update → discrepancy review → replenishment report |
| HR and payroll operations | Attendance exceptions, leave, onboarding documents, payroll inputs, full-and-final settlement | HR head, people-ops lead, founder | Attendance/leave → reviewed payroll inputs → employee record |
| Customer support and service | Chat/email/voice, SLA, escalation, repeated questions, CRM context, order or delivery status | CX/support head, operations lead | Ticket → customer/order context → assignment → SLA report |
| Finance and MIS | Invoice/ledger reconciliation, AR/AP, monthly reports, audit evidence, cross-team data collection | CFO, finance controller, founder | Invoice/payment → ledger → reconciled management report |
| Sales operations | Lead follow-up, quote/order handoff, pipeline hygiene, missed callbacks | Sales head, revenue operations | Lead → task/call → quotation → order and invoice |

Avoid making the job-title count the main score. Ten openings at a 10,000-person enterprise may be less useful than one detailed opening at a 100-person company. Deprioritize recruitment agencies posting for unnamed clients, stale/reposted jobs, pure BPO labor supply, very large enterprises with an incumbent ERP and long procurement cycles, and roles outside the Suite's actual capabilities. An existing SAP/ERP mention is a discovery clue for integration, not evidence of no system.

## 2. Search-role map by app

Search both `Executive` and adjacent titles: `Coordinator`, `Associate`, `Officer`, `Analyst`, `Specialist`, `Manager`, and India-specific `MIS` or `Storekeeper`. The JD matters more than the title. Use phrases below as separate queries; broad Boolean strings can create noisy results.

| Suite area | Job titles to search | Evidence to extract from the JD | Product claim to validate |
| --- | --- | --- | --- |
| ERP Stock / Warehousing | Inventory Executive, Stores Executive, Warehouse Executive, Stock Controller, Inventory Analyst, Dispatch Executive | Physical/system variance, inward/outward, transfers, bin locations, ageing, FIFO/FEFO, batch/expiry | Stock ledger, transfers, counts, exception reporting |
| ERP Buying / Suppliers | Purchase Executive, Procurement Executive, Sourcing Executive, Vendor Coordinator, Supply Chain Executive | RFQ, approvals, PO, supplier follow-up, GRN, invoice matching | Request → RFQ/PO → receipt → payable handoff |
| ERP Manufacturing / Quality | Production Planning Executive, PPC Executive, BOM Coordinator, Quality Executive, QC Inspector | BOM consumption, material availability, work orders, inspection, rejections, traceability | BOM/work-order/quality workflow in a real demo |
| ERP Accounts / Invoicing | Accounts Executive, Billing Executive, AR Executive, AP Executive, Finance Operations Executive | Invoices, credit notes, collections, bank reconciliation, close, audit trail | Accurate ledgers and reconciled financial reports |
| ERP Reporting / Projects / Assets | MIS Executive, Operations Analyst, Project Coordinator, Asset Executive | Manual consolidation, revenue/inventory tie-out, project cost, asset register | Role-specific dashboard backed by source transactions |
| HRMS / India Payroll | HR Executive, HR Operations Executive, Payroll Executive, Attendance Executive, Recruitment Coordinator | Onboarding, leave/attendance, salary inputs, compliance, employee letters, exits | Employee lifecycle and reviewed payroll handoff |
| CRM / Selling | Sales Coordinator, Inside Sales Executive, Sales Operations Executive, Lead Generation Executive | Lead assignment, follow-ups, quotes, pipeline, customer records | Lead-to-quote and task ownership |
| Helpdesk / Telephony | Customer Support Executive, Customer Service Executive, Support Specialist, Contact Centre Lead | Omnichannel contact, SLAs, escalations, knowledge base, call logging | Ticket/CRM context and SLA workflow; voice only if configured |

Start with **inventory/stores, HR operations, and support** because the pilot produced detailed examples for each. Add finance/MIS next. Treat regulated or deeply integrated work as a later track unless a specific, working demo is ready.

## 3. Source choice and pilot run

Use [Bebity's LinkedIn Jobs Scraper](https://apify.com/bebity/linkedin-jobs-scraper) for discovery: it returned full descriptions, company URLs, dates, and job URLs in the pilot. It has explicit `titles`, `locations`, `publishedAt`, and `rows` inputs. Use [Apify-maintained Indeed Scraper](https://apify.com/misceres/indeed-scraper) as a second source for confirmation and roles LinkedIn misses. Its pilot returned useful descriptions but also older/unrelated results, so filter locally before adding accounts. Apify's [Run Actor API](https://docs.apify.com/api/v2/actors-runs-post) supports a per-run charge cap; send the token in the `Authorization: Bearer` header, as [Apify recommends](https://docs.apify.com/api/v2). Never put the API token in this file, a URL, or a committed dataset.

**Actual pilot, 10 October 2026:**

| Source and run | Input | Result | Reported run usage |
| --- | --- | --- | ---: |
| [LinkedIn run `xebkx2DcnNf9azmJS`](https://console.apify.com/actors/runs/xebkx2DcnNf9azmJS) | Inventory Executive, HR Executive, Customer Support Executive × India; last month; 15 rows/search; enrichment off; $1 cap | 45 rows, 39 company names, 45 descriptions | US$0.0676 |
| [Indeed run `BxtxRLyfvlhKDbbsx`](https://console.apify.com/actors/runs/BxtxRLyfvlhKDbbsx) | Inventory Executive × Mumbai; 10 results; $1 cap | 10 rows, 10 company names; only 5 posted within the last 30 days | US$0.06 |

These are one-off observed charges, not a forecast or guaranteed price. Actor pricing and platform use can change. The Apify datasets were downloaded locally for analysis; this document keeps only a curated public-job shortlist. Links can close or change, so recheck before outreach.

### Reproducible bounded searches

Set `APIFY_TOKEN` in your own environment. Example request bodies; keep `maxTotalChargeUsd` and item limits on every run:

```json
{"titles":["Inventory Executive","HR Executive","Customer Support Executive"],"locations":["India"],"publishedAt":"r2592000","rows":15,"enrichCompany":false,"enrichCompanyWebsite":false,"companyProfile":true}
```

`POST https://api.apify.com/v2/acts/bebity~linkedin-jobs-scraper/runs?maxTotalChargeUsd=1&maxItems=45&waitForFinish=60`

```json
{"position":"Inventory Executive","country":"IN","location":"Mumbai","maxItemsPerSearch":10,"parseCompanyDetails":true,"saveOnlyUniqueItems":true}
```

`POST https://api.apify.com/v2/acts/misceres~indeed-scraper/runs?maxTotalChargeUsd=1&maxItems=10&waitForFinish=60`

For a weekly production search, split roles into focused runs by city/vertical, keep a spend cap, and record actor run ID, search, run date, source URL, job ID, publication date, and capture date. Deduplicate by source job ID and then by company domain + normalized title + location. A repost is one demand signal, not a new hire. Check the employer's own careers page when possible. Keep a 30-day active-posting window; expired jobs move to research history, not active outreach.

## 4. Curated companies from the pilot

The table is a *research queue*. “Angle” is an inference from the JD to test with a human, not a statement about the company's current software. Priorities reflect our likely ability to show a relevant workflow, company size, and JD specificity. Dates are the posting dates returned by the actors.

| Priority | Company and public posting | Posting date | Evidence from JD | Suite angle / next verification |
| --- | --- | --- | --- | --- |
| A | [Wellbeing Nutrition — Executive, Inventory](https://in.linkedin.com/jobs/view/executive-inventory-at-wellbeing-nutrition-4477154144) | 8 Oct | Inward/outward movement, cycle counts, slow/non-moving stock, management reports, audit documents | Stock reconciliation and ageing report; ask which warehouse/production systems hold the source data |
| A | [Vecmocon Technologies — Inventory Executive](https://in.linkedin.com/jobs/view/inventory-executive-at-vecmocon-technologies-4475709901) | 8 Oct | GRN, issues/returns/transfers, FIFO/FEFO, BOM-linked material availability, system/physical reconciliation | Demonstrate one manufacturing material flow and variance approval; verify BOM and quality workflow live |
| A | [Koffeetech Communications — HR Executive](https://in.linkedin.com/jobs/view/human-resources-executive-at-koffeetech-communications-4474046569) | 6 Oct | Recruitment, onboarding, employee records, attendance discrepancies, payroll inputs, exits | HRMS-to-payroll input workflow; JD already mentions HRMS, so ask where handoffs still cost time |
| A | [Dr. Neha's Medical Asthetic — Inventory Executive](https://in.indeed.com/viewjob?jk=8ee728ae02226226) | 8 Oct | Multi-clinic stock, expiry, transfers, physical checks, invoices, reports | Multi-location and expiry workflow; confirm batch/expiry data and clinic processes before proposing |
| B | [Reise Moto — Ecommerce Operations Executive](https://in.indeed.com/viewjob?jk=933211a12f41058f) | 5 Oct | Marketplace catalog, inventory versus physical stock, dispatch, returns, order exceptions | Strong pain signal; only pitch after verifying Amazon/Flipkart/Ajio connector scope or a manual import pilot |
| B | [Printo — Customer Support](https://in.linkedin.com/jobs/view/customer-support-team-at-printo-4468706674) | 21 Sep | Calls, customer queries, vendor/production coordination, order follow-up | Helpdesk + customer/order context; larger account, likely higher integration effort |
| B | [Ginger Affordable Solutions — HR Executive](https://www.linkedin.com/jobs/view/4466550763) | 15 Sep | Onboarding, attendance/leave records, payroll coordination, trackers | Simple HR operations pilot; verify actual employee volume and budget |
| B | [Anaxee Digital Runners — HR Executive](https://www.linkedin.com/jobs/view/4474633086) | 5 Oct | Recruiting, onboarding, training, performance and compensation across distributed operations | Potential distributed-workforce fit; title says “Aug 2026,” so verify vacancy is still active |
| B | [The Souled Store — MIS Executive](https://in.indeed.com/viewjob?jk=19b9b4ce454983e8) | 17 Sep | Revenue/expense/inventory reconciliation across MIS and accounting, audit documents | Finance/stock tie-out; larger retailer, qualify integrations and decision process first |
| C | [Parle Tableting Technologies — Stores Executive](https://in.linkedin.com/jobs/view/stores-executive-at-parle-tableting-technologies-pvt-ltd-4476553686) | 7 Oct | GRN, BOM, stock audits, ERP/SAP update, FIFO | Existing ERP/SAP and larger size point to integration rather than replacement; high-friction sale |
| C | [Sturlite India — Dead Inventory Executive](https://www.linkedin.com/jobs/view/4471060067) | 26 Sep | Dead stock, FSN/ABC analysis, inventory ageing, SAP S/4HANA | Strong reporting need, but incumbent SAP makes a narrow analytics/integration test necessary |

**Quality controls learned from this run:** a LinkedIn job attributed to Astranova described support for a different brand, so company identity needs manual verification. The Indeed search returned broad titles and jobs older than 30 days. Staffing agencies and very large employers appeared in the results but are not first-wave targets. Do not infer company size from employee count alone; actor profile fields may be stale.

## 5. Qualification and account scoring

Create one CRM Organization per verified employer domain, one Lead/Deal per live workflow opportunity, and attach the job URL plus a short evidence note. This is a proposed operating process, not an implemented integration. Score each company 0–100 during manual review:

| Factor | Points | How to award |
| --- | ---: | --- |
| Workflow fit | 0–30 | JD tasks map to a workflow we can show end-to-end today |
| Specific, repeated friction | 0–25 | Clear handoffs, reconciliation, exceptions, or reporting burden; more than generic “team player” text |
| Timing and intent | 0–15 | Direct employer post within 30 days, confirmed active |
| Buyer accessibility | 0–15 | Clear operational owner and plausible company size/sales cycle |
| Product readiness | 0–15 | No unbuilt connector or critical compliance claim needed for first pilot |

Subtract 20 for an agency/unknown employer, 15 for a named incumbent system requiring unbuilt integration, and 10 for a stale/repost-only signal. Scores of 75+ enter a tailored outreach queue; 55–74 need one more validation step; below 55 stay in research. The score ranks research effort, not conversion probability. Record the exact reason for every deduction.

Before contacting anyone, verify the job remains open, identify the business owner from public company sources, identify one process question the JD raises, and check whether a credible Suite demo exists. Avoid guessing private email addresses or using a scraped recruiter's personal details as a sales hook.

## 6. The outreach motion

Use one short, specific email to the likely workflow owner. Refer to one observed responsibility and offer a diagnostic or narrow demo. Never say the company has poor systems, claim access to internal data, or promise to replace the new hire. Send only after reviewing the posting and the recipient; keep outreach compliant with applicable platform rules and email requirements. Stop when someone opts out.

**Inventory example — Wellbeing Nutrition**

> Subject: A stock reconciliation workflow for your inventory team
>
> I saw the inventory role covering cycle counts, inward/outward movement, and slow-moving stock reporting. Those tasks often span warehouse records and management reports. We are testing a single workflow that flags count differences and produces an ageing view from the same transactions. Would a 15-minute walkthrough of how your team handles those handoffs be useful? I can show the current workflow and its limits.

**HR example — Koffeetech**

> Subject: Attendance exceptions to payroll inputs
>
> Your HR opening combines employee records, attendance discrepancies, and monthly payroll inputs. Hire Rabbits brings HRMS and payroll into one site. I would like to understand where the handoff still requires manual checking, then show a small reviewed exception flow if relevant. Is this owned by you or someone else in people operations?

**Support example — Printo**

> Subject: Customer query to production update
>
> The support opening mentions customer calls and coordination with production and vendors for order updates. We are working on keeping the customer conversation, owner, and order context together so follow-ups do not get lost. Is connecting those steps a current priority? If so, I can show a narrow example rather than a generic CRM demo.

For the first 20 accounts, founder-led/manual sending is preferable. Suggested sequence: day 0 tailored email; day 4 one follow-up with a concrete workflow sketch; day 10 final polite close. One recipient per account initially. Measure positive replies and discovery meetings, not open rates alone. Do not auto-send AI-generated copy without human review.

## 7. Turn JDs into product decisions

Keep a “JD evidence → workflow hypothesis → demo proof → gap” ledger. One job posting may reveal a useful feature idea but is insufficient to justify a build. Promote a gap to the roadmap only after it recurs across at least three qualified accounts or blocks a paid pilot. First see whether native ERPNext/HRMS/Helpdesk already solves it in the installed version; then test the workflow with real sample transactions.

| Evidence from pilot | First proof to assemble | Possible gap; do not promise yet |
| --- | --- | --- |
| Wellbeing/Vecmocon: variance, ageing, GRN, transfers | Stock receipt, count adjustment approval, ageing/variance report | Unified exception inbox and scheduled alerts |
| Vecmocon/Parle: BOM and production material availability | BOM → material request → issue → work order | Clear production-shortage view and quality handoff |
| Koffeetech/Ginger: attendance, leave, payroll inputs | Attendance exception → reviewed payroll input → salary slip | Human-approved draft letters and exception summaries |
| Printo: calls, queries, order/vendor coordination | Ticket → customer/order context → owner and SLA | Channel connector and supplier/production update handoff |
| Reise Moto: marketplace catalog/orders/stock | Demonstrate import and reconciled stock on one marketplace sample | Native marketplace connectors and SKU mapping are a major project |
| Souled Store: MIS versus accounts reconciliation | Invoice/stock/ledger source to one management report | Cross-module reconciliation checks and audit evidence pack |
| Dr. Neha's: clinic locations and expiry | Multi-warehouse transfer, batch/expiry record, physical count | Clinic-oriented mobile count/approval UX |

The current local app has had sparse/empty dashboards and navigation issues during development. Before outreach, verify every showcased report with a known company/date filter and real transactions. A screenshot of a populated demo is evidence of a demo, not proof that a customer's data and integrations will work without discovery.

## 8. Four-week execution plan and decision gates

| Week | Work | Deliverable / gate |
| --- | --- | --- |
| 1 | Run capped India searches for six high-fit roles; normalize/deduplicate; review 100 jobs; verify 20 employers and 10 live postings | 20-account research queue with evidence, buyer hypothesis, and score |
| 2 | Build three narrow demos (inventory, HR/payroll, support); audit capabilities/gaps; write one email per top account | 3 reproducible demos; no unsupported feature claims |
| 3 | Send 20 manually reviewed emails; follow up once; hold discovery calls; record objections and current systems | Baseline: delivered, replies, positive replies, meetings, qualified workflow pains |
| 4 | Offer 2–3 scoped pilot proposals with one workflow, named owner, data boundary, baseline, and success metric | Continue only if at least one prospect accepts a concrete pilot scope or strong discovery evidence emerges |

Pilot success should be measured in customer terms: fewer manual handoffs or duplicate entries, faster exception resolution, stock variance found earlier, payroll input errors caught before approval, or SLA adherence. Establish a baseline and measure the same process after the pilot. Do not assume savings from a salary figure in a JD; operational value also includes accuracy, auditability, and staff time.

Review results after 20 accounts: which role/search produced verified direct employers, which JD evidence led to a reply, which integration blocked progress, and what demo was convincing. Expand from India only after this first cohort shows a repeatable signal. Keep the actor runs capped and the raw data access limited to the team handling research.

## Sources and limits

- Product map: local [ARCHITECTURE.md](ARCHITECTURE.md) and the installed apps in this repository. It describes the local build, not a production certification.
- Scraper selection and input/pricing: [Bebity LinkedIn Actor](https://apify.com/bebity/linkedin-jobs-scraper), [Apify-maintained Indeed Actor](https://apify.com/misceres/indeed-scraper), [Apify API documentation](https://docs.apify.com/api/v2), [Run Actor API](https://docs.apify.com/api/v2/actors-runs-post).
- Job evidence: each public posting is linked in the curated-company table. Descriptions and dates were captured by the two Apify runs on 10 October 2026; employer sites and current vacancy status should be checked before contact.
- The sample is deliberately small, India-only, and title-biased. Actor results can be duplicate, mislabeled, stale, or from agencies; rankings and product hypotheses above are our inferences, not facts stated by employers.
