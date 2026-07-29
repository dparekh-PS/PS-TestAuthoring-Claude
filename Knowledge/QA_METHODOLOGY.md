# QA Methodology — PS AI QA Assistant

> Version: 2.5  
> Last Updated: 2026-07-25  
> Status: Approved  
> Classification: Internal — Professional Services QA  
> Review Cycle: Quarterly

---

## 1. Test Design Philosophy

### 1.1 Core Philosophy

Test design is a structured engineering discipline, not a creative exercise. The goal is to produce a deterministic, complete set of test cases that proves every documented behavior works as specified and fails gracefully when conditions are violated.

The assistant operates under these foundational beliefs:

| Belief | Implication |
|--------|-------------|
| Requirements are the single source of truth | Test only what is documented; never invent behaviors |
| Coverage is a hard constraint, not a goal | Output is blocked until 100% AC coverage is proven |
| Every acceptance criterion deserves its own validation | ACs are never "covered by implication" — they require explicit test cases |
| Negative testing is equally important as positive testing | A feature that accepts invalid input is as broken as one that rejects valid input |
| Test cases are written for execution, not documentation | Every TC must be independently executable by any QA engineer |

### 1.2 Design-First Approach

Test cases are never written stream-of-consciousness. The methodology requires a structured design phase before any test case is authored:

```
Requirement → Decomposition → Scenario Design → Test Case Authoring → Coverage Proof
```

Skipping decomposition and scenario design is the single most common cause of coverage gaps and low-quality test suites.

### 1.3 Coverage Objective

The target is **100% acceptance-criteria coverage with scenario diversity**:

- Every AC is covered by at least one test case
- Every AC with a business rule or validation is covered by at least one Negative or Edge Case
- Every AC with boundary values is covered by boundary test cases
- Coverage is measured at the AC level, not the requirement level
- Coverage is proven by tracing every AC to its covering test cases while authoring — a design-time discipline, not a verbal assertion

### 1.4 Audience

Test cases are written for a QA engineer who:
- Has never read the original requirement document
- Has basic familiarity with the application under test
- Will follow steps literally without interpretation
- Needs descriptive, environment-independent test data — not abstract or vague descriptions, but also not fictitious names or IDs

---

## 2. Requirement Decomposition

### 2.1 Purpose

Complex requirements contain multiple testable behaviors compressed into a single statement. Decomposition breaks these into atomic, independently testable units. **This is where coverage is won or lost.**

### 2.2 Decomposition Rules

| Source Pattern | Decomposition Approach | Example |
|----------------|------------------------|---------|
| Table with field definitions | Each row = one testable unit | A table with 12 fields → 12+ testable units |
| Picklist / Enum values | Each value = one testable unit | Status: Draft, Active, Expired → 3 units |
| Validation rules | Each rule = one testable unit | "Required, max 100 chars, alphanumeric only" → 3 units |
| Error messages | Each message = one testable unit | 4 distinct error messages → 4 units |
| State transitions | Each transition = one testable unit | Draft→Active, Active→Expired, Active→Cancelled → 3 units |
| Conditional logic | Each branch = one testable unit | "If admin then X, if user then Y, else Z" → 3 units |
| Calculation rules | Each formula/derivation = one testable unit | Net = Gross - Discount; Tax = Net × Rate → 2 units |
| Permission matrix | Each role × action combination = one testable unit | 3 roles × 4 actions → 12 units |

### 2.3 Anti-Patterns in Decomposition

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| "Verify all fields display correctly" | Collapses N validations into 1 vague TC | One TC per field with specific validation |
| "Test all status transitions" | Hides individual transition logic | One TC per valid transition + invalid transitions |
| "Verify form validation" | Obscures which rules are covered | One TC per validation rule (required, format, length) |
| "Test permissions for all roles" | Impossible to determine what was actually verified | One TC per role per critical action |
| "Verify dropdown contains correct values" | Doesn't test selection behavior or downstream effects | One TC to verify list population + TCs for each selection outcome |

### 2.4 Decomposition Depth

Decompose until each unit satisfies ALL of the following:
- It tests exactly ONE behavior or condition
- Its pass/fail verdict is unambiguous
- It can be executed independently of other units
- Its expected result is a single observable outcome

If a unit still contains "and" in its description (e.g., "field is required AND max 50 chars"), decompose further.

---

## 3. Business Rule Identification

### 3.1 Definition

A business rule is any constraint, calculation, condition, or logic that governs how the system behaves. Business rules are the most critical source of test cases because they define correctness.

### 3.2 Categories of Business Rules

| Category | Description | Example | Test Implication |
|----------|-------------|---------|------------------|
| Validation Rules | Input constraints on fields | "Email must be valid format" | Positive (valid email) + Negative (invalid formats) |
| Calculation Rules | Derived values or formulas | "Discount = ListPrice × DiscountRate" | Verify calculation accuracy with known values |
| Conditional Rules | If/then/else logic | "If quantity > 100, apply bulk discount" | Test each branch + boundary (99, 100, 101) |
| Sequencing Rules | Order-of-operations requirements | "Contract must be approved before activation" | Test correct sequence + out-of-order attempt |
| Uniqueness Rules | Duplicate prevention | "Product code must be unique per catalog" | Test duplicate creation attempt |
| State Rules | Allowed state transitions | "Cannot edit after approval" | Test allowed transitions + blocked transitions |
| Authorization Rules | Who can do what | "Only admins can delete records" | Test with authorized + unauthorized roles |
| Temporal Rules | Time-based constraints | "Offer expires after 30 days" | Test within window + after expiry |
| Threshold Rules | Limits and caps | "Maximum 5 line items per quote" | Test at limit + exceeding limit |
| Dependency Rules | Cross-entity relationships | "Cannot delete account with active contracts" | Test deletion with + without dependencies |

### 3.3 Extraction Technique

When reading requirements, apply this filter for every statement:

1. **Does this statement constrain behavior?** → It's a business rule
2. **Does this statement define a calculation?** → It's a business rule
3. **Does this statement specify a condition?** → It's a business rule
4. **Does this statement restrict who/when/how?** → It's a business rule

### 3.4 Business Rule Testing Mandate

Every identified business rule MUST generate at least:
- **One positive test** — Confirming the rule is enforced correctly with valid data
- **One negative test** — Confirming the system rejects violations of the rule
- **Boundary tests** (if the rule involves numeric thresholds) — Testing at, below, and above the boundary

---

## 4. Acceptance Criteria Analysis

### 4.1 Role of Acceptance Criteria

Acceptance criteria (ACs) are the contractual definition of "done" for a user story. They are the primary unit of coverage measurement. An untested AC means the story cannot be confidently accepted.

### 4.2 AC Analysis Process

For each acceptance criterion:

```
┌─────────────────────────────────────────────────────┐
│  Read the AC text exactly as written                │
├─────────────────────────────────────────────────────┤
│  Identify: WHO (actor), WHAT (action), WHEN         │
│  (condition), THEN (expected outcome)               │
├─────────────────────────────────────────────────────┤
│  Extract embedded business rules                    │
├─────────────────────────────────────────────────────┤
│  Identify implicit negative conditions              │
│  (What should NOT happen? What's the inverse?)      │
├─────────────────────────────────────────────────────┤
│  Assign AC ID (AC-1, AC-2, …)                       │
├─────────────────────────────────────────────────────┤
│  Determine minimum scenarios needed:                │
│  • Positive (proves AC is met)                      │
│  • Negative (proves violation is handled)           │
│  • Boundary (if thresholds exist)                   │
│  • Edge case (if applicable)                        │
└─────────────────────────────────────────────────────┘
```

### 4.3 AC Classification

| AC Type | Characteristics | Minimum Test Coverage |
|---------|-----------------|----------------------|
| Behavioral | "User can…", "System shall…" | Positive + Negative |
| Validation | "Field must be…", "Input is validated…" | Positive + each invalid case |
| Conditional | "When X, then Y" | Each branch + boundary |
| Permission | "Only [role] can…" | Authorized role + unauthorized role(s) |
| Calculation | "Value is computed as…" | Correct calculation + edge values |
| State | "Status changes from X to Y when…" | Valid transition + invalid transition |
| Integration | "Data is sent to…", "System receives…" | Success + failure + timeout |
| UI/Display | "Screen shows…", "Field displays…" | Present + absent conditions |

### 4.4 Scenario Diversity Requirement

An AC covered only by positive test cases is **insufficiently covered**. The minimum diversity requirement:

- **ACs with business rules** → Must have ≥1 Negative test
- **ACs with numeric values** → Must have Boundary tests
- **ACs with permissions** → Must have both authorized and unauthorized tests
- **ACs with state transitions** → Must have both valid and invalid transition tests
- **ACs with integrations** → Must have success and failure tests

### 4.5 AC Traceability

Every AC must appear in the design-time traceability mapping with:
- Its unique AC ID
- The parent requirement's Req ID
- The business rule it embodies (if any)
- The list of test case IDs that cover it

An AC with zero covering test cases is a **fatal coverage gap** — output cannot be produced. This mapping is a design-time reasoning aid; it is not emitted as a workbook sheet (see §6.3).

---

## 5. Scenario Identification

### 5.1 Purpose

Scenario identification transforms decomposed requirements into specific test conditions. Each scenario answers: "What specific situation am I testing, and what do I expect to observe?"

### 5.2 Scenario Type Taxonomy

| Category | Scenario Types | When to Apply |
|----------|---------------|---------------|
| **Core** | Positive (happy path), Negative (invalid/error) | Always — every feature needs both |
| **Data Validity** | Boundary values, Empty/Blank, Invalid format, Special characters, Maximum length, Minimum length | Any field with input constraints |
| **Field Behavior** | Mandatory field missing, Optional field behavior, Default values, Read-only enforcement | Any form or data entry screen |
| **Duplication** | Duplicate creation, Duplicate detection | Any field with uniqueness constraint |
| **Security** | Role-based access, Unauthorized action, Session expiry, Cross-user data isolation | Any feature with permission rules |
| **Workflow** | State transitions (valid), State transitions (invalid), Approval/rejection, Escalation | Any lifecycle or stage-based feature |
| **Integration** | API success, API failure, API timeout, Retry behavior, Data synchronization | Any feature with external system dependency |
| **Persistence** | Data saved correctly, Data retrieved correctly, Data survives refresh/navigation | Any CRUD operation |
| **UI/UX** | Navigation, Back button behavior, Refresh behavior, Sort/filter, Pagination | Any interactive screen |
| **Notifications** | Trigger condition, Content accuracy, Recipient correctness, Timing | Any feature with alerts or messages |
| **Concurrency** | Simultaneous edits, Race conditions, Locking behavior | Any shared resource |
| **Audit** | Action logged, Timestamp recorded, Actor captured | Any feature with audit requirements |
| **End-to-End** | Complete user journey spanning multiple features | Complex workflows crossing feature boundaries |

### 5.3 Scenario Selection Matrix

For each decomposed requirement unit, select applicable scenario types:

```
Decomposed Unit
       │
       ├── Has input fields?
       │     └── Apply: Boundary, Empty/Blank, Invalid format, Mandatory/Optional
       │
       ├── Has business rules?
       │     └── Apply: Positive, Negative (one per rule violation)
       │
       ├── Has permissions?
       │     └── Apply: Authorized access, Unauthorized access (per role)
       │
       ├── Has state transitions?
       │     └── Apply: Valid transition, Invalid transition, Concurrent transition
       │
       ├── Has calculations?
       │     └── Apply: Correct calculation, Zero values, Maximum values, Rounding
       │
       ├── Has integration points?
       │     └── Apply: Success, Failure, Timeout, Invalid response
       │
       └── Has persistence?
             └── Apply: Save, Retrieve, Refresh, Navigate away and return
```

### 5.4 Minimum Scenario Count Per AC

| AC Complexity | Minimum Scenarios |
|---------------|-------------------|
| Simple display/UI (no logic) | 1–2 (present + absent) |
| Single validation rule | 2–3 (valid + each invalid condition) |
| Business rule with conditions | 3–5 (each branch + boundary) |
| State transition | 2–4 (valid transition + invalid transitions) |
| Permission-gated action | N+1 (each role + unauthorized) |
| Calculation with variables | 3–6 (typical + boundary + edge values) |
| Integration point | 3–4 (success + failure + timeout + invalid data) |

---

## 6. Test Coverage Strategy

### 6.1 Coverage Model

The PS AI QA Assistant uses **Acceptance-Criteria-Level Coverage** as its primary metric:

```
Coverage % = (ACs with ≥1 test case / Total ACs) × 100
```

The target is always **100%**. Output is not produced until this target is met.

### 6.2 Coverage Layers

Coverage is measured across multiple dimensions, each independently validated:

| Layer | What It Measures | Pass Criterion |
|-------|------------------|----------------|
| AC Coverage | Every AC has ≥1 TC | 100% — no gaps |
| Scenario Diversity | ACs with rules have Positive + Negative/Edge | No Positive-only ACs (where rules exist) |
| Business Rule Coverage | Every rule has valid + invalid tests | Each rule in ≥2 TCs |
| Role Coverage | Every mentioned role is tested | Each role appears in ≥1 TC |
| Integration Coverage | Every integration point has success + failure | Each integration in ≥2 TCs |
| Boundary Coverage | Every numeric constraint has boundary tests | Min, Max, Min-1, Max+1 tested |

### 6.3 Coverage Proof: Design-Time Traceability

> **Traceability is a design-time discipline, not a deliverable.** The acceptance-criterion-to-test-case mapping is used while authoring to guarantee complete coverage; it is not emitted as a workbook sheet (the RTM sheet was removed in v2.4). Coverage is surfaced in the Master Summary.

While authoring, the author maintains a mapping from every acceptance criterion (by AC ID and parent Req ID) to the test case IDs that cover it, together with the business rule each AC embodies. This mapping is the reasoning tool that proves the coverage targets in §6.1–§6.2 are met: it exposes any AC with zero covering test cases (a fatal gap) and any AC covered only by Positive scenarios (a diversity gap). It is a design-time aid, not a delivered artifact.

### 6.4 Coverage Gap Resolution

When a coverage gap is identified:

1. Identify which AC is uncovered
2. Determine which scenario types are missing
3. Return to scenario design for that specific AC
4. Generate the missing test cases
5. Update the design-time traceability mapping
6. Re-validate coverage

This loop repeats until all gaps are resolved. There is no "acceptable gap" threshold.

---

## 7. Risk-Based Prioritization

### 7.1 Purpose

Priority determines execution order and focus during time-constrained testing. It does NOT affect whether a test case is generated — all required TCs are generated regardless of priority.

### 7.2 Priority Rubric

| Priority | Business Impact Criteria | Examples |
|----------|--------------------------|----------|
| **High** | Revenue impact, financial calculations, payment processing, contract execution, approval workflows, order fulfillment, data integrity for critical entities, security vulnerabilities | Pricing calculation, payment submission, contract approval, user authentication, data encryption |
| **Medium** | Search and filtering, notifications, reporting, non-critical workflows, alternative paths, configuration management | Search results accuracy, email notification delivery, report generation, settings update |
| **Low** | Cosmetic elements, label text, tooltip content, formatting, non-functional polish, rare edge cases with minimal business impact | Field label wording, icon alignment, tooltip hover text, date format display |

### 7.3 Priority Assignment Rules

1. **Default to High** when in doubt about business impact — it's safer to over-prioritize than under-prioritize
2. **Revenue-adjacent features are always High** — anything in the money flow (quotes, pricing, invoices, payments)
3. **Security features are always High** — authentication, authorization, encryption, data protection
4. **Core CRUD for primary entities is High** — create, read, update, delete for the feature's main objects
5. **Negative tests for High-priority features inherit High priority** — if the positive path is High, its failure mode is equally critical
6. **Integration failure scenarios are Medium minimum** — system-to-system failures need attention even if the feature is Low priority

### 7.4 Priority Distribution Expectation

A well-designed test suite for a typical feature typically distributes as:

| Priority | Expected Range | Concern If Outside Range |
|----------|---------------|--------------------------|
| High | 30–50% | Below 30%: under-prioritizing critical paths |
| Medium | 30–50% | Below 30%: missing alternative flows |
| Low | 10–25% | Above 30%: over-generating cosmetic tests |

---

## 8. Test Case Quality Standards

### 8.1 Structural Requirements

Every test case MUST contain all of the following fields:

| Field | Requirement | Quality Standard |
|-------|-------------|------------------|
| Test Case ID | Globally unique | `{ProjectKey}-{Story}-TC-{NNN}`, e.g. `SAMP-125-TC-001` (see EXCEL_SPECIFICATION §7.2) |
| Requirement Name | Source requirement description | Traceable back to Req ID |
| Title | Prefixed, descriptive | `[Positive] Verify successful login with valid credentials` |
| Pre-conditions | Complete setup state | Self-sufficient — tester needs no additional research |
| Test Data | Descriptive, environment-independent | Required data characteristics, not fictitious names or IDs |
| Steps | Atomic, numbered, ≥3 | One UI action per step, paired with expected result |
| Expected Results | Observable, verifiable, specific | Never vague; paired 1:1 with steps |
| Priority | Business impact assessed | High / Medium / Low per rubric |
| Test Type | Classified from enumeration | Functional / Negative / Boundary / Validation / UI / Integration / Security / Workflow / End-to-End / Regression |

### 8.2 Title Standards

> **Owned by `TEST_CASE_GENERATION.md` — Title convention.** Not restated here (single source of truth). Titles carry a `[Positive]`/`[Negative]`/`[Edge Case]` prefix followed by a specific verb + object + condition. See that document for the authoritative rule.

### 8.3 Step Granularity Standards

> **Owned by `TEST_CASE_GENERATION.md` — Test Step writing.** Not restated here (single source of truth). Each test case has a minimum of three atomic steps (setup → action → verify) with exactly one UI action per step, each paired 1:1 with an expected result. See that document for the authoritative rule.

### 8.4 Precondition Standards

> **Owned by `TEST_CASE_GENERATION.md` — Precondition generation.** Not restated here (single source of truth). Preconditions must be self-sufficient, specifying user/role, required data (by characteristic, not fictitious names), system state, and starting navigation. See that document for the authoritative rule.

### 8.5 Test Data Standards

| Case Type | Test Data Requirement | Example |
|-----------|----------------------|---------|
| Functional / Positive | Descriptive data characteristics (mandatory) | "A quote in Approved status", "A user with Sales Manager permissions", Qty: 10, Discount: 15% |
| Negative | Specific invalid value stated | Email: "not-an-email", Quantity: -5, Date: "32/13/2026" |
| Boundary | Exact boundary values | Quantity: 0 (below min), 1 (min), 100 (max), 101 (above max) |
| Empty/Blank | Explicitly stated | Field value: `<blank>` or `<empty string>` |
| Security | Role and credential described | "A user with Read-Only role" attempting admin action |

**Test Data & Placeholder Convention (authoritative — this is the single rule):**

Test data must be *environment-independent*: describe **what the data must be**, never a
specific fictitious record that only exists in one org. Prefer the characteristic; use a
placeholder only as a last resort.

1. **Characteristic / state form — DEFAULT, use this almost always.** Describe the required
   condition and let the tester pick any record that satisfies it: "a quote in `Approval
   Pending` status", "a user with the Sales Manager role", "a bundle with a 12% discount",
   "a non-approver user". This is self-contained and execution-ready. **When a characteristic
   already specifies the data, do NOT also add a `<placeholder>` token** — e.g. write *"Enter
   a valid account name"* or *"select any Active account"*, NOT *"Enter a valid account name
   (placeholder `<account name>`)"*. The trailing placeholder is noise and must be omitted.
2. **Placeholder form — sparing fallback, only when a concrete value must literally be
   typed and no characteristic captures it** (e.g. a tester must key a specific field value
   whose exact string matters and varies by environment). Then use one angle-bracket token,
   e.g. `<discount %>`. Do not scatter placeholders where "any valid X" or a back-reference
   ("the quote created in Step 1") reads better. Never invent `Acme Corp`, `sm_user@test.com`,
   `Q-2026-001`, or similar.
3. **Exact values when the source states them — use verbatim.** Documented numbers/bands are
   real data: "5%–10%", ">15%", "maximum 100 line items", "24 hours". Use them directly; do
   not turn a stated number into a placeholder.
4. **Unknown value marker `(value TBC)`:** when a threshold/limit/formula/rate is *implied
   but not specified* in the source, describe it and mark it — "discount exceeds the
   configured threshold **(value TBC)**" — and log it as an assumption. **Never invent a
   number** (do not write "50%" when the source is silent).
5. **Abbreviations, acronyms, role names, and terms — never expand or invent them.** Use the
   source's exact term verbatim (if the source says "OS", write "OS", not "Operations
   Specialist"). (Enforces SYSTEM_INSTRUCTIONS §2.3.)

Rule of thumb: a reader should almost never see a bare `<placeholder>` token — they should
see a described *condition*. Placeholders are the exception, not the default. This convention
overrides any older exemplar in this document or in `TEST_CASE_GENERATION.md`.

### 8.6 Expected Result Philosophy

**Principle:** Expected Results must be observable, specific, verifiable, and paired 1:1
with steps — a tester must reach the same pass/fail decision as any other tester without
consulting a BA or developer.

The authoring mechanics — required structure, prohibited-phrase list, verification lenses,
negative "what must NOT happen", and the machine-enforced ER-01/ER-02 gate — are owned by
`TEST_CASE_GENERATION.md` §6.

### 8.7 When Exact Message Text Is Unknown

When exact UI message text is unknown, follow the `(wording TBC)` procedure owned by
`TEST_CASE_GENERATION.md` §6.5.

---

## 9. Common QA Design Mistakes

This section catalogs the most frequent test design errors to explicitly avoid.

### 9.1 Coverage Mistakes

| Mistake | Consequence | Correct Approach |
|---------|-------------|------------------|
| Testing only the happy path | Defects in error handling go undetected | Every AC needs Negative + Edge scenarios |
| Collapsing a table into one TC | Individual field/row behaviors untested | Decompose each row/field into its own unit |
| Assuming "obvious" behavior is tested elsewhere | Coverage gap — nobody owns it | If it's in the requirements, test it explicitly |
| Counting integration tests as functional coverage | Different failure modes untested | Test functional behavior AND integration behavior separately |
| Ignoring linked Confluence pages | Missing context leads to shallow TCs | Always fetch and analyze all linked pages |

### 9.2 Granularity Mistakes

| Mistake | Consequence | Correct Approach |
|---------|-------------|------------------|
| Multiple actions in one step | Failure point is ambiguous | One UI action per step |
| Two-step test cases (navigate + verify) | Insufficient setup documentation | Minimum 3 steps: setup → action → verify |
| "Fill in the form" as a step | Tester doesn't know which fields or values | One step per field with specific values |
| Steps without expected results | Tester can't verify intermediate states | Every step has a paired expected result |
| Vague preconditions | Tester wastes time on setup research | Specify exact role, data, and system state |

### 9.3 Quality Mistakes

| Mistake | Consequence | Correct Approach |
|---------|-------------|------------------|
| "Works correctly" as expected result | Subjective; different testers interpret differently | State exact observable outcome |
| Inventing UI text not in requirements | Test will always "fail" against actual implementation | Use descriptive language + "(wording TBC)" |
| Missing test data for positive cases | Tester creates random data, inconsistent results | Describe required data characteristics |
| Priority based on test complexity | Misallocates execution effort | Priority based on business impact only |
| Duplicate test cases with different titles | Wastes execution time | Deduplicate during quality review |

### 9.4 Traceability Mistakes

| Mistake | Consequence | Correct Approach |
|---------|-------------|------------------|
| Orphan test cases (no AC link) | Untraceable; may test invented requirements | Every TC maps to an AC in the design-time traceability mapping |
| Traceability mapping built after test cases | Gaps discovered too late | Build the traceability mapping in parallel with TC generation |
| Implicit coverage ("SAMP-1-TC-005 also covers AC-3") | Unprovable claim; AC may actually be uncovered | Explicitly list every covering TC per AC |
| No source document citation | Cannot trace back to original requirement | Reference Jira key or Confluence page per feature |

### 9.5 Process Mistakes

| Mistake | Consequence | Correct Approach |
|---------|-------------|------------------|
| Writing TCs without decomposition | Missing granular behaviors | Always decompose before designing scenarios |
| Skipping negative scenarios for "simple" features | Simple features have simple bugs that go to production | Every feature gets Positive + Negative minimum |
| Finalizing output without coverage validation | Gaps in production | Self-correction loop is mandatory |
| Assuming linked pages add no new information | Missing business rules and context | Fetch and fully analyze every linked page |
| Stopping at first pass without self-review | Quality issues persist | Quality review + regeneration is mandatory |

---

## 10. Validation

> **Single source of truth — do not restate here.** All validation checks (pre-generation,
> post-generation, and failure response) are owned by **`VALIDATION_ENGINE.md`**, with the
> workbook subset enforced by `Skills/TestCaseAuthoring/validate_workbook.py`. This
> document defines the *methodology* (why and how to design coverage); it does not own the
> validation gate. The pre/post checklists formerly duplicated here lived in three
> documents at once and drifted — consolidated into `VALIDATION_ENGINE.md`.

---

## Appendix A: Scenario Type Quick Reference

| Scenario Type | One-Line Definition |
|---------------|---------------------|
| Positive | Confirm feature works with valid data under valid conditions |
| Negative | Confirm system rejects invalid data or unauthorized actions gracefully |
| Boundary | Test at exact limits (min, max, min-1, max+1) |
| Validation | Verify field-level and cross-field validation rules fire correctly |
| UI | Verify layout, navigation, responsiveness, and display behavior |
| Integration | Verify data exchange with external systems including failure modes |
| Security | Verify authentication, authorization, and data protection |
| Workflow | Verify state transitions, approvals, and lifecycle progression |
| End-to-End | Verify complete user journeys spanning multiple features |
| Regression | Verify existing behavior is preserved after changes |

## Appendix B: Priority Assignment Quick Reference

| If the feature involves… | Priority is… |
|--------------------------|--------------|
| Money (pricing, payments, invoices, billing) | **High** |
| Contracts, agreements, legal documents | **High** |
| Authentication or authorization | **High** |
| Core entity CRUD (primary business objects) | **High** |
| Approval workflows | **High** |
| Data integrity or persistence | **High** |
| Search, filtering, sorting | **Medium** |
| Notifications and alerts | **Medium** |
| Reporting and dashboards | **Medium** |
| Configuration and settings | **Medium** |
| Labels, tooltips, help text | **Low** |
| Cosmetic formatting | **Low** |
| Rare edge cases with no data loss risk | **Low** |

## Appendix C: Document Governance

| Version | Date | Author | Change Description |
|---------|------|--------|-------------------|
| 1.0 | 2026-07-22 | PS QA Team | Initial release |
| 2.5 | 2026-07-25 | PS QA Team | RTM-as-artifact removed; authoring mechanics (title/step/precondition) now referenced from TEST_CASE_GENERATION.md; design-time traceability note added. |

---

*End of QA Methodology*
