"""report.md  ->  report.html

The Markdown file is the editable source of truth for the report's prose.
This converts it into the HTML that preprint.py consumes.

report.md opens with a "::: front" block holding the title, byline, abstract,
keywords and colophon. That block is stripped here and read by preprint.py
instead; its format is documented at the top of front.py.

SYNTAX
------
## 1 · Executive summary        section heading
### 3.1 Construction            subsection heading
#### What we found              minor heading

Plain paragraphs are separated by a blank line and may span several source
lines; line breaks inside a paragraph are not significant.

{lead}  ...                     larger intro paragraph
{small} ...                     small grey paragraph (used under headings)
{tiny}  ...                     smallest grey paragraph

::: kpi                         the four-figure strip
82.9 | China's readiness score, …
:::

::: box The two indices         tinted box with a title
First paragraph.

Second paragraph.
:::

::: warn Four traps …           same, but rule-topped "caution" styling
:::

::: figure map_readiness        a figure; the body is its caption
Figure 1 · **Title.** Caption text …
:::

| Pillar | {.n} Weight | …      Markdown tables. A cell prefixed with {.n}
|---|---|---|                    is right-aligned (numeric).

{{RANKING_TABLE}}               left untouched; filled in at build time

Inline: **bold**, *italic*, and raw HTML both pass through unchanged, so
entities such as &middot; &yen; &sect; and <sup> work as written.
"""
import pathlib, re, sys
import front


def inline(t):
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t, flags=re.S)
    t = re.sub(r'(?<![\w*])\*([^*\n]+?)\*(?![\w*])', r'<i>\1</i>', t)
    return t.strip()


def table(lines):
    rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in lines]
    rows = [r for r in rows if not all(re.fullmatch(r':?-{2,}:?', c) for c in r)]
    head, body = rows[0], rows[1:]

    def cell(c, tag):
        cls = style = ""
        while True:                      # markers may appear in either order
            m = re.match(r'\{\.n\}\s*', c)
            if m:
                cls, c = ' class="n"', c[m.end():]; continue
            m = re.match(r'\{w=([\d.]+)%\}\s*', c)
            if m:
                style, c = f' style="width:{m.group(1)}%"', c[m.end():]; continue
            break
        return f"<{tag}{cls}{style}>{inline(c)}</{tag}>"

    out = ["<table>", "<thead><tr>" + "".join(cell(c, "th") for c in head) + "</tr></thead>", "<tbody>"]
    for r in body:
        out.append("<tr>" + "".join(cell(c, "td") for c in r) + "</tr>")
    out += ["</tbody></table>"]
    return "\n".join(out)


def convert(md):
    out, i, lines = [], 0, md.split("\n")
    while i < len(lines):
        ln = lines[i]

        if not ln.strip():
            i += 1; continue

        if ln.startswith("<!--"):                 # comments may span lines
            block = [ln]
            while "-->" not in lines[i] and i + 1 < len(lines):
                i += 1; block.append(lines[i])
            out.append("\n".join(block)); i += 1; continue

        if ln.strip() == "{{RANKING_TABLE}}":
            out.append("{{RANKING_TABLE}}"); i += 1; continue

        # ---- fenced blocks -------------------------------------------------
        if ln.startswith(":::"):
            head = ln[3:].strip().split(None, 1)
            kind = head[0]
            title = head[1] if len(head) > 1 else ""
            block, i = [], i + 1
            while i < len(lines) and lines[i].strip() != ":::":
                block.append(lines[i]); i += 1
            i += 1

            if kind == "kpi":
                rows, cells = [], []
                for b in block:                       # a new cell starts at each "|"
                    if not b.strip(): continue
                    if "|" in b: rows.append(b)
                    elif rows: rows[-1] += " " + b.strip()
                for r in rows:
                    v, k = r.split("|", 1)
                    cells.append(f'<div><div class="v">{inline(v)}</div>'
                                 f'<div class="l">{inline(k)}</div></div>')
                out.append('<div class="kpi">\n' + "\n".join(cells) + "\n</div>")

            elif kind in ("box", "warn"):
                cls = "box" if kind == "box" else "box warn"
                paras = [p for p in "\n".join(block).split("\n\n") if p.strip()]
                inner = "".join(f"<p>{inline(p)}</p>\n" for p in paras)
                out.append(f'<div class="{cls}">\n<h4>{inline(title)}</h4>\n{inner}</div>')

            elif kind == "figure":
                cap = inline(" ".join(b.strip() for b in block if b.strip()))
                out.append(f'<figure>\n<img src="{{{{IMG:{title}}}}}">\n'
                           f'<figcaption>{cap}</figcaption>\n</figure>')
            else:
                out.append("\n".join(block))
            continue

        # ---- tables --------------------------------------------------------
        if ln.lstrip().startswith("|"):
            tb = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                tb.append(lines[i]); i += 1
            out.append(table(tb)); continue

        # ---- headings ------------------------------------------------------
        m = re.match(r'(#{2,4})\s+(.*)', ln)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1; continue

        # ---- paragraphs ----------------------------------------------------
        para = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(":::") \
                and not re.match(r'#{2,4}\s', lines[i]) and not lines[i].lstrip().startswith("|"):
            para.append(lines[i]); i += 1
        text = " ".join(p.strip() for p in para)
        cls = ""
        m = re.match(r'\{(lead|small|tiny)\}\s*', text)
        if m:
            k = m.group(1); text = text[m.end():]
            cls = ' class="lead"' if k == "lead" else \
                  ' class="small" style="margin-top:-3pt"' if k == "small" else ' class="tiny"'
        out.append(f"<p{cls}>{inline(text)}</p>")
    return "\n\n".join(out)


HEAD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>The OpenMind Physical AI Readiness Index 2026</title></head><body>
<!-- Generated from report.md by md_to_html.py. Edit report.md, not this file. -->
"""

if __name__ == "__main__":
    src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "report.md")
    dst = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "report.html")
    _, body = front.parse(src.read_text(), src.name)   # front matter is preprint.py's
    dst.write_text(HEAD + convert(body) + "\n</body></html>\n")
    print(f"{src} -> {dst}  ({len(dst.read_text()):,} bytes)")
