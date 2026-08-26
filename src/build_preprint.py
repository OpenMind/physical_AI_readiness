import browser
import pathlib, base64, subprocess, pandas as pd

html = pathlib.Path("report_preprint.html").read_text()
for name in ["map_readiness","map_latitude","map_effective","map_pillars","map_clusters",
             "chart_quadrant","chart_top25","chart_uncertainty"]:
    fig = pathlib.Path(f"out/{name}.png")
    if not fig.exists():
        raise SystemExit(f"missing figure {fig}. Run the full build once:\n"
                         f"    python3 src/build.py")
    b64 = base64.b64encode(fig.read_bytes()).decode()
    html = html.replace("{{IMG:%s}}" % name, f"data:image/png;base64,{b64}")

df = pd.read_csv("out/pairi_2026.csv").sort_values("PAIRI", ascending=False)
rows = "".join(
    f"<tr><td class='n'>{i}</td><td>{r['name']}</td>"
    f"<td class='n'>{r.PAIRI:.1f}</td>"
    f"<td class='n'>{r.P1_energy:.0f}</td><td class='n'>{r.P2_compute:.0f}</td>"
    f"<td class='n'>{r.P3_robotics:.0f}</td><td class='n'>{r.P4_materials:.0f}</td>"
    f"<td class='n'>{r.P5_human:.0f}</td><td class='n'>{r.P6_demand:.0f}</td>"
    f"<td class='n'>{r.OLI:.0f}</td><td class='n'>{r.EFFECTIVE:.1f}</td></tr>"
    for i, (_, r) in enumerate(df.iterrows(), 1))
table = ("<table class='rank wide'><thead><tr><th class='n'>#</th><th>Country</th>"
         "<th class='n'>PAIRI</th><th class='n'>P1</th><th class='n'>P2</th>"
         "<th class='n'>P3</th><th class='n'>P4</th><th class='n'>P5</th>"
         "<th class='n'>P6</th><th class='n'>OLI</th><th class='n'>EFF</th>"
         "</tr></thead><tbody>" + rows + "</tbody></table>")
html = html.replace("{{RANKING_TABLE}}", table)

pathlib.Path("out/preprint_full.html").write_text(html)
CHROME = browser.find()
if not CHROME:
    raise SystemExit(browser.HINT)
subprocess.run([CHROME,"--headless=new",
  "--no-sandbox","--disable-gpu","--run-all-compositor-stages-before-draw",
  "--virtual-time-budget=30000","--no-pdf-header-footer",
  "--print-to-pdf=out/OpenMind_Physical_AI_Readiness_Index_2026.pdf",
  "out/preprint_full.html"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# Read the rendered PDF back and report what is in it. The link counts are a
# regression check: the reference locators and the inline [n] markers are only
# clickable if Chromium emitted annotations for them, and a CSS or markup change
# can silently take that away.
from pypdf import PdfReader

PDF = "out/OpenMind_Physical_AI_Readiness_Index_2026.pdf"
reader = PdfReader(PDF)
external, internal = 0, 0
for page in reader.pages:
    for ref in (page.get("/Annots") or []):
        a = ref.get_object()
        if a.get("/Subtype") != "/Link":
            continue
        action = a.get("/A")
        if action is not None and action.get_object().get("/S") == "/URI":
            external += 1
        elif a.get("/Dest") is not None or action is not None:
            internal += 1
print(f"pages: {len(reader.pages)} | links: {external} external, {internal} internal")
if not external:
    print("  !! no external link annotations - the reference URLs are not clickable")
if not internal:
    print("  !! no internal link annotations - the inline [n] markers do not jump")
