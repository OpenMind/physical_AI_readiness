"""Monte Carlo uncertainty on the analyst-assigned inputs.

About half the weighted index is analyst judgement rather than a cited figure,
and one analyst assigned all of it. The published scores give no sense of how
much that judgement could move them. This perturbs every analyst-assigned
input, re-runs the index thousands of times, and reports the distribution.

Perturbation model (stated as our honest uncertainty, not flattering error
bars). Three things matter and each is modelled:

  1. IDIOSYNCRATIC ERROR -- each analyst 0-100 score is noisy on its own.
  2. CORRELATED SINGLE-RATER BIAS -- one analyst scored every input, so error
     is correlated within a country: an analyst too generous to a country is
     too generous on all of its scores at once. Independent noise averages
     this away across twelve scores and six pillars, which understates rank
     uncertainty. We therefore decompose the total SD 10 per analyst score
     into a per-country bias b_c ~ N(0, 6) applied to ALL of that country's
     analyst scores in a draw, plus idiosyncratic N(0, 8) per score
     (6^2 + 8^2 = 10^2). OLI components (SD 3 total) decompose the same way:
     country bias N(0, 2) + idiosyncratic N(0, sqrt(5)).
  3. WEIGHTS -- the pillar weights are a choice, not a measurement. Each draw
     samples the six weights from a Dirichlet centred on the published vector
     (concentration 200, i.e. the 25% pillar varies with SD ~3 points), so the
     reported probabilities are not conditional on one hand-picked vector.

  estimated robot density   lognormal, SD 40% -- ONLY the ~44 countries IFR
                            does not publish; the 14 published values fixed
  supply-chain layer count  Gaussian, SD 0.7 of a layer
  cited hard data           NOT perturbed (generation, prices, MVA, wages,
                            AI investment, developer counts, demographics)

Separately, a named scenario: CHINA SOURCE HAIRCUT. The report's data-quality
corrections mostly run upward for China (excluded state capital, excluded
talent panels). The symmetric worry is that Chinese-sourced inputs -- shipment
counts, municipal output, company disclosures -- are inflated. The scenario
multiplies all of China's analyst scores and its installation count by 0.8 and
reports the ranking, so the reader can see whether rank 1 survives a 20%
haircut on everything China-sourced. (It does; see the output.)

Probabilities from N draws cannot distinguish 1.0 from 1 - 1/N, so anything
with zero exceedances is reported as ">0.999", never "1.000".
"""
import numpy as np, pandas as pd, build_index as B

RNG = np.random.default_rng(20260814)
N = 2000

IFR_PUBLISHED = {"KOR","SGP","DEU","JPN","SWE","DNK","SVN","USA","TWN","CHE","CAN","CHN","GBR","MEX"}

ANALYST_0_100 = ["grid_s","dc_s","chip_s","edge_s","oem_s","comp_s","hum_s",
                 "mag_s","cell_s","mach_s","soft_s","integ_s"]
OLI_PARTS = ["f_reg","f_lab","f_pub","f_dep"]
PILLARS = ["P1_energy","P2_compute","P3_robotics","P4_materials","P5_human","P6_demand"]
W0 = np.array([B.W[p] for p in PILLARS])          # published weight vector
CONC = 200                                        # Dirichlet concentration

SD_BIAS, SD_IDIO = 6.0, 8.0                       # 6^2 + 8^2 = 10^2
SD_OLI_BIAS, SD_OLI_IDIO = 2.0, np.sqrt(9 - 4)    # 2^2 + 5 = 3^2

base = B.compute(B.df_raw).sort_values("PAIRI", ascending=False)
names = B.df_raw["name"].values
iso = B.df_raw.index.values
nC = len(names)

pairi = np.zeros((N, nC)); oli = np.zeros((N, nC)); eff = np.zeros((N, nC))

BASE = B.df_raw.astype({c: float for c in ANALYST_0_100 + OLI_PARTS + ['rd', 'layers']})
EST = ~pd.Index(iso).isin(IFR_PUBLISHED)
BASELINE = B.compute(B.df_raw)

for k in range(N):
    d = BASE.copy()
    bias = RNG.normal(0, SD_BIAS, nC)                       # one per country
    for c in ANALYST_0_100:
        d[c] = np.clip(d[c] + bias + RNG.normal(0, SD_IDIO, nC), 0, 100)
    d.loc[EST, "rd"] = np.clip(d.loc[EST, "rd"] * RNG.lognormal(0, 0.40, EST.sum()), 0, 1400)
    d["layers"] = np.clip(d["layers"] + RNG.normal(0, 0.7, nC), 0, 7)
    obias = RNG.normal(0, SD_OLI_BIAS, nC)
    for c in OLI_PARTS:
        d[c] = np.clip(d[c] + obias + RNG.normal(0, SD_OLI_IDIO, nC), 0, 25)
    r = B.compute(d)
    w = RNG.dirichlet(W0 * CONC)                            # perturbed weights
    P = sum(wi * r[p] for wi, p in zip(w, PILLARS))
    pairi[k] = P.values
    oli[k] = (r.DEI if "DEI" in r else r.OLI).values
    eff[k] = (P * (0.45 + 0.55 * r.OLI / 100)).values

ranks = (-pairi).argsort(axis=1).argsort(axis=1) + 1
eranks = (-eff).argsort(axis=1).argsort(axis=1) + 1
pub_rank = (-BASELINE.PAIRI.values).argsort().argsort() + 1

out = pd.DataFrame({
    "iso": iso, "name": names,
    "PAIRI": BASELINE.PAIRI.values,
    "p05": np.percentile(pairi, 5, axis=0), "p95": np.percentile(pairi, 95, axis=0),
    "sd": pairi.std(axis=0),
    "rank": pub_rank,
    "rank_p05": np.percentile(ranks, 5, axis=0), "rank_p95": np.percentile(ranks, 95, axis=0),
    "eff": BASELINE.EFFECTIVE.values,
    "eff_p05": np.percentile(eff, 5, axis=0), "eff_p95": np.percentile(eff, 95, axis=0),
}).sort_values("PAIRI", ascending=False).round(2)
out.to_csv("out/pairi_uncertainty.csv", index=False)

idx = {n: i for i, n in enumerate(names)}


def P(a, b, arr):
    p = float((arr[:, idx[a]] > arr[:, idx[b]]).mean())
    return f"{min(p, 0.999):.3f}" if p in (0.0, 1.0) else f"{p:.2f}"


print(f"Monte Carlo, N={N}; correlated bias SD {SD_BIAS} + idiosyncratic SD {SD_IDIO}; "
      f"Dirichlet weights, concentration {CONC}\n")
print(out.head(14)[["name","PAIRI","p05","p95","sd","rank","rank_p05","rank_p95"]].to_string(index=False))

print("\n--- Probability the left country outranks the right, capability")
for a, b in [("China","Japan"),("China","United States"),("Japan","United States"),
             ("United States","South Korea"),("South Korea","Germany"),
             ("Germany","Taiwan"),("Taiwan","France"),("France","Switzerland")]:
    print(f"  P({a} > {b}) = {P(a,b,pairi)}")

print("\n--- Probability on effective deployment potential")
for a, b in [("China","Japan"),("Japan","United States"),("United States","South Korea"),
             ("Taiwan","Singapore"),("Singapore","Switzerland"),("Switzerland","Germany")]:
    print(f"  P({a} > {b}) = {P(a,b,eff)}")

pc1 = (ranks[:, idx['China']] == 1).mean()
pe1 = (eranks[:, idx['China']] == 1).mean()
top5 = np.mean([set(np.array(names)[np.argsort(-p)[:5]]) ==
                {'China','Japan','United States','South Korea','Germany'} for p in pairi])


def cap(p):
    return ">0.999" if p >= 1 - 1e-9 else f"{p:.3f}"


print("\n--- Stability of the headline claims")
print(f"  P(China ranks 1st on capability)          = {cap(pc1)}")
print(f"  P(China ranks 1st on effective potential) = {cap(pe1)}")
print(f"  P(top five = CHN/JPN/USA/KOR/DEU in any order) = {cap(top5)}")
print(f"  median |simulated rank - published rank|  = "
      f"{np.median(np.abs(ranks - pub_rank[None, :])):.2f} places")
print(f"  mean 90% PAIRI interval width = {np.mean(out.p95 - out.p05):.1f} points")

# ------------------------------------------------- SCENARIO: China source haircut
d = BASE.copy()
chn = d.index == "CHN"
for c in ANALYST_0_100:
    d.loc[chn, c] = d.loc[chn, c] * 0.8
d.loc[chn, "inst_k"] = d.loc[chn, "inst_k"] * 0.8
r = B.compute(d)
s = r.sort_values("PAIRI", ascending=False).reset_index()
crow = s[s.name == "China"].index[0] + 1
print(f"\n--- Scenario: all China analyst scores and installations x0.8")
print(f"  China PAIRI {r.loc['CHN','PAIRI']:.1f} (published 82.9), rank {crow} of {len(s)}; "
      f"margin over {s.name[1] if crow == 1 else s.name[0]}: "
      f"{s.PAIRI[0]-s.PAIRI[1]:.1f} points")
