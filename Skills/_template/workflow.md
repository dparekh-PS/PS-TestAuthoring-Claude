---
name: <SkillName> Workflow
type: Deterministic State Machine Specification (domain states only)
component: <SkillName> Skill
version: 0.1
status: Draft
inherits: Skills/_base/workflow.base.md
companion: skill.md
---

# <SkillName> Workflow

This skill **inherits** the shared substrate in `Skills/_base/workflow.base.md`
(`INIT / INTENT / ACQUIRE / REQ_VALIDATE / SELF_REVIEW / VALIDATE / ASSEMBLE / SUMMARY /
RETURN / HALT`, the context object, retry strategy, error recovery, and human
checkpoints). It defines **only the domain states** below, inserted between
`REQ_VALIDATE` and `SELF_REVIEW`.

## Domain states

Declare each with the standard nine-field contract. Replace the examples.

> A skill may define **N** domain states — the count is not fixed at three. The three
> placeholders below (`<STATE_1>/<STATE_2>/<STATE_3>`) are a starting scaffold: add or remove
> domain states as the skill requires, keeping the nine-field contract on each and pointing the
> last one's **Next state** at `SELF_REVIEW`.

### `<STATE_1>` — <name> (Processing)
- **Purpose:** <what this state accomplishes>
- **Entry criteria:** `REQ_VALIDATE` passed (sources validated).
- **Inputs:** <context fields consumed>
- **Actions:** <what the state does; which Knowledge doc it consults>
- **Knowledge dependencies:** <e.g. RISK_MODEL.md>
- **Exit criteria:** <the contract that must hold to advance>
- **Failure handling:** <bounded retry / checkpoint / HALT — per base>
- **Output:** <context fields produced>
- **Next state:** `<STATE_2>`

### `<STATE_2>` — <name> (Processing)
- ... (same nine fields) ... **Next state:** `<STATE_3>`

### `<STATE_3>` — <name> (Processing)
- ... (same nine fields) ... **Next state:** `SELF_REVIEW` (returns to base)

## Output specification

<Point to the owning spec for this skill's deliverable (a Knowledge/ doc). ASSEMBLE builds
to it; VALIDATE enforces it; the machine validator confirms it before RETURN.>
