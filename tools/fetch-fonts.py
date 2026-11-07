# Regenerate the self-hosted fonts: Poppins (assets/css/fonts.css + assets/fonts/poppins/*.woff2)
# and Vazirmatn (assets/css/fonts-arabic.css + assets/fonts/vazirmatn/).
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
# SUBSETS are the ones Poppins covers for our languages. It has no Persian or Arabic letters, so
# Vazirmatn supplies those; Chinese falls back to the system font.
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

# Vazirmatn, for the letters Poppins lacks: one variable file, the arabic subset, the weights
# Poppins has. Its faces are named Poppins on purpose: faces of one family and one weight with
# different unicode-ranges act as one font, so every rule and inline diagram that names Poppins
# gets these letters with nothing else to change. The weights must match exactly, so there is a
# face for each one: a single 300-700 range would win alone, and Latin would lose Poppins.
# header.html links the stylesheet on RTL pages only.
VAZIR_DIR = os.path.join(ROOT, "assets", "fonts", "vazirmatn")
VAZIR_CSS = os.path.join(ROOT, "assets", "css", "fonts-arabic.css")
VAZIR_FILE = "vazirmatn-arabic.woff2"
VAZIR_LICENSE = "https://raw.githubusercontent.com/rastikerdar/vazirmatn/master/OFL.txt"
VAZIR_HEADER = """/* Vazirmatn, self-hosted, for the Persian and Arabic letters Poppins does not have.
   VENDORED: do not hand-edit — regenerate with tools/fetch-fonts.py. Named Poppins on purpose:
   faces of one family and one weight with different unicode-ranges act as one font, so every
   rule and diagram that names Poppins draws these letters from here. One face per Poppins
   weight, all on one variable file, as the weights must match. Linked on RTL pages only. */
"""

os.makedirs(VAZIR_DIR, exist_ok=True)
css = get("https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300..700&display=swap")
body = re.search(r"/\* arabic \*/\s*@font-face \{(.*?)\}", css, re.S).group(1)
url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
path = os.path.join(VAZIR_DIR, VAZIR_FILE)
if not os.path.exists(path) or os.path.getsize(path) == 0:
    io.open(path, "wb").write(get(url, binary=True))
license_path = os.path.join(VAZIR_DIR, "OFL.txt")
if not os.path.exists(license_path):
    io.open(license_path, "wb").write(get(VAZIR_LICENSE, binary=True))
body = body.replace(url, "/assets/fonts/vazirmatn/" + VAZIR_FILE).replace("'Vazirmatn'", "'Poppins'")
faces = [re.sub(r"font-weight:[^;]+;", "font-weight: %s;" % w, body) for w in WEIGHTS.split(";")]
io.open(VAZIR_CSS, "w", encoding="utf-8", newline="\n").write(
    VAZIR_HEADER + "".join("\n@font-face {%s}\n" % f for f in faces))
print("vazirmatn: %d KB" % round(os.path.getsize(path) / 1024))
