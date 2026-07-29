# Test Case Generation Standard — PS AI QA Assistant

> Version: 1.1  
> Last Updated: 2026-07-25  
> Status: Approved  
> Classification: Internal — Professional Services QA  
> Review Cycle: Quarterly  
> Companion Documents: SYSTEM_INSTRUCTIONS.md, QA_METHODOLOGY.md, ARCHITECTURE.md

---

# QA Reasoning Loop

> **Owned by `SYSTEM_INSTRUCTIONS.md` — Workflow spine.** Not restated here (single
> source of truth). Reason like a Senior QA Engineer — understand the requirement,
> extract business rules and risks, then determine the evidence that proves the
> requirement works — *before* writing any test case. See that document for the
> authoritative workflow.

The concerns unique to this document are the authoring *mechanics* that turn a reasoned
requirement into rows: the column contract (§4.1), Title convention (§4.3), Precondition
generation (§4.4 / §4A), Test Step writing (§5), and the Expected Result standard (§6).
Those are owned here and not restated elsewhere.

## Final Rule

The AI must think first, then generate. Reasoning quality is more important than
generation speed. Aim for **complete acceptance-criterion coverage with no cap** on the
number of test cases, while avoiding redundant near-duplicate cases.

---

## 1. Requirement Analysis & Decomposition

> **Owned by `QA_METHODOLOGY.md` — Requirement Decomposition.** Not restated here (single
> source of truth). Source material is analyzed across every dimension and complex
> requirements are broken into atomic testable units, each with a stable Requirement/AC
> ID, before scenario design. See that document for the authoritative rule.

Test Case ID format — the one authoring identifier owned here — is defined in §4.2 and
defers to `EXCEL_SPECIFICATION.md`.

---

## 2. Business Rule Mapping

> **Owned by `QA_METHODOLOGY.md` — Business-Rule Classification.** Not restated here
> (single source of truth). Every business rule is classified and mapped to test cases
> that verify both its correct enforcement and its violation handling — a rule with
> positive-only coverage is insufficiently tested. See that document for the authoritative
> classification and minimum-coverage rules.

---

## 3. Scenario-to-Test Case Mapping

> **Owned by `QA_METHODOLOGY.md` — Scenario-Type Taxonomy.** Not restated here (single
> source of truth). The scenario-type catalog and the minimum scenario mix per acceptance
> criterion — including the rule that one scenario yields one test case and that an AC with
> rules must not be Positive-only — live there. See that document for the authoritative
> taxonomy. Each scenario is then implemented as executable rows using the mechanics in
> §4–§6 below.

---

## 4. Test Case Construction Standards

### 4.1 Complete Test Case Structure

The workbook column contract is owned by **`EXCEL_SPECIFICATION.md`** — exactly eight
columns, and no other document may add or remove one. Every test case is authored to
populate those eight columns:

| # | Column (per EXCEL_SPECIFICATION) | Description |
|---|----------------------------------|-------------|
| A | Test Case ID | Globally unique `{ProjectKey}-{Story}-TC-{NNN}` |
| B | Requirement Title | The source requirement this TC validates |
| C | Test Case Title | Prefixed descriptive title (`[Positive]`/`[Negative]`/`[Edge Case]`) |
| D | Pre-Conditions | Exact system state, user role, and data required |
| E | Step# | Sequential integer per step |
| F | Test Step | Single atomic action the tester performs |
| G | Expected Result | Observable outcome for the corresponding step |
| H | Priority | High / Medium / Low (per business impact) |

**Authoring concepts that are NOT columns:**
- **Test Data** is not a column — it is expressed inside Pre-Conditions and Test Steps as
  environment-independent characteristics/placeholders (see `QA_METHODOLOGY.md` — Test Data
  & Placeholder Convention).
- **Test Type** is not a column — it is encoded in the `[Positive]`/`[Negative]`/`[Edge Case]`
  prefix of the Test Case Title.
- **Actual Result** and **Status** are execution fields owned by Zephyr after import; they
  are intentionally absent from the workbook.

### 4.2 Test Case ID Convention

Test Case IDs follow the single format owned by **`EXCEL_SPECIFICATION.md` §7.2**:

```
{ProjectKey}-{Story}-TC-{NNN}      e.g. SAMP-125-TC-001
```

- Globally unique — the project+story prefix prevents collisions across workbooks,
  projects, and business units. A bare `SAMP-1-TC-001` is prohibited.
- Three-digit zero-padded sequence, restarting at 001 per workbook (uniqueness comes from
  the prefix). Never reused or recycled; assigned in generation order.

### 4.3 Title Convention

**Format:** `[Type Prefix] Verb + Object + Condition/Context`

**Type Prefixes (mandatory):**

| Prefix | When Used |
|--------|-----------|
| `[Positive]` | Happy path — valid data, authorized user, expected success |
| `[Negative]` | Error path — invalid data, unauthorized user, expected rejection |
| `[Edge Case]` | Boundary values, race conditions, unusual but valid scenarios |

**Title Examples:**

| Quality | Example | Issue |
|---------|---------|-------|
| ✅ Good | `[Positive] Verify user can create a new quote with all mandatory fields populated` | Clear actor, action, condition |
| ✅ Good | `[Negative] Verify system rejects quote when discount percentage exceeds 50%` | Specific violation condition |
| ✅ Good | `[Edge Case] Verify system accepts exactly 100 line items at the maximum limit` | Explicit boundary |
| ❌ Bad | `Test login` | No prefix, no specificity, no condition |
| ❌ Bad | `Verify form works` | Vague object, no condition |
| ❌ Bad | `Check validation` | Which validation? What form? What field? |
| ❌ Bad | `[Positive] Verify it works correctly` | "it" and "correctly" are meaningless |

### 4.4 Precondition Standards

Preconditions must create a **self-sufficient setup** — the tester should not need to research anything.

**Required elements:**

Test data must follow the **Test Data & Placeholder Convention** in `QA_METHODOLOGY.md` —
environment-independent characteristics stated characteristic-first, with a `<placeholder>`
only where a concrete value must be typed and genuinely cannot be known; never fictitious
names, emails, or IDs, and never invented numbers.

| Element | Must Specify | Example |
|---------|-------------|---------|
| User Context | Logged-in role (and permissions that matter) | "Logged in with the Sales Manager role" |
| Data Context | What entities must exist, by characteristic | "An account exists with status 'Active'; a product exists in the catalog with status 'Available'" |
| System State | Configuration, flags, settings | "Bulk discount feature is enabled; tax calculation is set to 'Automatic'" |
| Navigation State | Starting location | "User is on the Quotes list page" |

**Precondition quality comparison:**

| Bad | Good |
|-----|------|
| "User is logged in" | "User is logged in with the Sales Manager role and permission to create and edit quotes" |
| "Data exists" | "An account exists with status 'Active'; at least one product exists in the catalog with status 'Available'" |
| "On the right page" | "User has navigated to Settings > Quote Configuration > Discount Rules" |

---

## 4A. Execution-Ready Precondition Generation

Before writing any preconditions, the AI must analyze the requirement and identify everything that must already exist for the scenario to execute successfully.

For every test case, derive preconditions using the following analysis sequence:

1. Required User Role
2. Required Permissions
3. Required Business Object State
4. Required Configuration
5. Required Workflow Configuration
6. Required Environment Settings
7. Required Integration Dependencies (if applicable)
8. Required Regional Configuration (if applicable)

Generate preconditions as a numbered execution checklist.

### Rules

- Derive as many preconditions as the scenario genuinely requires (typically 3–6). Never
  pad to hit a count, and never invent system components or configuration that the source
  does not state.
- Every precondition must be independently verifiable.
- Never generate vague preconditions.
- Never use "User logged in" unless the role itself is significant.
- Describe required data characteristics instead of specific business data.

### Good Example

> 1. User is logged in with the Sales Manager role.
> 2. User has permission to submit quotes for approval.
> 3. A quote exists in the "Approval Requested" status.
> 4. User is on the Quote detail page for that quote.

### Bad Example

> - User logged in
> - Quote exists

---

## 5. Test Step Writing Guidelines

> **Use concrete Conga product terminology.** When a step maps to a standard Conga CPQ/CLM
> concept, name the real object, action, and lifecycle state from `CONGA_DOMAIN_REFERENCE.md`
> (e.g. "Click **Activate**; Status Category moves to **In Effect**") instead of a generic verb.
> This raises execution-readiness and reduces `(wording TBC)` markers. It does **not** relax the
> "Never Invent Anything" rule: specific record values, project-specific labels, thresholds, and
> custom configuration still come from the source or stay marked `(wording TBC)` / `(config TBC)`.

### 5.1 Step Granularity Rule

**Three steps is the FLOOR, not the target. Decompose to atomic steps first, then count.**
The step count of a test case is an *output* of decomposing the scenario into one-UI-action-per-step
(§5.2) — never a template to fill. Author the steps the scenario actually requires, then confirm
the total is at least three.

The mandatory structure:

| Step Position | Purpose | Example |
|---------------|---------|---------|
| Step 1 | Setup / Navigation (may be several atomic steps) | "Navigate to the Quotes section from the main menu" |
| Steps 2–N | Action(s) — exactly ONE UI action per step | "Enter a valid account name in the Account Name field" |
| Final Step | Verification / Assertion | "Verify the quote is saved with status 'Draft' and a success notification appears" |

**Do NOT force every test case into exactly three steps.** Collapsing several distinct UI
actions into one step to hit a fixed count is the most common granularity defect. A realistic,
well-decomposed manual test case usually runs **4–8 steps**; only a genuinely simple scenario (a
single field/control, a presence/absence check) legitimately lands at the three-step minimum. If
most test cases in a suite are exactly three steps, the suite is almost certainly under-decomposed
— re-check §5.2.

| ❌ Under-decomposed (compound steps, forced to 3) | ✅ Properly decomposed (one action per step) |
|--------------------------------------------------|----------------------------------------------|
| 1. Open the proposal and click 'Send Proposal' | 1. Open the proposal record |
| 2. Enter the recipient, set the sequence, and send | 2. Click the 'Send Proposal' button |
| 3. Verify the email is sent | 3. Enter the recipient details |
| | 4. Set the signing sequence for the recipients |
| | 5. Click the 'Send' button |
| | 6. Verify the email is sent with the document attached and the stage changes to Presented |

This is machine-checked (advisory) by `validate_workbook.py` **ST-01**, which flags a step that
bundles two UI actions (two action verbs joined by "and"/"then"). ST-01 is a Warning, not a gate —
the authoring discipline above is the real control; the check is a backstop.

### 5.2 One Action Per Step

Each step describes exactly **one user interaction** with the system. Never combine multiple actions.

| ❌ Incorrect (multiple actions) | ✅ Correct (atomic steps) |
|--------------------------------|--------------------------|
| "Fill in the form with name, email, and phone, then click Submit" | Step 2: "Enter a full name in the Full Name field" |
| | Step 3: "Enter a valid email in the Email field" |
| | Step 4: "Enter a valid phone number in the Phone field" |
| | Step 5: "Click the 'Submit' button" |
| "Navigate to Settings and change the timezone" | Step 2: "Click 'Settings' in the top navigation bar" |
| | Step 3: "Click 'General' in the left sidebar" |
| | Step 4: "Select 'UTC-5 Eastern Time' from the Timezone dropdown" |

### 5.3 Step Language Standards

| Rule | Correct | Incorrect |
|------|---------|-----------|
| Use imperative verbs | "Click", "Enter", "Select", "Navigate", "Verify" | "The user should click", "Try clicking" |
| Name the UI element | "Click the **'Save Draft'** button" | "Click the button" |
| Specify field names | "Enter the account name in the **Account Name** field" | "Enter the account name" |
| Specify values | "Select **'Active'** from the Status dropdown" | "Select a status" |
| Specify location | "In the **header section**, click **'New Quote'**" | "Click New Quote" |
| Be explicit about actions | "Press the **Enter** key" or "Click **'Search'**" | "Search for the record" |

### 5.4 Step-Expected Result Pairing

Every step MUST have a corresponding expected result. The pairing is 1:1 — no exceptions.

```
Step 1:     Navigate to the Quotes list page
Expected 1: Quotes list page loads displaying a table with columns:
            Quote Name, Account, Amount, Status, Created Date

Step 2:     Click the 'New Quote' button in the top-right corner
Expected 2: New Quote form opens with all fields empty;
            Status field is pre-populated with 'Draft'

Step 3:     Enter a quote name in the Quote Name field
Expected 3: Field accepts the input; no validation error is displayed

Step 4:     Select an account from the Account dropdown
Expected 4: Account is selected; Contact field auto-populates with
            the primary contact for the selected account

Step 5:     Click the 'Save' button
Expected 5: Quote is saved; success toast notification displays
            'Quote created successfully'; user is redirected to
            the Quote detail page showing all entered values
```

### 5.5 Navigation Steps

When a test case requires the user to reach a specific page, spell out the navigation explicitly:

| Bad | Good |
|-----|------|
| "Go to the settings page" | "Click 'Settings' in the left navigation sidebar" |
| "Open the record" | "In the Quotes table, click the hyperlinked Quote Name to open the record detail page" |
| "Navigate to the form" | "From the Dashboard, click 'Contracts' in the top menu bar, then click the 'New Contract' button" |

---

## 6. Expected Result Generation Standard

Expected Results must describe observable system behaviour that a **junior QA can verify without asking a BA or developer**, and that **two different testers would confirm identically**. This section is the single owner of *how* Expected Results are written; the workbook-level subset (banned phrases, empty/one-word results) is mechanically enforced by `Skills/TestCaseAuthoring/validate_workbook.py` — see VALIDATION_ENGINE.md.

Before writing an Expected Result, the AI must determine:

1. What changed?
2. What should the user see?
3. What should the system update?
4. Which business rule is being validated?
5. Which workflow transition occurred?
6. Which notification should be generated?
7. Which audit information should be available?
8. Which validations should be enforced?

Expected Results describe observable outcomes, never generic success statements.

### 6.1 Calibration — depth proportional to the step

Not every step needs a long checklist. Match verification depth to what the step actually does; **never pad a step with repeated or filler bullets to hit a count.**

| Step type | Expected Result depth |
|-----------|-----------------------|
| Navigation / setup / data-entry step | **One** bullet — the single observable outcome (page or section loaded, control visible/enabled, field accepts input with no error) |
| Action step carrying a rule or calculation | 1–2 bullets — the immediate outcome plus any inline validation or derived value |
| Key verification / final step of the test case | 2–6 bullets — the full, non-repeating set of checks that prove the requirement |

**Format:** each bullet on its own line, prefixed with `• `. **Maximum 6 bullets per step.** Each bullet states one verifiable, measurable outcome; no two bullets repeat the same check.

### 6.2 Verification lenses

For the key verification step, cover every lens the requirement or step **actually implies — and only those**:

| Lens | Verify |
|------|--------|
| UI behaviour | success/error message (content + location), button enabled/disabled, navigation target, correct field values, section visibility, grid/list row update, status-label change |
| Business logic | calculation result, rule-evaluation outcome, approval routing target, record create/update, state transition |
| Data validation | values persist after save, correct values displayed, data retained after refresh/reopen, mandatory-field enforcement, duplicate prevention |
| Backend / process | approval record created, audit/history entry added, notification generated (recipient + trigger), queue assignment, child/related records — **only when the requirement implies a backend effect** |

Do **not** assert a backend effect (audit entry, notification, child record) that the source does not state or clearly imply. Inventing system behaviour is prohibited — see SYSTEM_INSTRUCTIONS §2.3 (Never Invent Anything).

### 6.3 Negative and edge cases must state what must NOT happen

For `[Negative]` and `[Edge Case]` test cases the Expected Result must state, explicitly:

- **the outcome that must NOT occur** — e.g. no record created, no workflow or approval task triggered, record remains unchanged, user stays on the same page, data is not saved, duplicate not created; **and**
- **the validation/prevention behaviour and its location** — inline message below the field, error toast, banner at the top of the page — described by its *content*, never with invented exact wording.

**Example:** `• The quote is not submitted and its status does not change to "Approval Pending"; an inline validation message below the Discount field indicates the value exceeds the allowed threshold, and no approval task is created.`

### 6.4 Prohibited vague statements (enforced)

A standalone Expected Result consisting only of a bare phrase like the following is a **validation FAILURE** — replace it with the observable detail from §6.1–6.3:

> "Saved successfully" · "Record created" · "Record updated" · "Rule updated" · "Rule saved" · "Validation displayed" · "Quote submitted" · "Workflow triggered" · "Email sent" · "Success message displayed" · "Notification generated" · "Done" · "As expected" · "Works correctly"

| Prohibited | Why It Fails |
|------------|-------------|
| "Success message displayed" | Which message? What text? Where? |
| "Email sent" | To whom? What content? What subject? |
| "Record updated" | Which fields? What values? How to verify? |
| "Notification generated" | Which notification? Which recipient? What content? |

**Example — full test case (key step expanded):**

> Verify that:
> - Quote status changes to "Approval Requested".
> - A notification is generated for the configured recipient (only if the requirement specifies a notification).
> - The quote reference is displayed correctly on the confirmation.
> - The workflow/approval history records the status transition (only if the requirement specifies history).
> - No validation errors are displayed.

### 6.5 Handling Unknown Message Text

When the source requirement does not specify exact UI message text:

1. Write the expected result **descriptively** — what the message communicates, not exact words
2. Append `**(wording TBC)**`
3. Log as an Open Point in the output

**Example:**
> "Error notification displays indicating that the discount percentage cannot exceed the maximum allowed limit **(wording TBC)**"

**Never** invent message text that is not in the requirements.

---

## 7. Priority Assignment

> **Owned by `QA_METHODOLOGY.md` — Priority.** Not restated here (single source of truth).
> Priority (High / Medium / Low) reflects business impact if the tested behavior fails in
> production, assigned per the rubric, inheritance rules, and distribution guidance in that
> document. Priority is written into column H of every test case (see §4.1). See
> `QA_METHODOLOGY.md` for the authoritative rubric.

---

## 8. Test Coverage

> **Owned by `QA_METHODOLOGY.md` — Coverage Model.** Not restated here (single source of
> truth). Coverage is measured at the acceptance-criterion level, targets 100% with no cap,
> and spans the coverage layers (AC, scenario diversity, business rule, role, boundary,
> integration); the no-limit gap-resolution loop and coverage anti-patterns live there. See
> that document for the authoritative metric and rules.

---

## 9. Requirement Traceability

> **Owned by `QA_METHODOLOGY.md` — design-time traceability.** Traceability is a
> **design-time aid only** — the AC-to-TC mapping is used while authoring to guarantee
> complete coverage. The RTM is **not** emitted as a workbook sheet; coverage results are
> surfaced in the Master Summary and generation summary. See `QA_METHODOLOGY.md` for the
> authoritative traceability discipline.

---

## 10. Validation Before Output

> **Single source of truth — do not restate here.** Validation checks, severities, and
> the self-correction loop are owned by **`VALIDATION_ENGINE.md`**; the workbook-level
> subset is mechanically enforced by `Skills/TestCaseAuthoring/validate_workbook.py`.
> This document's job ends at authoring; validation is a separate concern with a single
> owner. Run every rule in `VALIDATION_ENGINE.md` before producing output, and do not
> deliver a workbook that fails the validator. (Previously this section restated a
> 15-check list that drifted out of sync with `VALIDATION_ENGINE.md` — removed.)

---

## 11. Error Handling

### 11.1 Source Retrieval Errors

| Error | Response | Impact on Output |
|-------|----------|------------------|
| Jira story not found (404) | Report error with exact key attempted; halt generation | No output — source does not exist |
| Confluence page not found (404) | Log as Open Point; proceed with Jira content only | Reduced coverage — clearly marked |
| Confluence page forbidden (403) | Log as Open Point with URL; proceed with available content | Reduced coverage — clearly marked |
| MCP connection failure | Report connection error; recommend retry | No output — cannot retrieve source |
| Empty Jira story (no description, no ACs) | Report that story lacks testable content; recommend story refinement | No output — nothing to test |

### 11.2 Analysis Errors

| Error | Response | Impact on Output |
|-------|----------|------------------|
| No acceptance criteria found | Check description for implicit ACs; if none, report gap | Generate from description if possible; otherwise report gap |
| Conflicting requirements between Jira and Confluence | Log as Conflict in Open Points; generate TCs for both interpretations | Output includes conflict documentation |
| Requirement references undefined term/entity | Log as Open Point; generate TC with assumption marked `[ASSUMPTION]` | Output includes assumption documentation |
| Circular dependency in business rules | Log as Conflict; test each rule independently | Output includes conflict documentation |

### 11.3 Generation Errors

| Error | Response | Impact on Output |
|-------|----------|------------------|
| Coverage validation fails | Enter the self-correction loop defined in `VALIDATION_ENGINE.md` | Output delayed until all checks pass |
| Duplicate test cases detected | Remove lower-quality duplicate; keep the more detailed version | Duplicate eliminated |
| Scenario count exceeds practical limit (>200 TCs) | Continue generating — there is no cap; quality is maintained regardless of volume | Large but complete output |
| Cannot determine correct priority | Default to **High** and document as Open Point | Conservative prioritization |

### 11.4 Output Errors

| Error | Response | Impact on Output |
|-------|----------|------------------|
| Excel generation script fails | Report error with details; retry with corrected data | Output delayed until script succeeds |
| Data validation warnings from script | Address each warning (coverage gaps, under-detailed TCs, missing test data) | Output delayed until warnings cleared |
| File write permission error | Report error; suggest alternative output directory | No file — manual intervention needed |

---

## 12. Quality Checklist

> **Single source of truth — do not restate here.** Pre-generation, per-test-case,
> post-generation, and final-output checks are owned by **`VALIDATION_ENGINE.md`**, and
> the workbook-structure checks are enforced by
> `Skills/TestCaseAuthoring/validate_workbook.py` against **`EXCEL_SPECIFICATION.md`**.
> The checklists formerly duplicated here referenced a stale schema (Traceability Matrix
> sheet, 12 columns including Test Data/Type/Actual Result/Status, `TC-{NNN}` IDs,
> `TC-{YYYYMMDD}` filenames) that no longer matches the specification — removed to prevent
> exactly that drift. Use `VALIDATION_ENGINE.md` and the validator.

---

## Appendix A: Test Type Enumeration

| Test Type | Definition | When to Use |
|-----------|-----------|-------------|
| Functional | Core feature behavior verification | Happy path CRUD, primary workflows |
| Negative | System response to invalid conditions | Bad data, unauthorized access, error states |
| Boundary | Testing at exact limits and thresholds | Min, max, min-1, max+1, zero, empty |
| Validation | Field-level and cross-field rule verification | Required fields, format checks, range limits |
| UI | Visual and interaction behavior | Layout, navigation, display, responsiveness |
| Integration | External system interaction | API success/failure, data sync, timeouts |
| Security | Access control and data protection | Auth, authz, session, encryption |
| Workflow | State machine and lifecycle testing | Transitions, approvals, rejections |
| End-to-End | Complete multi-feature user journeys | Cross-feature flows, onboarding, checkout |
| Regression | Existing behavior preservation | Re-verification after changes |

## Appendix B: Document Governance

| Version | Date | Author | Change Description |
|---------|------|--------|-------------------|
| 1.0 | 2026-07-22 | PS QA Team | Initial release |
| 1.1 | 2026-07-25 | PS QA Team | Trimmed to authoring mechanics; design concepts (coverage/scenario/business-rule/priority/decomposition) now referenced from QA_METHODOLOGY.md; RTM removed; placeholder examples made characteristic-first. |

---

*End of Test Case Generation Standard*
