# OpenMind Physical AI Readiness Index 2026

A geospatial analysis of where on earth advanced embodied AI can be built, powered,
staffed, supplied — and permitted to work.

Two composites over 58 countries:

- **PAIRI** — OpenMind Physical AI Readiness Index. Capability to build and operate advanced
  embodied AI at scale. Six weighted pillars, 0–100, higher is better.
- **OLI** — Operating Latitude Index. How much room law, labour and public opinion
  leave an operator to deploy and run autonomous machines. 0–100, higher is more
  permissive. (Previously the Deployment Eagerness Index; identical scores.)
- **EFFECTIVE** — `PAIRI × (0.45 + 0.55 × OLI/100)`. Latitude-weighted near-term
  deployment potential.

For both indices, higher is better.

## Headline result

| # | Country | PAIRI | OLI | Effective |
|---|---------|------:|----:|----------:|
| 1 | China | 82.9 | 72 | 70.1 |
| 2 | Japan | 69.6 | 61 | 54.6 |
| 3 | United States | 69.0 | 48 | 49.3 |
| 4 | South Korea | 66.9 | 41 | 45.2 |
| 5 | Germany | 66.1 | 28 | 39.9 |
| 6 | Taiwan | 55.4 | 58 | 42.6 |
| 7 | France | 51.8 | 24 | 30.1 |
| 8 | Switzerland | 51.3 | 60 | 40.0 |
| 9 | Sweden | 50.6 | 27 | 30.3 |
| 10 | Italy | 50.5 | 17 | 27.4 |

## Contents

```
OpenMind_Physical_AI_Readiness_Index_2026.pdf   25-page preprint (two-column, REVTeX-style)
src/out/
  pairi_2026.csv           full dataset, 58 countries
  pairi_clusters_2026.csv  22 metro clusters, same six pillars
  pairi_uncertainty.csv    Monte Carlo intervals per country
maps/                                  PNG + SVG figures
  map_readiness      PAIRI choropleth
  map_latitude      OLI choropleth
  map_effective      latitude-weighted potential
  map_clusters       22 metro clusters, scored
  map_pillars        six-pillar small multiples
  chart_quadrant     capability vs latitude scatter
  chart_top25        pillar decomposition, top 25
  chart_uncertainty  published score and 90% interval, top 25
src/
  report.md          <- THE PROSE. Every word of the paper, front matter
                        (title, byline, abstract, keywords, colophon) in the
                        "::: front" block at the top, body below it.
  references.md      <- THE SOURCES. One keyed record each; format at the top
  build.py           one command: rebuilds data, figures, and both PDFs
  browser.py         locates headless Chrome for the PDF step
  geodata.py         fetches and caches the country boundaries for the maps
  front.py           parses the front-matter block (format documented at the top)
  refs.py            parses references.md and numbers the citations
  md_to_html.py      report.md -> report.html (syntax documented at the top)
  preprint.py        applies the two-column preprint layout and citations
  build_preprint.py  renders the preprint PDF
  build_index.py     dataset construction + index computation
  bootstrap.py       Monte Carlo uncertainty over the analyst-assigned inputs
  make_maps.py       all figures
METHODOLOGY.md       pillars, weights, normalisation, data-quality policy
```

## Pillars and weights

| Pillar | Weight | Core question |
|---|---:|---|
| Energy & grid | 15% | Is power abundant, cheap, reliable and *connectable*? |
| Compute & semiconductors | 15% | Training, edge inference, and the silicon inside a robot |
| Robotics & actuation | 25% | Integration capacity, OEMs, and the actuator supply chain |
| Materials & supply chain | 15% | Magnets, rare earths, cells, bearings, machine tools |
| Human capital & software | 20% | Robot-learning researchers *and* integration engineers |
| Demand pull | 10% | Shrinking workforce × high wages × industrial base |

Operating latitude is scored on four 25-point components: law, labour, public
opinion, and demonstrated autonomy permissiveness. 25 means maximally permissive
on that dimension.

## Editing the report

`src/report.md` is the only file that holds the report's words, and nothing in
the build overwrites it. Change a sentence there and rebuild:

```bash
uv run src/build.py report     # prose -> both PDFs, skipping data and figures
uv run src/build.py            # everything, including the index and the maps
```

The build writes everything to `src/out/` and then copies both PDFs to the
repo root and all eight figures (PNG and SVG) to `maps/`, so the top-level
artifacts are always the latest build rather than hand-placed copies. The PDFs are rendered by headless Chrome. Do not edit `report.html`, `report_preprint.html` or the PDFs: every build
regenerates them.

Two things to know when rewriting:

- The `::: front` block at the top of `report.md` holds the title, byline,
  abstract, keywords and colophon. Format is documented at the top of
  `src/front.py`; body syntax at the top of `src/md_to_html.py`.
- Citations live in the prose as keys, so you can rewrite any sentence freely
  and its sources travel with it:

  ```
  ... more than all other countries combined.[@ifr-world-robotics-2025]
  ... on both counts.[@iea-rare-earth-elements-2026; @adamas-2026]
  ```

  Numbers are assigned at build time in order of first appearance, so you never
  write one and never renumber. A key with no record in `references.md` stops
  the build and names the key. Renaming a key is a find-and-replace across the
  two files.

Watch the numbers the build reports. `citations: 89 sources cited at 101 points`
should only change when you mean it to. `links: 173 external, 124 internal`
means the reference URLs are still clickable in the PDF and the `[n]` markers
still jump to the bibliography; the build warns if either falls to zero.

## Adding a source

Add a record to `references.md` and cite its key from `report.md`:

```
[iea-rare-earth-elements-2026]
  International Energy Agency, *Rare Earth Elements*, IEA, Paris, April 2026.
  https://www.iea.org/reports/rare-earth-elements
  note: subscription        # optional; shown in italics after the address
```

A record that is never cited still appears, in a `Background sources` section at
the end of the bibliography.

## Reproducing

From a clean clone, one command does everything — about 80 seconds, most of it
the Monte Carlo:

```bash
uv run src/build.py
```

It creates `src/out/`, fetches the Natural Earth 50m admin-0 boundaries into
`src/data/` on first run (pinned to tag `v5.1.2`, so the maps do not change when
upstream edits a border), runs the index and the bootstrap, draws every figure,
and renders both PDFs. Both directories are derived and are not in version
control.

## Metro clusters

Twenty-two clusters scored on the same six pillars. Top ten:
Shenzhen–Dongguan–Guangzhou 87 · Shanghai–Suzhou–Hangzhou 86 · Tokyo–Kanagawa 80 ·
Seoul–Gyeonggi+Ulsan 78 · Beijing 74 · Hefei–Wuhu 72 · Nagoya–Toyota 71 ·
Hsinchu–Taichung–Taipei 70 · Bay Area 70 · Stuttgart–Karlsruhe 70.

`pairi_clusters_2026.csv` also carries `q36`, a separate qualitative rank on capacity to
build at volume within 36 months. It disagrees with the index in two informative places:
the Bay Area (3rd on q36, 9th on PAIRI) and Beijing (10th on q36, 5th on PAIRI).

## Caveats

Scores are analytical constructs, not measurements. Roughly 55% of the weighted
index rests on cited figures; the remainder are analyst scores anchored to
documented evidence, because the underlying data does not exist publicly — no
country publishes a count of robot system integrators, IFR publishes robot density
for only ~14 countries free, and sensor market shares are paywalled. Differences of
under about 9 points between countries carry no ordering
information — measured, not asserted, by a Monte Carlo (`bootstrap.py`) that models
correlated single-rater bias and resamples the pillar weights on every draw. Scores were
assigned by a single analyst with no second rater, and OpenMind has a commercial interest
in this subject; both are stated in the report. See §12 of the
report and `METHODOLOGY.md` for the full gap list.

Published by OpenMind, [openmind.com](https://openmind.com). Issued August 2026. Data current as of August 2026. Questions and corrections:
research@openmind.com.
