---
name: TestCaseGenerator Examples
type: Curated Example Corpus (teach-by-example)
component: TestCaseGenerator Skill
version: 1.0
status: Approved
classification: Internal — Professional Services QA
governs: Knowledge/ (single source of truth)
companion: skill.md, workflow.md
---

# TestCaseGenerator — Curated Examples

## 1. Purpose

This document is a curated corpus of exemplary manual test cases. It teaches by
demonstration rather than instruction: it shows what excellent, execution-ready QA
writing looks like so that generated output can be pattern-matched against proven
examples.

It is not a user guide and not a set of rules. The authoritative rules — coverage
philosophy, authoring standard, validation logic, and workbook schema — remain
owned by the `Knowledge/` folder and are referenced here, never restated. The
full worked examples (Sections 7–13) conform to those standards and make them concrete;
the "Poor" items in the contrast pairs (Sections 3–6, 16) are deliberately
non-conforming and are labelled as such. Test Case IDs use a sample project/story key,
`SAMP-203-TC-###`, to illustrate the globally-unique format from `EXCEL_SPECIFICATION.md`
§7.2.

All examples are vendor-neutral. No project names, account names, user names,
quote IDs, or environment-specific identifiers appear. Following the
characteristic-first test-data convention (`QA_METHODOLOGY.md` §8.5), test data is
described by its defining characteristic — "a user with the approver role", "an
amount one unit above the approval threshold" — so a case executes without inventing
fictitious identifiers. Bare `<placeholder>` tokens, such as `<configured workflow>`,
are the exception: they are reserved for a concrete value the tester must type or
select but which cannot be known until the environment under test is in hand.

Every example is expressed in the mandatory feature-worksheet columns defined in
`EXCEL_SPECIFICATION.md`: **Test Case ID, Requirement Title, Test Case Title, Pre-Conditions,
Step#, Test Step, Expected Result, Priority.**

## 2. Writing Principles

The corpus is organized around six principles. Each example in this document
demonstrates one or more of them.

- **Traceability** — every test case names the requirement and acceptance criterion
  it proves, so coverage is verifiable rather than asserted.
- **Atomic steps** — each step is one observable tester action; setup, action, and
  verification are never collapsed into a single step.
- **Measurable expected results** — every expected result states observable evidence
  (a field value, status, message, or record change), not a generic "works" or
  "success".
- **Environment independence** — a test case is self-contained; a tester who has
  never read the requirement can execute it using descriptive, characteristic-first
  data.
- **Business-rule validation** — every rule with a threshold, permission, or
  transition is proven by both a conforming (positive) and a violating
  (negative/edge) case.
- **Review readiness** — assumptions and open points are surfaced, not buried, so a
  human reviewer can accept the deliverable with confidence.

## 3. Good vs Poor Examples

The contrast below is the fastest way to internalize the standard. Each pair uses
the same requirement; only the writing quality differs.

**Requirement (shared):** A user with the approver role can approve a request
whose amount is at or below the approval threshold; requests above the threshold
must be escalated.

**Poor:**

| Field | Value |
|-------|-------|
| Test Case Title | Test approval |
| Pre-Conditions | User logged in |
| Step 1 | Approve the request and check it works |
| Expected Result | Approval is successful |

Why it fails: the title carries no scenario type or intent; preconditions omit role,
record state, and configuration; the single step bundles action and verification and
is not atomic; the expected result is unmeasurable ("works", "successful"); and there
is no link to a requirement or acceptance criterion.

**Improved:**

| Field | Value |
|-------|-------|
| Test Case ID | SAMP-203-TC-014 |
| Requirement Title | Request Approval (R03 / AC-1) |
| Test Case Title | [Positive] Approver approves a request at or below the approval threshold |
| Pre-Conditions | 1. Logged in as a user with the approver role and approve permission. 2. A request exists in `Pending Approval` state with an amount equal to the approval threshold. 3. The approval workflow is enabled. 4. No prior approval decision exists on the request. |
| Step 1 | Open the request in `Pending Approval` state | The request detail view displays the amount equal to the approval threshold and an enabled **Approve** action |
| Step 2 | Select the **Approve** action | The status changes to `Approved`; an approval timestamp and the approver identity are recorded in the request history |
| Step 3 | Open the request history | The history shows exactly one `Approved` entry recording the acting approver and the timestamp |

Why it is better: the title declares scenario type and intent; the four preconditions
fix role, record state, configuration, and starting cleanliness; each of the three steps
is atomic with its own measurable expected result tied to observable evidence; and the
case is traced to `R03` / `AC-1`, satisfying the traceability standard in
`SYSTEM_INSTRUCTIONS.md`.

## 4. Preconditions Examples

Preconditions must establish user role, record/system state, and configuration —
enough for any tester to reach the starting point without guesswork.
`EXCEL_SPECIFICATION.md` treats preconditions that specify only a role as a warning.

**Poor:** `User is logged in.`

Why it fails: no role, no record state, no configuration; the tester cannot
reliably reproduce the starting condition.

**Improved:** `Logged in as a user with the approver role; a request exists in
Pending Approval state with an amount above the approval threshold; escalation is
enabled for a supported region.`

Why it is better: it names the role, the exact record state, the boundary-relevant
data condition, and the configuration flag, so the starting point is deterministic
and environment-independent.

## 5. Test Step Examples

A step is one atomic action the tester performs. Multiple actions in one step break
step-level verification and make failures ambiguous.

**Poor (compound):** `Enter the amount, submit the form, and open the approval
queue.`

Why it fails: three actions in one step; if the case fails, it is unclear which
action failed, and each action's outcome cannot be individually verified.

**Improved (atomic sequence):**

| Step# | Test Step |
|-------|-----------|
| 1 | Enter an amount one unit above the approval threshold in the **Amount** field |
| 2 | Select **Submit** |
| 3 | Open the **Approval Queue** |

Why it is better: each step isolates a single action, so each maps to its own
expected result and a failure points to one precise action.

## 6. Expected Result Examples

An expected result states observable evidence, per the verification-evidence
guidance in `TEST_CASE_GENERATION.md`. Evidence includes UI change, status, field
value, message, notification, audit history, or record update.

**Poor:** `It works as expected.`

Why it fails: nothing observable is specified; two testers could disagree on whether
the test passed.

**Improved (key verification step — multi-point):**
```
• The request status changes to "Escalated".
• A notification is generated for the escalation approver role (requirement specifies escalation notification).
• The request history records the escalation with a timestamp and the actor's identity.
```

Why it is better: it names independently observable evidence (status, notification, audit
entry), each on its own `• ` line, making pass/fail unambiguous and repeatable. Depth is
reserved for the *key* step — a navigation step above it would carry a single bullet such as
`• The Approvals list opens showing the request in the "Pending" state.` (calibration and
verification lenses are owned by `TEST_CASE_GENERATION.md` §6).

**Negative example — state what must NOT happen:**
```
• The escalation is not recorded and the request status remains "Pending".
• An inline message near the Escalate control indicates the user is not authorised to escalate; the user stays on the request page.
```

Why it is better: a negative result must assert the outcome that must *not* occur (status
unchanged, nothing recorded) plus the prevention/validation behaviour and its location —
never just "escalation fails".

## 7. Positive Test Case Example

Positive cases prove the requirement behaves correctly under valid, conforming
conditions. Titles are prefixed `[Positive]`.

| TC ID | Requirement Title | Test Case Title | Pre-Conditions | Step# | Test Step | Expected Result | Priority |
|-------|------------------|-------|----------------|-------|-----------|-----------------|----------|
| SAMP-203-TC-021 | Request Approval (R03 / AC-1) | [Positive] Approver approves a request at the approval threshold | 1. Logged in as a user with the approver role and approve permission. 2. A request exists in `Pending Approval` with amount equal to the approval threshold. 3. `<configured workflow>` enabled. 4. No prior approval decision exists on the request. | 1 | Open the request in `Pending Approval` state | Request detail displays amount equal to the approval threshold; **Approve** is enabled | High |
| | | | | 2 | Select **Approve** | Status changes to `Approved`; approval timestamp and approver identity recorded in history | |
| | | | | 3 | Open the request history | History shows one `Approved` entry with the acting approver | |

## 8. Negative Test Case Example

Negative cases prove the requirement rejects invalid input or unauthorized action
gracefully. A feature that accepts invalid input is as defective as one that rejects
valid input. Titles are prefixed `[Negative]`.

| TC ID | Requirement Title | Test Case Title | Pre-Conditions | Step# | Test Step | Expected Result | Priority |
|-------|------------------|-------|----------------|-------|-----------|-----------------|----------|
| SAMP-203-TC-022 | Request Approval (R03 / AC-2) | [Negative] Non-approver cannot approve a request | 1. Logged in as a user without approve permission. 2. A request exists in `Pending Approval` with amount within the approval threshold. 3. The approval workflow is enabled. 4. The request has no prior approval decision. | 1 | Open the request in `Pending Approval` state | Request detail is read-only; the **Approve** action is not displayed or is disabled | High |
| | | | | 2 | Attempt to trigger approval via the direct approval URL for the request | Action is blocked; an authorization error is shown; request status remains `Pending Approval` | |
| | | | | 3 | Open the request history | No approval entry is recorded for the non-approver | |

## 9. Edge Case Example

Edge cases exercise boundaries and unusual-but-valid conditions. Titles are prefixed
`[Edge Case]`. Boundary coverage pairs the exact limit with values immediately on
either side.

| TC ID | Requirement Title | Test Case Title | Pre-Conditions | Step# | Test Step | Expected Result | Priority |
|-------|------------------|-------|----------------|-------|-----------|-----------------|----------|
| SAMP-203-TC-023 | Request Approval (R03 / AC-3) | [Edge Case] Request one unit above threshold requires escalation | 1. Logged in as a user with the approver role. 2. Escalation is enabled for a supported region. 3. The approval workflow is enabled with an escalation path. 4. An escalation approver is configured to receive escalations. | 1 | Create a request with an amount one unit above the approval threshold | Request is created in `Pending Approval` state | Medium |
| | | | | 2 | Attempt to approve the request directly | Direct approval is blocked; the system indicates escalation is required | |
| | | | | 3 | Submit the request for escalation | Status changes to `Escalated`; the escalation approver is notified | |

Boundary set proven across the corpus: amount equal to the threshold (positive
approval, SAMP-203-TC-021), one unit above (escalation, SAMP-203-TC-023), and — where the requirement
defines a lower bound — one unit below any minimum.

## 10. Business Rule Coverage Example

Every business rule with a threshold, permission, or transition requires both a
conforming case and a violating case. The table shows how one rule maps to a
coverage set, demonstrating the coverage philosophy in `QA_METHODOLOGY.md` without
restating it.

**Business rule:** Requests at or below the approval threshold may be approved
by an approver; requests above must be escalated; only an approver
may approve.

| Rule dimension | Scenario | Example TC | Type |
|----------------|----------|-----------|------|
| Threshold — at limit | Approve at threshold succeeds | SAMP-203-TC-021 | Positive |
| Threshold — above limit | Above-threshold requires escalation | SAMP-203-TC-023 | Edge Case |
| Permission — authorized | An approver can approve | SAMP-203-TC-021 | Positive |
| Permission — unauthorized | A non-approver cannot approve | SAMP-203-TC-022 | Negative |
| Transition | `Pending Approval` → `Approved` / `Escalated` recorded in history | SAMP-203-TC-021, SAMP-203-TC-023 | Positive / Edge |

The rule is fully covered only when every dimension has at least one case and every
threshold/permission has both a conforming and a violating case.

## 11. Requirement Traceability Example

Traceability is reasoned at the acceptance-criterion level, not merely the
requirement level, at design time — it guides which test cases to author and where
coverage gaps remain. It is not a delivered workbook sheet; the traceability
discipline itself is owned by `QA_METHODOLOGY.md`. The prose below illustrates the
design-time reasoning for one requirement.

Working through requirement `R03` criterion by criterion:

- **AC-1 — Approver can approve at or below threshold.** Covered by the positive
  case `SAMP-203-TC-021`, which approves a request at the threshold. No violating
  scenario is meaningful for this criterion on its own.
- **AC-2 — Only an approver may approve.** The conforming side is already exercised by
  `SAMP-203-TC-021` (an approver *can* approve), so the criterion needs a violating
  case: `SAMP-203-TC-022` proves a non-approver cannot.
- **AC-3 — Above-threshold requests must escalate.** The conforming side is again
  covered by `SAMP-203-TC-021` (an at/below-threshold request does *not* escalate),
  and the boundary case `SAMP-203-TC-023` proves an above-threshold request does.

Notice that a single case (`SAMP-203-TC-021`) legitimately covers the conforming side
of several criteria, so complete coverage does not mean one case per AC. The reasoning
also surfaces the rule the Validation Engine enforces: an AC with positive-only
coverage where a violation is possible is a coverage gap (scenario-balance thresholds,
`VALIDATION_ENGINE.md`).

## 12. Scenario Grouping Example

Test cases are grouped by requirement and, within a requirement, ordered by scenario
type — positive first, then negative, then edge — so a reviewer reads coverage in a
predictable sequence.

```
Feature: Request Approval
└── R03  Request Approval
    ├── AC-1  Approve at/below threshold
    │   └── SAMP-203-TC-021  [Positive] Approve at threshold
    ├── AC-2  Only approver may approve
    │   └── SAMP-203-TC-022  [Negative] Non-approver cannot approve
    └── AC-3  Above threshold escalates
        └── SAMP-203-TC-023  [Edge Case] One unit above threshold escalates
```

The grouping makes gaps visible at a glance: an acceptance criterion with no child
test case, or a rule-bearing criterion with only a positive child, stands out
immediately.

## 13. Excel Output Example

The following illustrates one test case rendered in the mandatory column order from
`EXCEL_SPECIFICATION.md`. As that specification defines, TC-level fields (Test Case ID, Requirement Title,
Test Case Title, Pre-Conditions, Priority) are **forward-filled — the same value repeats
on every step row, never merged** — while Step#, Test Step, and Expected Result carry one
row per step. (The ASCII diagram below marks these cells "(repeated)"; earlier drafts said
"merged" — merges are now prohibited so sort/filter/Zephyr import work.)

```
┌──────────┬─────────────────────┬───────────────────────────┬──────────────────────────┬──────┬──────────────────────┬────────────────────────────┬──────────┐
│ Test     │ Requirement Title    │ Title                     │ Pre-Conditions           │ Step#│ Test Step            │ Expected Result            │ Priority │
│ Case ID  │                     │                           │                          │      │                      │                            │          │
├──────────┼─────────────────────┼───────────────────────────┼──────────────────────────┼──────┼──────────────────────┼────────────────────────────┼──────────┤
│ SAMP-203-TC-021   │ Request Approval    │ [Positive] Approver       │ Logged in as             │  1   │ Open the request in  │ Amount equals the          │ High     │
│ (repeated) │ (R03 / AC-1)  │ approves a request at     │ <approver role>; request │      │ Pending Approval     │ <approval threshold>;      │ (repeated) │
│          │ (repeated)            │ the approval threshold    │ in Pending Approval with │      │ state                │ Approve is enabled         │          │
│          │                     │ (repeated)                  │ amount = <approval       ├──────┼──────────────────────┼────────────────────────────┤          │
│          │                     │                           │ threshold>; <configured  │  2   │ Select Approve       │ Status → Approved;         │          │
│          │                     │                           │ workflow> enabled        │      │                      │ timestamp + approver       │          │
│          │                     │                           │ (repeated)                 │      │                      │ recorded in history        │          │
│          │                     │                           │                          ├──────┼──────────────────────┼────────────────────────────┤          │
│          │                     │                           │                          │  3   │ Open request history │ History shows one Approved │          │
│          │                     │                           │                          │      │                      │ entry by <approver role>   │          │
└──────────┴─────────────────────┴───────────────────────────┴──────────────────────────┴──────┴──────────────────────┴────────────────────────────┴──────────┘
```

Conformance notes: columns appear in the exact specified order with none added or
removed; the title begins with a `[Positive]` prefix; every step row has both an
action and a measurable expected result; and Priority is one of `High`/`Medium`/`Low`.

## 14. Validation Examples

Each example shows a finding the Validation Engine raises and the correction that
clears it. The validation *rules* are owned by `VALIDATION_ENGINE.md`; these examples
show what conforming output looks like after correction.

- **Acceptance-criteria coverage:** *Finding* — `AC-3` has no covering test case.
  *Correction* — add `SAMP-203-TC-023` (edge case) so every AC has ≥1 test case.
- **Scenario diversity:** *Finding* — `AC-2` (a permission rule) has positive-only
  coverage. *Correction* — add the negative case `SAMP-203-TC-022`; the Master Summary
  positive-only count returns to its target of 0.
- **Atomic steps:** *Finding* — a step combines "enter amount and submit".
  *Correction* — split into two sequential steps, each with its own expected result.
- **Measurable expected result:** *Finding* — expected result reads "approval
  works". *Correction* — replace with observable evidence: status, timestamp, and
  history entry.
- **Environment independence:** *Finding* — a step hardcodes a specific account
  identifier. *Correction* — replace with characteristic-first data
  (`a request with an amount equal to the approval threshold`).
- **Duplicate detection:** *Finding* — two test cases assert identical action and
  evidence. *Correction* — merge into one and reallocate the freed coverage to an
  uncovered AC.

## 15. AI Self Review Example

Before the formal validation gate, the internal self-review pass challenges each
test case. The illustration below shows the self-challenge questions applied to a
draft and the resulting improvement.

**Draft under review:** `SAMP-203-TC-030 [Positive] Approve request` — one step: "Approve the
request; it is approved." Preconditions: "User logged in."

Self-challenge outcome:

- *Is every acceptance criterion covered?* No — `AC-2` (unauthorized approval) has
  no case. → Add a negative case.
- *Are steps atomic?* No — action and verification are merged. → Split into an action
  step and a verification step.
- *Is the expected result measurable?* No — "it is approved" restates the action. →
  Replace with status, timestamp, and history evidence.
- *Are preconditions sufficient?* No — role, record state, and configuration are
  missing. → Add the approver role, `Pending Approval` state, and the configured
  approval workflow.
- *Could a tester execute this immediately?* Only after the above corrections.

Corrected result: the draft becomes `SAMP-203-TC-021` as shown in Section 7, and a companion
`SAMP-203-TC-022` is added to close the `AC-2` gap. The self-review resolves cheap defects
before the blocking Validation Engine gate runs.

## 16. Anti-Patterns

The following recurring defects must be recognized and avoided. Each is shown as the
anti-pattern followed by the corrective pattern.

- **Vague titles** — "Test login" → declare scenario type and intent:
  "[Positive] User signs in with valid credentials".
- **Compound steps** — "enter data, submit, and verify" → one atomic action per
  step, each with its own expected result.
- **Unmeasurable results** — "works as expected", "successful" → name observable
  evidence (status, field value, message, audit entry).
- **Role-only preconditions** — "user is logged in" → add record state, data
  condition, and configuration.
- **Positive-only coverage of a rule** — approving only the happy path → add the
  negative/edge case that violates the rule.
- **Missing traceability** — a test case with no requirement/AC reference → link
  every case to its `R`/`AC` ID.
- **Hardcoded environment data** — a fixed account name or quote ID →
  characteristic-first data (`a user with the required role`, `an amount above the
  approval threshold`); reserve `<placeholder>` tokens for values that must be typed
  but cannot be known.
- **Invented behavior** — testing a rule the source never states → record the
  assumption as an open point for review instead of asserting undocumented behavior.
- **Count over coverage** — many shallow, near-duplicate cases → fewer comprehensive
  cases that each close a distinct coverage item.

Each corrective pattern maps directly to a principle in Section 2 and to a check the
Validation Engine enforces, so avoiding these anti-patterns is what makes output both
review-ready and gate-passing.
