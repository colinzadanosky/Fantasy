"""Extension 9: used-market value of the Hemi. MY2023 Ram 1500 used listings, Dallas (100-mile radius), KBB 2026-11-11,
split by KBB cylinder filter (8 = 5.7 Hemi, 6 = 3.6 Pentastar V6). Hedonic: log price ~ V8 + trim + log mileage."""
import pathlib, numpy as np, pandas as pd, statsmodels.formula.api as smf
ROOT = pathlib.Path(__file__).resolve().parents[1]; OUT = ROOT / "results/extensions"
u = pd.read_csv(ROOT / "data/raw/listings/kbb_used_ram1500_my2023_dallas_2026-11-11.csv").drop_duplicates(["listing_id", "trim"])
u = u[(u.year == 2023) & ~u.trim.str.contains("TRX|Classic|Limited|Rebel|Warlock")]   # comparable trims in both groups
u.loc[u.trim.eq("4x4 Crew Cab"), "trim"] = "Big Horn"
u["v8"] = (u.engine_filter == "8CLDR").astype(int); u["lp"] = np.log(u.listed_price); u["lmi"] = np.log(u.mileage.clip(lower=1000))
m = smf.ols("lp ~ v8 + C(trim) + lmi", u).fit(cov_type="HC1")
both = u.groupby("trim").v8.nunique().loc[lambda s: s == 2].index
m2 = smf.ols("lp ~ v8 + C(trim) + lmi", u[u.trim.isin(both)]).fit(cov_type="HC1")
avg = u.listed_price.mean()
md = ["# 9. Used Ram 1500 resale: does the Hemi hold value? (MY2023, Dallas, 2026-11-11)", "",
      f"n = {int(m.nobs)} used MY2023 Ram 1500 listings (Tradesman, Big Horn, Lone Star, Laramie), {int(u.v8.sum())} Hemi and {int((1-u.v8).sum())} V6.", "",
      "| Spec | Hemi premium (log pts) | SE | p | n |", "|---|---:|---:|---:|---:|",
      f"| trim + log mileage | {m.params['v8']:+.3f} | {m.bse['v8']:.3f} | {m.pvalues['v8']:.3f} | {int(m.nobs)} |",
      f"| trims sold with both engines only | {m2.params['v8']:+.3f} | {m2.bse['v8']:.3f} | {m2.pvalues['v8']:.3f} | {int(m2.nobs)} |", "",
      f"At the sample mean price (${avg:,.0f}) the premium is about **${avg*(np.exp(m.params['v8'])-1):,.0f}**. Compare it with the Hemi "
      "option price on the original window sticker (not collected here). A used premium well below the option price means "
      "the Hemi's extra price did not survive into resale.", "",
      "Read with care: this is a single-day sample from one metro, and the MY2023 'six-cylinder' is the 3.6 Pentastar V6, "
      "not today's 3.0 Hurricane. A clean test of the 2026 powertrain mix needs 2-3 years of MY2026 used listings."]
(OUT / "09_resale.md").write_text("\n".join(md) + "\n"); print("\n".join(md))
