# Sources

High-resolution originals and working files kept for future re-export. This
folder is **excluded from the Jekyll build** (the `.` prefix), so nothing here
is published — the optimized copies under `/assets/` are what ship.

- `images/` — full-resolution image originals.

| Source | Optimized asset | Notes |
|---|---|---|
| `images/manager-logo.webp` (512×512) | `/assets/images/general/manager-logo.webp` (300×300) | Displayed at ≤100 px; 300 covers retina. Re-export with `sharp(src).resize(300,300,{fit:'inside'}).webp({quality:85})`. |
