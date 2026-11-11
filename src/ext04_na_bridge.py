"""Extension 4: North America AOI bridges and how much of the 'Industrial' improvement is repeatable.

Bridge values are transcribed from the waterfall chart images in the MD&A of Stellantis' 20-F and interim
reports on SEC EDGAR (src/collect_sec_mdna.py downloads them; charts are images, so values were read off the
labels and checked: every bridge sums to the reported end-point AOI within EUR 2m).
Component amounts (warranty, regulatory/CAFE, tariffs) come from the text of the same filings; the decomposition and its basis are in
results/extensions/04_industrial_decomposition.csv."""
import pathlib, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; P = ROOT / "data/processed"; OUT = ROOT / "results/extensions"
OUT.mkdir(parents=True, exist_ok=True)

COLS = ["start", "volume_mix", "net_price", "industrial", "sga", "rnd", "fx_other", "end"]
B = [  # period, comparison, source image, values (EUR m)
 ("FY2021", "FY2020 PF", "20F_2022 g3 (old driver set; vol/mix = industry+line mix+share)", [6123, 557 + 2638 - 786, 4897, -1651, -30, -500, 108, 11356]),
 ("H1 2022", "H1 2021 PF", "interim_2022_H1 (old driver set)", [5236, -1226 + 120 + 125, 2337, -1810, 177, -1, 2725, 7683]),
 ("FY2022", "FY2021 PF", "20F_2024 g6 (restated driver set)", [11342, -843, 5377, -3898, 235, 70, 1704, 13987]),
 ("H1 2023", "H1 2022", "interim_2023_H1", [7683, -1057, 1304, 24, -74, 26, 121, 8027]),
 ("FY2023", "FY2022", "20F_2024 g5", [13987, -2261, 1743, 366, 19, -4, -552, 13298]),
 ("H1 2024", "H1 2023", "interim_2024_H1", [8027, -2674, -374, -473, 70, 53, -263, 4366]),
 ("FY2024", "FY2023", "20F_2025 g3", [13298, -6971, -2068, -1253, -48, 222, -520, 2660]),
 ("H1 2025", "H1 2024", "interim_2025_H1", [4366, -2773, -1173, -944, -92, -4, -331, -951]),
 ("FY2025", "FY2024", "20F_2026 g4", [2660, -1430, -883, -1557, -81, -139, -462, -1892]),
 ("Q1 2026", "Q1 2025", "interim_2026_Q1", [-542, 640, 186, 181, -68, -70, -64, 263]),
 ("Q2 2026", "Q2 2025", "interim_2026_Q2", [-440, 409, -59, 603, -158, -101, 30, 284]),
 ("H1 2026", "H1 2025", "interim_2026_Q2", [-982, 1049, 123, 745, -229, -172, 13, 547]),
 ("Q3 2026", "Q3 2025", "interim_2026_Q3", [-475, -247, 421, 529, -38, -172, 46, 64]),
 ("9M 2026", "9M 2025", "interim_2026_Q3", [-1457, 1086, 245, 1334, -263, -348, 14, 611]),
]
rows = []
for per, cmp_, src, v in B:
    d = dict(zip(COLS, v)); d.update(period=per, vs=cmp_, source=src)
    d["check_residual"] = d["start"] + sum(d[c] for c in COLS[1:-1]) - d["end"]
    rows.append(d)
br = pd.DataFrame(rows)[["period", "vs"] + COLS + ["check_residual", "source"]]
assert br.check_residual.abs().max() <= 2, br
br.to_csv(P / "na_aoi_bridges.csv", index=False)

# Implied H2 bridges (FY minus H1), same driver set from FY2023 on
h2 = []
for fy, h1 in [("FY2023", "H1 2023"), ("FY2024", "H1 2024"), ("FY2025", "H1 2025")]:
    a, b = br.set_index("period").loc[fy, COLS[1:-1]], br.set_index("period").loc[h1, COLS[1:-1]]
    h2.append({"period": "H2 " + fy[2:], **(a - b).to_dict()})
h2 = pd.DataFrame(h2)
# Implied Q3 2025 vs Q3 2024 is not available (Q3 2025 had no MD&A walk).

# ---------- decomposition of the 9M 2026 and Q3 2026 Industrial improvement
# All EUR bn. Sources: interim_2026_Q2/Q3 'Cost of revenues' paragraphs, Q1/Q2/Q3 2026 press releases (guidance).
dec = pd.DataFrame([
 # component, 9M low, 9M high, Q3 low, Q3 high, repeatable?, basis
 ("Regulatory (CAFE penalty elimination, OBBB Jul-2025)", 0.6, 0.6, 0.2, 0.2, "Level persists while law stands; YoY gain ends once 2025 H2 is lapped (already only 0.2 in Q3). Policy, not efficiency.",
  "NA regulatory expense -1.2bn 9M; excluded from AOI: 2026 net benefit 0.3, 2025 net cost 0.3 -> in-AOI = 1.2 - 0.6 = 0.6. Q3: -0.2, exclusions negligible."),
 ("Warranty: non-repeat of 2025 in-AOI change in estimate, net of higher warranty/recall", 0.0, 0.5, 0.0, 0.3, "One-time base effect (the 2025 charge does not recur; nothing to repeat in 2027).",
  "Group warranty expense -3.8bn 9M / -3.6bn Q3, of which 3.3bn was the Q3-2025 charge already excluded from AOI -> in-AOI 0.5 / 0.3 group-wide (upper bound for NA). Total H2-25 charge 5.3bn vs 4.13bn excluded."),
 ("IEEPA tariff refund (Q1 2026)", 0.4, 0.4, 0.0, 0.0, "One-time.", "~0.4bn IEEPA tariff cost adjustment recognised Q1 2026."),
 ("Underlying 2026 tariff cost vs 2025", -0.4, -0.4, -0.1, 0.1, "Recurring headwind (masked by refund).", "Mgmt: tariff impact 'broadly neutral' YoY 9M incl. refund -> ex-refund roughly -0.4. Group net tariffs 9M26 0.6bn (gross ~1.0bn); FY25 ~1.2bn, H1-25 0.3bn."),
], columns=["component", "ytd_low", "ytd_high", "q3_low", "q3_high", "repeatability", "basis"])
IND_9M, IND_Q3 = 1.334, 0.529
resid = dict(component="Residual: manufacturing + purchasing efficiency incl. VCP, net of raw-material inflation, recall costs, lower D&A on impaired assets",
             ytd_low=round(IND_9M - dec.ytd_high.sum(), 3), ytd_high=round(IND_9M - dec.ytd_low.sum(), 3),
             q3_low=round(IND_Q3 - dec.q3_high.sum(), 3), q3_high=round(IND_Q3 - dec.q3_low.sum(), 3),
             repeatability="Repeatable to the extent it is VCP/purchasing; part is lower depreciation after 2025 impairments (non-cash).",
             basis="Industrial total minus the itemised components.")
dec = pd.concat([dec, pd.DataFrame([resid])], ignore_index=True)
dec.to_csv(OUT / "04_industrial_decomposition.csv", index=False)

# simple summary numbers
rep_low, rep_high = resid["ytd_low"], resid["ytd_high"]
one_low = 0.4 + 0.0; one_high = 0.4 + 0.5
def fmt(x): return f"{x:,.0f}"
md = ["# 4. North America operating-income bridges: repeatable savings vs disappearing costs", "",
      "## Bridges (EUR m), transcribed from the MD&A waterfall charts",
      "", "| Period | vs | Start | Vol & mix | Net price | Industrial | SG&A | R&D | FX & other | End |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
for r in br.itertuples():
    md.append(f"| {r.period} | {r.vs} | {fmt(r.start)} | {fmt(r.volume_mix)} | {fmt(r.net_price)} | **{fmt(r.industrial)}** | {fmt(r.sga)} | {fmt(r.rnd)} | {fmt(r.fx_other)} | {fmt(r.end)} |")
md += ["", "Implied H2 Industrial (FY minus H1): " + ", ".join(f"{r.period} {fmt(r.industrial)}" for r in h2.itertuples()), "",
       f"Cumulative Industrial, FY2022 to FY2025: {fmt(br.set_index('period').loc[['FY2022','FY2023','FY2024','FY2025'],'industrial'].sum())}. "
       f"Recovered in 9M 2026: {fmt(IND_9M*1000)}.", ""]
md += ["## What is inside the 9M 2026 Industrial +1,334 (EUR bn)", "", "| Component | 9M 2026 | Q3 2026 | Repeatable? |", "|---|---|---|---|"]
for r in dec.itertuples():
    rng = lambda a, b: f"{a:+.1f}" if abs(a - b) < 1e-9 else f"{a:+.1f} to {b:+.1f}"
    md.append(f"| {r.component} | {rng(r.ytd_low, r.ytd_high)} | {rng(r.q3_low, r.q3_high)} | {r.repeatability} |")
md += ["", f"**Answer.** Of the EUR 1.33bn, about **EUR {rep_low:.1f}-{rep_high:.1f}bn ({rep_low/IND_9M:.0%}-{rep_high/IND_9M:.0%})** is left for "
       "manufacturing/purchasing efficiency (VCP) after removing the items management itemises. About EUR 0.6bn (45%) is the CAFE "
       "penalty elimination: it keeps the cost level lower, but it is a policy windfall, not efficiency, and the YoY gain stops "
       f"after mid-2026. EUR {one_low:.1f}-{one_high:.1f}bn is one-time (the IEEPA refund and the warranty base effect), and the refund "
       "hides about EUR 0.4bn of recurring tariff cost.", "",
       "Even the residual overstates cash efficiency. It is also net of raw-material inflation and higher recall costs (negative), "
       "and it includes lower depreciation after the EUR 5.7bn of NA platform impairments in 2025 (positive, non-cash).",
       "", "**Restructuring is not in this bridge.** Stellantis excludes restructuring, impairments, the warranty re-estimate "
       "(EUR 3.25bn NA) and the CAFE write-offs from AOI. They sit in the reconciliation table, not in 'Industrial'.",
       "", "**Disclosure limits.** Stellantis does not split 'Industrial' into purchasing, manufacturing, warranty and tariffs in "
       "the waterfall. The split above uses the group-level Cost of revenues commentary (warranty) and NA-specific text "
       "(regulatory, tariffs). The warranty range is therefore an upper bound for NA. The earnings-call slides (stellantis.com) "
       "may carry more detail, but the site blocks this environment (403).", "",
       "Sources: Stellantis 20-F FY2021-FY2025 and interim reports H1 2021-Q3 2026 (MD&A charts and Cost of revenues notes); "
       "Q1/Q2/Q3 2026 results press releases (tariff guidance). FY2025 net tariffs of ~EUR 1.2bn come from press coverage of the FY2025 results."]
(OUT / "04_na_bridge.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
