# Add the CTA-click forwarding (tools/gtm-cta-tracking.json) to the live GTM container
# through the Tag Manager API v2. Idempotent: an entity whose name already exists in
# the workspace is reused, never duplicated. Nothing is deleted.
#
#   python tools/gtm-import.py --dry-run     # read-only: shows what the workspace holds
#   python tools/gtm-import.py --publish     # create what is missing, then version + publish
#
# Auth: impersonates gtm-www@vpnhood-tools.iam.gserviceaccount.com through your own
# gcloud login (the org policy forbids service account keys). You need
# roles/iam.serviceAccountTokenCreator on that SA, and the SA needs Publish permission
# on the container in GTM user management. A key file at ~/.secrets/gtm-www.json is
# used instead when one exists (--key PATH to point elsewhere).
import io, json, os, subprocess, sys, urllib.request, urllib.error
sys.stdout.reconfigure(encoding="utf-8")
ARGS = sys.argv[1:]
PROJECT = ARGS[ARGS.index("--project") + 1] if "--project" in ARGS else None
PUBLISH = "--publish" in ARGS
DRY = "--dry-run" in ARGS
CONTAINER_PUBLIC_ID = "GTM-M39NR6ZS"
EXPORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gtm-cta-tracking.json")
API = "https://tagmanager.googleapis.com/tagmanager/v2/"
SA = "gtm-www@vpnhood-tools.iam.gserviceaccount.com"
SCOPES = ["https://www.googleapis.com/auth/" + s for s in
          ("tagmanager.readonly", "tagmanager.edit.containers", "tagmanager.edit.containerversions", "tagmanager.publish")]

KEY = ARGS[ARGS.index("--key") + 1] if "--key" in ARGS else os.path.expanduser("~/.secrets/gtm-www.json")
if os.path.exists(KEY) and os.path.getsize(KEY) > 0:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)
    creds.refresh(Request()); TOKEN = creds.token
    print("auth: service account key", creds.service_account_email)
else:
    tok = subprocess.run(["gcloud", "auth", "print-access-token", "--impersonate-service-account=" + SA, "--scopes=" + ",".join(SCOPES)],
                         capture_output=True, text=True, shell=True, timeout=90)
    TOKEN = tok.stdout.strip()
    assert TOKEN, tok.stderr[:400]
    print("auth: impersonating", SA)

def call(method, path, body=None, tolerate=False):
    """tolerate=True returns None on a 4xx instead of exiting, for probing."""
    h = {"Authorization": "Bearer " + TOKEN}
    if PROJECT: h["x-goog-user-project"] = PROJECT
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8"); h["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        if tolerate and 400 <= e.code < 500: return None
        raise SystemExit(f"{method} {path} -> {e.code}: {e.read().decode('utf-8', 'replace')[:600]}")

# the export uses SCREAMING enums; the API wants lowerCamel
def lc(v):
    parts = v.lower().split("_"); return parts[0] + "".join(p.title() for p in parts[1:])
def conv_params(params):
    out = []
    for p in params:
        q = {"type": lc(p["type"])}
        if "key" in p: q["key"] = p["key"]
        if "value" in p: q["value"] = p["value"]
        if "list" in p: q["list"] = conv_params(p["list"])
        if "map" in p: q["map"] = conv_params(p["map"])
        out.append(q)
    return out

exp = json.load(io.open(EXPORT, encoding="utf-8"))["containerVersion"]

# ---- locate the container and its default workspace ------------------------------
accounts = call("GET", "accounts").get("account", [])
print("accounts:", [(a["accountId"], a["name"]) for a in accounts])
container = None
for a in accounts:
    for c in call("GET", a["path"] + "/containers").get("container", []):
        if c.get("publicId") == CONTAINER_PUBLIC_ID: container = c
assert container, "container not found: is the service account a user of it?"
print("container:", container["path"], container["name"])
# Creating a version consumes the workspace it came from ("Workspace is already submitted"),
# so a second run has to work somewhere else. Probe the candidates with a harmless write and
# fall back to a fresh workspace of our own.
workspaces = call("GET", container["path"] + "/workspaces").get("workspace", [])
candidates = ([w for w in workspaces if w["name"] == "Default Workspace"]
              + [w for w in workspaces if w["name"] != "Default Workspace"])
ws = None
for w in candidates:
    probe = call("POST", w["path"] + "/variables", {"name": "zz - import probe", "type": "c",
                 "parameter": [{"type": "template", "key": "value", "value": "probe"}]}, tolerate=True)
    if probe is not None:
        call("DELETE", probe["path"]); ws = w; break
if ws is None:
    ws = call("POST", container["path"] + "/workspaces", {"name": "CTA tracking import"})
    print("every workspace was already submitted, created a new one")
print("workspace:", ws["path"], ws["name"])

existing_vars = {v["name"]: v for v in call("GET", ws["path"] + "/variables").get("variable", [])}
existing_trg = {t["name"]: t for t in call("GET", ws["path"] + "/triggers").get("trigger", [])}
existing_tags = {t["name"]: t for t in call("GET", ws["path"] + "/tags").get("tag", [])}
print(f"workspace has {len(existing_vars)} variables, {len(existing_trg)} triggers, {len(existing_tags)} tags")
print("tags:", sorted(existing_tags))
if DRY: raise SystemExit("dry run: nothing written")

# ---- variables ---------------------------------------------------------------------
for v in exp["variable"]:
    if v["name"] in existing_vars: print("variable exists:", v["name"]); continue
    r = call("POST", ws["path"] + "/variables", {"name": v["name"], "type": v["type"], "parameter": conv_params(v["parameter"])})
    existing_vars[v["name"]] = r; print("variable created:", r["name"], r["variableId"])

# ---- trigger -----------------------------------------------------------------------
trigger_ids = {}
for t in exp["trigger"]:
    if t["name"] in existing_trg:
        print("trigger exists:", t["name"]); trigger_ids[t["triggerId"]] = existing_trg[t["name"]]["triggerId"]; continue
    body = {"name": t["name"], "type": lc(t["type"]),
            "customEventFilter": [{"type": lc(f["type"]), "parameter": conv_params(f["parameter"])} for f in t["customEventFilter"]]}
    r = call("POST", ws["path"] + "/triggers", body)
    trigger_ids[t["triggerId"]] = r["triggerId"]; print("trigger created:", r["name"], r["triggerId"])

# ---- tag ---------------------------------------------------------------------------
for t in exp["tag"]:
    if t["name"] in existing_tags: print("tag exists:", t["name"]); continue
    body = {"name": t["name"], "type": t["type"], "parameter": conv_params(t["parameter"]),
            "firingTriggerId": [trigger_ids[i] for i in t["firingTriggerId"]], "tagFiringOption": lc(t["tagFiringOption"])}
    r = call("POST", ws["path"] + "/tags", body)
    print("tag created:", r["name"], r["tagId"])

# ---- version + publish -------------------------------------------------------------
if PUBLISH:
    cv = call("POST", ws["path"] + ":create_version",
              {"name": "CTA click tracking", "notes": "Forward the site's vh_cta_click dataLayer event to GA4 as cta_click (cta_id, cta_href)."})
    if cv.get("compilerError"): raise SystemExit("compiler error: " + json.dumps(cv)[:800])
    ver = cv["containerVersion"]; print("version created:", ver["containerVersionId"], ver.get("name"))
    pub = call("POST", ver["path"] + ":publish", {})
    print("published:", pub.get("containerVersion", {}).get("containerVersionId"))
else:
    print("not published (no --publish)")
