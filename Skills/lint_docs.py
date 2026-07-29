#!/usr/bin/env python3
"""
Documentation linter for PS-TestAuthoring.

Guards the invariants established during the architecture remediation so they do not
silently regress. Run from the project root:

    python Skills/lint_docs.py

Exit codes:
    0 = clean (no errors)
    1 = one or more ERRORS
    2 = usage error

ERRORS fail the check; WARNINGS are advisory. Intended to run in CI on every change to
Knowledge/ or Skills/.
"""

import sys, re, glob, os

ROOT = os.getcwd()
KNOWLEDGE = glob.glob("Knowledge/*.md")
SKILLS = glob.glob("Skills/**/*.md", recursive=True)
ALL_MD = KNOWLEDGE + SKILLS

errors, warnings = [], []

def err(f, msg): errors.append((f, msg))
def warn(f, msg): warnings.append((f, msg))

def read(f):
    with open(f, encoding="utf-8") as fh:
        return fh.read()

# Load the deterministic validator once — it is the single source of truth for both the
# schema version and the rule catalog, cross-checked against the docs/code below.
def _load_validator():
    import importlib.util
    p = "Skills/TestCaseAuthoring/validate_workbook.py"
    if not os.path.exists(p):
        return None
    try:
        spec = importlib.util.spec_from_file_location("vw_lint", p)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        return m
    except BaseException:
        return None
VW = _load_validator()
CURRENT_SCHEMA = VW.SCHEMA_VERSION if VW else "2.5"

# ---- CHECK 1: encoding corruption (mojibake) --------------------------------
MOJIBAKE = ["âœ", "â†", "â€", "Ã¢", "Ã©", "â\x80"]
for f in ALL_MD:
    s = read(f)
    hits = [m for m in MOJIBAKE if m in s]
    if hits:
        err(f, f"character-encoding corruption (mojibake) present: {hits}")

# ---- CHECK 2: retired vocabulary --------------------------------------------
# Maturity vocabulary is Planned/Pilot/Production; "Production Ready" is retired.
for f in ALL_MD:
    s = read(f)
    # "Pilot" is a VALID maturity for a built-but-not-Production skill; only truly retired
    # vocabulary is flagged ("Production Ready" -> "Production"; "Future" -> "Planned").
    for term, repl in [("Production Ready", "Production"),
                       ("Maturity Level:** Future", "Planned"),
                       ("Maturity Level: Future", "Planned")]:
        if term in s:
            warn(f, f"retired term {term!r} present (use {repl!r})")

# ---- CHECK 3: schema-version single-source coherence ------------------------
# The schema version is owned by validate_workbook.py (SCHEMA_VERSION). Everything else must
# agree with it; nothing else may hard-code a different literal.
spec = "Knowledge/EXCEL_SPECIFICATION.md"
if os.path.exists(spec):
    s = read(spec)
    # the spec's mandatory stamp must match the validator's current schema
    mandated = sorted(set(re.findall(r"must (?:contain|embed) `schema:([0-9]+\.[0-9]+)", s)))
    for m in mandated:
        if m != CURRENT_SCHEMA:
            err(spec, f"mandates schema:{m} but the validator's SCHEMA_VERSION is {CURRENT_SCHEMA} — single-source drift")
# no other Python file may hard-code a schema:X.Y literal (they must read SCHEMA_VERSION)
for pf in ["Skills/TestCaseAuthoring/apply_merged_layout.py"]:
    if os.path.exists(pf):
        for lit in sorted(set(re.findall(r"schema:([0-9]+\.[0-9]+)", read(pf)))):
            err(pf, f"hard-codes a schema:{lit} literal — read SCHEMA_VERSION from validate_workbook.py instead")

# ---- CHECK 4: bare (non-global) Test Case IDs -------------------------------
# Global format is {Key}-{Story}-TC-NNN. A bare TC-NNN suggests a stale example.
BARE_TC = re.compile(r"(?<![A-Z0-9-])TC-\d{3,}\b")
ALLOW_BARE = {"Knowledge/EXCEL_SPECIFICATION.md"}  # spec explains the format itself
for f in KNOWLEDGE + [x for x in SKILLS if x.endswith(".md")]:
    if f in ALLOW_BARE:
        continue
    s = read(f)
    n = len(BARE_TC.findall(s))
    if n:
        warn(f, f"{n} bare 'TC-NNN' id(s) — global format is {{Key}}-{{Story}}-TC-NNN")

# ---- CHECK 5: suspect section cross-references into VALIDATION_ENGINE --------
# VALIDATION_ENGINE.md uses named headers, not numbered sections, so 'VALIDATION_ENGINE.md §N' is broken.
SEC_REF = re.compile(r"VALIDATION_ENGINE\.md\s*§\s*\d")
for f in ALL_MD:
    s = read(f)
    if SEC_REF.search(s):
        err(f, "cross-reference to a numbered VALIDATION_ENGINE.md section (it has none — use a named header)")

# ---- CHECK 6: single-source ownership (no duplicated workbook column table) -
# Only EXCEL_SPECIFICATION and EXAMPLES may render the full feature-column header row.
COLROW = re.compile(r"Test Case ID\s*\|\s*Requirement Title\s*\|\s*Test Case Title")
OWNERS = {"Knowledge/EXCEL_SPECIFICATION.md", "Knowledge/EXAMPLES.md"}
for f in ALL_MD:
    if f in OWNERS:
        continue
    if COLROW.search(read(f)):
        warn(f, "renders the full feature-column header — schema is owned by EXCEL_SPECIFICATION.md; reference it instead")

# ---- CHECK 7: (removed) merged-cell prohibition — merged layout is standard as of v2.3 ----

# ---- CHECK 8: validation rule catalog is single-sourced from the validator ---
# The machine-enforced rule table in VALIDATION_ENGINE.md is GENERATED from
# validate_workbook.py's RULES catalog. Fail if the doc drifts from the code, if the catalog
# is internally inconsistent, or if any OTHER doc restates the code/severity table.
if VW is None:
    warn("Skills/lint_docs.py", "could not load validate_workbook.py (openpyxl missing?) — RULES single-source check skipped")
else:
    try:
        # 8a: RULES catalog must match the codes the validator actually emits
        for p in VW.rules_consistency_errors():
            err("Skills/TestCaseAuthoring/validate_workbook.py", p)

        # 8b: VALIDATION_ENGINE.md generated block must equal the validator's output
        _ve = "Knowledge/VALIDATION_ENGINE.md"
        if os.path.exists(_ve):
            _s = read(_ve)
            _m = re.search(re.escape(VW.RULES_BEGIN) + r"(.*?)" + re.escape(VW.RULES_END), _s, re.S)
            if not _m:
                err(_ve, "missing generated RULES block — run: python Skills/TestCaseAuthoring/validate_workbook.py --rules")
            elif (VW.RULES_BEGIN + _m.group(1) + VW.RULES_END).strip() != VW.emit_rules_block().strip():
                err(_ve, "machine-enforced RULES table is out of sync with validate_workbook.py — regenerate via --rules")

        # 8c: no other doc may render the machine-enforced code+severity table
        _CODEROW = re.compile(r"\|\s*(?:WV|DV|CV|ER|SV|NS|DP)-\d{2}\s*\|\s*(?:FATAL|BLOCKING|WARNING|Fatal|Blocking|Warning)\s*\|")
        for f in ALL_MD:
            if f == _ve:
                continue
            if _CODEROW.search(read(f)):
                err(f, "restates the machine-enforced rule code/severity table — owned by validate_workbook.py, rendered only in VALIDATION_ENGINE.md")
    except Exception as e:
        err("Skills/lint_docs.py", f"RULES single-source check failed: {e}")

# ---- CHECK 9: MASTER_CONTEXT registry versions vs each doc's real header ------
# Appendix A of MASTER_CONTEXT lists a version per document. Warn if a registry row's version
# disagrees with that document's own header — the drift the registry exists to prevent.
_mc = "Knowledge/MASTER_CONTEXT.md"
if os.path.exists(_mc):
    _mctext = read(_mc)
    _mclines = [ln for ln in _mctext.splitlines() if "|" in ln]  # registry table rows
    for f in KNOWLEDGE:
        base = os.path.basename(f)
        hm = re.search(r"^>?\s*Version:\s*([0-9]+\.[0-9]+)", read(f), re.M)
        if not hm:
            continue
        ver = hm.group(1)
        for ln in _mclines:
            if base in ln:
                found = re.findall(r"(?<![§.\d])([0-9]+\.[0-9]+)(?!\d)", ln)
                if found and ver not in found:
                    warn(_mc, f"Appendix A lists {base} as {found} but its header is {ver}")
                break

# ---- report -----------------------------------------------------------------
def report():
    print(f"doc-lint: {len(ALL_MD)} files scanned  |  {len(errors)} error(s), {len(warnings)} warning(s)")
    for f, m in errors:
        print(f"  [ERROR]   {f}: {m}")
    for f, m in warnings:
        print(f"  [WARN]    {f}: {m}")
    if not errors and not warnings:
        print("  clean.")

report()
sys.exit(1 if errors else 0)
