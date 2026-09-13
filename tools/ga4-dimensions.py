# Register the CTA event parameters as event-scoped custom dimensions on the GA4 property
# that owns the site's measurement id. A parameter GA4 has not been told about is collected
# but never appears in a report, and registering one is NOT retroactive.
#
#   python tools/ga4-dimensions.py            # report what exists
#   python tools/ga4-dimensions.py --create   # create what is missing
#
# Auth: impersonates ai-agent@vpnhood-tools.iam.gserviceaccount.com through your own gcloud
# login (the org policy forbids service-account keys). You need
# roles/iam.serviceAccountTokenCreator on that account, and the account needs the **Editor**
# role on the GA4 property — Viewer and Analyst can read but cannot create definitions.
#
# The property is looked up by measurement id rather than hardcoded, so this keeps working
# if the property is recreated. Today that resolves to "www.vpnhood.com".
import json, subprocess, sys, urllib.request, urllib.error
sys.stdout.reconfigure(encoding="utf-8")

CREATE = "--create" in sys.argv
MEASUREMENT_ID = "G-DWH7NV15XQ"
SA = "ai-agent@vpnhood-tools.iam.gserviceaccount.com"
SCOPES = ",".join(["https://www.googleapis.com/auth/analytics.edit",
                   "https://www.googleapis.com/auth/analytics.readonly"])
API = "https://analyticsadmin.googleapis.com/v1beta/"
# parameter name (must match assets/js/vh-general.js), report label, description
WANT = [("cta_id", "CTA id", "Which CTA was clicked: the data-vh-track value on the link."),
        ("cta_href", "CTA destination", "Where the clicked CTA pointed.")]

TOKEN = subprocess.run(["gcloud", "auth", "print-access-token",
                        "--impersonate-service-account=" + SA, "--scopes=" + SCOPES],
                       capture_output=True, text=True, shell=True, timeout=120).stdout.strip()
assert TOKEN, "could not mint a token: is the token-creator grant in place?"

def call(method, path, body=None):
    h = {"Authorization": "Bearer " + TOKEN}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8"); h["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read(); return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise SystemExit("%s %s -> %s: %s" % (method, path, e.code, e.read().decode("utf-8", "replace")[:400]))

target = None
for acct in call("GET", "accountSummaries").get("accountSummaries", []):
    for ps in acct.get("propertySummaries", []):
        for st in call("GET", ps["property"] + "/dataStreams").get("dataStreams", []):
            if st.get("webStreamData", {}).get("measurementId") == MEASUREMENT_ID:
                target = (acct["displayName"], ps["displayName"], ps["property"], st["displayName"])
assert target, "no property carries " + MEASUREMENT_ID + " (is the service account a user of it?)"
account, prop_name, prop, stream = target
print("account: %s | property: %s (%s) | stream: %s" % (account, prop_name, prop, stream))

have = {d["parameterName"]: d for d in call("GET", prop + "/customDimensions").get("customDimensions", [])}
print("event-scoped dimensions today:", sorted(k for k, v in have.items() if v.get("scope") == "EVENT"))
for param, display, desc in WANT:
    if param in have:
        print("already registered:", param, "->", have[param]["displayName"], have[param]["scope"]); continue
    if not CREATE:
        print("MISSING:", param, "(run with --create)"); continue
    r = call("POST", prop + "/customDimensions",
             {"parameterName": param, "displayName": display, "description": desc, "scope": "EVENT"})
    print("created:", r["parameterName"], "->", r["displayName"], r["scope"])
