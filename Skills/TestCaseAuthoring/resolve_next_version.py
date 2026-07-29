#!/usr/bin/env python3
"""
Resolve the next version-safe base filename for a project's daily workbook, by
listing the project's OneDrive folder (metadata only -- no content read-back
needed, so this works within this environment's egress policy) and checking
for an existing file with the same base name.

This never guesses: it lists the real folder contents via Microsoft Graph
(same drive_id/item_id resolution as upload_to_onedrive.py, from
onedrive_folders.json) and picks the next free `_v{N}` suffix deterministically.

Usage:
    python resolve_next_version.py <ProjectKey> <base_name_without_ext>
    e.g. python resolve_next_version.py SAMP TC-SAMP_20260729

Prints the resolved base name (without extension) to stdout, e.g.:
    TC-SAMP_20260729          (no prior file today -> first generation)
    TC-SAMP_20260729_v2       (one prior file today -> next version)
    TC-SAMP_20260729_v3       (two prior files today -> next version)

Exit codes: 0 = resolved (prints result), 2 = usage / project not registered / Graph error.
"""
import sys, os, re, json, requests

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDERS_FILE = os.path.join(HERE, "onedrive_folders.json")


def get_token():
    tenant = os.environ["AZURE_TENANT_ID"]
    client_id = os.environ["AZURE_CLIENT_ID"]
    client_secret = os.environ["AZURE_CLIENT_SECRET"]
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }
    r = requests.post(url, data=data, timeout=20)
    r.raise_for_status()
    return r.json()["access_token"]


def load_folder(project_key):
    if not os.path.exists(FOLDERS_FILE):
        sys.stderr.write(f"No {FOLDERS_FILE} found -- register the project's OneDrive folder first.\n")
        sys.exit(2)
    with open(FOLDERS_FILE) as f:
        folders = json.load(f)
    entry = folders.get("projects", {}).get(project_key)
    if not entry:
        sys.stderr.write(f"Project {project_key!r} is not registered in {FOLDERS_FILE}.\n")
        sys.exit(2)
    return entry


def list_children(token, drive_id, item_id):
    """Paginate through all children of the destination folder."""
    names = []
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/children?$select=name&$top=200"
    while url:
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
        r.raise_for_status()
        j = r.json()
        names.extend(it["name"] for it in j.get("value", []))
        url = j.get("@odata.nextLink")
    return names


def resolve(project_key, base_name):
    folder = load_folder(project_key)
    token = get_token()
    names = list_children(token, folder["drive_id"], folder["item_id"])

    # Match exactly "<base_name>.xlsx" or "<base_name>_v<N>.xlsx" -- anchored, so a
    # per-story-named file (e.g. TC-SAMP-125_...) never false-matches a project-day
    # base name (e.g. TC-SAMP_...).
    pat = re.compile(r"^" + re.escape(base_name) + r"(?:_v(\d+))?\.xlsx$")
    highest = None  # None = base name itself not seen yet; 1 = base name seen, no _vN yet
    for n in names:
        m = pat.match(n)
        if not m:
            continue
        if m.group(1) is None:
            highest = max(highest or 1, 1)
        else:
            highest = max(highest or 1, int(m.group(1)))

    if highest is None:
        return base_name                      # no file for this project+day yet -- first generation
    return f"{base_name}_v{highest + 1}"       # bump past the highest version seen


def main():
    if len(sys.argv) != 3:
        sys.stderr.write(__doc__)
        sys.exit(2)
    project_key, base_name = sys.argv[1:3]
    print(resolve(project_key, base_name))


if __name__ == "__main__":
    main()
