# Methodology

OpenMind Physical AI Readiness Index 2026. Data current as of August 2026.

## 1. Scope

"Physical AI" means machines that perceive, decide and act in the physical world
under learned rather than scripted control: humanoid and legged robots,
general-purpose manipulators, autonomous mobile robots and vehicles, and the
autonomous end of conventional industrial automation.

The operative question: *if an operator wanted to deploy ten thousand capable
general-purpose robots in a country within five years, what would have to be true of
that country?*

58 countries are scored. Coverage was chosen to include every economy with a
plausible role in building, supplying or absorbing physical AI at scale, plus a
representative set of large developing economies for contrast.

## 2. Index construction

Each country receives six pillar scores on 0–100, combined with fixed weights into
PAIRI. Within pillars, indicators are min–max normalised across the panel, with
winsorising bounds where one country would otherwise compress the scale, and
log-transformed where the distribution spans orders of magnitude (electricity
generation, robot installations, manufacturing value added, AI investment, developer
counts, wages).

Aggregation is a simple weighted arithmetic mean. No compensatory penalties, no
geometric aggregation. The pillars substitute for one another at the margin, and a
more elaborate functional form would imply precision the inputs cannot support.

### 2.1 Pillar 1 — Energy & grid (15%)

| Sub-indicator | Weight | Transform | Source |
|---|---:|---|---|
| Total electricity generation, TWh, 2025 | 30% | log, min–max | Ember Yearly Electricity Data |
| Electricity demand per capita, kWh | 20% | min–max, 200–20,000 | Ember |
| Net installed capacity growth, % YoY | 20% | min–max, 0–15% | Ember |
| Industrial electricity price, USD/kWh | 20% | min–max inverted, $0.05–0.30 | EIA, Eurostat nrg_pc_205, GlobalPetrolPrices, DESNZ |
| Grid reliability & headroom | 10% | analyst score | World Bank Enterprise Surveys, SAIDI, LBNL/NERC queue data |

Note on capacity: the `cap_g` column is a **net** measure (additions minus
retirements), so it is systematically lower than headline gross new-build figures.
China's +16.7% and the US's +3.0% are both net. Gross utility-scale US additions in
2025 were about 53 GW (EIA); China's total installed capacity reached 3,890 GW
(NEA), an increase of roughly 540 GW.

### 2.2 Pillar 2 — Compute & semiconductors (15%)

| Sub-indicator | Weight | Source |
|---|---:|---|
| Wafer fab capacity share, % of global | 25% | SEMI World Fab Forecast 2025 (regional where national unavailable) |
| Datacentre / AI compute presence | 30% | analyst score: Epoch AI, Synergy, JLL, C&W, EUDCA, national programmes |
| Advanced AI silicon access | 20% | analyst score: US BIS control status, Commerce licences |
| Edge silicon & sensor manufacture | 25% | analyst score: automotive MCU/power semi share, sensor makers, OSAT |

Raw datacentre MW is deliberately **not** used: European figures (EUDCA/Pb7, 2024
baseline, 50 kW+ threshold) and APAC/Americas figures (metro colocation inventory
excluding hyperscale self-build) are not comparable, and mixing them biases heavily
against the US and China.

### 2.3 Pillar 3 — Robotics & actuation (25%)

| Sub-indicator | Weight | Source |
|---|---:|---|
| Industrial robot density per 10k mfg employees | 18% | IFR World Robotics 2025 (14 countries); analyst estimate otherwise |
| 2024 installations, thousands | 14% | IFR (log) |
| Domestic robot OEM capability | 20% | analyst score: OEM presence, market share, export share |
| Component supply depth | 24% | analyst score: reducers, screws, motors, bearings, encoders, F/T sensors, hands |
| Humanoid programme strength | 10% | analyst score: shipped units, funded programmes, announced-vs-actual |
| Manufacturing value added, USD bn | 14% | World Bank WDI NV.IND.MANF.CD (log) |

**Critical caveat.** IFR revised China's manufacturing-employment denominator in
World Robotics 2025. China reads 470/10,000 on the old basis and 166 on the new one;
the global average fell 162 → 132 for the same reason. Cross-vintage comparison is
invalid. This index uses the 2024 basis throughout.

### 2.4 Pillar 4 — Materials & supply chain (15%)

| Sub-indicator | Weight | Source |
|---|---:|---|
| Supply-chain layers held at scale, 0–7 | 22% | derived: RE mining, RE separation, metal/alloy, magnets, cells, CAM/AAM, precision mechanics |
| Magnet & rare-earth position | 34% | analyst score: IEA Rare Earth Elements, USGS MCS 2026, Adamas |
| Battery cell & component position | 20% | analyst score: IEA GEVO 2026, Benchmark, SNE Research |
| Machine tools, bearings, precision mechanics | 24% | analyst score: Gardner, CECIMO, ITIF, company disclosures |

Magnets carry the heaviest sub-weight because they are the demonstrable constraint:
94% of world sintered rare-earth permanent magnet manufacture and 91% of rare earth
refining are Chinese (IEA, 2024 data), heavy-rare-earth processing capacity is
estimated at 99%+, and export licensing has been discretionary since April 2025.

### 2.5 Pillar 5 — Human capital & software (20%)

| Sub-indicator | Weight | Source |
|---|---:|---|
| AI authors & inventors per 100k population | 14% | Stanford AI Index 2026 ch.1 |
| AI private investment 2025, USD bn | 16% | Stanford AI Index 2026 ch.4 (log) |
| Developers, millions | 14% | GitHub Octoverse 2025 (log) |
| Natural science + engineering share of graduates | 8% | UNESCO UIS / World Bank |
| Robotics software / foundation-model capability | 24% | analyst score |
| Integration & skilled-trades capacity | 24% | analyst score: robot density, documented shortages, integrator base |

Integration capacity is weighted equally with software capability because the two
stocks are decoupling and the integration stock is the binding one. This is a
deliberate departure from conventional AI-readiness indices.

**China correction.** The AI Index author/inventor panel is LinkedIn-derived and
excludes China entirely; GitHub structurally undercounts it. Uncorrected, a naive
composite zeroes out the world's second-largest AI workforce. This index applies a
documented correction to China's `ai100k` and `dev_m` inputs. China's `ai_inv`
figure of $12.4bn also excludes an estimated ~$184bn of state guidance-fund capital
deployed 2000–2023.

### 2.6 Pillar 6 — Demand pull (10%)

| Sub-indicator | Weight | Source |
|---|---:|---|
| Working-age (25–64) change 2025→2040, % | 45% | UN WPP 2024, inverted (shrinking = higher pull) |
| Manufacturing wage, USD/month | 35% | Eurostat, ILO, national statistics (log) |
| Manufacturing value added, USD bn | 20% | World Bank WDI (log) |

## 3. Operating Latitude Index

Four components, 25 points each, higher = more permissive. Each is the inverse of a
friction input recorded in the build script.

- **Law** — comprehensive AI law status, machinery and product-liability regimes,
  and whether an applicable safety standard exists at all.
- **Labour** — union density, collective bargaining coverage, works council rights,
  employment protection, and **sectoral union concentration in deploying
  industries**, which the evidence shows matters far more than aggregate density.
- **Public** — survey-measured excitement, concern and institutional trust (Ipsos AI
  Monitor 2025, Pew 2025, Stanford AI Index ch.9, Eurobarometer, Edelman 2026).
- **Autonomy** — demonstrated willingness to permit driverless and autonomous
  operation. **Scored on civil deployment only.** Where military and civil latitude
  diverge, the civil case governs. Ukraine is the extreme instance: it operates more
  autonomous machines than any country on earth and scores 5 of 25 here, because
  wartime military permissiveness is out of scope. See report §7.1.

## 4. Effective Deployment Potential

```
EFFECTIVE = PAIRI × (0.45 + 0.55 × OLI/100)
```

The 0.55 coefficient encodes a judgement: reluctance delays deployment and raises its
cost without preventing it, so a country at zero latitude still keeps 45% of its
capability. **This is the single most arguable number in the analysis.**
Setting it to 0.35 or 0.75 materially reorders the middle of the table. Both raw
components ship in the dataset so anyone can recompute.

## 5. Data quality policy

Three classes of input:

- **CITED** — direct from a named source with a year. Electricity generation,
  prices, IFR robot density where published, manufacturing value added, AI authors
  per capita, AI investment, working-age projections, wages, union density.
- **DERIVED** — computed from cited inputs (supply-chain layer counts, per-capita
  ratios, index scores).
- **ESTIMATED** — analyst scores anchored to documented qualitative evidence.
  Component supply depth, robotics software capability, integration capacity, edge
  silicon tier, datacentre presence, and robot density for the ~40 countries IFR
  does not publish free.

Roughly **55% of the weighted index rests on cited numbers, 45% on anchored analyst
scores.** No figure in this project is invented; every estimate is anchored to
evidence documented in the research record.

## 6. Known gaps

1. **Robot density is unavailable for ~40 of 58 countries.** IFR publishes 13–14
   values free; the full table is a paid report. Estimates are ordinal, not cardinal.
2. **No country publishes a count of robot system integrators.** Not IFR, A3, VDMA
   or JARA. This is plausibly the most important missing statistic in the field.
3. **Datacentre capacity is not comparable across regions** (see §2.2).
4. **Country-level AI accelerator stock below the US/China/Korea tier is not
   resolvable.** Epoch's dataset covers 10–20% of global AI compute and ~2% of
   China's export-controlled chips, by its own caveat.
5. **Sensor market shares are paywalled** (Yole, TechInsights) for CMOS image
   sensors, IMUs, force/torque sensors and encoders. Lidar is the exception.
6. **STEM graduate absolutes are 2020-vintage**; UNESCO field shares mostly
   2016–2019.
7. **OECD EPL values were not retrievable**; latest vintage appears to be 2019.
   Union density is largely 2018 ICTWSS.
8. **Robotics conference country breakdowns** (ICRA, IROS, CoRL, RSS) are not
   published.
9. **Country-level battery cell capacity in GWh** exists only inside Benchmark and
   BNEF subscriptions.
10. **Ukraine** has no usable post-2022 energy data, and its score measures sustained
    general-purpose industrial capacity under peacetime conditions rather than its
    uncrewed-systems industry, which leads the world on volume and iteration speed.
    The index has no indicator for iteration velocity, which report §7.1 argues is a
    variable independent of the six pillars. **Taiwan** is absent from World
    Bank manufacturing value added. **Russia's** nominal capacity overstates what is
    practically accessible under sanctions.
11. **China** is measured unevenly, and the unevenness is not symmetric. The pillars
    carrying its margin — energy, robotics and actuation, materials — rest on
    quantities counted independently outside China (IFR, Ember, IEA, USGS, SEMI,
    audited supplier filings) and are among the best-evidenced inputs in the index.
    The weakness is in human capital and software (20% of weight), where talent
    panels exclude China, GitHub undercounts it, and disclosed AI investment omits
    state guidance-fund capital. Uncorrected, each of those gaps understates China;
    the corrections applied here reduce but do not eliminate the residual, which
    therefore still runs low rather than high. Countervailing risks — announced
    versus actual capacity, and the robot-density denominator revision — are handled
    by scoring shipped units and by using the 2024 density basis throughout.

## 7. Uncertainty from the analyst-assigned inputs

`src/bootstrap.py` perturbs every analyst-assigned input and re-runs the index 2,000
times, writing `pairi_uncertainty.csv`. Because a single analyst assigned every score,
the error model allows for correlated bias, not just noise: each draw shifts all of a
country's analyst scores together by a per-country bias term (SD 6) plus idiosyncratic
noise per score (SD 8), totalling SD 10 per score; operating-latitude components are
split the same way (country term SD 2 + component noise, total SD 3). Each draw also
resamples the six pillar weights from a Dirichlet centred on the published vector
(concentration 200, so the 25% pillar varies with SD ≈ 3 points), making the reported
probabilities robust to the weighting choice as well as the scoring. Estimated robot
density (44 of 58 countries) moves lognormally by SD 40%, with IFR's 14 published values
held fixed; the supply-chain layer count by SD 0.7. Cited hard data is not perturbed.

An earlier version of this analysis perturbed the analyst scores independently, which
averaged single-rater bias away across a country's twelve scores and produced intervals
roughly half as wide (±2.2) and several probabilities of exactly 1.000. The correlated
model is the honest one, and the numbers below supersede the earlier ones.

Results:

| Quantity | Value |
|---|---|
| Mean 90% interval on PAIRI | 9.4 points (about ±4.7) |
| Median rank movement vs published rank | ~2 places |
| P(China 1st on capability) | >0.999 (no exceedance in 2,000 draws) |
| P(China 1st on effective potential) | 0.994 |
| P(top five identity unchanged) | 0.987 |
| P(Japan > United States, capability) | 0.54 — a tie |
| P(Japan > United States, effective) | 0.83 |
| P(South Korea > Germany) | 0.56 — a tie |
| P(France > Switzerland) | 0.55 — a tie |
| P(Taiwan > Singapore, effective) | 0.51 — no information |
| P(Switzerland > Germany, effective) | 0.47 — the published 7th/8th ordering is a coin flip |

A separate named scenario multiplies every China analyst score and its installation
count by 0.8, on the theory that Chinese-sourced figures (shipments, municipal output,
company disclosures) might be systematically inflated. China's PAIRI falls from 82.9 to
74.2 and it remains 1st, 4.6 points ahead of Japan. The report's data-quality
corrections for China otherwise run upward (excluded state capital, excluded talent
panels); this scenario is the downward test.

**Use about 9 points as the threshold below which a gap carries no ordering
information.** No probability is reported as 1.000: with 2,000 draws, zero exceedances
bounds a model-conditional probability only above 0.999.

## 8. Weight sensitivity

| Variant | Effect |
|---|---|
| Robotics 25% → 15%, redistributed to compute and human capital | US moves to 2nd above Japan; China's lead over 2nd narrows from 13.3 to 10.9 points; top five unchanged |
| Demand pull dropped, weights renormalised | Italy −3.7, Korea −2.3, Germany −2.2, Japan −1.1, India +1.0; order of top five unchanged |
| Latitude coefficient 0.55 → 0.35 | Germany rises to 49.5 effective, reordering the 5–12 band |
| Latitude coefficient 0.55 → 0.75 | Italy falls below Vietnam |

The ranking is robust to plausible reweighting — and since the Monte Carlo now
resamples weights on every draw, the §7 probabilities already include this
sensitivity rather than treating it separately. **The margins are not robust.**
Differences of several points between adjacent countries are inside the noise.

## 9. Verification

Twelve load-bearing claims were independently re-verified against primary sources
after drafting. Ten confirmed as stated; two were corrected in the final text:

- US 2025 capacity additions were restated from a net Ember figure to EIA's ~53 GW
  of gross utility-scale additions, and capacity figures were re-attributed from
  Ember to NEA and EIA.
- "No robot tax has been enacted anywhere" was narrowed to "no jurisdiction has
  enacted a *direct* tax on robots", noting South Korea's 2017 reduction of the
  automation-investment tax deduction.

Attribution was also tightened on the heavy-rare-earth 99% figure (industry
estimates, not IEA) and the Harmonic Drive market share (restated as a 71–85%
range across trade sources, since no audited figure exists).

### 9.1 Locator check

Every one of the 116 reference locators has been retrieved and checked against
the work it claims to point to. All 116 resolve.

The first pass was automated. Nine locators returned 404 and were replaced with
the publisher's current canonical address. One pointed at the wrong document
entirely — the ISO page cited for ISO/CD 25785-1 (legged-robot safety) resolved
to ISO/DIS 17846, a welding-equipment labelling draft — and now points at
ISO/CD 25785-1. Six could not be fetched automatically, because of robots.txt,
bot filtering, or a JavaScript-rendered data browser.

Those six were then checked by hand, which is how the remaining errors were
found: OICA had restructured its site and dropped the cited path, and the Estun
investor page had moved. Both were replaced. One further URL had failed
automated retrieval only through a transient server error. The last three —
Eurostat's electricity-price data browser, the German Betriebsverfassungsgesetz
on gesetze-im-internet, and a Ukrainska Pravda article — refuse automated
requests but load normally in a browser, and were confirmed manually.

The lesson is recorded rather than smoothed over: automated link checking
cleared 113 of 116 locators and left three it could not judge, and two of the
six it could not fetch were in fact broken. A machine check is a filter, not a
guarantee.

The check also corrected two citations rather than their URLs: the UBTech FY2025
results announcement is dated March 2026, not April; and the German
skilled-worker statistics are published by KOFA, a project of the Institut der
deutschen Wirtschaft Köln, not by the Bundesagentur für Arbeit.

Locators in the PDF are live link annotations, and each inline [n] marker links
to its own bibliography entry.

## 10. Metro cluster scores

Twenty-two clusters are scored on the same six pillars and the same weights, at metro
rather than national resolution. Scores are analyst-assigned, built on the national
pillar baseline and adjusted for documented cluster-level evidence (anchor firms,
facility announcements, funding rounds, output statistics, and named local
constraints). No equivalent to IFR exists at metro resolution, so the cluster ranking
should be read as ordinal.

`pairi_clusters_2026.csv` also carries a `q36` column: a separate qualitative rank on
capacity to design, build and deploy advanced robots at volume within 36 months. It
weights demonstrated throughput and supply-chain control over research prestige and
valuation, and it disagrees with the index in two informative places — the Bay Area
(3rd on q36, 9th on PAIRI) and Beijing (10th on q36, 5th on PAIRI).

## 11. Naming

The capability index is the **OpenMind Physical AI Readiness Index (PAIRI)**.

Its companion has been renamed twice, and earlier numbers convert cleanly:

1. It began as a **Deployment Friction Index (DFI)**, scored so that high meant *more*
   resistance.
2. It was then flipped to a **Deployment Eagerness Index (DEI)**, so that high meant
   *more* willing and both indices pointed the same way. `DEI = 100 − DFI`.
3. It is now the **Operating Latitude Index (OLI)** — same definition, same polarity,
   same components. `OLI = DEI`. The rename avoids collision with the unrelated and
   widely used DEI acronym, which in a report touching on labour policy would invite
   misreading.

"Operating latitude" means the room a jurisdiction gives an operator to deploy and run
autonomous machines. Where the text needs to avoid confusion with geographic latitude it
says "operating latitude" in full.

## 12. Document formats

The report is issued as a two-column preprint (Latin Modern Roman, REVTeX-style section
numbering, `FIG.`/`TABLE` captions, 102 numbered references with inline citations). The
prose is in `src/report.md`; `src/preprint.py` converts it into preprint layout,
inserts the citation apparatus, and emits `report_preprint.html`; `src/build_preprint.py`
embeds the figures and renders the PDF via headless Chromium.

## 13. Competing interests and authorship

OpenMind builds products in the physical AI sector and therefore has a commercial
interest in the subject of this index. Mitigations, offered rather than claimed to be
sufficient: the full dataset and the code producing every figure are published, so a
reader can substitute their own weights or scores; §7 above quantifies how far the
analyst judgements could move the result, including the orderings that do not survive;
and §6 lists the gaps.

Country and cluster scores were assigned by a **single analyst**. There was no second
rater and no inter-rater reliability statistic. A different analyst working from the
same evidence would produce different numbers; §7 bounds how different, but does not
substitute for the missing second opinion.

No external party funded, commissioned or reviewed this report.
