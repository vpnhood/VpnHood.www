# Sources

High-resolution originals and working files kept for future re-export. This
folder is **excluded from the Jekyll build** (the `.` prefix), so nothing here
is published — the optimized copies under `/assets/` are what ship.

- `images/` — full-resolution image originals.

| Source | Optimized asset | Notes |
|---|---|---|
| `images/manager-logo.webp` (512×512) | `/assets/images/general/manager-logo.webp` (300×300) | Displayed at ≤100 px; 300 covers retina. Re-export with `sharp(src).resize(300,300,{fit:'inside'}).webp({quality:85})`. |
| `images/banner-purple-light.webp` (924×764) | `/assets/images/home/banner-purple-light.webp` (480w) | Decorative hero glow (radial blur); displayed up to 924 px but upscaling a blur is invisible. `sharp(src).resize({width:480}).webp({quality:82})`. |
| `images/banner-green-light.webp` (856×837) | `/assets/images/home/banner-green-light.webp` (480w) | Same as above. `sharp(src).resize({width:480}).webp({quality:82})`. |
| `images/commiunity-bg.webp` (1130×592) | `/assets/images/home/commiunity-bg.webp` (960w) | Soft horizon arc; conservative 960w (~1.18× upscale on desktop). `sharp(src).resize({width:960}).webp({quality:82})`. |
