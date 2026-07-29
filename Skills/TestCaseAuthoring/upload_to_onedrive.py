#!/usr/bin/env python3
"""
Deliver a generated workbook (and its coverage-ledger sidecar) to the project's
OneDrive folder via the Microsoft Graph API, using app-only (client credentials)
auth against AZURE_TENANT_ID / AZURE_CLIENT_ID / AZURE_CLIENT_SECRET.
The destination drive_id/item_id for each ProjectKey is read from
onedrive_folders.json beside this script -- it is resolved ONCE via a real
Graph lookup (see that file's "resolved_via" note) and never guessed. If a
ProjectKey has no entry, this script refuses to guess a destination and exits
with an error asking for the folder to be registered first.
Known limitation (environment-specific): this session's egress policy allows
direct HTTPS to graph.microsoft.com and login.microsoftonline.com, but blocks
the tenant's *.sharepoint.com host. Simple small-file uploads
(PUT .../items/{id}:/{name}:/content) are served entirely by the Graph API
front door and work fine. Reading file *content* back
(GET .../content) 302-redirects to a pre-authenticated *.sharepoint.com
download URL, which this proxy blocks -- so this script cannot
verify-by-reading-content-back in that kind of restricted environment.
Metadata reads (listing children, item properties) stay on graph.microsoft.com
and work -- so after each upload this script does an independent metadata GET
(verify_one) and confirms the item exists with the expected size before
exiting 0. A workbook is only "delivered" if this script prints "uploaded and
verified present" for both files; the caller must treat any other outcome
(non-zero exit, exception) exactly like a failed upload -- do not register IDs
or apply the tc-generated label. This exists because a prior run's workbook
was found registered in id_ledger.json and labeled with no corresponding file
ever present in OneDrive: this verification step, plus not skipping it in the
caller, is the fix.
Usage:
    python upload_to_onedrive.py <ProjectKey> <workbook.xlsx> <coverage.json>
"""
import sys, os, json, requests
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
        sys.stderr.write(
            f"No {FOLDERS_FILE} found. Resolve the project's OneDrive folder via a "
            f"real Graph lookup first (list drives/children) and register it there -- "
            f"never guess a drive_id/item_id.\n"
        )
        sys.exit(2)
    with open(FOLDERS_FILE) as f:
        folders = json.load(f)
    entry = folders.get("projects", {}).get(project_key)
    if not entry:
        sys.stderr.write(
            f"Project '{project_key}' is not registered in {FOLDERS_FILE}. "
            f"Resolve its OneDrive folder via a real Graph lookup and add it -- "
            f"never guess a drive_id/item_id.\n"
        )
        sys.exit(2)
    return entry
CONTENT_TYPES = {
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".json": "application/json",
}
def upload_one(token, drive_id, item_id, local_path):
    name = os.path.basename(local_path)
    ext = os.path.splitext(name)[1].lower()
    content_type = CONTENT_TYPES.get(ext, "application/octet-stream")
    with open(local_path, "rb") as f:
        data = f.read()
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}:/{name}:/content"
    r = requests.put(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": content_type},
        data=data,
        timeout=120,
    )
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Upload failed for {name}: {r.status_code} {r.text[:500]}")
    j = r.json()
    return {"name": name, "id": j.get("id"), "size": j.get("size"), "webUrl": j.get("webUrl"), "local_size": len(data)}
def verify_one(token, drive_id, item_id, expected):
    """Re-fetch the uploaded item's metadata straight from Graph (independent of the
    PUT response) and confirm it really exists with the expected size. A workbook is
    NOT considered delivered — and must not be registered or labeled — until this
    passes, because the PUT response alone has been observed to go stale (e.g. a
    later out-of-band deletion) between upload and registration."""
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}:/{expected['name']}:"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(
            f"Delivery verification failed for {expected['name']}: "
            f"GET returned {r.status_code} {r.text[:300]} — item is not confirmed present in OneDrive."
        )
    j = r.json()
    if j.get("size") != expected["local_size"]:
        raise RuntimeError(
            f"Delivery verification failed for {expected['name']}: "
            f"remote size {j.get('size')} != local size {expected['local_size']}."
        )
    return True
def main():
    if len(sys.argv) != 4:
        sys.stderr.write(__doc__)
        sys.exit(2)
    project_key, workbook_path, coverage_path = sys.argv[1:4]
    for p in (workbook_path, coverage_path):
        if not os.path.exists(p):
            sys.stderr.write(f"File not found: {p}\n")
            sys.exit(2)
    folder = load_folder(project_key)
    token = get_token()
    results = []
    for p in (workbook_path, coverage_path):
        results.append(upload_one(token, folder["drive_id"], folder["item_id"], p))
    for res in results:
        verify_one(token, folder["drive_id"], folder["item_id"], res)
    for res in results:
        print(f"{res['name']}: uploaded and verified present in OneDrive (id={res['id']}, size={res['size']})")
        print(f"  webUrl: {res['webUrl']}")
if __name__ == "__main__":
    main()
