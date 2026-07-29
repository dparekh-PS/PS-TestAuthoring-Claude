# Data Handling, Security & Privacy Standard — PS AI QA Assistant

> Version: 1.0
> Last Updated: 2026-07-23
> Status: Approved
> Classification: Internal — Professional Services QA
> Owner: this document is the single source of truth for how ingested and generated
> data is classified, handled, retained, and where it flows. No other document may
> define data-handling rules; they reference this one.

---

## 1. Why this document exists

The assistant ingests requirement content from customer-facing systems (Jira stories,
Confluence pages, Word/PDF documents) and produces test-case workbooks. That content can
contain confidential and personal data. This standard defines how that data must be
treated. It also corrects a previously stated, **incorrect** claim that "all processing
occurs locally" — see §6.

## 2. Data the assistant touches

| Source | Typical sensitivity | Examples |
|--------|--------------------|----------|
| Jira stories / ACs | Confidential (customer project) | requirement text, reporter/assignee names |
| Confluence pages | Confidential | design notes, org/process detail |
| Uploaded documents (Word/PDF) | Confidential to Restricted | SOWs, specs; may embed PII/credentials |
| Generated workbooks | Confidential | test cases derived from the above |

## 3. Data classification

| Class | Definition | Handling |
|-------|-----------|----------|
| **Public** | Approved for external release | No restriction |
| **Internal** | Conga-internal, non-customer | Default for this project's own governing docs |
| **Confidential** | Customer project material | Default for ALL ingested requirement content and generated output |
| **Restricted** | PII, secrets, regulated data | Must be minimised or redacted before use (see §4) |

Treat every ingested source as **Confidential unless known to be more sensitive**. Never
downgrade a classification.

## 4. Personal data (PII) and secrets — minimisation

The assistant's job is to test *behaviour*, not to reproduce personal or secret data.

- **Do not copy real PII into test cases.** Real names, emails, phone numbers, addresses,
  government IDs, and account numbers found in a source must be replaced with the
  environment-independent `<placeholders>` defined in `QA_METHODOLOGY.md` §8.5. This is
  both a quality rule and a privacy control.
- **Never reproduce secrets.** API keys, passwords, tokens, or connection strings that
  appear in a source must never be echoed into a test case, step, expected result, or
  summary. If encountered, log an Open Point ("credential present in source — not
  reproduced") and continue.
- **Redact before escalation.** When quoting a source in an Assumption/Conflict/Open Point,
  quote only the minimum needed and strip embedded PII/secrets.
- If a source is **predominantly** PII or clearly out of scope for QA (e.g. an exported
  customer contact list), stop and raise it with the requester rather than processing it.

## 5. Retention & artifacts

| Item | Retention rule |
|------|---------------|
| Ingested source content | Held only for the duration of the generation run; not persisted beyond the produced workbook |
| Generated workbook | Owned by the requester; stored in the requester's approved location, not duplicated elsewhere by the assistant |
| Backups created during migration/tooling | Kept only as long as needed to verify a change, then removed |
| Logs / debug output | Must not contain Confidential requirement text or any PII/secrets |

Workbooks carry `Comments: "AI-generated. Pending human QA review."` (per
`EXCEL_SPECIFICATION.md` §13.3) and must not be treated as an authoritative record until
reviewed.

## 6. Where data actually flows (accurate statement)

**Correction of a prior claim.** Earlier documentation stated "all data processing occurs
locally — no requirement data is sent to external services." That is **not accurate** for
this deployment and must not be relied upon.

The accurate statement: ingested requirement content **is sent to the configured
cloud-hosted large-language-model provider** to perform analysis and generation. Data in
transit is protected by the provider's transport encryption, and use is governed by the
organisation's agreement with that provider. Therefore:

- Only send content the organisation's LLM agreement permits.
- Restricted data (§3) must be minimised/redacted (§4) **before** it reaches the model.
- Do not paste credentials or regulated data into the assistant on the assumption it stays
  local — it does not.

Teams that require strictly local processing must raise that as a deployment requirement;
it is not the current behaviour.

## 7. Access & governance

- Access to sources follows the requester's existing Jira/Confluence permissions; the
  assistant does not broaden access and only reads what the connected account can read.
- This standard is reviewed on the same quarterly cycle as the other Knowledge documents.
- Violations (PII leakage into output, secrets reproduced, misclassification) are treated
  as defects in the generated deliverable and block delivery until corrected.

## Appendix: Document Governance

| Version | Date | Author | Change Description |
|---------|------|--------|-------------------|
| 1.0 | 2026-07-23 | PS QA Team | Initial release — classification, PII/secret minimisation, retention, accurate cloud-LLM data-flow statement. |
