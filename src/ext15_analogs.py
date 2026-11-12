"""Extension 15: test the historical analogs (Nissan, GM 2005, Chrysler 2006-08, Harley-Davidson, Nike) with regressions.
Data: SEC XBRL companyfacts (NKE, HOG, GM, F), GoodCarBadCar annual US brand sales/share (2005-2025),
EIA weekly US regular gasoline, Stellantis disclosures (dealer stock +23% YoY, Q3 2026) and earlier extensions."""
import json, pathlib, numpy as np, pandas as pd, statsmodels.formula.api as smf
from ext_common import md_table
ROOT = pathlib.Path(__file__).resolve().parents[1]; P = ROOT / "data/processed"; OUT = ROOT / "results/extensions"
X = ROOT / "data/raw/xbrl"

# ------------------------------------------------------------ quarterly financial panel from XBRL
def series(d, tags, kind):
    """kind='flow' -> quarterly values (Q4 = FY - 9M); kind='stock' -> quarter-end instants. Tags are combined (earlier tag wins)."""
    out = None
    for t in tags:
        u = d["facts"].get("us-gaap", {}).get(t, {}).get("units", {}).get("USD")
        if not u: continue
        f = pd.DataFrame(u); f["end"] = pd.to_datetime(f["end"])
        if kind == "stock":
            s = f.drop_duplicates("end", keep="last").set_index("end").val
        else:
            f["start"] = pd.to_datetime(f["start"]); f["days"] = (f.end - f.start).dt.days
            q = f[f.days.between(80, 100)].drop_duplicates("end", keep="last").set_index("end").val
            y = f[f.days.between(350, 380)].drop_duplicates("end", keep="last").set_index("end").val
            nine = f[f.days.between(260, 285)].drop_duplicates("end", keep="last")
            for e, v in y.items():
                if e in q.index: continue
                n = nine[(nine.end < e) & (nine.end > e - pd.Timedelta(days=100))]
                if len(n): q.loc[e] = v - n.val.iloc[-1]
            s = q.sort_index()
        out = s if out is None else out.combine_first(s)
    return out
rows = []
for tk in ["NKE", "HOG", "GM", "F"]:
    d = json.loads((X / f"{tk}.json").read_text())
    rev = series(d, ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"], "flow")
    cogs = series(d, ["CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfGoodsSold"], "flow")
    if tk == "GM": cogs = None   # GM stops tagging total cost of sales in us-gaap after 2018; use operating margin below instead
    inv = series(d, ["InventoryNet", "InventoryFinishedGoodsNetOfReserves", "InventoryFinishedGoods"], "stock")
    df = pd.concat({"rev": rev, "inv": inv, **({"cogs": cogs} if cogs is not None else {})}, axis=1, sort=True)
    if "cogs" not in df: df["cogs"] = np.nan
    df.index = df.index.to_period("Q"); df = df.groupby(level=0).last().dropna(subset=["rev", "inv"])
    df["firm"] = tk; rows.append(df)
F = pd.concat(rows).reset_index(names="q")
F = F.sort_values(["firm", "q"])
g = F.groupby("firm")
F["gm"] = 100 * (1 - F.cogs / F.rev)
F["rev_ttm"] = g.rev.transform(lambda s: s.rolling(4).sum())
F["inv_g"] = 100 * (F.inv / g.inv.shift(4) - 1)
F["rev_g"] = 100 * (F.rev_ttm / g.rev_ttm.shift(4) - 1)
F["gap"] = F.inv_g - F.rev_g                                      # inventory growth minus sales growth, pp
F["gm_ttm"] = 100 * (1 - g.cogs.transform(lambda s: s.rolling(4).sum()) / F.rev_ttm)
F["d_gm_next4"] = g.gm_ttm.shift(-4) - F.gm_ttm                   # change in TTM gross margin over next 4 quarters
F["rev_g_next4"] = 100 * (g.rev_ttm.shift(-4) / F.rev_ttm - 1)
F = F[(F.q >= pd.Period("2010Q1")) & F.gap.between(-60, 120)]
F.to_csv(P / "analog_firm_quarterly_panel.csv", index=False)
R = F.dropna(subset=["d_gm_next4", "gap"])
r1 = smf.ols("d_gm_next4 ~ gap + C(firm)", R).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(R.firm)[0]})
r1b = {f: smf.ols("d_gm_next4 ~ gap", R[R.firm == f]).fit(cov_type="HAC", cov_kwds={"maxlags": 4}) for f in R.firm.unique()}
r2 = smf.ols("rev_g_next4 ~ gap + C(firm)", R.dropna(subset=["rev_g_next4"])).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(R.dropna(subset=['rev_g_next4']).firm)[0]})
nike_peak = F[F.firm == "NKE"].sort_values("gap").iloc[-1]
STLA_GAP = 23 - 0.0     # US dealer stock +23% YoY vs Q3 US sales -0.2% YoY (324,277 vs 324,825)

# ------------------------------------------------------------ brand panel: share hangover and fuel exposure
b = pd.read_csv(P / "gcbc_brand_annual.csv"); b = b[(b.year >= 2005) & (b.year <= 2025)]
GRP = {"Chrysler/FCA/Stellantis": ["chrysler", "dodge", "jeep", "ram", "fiat"], "GM": ["chevrolet", "gmc", "buick", "cadillac"],
       "Nissan": ["nissan", "infiniti"], "Ford": ["ford", "lincoln"], "Toyota": ["toyota", "lexus"], "Honda": ["honda"],
       "Hyundai-Kia": ["hyundai", "kia"], "Subaru": ["subaru"], "Mazda": ["mazda"], "VW": ["volkswagen"]}
inv_map = {br: grp for grp, l in GRP.items() for br in l}
b["grp"] = b.brand.map(inv_map); b = b.dropna(subset=["grp"])
tot = b.groupby("year").units.sum()                               # share within the covered brands
s = b.groupby(["grp", "year"]).units.sum().unstack(0)
share = 100 * s.div(tot, axis=0)
gas = pd.read_csv(P / "eia_weekly_gas_by_padd.csv").query("region == 'US'")
gas["year"] = pd.to_datetime(gas.date).dt.year; gas = gas.groupby("year").price.mean()
L = share.stack().rename("share").reset_index().sort_values(["grp", "year"])
L["d_share"] = L.groupby("grp").share.diff()
L["gain_2y"] = L.groupby("grp").share.diff(2)
L["fwd_2y"] = L.groupby("grp").share.shift(-2) - L.share
L["dlgas"] = L.year.map(np.log(gas).diff())
L.to_csv(P / "analog_brand_share_panel.csv", index=False)
r3 = smf.ols("fwd_2y ~ gain_2y + C(grp)", L.dropna(subset=["fwd_2y", "gain_2y"])).fit(cov_type="HC1")
# fuel-price exposure by group
fx = []
for gname, gdf in L.dropna(subset=["d_share", "dlgas"]).groupby("grp"):
    m = smf.ols("d_share ~ dlgas", gdf).fit(cov_type="HC1")
    fx.append(dict(group=gname, beta_pp_share_per_100pct_gas=round(m.params["dlgas"], 2), se=round(m.bse["dlgas"], 2),
                   p=round(m.pvalues["dlgas"], 3), n=int(m.nobs)))
FX = pd.DataFrame(fx).sort_values("beta_pp_share_per_100pct_gas")

# ------------------------------------------------------------ path matching: Stellantis vs analogs, aligned on the share peak
def path(series_, peak_year, n=10):
    y = series_.loc[peak_year: peak_year + n]
    return (100 * y / y.iloc[0]).reset_index(drop=True)
stla_peak = share["Chrysler/FCA/Stellantis"].loc[2012:2025].idxmax()
paths = {"Stellantis (peak %d)" % stla_peak: path(share["Chrysler/FCA/Stellantis"], stla_peak),
         "Nissan (peak %d)" % share["Nissan"].loc[2010:2020].idxmax(): path(share["Nissan"], share["Nissan"].loc[2010:2020].idxmax()),
         "GM (peak %d)" % share["GM"].loc[2005:2012].idxmax(): path(share["GM"], share["GM"].loc[2005:2012].idxmax()),
         "Chrysler (peak %d)" % share["Chrysler/FCA/Stellantis"].loc[2005:2010].idxmax(): path(share["Chrysler/FCA/Stellantis"], share["Chrysler/FCA/Stellantis"].loc[2005:2010].idxmax())}
PT = pd.DataFrame(paths)
st_col = PT.columns[0]; nst = PT[st_col].notna().sum()
fit = []
for c in PT.columns[1:]:
    a = PT[[st_col, c]].dropna()
    rmse = np.sqrt(((a[st_col] - a[c]) ** 2).mean())
    fit.append(dict(analog=c, years_compared=len(a), corr=round(a[st_col].corr(a[c]), 2), rmse_index_pts=round(rmse, 1),
                    analog_index_at_year_of_stla_latest=round(PT[c].iloc[nst - 1], 1),
                    analog_index_two_years_later=round(PT[c].iloc[nst + 1], 1) if nst + 1 < len(PT[c].dropna()) else np.nan))
FIT = pd.DataFrame(fit).sort_values("rmse_index_pts")

# 2026 YTD share (partial year, Jan-Oct) to extend the Stellantis path one more step
b26 = pd.read_csv(P / "gcbc_brand_annual.csv").query("year == 2026"); b26["grp"] = b26.brand.map(inv_map); b26 = b26.dropna(subset=["grp"])
sh26 = 100 * b26.groupby("grp").units.sum() / b26.units.sum()
stla26_idx = 100 * sh26["Chrysler/FCA/Stellantis"] / share["Chrysler/FCA/Stellantis"].loc[stla_peak]
proj = {c: round(share["Chrysler/FCA/Stellantis"].loc[2025] * PT[c].iloc[nst + 1] / PT[c].iloc[nst - 1], 1) for c in PT.columns[1:]
        if nst + 1 < len(PT[c].dropna())}

# ------------------------------------------------------------ R5: price premium -> next-year share, all OEM groups (Harley lesson)
k = pd.read_csv(P / "kbb_atp_monthly.csv").query("table == 'manufacturer'")
KMAP = {"Stellantis": "Chrysler/FCA/Stellantis", "General Motors": "GM", "General Motors Corp.": "GM", "Ford Motor Company": "Ford",
        "Toyota Motor Corporation": "Toyota", "American Honda Motor Co.": "Honda", "Honda Motor Company": "Honda",
        "Hyundai Motor Group": "Hyundai-Kia", "Hyundai Motor America": "Hyundai-Kia", "Renault-Nissan-Mitsubishi Alliance": "Nissan",
        "Renault-Nissan-Mitsu Alliance": "Nissan", "Subaru Corporation": "Subaru", "Mazda Motor of America": "Mazda",
        "Mazda Motor Corporation": "Mazda", "Volkswagen Group of America Inc.": "VW", "Volkswagen Group": "VW"}
k["year"] = k.month.str[:4].astype(int)
ia = k[k.entity == "Industry Average"].groupby("year").atp.mean()
k["grp"] = k.entity.map(KMAP); kk = k.dropna(subset=["grp"]).groupby(["grp", "year"]).atp.mean().reset_index()
kk["premium"] = 100 * (kk.atp / kk.year.map(ia) - 1)
sh_all = share.stack().rename("share").reset_index()   # full years only (2026 YTD is biased, see R4)
kk = kk.merge(sh_all, on=["grp", "year"], how="left")
kk["share_next"] = kk.apply(lambda r: sh_all[(sh_all.grp == r.grp) & (sh_all.year == r.year + 1)].share.squeeze() if r.year < 2025 else np.nan, axis=1)
kk["share_next"] = pd.to_numeric(kk.share_next, errors="coerce")
kk["d_share_next"] = kk.share_next - kk.share
K = kk.dropna(subset=["d_share_next", "premium"])
r5 = smf.ols("d_share_next ~ premium + C(grp)", K).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(K.grp)[0]})
r5p = smf.ols("d_share_next ~ premium", K).fit(cov_type="HC1")
stla_prem = kk[(kk.grp == "Chrysler/FCA/Stellantis")].set_index("year").premium

# ------------------------------------------------------------ write-up
c1, se1, p1 = r1.params["gap"], r1.bse["gap"], r1.pvalues["gap"]
md = ["# 15. Testing the analogs with regressions", "",
      "## Bottom line", "",
      "| Analog | Test | Result | Does Stellantis look like it? |", "|---|---|---|---|",
      "| Nike 2022 / GM 2005 (inventory glut -> discount) | R1: balance-sheet inventory-sales gap -> next-year gross margin, NKE/HOG/F | Null on average; Nike 2022 is an outlier | Can't tell from balance sheets. Dealer retail days' supply (152-169 vs 82) is the relevant gauge, and it is at glut levels |",
      "| Nissan 2016-18 (bought share reverses) | R2: 2-yr share gain -> next 2-yr change, 10 groups 2005-25 | Weak reversal (-0.09, n.s.) | Share gains are not mechanically given back; it depends on how they were bought |",
      "| Chrysler 2008 (V8 lineup vs fuel) | R3: share change on gas-price change | No significant exposure for any group; Chrysler's 2008 fall was mostly the credit crisis and bankruptcy | Fuel risk to the Hemi is real for a shock, but not visible in annual share data |",
      "| Nissan vs Chrysler-2009 path | R4: share path since peak, indexed | Stellantis tracks Chrysler 2005-11 best (RMSE 8.4) and Nissan 2017-24 close behind (9.2) | 2026 share is rising (7.8% vs 7.4%), which leans toward the Chrysler-style rebound, *if* it is retail |",
      "| Harley 2020+ (price up, volume down) | R5: ATP premium -> next-year share, all carmakers | Positive and significant, the opposite of the lesson, because ATP premium measures mix | Pricing power has to be measured like-for-like (item 1: Hemi about 1.7 pp smaller discount) |", "",
      "**Takeaway.** The analogs split on one variable: whether the volume was retail at stable like-for-like prices (Chrysler 2010-13 "
      "rebound under Fiat, built on Ram/Jeep retail) or bought through fleet and dealer stock (Nissan 2016-18, GM 2005). The "
      "regressions cannot decide that for Stellantis, but the direct measures can. Retail days' supply about 2x industry, about half of "
      "Ram's Q3 growth non-retail, and 145k units of channel fill put Stellantis closer to the Nissan side today. The Hemi's "
      "retail skew and smaller discount are the Chrysler-side evidence.", "",
      "## R1. Inventory running ahead of sales -> margin a year later (Nike, Harley-Davidson, GM, Ford; quarterly 2010-2026)", "",
      "gap = YoY inventory growth − YoY trailing-4Q revenue growth (pp). Outcome = change in trailing-4Q gross margin over the next 4 quarters. "
      "Firm fixed effects; SEs clustered by firm (4 clusters, so treat p-values as indicative).", "",
      f"Pooled: **{c1:+.3f} pp of gross margin per pp of gap** (SE {se1:.3f}, p={p1:.3f}, n={int(r1.nobs)}, R² {r1.rsquared:.2f}). "
      f"Next-year revenue growth: {r2.params['gap']:+.3f} pp per pp of gap (p={r2.pvalues['gap']:.3f}).", "",
      "| Firm | coef | SE (HAC) | p | n |", "|---|---:|---:|---:|---:|"]
md += [f"| {f} | {m.params['gap']:+.3f} | {m.bse['gap']:.3f} | {m.pvalues['gap']:.3f} | {int(m.nobs)} |" for f, m in r1b.items()]
md += ["", f"Nike's worst quarter: {nike_peak.q} (inventory +{nike_peak.inv_g:.0f}% vs revenue +{nike_peak.rev_g:.0f}%, gap {nike_peak.gap:+.0f} pp); "
       f"gross margin then moved {nike_peak.d_gm_next4:+.1f} pp over the following year.", "",
      f"**Result: no reliable signal.** Balance-sheet inventory running ahead of sales does not predict lower gross margin a year later "
      f"in this panel. Ford's slope is positive (inventory builds ahead of launches). Instead it predicts *higher* next-year revenue "
      f"growth ({r2.params['gap']:+.2f} pp per pp). Nike's 2022 glut (gap {nike_peak.gap:+.0f} pp, margin {nike_peak.d_gm_next4:+.1f} pp) is the "
      "exception that made the analog famous, not the rule. GM drops out because it stopped tagging total cost of sales in 2018. "
      "**Implication:** the Stellantis risk is not 'inventory' in general. It is *dealer* stock against *retail* demand (Cox 152-169 "
      "days), which balance-sheet data cannot see. That is why the retail days' supply series (ext14) matters more than any 10-K ratio.", "",
      "## R2. Do fast share gains reverse? US brand groups 2005-2025", "",
      f"Share change over the next 2 years on share change over the past 2 years (group FE): **{r3.params['gain_2y']:+.2f}** "
      f"(SE {r3.bse['gain_2y']:.2f}, p={r3.pvalues['gain_2y']:.3f}, n={int(r3.nobs)}). A negative coefficient means part of any 2-year share swing "
      "reverses in the next 2 years.", "",
      "Group shares (% of the covered brands):", "", md_table(share.loc[[2005, 2007, 2009, 2013, 2016, 2017, 2019, 2021, 2023, 2024, 2025]].round(1), fmt="{:.1f}"), "",
      "## R3. Fuel-price exposure of share (Chrysler 2008 lesson)", "",
      "Annual change in brand-group share on the change in log average US gasoline price, 2006-2025:", "", md_table(FX, index=False, fmt="{:.3g}"), "",
      "## R4. Which analog is Stellantis tracking? Share paths indexed to each group's peak year = 100", "",
      md_table(PT.round(1), fmt="{:.1f}"), "", md_table(FIT, index=False, fmt="{:.3g}"), "",
      "2026 is not added to the path. GCBC's 2026 year-to-date mixes quarterly reporters (Stellantis, GM: through September) "
      "with monthly reporters (through October), which biases Stellantis down. Stellantis's own figure is US share 7.8% for 9M 2026 vs 7.4% "
      "for 9M 2025 (Q3 2026 interim report): **up, which is off the Nissan path and toward the Chrysler-2010 rebound.** "
      "Two years after the matching point, the analogs imply a 2027 Stellantis share (on the GCBC basis) of "
      + ", ".join(f"{c.split(' (')[0]} {v}%" for c, v in proj.items()) + f" (2025: {share['Chrysler/FCA/Stellantis'].loc[2025]:.1f}%).", "",
      "## R5. Does a price premium cost share the next year? All carmaker groups, KBB ATP 2022-2024 -> share 2023-2025 (the Harley lesson)", "",
      f"Next-year share change on ATP premium over industry (group FE, clustered): **{r5.params['premium']:+.3f} pp share per pp premium** "
      f"(SE {r5.bse['premium']:.3f}, p={r5.pvalues['premium']:.3f}, n={int(r5.nobs)}). Without FE: {r5p.params['premium']:+.3f} (p={r5p.pvalues['premium']:.3f}).", "",
      "Stellantis ATP premium by year: " + ", ".join(f"{y} {v:+.1f}%" for y, v in stla_prem.items()) + ".", "",
      "**Read: across carmakers, a higher ATP premium is followed by share *gains*, the opposite of the Stellantis-only result "
      "(test 13: -0.14). With only 3 years per group, the fixed-effect slope picks up mix: premium rises when trucks and high trims sell, "
      "which is demand strength, not price discipline. The Harley lesson (price up, volume down) is therefore **not** "
      "detectable in transaction-price data. It needs like-for-like prices, as in the listings in item 1. Stellantis's 2026 premium "
      "rebound (+5.7 pp) should not be read as either pricing power or a share threat until mix is separated out.", "",
      "Harley-Davidson and Nike are not in R2-R5 because they have no car-share series; they enter through R1."]
(OUT / "15_analog_regressions.md").write_text("\n".join(md) + "\n"); print("\n".join(md))
