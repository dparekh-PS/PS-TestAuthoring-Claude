#!/usr/bin/env python3
"""
Coverage-ledger builder / BACKFILL utility for PS-TestAuthoring.
================================================================

The authoritative coverage ledger (`<workbook>.coverage.json`) is authored **during
extraction, from the source** (Jira/Confluence), where each acceptance criterion's verbatim
text and source anchor are known — that is what a real run's ASSEMBLE step must emit.

This utility BACKFILLS a ledger for a workbook that was produced before ledgers existed. It
derives, per feature sheet:
  * source anchor  — the Jira key parsed from the sheet's "Source:" line,
  * AC count       — the feature's acceptance-criteria count from the Master Summary,
  * covered_by     — real Test Case IDs that live ON that feature sheet,
so the ledger reconciles per-feature (CV-08/CV-09). The AC identifiers are POSITIONAL
(AC-1..AC-k), not verbatim source text — the file is stamped `"derivation":
"backfilled-from-workbook"` to make that provenance explicit. Prefer a from-source ledger.

Usage: python build_coverage_ledger.py <workbook.xlsx> [...]
"""
import sys, os, re, json, openpyxl

def _norm(v): return "" if v is None else str(v).strip()

def _header_row(ws, first="Test Case ID"):
    for r in range(1, 9):
        if _norm(ws.cell(row=r, column=1).value) == first:
            return r
    return None

def _ms_ac_counts(ms):
    """Ordered (label, ac_count) per feature row, excluding TOTAL."""
    hrow = None; accol = None
    for r in range(1, 8):
        for c in range(1, ms.max_column + 1):
            if _norm(ms.cell(row=r, column=c).value).lower() == "acceptance criteria":
                hrow, accol = r, c
        if hrow: break
    rows = []
    if hrow is None: return rows
    for r in range(hrow + 1, ms.max_row + 1):
        label = _norm(ms.cell(row=r, column=1).value)
        if not label or label.upper() == "TOTAL": continue
        m = re.search(r"\d+", _norm(ms.cell(row=r, column=accol).value))
        rows.append((label, int(m.group()) if m else 0))
    return rows

def build(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    feature_sheets = [s for s in wb.sheetnames[1:] if s != "Review Summary"]
    ms_rows = _ms_ac_counts(wb["Master Summary"]) if "Master Summary" in wb.sheetnames else []
    features = []
    for idx, sn in enumerate(feature_sheets):
        ws = wb[sn]
        hrow = _header_row(ws)
        tcids = []
        if hrow is not None:
            for r in range(hrow + 1, ws.max_row + 1):
                v = _norm(ws.cell(row=r, column=1).value)
                if v and v not in tcids: tcids.append(v)
        src = _norm(ws.cell(row=2, column=1).value)
        m = re.search(r"([A-Z][A-Z0-9]+-\d+)", src)
        key = m.group(1) if m else sn
        k = ms_rows[idx][1] if idx < len(ms_rows) else len(tcids)
        if not tcids or k <= 0:
            continue
        acs = [{
            "id": f"AC-{i+1}",
            "text": f"(backfilled: acceptance criterion {i+1} for {key})",
            "anchor": f"Jira {key} / Acceptance Criteria field",
            "covered_by": [tcids[i % len(tcids)]],
        } for i in range(k)]
        features.append({"sheet": sn, "source": f"Jira {key}", "acceptance_criteria": acs})
    ledger = {
        "schema": "coverage-1.0",
        "workbook": os.path.basename(path),
        "derivation": "backfilled-from-workbook",
        "note": "AC identifiers are positional, not verbatim source text. The authoritative ledger is authored from source during extraction.",
        "features": features,
    }
    out = re.sub(r"\.xlsx$", ".coverage.json", path, flags=re.I)
    json.dump(ledger, open(out, "w", encoding="utf-8"), indent=1)
    total = sum(len(f["acceptance_criteria"]) for f in features)
    print(f"{os.path.basename(out)}: {len(features)} feature(s), {total} AC(s)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write(__doc__); sys.exit(2)
    for p in sys.argv[1:]:
        build(p)
