"""Front matter: the report's title-page and colophon prose, kept in report.md.

Everything a reader sees as words now lives in report.md. preprint.py owns the
layout — the HTML skeleton, the CSS, the citation machinery — and takes its text
from here. Nothing in this file knows what the report says.

FORMAT
------
A single fenced block at the very top of report.md:

    ::: front
    key: a one-line value

    key:
      an indented value that runs over
      several lines

      and may have blank lines in it for readability
    :::

A key is lower-case letters, digits and hyphens, at zero indent, followed by a
colon. Everything until the next key (or the closing ":::") belongs to it.

Line breaks
    In most fields the line breaks you type are cosmetic: the value is reflowed
    into one flowing block, and blank lines in the source vanish. That is what
    you want for an abstract or a colophon, where the source should be easy to
    edit and the output is justified prose.

    In `title` and `affiliation` the line breaks are real and become <br>.
    Those are the two places where the author, not the typesetter, decides
    where the line turns.

Markup
    **bold**, *italic*, `monospace`, [link text](https://url), and raw HTML and
    entities pass through as they do everywhere else in report.md (&middot;
    &sect; &ndash; and so on). A bare email address becomes a mailto link.
    Links here become real clickable annotations in the PDF.

Fields
    runninghead   the small rule-under line above the title
    title         the title itself; line breaks are honoured
    authors       the byline
    affiliation   under the byline; line breaks are honoured
    corresponding shown in red under the affiliation. Optional: delete the
                  field and the line disappears.
    abstract      the abstract
    keywords      the keyword list; the "Keywords:" label is supplied by the
                  template, so do not type it here
    colophon      the block at the very end of the paper. Run-in labels are
                  written **Like this.**
    accessed      the access date appended to every reference

Missing a required field is a build error naming the field, not a silent gap in
the paper.
"""
import re

# Fields whose line breaks are the author's and survive into the output.
LINEBREAK = {"title", "affiliation"}

REQUIRED = ["runninghead", "title", "authors", "affiliation",
            "abstract", "keywords", "colophon", "accessed"]

KEY = re.compile(r'^([a-z][a-z0-9-]*):[ \t]*(.*)$')


def inline(t):
    """The inline markup of report.md, plus links, `code` spans and bare emails."""
    t = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t, flags=re.S)
    t = re.sub(r'(?<![\w*])\*([^*\n]+?)\*(?![\w*])', r'<i>\1</i>', t)
    t = re.sub(r'`([^`\n]+?)`', r'<code>\1</code>', t)
    t = re.sub(r'(?<![\w.:@"-])([\w.+-]+@[\w-]+(?:\.[\w-]+)+)',   # no trailing full stop
               r'<a href="mailto:\1">\1</a>', t)
    return t.strip()


def split(md):
    """(front_text, body) — the ::: front block and the report without it."""
    m = re.search(r'^::: *front[ \t]*\n(.*?)^:::[ \t]*\n?', md, re.S | re.M)
    if not m:
        return "", md
    return m.group(1), md[:m.start()] + md[m.end():]


def fields(front_text):
    """Front-matter text -> {key: raw lines}."""
    out, key = {}, None
    for ln in front_text.split("\n"):
        m = KEY.match(ln)
        if m:
            key = m.group(1)
            out[key] = [m.group(2)] if m.group(2).strip() else []
        elif key is not None:
            out[key].append(ln.strip())
    return out


def render(raw, key):
    """Raw lines -> the HTML fragment the template drops in."""
    if key in LINEBREAK:
        lines = [inline(l) for l in raw if l.strip()]
        return "<br>\n".join(lines)
    # reflow: every line, and every paragraph, joins into one block
    return inline(" ".join(l.strip() for l in raw if l.strip()))


def parse(md, path="report.md"):
    """(front, body). `front` is {key: html}; `body` is report.md without it."""
    front_text, body = split(md)
    if not front_text.strip():
        raise SystemExit(f"{path}: no '::: front' block. See front.py for the format.")
    raw = fields(front_text)
    missing = [k for k in REQUIRED if not raw.get(k)]
    if missing:
        raise SystemExit(f"{path}: front matter is missing {', '.join(missing)}. "
                         f"See front.py for the field list.")
    unknown = [k for k in raw if k not in REQUIRED + ["corresponding"]]
    if unknown:
        print(f"  !! front matter: unused field(s) {', '.join(unknown)} — typo?")
    front = {k: render(v, k) for k, v in raw.items() if v}
    # a plain-text title for <title>, from the first typed line
    front["title_plain"] = re.sub(r'<[^>]+>', '', raw["title"][0]).strip().rstrip(":")
    return front, body
