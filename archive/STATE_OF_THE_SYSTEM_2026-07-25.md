# PS-TestAuthoring — State of the System (post-remediation re-audit)

> Date: 2026-07-25 (afternoon, after the Priority-1 remediation)
> Method: five parallel deep-readers covering every file; claims verified by *running* the validator, linter, and constructed fixtures — not by trusting the docs.
> This is the single living assessment. The three earlier score docs (`ARCHITECTURE_REVIEW_2026-07-23.md` = 5.2, morning `ENTERPRISE_ARCHITECTURE_REVIEW_2026-07-25.md` = 5.0, `REMEDIATION_SCORECARD.md` = 7.5) are point-in-time snapshots and should be archived — see the repo-hygiene note.

---

## Headline

**Overall: 6.0 / 10** — up from the board review's 5.0, and the gains are real: the RULES single-sourcing is airtight (verified byte-identical, lint-guarded), cross-workbook ID collision (NS-01) actually works, RTM is genuinely gone, and the standards consolidation relocated every rule without orphaning one. But the re-audit found two sobering patterns that cap the score:

1. **Several flagship mechanisms are built but not *exercised*.** The coverage ledger — the fix for self-graded coverage — produces **no sidecar on any of the three shipped workbooks**, and a missing ledger is only a *Warning*, so in practice coverage is still self-graded. ID registration works but is **manual and not wired into the workflow**, so a forgotten `--register` silently defeats NS-01. Data-handling rules are **honor-system** — nothing enforces them.
2. **A second wave of doc drift hit the execution layer.** When the substrate changed (v2.4→v2.5, ledger, namespacing), the top-level docs got updated but the **Skills execution docs did not**: `skill.md`, `workflow.md`, and `examples.md` still describe the v2.4 world (a "Coverage Summary" artifact, "Requirement Traceability" checks) and never mention the ledger, `--register`, namespacing, or `_vN` versioning. Following the skill docs alone now yields an out-of-contract run.

The honest read: **the engine got stronger, the top-level story got consistent, but the enforcement wiring and the skill-level docs lagged behind the mechanisms we built.**

## Scores

| Area | Now | Board (07-25 AM) | Note |
|------|:---:|:---:|------|
| Architecture | 6.0 | 6 | Ownership/precedence sound; ARCHITECTURE.md still has a phantom "generate traceability/coverage sheet" pipeline step + a non-existent interactive-review UI. |
| Knowledge Base | 6.0 | 5 | Consolidation real, no orphaned rules; capabilities honestly labeled. Docked for Expected-Result dual-ownership + `(wording TBC)` triplication + two live schema/layout contradictions. |
| Skills | 4.0 | 5 | `_base` is current and strong, but skill.md/workflow.md/examples.md drifted to v2.4; workflow.md re-copies `_base` and its ACQUIRE lost the anti-bug hardening. |
| Validation | 5.0 | 4 | Structural/ID gating strong + single-sourced; but the coverage ledger isn't produced (still self-graded in practice), is cross-sheet bypassable when present, and 5 categories remain doc-only. |
| AI Reasoning | 5.0 | 5 | Strong doctrine, but a worked "Good Example" still fabricates an "Email Notification Framework"; 4-precondition floor invites padding. |
| Maintainability | 5.0 | 4 | RULES single-sourcing is exemplary; undercut by schema version triplicated in 3 code files and a fresh crop of stale docs. |
| Scalability | 5.0 | 3 | Namespacing model added; but `apply_merged_layout.py` crashes on re-run, id_ledger is a full-file rewrite, no shared validator interface. |
| Reusability | 4.0 | 5 | `_base` + template real, but only extends to workbook-clones: Jira-coupled ACQUIRE, 3-slot state assumption, no interchange schema, no non-workbook validator interface. |
| Documentation | 5.0 | 5 | Entry points reconciled; but three conflicting score docs at root, README/Flow file trees lag the real repo. |
| Enterprise Readiness | 5.0 | 4 | Namespacing + coverage machinery exist; but registration + ledger are manual/unexercised and data governance is unenforced. |
| **Overall** | **6.0** | **5.0** | Real, verifiable gains; capped by unexercised flagship mechanisms + skill-layer drift. |

---

## The single most important finding

**Coverage is still self-graded in practice.** `validate_workbook.py` genuinely implements CV-08/09/10 against a `<workbook>.coverage.json` sidecar — verified working on a constructed fixture. But:

- **No sidecar exists** next to `TC-Epic04…_v4`, `TC-SAMP-110…_v6`, or `TC-SAMP-166…_v6`.
- A missing ledger is only **CV-11 (Warning)** — it does not block. So CV-08/09/10 never run on any real deliverable, and the Master Summary's "100%" is unchecked — exactly the defect the ledger was meant to close. VALIDATION_ENGINE.md even claims "a compliant run is never in this state," yet every real run *is*.
- When a ledger *is* present, two gaps remain: `covered_by` is checked against the **global** ID set, not the AC's own feature (a constructed cross-sheet mismapping **passed with zero findings**), and CV-09 reconciles **totals only**, so per-feature coverage integrity is unverified. The `anchor` check only rejects an empty string.

The mechanism is right; it just isn't wired to run or produced by any run. Fixing this is the highest-value single change available.

---

## File-by-file: is what's described actually used? (the direct answer to your question)

Status key: **OK** = accurate & used · **Stale** = lags the real tree · **Drift** = contradicts code/owner · **Aspirational** = describes something that doesn't run.

| File | Status | The gap (what's described vs what's real) |
|------|:------:|-------------------------------------------|
| `Knowledge/MASTER_CONTEXT.md` | Stale | Own version header frozen at 1.0/07-22 despite v2.4/v2.5 edits; Appendix A mis-states 3 doc versions; §5.2 cites Master-Summary "columns G–H" (only A–F exist); trailing line still says "authoritative entry point" (contradicts its reconciled header). |
| `Knowledge/ARCHITECTURE.md` | Drift | Honesty banner is good, but Stage 6 still says "generate traceability sheet / coverage summary" (removed in v2.4); §5/§9 present a non-existent interactive review UI as architecture. |
| `Knowledge/AI_CAPABILITIES.md` | OK | 8 capabilities honestly labeled against the real skill tree. Minor: "matches SKILLS_REGISTRY exactly" isn't literally true; maturity vocabulary quoted as 3 levels elsewhere vs 4 here. |
| `Knowledge/USER_REQUEST_PATTERNS.md` | Drift | Still uses the retired "Future" label its own owner (AI_CAPABILITIES §7) banned (INT-07/08). Intents INT-02/03/04 route to unbuilt skills with no "capability-not-built → HALT" guard. |
| `Knowledge/DATA_HANDLING.md` | Aspirational | Accurate policy, but honor-system: zero PII/secret enforcement in the validator, and no `Skills/` workflow even references it. §7 "blocks delivery" is unbacked. |
| `Knowledge/README.md` | OK | Exemplary map; only misses naming the registry/ledger/coverage-sidecar artifacts. |
| `Knowledge/SYSTEM_INSTRUCTIONS.md` | Drift | §3.12 pins `schema:2.4` and "(v2.4)"; a run following it literally would stamp 2.4 and be **rejected by the validator (SV-02)**. Owner is 2.5. |
| `Knowledge/QA_METHODOLOGY.md` | Drift | Relocations real, but §8.6 still co-owns the Expected-Result standard with TCG §6 (both say "single owner"); prohibited-phrase blacklist restated 3–4×. |
| `Knowledge/TEST_CASE_GENERATION.md` | Drift | Mechanics solid, but §4A "Good Example" fabricates system components ("Email Notification Framework is enabled") — a worked example teaching invention. 4-precondition floor lacks a "don't pad" guard. |
| `Knowledge/EXAMPLES.md` | Drift | §13 teaches the abandoned forward-fill/"merges prohibited" layout — false against the current merged-cell owner. One TC still uses `<configured workflow>` where a characteristic belongs. |
| `Knowledge/EXCEL_SPECIFICATION.md` | Drift | Columns/schema/ID match code. But Appendix B still claims feature sheets have "no merged cells"; §15.2 cites deleted row-grouping; §14.2 cites non-existent CV-02/CV-03. |
| `Knowledge/VALIDATION_ENGINE.md` | OK/Aspirational | RULES block byte-matches code (excellent). But 5 whole categories (duplicate, scenario balance, environment-independence, risk, extraction fidelity) are doc-only, unenforced. |
| `Skills/TestCaseAuthoring/validate_workbook.py` | OK | 32 codes, all real and reachable; RULES consistency clean; NS-01 proven. Bugs: cross-sheet ledger bypass, totals-only CV-09, basename-only workbook identity, no ledger atomicity. |
| `Skills/TestCaseAuthoring/apply_merged_layout.py` | Drift/bug | **Crashes on re-run** (`MergedCell … read-only`) — a regeneration hazard. Also hardcodes `schema:2.5` (a presentation script owning the schema stamp); row-height heuristic is fragile at scale. |
| `Skills/lint_docs.py` | OK | Strong where it acts; doesn't parse the JSON files, doesn't check schema-version coherence across the 3 code files, doesn't verify a delivered workbook has a sidecar. |
| `Skills/TestCaseAuthoring/project_registry.json` | OK | Consulted (NS-02 proven). Only 2 projects seeded; new keys warn until onboarded. |
| `Skills/TestCaseAuthoring/id_ledger.json` | OK | Consulted (NS-01 proven), 224 IDs. Full-file rewrite per register; won't scale to tens of thousands without a real store. |
| `Skills/_base/workflow.base.md` | OK | The one current, authoritative skill doc. But Jira-coupled ACQUIRE + 3-slot state assumption limit reuse; interchange object is prose-only. |
| `Skills/_template/*` | Stale | Hardcodes exactly 3 states; no path for a non-workbook skill; no mention of ledger/register. |
| `Skills/TestCaseAuthoring/skill.md` | Stale | Still lists a "Coverage Summary" deliverable + "traceability matrix" coverage gate; never mentions the ledger/register/namespacing/versioning; RiskAssessment listed twice; version header incoherent. |
| `Skills/TestCaseAuthoring/workflow.md` | Drift | Re-copies `_base` and the copy drifted: ACQUIRE lost the Jira custom-field / retrieval-miss hardening; ASSEMBLE omits the ledger + `_vN` versioning; duplicate/contradictory RiskAssessment placement. |
| `Skills/TestCaseAuthoring/examples.md` | Stale | Advertises "Coverage Summary" artifact + "Requirement Traceability" checks (both retired); pinned to v2.4. |
| `Skills/README.md` | Stale | Validator paragraph says coverage checks "retired in v2.4" — v2.5 restored them (CV-06/07) and added the ledger + NS checks it never mentions. |
| `Skills/SKILLS_REGISTRY.md` | Stale | Declares EXCEL_SPEC "v2.1" (actual v2.5); points TraceabilityAnalysis at deleted "§4.7"; omits validator capabilities + JSON artifacts; disagrees with USER_REQUEST_PATTERNS on RequirementReview status. |
| `README.md` (root) | Stale | "only executable code is validator + linter" — misses `apply_merged_layout.py`; tree omits the 2 JSON files; anchored to v2.4. |
| `PROJECT_INSTRUCTIONS.md` | OK/heavy | Reconciliation landed + DATA_HANDLING added, but ~130 of 177 lines still duplicate MASTER_CONTEXT's catalog/sequence/principles despite calling itself a "thin router." |
| `PS-TestAuthoring_Flow_and_Files.md` | Stale | Best single map, but lists SAMP samples as `_v4` (real: `_v6`), omits the Epic04 workbook and the newest review. |
| `REMEDIATION_SCORECARD.md` | Drift | Presents "7.5" as the live score and makes a now-false RTM-coverage claim. Archive it. |
| `ARCHITECTURE_REVIEW_2026-07-23.md` | Snapshot | Valid historical baseline (5.2); most findings remediated. Archive. |
| `ENTERPRISE_ARCHITECTURE_REVIEW_2026-07-25.md` (AM) | Snapshot | Sharp, but already partly stale (namespacing/ledger/entry-points since addressed). Superseded by this doc. |

---

## Prioritized fix list

### Priority 1 — makes a "built" mechanism actually work / prevents a broken run
1. **Make the coverage ledger real:** wire ledger generation into ASSEMBLE (produce `<wb>.coverage.json` from the extraction data every run), generate ledgers for the 3 shipped workbooks, and make a *missing* ledger blocking (CV-11 → Blocking) once generation is in place. Tighten CV-08 to check `covered_by` against the AC's own feature sheet, and CV-09 to reconcile per-feature, not totals-only.
2. **Fix `apply_merged_layout.py` re-run crash** (unmerge before re-merge) — regeneration currently hard-fails.
3. **Update the Skills execution docs to v2.5:** `skill.md`, `workflow.md`, `examples.md` — replace "Coverage Summary/Requirement Traceability" with the real outputs (workbook + `.coverage.json`), add the ledger/`--register`/namespacing/`_vN` steps, collapse workflow.md's duplicated `_base` states to references, and restore the ACQUIRE Jira-hardening the copy lost.
4. **Remove the `schema:2.4` pin in SYSTEM_INSTRUCTIONS §3.12** (defer to EXCEL_SPEC) — a literal follow would fail the validator.
5. **Wire `--register` into ASSEMBLE/RETURN** so ID registration isn't a forgettable manual step.

### Priority 2 — governance & drift
6. Single-source the schema version (one constant; `apply_merged_layout` + `lint_docs` + EXCEL_SPEC header derive from it; lint the equality).
7. Add a PII/secret scan (new DP-01/02 codes in the RULES catalog) to make DATA_HANDLING enforceable, and reference it from the workflow.
8. Fix the EXCEL_SPEC contradictions (Appendix B "no merged cells", §15.2 row-grouping, §14.2 CV-02/03) and the ARCHITECTURE Stage 6 / §9 phantom steps.
9. Reconcile SKILLS_REGISTRY (v2.5, drop §4.7, add validator capabilities/JSON artifacts) and the RequirementReview status vs USER_REQUEST_PATTERNS; swap "Future"→"Planned".
10. Bump MASTER_CONTEXT's header + Appendix A (and lint the registry against real file headers); refresh root README + Flow file trees; archive the three old score docs.

### Priority 3 — depth & reach
11. Resolve Expected-Result dual-ownership (QA §8.6 → philosophy pointer only); de-triplicate `(wording TBC)`.
12. Rewrite the TCG §4A "Good Example" to stop fabricating system components; add a "don't pad preconditions" guard.
13. Extensibility groundwork: a shared validator interface for non-workbook skills, a JSON-schema interchange object, and a source-agnostic ACQUIRE core + Atlassian adapter.
14. Add the cheap semantic validators (near-duplicate detection, environment-independence regex) that are still doc-only.

---

## Bottom line

The remediation delivered genuine, verifiable structural wins — but it also revealed that **building a mechanism is not the same as wiring it in**. The coverage ledger, ID registration, and data-handling policy all exist in code/policy and none is actually enforced on a real run; and the skill-execution docs quietly fell a version behind the substrate. Closing Priority 1 — making the ledger produce and block, fixing the re-run crash, and bringing the skill docs to v2.5 — is what turns this from "a strong engine with a good story" into "a system that does what it says." That would credibly move the overall score to ~7.5.
