---
name: <SkillName>
type: Skill Contract
version: 0.1
status: Draft
classification: Internal — Professional Services QA
inherits: Skills/_base/workflow.base.md
companion: workflow.md
---

# <SkillName> Skill

> Template. Copy `Skills/_template/` to `Skills/<SkillName>/` and fill every `<...>`.
> Do NOT restate base machinery, QA methodology, validation rules, or output schema —
> reference their owners.

## Responsibility

<One or two sentences: what this skill produces and for whom.>

## Supported inputs

<Jira story / Confluence page / Word doc / prior artifact / etc.>

## Deliverables

<The artifact(s) this skill returns, and the owning spec, e.g. "an .xlsx per
EXCEL_SPECIFICATION" or "a new Knowledge-governed report">.

## Execution

This skill runs the shared workflow in `Skills/_base/workflow.base.md`. It adds only the
domain states declared in its `workflow.md`; `INIT / INTENT / ACQUIRE / REQ_VALIDATE /
SELF_REVIEW / VALIDATE / ASSEMBLE / SUMMARY / RETURN / HALT`, retries, error recovery, and
human checkpoints are inherited unchanged.

## Knowledge dependencies

<List the Knowledge/ documents this skill consults (its methodology doc, VALIDATION_ENGINE,
and its output spec). Each is referenced, never duplicated.>

## Machine validator

<Path to the deterministic validator for this skill's deliverable, or "reuses
Skills/TestCaseAuthoring/validate_workbook.py" if it emits the standard workbook.>

If this skill does **not** emit the standard workbook, implement your own validator on the
shared substrate: import `Report` and `run_cli` from `Skills/_base/validator_base.py`, declare
your own `RULES` catalog, and write your own checks. Do not re-implement the finding model,
severity taxonomy, or CLI — they are inherited from `_base`. (`validate_workbook.py` is the
workbook-emitting reference implementation of exactly this pattern.)

If this skill hands requirement data to or from another skill, produce/consume the owned
interchange object `Skills/_base/interchange.schema.json` (`interchange-1.0`) rather than
re-parsing the raw source.

## Non-goals / boundaries

<What this skill explicitly does NOT do.>

## Registry

Add one row to `Skills/SKILLS_REGISTRY.md` and follow the "How to add a skill" checklist.
