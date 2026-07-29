---
name: TestCaseAuthoring Workflow
type: Deterministic State Machine Specification
component: TestCaseAuthoring Skill
version: 2.5
date: 2026-07-25
status: Approved
classification: Internal — Professional Services QA
governs: Knowledge/ (single source of truth)
inherits: Skills/_base/workflow.base.md (Inheritance v1.1)
companion: skill.md
---

# TestCaseAuthoring Workflow Specification

## Workflow Overview

This document specifies the runtime behavior of the TestCaseAuthoring skill as a
deterministic finite state machine (FSM). It is not a linear procedure: execution
is modeled as a set of discrete states connected by guarded transitions, so that
the same inputs always drive the same state sequence and produce equivalent
deliverables.

The workflow is an orchestration layer. Each state coordinates *when* and *in
what order* the governing Knowledge documents are invoked and *what contract* must
hold before control advances; it does not restate the QA methodology, authoring
standards, validation rules, or workbook schema. All domain logic remains owned
exclusively by the `Knowledge/` folder — the single source of truth — and is
referenced, never duplicated, here.

The machine is defined by:

- **States** — the full FSM is `INIT → INTENT → ACQUIRE → REQ_VALIDATE → ANALYZE →
  PLAN → DESIGN → SELF_REVIEW → VALIDATE → ASSEMBLE → SUMMARY → RETURN` (plus
  `HALT`). Each state is an isolated, independently testable unit with a fixed
  contract (Purpose, Entry Criteria, Inputs, Actions, Knowledge Dependencies, Exit
  Criteria, Failure Handling, Output, Next State). All states except `ANALYZE`,
  `PLAN`, and `DESIGN` are owned by `Skills/_base/workflow.base.md`; only those
  three domain states are specified in full here.
- **Transitions** — a state advances only when its Exit Criteria evaluate true;
  otherwise a guarded transition routes to an error-recovery, retry, or
  human-review path. There are no implicit or unconditional transitions.
- **State data (context object)** — an accumulating, append-only record carried
  between states (request metadata, normalized requirements, provenance, coverage
  plan, generated artifacts, validation results, and status flags). A state reads
  the context, adds its output, and passes it forward; it never mutates a prior
  state's output.
- **Terminal states** — `RETURN_DELIVERABLES` (success) and `HALT` (safe stop with
  guidance). Every recovery path resolves to a retry, a human checkpoint, or
  `HALT`; no path dead-ends.

Determinism guarantee: given identical inputs and identical Knowledge document
versions, the FSM traverses an identical state path and yields an equivalent
deliverable, independent of requester or project.

## Inheritance (v1.1)

This workflow **inherits the shared substrate** in `Skills/_base/workflow.base.md`. The
states `INIT, INTENT, ACQUIRE, REQ_VALIDATE, SELF_REVIEW, VALIDATE, ASSEMBLE, SUMMARY,
RETURN, HALT`, plus the context object, bounded retry strategy, error recovery, and human
checkpoints, are **owned by the base**, which is authoritative; they appear below only as
short stubs pointing to the base (never re-specified, to prevent drift). The states this
skill genuinely owns are the **domain states** `ANALYZE → PLAN → DESIGN`, specified in
full below. A second skill reuses the base and swaps in its own domain states; nothing
here is copied. See `Skills/SKILLS_REGISTRY.md`.

## State Inventory

(Ownership per the Inheritance note above: all states except `ANALYZE`, `PLAN`, and
`DESIGN` are inherited from `Skills/_base/workflow.base.md`.)

| # | State | ID | Kind |
|---|-------|----|------|
| 1 | Request Initialization | `INIT` | Entry |
| 2 | Intent Recognition | `INTENT` | Decision |
| 3 | Requirement Acquisition | `ACQUIRE` | I/O |
| 4 | Requirement Validation | `REQ_VALIDATE` | Gate |
| 5 | Business Analysis | `ANALYZE` | Processing |
| 6 | Coverage Planning | `PLAN` | Processing |
| 7 | Test Design | `DESIGN` | Processing |
| 8 | AI Self Review | `SELF_REVIEW` | Gate |
| 9 | Validation Engine | `VALIDATE` | Gate |
| 10 | Workbook Assembly | `ASSEMBLE` | I/O |
| 11 | Generation Summary | `SUMMARY` | Processing |
| 12 | Return Deliverables | `RETURN` | Terminal (success) |
| — | Halt | `HALT` | Terminal (safe stop) |

## State Transition Diagram (ASCII)

```
                         ┌───────────────────────────────────────────────┐
                         │                                               │
                         ▼                                               │
   ( start )──▶ [1 INIT] ──▶ [2 INTENT] ──▶ [3 ACQUIRE] ──▶ [4 REQ_VALIDATE]
                   │            │  ▲            │  ▲                │  │
                   │            │  │clarify     │  │retry           │  │clarify
                   │            │  └────────────┼──┴────────────────┘  │
                   │            │  (HUMAN CP-1) │  (retry ≤N)          │ (HUMAN CP-2)
                   │            ▼               ▼                       ▼
                   │        [HALT]◀─────────[HALT]◀──────────────── proceed
                   │                                                   │
                   │                                                   ▼
                   │                                            [5 ANALYZE]
                   │                                                   │
                   │                                                   ▼
                   │                                             [6 PLAN]
                   │                                                   │
                   │                                                   ▼
                   │                                            [7 DESIGN]
                   │                                                   │
                   │                                                   ▼
                   │                                        [8 SELF_REVIEW]
                   │                                          │ pass │ fail
                   │                                          │      └──┐
                   │                                          ▼         │ correct
                   │                                    [9 VALIDATE]     │ & re-enter
                   │                                     │ pass │ fail   │ (≤N)
                   │                                     │      ├────────┘
                   │                                     │      │ unresolved
                   │                                     │      ▼
                   │                                     │  (HUMAN CP-3)──▶[HALT]
                   │                                     ▼
                   │                              [10 ASSEMBLE]
                   │                                     │
                   │                                     ▼
                   │                              [11 SUMMARY]
                   │                                     │
                   │                                     ▼
                   │                              [12 RETURN] ──▶ ( end: review-required )
                   │
                   └──(unrecoverable init error)──▶ [HALT]

  Legend:  [n STATE] = FSM state    ──▶ guarded transition (Exit Criteria true)
           HUMAN CP-x = human review checkpoint    [HALT] = safe terminal stop
           retry ≤N = bounded retry per Retry Strategy
```

## States

The domain states `ANALYZE`, `PLAN`, and `DESIGN` are specified below in the fixed
nine-field contract (Purpose, Entry Criteria, Inputs, Actions, Knowledge
Dependencies, Exit Criteria, Failure Handling, Output, Next State). The remaining
states are inherited and appear as short stubs pointing to
`Skills/_base/workflow.base.md`, which holds their authoritative contracts. States
are self-contained: a state depends only on the context object it receives and the
Knowledge documents it names, never on the internal behavior of another state.

### 1. Request Initialization — `INIT`

Inherited from `Skills/_base/workflow.base.md` — see there for the full contract. The
base establishes the authoritative reasoning frame (`MASTER_CONTEXT.md`,
`SYSTEM_INSTRUCTIONS.md`) and instantiates the context object. Next state: `INTENT`.

### 2. Intent Recognition — `INTENT`

Inherited from `Skills/_base/workflow.base.md` — see there for the full contract. The
base confirms the request maps to the manual-test-case-generation capability
(`USER_REQUEST_PATTERNS.md`, `AI_CAPABILITIES.md`), enumerates the source manifest,
and routes low-confidence intent to CP-1. Next state: `ACQUIRE` or `HALT`.

### 3. Requirement Acquisition — `ACQUIRE`

Inherited from `Skills/_base/workflow.base.md` — see there for the full contract. The
base owns Atlassian MCP retrieval and the Jira hardening (`fields:["*all"]`, the
Acceptance Criteria custom field, and distinguishing an absent value from a
not-fetched one), Confluence link resolution, upload/inline parsing, source
consolidation with provenance, and access-failure recovery. It is intentionally not
re-specified here to avoid drift. Next state: `REQ_VALIDATE`.

### 4. Requirement Validation — `REQ_VALIDATE`

Inherited from `Skills/_base/workflow.base.md` — see there for the full contract. The
base assesses completeness and input sufficiency, classifies findings as blocking or
recordable, and routes blocking deficiencies to CP-2. Next state: `ANALYZE`.

### 5. Business Analysis — `ANALYZE`

- **Purpose:** Derive the testable meaning of the validated requirements —
  decomposition into testable units, business rules, and actors.
- **Entry Criteria:** Validated requirement set present.
- **Inputs:** Validated requirement set; open-points ledger.
- **Actions:** Invoke the requirement-decomposition and reasoning discipline defined
  in the Knowledge base to produce testable assertions with stable identifiers.
  This state orchestrates that reasoning; it does not define it.
- **Knowledge Dependencies:** `QA_METHODOLOGY.md` (decomposition discipline),
  `TEST_CASE_GENERATION.md` (QA reasoning loop, analysis steps).
- **Exit Criteria:** Every in-scope requirement is decomposed into identified
  testable units with stable IDs.
- **Failure Handling:** If decomposition surfaces a previously undetected blocking
  ambiguity, transition back to `REQ_VALIDATE` (bounded) to reclassify and, if
  needed, reach CP-2.
- **Output:** Decomposed testable-assertion model.
- **Next State:** `PLAN`.

### 6. Coverage Planning — `PLAN`

- **Purpose:** Establish the coverage target and scenario plan that generation must
  satisfy, before any test case is authored.
- **Entry Criteria:** Decomposed testable-assertion model present.
- **Inputs:** Testable-assertion model.
- **Actions:** Map scenario coverage (positive, negative, boundary, edge, and other
  required scenario classes) to each acceptance criterion, establishing the
  acceptance-criteria-level coverage plan that later states populate and validate
  against. The per-feature, source-anchored AC-to-test-case mapping captured here is
  what is written to the `<name>.coverage.json` coverage ledger at `ASSEMBLE`.
- **Knowledge Dependencies:** `QA_METHODOLOGY.md` (coverage philosophy and scenario
  design).
- **Exit Criteria:** A coverage plan exists in which every acceptance criterion is
  associated with its required scenario classes.
- **Failure Handling:** If the plan cannot achieve full AC association from the
  available model, return to `ANALYZE` (bounded) to complete decomposition.
- **Output:** Coverage plan (per-feature AC-to-scenario mapping).
- **Next State:** `DESIGN`.

### 7. Test Design — `DESIGN`

- **Purpose:** Author execution-ready manual test cases that satisfy the coverage
  plan.
- **Entry Criteria:** Coverage plan present.
- **Inputs:** Coverage plan; testable-assertion model.
- **Actions:** Execute the authoring standard to produce self-contained test cases
  with preconditions, steps, expected results, and environment-independent test
  data, each linked to its source acceptance criterion. This state applies the
  standard; it does not define it.
- **Knowledge Dependencies:** `TEST_CASE_GENERATION.md` (authoring standard and
  reasoning loop), `QA_METHODOLOGY.md` (scenario and test-data expectations).
- **Exit Criteria:** A test case exists for every planned coverage item and each is
  linked to its acceptance criterion.
- **Failure Handling:** If a planned item cannot be authored, return to `PLAN`
  (bounded) to reconcile the plan; if reconciliation fails, escalate via CP-3.
- **Output:** Draft test case set with AC linkage.
- **Next State:** `SELF_REVIEW`.

### 8. AI Self Review — `SELF_REVIEW`

Inherited from `Skills/_base/workflow.base.md` — see there for the full contract. The
base runs an internal quality and coverage pass on the draft (rubric from
`QA_METHODOLOGY.md` and `TEST_CASE_GENERATION.md`), applies first-pass corrections,
and routes coverage gaps back to `DESIGN`/`PLAN` under bounded retry. Next state:
`VALIDATE`.

### 9. Validation Engine — `VALIDATE`

Inherited from `Skills/_base/workflow.base.md` — see there for the full contract. The
base runs the mandatory, blocking validation pipeline defined by
`VALIDATION_ENGINE.md` and single-sourced in `validate_workbook.py` (the RULES
catalog, `--rules`). Coverage completeness is checked via CV-06/07 and the coverage
ledger via CV-08/09/10, with a missing or malformed ledger blocking (CV-11);
cross-workbook Test Case ID uniqueness is checked via NS-01 (Fatal) and NS-02
(Warning) against `project_registry.json` and `id_ledger.json`. Next state:
`ASSEMBLE`.

### 10. Workbook Assembly — `ASSEMBLE`

Inherited from `Skills/_base/workflow.base.md` — see there for the full contract,
including `_v{N}` regeneration versioning (a new file is written, never an
overwrite). **TestCaseAuthoring specifics:** the outputs are the Excel workbook
(six-column Master Summary + one eight-column feature worksheet per feature, no
Review Summary/RTM sheet as of v2.4) per `EXCEL_SPECIFICATION.md`, the REQUIRED
`<name>.coverage.json` coverage ledger written alongside it, and the
`apply_merged_layout` presentation pass. ID registration is not performed here —
`RETURN` registers IDs via `validate_workbook.py --register <workbook>` after
delivery. Next state: `SUMMARY`.

### 11. Generation Summary — `SUMMARY`

Inherited from `Skills/_base/workflow.base.md` — see there for the full contract. The
base compiles the response-level generation summary (coverage, validation, source
provenance, assumptions/open-points/conflicts), reports the diff versus the prior
`_v{N}` version on regeneration, and asserts each success criterion holds. Next
state: `RETURN`.

### 12. Return Deliverables — `RETURN`

Inherited from `Skills/_base/workflow.base.md` — see there for the full contract. The
base returns the workbook and its coverage ledger with an explicit review-required
posture. **TestCaseAuthoring specific:** after the workbook passes and is delivered,
`RETURN` registers its IDs via `validate_workbook.py --register <workbook>`. Terminal
success state.

## Error Recovery Paths

Every failure resolves to exactly one of three outcomes: bounded retry, human
checkpoint, or safe `HALT`. No path continues the pipeline on unresolved failure,
and no path dead-ends.

| Failure condition | Origin state(s) | Recovery path | Terminal if unresolved |
|-------------------|-----------------|---------------|------------------------|
| Framework/init load error | `INIT` | None (non-retryable) | `HALT` |
| Ambiguous / low-confidence intent | `INTENT` | CP-1 clarification | `HALT` |
| Transient source access failure (Jira/Confluence via MCP) | `ACQUIRE` | Bounded retry | `HALT` (if primary) |
| Permanent failure on sole/primary source | `ACQUIRE` | None | `HALT` |
| Failure on supplementary source | `ACQUIRE` | Log + continue with reduced context (flagged in the generation summary) | proceeds |
| Incomplete requirements / missing primary AC | `REQ_VALIDATE` | CP-2 clarification | `HALT` |
| Cross-source conflict | `REQ_VALIDATE` | `MASTER_CONTEXT.md` precedence, else record open point → CP-2 | `HALT` |
| Late-discovered blocking ambiguity | `ANALYZE` | Return to `REQ_VALIDATE` (bounded) → CP-2 | `HALT` |
| Coverage plan cannot reach full AC association | `PLAN` | Return to `ANALYZE` (bounded) | CP-3 → `HALT` |
| Planned coverage item not authorable | `DESIGN` | Return to `PLAN` (bounded) | CP-3 → `HALT` |
| Self-review coverage/quality gap | `SELF_REVIEW` | Return to `DESIGN`/`PLAN` (bounded) | CP-3 → `HALT` |
| Validation failure | `VALIDATE` | Automatic-correction loop re-enters `VALIDATE` (bounded) | CP-3 → `HALT` |
| Workbook schema non-conformance | `ASSEMBLE` | Structural correction + one re-assembly | `HALT` |
| Unmet success criterion | `SUMMARY` | Return to earliest responsible state (bounded) | CP-3 → `HALT` |
| Delivery failure | `RETURN` | None (work preserved) | `HALT` |

On any `HALT`, the machine emits a diagnostic identifying the originating state,
the failure classification, what was and was not completed, and the corrective
action required. Partial, unvalidated, or fabricated deliverables are never
returned.

## Retry Strategy

Retries are bounded and deterministic so the machine cannot loop indefinitely.

- **Scope:** Retries apply only to states whose failure is potentially transient or
  self-correcting — `ACQUIRE` (source access) and the design/validation loop
  (`PLAN`, `DESIGN`, `SELF_REVIEW`, `VALIDATE`). Deterministic-logic and terminal
  states are not retried.
- **Bound:** Each retryable state carries a fixed maximum attempt count, `N`
  (default `N = 2` corrective re-entries beyond the first attempt). The bound is a
  configuration value, not a Knowledge rule.
- **Counter discipline:** Attempt counters are tracked per state in the context
  object and reset only on a successful exit from that state, preventing unrelated
  failures from sharing a budget.
- **Backoff:** For `ACQUIRE`, transient MCP/network failures use bounded backoff
  between attempts; corrective re-entries in the design/validation loop carry no
  delay because they perform new work rather than repeating an identical call.
- **Loop-prevention invariant:** A corrective re-entry must change the context
  (a completed correction or newly acquired input). A re-entry that would repeat
  with unchanged context is disallowed and is treated as retry exhaustion.
- **Escalation:** Exhausting the retry bound routes to the state's designated human
  checkpoint (CP-3 for the generation loop) or to `HALT`, per the Error Recovery
  Paths table. The machine never silently degrades output to avoid escalation.

## Human Review Checkpoints

Human checkpoints are explicit, named states where control is intentionally handed
to a person. They are the only points at which the machine solicits human input,
keeping human involvement predictable and auditable.

- **CP-1 — Intent Clarification (at `INTENT`):** Triggered when intent confidence is
  below threshold or the request is ambiguous. The requester confirms intent or
  scope; a confirmed response resumes at `ACQUIRE`, abandonment routes to `HALT`.
- **CP-2 — Requirement Clarification (at `REQ_VALIDATE`):** Triggered by blocking
  requirement deficiencies — incomplete requirements, missing primary acceptance
  criteria, or unresolved cross-source conflicts. The requester supplies missing
  detail or a conflict decision; resolution resumes at `ANALYZE`, abandonment routes
  to `HALT`.
- **CP-3 — Generation Escalation (at `SELF_REVIEW` / `VALIDATE` / `SUMMARY`):**
  Triggered when the design/validation loop cannot reach passing quality within the
  retry bound, or a success criterion cannot be met. A QA reviewer decides whether
  to accept documented limitations, provide guidance to resume, or stop; the outcome
  resumes at the responsible state or routes to `HALT`.
- **Mandatory final review (at `RETURN`):** Distinct from CP-1–CP-3, every
  successful deliverable is returned review-required. This is not a failure-triggered
  checkpoint but a standing quality posture: the human QA reviewer owns final
  acceptance, and the machine never marks a deliverable as accepted.

## Extensibility for Future Skills

The FSM is designed so future capabilities extend it by adding states, transitions,
and governing Knowledge documents — without rewriting existing states. The stable
extension points are the shared context object, the guarded-transition model, and
per-state delegation to a dedicated Knowledge document. New capabilities reuse the
existing `INIT`, `INTENT`, `ACQUIRE`, error-recovery, retry, and checkpoint
machinery.

- **Risk Assessment** — inserts a scoring state between `PLAN` and `DESIGN` that
  ranks requirements and scenarios by business impact and technical risk, enriching
  the context object so `DESIGN` can prioritize. It reuses the acquisition and
  validation states unchanged. Governed by a new `RISK_MODEL.md`; no existing
  state's contract changes.
- **Gap Analysis** — adds a comparison state that ingests an existing test suite
  (via `ACQUIRE`, extended with a new source type) and diffs it against the coverage
  plan from `PLAN`, emitting untested-behavior findings. It reuses acquisition,
  planning, and reporting machinery.

Each future state must declare the same nine-field contract, delegate its domain
logic to a dedicated Knowledge document, and resolve every failure to retry, a
human checkpoint, or `HALT` — preserving the determinism, modularity, and
separation of orchestration from knowledge that define this workflow.
