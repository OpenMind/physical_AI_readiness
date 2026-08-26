"""References: parsed from references.md, cited by key from report.md.

The prose carries the key, not a number:

    ... more than all other countries combined.[@ifr-world-robotics-2025]
    ... on both counts.[@iea-rare-earth-elements-2026; @adamas-2026]

Numbers are assigned here, in order of first appearance, so no number is ever
written by hand and rewriting a sentence cannot detach its citation. A key with
no record is a build error naming the key.

references.md format is documented at the top of that file.
"""
import re
from collections import OrderedDict

KEY = re.compile(r'^\[([A-Za-z0-9][A-Za-z0-9._-]*)\]\s*$')
CITE = re.compile(r'\[@([^\]]+)\]')
NUMBERING = "appearance"          # or "listed", to number by references.md order


def parse(text, path="references.md"):
    """references.md -> OrderedDict key -> {cite, url, note}."""
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    out, key = OrderedDict(), None
    for ln in text.split("\n"):
        m = KEY.match(ln.strip()) if not ln.startswith(" ") else None
        if m:
            key = m.group(1)
            if key in out:
                raise SystemExit(f"{path}: duplicate key [{key}]")
            out[key] = {"cite": [], "url": "", "note": ""}
            continue
        if key is None or not ln.strip():
            continue
        t = ln.strip()
        if t.lower().startswith("note:"):
            out[key]["note"] = t[5:].strip()
        elif re.match(r'https?://', t):
            out[key]["url"] = t
        else:
            out[key]["cite"].append(t)
    for k, v in out.items():
        v["cite"] = inline(" ".join(v["cite"]))
        if not v["cite"]:
            raise SystemExit(f"{path}: [{k}] has no citation text")
    if not out:
        raise SystemExit(f"{path}: no records found")
    return out


def inline(t):
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t, flags=re.S)
    t = re.sub(r'(?<![\w*])\*([^*\n]+?)\*(?![\w*])', r'<i>\1</i>', t)
    return t.strip()


def resolve(body, records, marker):
    """Replace every [@key] in `body` with marker(numbers). Returns
    (body, ordered list of cited keys, list of undefined keys used)."""
    order, missing = [], []

    def sub(m):
        ks = [k.strip().lstrip("@") for k in m.group(1).split(";")]
        nums = []
        for k in ks:
            if k not in records:
                missing.append(k)
                continue
            if k not in order:
                order.append(k)
            nums.append(k)
        return marker(nums) if nums else ""

    body = CITE.sub(sub, body)
    return body, order, missing


BAD = [
    (re.compile(r'\[\s*(https?://[^\]]+)\]'),
     "a bare URL in square brackets. Add a record to references.md and cite its key"),
    (re.compile(r'\[@([^\]]*)\]'), "an unresolved citation marker"),
    (re.compile(r'\[@[^\]]*$', re.M), "an unclosed [@ marker"),
]


def lint(body):
    """Anything that looks like a citation but was not resolved. A bare
    [http...] renders as literal text in the PDF, which is how a broken
    reference gets published."""
    out = []
    for pat, why in BAD:
        for m in pat.finditer(body):
            out.append(f"{why}:  {m.group(0)[:88]}")
    return out


def numbering(records, order):
    """key -> [n]. Cited sources first in citation order, then the rest."""
    if NUMBERING == "listed":
        return {k: i for i, k in enumerate(records, 1)}, len(order)
    rest = [k for k in records if k not in order]
    return {k: i for i, k in enumerate(order + rest, 1)}, len(order)
