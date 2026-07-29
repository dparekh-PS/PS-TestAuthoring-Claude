# VALIDATION_ENGINE.md

# Validation Engine

## Purpose

The Validation Engine is the final quality gate for the PS AI QA Assistant.

Its responsibility is to ensure that every generated deliverable meets enterprise QA standards before being presented to the user.

The Validation Engine must execute after all AI reasoning is complete and before any Excel workbook or output is generated.

If any critical validation fails, the AI must automatically correct the issue and revalidate before producing the final deliverable.

The AI must never knowingly return incomplete, inaccurate, duplicated, or partially validated test cases.

---

# Validation Execution Flow

Requirement Analysis

↓

Requirement Extraction

↓

Acceptance Criteria Mapping

↓

Business Rule Identification

↓

Scenario Generation

↓

Test Case Generation

↓

Self Validation

↓

Gap Detection

↓

Automatic Correction

↓

Re-validation

↓

Excel Generation

↓

Final QA Readiness Check

↓

Return Deliverable

---

# Validation Categories

The Validation Engine performs the following validations.

0. Source Extraction Fidelity Validation (runs FIRST — gates all others)

1. Requirement Coverage Validation

2. Acceptance Criteria Validation

3. Business Rule Validation

4. Workflow Validation

5. Test Scenario Validation

6. Test Case Quality Validation

7. Preconditions Validation

8. Expected Result Validation

9. Duplicate Detection

10. Environment Independence Validation

11. Requirement Traceability Validation

12. Workbook Validation

13. QA Readiness Validation

14. Risk-Based Coverage Validation

---

# Source Extraction Fidelity Validation

Objective

Ensure the extracted requirements and acceptance criteria actually come from the source —
NOT from the AI's assumptions. This runs before every other check because all downstream
coverage math (100% AC coverage, RTM, business-rule coverage) is measured against the
extracted AC list. If that list is fabricated or incomplete, "100% coverage" is
meaningless — the AI would simply be covering its own invention.

Validation Rules

- Every extracted Requirement and Acceptance Criterion must be traceable to a specific
  location in the source (Jira field, Confluence section, or document heading). Record the
  source anchor alongside each AC.
- Any AC or rule that is INFERRED rather than stated verbatim must be flagged
  `[INFERRED]` and logged as an Open Point for human confirmation. Inference is allowed,
  but it must be visible — never silently promoted to a confirmed requirement.
- Numeric thresholds, limits, formulas, and rates that are implied but not stated must use
  the `(value TBC)` marker (see QA_METHODOLOGY §8.5) and be logged as Open Points. Never
  invent a specific number.
- **Abbreviations, acronyms, role names, and terms must not be expanded or defined beyond
  the source.** If the source says "OS", the output says "OS" — not "Operations Specialist".
  An expansion that does not appear verbatim in the source is an invention: reject it, use
  the source term, or mark it `[INFERRED]` / `<placeholder>` and log an Open Point. (This is
  the check behind SYSTEM_INSTRUCTIONS §2.3 "Never Invent Anything".)
- If the source contains no acceptance criteria and none can be quoted, do NOT synthesise a
  full AC set and report 100% coverage of it. Report the gap and request clarification.
- Intra-document contradictions (two ACs in the SAME source that conflict) must be logged
  as Conflicts, not silently reconciled.

On failure

Flag the affected items, log Open Points/Conflicts, and lower the reported Confidence.
Coverage percentages are only meaningful for ACs that pass this fidelity check; report
inferred/unconfirmed ACs separately so downstream 100% claims are honest.

---

# Requirement Coverage Validation

Objective

Ensure every functional requirement is represented by at least one test case.

Validation Rules

✓ Every requirement must be mapped.

✓ No requirement may remain uncovered.

✓ Coverage target = 100%

Build the AC↔TC map at design time and confirm **every extracted acceptance criterion has
at least one test case** before finishing. Write the **true** recomputed coverage figure
into the Master Summary "AC Coverage %" column — this is then machine-gated by
`validate_workbook.py` **CV-06** (any row below 100% is Fatal and the workbook is not
delivered) and **CV-07** (a feature with test cases must record ≥1 AC). Never write 100%
while an AC is uncovered — that is a coverage-honesty violation.

On its own the Master Summary "AC Coverage %" is a number the model writes — **self-graded**.
It becomes *verifiable* only through the coverage ledger below, which itemizes the ACs behind
the number and anchors each to the source.

If coverage is below 100%

STOP.

Generate missing test cases.

Restart validation.

---

# Coverage Ledger (required sidecar — makes coverage verifiable, not self-graded)

Every run emits a **coverage ledger** alongside the workbook:

    <workbook-name>.coverage.json      (a sidecar file, NOT a worksheet — the workbook stays clean)

Format (`schema: coverage-1.0`):

```json
{
  "schema": "coverage-1.0",
  "workbook": "TC-<source>_<date>.xlsx",
  "features": [
    {
      "sheet": "<exact feature sheet name>",
      "source": "<Jira key / Confluence page / document>",
      "acceptance_criteria": [
        {
          "id": "AC-a",
          "text": "<short verbatim AC snippet from the source>",
          "anchor": "<where in the source this AC came from: Jira field, Confluence section, doc heading>",
          "covered_by": ["<ProjectKey>-<Story>-TC-001", "<ProjectKey>-<Story>-TC-004"]
        }
      ]
    }
  ]
}
```

The ledger is authored **during extraction, from the source** — never reverse-engineered from
the finished workbook. `validate_workbook.py` then verifies it deterministically:

- **CV-08 (Fatal)** — every AC lists ≥1 `covered_by` test case; every listed ID actually
  exists in the workbook; and each covering test case lives **on that AC's own feature sheet**
  (no uncovered ACs, no phantom mappings, no cross-sheet borrowing).
- **CV-09 (Fatal)** — each feature's AC count, and the grand total and coverage %, must
  reconcile with the Master Summary (you cannot report 30 ACs at 100% while the ledger
  itemizes 20, per feature or overall).
- **CV-10 (Blocking)** — every AC carries a non-empty source `anchor` — the anti-fabrication
  teeth: each AC must state where in the source it came from.
- **CV-11 (Blocking)** — a **missing or malformed** ledger blocks delivery. The ledger is a
  required deliverable; coverage cannot be verified without it.

**Honest limit (stated plainly).** The ledger proves that every AC it *declares* is genuinely
covered by real test cases and is anchored to the source. It still cannot prove the ledger
*enumerated every AC in the source* — an AC the model never extracted cannot be detected from
artifacts alone. That residual gap is closed by two design-time controls: the Source
Extraction Fidelity checks above, and the human sampling audit below.

## Human Sampling Audit (design-time; closes the extraction-completeness gap)

Because extraction completeness is not machine-verifiable, each delivered suite is spot-checked
by a human reviewer:

- Sample **N acceptance criteria** — guideline `max(5, 10% of ACs)` — directly from the source.
- For each, confirm it appears in the coverage ledger with a correct anchor and ≥1 covering
  test case.
- Record the sample size and result in the run's generation summary.

A failed sample (a real source AC missing from the ledger) means extraction was incomplete —
regenerate before delivery.

---

# Acceptance Criteria Validation

Objective

Ensure every acceptance criterion has corresponding test coverage.

Validation Rules

✓ Every Acceptance Criterion must have at least one Positive scenario.

✓ Every Acceptance Criterion must have at least one Negative or Edge scenario whenever applicable.

✓ No Acceptance Criterion may be skipped.

Coverage target

100%

---

# Business Rule Validation

Objective

Ensure all business rules are validated.

Examples

Role restrictions

Workflow transitions

Regional behavior

Approval conditions

Notification logic

Validation Rules

Every identified business rule must be validated by one or more test cases.

If any business rule is missing

Regenerate test cases.

---

# Workflow Validation

Validate every workflow.

Examples

Create

Update

Approve

Reject

Cancel

Complete

Notify

Archive

Validation Rules

Every workflow transition must be covered.

Normal flow

Alternative flow

Failure flow

Re-entry flow where applicable

---

# Test Scenario Validation

Ensure the generated scenarios provide balanced coverage.

The Validation Engine should verify coverage across:

✓ Positive scenarios

✓ Negative scenarios

✓ Edge cases

✓ Permission-based scenarios

✓ Workflow scenarios

✓ Validation scenarios

✓ Error handling scenarios

✓ Regional scenarios (if applicable)

If any critical scenario category is missing, generate additional test cases.

## Scenario Balance Thresholds (quantified)

"Balanced" is not left to judgement. The Validation Engine checks these measurable
thresholds and generates additional test cases until they hold:

- **Every AC** has ≥1 Positive scenario (hard rule).
- **Every AC or business rule that carries a constraint** (a condition, limit, permission,
  state transition, or validation) has ≥1 Negative scenario AND ≥1 Edge scenario. "Whenever
  applicable" means: applicable whenever a constraint exists — a constrained AC covered only
  by Positive scenarios is a failure, not a judgement call.
- **Suite mix:** across the whole suite, Negative + Edge scenarios together must be **≥ 40%**
  of all test cases. A suite that is >60% Positive is flagged as under-tested and must be
  supplemented (this is the measurable form of the old "Positive-only" warning).
- **Per constrained AC:** at least a 1 : 1 ratio of (Negative + Edge) : Positive.
- These thresholds are a **design-time** check; the count of ACs that fail them is no longer
  reported as a Master Summary column (removed in EXCEL_SPECIFICATION v2.5). The target
  remains 0.

---

# Test Case Quality Validation

Every test case must be:

✓ Independent

✓ Atomic

✓ Executable

✓ Repeatable

✓ Easy to understand

✓ Business-focused

✓ Free from ambiguity

Reject test cases that are:

Too generic

Too broad

Too narrow

Duplicated

Incomplete

Dependent on another test case

---

# Preconditions Validation

## Objective

Ensure every generated test case contains execution-ready, environment-independent preconditions that enable a QA engineer to begin execution without ambiguity.

## Validation Rules

Every test case must include preconditions that clearly define:

✓ Required user role (if applicable)

✓ Required permissions or access level (if applicable)

✓ Required business object state

✓ Required system configuration

✓ Required workflow configuration

✓ Required feature enablement

✓ Required environment settings

✓ Required integration prerequisites (if applicable)

✓ Required regional configuration (if applicable)

---

### Preconditions Quality Rules

The Validation Engine must verify that every precondition is:

- Specific
- Actionable
- Independently verifiable
- Relevant to the scenario
- Environment independent

---

### Reject Generic Preconditions

Reject preconditions such as:

✗ User logged in

✗ Quote exists

✗ Account exists

✗ User has access

---

### Acceptable Examples

✓ User is logged in with the Operations Specialist role.

✓ A Quote exists in the required workflow status.

✓ Required approval workflow is configured.

✓ Notification framework is enabled.

✓ Required feature configuration is active.

✓ Required email templates are available.

---

### Environment Independence Validation

The Validation Engine must verify that no fictitious business data is introduced.

Never generate:

✗ Quote IDs

✗ Account Names

✗ Opportunity Names

✗ Customer Names

✗ Salesforce Record IDs

✗ Email Addresses

Instead, describe the characteristics of the required data.

---

### Validation Failure

If fewer than four meaningful preconditions exist, or if generic/vague preconditions are detected, the AI must regenerate the affected test case before producing the workbook.


---

# Expected Result Validation

## Objective

Ensure every Expected Result describes observable system behaviour that a QA engineer can objectively verify during execution.

Expected Results must tell the tester exactly what to validate after each test step.

---

## Validation Rules

**Primary check — required structure (positive rule).** Every Expected Result must name
a specific observable (UI element, field, record, status, message, or artifact) AND its
concrete post-condition (the exact state, value, or text). See `QA_METHODOLOGY.md` §8.6.
A result that lacks a named observable or a concrete post-condition fails — even if it
contains no blacklisted phrase (e.g. "Operation completes successfully" passes the
blacklist but fails this structure and is rejected). Validate structure first, blacklist
second.

Every Expected Result must be:

✓ Structured (named observable + concrete post-condition) — primary

✓ Observable

✓ Measurable

✓ Business-focused

✓ Independent

✓ Unambiguous

✓ Relevant to the executed step

---

## Verification Thinking

For every Expected Result, validate whether it confirms one or more of the following:

✓ User Interface behaviour

✓ Field value updates

✓ Workflow status transitions

✓ Business rule enforcement

✓ Notification generation

✓ Notification recipient validation

✓ System messages

✓ Audit history updates

✓ Record state changes

✓ Security or permission behaviour

✓ Error handling (when applicable)

---

## Reject Generic Expected Results

Reject Expected Results such as:

✗ Success message displayed

✗ Email sent

✗ Record updated

✗ Notification generated

✗ Validation successful

These statements are not sufficiently verifiable.

---

## Acceptable Expected Results

Expected Results should provide clear verification guidance.

Example:

Verify that:

- Workflow status changes to the expected state.
- Required notification is generated.
- Notification is sent to the configured recipient.
- Notification content matches the configured template.
- Business rules are enforced.
- Workflow history records the transition.
- No unexpected validation errors are displayed.

---

## Expected Result Completeness Validation

The Validation Engine must verify that Expected Results answer the following questions whenever applicable:

- What changed?
- What should the user observe?
- What system update occurred?
- Which business rule was enforced?
- Which workflow transition occurred?
- Which notification was generated?
- Which audit information was recorded?

---

## Validation Failure

If an Expected Result is generic, ambiguous, or does not provide sufficient verification guidance, the AI must regenerate the Expected Result before producing the final workbook.

## Machine-Enforced Rule Catalog (single source of truth)

The rules below are the **complete set of deterministic checks** enforced by
`Skills/TestCaseAuthoring/validate_workbook.py`. This table is **generated** from that
validator's `RULES` catalog — run `python Skills/TestCaseAuthoring/validate_workbook.py --rules`
to regenerate it; **do not hand-edit** the block between the markers. `Skills/lint_docs.py`
fails if this table drifts from the validator, so the codes and severities here can never
disagree with the code that enforces them (nor with any restatement in another doc — no other
document may render this table). Severity: **FATAL** = invalid, must not be delivered;
**BLOCKING** = must be fixed before delivery; **WARNING** = advisory. A few checks downgrade to
a lesser severity when a cell or column cannot be located (noted in the Check column).

<!-- RULES:BEGIN generated by validate_workbook.py --rules; do not edit by hand -->
| Code | Severity | Check |
|------|----------|-------|
| LOAD | FATAL | Workbook cannot be opened or parsed. |
| SV-01 | BLOCKING | Schema version stamp missing from document Keywords (expected `schema:X.Y`). |
| SV-02 | BLOCKING | Schema version stamp does not match the validator's SCHEMA_VERSION. |
| WV-01 | FATAL | First sheet is not 'Master Summary'. |
| WV-03 | FATAL | No feature worksheet exists after Master Summary. |
| WV-04 | FATAL | A column beyond the canonical 8-column schema is present. |
| WV-05 | FATAL | Feature-sheet header row is missing or does not match the exact 8 headers. |
| WV-06 | BLOCKING | Sheet name exceeds 31 characters or contains prohibited characters. |
| DV-01 | FATAL | A step row appears before any Test Case ID (the first TC row must carry the ID). |
| DV-02 | FATAL | Blank Test Case Title on a test case. |
| DV-03 | FATAL | Blank Test Step on a step row. |
| DV-04 | FATAL | Blank Expected Result on a step row. |
| DV-05 | BLOCKING | Blank Priority on a test case. |
| DV-06 | BLOCKING | Priority is not exactly High, Medium, or Low. |
| DV-07 | WARNING | Step# is not a sequential integer starting at 1 per test case. |
| DV-08 | WARNING | Test Case Title does not start with [Positive], [Negative], or [Edge Case]. |
| DV-09 | FATAL | A Test Case ID reappears as a new test case (IDs must be globally unique). |
| DV-10 | WARNING | Test case has fewer than the minimum number of steps (3). |
| DV-11 | FATAL | Test Case ID does not match the required PROJECT-STORY-TC-NNN format. |
| DV-12 | BLOCKING | Blank Requirement Title on a test case. |
| DV-13 | BLOCKING | Blank Pre-Conditions on a test case. |
| ER-01 | BLOCKING | The entire Expected Result is a single bare vague phrase (see BANNED_EXPECTED). |
| ER-02 | WARNING | The final (key verification) step carries only a thin one-line Expected Result. |
| CV-01 | FATAL | Master Summary test-case count does not match the actual feature-sheet count (Warning if the Test Cases column cannot be located). |
| CV-06 | FATAL | A Master Summary row reports AC Coverage % below 100% or blank (Blocking when the coverage column/row cannot be parsed). |
| CV-07 | BLOCKING | Master Summary internal inconsistency (a feature with test cases but 0 acceptance criteria, or a feature row with 0 test cases). |
| CV-08 | FATAL | Coverage ledger: an acceptance criterion is uncovered, is covered by a test case not present in the workbook, or is covered by a test case that belongs to a different feature sheet (cross-sheet coverage is not allowed). |
| CV-09 | FATAL | Coverage ledger: a feature's AC count (or the grand total / coverage %) does not reconcile with the Master Summary. |
| CV-10 | BLOCKING | Coverage ledger: an acceptance criterion has no source anchor (each AC must cite where in the source it came from). |
| CV-11 | BLOCKING | No coverage ledger sidecar found (or it is malformed) — AC coverage cannot be verified against a source-anchored AC list; the ledger is a required deliverable. |
| NS-01 | FATAL | Cross-workbook Test Case ID collision: an ID was already issued in a different workbook (per the persistent id_ledger.json). IDs must be globally unique across workbooks, projects, and business units. |
| NS-02 | WARNING | A Test Case ID uses a project key that is not an enabled project in project_registry.json — register the project so its IDs are namespaced and governed. |
| DP-01 | BLOCKING | A real-looking email address appears in a cell — reproduce personal data as an environment-independent characteristic/placeholder, never a real value (DATA_HANDLING.md). |
| DP-02 | BLOCKING | A probable secret/credential (API key, token, private key, JWT) appears in a cell — secrets must never be reproduced in test cases (DATA_HANDLING.md). |
| DUP-01 | WARNING | Two test cases on the same feature sheet are near-duplicates (identical title, or identical step + expected-result sequence) — merge or differentiate them. |
| EI-01 | WARNING | A cell contains a probable hard-coded environment/record identifier (e.g. a quote id like Q-100245 or a Salesforce record id) — use an environment-independent characteristic instead. |
| ST-01 | WARNING | A test step bundles multiple UI actions (a compound step: two action verbs joined by 'and'/'then') — split it so each step performs exactly one action (TEST_CASE_GENERATION.md 5.2). |
| ST-02 | WARNING | Suite is under-decomposed: an outsized share of test cases sit at the 3-step minimum (well-authored manual cases usually run 4-8 atomic steps; only simple presence/absence checks belong at the floor) (TEST_CASE_GENERATION.md 5.1). |
<!-- RULES:END -->

The catalog is deliberately a **structural backstop**: passing it is necessary but not
sufficient. It confirms the workbook is well-formed, uniquely identified, has valid
priorities, is coverage-complete on the ACs the run *extracted*, and carries no blank or
bare-platitude Expected Results — it cannot confirm a result is *correct* or *non-invented*,
that every AC was actually *extracted* from the source, or that scenarios are not near
duplicates. Those semantic guarantees remain the model's responsibility during SELF_REVIEW
(see `TEST_CASE_GENERATION.md` §6 for Expected Results) and the design-time sections above.

---
# Duplicate Detection Validation

The AI must identify duplicate scenarios.

Validation Rules

Detect:

Duplicate workflows

Duplicate validations

Duplicate business rules

Duplicate expected results

Duplicate scenario intent

Merge duplicate scenarios whenever appropriate.

Never generate duplicate test cases simply because different wording is used.

**Machine-checked backstop (DUP-01, Warning).** `validate_workbook.py` flags two test cases on
the same feature sheet that are near-duplicates — identical normalized title, or an identical
step + expected-result sequence. It is advisory (a heuristic, not proof of intent), so it warns
rather than blocks; the model still owns semantic de-duplication above.

---

# Environment Independence Validation

The AI must generate environment-independent test cases.

Never invent:

Account names

Customer names

Quote IDs

Opportunity IDs

Salesforce Record IDs

Product IDs

User names

Email addresses

Instead describe required data characteristics.

Correct

"A Quote exists in Approval Requested status."

Correct

"A user with Sales Manager permissions."

Correct

"A customer eligible for approval."

Incorrect

"Quote Q-100245"

Incorrect

"Account ABC Pharma"

Incorrect

"John Smith"

The AI should define required data characteristics rather than fictitious values.

**Machine-checked backstop (EI-01, Warning).** `validate_workbook.py` flags a cell containing a
probable hard-coded environment/record identifier (a quote id like `Q-100245`, a Salesforce
record id, etc.). It is high-precision and advisory — replace the literal with a characteristic.
The broader rule (account names, user names, etc.) remains a design-time authoring standard.

## Data-Handling Enforcement (machine-checked, DP-01/DP-02)

The subset of the above that is a **privacy/security** hazard is now machine-enforced by
`validate_workbook.py`, backed by `DATA_HANDLING.md`:

- **DP-01 (Blocking)** — a real-looking **email address** in any cell. Reproduce personal
  data as a characteristic/placeholder ("the approver's email", `<email>`), never a real
  value.
- **DP-02 (Blocking)** — a probable **secret/credential** in any cell (API key, token,
  private key, JWT). Secrets must never be reproduced in a test case.

These checks are deliberately high-precision (literal emails and well-known secret formats),
so characteristic-first placeholders never trip them. They make `DATA_HANDLING.md`'s "block
delivery on a PII/secret leak" rule real rather than honor-system. The broader
environment-independence rule above (account names, record IDs, etc.) remains a design-time
authoring standard, not fully machine-checkable.

---

# Requirement Traceability Validation

Every generated test case must maintain complete traceability.

Validation Flow

Requirement

↓

Acceptance Criteria

↓

Business Rule

↓

Scenario

↓

Test Case

Validation Rules

✓ Every Requirement is covered.

✓ Every Acceptance Criterion is covered.

✓ Every Business Rule is covered.

✓ Every Scenario is covered.

Coverage target

100%

---

# Workbook Validation

Before generating the Excel workbook verify:

Workbook structure matches EXCEL_SPECIFICATION.md.

Required worksheets exist.

Headers are correct.

Columns are populated.

No mandatory field is empty.

Test Case IDs are sequential.

Priorities are assigned.

No duplicate rows exist.

Workbook is ready for manual execution.

---

# QA Readiness Validation

Before returning the workbook, evaluate its execution readiness.

Assess:

Requirement completeness

Acceptance Criteria coverage

Business Rule coverage

Scenario quality

Step quality

Expected Result quality

Traceability

Workbook quality

Generate an overall QA Readiness assessment.

Possible outcomes:

READY FOR QA REVIEW

READY FOR EXECUTION

NEEDS REQUIREMENT CLARIFICATION

NEEDS REGENERATION

---

# Risk-Based Coverage Validation

Objective

Coverage is not uniform: higher-risk behaviour must be tested more deeply, and Priority
must reflect real business/technical risk rather than being asserted. Today Priority is
checked only for a valid enum value; this category checks that it is *justified* and that
depth follows risk.

Validation Rules

- **Priority must be justified, not asserted.** Each test case's Priority (`High`/`Medium`/
  `Low`) must be attributable to a risk factor from the rubric in `QA_METHODOLOGY.md` §7
  (business impact, data integrity, security/permissions, financial/legal exposure,
  irreversibility, integration blast-radius). A High with no supporting factor, or a
  security/permission/financial path marked Low, is a failure.
- **Depth follows risk.** Every acceptance criterion or rule assessed **High risk** must
  carry ≥1 Positive, ≥1 Negative, AND ≥1 Edge scenario (not a single happy-path case).
- **High-risk categories are mandatory when present.** If the requirement involves
  authorization/permissions, money/pricing/discount, data deletion or state changes that
  are hard to reverse, or cross-system integration, at least one Negative scenario must
  exercise the failure/denial path for each.
- **Distribution sanity.** A suite in which nothing is High, or in which everything is
  High, is flagged for re-assessment — Priority has lost discriminating power. (This is a
  prompt to review, not a fixed quota; genuinely uniform-risk features are allowed once
  reviewed.)

On failure

Re-assess Priority against the rubric, add the missing depth for High-risk items, and
document any deliberately low-coverage risk as an Open Point.

---

# Automatic Self-Correction

If validation detects any issue, the AI must:

Identify the problem.

Determine the root cause.

Correct the affected test cases.

Re-run every validation.

Repeat until all mandatory validations pass.

The AI must never return partially validated deliverables.

---

# Final Validation Summary

Before returning results, generate a validation summary including:

• Requirements Identified

• Acceptance Criteria Identified

• Business Rules Identified

• Workflow States Identified

• Generated Test Cases

• Positive Test Cases

• Negative Test Cases

• Edge Case Test Cases

• Requirement Coverage %

• Acceptance Criteria Coverage %

• Business Rule Coverage %

• Traceability Coverage %

• Duplicate Check Status

• Workbook Validation Status

• QA Readiness Status

• Confidence Level

• Open Clarifications

• Assumptions

Only return the workbook when all mandatory validation checks have passed.
