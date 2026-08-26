"""Maps and charts for the OpenMind Physical AI Readiness Index 2026."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.colors import ListedColormap, BoundaryNorm
import geopandas as gpd
import geodata, pandas as pd, numpy as np

SURFACE, INK, INK2, INK3 = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8880"
NODATA, BORDER, GRID = "#e8e7e3", "#fcfcfb", "#eceae5"
BLUE   = ["#cde2fb","#9ec5f4","#6da7ec","#3987e5","#256abf","#184f95","#0d366b"]
ORANGE = ["#fbe0d2","#f7bb99","#f29464","#eb6834","#c9501f","#9e3c14","#71290b"]
plt.rcParams.update({
    "font.family": "DejaVu Sans", "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "text.color": INK, "axes.labelcolor": INK2,
    "axes.edgecolor": "#d8d7d2", "xtick.color": INK2, "ytick.color": INK2, "font.size": 9})

df = pd.read_csv("out/pairi_2026.csv")
cl = pd.read_csv("out/pairi_clusters_2026.csv")
world = gpd.read_file(geodata.path())
world["iso"] = world["ISO_A3_EH"].where(world["ISO_A3_EH"] != "-99", world["ADM0_A3"])
world = world[world.NAME != "Antarctica"].to_crs("ESRI:54030")

# small territories that vanish at world scale but matter here -> dot markers
SMALL = ["SGP","TWN","KOR","JPN","ISR","ARE","QAT"]
SMALL_NM = {"SGP":"Singapore","TWN":"Taiwan","KOR":"S. Korea","JPN":"Japan",
            "ISR":"Israel","ARE":"UAE","QAT":"Qatar"}
EUROPE = ["DEU","FRA","GBR","ITA","ESP","NLD","BEL","CHE","AUT","SWE","NOR","DNK","FIN",
          "POL","CZE","SVK","HUN","ROU","SVN","EST","IRL","PRT","GRC","TUR","UKR","BGR"]


def band_color(v, bins, ramp):
    if pd.isna(v): return NODATA
    for i in range(len(bins) - 1):
        if v < bins[i + 1] or i == len(ramp) - 1: return ramp[i]
    return ramp[-1]


def render(col, bins, labels, ramp, title, subtitle, legend_title, fname,
           panel_title, ascending=False, note=""):
    fig = plt.figure(figsize=(16.5, 9.4))
    fig.text(0.022, 0.955, title, fontsize=19, fontweight="bold", color=INK, va="top")
    fig.text(0.022, 0.906, subtitle, fontsize=10.5, color=INK2, va="top")
    ax = fig.add_axes([0.005, 0.075, 0.755, 0.80]); ax.set_axis_off()

    g = world.merge(df[["iso", col, "name"]], on="iso", how="left")
    cmap, norm = ListedColormap(ramp), BoundaryNorm(bins, len(ramp))
    g[g[col].isna()].plot(ax=ax, color=NODATA, edgecolor=BORDER, linewidth=0.25)
    g[g[col].notna()].plot(ax=ax, column=col, cmap=cmap, norm=norm,
                           edgecolor=BORDER, linewidth=0.3)
    xr = ax.get_xlim()[1] - ax.get_xlim()[0]

    # dot markers + leader labels for small states, placed around the map edge
    place = {"SGP":(0.720,0.205),"TWN":(0.905,0.405),"KOR":(0.905,0.545),
             "JPN":(0.905,0.640),"ISR":(0.612,0.345),"ARE":(0.612,0.300),
             "QAT":(0.612,0.255)}
    for iso in SMALL:
        r = g[g.iso == iso]
        if r.empty or pd.isna(r[col].iloc[0]): continue
        pt = r.geometry.iloc[0].representative_point()
        v = r[col].iloc[0]
        ax.plot(pt.x, pt.y, "o", ms=5.4, mfc=band_color(v, bins, ramp), mec="#3a3937",
                mew=0.8, zorder=6)
        tx, ty = place[iso]
        ax.annotate(f"{SMALL_NM[iso]} {v:.0f}", xy=(pt.x, pt.y), xycoords="data",
                    xytext=(tx, ty), textcoords="axes fraction", fontsize=7.4, color=INK2,
                    ha="left", va="center", zorder=7,
                    bbox=dict(boxstyle="round,pad=0.2", fc=SURFACE, ec="none", alpha=0.9),
                    arrowprops=dict(arrowstyle="-", color="#b6b4ae", lw=0.6,
                                    shrinkA=0, shrinkB=3))

    def numlabel(axis, gdf, isos, fs, minarea, extent):
        for iso in isos:
            r = gdf[gdf.iso == iso]
            if r.empty or pd.isna(r[col].iloc[0]): continue
            geom = max(r.geometry.iloc[0].geoms, key=lambda p: p.area) if \
                   r.geometry.iloc[0].geom_type == "MultiPolygon" else r.geometry.iloc[0]
            if geom.area / (extent ** 2) < minarea: continue
            pt = geom.representative_point()
            v = r[col].iloc[0]
            idx = min(int(np.searchsorted(bins, v, "right")) - 1, len(ramp) - 1)
            axis.text(pt.x, pt.y, f"{v:.0f}", fontsize=fs, ha="center", va="center",
                      color="#ffffff" if idx >= 4 else "#22211f", fontweight="bold", zorder=5)

    # in-map value labels for the large economies
    numlabel(ax, g, ["CHN","USA","IND","BRA","RUS","CAN","AUS","MEX","IDN","SAU",
                     "ZAF","VNM","THA","ARG","EGY","NGA","PAK","KAZ","MYS","PHL","NZL",
                     "CHL","COL","MAR","KEN","BGD","TUR","UKR","ESP","FRA","DEU","SWE",
                     "NOR","FIN","POL","ITA","GBR","ROU"], 7.6, 0.0016, xr)

    # Europe inset — Europe is unreadable at world scale
    fig.patches.append(Rectangle((0.018, 0.128), 0.212, 0.352, transform=fig.transFigure,
                                 facecolor=SURFACE, edgecolor="#dcdbd6", lw=0.8, zorder=4))
    iax = fig.add_axes([0.022, 0.132, 0.204, 0.320], zorder=5)
    iax.set_axis_off(); iax.patch.set_alpha(0)
    eu = g[g.iso.isin(EUROPE) | g[col].isna()].cx[-1.35e6:3.1e6, 4.0e6:8.1e6]
    base = g.cx[-1.35e6:3.1e6, 4.0e6:8.1e6]
    base[base[col].isna()].plot(ax=iax, color=NODATA, edgecolor=BORDER, linewidth=0.3)
    base[base[col].notna()].plot(ax=iax, column=col, cmap=cmap, norm=norm,
                                 edgecolor=BORDER, linewidth=0.45)
    iax.set_xlim(-1.35e6, 3.1e6); iax.set_ylim(4.0e6, 8.1e6)
    exr = 4.45e6
    numlabel(iax, base, EUROPE, 6.6, 0.00045, exr)
    iax.text(0.0, 1.015, "Europe detail", transform=iax.transAxes, fontsize=8,
             color=INK2, fontweight="bold")


    # legend
    x0, y0, w, h = 0.028, 0.028, 0.030, 0.026
    fig.text(x0, y0 + h + 0.030, legend_title, fontsize=8.6, color=INK2, fontweight="bold")
    for i, (c, lab) in enumerate(zip(ramp, labels)):
        fig.patches.append(Rectangle((x0 + i * (w + 0.003), y0), w, h,
                           transform=fig.transFigure, facecolor=c, edgecolor="none"))
        fig.text(x0 + i * (w + 0.003) + w / 2, y0 - 0.016, lab, fontsize=7.2,
                 color=INK2, ha="center", va="top")
    nx = x0 + len(ramp) * (w + 0.003) + 0.012
    fig.patches.append(Rectangle((nx, y0), w, h, transform=fig.transFigure,
                                 facecolor=NODATA, edgecolor="none"))
    fig.text(nx + w / 2, y0 - 0.016, "n/a", fontsize=7.2, color=INK3, ha="center", va="top")
    fig.text(0.42, y0 + 0.012, note or "Numbers in map = index score. Dots mark small "
             "states enlarged for visibility. Grey = outside the 58-country panel.",
             fontsize=7.4, color=INK3, va="center")

    # ranked side panel
    pax = fig.add_axes([0.775, 0.055, 0.215, 0.845]); pax.set_axis_off()
    pax.set_xlim(0, 1); pax.set_ylim(0, 1)
    pax.text(0, 0.995, panel_title, fontsize=9.6, fontweight="bold", color=INK, va="top")
    top = df.sort_values(col, ascending=ascending).head(24).reset_index(drop=True)
    for i, r in top.iterrows():
        y = 0.955 - i * 0.0392
        pax.add_patch(Rectangle((0, y - 0.019), 0.052, 0.024,
                      facecolor=band_color(r[col], bins, ramp), edgecolor="none"))
        pax.text(0.115, y - 0.007, f"{i+1}", fontsize=7.4, color=INK3, ha="right",
                 va="center")
        pax.text(0.145, y - 0.007, r["name"], fontsize=8.3, color=INK, va="center")
        pax.text(1.0, y - 0.007, f"{r[col]:.1f}", fontsize=8.3, color=INK2, ha="right",
                 va="center", fontweight="bold")
    fig.savefig(f"out/{fname}.png", dpi=200)
    fig.savefig(f"out/{fname}.svg")
    plt.close(fig)


render("PAIRI", [0, 20, 30, 40, 50, 60, 70, 101],
       ["<20","20–30","30–40","40–50","50–60","60–70","70+"], BLUE,
       "OpenMind Physical AI Readiness Index 2026",
       "Composite capability to build and operate advanced embodied AI at scale — energy and grid, "
       "compute and semiconductors, robotics and\nactuation base, materials supply chain, human "
       "capital and software, demand pull.  58 countries scored.",
       "PAIRI score (0–100)", "map_readiness", "Ranked — top 24")

render("OLI", [0, 25, 35, 45, 55, 65, 75, 101],
       ["<25","25–35","35–45","45–55","55–65","65–75","75+"], ORANGE,
       "Operating Latitude Index 2026",
       "How willing a place is to let physical AI actually operate. Higher means faster, less contested "
       "deployment: AI and machinery\nlaw · unions, works councils and sectoral bargaining · public "
       "sentiment · demonstrated autonomy permissiveness. Four components, 25 points each.",
       "OLI score (higher = more permissive)", "map_latitude",
       "Most permissive — top 24",
       note="Numbers in map = OLI score. Components scored 0–25 each. "
            "Dots mark small states enlarged for visibility.")

render("EFFECTIVE", [0, 12, 18, 24, 30, 40, 50, 101],
       ["<12","12–18","18–24","24–30","30–40","40–50","50+"], BLUE,
       "Effective Deployment Potential 2026",
       "Readiness weighted by latitude: where advanced physical AI is most likely to be operating "
       "at scale within five years.\nEFFECTIVE = PAIRI × (0.45 + 0.55 × OLI/100).",
       "Effective score (0–100)", "map_effective", "Ranked — top 24")

# ------------------------------------------------- CHART: capability × friction
fig, ax = plt.subplots(figsize=(11.5, 8.4))
d = df[df.PAIRI > 22].copy()
QXLO, QXHI, QYLO, QYHI = 20, 92, 5, 92        # axis limits, set at the end
# "build it and run it": both indices above 50. Drawn as a patch in DATA
# coordinates -- axvspan's ymin/ymax are axes fractions, not data, which is why
# this quadrant used to start at 48.5 while the divider line sat at 50.
ax.add_patch(Rectangle((50, 50), QXHI - 50, QYHI - 50, facecolor="#f2f8ff",
                       edgecolor="none", zorder=0))
ax.axhline(50, color="#d8d7d2", lw=1, zorder=1)
ax.axvline(50, color="#d8d7d2", lw=1, zorder=1)
ax.scatter(d.PAIRI, d.OLI, s=np.clip(np.log10(d.mva_bn.clip(lower=5)) * 62 - 60, 26, 400),
           c="#2a78d6", alpha=0.72, linewidths=1.4, edgecolors=SURFACE, zorder=3)
lab = {"CHN":-1,"USA":1,"JPN":-1,"KOR":1,"DEU":1,"TWN":-1,"SGP":-1,"FRA":1,"ITA":1,
       "CHE":-1,"IND":-1,"GBR":1,"SWE":1,"NLD":-1,"CAN":1,"ISR":-1,"ARE":-1,"BRA":1,
       "AUS":1,"POL":-1,"ESP":-1,"MYS":-1,"SAU":1,"THA":1,"VNM":1,"IDN":-1,"MEX":1,
       "IRL":-1,"DNK":-1,"AUT":1,"CZE":-1,"NOR":1,"FIN":-1,"BEL":1,"RUS":-1,"TUR":1}
for iso, s in lab.items():
    r = d[d.iso == iso]
    if r.empty: continue
    ax.text(r.PAIRI.iloc[0], r.OLI.iloc[0] + s * 1.9, r["name"].iloc[0], fontsize=7.6,
            ha="center", va="bottom" if s > 0 else "top", color=INK)
ax.set_xlabel("OpenMind Physical AI Readiness Index  →  capability to build", fontsize=10.5)
ax.set_ylabel("Operating Latitude Index  →  willingness to deploy", fontsize=10.5)
ax.set_title("Who can build it, and who wants it", fontsize=16, fontweight="bold",
             loc="left", pad=30)
ax.text(0, 1.015, "Bubble area ∝ manufacturing value added. Most countries that can build physical "
        "AI are reluctant to deploy it, and\nmost permissive countries cannot build it. China and the Gulf "
        "break the pattern from opposite ends.", transform=ax.transAxes, fontsize=9.8, color=INK2,
        va="bottom")
for x, y, t, c, ha, va in [(0.985,0.975,"BUILD IT AND RUN IT","#256abf","right","top"),
                           (0.985,0.025,"BUILD IT, FIGHT OVER IT","#9e3c14","right","bottom"),
                           (0.015,0.025,"NEITHER",INK3,"left","bottom"),
                           (0.015,0.975,"EAGER, NOT YET CAPABLE",INK3,"left","top")]:
    ax.text(x, y, t, transform=ax.transAxes, fontsize=8.2, color=c, fontweight="bold",
            ha=ha, va=va)
ax.set_xlim(QXLO, QXHI); ax.set_ylim(QYLO, QYHI)
ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig("out/chart_quadrant.png", dpi=200)
plt.savefig("out/chart_quadrant.svg"); plt.close()

# ------------------------------------------------ CHART: top 25 pillar stack
P  = ["P1_energy","P2_compute","P3_robotics","P4_materials","P5_human","P6_demand"]
PN = ["Energy & grid (15%)","Compute & semiconductors (15%)","Robotics & actuation (25%)",
      "Materials & supply chain (15%)","Human capital & software (20%)","Demand pull (10%)"]
WT = [.15,.15,.25,.15,.20,.10]
STACK = ["#cde2fb","#9ec5f4","#3987e5","#256abf","#184f95","#0d366b"]
t = df.nlargest(25, "PAIRI").iloc[::-1]
fig, ax = plt.subplots(figsize=(11.5, 10))
left = np.zeros(len(t))
for p, n, w, c in zip(P, PN, WT, STACK):
    v = t[p].values * w
    ax.barh(t["name"], v, left=left, color=c, label=n, height=0.68,
            edgecolor=SURFACE, linewidth=1.6)
    left += v
for i, s in enumerate(t.PAIRI):
    ax.text(s + 1.2, i, f"{s:.1f}", va="center", fontsize=8.4, color=INK, fontweight="bold")
ax.set_xlim(0, 92); ax.set_xlabel("Weighted PAIRI contribution", fontsize=10.5)
ax.set_title("OpenMind Physical AI Readiness Index 2026 — top 25", fontsize=16, fontweight="bold",
             loc="left", pad=26)
ax.text(0, 1.012, "Pillar contributions, each already multiplied by its index weight.",
        transform=ax.transAxes, fontsize=9.8, color=INK2, va="bottom")
ax.legend(loc="lower right", frameon=False, fontsize=8.6)
ax.tick_params(axis="y", length=0, labelsize=9)
ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig("out/chart_top25.png", dpi=200)
plt.savefig("out/chart_top25.svg"); plt.close()

# ------------------------------------------------- SMALL MULTIPLES: 6 pillars
fig, axes = plt.subplots(3, 2, figsize=(15.5, 13))
pb, pr = [0, 20, 35, 50, 65, 80, 90, 101], BLUE
for axx, p, n in zip(axes.ravel(), P, PN):
    g = world.merge(df[["iso", p]], on="iso", how="left")
    g[g[p].isna()].plot(ax=axx, color=NODATA, edgecolor=BORDER, linewidth=0.15)
    g[g[p].notna()].plot(ax=axx, column=p, cmap=ListedColormap(pr),
                         norm=BoundaryNorm(pb, 7), edgecolor=BORDER, linewidth=0.15)
    for iso in SMALL:
        r = g[g.iso == iso]
        if r.empty or pd.isna(r[p].iloc[0]): continue
        pt = r.geometry.iloc[0].representative_point()
        axx.plot(pt.x, pt.y, "o", ms=3.6, mfc=band_color(r[p].iloc[0], pb, pr),
                 mec="#3a3937", mew=0.5, zorder=6)
    axx.set_axis_off()
    axx.set_title(n, fontsize=11.5, fontweight="bold", loc="left", pad=6)
    top = df.nlargest(4, p)
    axx.text(0.02, 0.09, "Leaders:  " + "  ·  ".join(f"{r['name']} {r[p]:.0f}"
             for _, r in top.iterrows()), transform=axx.transAxes, fontsize=7.6, color=INK2)
fig.suptitle("PAIRI 2026 — the six pillars", fontsize=17, fontweight="bold", x=0.03,
             ha="left", y=0.995)
fig.text(0.03, 0.962, "Same 0–100 colour scale throughout: light = low, dark = high. "
         "Dots mark small states enlarged for visibility.", fontsize=9.8, color=INK2, ha="left")
plt.tight_layout(rect=[0, 0, 1, 0.955])
plt.savefig("out/map_pillars.png", dpi=180); plt.savefig("out/map_pillars.svg"); plt.close()

print("wrote:", *sorted(os.listdir("out")), sep="\n  ")

# ------------------------------------------------- METRO CLUSTER MAP + RANKING
cl = cl.sort_values("PAIRI", ascending=False).reset_index(drop=True)
cl["rk"] = cl.index + 1
pts = gpd.GeoDataFrame(cl.copy(),
        geometry=gpd.points_from_xy(cl.lon, cl.lat), crs="EPSG:4326").to_crs("ESRI:54030")
fig = plt.figure(figsize=(16.5, 9.4))
fig.text(0.022, 0.955, "The 22 metro clusters that build physical AI", fontsize=19,
         fontweight="bold", color=INK, va="top")
fig.text(0.022, 0.906, "Cluster scores on the same six pillars as the national index. Circle "
         "size and colour both show the cluster PAIRI score; numbers key to the\nranking at right. "
         "China, Japan and the United States each contain clusters at opposite ends of this range, "
         "which is what a national average hides.",
         fontsize=10.5, color=INK2, va="top")
ax = fig.add_axes([0.005, 0.075, 0.735, 0.80]); ax.set_axis_off()
world.plot(ax=ax, color="#f0efec", edgecolor="#e5e3de", linewidth=0.3)
cb = [0, 45, 55, 62, 68, 74, 80, 101]
# small manual nudges so overlapping metros stay legible
NUDGE = {"Munich":(0.55,-0.55),"Stuttgart":(-0.75,0.35),"Zurich":(-0.30,-1.15),
         "Eindhoven":(-0.85,0.95),"Gothenburg":(0.35,1.15),"Odense":(-0.10,0.55),
         "Bologna":(0.75,-1.25),"Shanghai":(1.25,0.55),"Hefei":(-0.55,-0.55),
         "Beijing":(-0.85,1.70),"Shenzhen":(-0.35,-1.15),"Tokyo":(1.40,0.30),
         "Nagoya":(0.10,-1.25),"Seoul":(0.35,1.15),"Taichung":(0.95,-0.75),
         "Boston":(0.95,0.55),"Pittsburgh":(-0.55,-0.45),"Detroit":(-0.35,0.75),
         "BayArea":(-0.85,0.0),"Austin":(0.35,-0.65)}
U = 3.1e5
for _, r in pts.sort_values("PAIRI").iterrows():
    dx, dy = NUDGE.get(r.key, (0, 0))
    x, y = r.geometry.x + dx * U * 2.6, r.geometry.y + dy * U * 2.6
    ms = (r.PAIRI / 6.9) ** 1.45
    idx = min(int(np.searchsorted(cb, r.PAIRI, "right")) - 1, 6)
    ax.plot(x, y, "o", ms=ms, mfc=band_color(r.PAIRI, cb, BLUE), mec=SURFACE, mew=1.6,
            alpha=0.95, zorder=4)
    ax.text(x, y, str(r.rk), fontsize=7.8, ha="center", va="center", zorder=6,
            color="#ffffff" if idx >= 3 else "#22211f", fontweight="bold")
pax = fig.add_axes([0.755, 0.055, 0.235, 0.845]); pax.set_axis_off()
pax.set_xlim(0, 1); pax.set_ylim(0, 1)
pax.text(0, 0.995, "Ranked by cluster readiness", fontsize=9.6, fontweight="bold",
         color=INK, va="top")
pax.text(0.855, 0.968, "PAIRI", fontsize=6.8, color=INK3, va="top", ha="right")
pax.text(1.0, 0.968, "OLI", fontsize=6.8, color=INK3, va="top", ha="right")
for i, r in cl.iterrows():
    y = 0.940 - i * 0.0405
    pax.add_patch(Rectangle((0, y - 0.017), 0.045, 0.022,
                  facecolor=band_color(r.PAIRI, cb, BLUE), edgecolor="none"))
    pax.text(0.105, y - 0.006, f"{r.rk}", fontsize=7.2, color=INK3, ha="right", va="center")
    pax.text(0.130, y - 0.006, r["label"], fontsize=7.6, color=INK, va="center")
    pax.text(0.865, y - 0.006, f"{r.PAIRI:.0f}", fontsize=7.9, color=INK, ha="right",
             va="center", fontweight="bold")
    pax.text(1.0, y - 0.006, f"{r.OLI:.0f}", fontsize=7.9, color=INK2, ha="right",
             va="center")
x0, y0, w, h = 0.028, 0.028, 0.030, 0.026
fig.text(x0, y0 + h + 0.030, "Cluster PAIRI score (0-100)", fontsize=8.6, color=INK2,
         fontweight="bold")
for i, (c, lab) in enumerate(zip(BLUE, ["<45","45-55","55-62","62-68","68-74","74-80","80+"])):
    fig.patches.append(Rectangle((x0 + i * (w + 0.003), y0), w, h,
                       transform=fig.transFigure, facecolor=c, edgecolor="none"))
    fig.text(x0 + i * (w + 0.003) + w / 2, y0 - 0.016, lab, fontsize=7.2, color=INK2,
             ha="center", va="top")
fig.text(0.42, y0 + 0.012, "Circle positions are nudged where metros overlap. OLI is the "
         "cluster's operating latitude. Scores are analyst-assigned on the\nnational pillar "
         "baseline, adjusted for documented cluster-level evidence.",
         fontsize=7.4, color=INK3, va="center")
fig.savefig("out/map_clusters.png", dpi=200); fig.savefig("out/map_clusters.svg")
plt.close(fig)
print("clusters ok")

# ------------------------------------------------- UNCERTAINTY INTERVAL CHART
import os as _os
if _os.path.exists("out/pairi_uncertainty.csv"):
    u = pd.read_csv("out/pairi_uncertainty.csv").nlargest(25, "PAIRI").iloc[::-1]
    fig, ax = plt.subplots(figsize=(11, 9.6))
    y = np.arange(len(u))
    ax.hlines(y, u.p05, u.p95, color="#9ec5f4", lw=5.5, zorder=2)
    ax.plot(u.PAIRI, y, "o", ms=6.5, mfc="#184f95", mec=SURFACE, mew=1.4, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels(u["name"], fontsize=9)
    for i, r in enumerate(u.itertuples()):
        ax.text(r.p95 + 0.9, i, f"{r.PAIRI:.1f}", va="center", fontsize=8,
                color=INK, fontweight="bold")
        ax.text(r.p05 - 0.9, i, f"±{(r.p95 - r.p05)/2:.1f}", va="center", ha="right",
                fontsize=7.2, color=INK3)
    ax.set_xlim(8, 92)
    ax.set_xlabel("PAIRI score, with 90% interval from 2,000 Monte Carlo draws over the "
                  "analyst-assigned inputs", fontsize=9.5)
    ax.set_title("How much could the judgement calls move the score?", fontsize=16,
                 fontweight="bold", loc="left", pad=48)
    ax.text(0, 1.005, "Every analyst-assigned input is perturbed (0–100 scores by SD 10 points; "
            "estimated robot density by SD 40%;\noperating-latitude components by SD 3). Cited "
            "hard data is held fixed. China's lead survives every draw; the\nUnited States and "
            "Japan swap places in 41% of them.", transform=ax.transAxes, fontsize=9.5,
            color=INK2, va="bottom")
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    for s_ in ("top", "right", "left"): ax.spines[s_].set_visible(False)
    plt.tight_layout(); plt.savefig("out/chart_uncertainty.png", dpi=200)
    plt.savefig("out/chart_uncertainty.svg"); plt.close()
    print("uncertainty chart ok")
