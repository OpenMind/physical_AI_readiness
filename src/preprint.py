"""Transform the report into a physics-preprint (REVTeX-style) layout:
two columns, Latin Modern Roman, roman-numeral sections, FIG./TABLE captions,
and a numbered bibliography with inline [n] citations."""
import pathlib, re, html
import front, refs

# The title-page and colophon prose lives in report.md, not here. This file
# owns the layout; the words are the author's.
FRONT, _ = front.parse(pathlib.Path("report.md").read_text())

src = pathlib.Path("report.html").read_text()
first = src.find("<h2>")                     # the body starts at the first section
if first < 0:
    raise SystemExit("report.html has no <h2> heading; did md_to_html.py run?")
body = src[first:src.index("</body>")]

# ---------------------------------------------------------------- REFERENCES
# Sources live in references.md, keyed. report.md cites them by key. Numbers are
# assigned in order of first appearance, so nothing here depends on the wording
# of a sentence -- which is what the old phrase-matching scheme depended on.
REC = refs.parse(pathlib.Path("references.md").read_text())


def marker(keys):
    nums = ",".join(f"<a href='#ref-{k}'>{{{k}}}</a>" for k in keys)
    return f"<sup class='c'>[{nums}]</sup>"


body, ORDER, MISSING = refs.resolve(body, REC, marker)
if MISSING:
    raise SystemExit("report.md cites keys with no record in references.md:\n  "
                     + "\n  ".join(sorted(set(MISSING))))
PROBLEMS = refs.lint(body)
if PROBLEMS:
    raise SystemExit("report.md has citation markup the build cannot resolve:\n  "
                     + "\n  ".join(PROBLEMS))
NUM, n_cited = refs.numbering(REC, ORDER)
for k, n in NUM.items():                      # placeholders -> final numbers
    body = body.replace("{%s}" % k, str(n)).replace("#ref-%s'" % k, "#ref%d'" % n)
print(f"citations: {len(ORDER)} sources cited at "
      f"{body.count(chr(60) + 'sup class=')} points in the prose")

# ------------------------------------------------------- STRUCTURAL SURGERY

# Headings are DERIVED from report.md, not duplicated here. Rename a section in
# the prose and the preprint follows. Only the labels that deliberately differ
# from the prose heading are listed below.
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI",
         "XII", "XIII", "XIV", "XV"]
SEC_LABEL = {                       # section number -> preprint heading
 1: "INTRODUCTION AND PRINCIPAL RESULTS",
 2: "SCOPE AND DEFINITIONS",
 3: "METHOD",
 4: "RESULTS: NATIONAL READINESS",
 6: "OPERATING LATITUDE",
 9: "METRO-CLUSTER RESOLUTION",
 11: "FORWARD INDICATORS",
}
APPENDIX = {13: "APPENDIX A"}       # sections set as an appendix, not numbered
SUB_LABEL = {                       # subsection number -> preprint label
 "3.2": "Choice of weights",
 "6.4": "Public opinion",
 "9.2": "The ten leading clusters",
}

seen = []


def sec(m):
    n, title = int(m.group(1)), m.group(2).strip()
    seen.append(n)
    label = SEC_LABEL.get(n, title.upper())
    if n in APPENDIX:
        return f'<h2 class="appx">{APPENDIX[n]}: {label}</h2>'
    if n >= len(ROMAN):
        raise SystemExit(f"report.md: section {n} has no roman numeral; extend ROMAN")
    return f"<h2>{ROMAN[n]}. {label}</h2>"


body = re.sub(r'<h2>(\d+) &middot; (.*?)</h2>', sec, body)
if not seen:
    raise SystemExit("report.md: no '## N &middot; Title' section headings found")
if seen != sorted(seen) or len(set(seen)) != len(seen):
    raise SystemExit(f"report.md: section numbers are out of order or repeated: {seen}")
missing = [n for n in SEC_LABEL if n not in seen] + [n for n in APPENDIX if n not in seen]
if missing:
    print(f"  !! preprint.py names section(s) {missing} that report.md no longer has")


def sub(m):
    n, i, title = int(m.group(1)), int(m.group(2)), m.group(3).strip()
    return f'<h3>{chr(64 + i)}. {SUB_LABEL.get(f"{n}.{i}", title)}</h3>'


body = re.sub(r'<h3>(\d+)\.(\d+) (.*?)</h3>', sub, body)
n_sub = len(re.findall(r"<h3>[A-Z]\. ", body))
print(f"headings: {len(seen)} sections, {n_sub} lettered subsections")

# FIG. n. captions
fign = [0]
def figcap(m):
    fign[0] += 1
    inner = re.sub(r'^<b>Fig\. \d+ &middot; ', '', m.group(1))
    inner = re.sub(r'^([^<]*?)</b>', r'<b>\1</b>', inner)
    return f'<figcaption><span class="fl">FIG. {fign[0]}.</span> {inner}</figcaption>'
body = re.sub(r'<figcaption>(.*?)</figcaption>', figcap, body, flags=re.S)

# TABLE captions above tables
body = body.replace('<table>\n<thead><tr><th>Pillar</th>',
  '<div class="tabcap"><span class="fl">TABLE I.</span> Pillar weights, principal '
  'indicators and primary sources.</div>\n<table>\n<thead><tr><th>Pillar</th>')
body = body.replace('<table>\n<thead><tr><th style="width:4%">#</th>',
  '<div class="tabcap"><span class="fl">TABLE II.</span> The ten leading metro clusters, '
  'scored on the same six pillars at metro resolution. The final column is a separate '
  'qualitative rank on capacity to build at volume within 36 months.</div>\n'
  '<table>\n<thead><tr><th style="width:4%">#</th>')
body = body.replace('<p class="small" style="margin-top:-3pt">PAIRI = OpenMind',
                    '<p class="small spanall" style="margin-top:-3pt">PAIRI = OpenMind')
body = body.replace('{{RANKING_TABLE}}',
  '<div class="tabcap wide"><span class="fl">TABLE III.</span> Complete country ranking. '
  'PAIRI is the capability composite; OLI the latitude composite; EFF the '
  'latitude-weighted product.</div>\n{{RANKING_TABLE}}')

# figures that must span both columns
body = body.replace('<figure>', '<figure class="wide">')


# The key-figures strip is a column-spanning element. Left inside section I it
# splits the opening paragraph across the break, so hoist it to sit directly
# under the keyword line as a banner.
m = re.search(r'<div class="kpi">\n.*?\n</div>', body, re.S)
KPI = ""
if m:
    KPI = m.group(0)
    body = body[:m.start()] + body[m.end():]

# ------------------------------------------------------------- BIBLIOGRAPHY
print(f"references: {len(REC)} defined, {n_cited} cited inline, "
      f"{len(REC) - n_cited} background")
bib = ('<h2 class="nobreakafter">References and data sources</h2>\n'
       '<p class="srcnote">Numbered in order of first citation. Entries after the last '
       'numbered citation informed the scoring without supporting a specific claim. The '
       'full working source list, running to roughly 180 items, accompanies the dataset.'
       '</p>\n<div class="bib">\n')
ACCESSED = f'Accessed {FRONT["accessed"]}.'


def locator(rec):
    """The URL becomes a real anchor so the PDF carries a clickable link
    annotation; a note is set as prose rather than printed as an address."""
    note = rec["note"]
    if note == "subscription":
        note = "subscription service"
    if not rec["url"]:
        tail = (f' <span class="sub">{note}</span>' if note else
                ' <span class="sub">no public locator; see the working source list</span>')
        return tail
    out = f' <a class="loc" href="{rec["url"]}">{rec["url"]}</a>'
    if note:
        out += f' <span class="sub">{note}</span>'
    return out


ordered = sorted(REC.items(), key=lambda kv: NUM[kv[0]])
for k, rec in ordered:
    n = NUM[k]
    if n == n_cited + 1 and n_cited < len(REC):
        bib += ('<div class="bibsep">Background sources, not cited for a specific '
                'claim</div>\n')
    bib += (f'<div id="ref{n}"><span class="bn">[{n}]</span>{rec["cite"]}'
            f'{locator(rec)} {ACCESSED}</div>\n')
bib += '</div>\n'

CSS = """
@page { size: A4; margin: 17mm 15mm 16mm 15mm; @bottom-center { content: counter(page); } }
:root{ --ink:#000; --ink2:#333; --ink3:#5a5a5a; --rule:#bfbfbf; --surf:#fff;
  --tint:#f2f2f2; }
*{box-sizing:border-box}
body{ font-family:"Latin Modern Roman","Nimbus Roman","Times New Roman",serif;
  font-size:9.1pt; line-height:1.30; color:var(--ink); margin:0; text-align:justify;
  hyphens:auto; -webkit-hyphens:auto; background:#fff; }
.doc{ column-count:2; column-gap:6.5mm; column-fill:auto; }
p{ margin:0; text-indent:1.1em; }
p.noind, .lead, figcaption, .tabcap, .bib div, .small, .tiny, .kpi div, .box p{ text-indent:0 }
h1,h2,h3,h4{ font-weight:normal; }
h2{ font-size:8.6pt; text-align:center; text-transform:uppercase; letter-spacing:0.6pt;
  margin:11pt 0 4pt; break-after:avoid; font-variant:small-caps; }
h2.appx{ column-span:all; break-before:page; border-top:0.5pt solid var(--rule);
  padding-top:8pt; margin-top:0 }
h2.nobreakafter{ column-span:all; border-top:0.5pt solid var(--rule); padding-top:8pt;
  margin-top:12pt; }
h3{ font-size:9.1pt; font-style:italic; text-align:center; margin:8pt 0 3pt;
  break-after:avoid; }
h4{ font-size:9.1pt; font-style:italic; margin:7pt 0 2pt; break-after:avoid;
  text-transform:none; letter-spacing:0; }
sup.c{ font-size:7.2pt; line-height:0; }
a{ color:inherit; text-decoration:none }
code{ font-family:monospace }
.small{font-size:8pt;color:var(--ink2);line-height:1.28}
.tiny{font-size:7.2pt;color:var(--ink3);line-height:1.25}
.lead{font-size:9.1pt;line-height:1.30;color:var(--ink)}
figure{ margin:7pt 0 8pt; break-inside:avoid; }
figure.wide{ column-span:all; margin:9pt 0 10pt; }
figure img{ width:100%; display:block; border:0.4pt solid var(--rule); }
figcaption{ font-size:7.7pt; color:var(--ink2); margin-top:3.5pt; line-height:1.26;
  text-align:justify; }
.fl{ font-variant:small-caps; letter-spacing:0.3pt; color:var(--ink); }
.tabcap{ font-size:7.7pt; color:var(--ink2); line-height:1.26; margin:8pt 0 3pt;
  text-align:justify; }
table{ width:100%; border-collapse:collapse; font-size:7.3pt; margin:0 0 8pt;
  break-inside:avoid; }
th{ text-align:left; border-top:0.9pt solid var(--ink); border-bottom:0.5pt solid var(--ink);
  padding:2.6pt 3pt; font-weight:normal; font-style:italic; }
td{ padding:2.2pt 3pt; vertical-align:top; }
tbody tr:last-child td{ border-bottom:0.9pt solid var(--ink); }
td.n,th.n{ text-align:right; font-variant-numeric:tabular-nums }
tbody tr:nth-child(even){ background:transparent }
table.wide, .tabcap.wide, p.spanall{ column-span:all }
table.wide{ font-size:7.1pt }
table.rank.wide{ break-inside:auto }
table.rank.wide thead{ display:table-header-group }
table.rank.wide tr{ break-inside:avoid }
table.rank.wide tbody tr:last-child td{ border-bottom:0.9pt solid var(--ink) }
table.wide td, table.wide th{ padding:1.5pt 4pt }
.rank td{ padding:1.7pt 3pt }
.kpi{ display:flex; gap:5pt; margin:2pt 0 11pt; column-span:all;
  border-top:0.9pt solid var(--ink); border-bottom:0.5pt solid var(--ink);
  padding:5pt 0 6pt; }
.kpi div{ flex:1; padding-right:6pt; }
.kpi .v{ font-size:13pt; line-height:1; }
.kpi .l{ font-size:7.2pt; color:var(--ink2); line-height:1.24; margin-top:2.5pt }
.box{ background:var(--tint); padding:5pt 6pt; margin:7pt 0; break-inside:avoid;
  font-size:8.3pt; line-height:1.28; }
.box h4{ margin:0 0 2pt; font-style:italic }
.box p{ margin:0 0 3pt }
.warn{ background:#fff; border-top:0.5pt solid var(--ink); border-bottom:0.5pt solid var(--ink);
  padding:5pt 0; }
hr{ display:none }
.srcnote{ column-span:all; font-size:7.4pt; color:var(--ink2); text-indent:0;
  margin:0 0 5pt; text-align:justify }
.bib{ column-span:all; column-count:2; column-gap:6.5mm; font-size:7.1pt; line-height:1.24;
  text-align:left; }
.bib div{ padding-left:16pt; text-indent:-16pt; margin-bottom:1.6pt;
  break-inside:avoid; }
.bn{ display:inline-block; width:16pt; text-indent:0 }
.bibsep{ font-style:italic; color:var(--ink3); margin:4pt 0 2.5pt;
  padding-top:3pt; border-top:0.4pt solid var(--rule); break-after:avoid }
.loc{ font-family:"Latin Modern Mono",monospace; font-size:6.2pt; color:var(--ink3);
  overflow-wrap:anywhere; word-break:normal; hyphens:none; }
.sub{ font-style:italic; color:var(--ink3) }
/* ---- title page ---- */
.tp{ column-span:all; text-align:center; margin:0 0 10pt; }
.pnum{ font-size:7.4pt; color:var(--ink2); text-align:left; letter-spacing:0.4pt;
  text-transform:uppercase;
  border-bottom:0.4pt solid var(--rule); padding-bottom:3pt; margin-bottom:12pt; }
.tp h1{ font-size:15.5pt; line-height:1.18; margin:0 0 8pt; letter-spacing:0.1pt; }
.tp .au{ font-size:9.6pt; margin-bottom:2pt }
.tp .af{ font-size:8.4pt; font-style:italic; color:var(--ink2); line-height:1.38;
  margin-top:1pt }
.tp .dt{ font-size:8.2pt; color:var(--ink2); margin-top:5pt }
.tp .coi{ font-size:7.6pt; color:var(--ink2); margin-top:3pt; font-style:italic }
.abs{ column-span:all; margin:6pt 0 10pt; padding:0 12mm; font-size:8.4pt;
  line-height:1.32; text-align:justify; }
.abs .h{ font-variant:small-caps; letter-spacing:0.5pt; font-size:8pt; }
.kw{ column-span:all; padding:0 12mm; font-size:7.8pt; color:var(--ink2);
  margin-bottom:9pt; text-align:justify; }
.rule{ column-span:all; border-top:0.5pt solid var(--rule); margin:0 0 9pt }
.colophon{ column-span:all; border-top:0.5pt solid var(--rule); margin-top:11pt;
  padding-top:6pt; font-size:7.2pt; color:var(--ink2); line-height:1.3; text-align:left }
"""

TITLE_T = """
<div class="tp">
<div class="pnum">{RUNNINGHEAD}</div>
<h1>{TITLE}</h1>
<div class="au">{AUTHORS}</div>
<div class="af">{AFFILIATION}</div>
{CORRESPONDING}
</div>
<div class="abs"><span class="h">Abstract.</span> {ABSTRACT}</div>
<div class="kw"><i>Keywords:</i> {KEYWORDS}</div>
{KPI}
"""

COLOPHON = f"""
<div class="colophon">
{FRONT["colophon"]}
</div>
"""

SLOTS = {
    "{RUNNINGHEAD}":   FRONT["runninghead"],
    "{TITLE}":         FRONT["title"],
    "{AUTHORS}":       FRONT["authors"],
    "{AFFILIATION}":   FRONT["affiliation"],
    "{CORRESPONDING}": (f'<div class="coi">{FRONT["corresponding"]}</div>'
                        if FRONT.get("corresponding") else ""),
    "{ABSTRACT}":      FRONT["abstract"],
    "{KEYWORDS}":      FRONT["keywords"],
    "{KPI}":           KPI or '<div class="rule"></div>',
}
TITLE = TITLE_T
for slot, text in SLOTS.items():
    TITLE = TITLE.replace(slot, text)

out = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{html.escape(FRONT["title_plain"])}</title>
<style>{CSS}</style></head><body>
<div class="doc">
{TITLE}
{body}
{bib}
{COLOPHON}
</div>
</body></html>"""
pathlib.Path("report_preprint.html").write_text(out)
print("preprint html written:", len(out), "bytes")
