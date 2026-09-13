# Regenerate the self-hosted Poppins: assets/css/fonts.css + assets/fonts/poppins/*.woff2.
#
#   python tools/fetch-fonts.py
#
# Google Fonts is blocked by the Great Firewall, so the site may not hot-link it (see
# CLAUDE.md). This asks Google for the stylesheet with a modern browser User-Agent, which
# returns woff2 with a unicode-range per subset, downloads every face it names and rewrites
# the URLs to /assets/fonts/. Existing files are kept, so a rerun only fetches what is new.
#
# WEIGHTS must match what the site actually declares (SCSS font-weight values plus the
# Bootstrap utilities: fw-normal 400, fw-medium 500, fw-semibold 600, fw-bold 700). Nothing
# declares an italic, so none is fetched; a browser synthesises one if content ever needs it.
# SUBSETS are the ones Poppins covers for our languages: our non-Latin trees (Arabic, Hebrew,
# Japanese, Korean, Chinese, Persian, Urdu) fall back to the system font either way.
import io, os, re, sys, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

WEIGHTS = "300;400;500;600;700"
SUBSETS = ("latin", "latin-ext", "devanagari")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts", "poppins")
CSS_OUT = os.path.join(ROOT, "assets", "css", "fonts.css")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
HEADER = """/* Poppins, self-hosted. VENDORED: do not hand-edit — regenerate with tools/fetch-fonts.py.
   Google Fonts is blocked by the Great Firewall, so the faces are served from /assets/fonts/.
   Only the five weights the site actually uses (300/400/500/600/700) and the three subsets
   Poppins covers for our languages (latin, latin-ext, devanagari) are included; no italics,
   as nothing declares one. unicode-range keeps a visitor from downloading subsets they
   never render. */
"""

def get(url, binary=False):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read() if binary else r.read().decode("utf-8")

os.makedirs(FONT_DIR, exist_ok=True)
css = get("https://fonts.googleapis.com/css2?family=Poppins:wght@%s&display=swap" % WEIGHTS)
blocks = re.findall(r"/\* (\w[\w-]*) \*/\s*@font-face \{(.*?)\}", css, re.S)
blocks = [(s, b) for s, b in blocks if s in SUBSETS]
assert len(blocks) == len(SUBSETS) * len(WEIGHTS.split(";")), "unexpected face count: %d" % len(blocks)

out, fetched = [HEADER], 0
for subset, body in blocks:
    weight = re.search(r"font-weight:\s*(\d+)", body).group(1)
    url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
    name = "poppins-%s-%s.woff2" % (subset, weight)
    path = os.path.join(FONT_DIR, name)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        io.open(path, "wb").write(get(url, binary=True)); fetched += 1
    out.append("/* %s */\n@font-face {%s}\n" % (subset, body.replace(url, "/assets/fonts/poppins/" + name)))

io.open(CSS_OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out))
total = sum(os.path.getsize(os.path.join(FONT_DIR, f)) for f in os.listdir(FONT_DIR))
print("faces: %d (%d downloaded), fonts on disk: %d files / %d KB"
      % (len(blocks), fetched, len(os.listdir(FONT_DIR)), round(total / 1024)))
