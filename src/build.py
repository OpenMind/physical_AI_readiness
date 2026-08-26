#!/usr/bin/env python3
"""Build everything from source, in order.

    python3 src/build.py            # full rebuild
    python3 src/build.py report     # prose -> PDF only (skips the index and figures)

Chain:
    build_index.py   pairi_2026.csv, pairi_clusters_2026.csv   (data)
    bootstrap.py     pairi_uncertainty.csv                     (Monte Carlo, ~40 s)
    make_maps.py     out/*.png, out/*.svg                      (figures)
    md_to_html.py    report.md -> report.html                  (prose)
    preprint.py      report.html -> report_preprint.html       (layout + citations)
    build_preprint.py -> OpenMind_Physical_AI_Readiness_Index_2026.pdf
"""
import subprocess, sys, pathlib
import browser

HERE = pathlib.Path(__file__).resolve().parent
(HERE / "out").mkdir(exist_ok=True)   # first run on a fresh clone
CHROME = browser.find()
PY = sys.executable                   # so `uv run src/build.py` keeps its env
PROSE_ONLY = len(sys.argv) > 1 and sys.argv[1] == "report"

STEPS = ([] if PROSE_ONLY else [
    ("index   ", [PY, "build_index.py"]),
    ("bootstrap", [PY, "bootstrap.py"]),   # writes out/pairi_uncertainty.csv,
    ("figures ", [PY, "make_maps.py"]),    # which Fig. 3 is drawn from
]) + [
    ("prose   ", [PY, "md_to_html.py", "report.md", "report.html"]),
    ("layout  ", [PY, "preprint.py"]),
    ("pdf     ", [PY, "build_preprint.py"]),
]

for name, cmd in STEPS:
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True)
    if r.returncode:
        print(f"[{name}] FAILED\n{r.stdout}\n{r.stderr}")
        sys.exit(1)
    tail = [l for l in r.stdout.strip().split("\n") if l.strip()][-3:]
    print(f"[{name}] " + " | ".join(t.strip() for t in tail))
    for l in r.stdout.split("\n"):
        if "!!" in l or l.strip().startswith("-") or "Edit the CITES" in l:
            print(f"           {l.strip()}")

# The repo keeps a copy of each PDF at its root -- that is what a visitor
# opens first. Publish them from the build so they can never go stale by hand.
FIGURES = ["map_readiness", "map_latitude", "map_effective", "map_pillars",
           "map_clusters", "chart_quadrant", "chart_top25", "chart_uncertainty"]
ROOT = HERE.parent
if (ROOT / "README.md").exists():                  # only when src/ sits in the repo
    import shutil
    published = 0
    for f in ["OpenMind_Physical_AI_Readiness_Index_2026.pdf"]:
        if (HERE / "out" / f).exists():
            shutil.copy2(HERE / "out" / f, ROOT / f); published += 1
    (ROOT / "maps").mkdir(exist_ok=True)
    for name in FIGURES:                           # explicit list: out/ also holds scratch
        for ext in (".png", ".svg"):
            f = HERE / "out" / (name + ext)
            if f.exists():
                shutil.copy2(f, ROOT / "maps" / f.name); published += 1
    print(f"[publish ] {published} files copied to the repo root and maps/")

print("\nDone. PDFs are in out/.")
