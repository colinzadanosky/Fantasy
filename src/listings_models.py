"""Listing-based tests (21, 22, 26, 27, 29, 30; also 16, 17, 41, 42, 45 once state/metro fields exist).
NOT RUN YET: requires the weekly listing scrape. Expected input: data/processed/listings_weekly.csv with one row per
VIN x scrape week and columns:
    vin, scrape_date, make, model, model_year, trim, powertrain (from NHTSA vPIC decode), price, msrp,
    dealer_id, metro, state, dist_to_center_mi, color, package, days_listed
A VIN 'exits' when it disappears for 2 consecutive scrapes (sold or transferred).
Usage: python3 src/listings_models.py [path/to/listings_weekly.csv]"""
import sys, numpy as np, pandas as pd
import statsmodels.formula.api as smf
from statsmodels.duration.hazard_regression import PHReg


def build_spells(df):
    df = df.sort_values(["vin", "scrape_date"]); last = df.scrape_date.max()
    g = df.groupby("vin")
    sp = g.agg(first=("scrape_date", "min"), last_seen=("scrape_date", "max"), price=("price", "median"),
               msrp=("msrp", "max"), powertrain=("powertrain", "first"), make=("make", "first"), model=("model", "first"),
               model_year=("model_year", "first"), trim=("trim", "first"), metro=("metro", "first"),
               dist=("dist_to_center_mi", "first"), color=("color", "first"), dealer_id=("dealer_id", "first")).reset_index()
    sp["duration"] = (sp.last_seen - sp["first"]).dt.days + 7
    sp["exited"] = (sp.last_seen < last - pd.Timedelta(days=14)).astype(int)   # censor VINs still listed
    sp["disc_pct"] = 100 * (1 - sp.price / sp.msrp)
    sp["price_band"] = pd.cut(sp.price, [0, 40e3, 50e3, 60e3, 70e3, 1e7], labels=["<40k", "40-50k", "50-60k", "60-70k", "70k+"])
    sp["prior_my"] = (sp.model_year < sp["first"].dt.year + (sp["first"].dt.month >= 9)).astype(int)
    return sp


def run(path):
    df = pd.read_csv(path, parse_dates=["scrape_date"]); sp = build_spells(df); out = {}
    # 21 hazard of exit ~ powertrain + price band + metro (Cox PH, stratified by model)
    m21 = PHReg.from_formula("duration ~ C(powertrain) + C(price_band) + C(metro)", sp, status=sp.exited, strata=sp.model).fit()
    out[21] = m21.summary()
    # 22 days listed ~ powertrain | trim, price (exited units only)
    s = sp[sp.exited == 1]
    out[22] = smf.ols("np.log(duration) ~ C(powertrain) + C(trim) + np.log(price)", s).fit(cov_type="cluster", cov_kwds={"groups": s.dealer_id}).summary()
    # 16/17 discount ~ powertrain, model year
    out[16] = smf.ols("disc_pct ~ C(powertrain) + C(model) + C(metro)", sp).fit(cov_type="HC1").summary()
    out[17] = smf.ols("disc_pct ~ prior_my * C(powertrain) + C(model)", sp).fit(cov_type="HC1").summary()
    # 26 prior-model-year share ~ powertrain
    out[26] = smf.logit("prior_my ~ C(powertrain) + C(model)", sp).fit(disp=0).summary()
    # 27 Stellantis vs Ford within price band
    sp["stla"] = sp.make.isin(["Jeep", "Ram", "Dodge", "Chrysler"]).astype(int)
    out[27] = PHReg.from_formula("duration ~ stla + C(metro)", sp, status=sp.exited, strata=sp.price_band.astype(str)).fit().summary()
    # 29 distance from metro center; 30 color/package within powertrain
    out[29] = PHReg.from_formula("duration ~ np.log1p(dist) * C(powertrain)", sp, status=sp.exited, strata=sp.model).fit().summary()
    out[30] = PHReg.from_formula("duration ~ C(color)", sp, status=sp.exited, strata=(sp.model + "_" + sp.powertrain)).fit().summary()
    return out


if __name__ == "__main__":
    for k, v in run(sys.argv[1] if len(sys.argv) > 1 else "data/processed/listings_weekly.csv").items():
        print(f"=== test {k}\n{v}\n")
