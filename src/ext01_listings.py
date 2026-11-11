"""Extension 1 (+10, 11, 12): Hemi V8 vs six-cylinder Ram 1500 discounts from a one-day KBB/Autotrader listing pull.
Inputs: data/raw/listings/kbb_ram1500_2026-11-11_batch*.csv (Ram 1500, by market and KBB cylinder filter),
        data/raw/listings/kbb_rivals_2026-11-11.csv (F-150, Silverado 1500, Dallas),
        data/processed/ny_new_pickup_registrations.csv.gz (sales-to-inventory cross-check, NY geography).
Listing pages were read with a fetch tool on 2026-11-11 (the first ~45 listings per page in KBB's default order;
MSRP and advertised price as displayed; price includes ~$314 dealer doc/registration fees). Two detail pages were
spot-checked against the extracted values (engine, MSRP, price matched)."""
import glob, pathlib, numpy as np, pandas as pd
import statsmodels.formula.api as smf
from ext_common import md_table
ROOT = pathlib.Path(__file__).resolve().parents[1]; RAW = ROOT / "data/raw/listings"; OUT = ROOT / "results/extensions"
P = ROOT / "data/processed"

L = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(str(RAW / "kbb_ram1500_*_batch*.csv")))])
L = L.drop_duplicates("listing_id").reset_index(drop=True)
L["engine"] = np.where(L.engine_filter.eq("8CLDR"), "Hemi V8", "6-cyl")
L["dealer_name"] = L.dealer_name.fillna("unknown")
n0 = len(L)
L = L[L.msrp.notna()]
L = L[~L.trim.str.contains("TRX|RHO", regex=True)]                         # supercharged / high-output performance trims
L.loc[L.trim.eq("4x4 Crew Cab"), "trim"] = "Big Horn"
med = L.groupby(["trim", "year"]).msrp.transform("median")
L["msrp_suspect"] = L.msrp > 1.25 * med                                     # e.g. 'MSRP' of $98k on a Big Horn
L["disc_pct"] = 100 * (1 - L.listed_price / L.msrp)
L["disc_usd"] = L.msrp - L.listed_price
clean = L[~L.msrp_suspect].copy()
clean["id_pct"] = clean.groupby("market").listing_id.rank(pct=True)           # higher = listed more recently
clean["v8"] = (clean.engine == "Hemi V8").astype(int)
clean["lmsrp"] = np.log(clean.msrp)
clean.to_csv(P / "listings_ram1500_2026-11-11.csv", index=False)

res = []
def fit(name, formula, df):
    m = smf.ols(formula, df).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(df.dealer_name)[0]})
    res.append(dict(spec=name, coef_v8=m.params["v8"], se=m.bse["v8"], p=m.pvalues["v8"], n=int(m.nobs), r2=m.rsquared))
    return m
fit("discount % ~ V8 (raw)", "disc_pct ~ v8", clean)
fit("+ trim, model year, market, log MSRP", "disc_pct ~ v8 + C(trim) + C(year) + C(market) + lmsrp", clean)
fit("+ dealer FE (within-dealer)", "disc_pct ~ v8 + C(trim) + C(year) + lmsrp + C(dealer_name)", clean)
fit("MY2026 only, trim + market + dealer FE", "disc_pct ~ v8 + C(trim) + lmsrp + C(dealer_name)", clean[clean.year == 2026])
fit("MY2027 only, trim + market", "disc_pct ~ v8 + C(trim) + C(market) + lmsrp", clean[clean.year == 2027])
fit("Big Horn/Lone Star only, + year + dealer FE", "disc_pct ~ v8 + C(year) + lmsrp + C(dealer_name)", clean[clean.trim.isin(["Big Horn", "Lone Star"])])
fit("listing-age proxy: ID percentile ~ V8 + trim + year + market", "id_pct ~ v8 + C(trim) + C(year) + C(market)", clean)
R = pd.DataFrame(res); R.to_csv(OUT / "01_listing_discount_models.csv", index=False)

by = clean.groupby(["year", "engine"]).agg(n=("disc_pct", "size"), mean_disc=("disc_pct", "mean"), median_disc=("disc_pct", "median"),
                                           mean_disc_usd=("disc_usd", "mean"), mean_msrp=("msrp", "mean")).round(1)
bm = clean.groupby(["market", "engine"]).agg(n=("disc_pct", "size"), mean_disc=("disc_pct", "mean"),
                                             market_total=("market_total", "first")).round(1).reset_index()
inv = bm.pivot(index="market", columns="engine", values="market_total")
inv["v8_share_of_inventory"] = (inv["Hemi V8"] / inv.sum(axis=1)).round(3)
dm = bm.pivot(index="market", columns="engine", values="mean_disc")
inv["disc_gap_v8_minus_6cyl_pp"] = (dm["Hemi V8"] - dm["6-cyl"]).round(1)
bt = clean[clean.trim.isin(["Express", "Big Horn", "Lone Star", "Laramie", "Warlock", "Tradesman", "Rebel"])].groupby(
    ["trim", "engine"]).disc_pct.agg(["size", "mean"]).round(1).unstack()
bt.columns = [f"{a}_{b}".replace("size", "n").replace("mean", "disc") for a, b in bt.columns]

# ---------- sales-to-inventory: NY registrations vs NYC-area listings
ny = pd.read_csv(P / "ny_new_pickup_registrations.csv.gz", parse_dates=["reg_date"], low_memory=False)
r = ny[(ny.nameplate == "Ram 1500") & ny.engine.isin(["Hemi V8", "6-cyl"]) & ~ny.Trim.fillna("").str.contains("RHO|TRX")]
r = r.assign(q=r.reg_date.dt.to_period("Q").astype(str))
sh = r[r.q.isin(["2025Q4", "2026Q1", "2026Q2", "2026Q3", "2026Q4"]) & (r.my >= 2026)].groupby("q").apply(
    lambda g: pd.Series({"hemi_share_all": (g.engine == "Hemi V8").mean(),
                         "hemi_share_retail": (g[g.channel == "retail"].engine == "Hemi V8").mean(), "n": len(g)})).round(3)
sh["n"] = sh.n.astype(int)
nyc_inv = inv.loc["New York NY", "v8_share_of_inventory"]
# geography within NY (retail, MY2026+)
rr = r[(r.my >= 2026) & (r.channel == "retail") & (r.county != "OUT-OF-STATE")]
NYC = {"KINGS", "QUEENS", "NEW YORK", "BRONX", "RICHMOND"}; LI = {"NASSAU", "SUFFOLK"}
rr = rr.assign(region=np.where(rr.county.isin(NYC), "NYC", np.where(rr.county.isin(LI | {"WESTCHESTER", "ROCKLAND"}), "NYC suburbs", "Upstate")))
geo = rr.groupby("region").engine.apply(lambda s: (s == "Hemi V8").mean()).round(3).to_frame("hemi_share_retail")
geo["n"] = rr.region.value_counts()
cty = rr.groupby("county").agg(n=("engine", "size"), hemi=("engine", lambda s: (s == "Hemi V8").mean()))
cty = cty[cty.n >= 100].sort_values("hemi").round(3)

# ---------- rivals (item 10)
rv = pd.read_csv(RAW / "kbb_rivals_2026-11-11.csv").drop_duplicates("listing_id")
rv = rv[(rv.msrp < 100000)]
rv["disc_pct"] = 100 * (1 - rv.listed_price / rv.msrp)
rv = rv[rv.disc_pct.between(-5, 45)]
dal = clean[clean.market == "Dallas TX"]; dal = dal.assign(model="Ram 1500 (" + dal.engine + ")")
cmpd = pd.concat([dal[["model", "disc_pct", "msrp"]], rv[["model", "disc_pct", "msrp"]]])
comp = cmpd.groupby("model").agg(n=("disc_pct", "size"), mean_disc=("disc_pct", "mean"), median_disc=("disc_pct", "median"),
                                 mean_msrp=("msrp", "mean"), market_listings=("model", "size")).round(1)
comp = comp.drop(columns="market_listings")
cmpd["ram"] = cmpd.model.str.startswith("Ram").astype(int); cmpd["lmsrp"] = np.log(cmpd.msrp)
mr = smf.ols("disc_pct ~ ram + lmsrp", cmpd).fit(cov_type="HC1")

# prior-model-year inventory (item 11): MY2027 is current; MY2025/2026 are prior-year stock
pm = clean.assign(prior=clean.year < 2027).groupby("engine").agg(n=("prior", "size"), prior_my_share=("prior", "mean")).round(3)
pmm = clean.assign(prior=clean.year < 2027).groupby("market").prior.mean().round(3).to_frame("prior_my_share")
gap_prior = clean[clean.year < 2027].groupby("engine").disc_pct.mean() - clean[clean.year == 2027].groupby("engine").disc_pct.mean()

# ---------- write-up
f = lambda x: f"{x:+.2f}"
md = ["# 1. Does the Hemi need smaller discounts? (one-day listing pull, 2026-11-11)", "",
      f"Listings: {n0} Ram 1500 listings across Dallas, Detroit, Atlanta, Phoenix and New York (50-mile radius each), read from "
      "KBB/Autotrader search pages filtered by cylinder count (8 = 5.7 Hemi; 6 = 3.0 Hurricane). After dropping TRX/RHO, "
      f"missing MSRP and {int(L.msrp_suspect.sum())} listings with an implausible MSRP (>1.25x the trim median; one Long Island dealer), "
      f"**{len(clean)} listings** remain from {clean.dealer_name.nunique()} dealers. Discount = 1 - advertised price / MSRP.", "",
      "## Discount by model year and engine", "", md_table(by, fmt="{:.1f}"), "",
      "## Regression: discount (pp of MSRP) on Hemi dummy, SEs clustered by dealer", "",
      "| Spec | Hemi coef (pp) | SE | p | n |", "|---|---:|---:|---:|---:|"]
md += [f"| {x.spec} | {x.coef_v8:+.2f} | {x.se:.2f} | {x.p:.3f} | {x.n} |" for x in R.itertuples()]
md += ["", "## By trim", "", md_table(bt, fmt="{:.1f}"), "",
       "## By market: inventory mix and discount gap (items 12)", "", md_table(inv, fmt="{:.3g}"), "",
       "## Sales-to-inventory check (NY registrations vs NYC-area listings)", "",
       f"Hemi share of NYC-area Ram 1500 inventory (KBB, excl. TRX/RHO not separable in totals): **{nyc_inv:.0%}**.", "",
       "Hemi share of new NY Ram 1500 registrations (MY2026+, i.e. years where both engines are offered; excl. TRX/RHO):", "", md_table(sh, fmt="{:.3g}"), "",
       "Within New York, retail MY2026+ registrations:", "", md_table(geo, fmt="{:.3g}"), "",
       "Counties with >=100 retail MY2026+ registrations, lowest to highest Hemi share:", "", md_table(cty, fmt="{:.3g}"), "",
       "## Prior-model-year inventory (item 11)", "", md_table(pm, fmt="{:.3g}"), "", md_table(pmm, fmt="{:.3g}"), "",
       f"Extra discount on prior-MY vs MY2027 stock: 6-cyl {gap_prior['6-cyl']:+.1f} pp, Hemi {gap_prior['Hemi V8']:+.1f} pp.", "",
       "## Ram vs F-150 vs Silverado 1500 discounts, Dallas (item 10)", "", md_table(comp, fmt="{:.1f}"), "",
       f"Ram minus rivals, controlling for log MSRP: {mr.params['ram']:+.1f} pp (SE {mr.bse['ram']:.1f}, p={mr.pvalues['ram']:.3f}, n={int(mr.nobs)}).", ""]
(OUT / "01_listings.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
