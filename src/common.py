"""Shared loaders and regression helpers for the Stellantis powertrain-demand tests."""
import pathlib, re
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / "data/processed"
OUT = ROOT / "results"; (OUT / "details").mkdir(parents=True, exist_ok=True)

RESULTS = []          # one row per reported coefficient
MODELS = []           # (test, title, spec, model, terms, status) for charts


def record(test, title, status, model=None, terms=(), n=None, spec="", note="", data="", extra=None):
    """Append result rows. status: RUN | RUN (proxy) | DESCRIPTIVE | BLOCKED."""
    base = dict(test=test, title=title, status=status, spec=spec, data=data, note=note)
    if model is None:
        RESULTS.append({**base, "n": n, **(extra or {})}); return
    MODELS.append(dict(test=test, title=title, spec=spec, model=model, terms=list(terms), status=status))
    with open(OUT / "details" / f"test_{test:02d}.txt", "a") as fh:
        fh.write(f"### {title}\n{spec}\n{model.summary()}\n\n")
    r2 = getattr(model, "rsquared", np.nan)
    for t in terms:
        RESULTS.append({**base, "term": t, "coef": model.params[t], "se": model.bse[t],
                        "p": model.pvalues[t], "n": int(model.nobs), "r2": r2, **(extra or {})})


def ols(formula, df, hac=None, cluster=None):
    """HAC/cluster SEs only when the sample can support them; below 15 obs fall back to classical SEs."""
    m = smf.ols(formula, data=df)
    if m.nobs < 15:
        return m.fit()
    if cluster is not None:
        return m.fit(cov_type="cluster", cov_kwds={"groups": df[cluster]})
    if hac:
        return m.fit(cov_type="HAC", cov_kwds={"maxlags": hac})
    return m.fit(cov_type="HC1")


# ---------------------------------------------------------------- loaders
def qstr(p):  # Period -> '2025Q3'
    return f"{p.year}Q{p.quarter}"


def stla_long():
    return pd.read_csv(P / "stellantis_us_quarterly_sales.csv")


def stla_wide():
    d = stla_long()
    w = d.pivot_table(index="quarter", columns="model", values="units", aggfunc="sum").sort_index()
    w.index.name = "quarter"
    return w


def gcbc_q(country="US"):
    g = pd.read_csv(P / "gcbc_quarterly_sales.csv")
    return g[g.country == country]


def industry_q():
    b = pd.read_csv(P / "bea_light_vehicle_sales_monthly.csv", parse_dates=["date"])
    b["quarter"] = b.date.dt.to_period("Q").map(qstr)
    q = b.groupby("quarter").agg(lv_nsa_k=("lv_nsa_k", "sum"), lv_saar_m=("lv_saar_m", "mean"),
                                 ltrucks_nsa_k=("ltrucks_nsa_k", "sum"), months=("date", "count"))
    return q[q.months == 3].drop(columns="months")


def atp_monthly():
    a = pd.read_csv(P / "kbb_atp_monthly.csv")
    return a


def atp_q(entities, table="make"):
    a = atp_monthly(); a = a[(a.table == table) & a.entity.isin(entities)].copy()
    a["quarter"] = pd.PeriodIndex(a.month, freq="M").asfreq("Q").map(qstr)
    g = a.groupby(["quarter", "entity"]).agg(atp=("atp", "mean"), m=("atp", "count")).reset_index()
    g = g[g.m == 3]
    return g.pivot(index="quarter", columns="entity", values="atp")


def g19_q():
    t = pd.read_csv(P / "g19_terms_of_credit_quarterly.csv")
    c60 = [c for c in t.columns if "60-month new car" in c][0]
    fin = [c for c in t.columns if "finance companies" in c and "Interest" in c][0]
    return t.set_index("quarter")[[c60, fin]].rename(columns={c60: "rate60_bank", fin: "rate_fincos"})


def umich_q():
    u = pd.read_csv(P / "umich_sentiment_monthly.csv", parse_dates=["date"])
    u["quarter"] = u.date.dt.to_period("Q").map(qstr)
    return u.groupby("quarter").umich_sentiment.mean()


def gas_q(region="US"):
    e = pd.read_csv(P / "eia_weekly_gas_by_padd.csv", parse_dates=["date"])
    e = e[e.region == region]; e["quarter"] = e.date.dt.to_period("Q").map(qstr)
    return e.groupby("quarter").price.mean()


def trends_m():
    t = pd.read_csv(P / "google_trends_monthly.csv", parse_dates=["date"])
    return t


def trends_q(group, term):
    t = trends_m(); t = t[(t.group == group) & (t.term == term)].copy()
    t["quarter"] = t.date.dt.to_period("Q").map(qstr)
    g = t.groupby("quarter")["index"].agg(["mean", "count"]); return g[g["count"] == 3]["mean"]


def powertrains():
    return pd.read_csv(P / "powertrains_by_model_year.csv")


def quarter_to_my(q):
    """Lineup on sale in a calendar quarter: Q4 is assumed to carry the next model year."""
    y, k = int(q[:4]), int(q[-1])
    return y + 1 if k == 4 else y


def add_time(df, col="quarter"):
    df = df.copy()
    per = pd.PeriodIndex(df[col], freq="Q")
    df["qtr"] = per.quarter.astype(str)
    df["t"] = (per.year - 2021) * 4 + per.quarter
    return df


def save_results():
    r = pd.DataFrame(RESULTS)
    r.to_csv(OUT / "regression_results.csv", index=False)
    return r
