# Conga CPQ & CLM Domain Reference — PS AI QA Assistant

> Version: 1.0
> Last Updated: 2026-07-25
> Status: Approved
> Classification: Internal — Professional Services QA
> Review Cycle: Quarterly
> Companion Documents: TEST_CASE_GENERATION.md, QA_METHODOLOGY.md, SYSTEM_INSTRUCTIONS.md

---

## 1. Purpose

This document is the **domain reference** for Conga CPQ and Conga CLM (formerly Apttus). It
exists so that generated manual test cases use the **correct, standard product terminology,
object names, lifecycle states, and action labels** instead of generic phrasings — which makes
them execution-ready and cuts the number of `(wording TBC)` markers a Solution Architect has to
resolve during review.

### 1.1 How to use it (and its limits)

- **Use it to name things correctly.** When the source describes a behaviour that maps to a
  standard Conga concept (e.g. "activate the agreement"), author the step using the product's
  real object, action, and state names from this reference (e.g. "Click **Activate**; the
  agreement Status Category moves to **In Effect**").
- **It is a reference, not a licence to invent.** This does not override the "Never Invent
  Anything" rule in `SYSTEM_INSTRUCTIONS.md`. Standard product terminology is not invention;
  a specific *record value*, a project-specific *field label*, a *threshold*, or a *custom
  configuration* still must come from the source. When a label or behaviour is genuinely
  project-specific and unverified, keep the `(wording TBC)` / `(config TBC)` marker and log it.
- **Editions differ.** Conga ships in several forms (Apttus "classic" on Salesforce, Conga CLM
  on Salesforce, Conga CLM standalone/Novatus, and the newer Conga platform). Exact API names,
  labels, and default statuses vary by edition and by each customer's configuration. Treat this
  as the *canonical vocabulary to reach for*, and defer to the project's actual configuration
  (Confluence/design docs/Jira) when the two disagree — record the difference as an assumption.

---

## 2. Product Landscape

| Product | Role in the quote-to-contract lifecycle | Typical test surface |
|---------|-----------------------------------------|----------------------|
| **Conga CPQ** | Configure-Price-Quote: builds the Quote/Proposal, pricing, discounting, and line items | Quote creation, pricing/discount rules, proposal generation, acceptance |
| **Conga CLM** | Contract Lifecycle Management: the **Agreement** record and its lifecycle | Agreement creation, activation, amendment, renewal, termination, expiry |
| **Conga Composer / X-Author for Contracts** | Document generation (Word/PDF) from templates | Generate proposal/agreement document, template selection, output format, watermark |
| **Conga Sign** | Electronic signature | Send for eSignature, signer sequence, reminders, recall, signature status |
| **Conga Billing / Invoicing** | Invoicing and revenue (where in scope) | Consolidated invoicing, pro-rata credits, billing schedules |
| **External ERP (e.g. Microsoft D365)** | Downstream financial/asset system | Integration on activation ("send to D365"), asset coverage sync |

The standard flow this reference supports:

```
Account / Opportunity -> Quote/Proposal (CPQ) -> [accepted] -> Agreement (CLM)
   -> Activate (In Effect) -> [Amend | Renew | Terminate | Expire]
Generate document (Composer/X-Author) -> Send for eSignature (Conga Sign)
Finalized order -> Assets -> Renewal opportunity/quote -> Renewal Agreement
```

---

## 3. Core Objects and Relationships

Standard objects (Salesforce editions shown; names vary by edition — verify against the org):

| Business concept | Common object (Apttus/Conga on Salesforce) | Notes |
|------------------|--------------------------------------------|-------|
| Quote / Proposal | `Apttus_Proposal__Proposal__c` | The CPQ quote header |
| Proposal Line Item | `Apttus_Proposal__Proposal_Line_Item__c` | Products/services on the quote |
| Agreement | `Apttus__APTS_Agreement__c` | The CLM contract record |
| Agreement Line Item | `Apttus__AgreementLineItem__c` | Coverage/products on the agreement |
| Asset Line Item | `Apttus_Config2__AssetLineItem__c` | Installed-base asset created from a finalized order |
| Order | `Apttus_Config2__Order__c` | Order generated from an accepted quote |
| Account / Opportunity / Contact | Salesforce standard objects | Referenced/defaulted onto the agreement |

Key relationships to reason about when designing coverage:

- An **accepted Proposal** can create an **Agreement** (auto or via a "Create Agreement" action),
  copying Account, Opportunity, and Proposal reference fields, and defaulting the Agreement Name.
- **Eligible proposal line items** (e.g. warranty/renewal service products) become **Agreement
  Line Items**; non-eligible items (e.g. finished goods) are excluded.
- **Asset Line Items** created from a finished-goods (FG) bundle order should link to the
  respective Agreement for coverage traceability.
- **Record Type** is often driven by proposal type (e.g. New Sale vs Service Renewal).

---

## 4. Agreement Lifecycle: Status vs Status Category

Conga agreements track **two** related fields — author both when the source mentions status:

- **Status Category** (`Apttus__Status_Category__c`) — the coarse lifecycle bucket shown on the
  chevron.
- **Status** (`Apttus__Status__c`) — the finer state within a category.

Standard (out-of-the-box) **Status Categories** and representative statuses (customers often trim
or rename these; the chevron is configurable):

| Status Category | Representative Status values | Meaning |
|-----------------|------------------------------|---------|
| **Request** | Draft, In Review | Newly created / being prepared |
| **In Authoring** | Author Contract, In Authoring | Document being authored (often trimmed out for simple flows) |
| **In Signatures** | Ready for Signatures, Other Party Signatures, Fully Signed | Out for signature (often trimmed out where Conga Sign is not used inline) |
| **In Effect** | Activated, In Effect | Live/active contract — the "Activated" state referenced in CLM stories typically maps here |
| **Amendment** | Amend Request, In Amendment | An amendment version is in progress |
| **Renewal** | Renewal in Progress | A renewal is in progress |
| **Expired** | Expired | End date reached |
| **Terminated** | Terminated | Ended early |
| **Cancelled** | Cancelled | Voided before activation |

Authoring guidance:
- When a story says "activate the agreement", the observable outcome is normally **Status
  Category = In Effect** (Status such as *Activated* / *In Effect*). If a project distinguishes
  a discrete "Activated" status from "In Effect", keep that nuance as `(config TBC)` and log it.
- The chevron stages named in many CLM stories (Request, In Effect, Amended, Terminated,
  Expired) are Status Categories; "removing In Authoring / In Approvals / In Signatures" means
  trimming those categories from the configured chevron.

---

## 5. Standard Lifecycle Actions (button/action vocabulary)

Use these standard action names in steps rather than generic verbs:

| Action | Where | Standard effect |
|--------|-------|-----------------|
| **Create Agreement** | From an accepted Proposal/Quote | Creates the Agreement, copies references, defaults fields/record type |
| **Activate** | Agreement header | Moves Status Category to **In Effect**; may trigger downstream integration (e.g. send to D365) |
| **Amend** | Agreement (in Effect) | Creates a new **version**; original retained read-only |
| **Renew** | Agreement (expiring/expired) or via renewal batch | Creates renewal opportunity/quote and, on acceptance, a linked renewal agreement |
| **Terminate** | Active agreement | Ends before expiry; Status Category **Terminated**; captures date/reason |
| **Expire** | Agreement at/after end date (auto or manual) | Status Category **Expired** |
| **Cancel** | Pre-activation agreement | Status Category **Cancelled** |
| **Generate** | Agreement/Proposal | Runs Composer/X-Author to produce the document |
| **Regenerate** | After a prior generation | Produces a fresh document version |
| **Send for eSignature** | Generated document | Sends via Conga Sign to recipients |
| **Recall** | In-flight Conga Sign transaction | Withdraws the signature request |

---

## 6. Versioning and Amendment

- Amendment creates a **new agreement version** rather than overwriting the original.
- **Exactly one version is active** at a time; prior versions are **read-only** and retained for
  history with timestamps and users.
- Amendable content typically includes coverage type, coverage duration, pricing, and terms;
  totals recalculate after changes.
- Amendment is usually gated to specific lifecycle states (e.g. In Effect).

---

## 7. Renewals

- Renewal can be **manual** (from an expiring/expired agreement) or **automated** via the Conga
  **renewal batch job**, commonly configured to run a set number of days before expiry (e.g. 90
  days — the exact window is a per-project config; treat a specific number as `(config TBC)`
  unless the source states it).
- Standard pattern: **Renewal Opportunity -> Renewal Quote -> [accepted] -> Renewal Agreement**,
  with the renewal agreement **linked to the original** and correct start/end dates for the new
  term. Eligible service line items carry forward; non-eligible items do not.
- Multi-system / master-agreement renewal scenarios (e.g. a short interim renewal plus a renewal
  aligned to a future master agreement) are a known complex case — design explicit coverage.

---

## 8. Document Generation and e-Signature

- **Generation**: via Conga Composer or X-Author for Contracts against a **template**; output
  formats commonly **DOCX** and **PDF**; a **DRAFT watermark** may be applied for
  not-yet-approved documents (via template configuration or an "Include Watermark" option).
- **Conga Sign**: send the generated document to recipients with a **signing sequence**;
  parameters include **reminders** and **expiration**; supports **recall** and **reinitiate**.
- **Conga Sign transaction statuses** (representative): Sent/Out for Signature, Signed,
  Completed, Declined, Cancelled, Recalled. The signed document is stored back on the record
  (e.g. Notes & Attachments / Files) once completed.

---

## 9. Integration and Billing Touchpoints

- **ERP / D365**: activation may "send to D365" (or the configured ERP). Where the source
  mentions integration as a precondition to activation, include it as a precondition and cover
  the failure/missing-integration path.
- **Billing / Invoicing**: consolidated invoicing across contracts/systems, **pro-rata credits**
  for pre-paid portions on termination/amendment, and holding credits per customer-specific
  agreements are known Canon-style requirements — where in scope, design explicit coverage and
  mark unspecified rules `(value TBC)`.
- **Assets / coverage**: a physical asset should reflect coverage per the active agreement, and
  should stop showing as covered from a termination date.

---

## 10. Common Roles / Personas

Use the source's exact role names; these are the ones that commonly appear in CPQ/CLM flows:

| Role | Typical responsibilities |
|------|--------------------------|
| **CLM Admin** | Configures record types, defaulting, lifecycle stages, amendment/versioning, notification rules |
| **Account Manager** | Creates/reviews/saves agreements, activates, amends, initiates renewals |
| **Canon Care (or renewals team)** | Owns renewals where the Account Manager does not |
| **Sales Manager** | Common notification recipient (e.g. expiry alerts) |
| **Approver** | Approval steps where an approval process is in scope |

---

## 11. Generic-to-Conga Phrasing Map (apply during authoring)

| Generic phrasing (avoid) | Preferred Conga phrasing (use where standard) |
|--------------------------|-----------------------------------------------|
| "Trigger contract generation" | "Click **Create Agreement** on the accepted proposal" |
| "Activate the agreement" | "Click **Activate**; Status Category moves to **In Effect**" |
| "The agreement is cancelled" | "Status Category updates to **Cancelled**" |
| "Generate the document" | "Click **Generate**; select template and output format (DOCX/PDF)" |
| "Send the document for signature" | "Click **Send for eSignature** (Conga Sign); set recipients and signing sequence" |
| "Create a new version" | "Click **Amend**; a new agreement **version** is created, prior version read-only" |
| "Start a renewal" | "Create a **Renewal Opportunity** and **Renewal Quote**; on acceptance a linked **Renewal Agreement** is created" |

Where a step depends on a project-specific label, message text, threshold, or custom config that
the source does not state, keep the `(wording TBC)` / `(value TBC)` / `(config TBC)` marker and
log it as an Open Point — this reference narrows what must be deferred, it does not eliminate the
deferral rule.

---

## Appendix A: Document Governance

| Version | Date | Author | Change Description |
|---------|------|--------|-------------------|
| 1.0 | 2026-07-25 | PS QA Team | Initial release — Conga CPQ/CLM objects, lifecycle (Status vs Status Category), standard actions, versioning, renewals, document generation/e-sign, integration/billing touchpoints, roles, and a generic-to-Conga phrasing map to raise execution-readiness and reduce (wording TBC). |

---

*End of Conga CPQ & CLM Domain Reference*
