---
name: Base Skill Workflow
type: Shared Deterministic State Machine Substrate
component: Skills/_base
version: 1.0
status: Approved
classification: Internal — Professional Services QA
governs: Knowledge/ (single source of truth)
inherited-by: every skill under Skills/
---

# Base Skill Workflow (Shared Substrate)

This document owns the **reusable execution machinery** shared by every skill in the
project. A skill does **not** re-invent request handling, intent routing, source
acquisition, retries, error recovery, human checkpoints, validation gating, assembly,
or the context object — it **inherits** them from here and adds only its own
**domain states**.

This is the fix for the "monolithic single skill" problem: previously the only workflow
lived inside `TestCaseAuthoring` and a second skill would have had to copy the state
machine. Now the state machine lives here once; each skill is `base + its domain states +
one manifest entry` (see `Skills/SKILLS_REGISTRY.md`).

> Domain logic (QA methodology, authoring standards, validation rules, workbook schema)
> remains owned exclusively by `Knowledge/`. This file owns only *orchestration*.

---

## Shared states (inherited by all skills)

| # | State | ID | Kind | Owned by |
|---|-------|----|------|----------|
| 1 | Request Initialization | `INIT` | Entry | base |
| 2 | Intent Recognition | `INTENT` | Decision | base (routes via `USER_REQUEST_PATTERNS.md`) |
| 3 | Source Acquisition | `ACQUIRE` | I/O | base |
| 4 | Source Validation | `REQ_VALIDATE` | Gate | base |
| — | *(domain states)* | *(skill-defined)* | Processing | **the skill** |
| 8 | Self Review | `SELF_REVIEW` | Gate | base |
| 9 | Validation | `VALIDATE` | Gate | base (rules from `VALIDATION_ENGINE.md`) |
| 10 | Deliverable Assembly | `ASSEMBLE` | I/O | base (schema from the skill's output spec) |
| 11 | Summary | `SUMMARY` | Processing | base |
| 12 | Return Deliverables | `RETURN` | Terminal (success) | base |
| — | Halt | `HALT` | Terminal (safe stop) | base |

A skill inserts its **domain states** between `REQ_VALIDATE` and `SELF_REVIEW`. Example:
TestCaseAuthoring inserts `ANALYZE → PLAN → DESIGN`; a future RiskAssessment skill would
insert `IDENTIFY_RISKS → SCORE → PRIORITIZE`. The surrounding states are identical.

> **Domain-state count is not fixed at three.** The positions numbered 5/6/7 above are
> illustrative; a skill may define however many domain states it needs (one, three, seven).
> The shared states (1–4 and 8–12) are what is fixed, not the size of the domain middle.

## Source acquisition rules (`ACQUIRE` / `REQ_VALIDATE`)

Acquisition is where a whole run can be silently poisoned: if a source field is missed, every
downstream step (analysis, coverage, verdicts) operates on incomplete input while looking
complete. The rules split into a **source-agnostic core** that every skill obeys regardless of
where its input comes from, and **source adapters** that a skill opts into for a specific
backend (e.g. Atlassian). A non-Atlassian skill (e.g. DefectAnalysis) obeys the core and is not
bound to Jira/Confluence semantics.

### Source-agnostic core (mandatory for every skill)

- **Fetch ALL of the source, completely.** Retrieve the full source object — every field,
  section, attachment, and linked body it exposes — not a guessed subset. A scoped fetch that
  narrows to a presumed set of fields is prohibited whenever a complete fetch is available.
- **Distinguish "absent" from "not fetched".** `REQ_VALIDATE` must NOT conclude a source lacks
  a piece of content (e.g. acceptance criteria) until a full fetch has confirmed it. An empty
  result from a scoped fetch is treated as a **retrieval miss** (retry with a complete fetch),
  never as "the source has none". Concluding absence without a full fetch is a defect.
- **Record provenance.** Every acquired requirement/AC carries where it came from (issue field,
  Confluence section, doc heading, defect field, etc.) so later steps and reviewers can trace it.
- **Retrieval failure is not silent.** A 404/403/timeout on a source is logged (Open Point) and
  surfaced; it never degrades quietly into "nothing found".
- **Data handling.** Apply `DATA_HANDLING.md` to all acquired content: never copy real PII or
  secrets into the deliverable — represent personal data as a characteristic/placeholder. The
  validator enforces this at the gate (DP-01 email, DP-02 secret, both Blocking).

### Atlassian adapter (Jira / Confluence)

A skill whose source is Atlassian opts into this adapter in addition to the core above. These
rules exist because a real run missed the Jira Acceptance Criteria custom field by fetching a
guessed field name — the fix lives here, in the shared substrate, so it protects every skill
that uses this adapter.

- **Jira — never rely on a literal field name.** Acceptance criteria almost always live in a
  **custom field** (e.g. `customfield_15746` "Acceptance Criteria"), *not* the description and
  *not* a field literally named "acceptance criteria". Fetch with `fields:["*all"]` (or resolve
  the field id via the `names` map from `expand:names`) and read the description, the
  Acceptance Criteria custom field, labels, components, and comments. A scoped fetch by guessed
  field name is prohibited for the acceptance-criteria field. (This is the concrete realization
  of the core's "fetch ALL of the source" rule for Jira.)
- **Confluence — follow every remote/issue link** and fetch each linked page's body. If two
  links resolve to the same or duplicate content, record it as a low-severity source note
  rather than treating them as two independent sources.

## Shared contracts

**Context object (append-only).** Every state reads the accumulating context, appends its
output, and passes it forward; no state mutates a prior state's output. Base fields:
`request` (raw ask), `intent` (from `INTENT`), `sources` + `provenance` (from `ACQUIRE`),
`status_flags`, `retries`, and `deliverables`. Skills add their own namespaced fields.

**Interchange object (inter-skill handoff).** The in-memory context above is per-run; the
**normalized requirement representation** exchanged *between* skills has an owned machine schema
in `Skills/_base/interchange.schema.json` (`schema: interchange-1.0`). It defines the
source-agnostic shape — `source`, `requirements[]` (each with `acceptance_criteria[]` carrying
`id`/`text`/`anchor`/`inferred`/`business_rules`), `actors`, `workflows`, `open_points`,
`conflicts`. A producer skill (e.g. RequirementAnalysis) emits an object conforming to this
schema; a consumer skill (e.g. TestCaseAuthoring) reads it instead of re-parsing the raw source.
Producer→consumer handoff targets this schema so neither skill re-implements the other's parsing.

**Retry strategy (bounded).** Any I/O or gate failure may retry up to **N = 2** times with
the same inputs before routing to a human checkpoint or `HALT`. A retry counter per state
prevents loops; the invariant is *no state may be entered more than N+1 times per run*.

**Error recovery.** Every failure maps to exactly one of: (a) bounded retry, (b) a human
checkpoint, or (c) `HALT` with guidance. No path dead-ends; no path silently drops work.

**Human checkpoints.** `CP-1` (ambiguous intent, after `INTENT`) and `CP-2` (insufficient/
contradictory sources, after `REQ_VALIDATE`) pause for clarification rather than guessing —
consistent with the "never invent" guardrail in `SYSTEM_INSTRUCTIONS.md`.

**Determinism guarantee.** Given identical inputs and identical `Knowledge/` versions, the
FSM traverses an identical state path and yields an equivalent deliverable. (Note: this is
a design goal enforced by the gates + the deterministic output validator; the LLM steps are
made reproducible by pinning the governing documents, not by claiming the model is itself
deterministic.)

**Gating rule.** `VALIDATE` must pass every applicable rule in `VALIDATION_ENGINE.md`, and
`ASSEMBLE` must produce an artifact that passes the skill's machine validator (for
workbook-producing skills, `validate_workbook.py`) before `RETURN`. A deliverable that
fails its validator is never returned.

**Shared validator substrate.** The finding model, severity taxonomy, and CLI contract are
owned by `Skills/_base/validator_base.py`: a `Report` class (findings + FATAL/BLOCKING/WARNING
severity model), `print_report`, `run_cli(validate_fn, argv, doc)` (paths + `--json`, exit
codes 0/1/2), and `emit_rules_markdown(rules)`. A skill's machine validator imports `Report`
and `run_cli` from there and writes **only** its own checks plus its RULES catalog — it does not
re-invent findings, severities, or the CLI. This keeps every skill on one finding model and one
CLI contract. `validate_workbook.py` is the reference implementation (workbook-emitting) and
imports `Report`/`print_report`/`run_cli` from `_base`; a non-workbook skill implements its own
validator on the same substrate.

**Presentation step (ASSEMBLE).** After building the artifact, `ASSEMBLE` applies the
standard presentation defined by the skill's output spec, then validates. For
TestCaseAuthoring workbooks this means running `apply_merged_layout.py` to merge the
TC-level columns vertically per test case (EXCEL_SPECIFICATION §6.6) — presentation only,
same columns/IDs/schema.

**Coverage ledger (ASSEMBLE, REQUIRED for TestCaseAuthoring).** Alongside the workbook,
`ASSEMBLE` writes the coverage ledger sidecar `<workbook-name>.coverage.json` — the itemized,
source-anchored AC-to-test-case mapping captured **during extraction** (`ACQUIRE` /
`REQ_VALIDATE`), never reverse-engineered from the finished workbook. Each AC records its
source `anchor` and the `covered_by` test cases **on its own feature sheet**. The validator
checks it per feature (CV-08/09/10) and a **missing or malformed ledger is now BLOCKING
(CV-11)** — the ledger is a required deliverable, not optional. This is what turns the Master
Summary coverage % from a self-graded number into a verifiable claim — see VALIDATION_ENGINE.md
"Coverage Ledger". The ledger is a sidecar file, not a worksheet, so the workbook stays clean.

**ID registration (RETURN, required for workbook skills).** After a workbook passes and is
delivered, `RETURN` records its Test Case IDs in the persistent ID ledger by running
`validate_workbook.py --register <workbook.xlsx>`. This is what makes cross-workbook ID
uniqueness (NS-01) real rather than conventional — an unregistered delivery leaves its IDs
free to be silently reused by a later run. Registration is part of delivery, not an optional
manual step; a workbook is not considered "delivered" until its IDs are registered.

**Regeneration & versioning (shared behavior of `INIT` + `ASSEMBLE`).** A run for a source
that has already produced a deliverable is a *regeneration*, not a fresh run, and must be
handled deterministically:

- **`INIT` — detect prior deliverable.** Derive the canonical output name from the source
  (per the output spec's naming rule). If a file with that base name already exists, set
  `context.regeneration = true` and record the highest existing `_v{N}` suffix.
- **`ASSEMBLE` — never overwrite; version.** The first deliverable uses the base name
  (no suffix). Each regeneration writes a NEW file with the next `_v{N}` suffix
  (`…_v2`, `…_v3`), per `EXCEL_SPECIFICATION.md` §7.1 / §12.2. Prior versions are left
  intact so changes are auditable.
- **`SUMMARY` — reconcile against the prior version.** When `regeneration = true`, the
  summary must state what changed relative to the previous version: test cases
  added / removed / modified, coverage delta, and any newly resolved or newly opened
  Open Points. A regeneration that silently replaces a file with no diff is prohibited.
- **New source ≠ regeneration.** A different story/sprint produces a new base name with no
  suffix; only identical-source re-runs version.

## What a skill must supply

1. Its **domain states** (the processing middle) with the standard nine-field state
   contract (Purpose, Entry, Inputs, Actions, Knowledge Deps, Exit, Failure, Output, Next).
2. Its **output specification** (the schema `ASSEMBLE` builds and `VALIDATE` enforces).
3. One entry in `Skills/SKILLS_REGISTRY.md`.

Everything else is inherited from this document unchanged.
