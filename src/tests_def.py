"""Sections D (interest/perception, 31-40), E (macro/regional/policy, 41-50), F (financial/downstream, 51-56)."""
import re, numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from common import *

W = stla_wide(); IND = industry_q(); gq = gcbc_q("US").pivot_table(index="quarter", columns="model", values="units")
QS = [q for q in W.index if "2021Q3" <= q <= "2026Q3"]


def qframe(**cols):
    d = pd.DataFrame(cols); d.index.name = "quarter"
    return add_time(d.reset_index())


# ================================================================ D
def test31():
    for term in ["Ram Hemi", "Ram 1500"]:
        tr = trends_q("hemi", term)
        for y, lab in [("Ram PU (total)", "Ram pickups"), ("Ram LD PU", "Ram 1500")]:
            d = qframe(units=W[y], tr=tr, ind=IND.lv_nsa_k).dropna(subset=["units", "ind"]).sort_values("quarter")
            d["ly"], d["lind"] = np.log(d.units), np.log(d.ind)
            for L in (0, 1):
                d[f"ltr{L}"] = np.log(d.tr.shift(L))
            dd = d.dropna(subset=["ltr0", "ltr1"])
            m = ols("ly ~ ltr0 + ltr1 + lind + C(qtr)", dd, hac=2)
            record(31, f'Trends "{term}" ~ {lab} sales (current + 1-quarter lag)', "RUN", m, ["ltr0", "ltr1"],
                   spec="log(units) ~ log(Trends_t) + log(Trends_{t-1}) + log(industry) + quarter-of-year; HAC(2)",
                   data="Google Trends (US, monthly averaged to quarter); Stellantis PDFs",
                   note="1-3 month lags are not testable: Stellantis reports quarterly. Quarter lag ~ 1-3 months.")
            dd = d.assign(ly_l1=d.ly.shift(1)).dropna(subset=["ltr1", "ly_l1"])
            m2 = ols("ly ~ ly_l1 + ltr1 + lind + C(qtr)", dd, hac=2)
            record(31, f'Granger-style: {lab} sales ~ own lag + Trends "{term}" lag', "RUN", m2, ["ltr1"],
                   spec="log(units_t) ~ log(units_{t-1}) + log(Trends_{t-1}) + log(industry) + quarter-of-year")


def test32():
    t = trends_m(); t = t[t.group == "hybrid"].pivot(index="date", columns="term", values="index")
    t.to_csv(OUT / "details/test_32_trends_monthly.csv")
    d = qframe(cher=W["Cherokee"], rav=gq["Toyota RAV4"], tc=trends_q("hybrid", "Cherokee hybrid"), tr=trends_q("hybrid", "RAV4 hybrid")).dropna()
    d = d[d.quarter >= "2025Q4"]; d["sales_ratio"] = d.cher / d.rav; d["trends_ratio"] = d.tc / d.tr
    d.to_csv(OUT / "details/test_32_data.csv", index=False)
    c = np.corrcoef(d.sales_ratio, d.trends_ratio)[0, 1] if len(d) > 2 else np.nan
    record(32, 'Cherokee/RAV4 sales ratio vs "Cherokee hybrid"/"RAV4 hybrid" search ratio', "DESCRIPTIVE", n=len(d),
           spec="correlation over quarters with Cherokee hybrid on sale (2025Q4-2026Q3)", data="Google Trends; Stellantis PDFs; GCBC",
           note=f"Only {len(d)} quarters; RAV4 sales are not split hybrid/ICE in public data. Mean search ratio = {d.trends_ratio.mean():.3f}, "
                f"mean sales ratio = {d.sales_ratio.mean():.3f}.", extra=dict(term="corr", coef=c))


def test33():
    share = (trends_q("price", "Jeep price") / trends_q("price", "Jeep")).rename("ps")
    d = qframe(jeep=W["Jeep"], ps=share, ind=IND.lv_nsa_k).dropna().sort_values("quarter")
    d["ly"], d["lind"], d["ps_l1"] = np.log(d.jeep), np.log(d.ind), d.ps.shift(1) * 100
    d["ps0"] = d.ps * 100
    m = ols("ly ~ ps0 + ps_l1 + lind + C(qtr)", d.dropna(), hac=2)
    record(33, 'Jeep sales ~ "Jeep price" search share (% of "Jeep" searches)', "RUN", m, ["ps0", "ps_l1"],
           spec="log(Jeep) ~ price-search share_t + share_{t-1} + log(industry) + quarter-of-year; HAC(2)",
           data="Google Trends", note='"Jeep too expensive" and "Jeep deals" have ~zero Trends volume; "Jeep price" used.')


def test38():
    w = pd.read_csv(P / "wikipedia_pageviews_monthly.csv"); w["quarter"] = pd.PeriodIndex(w.month.astype(str), freq="M").asfreq("Q").map(qstr)
    wq = w.groupby(["model", "quarter"]).views.agg(["sum", "count"]).reset_index(); wq = wq[wq["count"] == 3]
    MAP = {"Ram pickup": ("S", "Ram PU (total)"), "Wrangler": ("S", "Wrangler"), "Grand Cherokee": ("S", "Grand Cherokee"),
           "Compass": ("S", "Compass"), "Cherokee": ("S", "Cherokee"), "Gladiator": ("S", "Gladiator"), "Wagoneer family": ("S", "Wagoneer family"),
           "Durango": ("S", "Durango"), "Hornet": ("S", "Hornet"), "Pacifica": ("S", "Pacifica"), "Wagoneer S": ("S", "Wagoneer S"),
           "ProMaster Van": ("S", "ProMaster Van"), "Charger": ("S", ["Charger ICE", "Charger BEV"]),
           "Ford F-Series": ("G", "Ford F-Series"), "Chevrolet Silverado": ("G", "Chevrolet Silverado"), "Toyota RAV4": ("G", "Toyota RAV4")}
    wq = wq[wq.model.isin(MAP)]   # Ford Bronco pageviews collected but GCBC has no Bronco sales
    rows = []
    for _, r in wq.iterrows():
        src, col = MAP[r.model]; tab = W if src == "S" else gq
        if r.quarter not in tab.index: continue
        u = tab.loc[r.quarter, col].sum() if isinstance(col, list) else tab.loc[r.quarter, col]
        if pd.notna(u) and u >= 500: rows.append(dict(model=r.model, quarter=r.quarter, units=u, views=r["sum"]))
    d = add_time(pd.DataFrame(rows)).sort_values(["model", "quarter"])
    d["ly"], d["lv"] = np.log(d.units), np.log(d.views); d["lv_l1"] = d.groupby("model").lv.shift(1)
    d = d[d.quarter >= "2021Q3"]; d.to_csv(OUT / "details/test_38_panel.csv", index=False)
    m = ols("ly ~ lv + C(model) + C(quarter)", d, cluster="model")
    record(38, "Model sales ~ Wikipedia pageviews (model panel)", "RUN", m, ["lv"],
           spec="log(units) ~ log(pageviews) + model FE + quarter FE; cluster model", data="Wikimedia REST API; Stellantis PDFs; GCBC",
           note=f"{d.model.nunique()} nameplates (13 Stellantis + 3 rivals), 2021Q3-2026Q3")
    m2 = ols("ly ~ lv_l1 + C(model) + C(quarter)", d.dropna(subset=["lv_l1"]), cluster="model")
    record(38, "Same, pageviews lagged one quarter", "RUN", m2, ["lv_l1"], spec="log(units_t) ~ log(views_{t-1}) + FE")


def test40():
    t = trends_m(); t = t[t.group == "brands"].copy(); t["quarter"] = t.date.dt.to_period("Q").map(qstr)
    p = t.pivot_table(index="quarter", columns="term", values="index", aggfunc="mean")
    ss = (p[["Jeep", "Dodge", "Chrysler"]].sum(axis=1) / p.sum(axis=1) * 100).rename("search_share")
    d = qframe(stla=W["Stellantis"], ind=IND.lv_nsa_k, ss=ss).dropna(); d["share"] = d.stla / (d.ind * 1000) * 100
    d = d.sort_values("quarter"); d["ss_l1"] = d.ss.shift(1)
    m = ols("share ~ ss + C(qtr)", d, hac=2)
    record(40, "Stellantis US share ~ Stellantis brands' search share vs Ford+Toyota", "RUN", m, ["ss"],
           spec="share% ~ search share% (Jeep+Dodge+Chrysler)/(those+Ford+Toyota) + quarter-of-year; HAC(2)",
           data="Google Trends (one payload, comparable scale); Stellantis PDFs; BEA", note="Ram excluded from Trends (term 'Ram' ambiguous; 'Ram trucks' ~0 volume).")
    m2 = ols("share ~ ss_l1 + C(qtr)", d.dropna(), hac=2)
    record(40, "Same, search share lagged one quarter", "RUN", m2, ["ss_l1"])


def blocked_d():
    B = {34: ("Reddit price-complaint share ~ brand ATP", "reddit.com returns 403 from this environment; needs Reddit API credentials (OAuth app)."),
         35: ("Reddit Hemi sentiment ~ Ram retail growth", "Same: Reddit API access required."),
         36: ("YouTube review views ~ launch-quarter sales", "YouTube Data API v3 requires an API key; none configured."),
         37: ("CarGurus deal-rating mix ~ exit rate", "Requires CarGurus listings scrape (site returns 406; check terms)."),
         39: ("Dealer review sentiment ~ inventory turn", "Google Places API key required, plus dealer inventory turns from the listings scrape.")}
    for k, (t, why) in B.items(): record(k, t, "BLOCKED", note=why)


# ================================================================ E
def test41():
    gas = gas_q("US")
    d = qframe(ram=W["Ram PU (total)"], ld=W["Ram LD PU"], ind=IND.lv_nsa_k, gas=gas, f=gq["Ford F-Series"], s=gq["Chevrolet Silverado"])
    d = d.dropna(subset=["ram", "ind", "gas"])
    d["lshare"] = np.log(d.ram / (d.ram + d.f + d.s)); d["lgas"] = np.log(d.gas); d["lind"] = np.log(d.ind)
    m = ols("lshare ~ lgas + C(qtr)", d, hac=2)
    record(41, "PROXY: Ram share of full-size pickups ~ US gasoline price", "RUN (proxy)", m, ["lgas"],
           spec="log(Ram/(Ram+F-Series+Silverado)) ~ log(EIA retail regular) + quarter-of-year; HAC(2)",
           data="EIA weekly gasoline; Stellantis PDFs; GCBC",
           note="The planned test (Hemi share of listings by region ~ regional gas) needs the listings scrape; this national proxy cannot isolate the V8.")
    # cross-state: Hemi search intensity ~ PADD gas price (see test 45 for state covariates)


PADD = {1: "CT ME MA NH RI VT DE DC MD NJ NY PA FL GA NC SC VA WV", 2: "IL IN IA KS KY MI MN MO NE ND SD OH OK TN WI",
        3: "AL AR LA MS NM TX", 4: "CO ID MT UT WY", 5: "AK AZ CA HI NV OR WA"}
ST = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
      "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
      "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
      "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
      "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
      "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
      "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
      "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}


def state_covariates():
    cache = P / "state_covariates.csv"
    raw = ROOT / "data/raw/census"
    if not (raw / "est23all.xls").exists(): return pd.read_csv(cache, index_col=0)
    s = pd.read_excel(raw / "est23all.xls", header=3, dtype={"State FIPS Code": str, "County FIPS Code": str})
    s = s[s["County FIPS Code"] == "000"]; inc = s.set_index("Postal Code")["Median Household Income"].rename("med_income")
    ua = pd.read_excel(raw / "2020_UA_COUNTY.xlsx", dtype={"STATE": str})
    popcol = [c for c in ua.columns if c.upper() == "POP_COU"][0]; rur = [c for c in ua.columns if c.upper() == "POP_RUR"][0]
    st_name = [c for c in ua.columns if c.upper() == "STATE_NAME"][0]
    r = ua.groupby(st_name)[[popcol, rur]].sum(); r["rural_share"] = r[rur] / r[popcol] * 100
    r.index = r.index.map(ST); rural = r.rural_share
    mv = pd.read_excel(raw / "mv1.xlsx", header=None).iloc[9:, [0, 3, 9]]; mv.columns = ["state", "autos", "trucks"]
    mv["state"] = mv.state.astype(str).str.replace(r"\s*\(\d+\)", "", regex=True).str.strip().map(ST)
    mv = mv.dropna(subset=["state"]); mv["truck_share"] = pd.to_numeric(mv.trucks) / (pd.to_numeric(mv.autos) + pd.to_numeric(mv.trucks)) * 100
    parts = [inc, rural, mv.set_index("state").truck_share]
    parts = [x[x.index.notna() & ~x.index.duplicated() & (x.index != "US")] for x in parts]
    out = pd.concat(parts, axis=1); out.to_csv(cache)
    return out


def test45():
    h = pd.read_csv(P / "trends_state_hemi.csv"); h["st"] = h.geoName.map(ST)
    cov = state_covariates()
    gas = pd.read_csv(P / "eia_weekly_gas_by_padd.csv", parse_dates=["date"]); gas = gas[gas.date >= "2025-06-01"]
    gp = gas.groupby("region").price.mean(); padd_price = {}
    for k, sts in PADD.items():
        reg = [r for r in gp.index if r.startswith(f"PADD{k}")][0]
        for s_ in sts.split(): padd_price[s_] = gp[reg]
    d = h.set_index("st").join(cov); d["gas"] = d.index.map(padd_price); d = d.dropna()
    for c in ["Hemi", "med_income", "rural_share", "truck_share", "gas"]: d[c] = d[c].astype(float)
    d.to_csv(OUT / "details/test_45_state.csv")
    m = ols("Hemi ~ np.log(med_income) + rural_share + truck_share", d)
    record(45, 'State "Hemi" search intensity ~ income, rurality, truck share', "RUN (proxy)", m,
           ["np.log(med_income)", "rural_share", "truck_share"], spec="Trends state index (Jun 2025-Oct 2026) ~ log median HH income + rural % + truck registration %; HC1",
           data="Google Trends by state; Census SAIPE 2023; Census 2020 urban/rural by county; FHWA MV-1 2022",
           note="Search interest stands in for Hemi share of sales/listings (needs scrape). Trends index is relative within each state.")
    m2 = ols("Hemi ~ np.log(gas) + np.log(med_income) + rural_share + truck_share", d)
    record(41, 'Cross-state: "Hemi" search intensity ~ regional (PADD) gas price', "RUN (proxy)", m2, ["np.log(gas)"],
           spec="state Trends index ~ log PADD avg gas price (Jun 2025-Oct 2026) + state covariates; HC1", data="EIA PADD prices; Trends; Census; FHWA",
           note="Only 5 distinct gas prices (PADD level); weak identification.")


def test43():
    rates = g19_q()
    d = qframe(stla=W["Stellantis"], ram=W["Ram"], jeep=W["Jeep"], ind=IND.lv_nsa_k, r60=rates.rate60_bank).dropna()
    d["share"] = d.stla / (d.ind * 1000) * 100; d["lind"] = np.log(d.ind)
    for y, lab in [("stla", "Stellantis"), ("ram", "Ram"), ("jeep", "Jeep")]:
        d["ly"] = np.log(d[y])
        m = ols("ly ~ r60 + C(qtr)", d, hac=2)
        record(43, f"{lab} sales ~ 60-month new-car loan rate", "RUN", m, ["r60"], spec="log(units) ~ rate (pp) + quarter-of-year; HAC(2)",
               data="Fed G.19 terms of credit (commercial banks, 60m new car); Stellantis PDFs")
        m2 = ols("ly ~ r60 + lind + C(qtr)", d, hac=2)
        record(43, f"{lab} sales ~ loan rate, controlling for industry volume (excess sensitivity)", "RUN", m2, ["r60"],
               spec="log(units) ~ rate + log(industry units) + quarter-of-year; HAC(2)")


BAND = {"high": ["Ram PU (total)", "Wagoneer family"], "mid": ["Wrangler", "Gladiator", "Grand Cherokee", "Durango", "Pacifica", "Charger ICE", "Challenger"],
        "low": ["Compass", "Cherokee", "Hornet", "Renegade", "Voyager"]}


def test44():
    sent = umich_q(); rows = []
    for b, ms in BAND.items():
        for q in QS:
            u = W.loc[q, [m for m in ms if m in W.columns]].fillna(0).sum()
            rows.append(dict(band=b, quarter=q, units=u, sent=sent.get(q), ind=IND.lv_nsa_k.get(q)))
    d = add_time(pd.DataFrame(rows).dropna()); d["ly"] = np.log(d.units); d["lind"] = np.log(d.ind)
    m = ols("ly ~ sent:C(band) + C(band) + C(band):C(qtr)", d, hac=2)
    record(44, "Stellantis sales by price band ~ U. Michigan sentiment", "RUN", m, [f"sent:C(band)[{b}]" for b in ["high", "mid", "low"]],
           spec="log(band units) ~ sentiment x band + band FE + band x quarter-of-year; HAC(2)",
           data="U. Michigan ICS; Stellantis PDFs", note="Bands by KBB segment ATP: high = full-size pickup/SUV (>$65k), mid = $45-60k, low = compact (<$40k).")
    d2 = d.copy(); d2["lshare"] = d2.ly - d2.lind
    m2 = ols("lshare ~ sent:C(band) + C(band) + C(band):C(qtr)", d2, hac=2)
    record(44, "Band sales relative to industry ~ sentiment (does Stellantis feel shocks more than the market?)", "RUN", m2,
           [f"sent:C(band)[{b}]" for b in ["high", "mid", "low"]], spec="log(band units / industry units) ~ sentiment x band + FE")


def test46():
    record(46, "Stellantis share ~ Texas/Southeast vs coastal states", "BLOCKED",
           note="State new-vehicle registration data by make is licensed (S&P Global Mobility/Experian); no free state series found.")


def test47():
    pt = powertrains(); stl = ["Wrangler", "Gladiator", "Grand Cherokee", "Wagoneer family", "Ram LD PU", "Durango", "Charger ICE", "Challenger"]
    v8 = pt[pt.model.isin(stl)].groupby("model_year").apply(lambda g: int(g.powertrains.str.count(r"_\d\.\dL_8cyl").sum()), include_groups=False)
    v8.rename("v8_powertrains").to_csv(OUT / "details/test_47_v8_count_by_my.csv")
    rows = []
    for q in QS:
        tot = W.loc[q, "Stellantis"]; v = 0
        for m in stl:
            r = pt[(pt.model == m) & (pt.model_year == quarter_to_my(q))]
            if len(r) and r.iloc[0].has_v8 and m in W.columns and pd.notna(W.loc[q, m]): v += W.loc[q, m]
        rows.append(dict(quarter=q, v8_share=100 * v / tot))
    d = add_time(pd.DataFrame(rows)); d["post"] = (d.quarter >= "2025Q3").astype(int)
    d.to_csv(OUT / "details/test_47_data.csv", index=False)
    m = ols("v8_share ~ post + t + C(qtr)", d, hac=2)
    record(47, "Event study: share of Stellantis sales from V8-offering nameplates ~ post CAFE-penalty zeroing (Jul 2025)", "RUN (proxy)", m, ["post"],
           spec="V8-available sales share % ~ post(>=2025Q3) + trend + quarter-of-year; HAC(2)", data="EPA lineups; Stellantis PDFs",
           note="Production V8 share is not public; this uses nameplate V8 availability. Hemi-return decision (Jun 2025) predates the July 2025 law, "
                f"so policy and demand are not separable. V8 powertrains offered by MY: {dict(v8)}")


def test48():
    a = atp_monthly(); a = a[a.table == "manufacturer"]
    pv = a.pivot_table(index="month", columns="entity", values="atp")
    peers = ["Ford Motor Company", "General Motors", "Toyota Motor Corporation", "Honda Motor Company", "Hyundai Motor Group"]
    rows = []
    for mnth, r in pv.iterrows():
        for e in ["Stellantis"] + peers:
            if pd.notna(r.get(e)): rows.append(dict(month=mnth, mfr=e, latp=np.log(r[e]), stla=int(e == "Stellantis")))
    d = pd.DataFrame(rows); d["post"] = (d.month >= "2025-04").astype(int); d["sp"] = d.stla * d.post
    d["tt"] = pd.PeriodIndex(d.month, freq="M").map(lambda p: p.ordinal); d["mfr_t"] = d.tt
    m = ols("latp ~ sp + C(mfr) + C(month)", d, cluster="month")
    record(48, "Tariffs: Stellantis ATP vs peer OEMs after April 2025 auto tariffs", "RUN", m, ["sp"],
           spec="log(ATP) ~ Stellantis x Post(>=Apr 2025) + OEM FE + month FE; cluster month", data="KBB ATP manufacturer table, Mar 2022-Oct 2026",
           note="Peers: Ford, GM, Toyota, Honda, Hyundai. ATP reflects mix and excludes incentives; tariff pass-through and mix shift are not separable.")
    m2 = ols("latp ~ sp + C(mfr) + C(month) + C(mfr):tt", d, cluster="month")
    record(48, "Same, with OEM-specific linear trends", "RUN", m2, ["sp"], spec="+ OEM x linear trend")


def test49():
    d = qframe(bev=W[["Charger BEV", "Wagoneer S", "500e"]].fillna(0).sum(axis=1), cb=W["Charger BEV"].fillna(0),
               ci=W["Charger ICE"].fillna(0), stla=W["Stellantis"]).loc[lambda x: x.quarter >= "2025Q1"]
    d["post"] = (d.quarter >= "2025Q4").astype(int); d["charger_bev_share"] = 100 * d.cb / (d.cb + d.ci)
    d["bev_share_stla"] = 100 * d.bev / d.stla; d.to_csv(OUT / "details/test_49_data.csv", index=False)
    m = ols("charger_bev_share ~ post", d, hac=1)
    record(49, "Charger BEV share of Charger sales ~ post EV-credit expiry (Sep 30 2025)", "RUN", m, ["post"],
           spec="BEV share % ~ post(>=2025Q4); HAC(1); 2025Q1-2026Q3", data="Stellantis PDFs",
           note="n=7; Sixpack ICE ramp coincides with the credit expiry, so the effect is an upper bound on the policy effect.")
    m2 = ols("bev_share_stla ~ post", d, hac=1)
    record(49, "Stellantis BEV share (Charger BEV + Wagoneer S + 500e) ~ post credit expiry", "RUN", m2, ["post"], spec="BEV % of Stellantis US ~ post")


def test50():
    ca = gcbc_q("CA").pivot_table(index="quarter", columns="model", values="units")
    rows = []
    for q in QS:
        if q not in ca.index: continue
        rows.append(dict(unit="Ram", quarter=q, units=ca.loc[q, "Ram pickup (GCBC)"]))
        for c in ["Ford F-Series", "Chevrolet Silverado", "GMC Sierra", "Toyota Tundra"]: rows.append(dict(unit=c, quarter=q, units=ca.loc[q, c]))
    d = add_time(pd.DataFrame(rows).dropna()); d["ly"] = np.log(d.units); d["tp"] = ((d.unit == "Ram") & (d.quarter >= "2025Q4")).astype(int)
    d["ram_t"] = (d.unit == "Ram") * d.t
    m = ols("ly ~ tp + C(unit) + C(quarter)", d)
    record(50, "Canada: Ram pickups vs Canadian full-size rivals after US Hemi return", "RUN", m, ["tp"],
           spec="log(units) ~ Ram x Post(>=2025Q4) + unit FE + quarter FE; HC1", data="GCBC Canada tables (from OEM reports)",
           note="Hemi return applied to Canada too, so this is a replication in a second market, not a spillover test. Mexico: no public model data.")
    m2 = ols("ly ~ tp + ram_t + C(unit) + C(quarter)", d)
    record(50, "Same, with Ram-specific trend", "RUN", m2, ["tp"], spec="+ Ram x trend")
    tot = pd.read_csv(P / "stellantis_canada_quarterly_totals.csv").set_index("quarter").ca_units
    d2 = qframe(ca=tot, us=W["Stellantis"]).dropna().sort_values("quarter")
    d2["gca"], d2["gus"] = np.log(d2.ca).diff(4), np.log(d2.us).diff(4)
    m3 = ols("gca ~ gus", d2.dropna(), hac=2)
    record(50, "Stellantis Canada YoY growth ~ US YoY growth", "RUN", m3, ["gus"], spec="d4 log(Canada total) ~ d4 log(US total); HAC(2)",
           data="Stellantis Canada releases (quarterly totals)")


# ================================================================ F
def na_fin():
    na = pd.read_csv(P / "stellantis_na_segment_raw.csv"); rec = {}
    for _, r in na.iterrows():
        for side in ["cur", "prev"]:
            per = r[f"period_{side}"].replace(" Pro Forma", "").strip()
            if not re.match(r"^(H[12]|Q[1-4]) 20\d\d$", per): continue
            if per in rec and side == "prev": continue        # prefer the period's own release
            rec[per] = dict(ship=r[f"shipments_k_{side}"], rev=r[f"net_revenues_eur_m_{side}"], aoi=r[f"aoi_eur_m_{side}"],
                            margin=r[f"aoi_margin_pct_{side}"])
    d = pd.DataFrame(rec).T; d.index.name = "period"; d = d.reset_index()
    # derive Q4 2025 = H2 2025 - Q3 2025
    if {"H2 2025", "Q3 2025"} <= set(d.period):
        h, q3 = d.set_index("period").loc["H2 2025"], d.set_index("period").loc["Q3 2025"]
        q4 = dict(period="Q4 2025", ship=h.ship - q3.ship, rev=h.rev - q3.rev, aoi=h.aoi - q3.aoi); q4["margin"] = 100 * q4["aoi"] / q4["rev"]
        d = pd.concat([d, pd.DataFrame([q4])])
    if {"Q1 2026", "Q2 2026"} <= set(d.period):
        a, b = d.set_index("period").loc["Q1 2026"], d.set_index("period").loc["Q2 2026"]
        h1 = dict(period="H1 2026", ship=a.ship + b.ship, rev=a.rev + b.rev, aoi=a.aoi + b.aoi); h1["margin"] = 100 * h1["aoi"] / h1["rev"]
        d = pd.concat([d, pd.DataFrame([h1])])
    fx = pd.read_csv(P / "eurusd_daily.csv", parse_dates=["date"])
    def qs(per):
        k, y = per.split(); y = int(y)
        return [f"{y}Q{i}" for i in ((1, 2) if k == "H1" else (3, 4) if k == "H2" else (int(k[1]),))]
    def fxavg(per):
        k, y = per.split(); y = int(y); mo = {"H1": (1, 6), "H2": (7, 12)}.get(k, (3 * int(k[1]) - 2, 3 * int(k[1])))
        s = fx[(fx.date.dt.year == y) & fx.date.dt.month.between(*mo)].eurusd
        return s.mean()
    d["eurusd"] = d.period.map(fxavg)
    def ram_share(p):
        q_ = qs(p)
        if not all(x in W.index for x in q_): return np.nan
        return 100 * sum(W.loc[x, "Ram"] for x in q_) / sum(W.loc[x, "Stellantis"] for x in q_)
    d["ram_share_us"] = d.period.map(ram_share)
    d["rev_per_unit_usd_k"] = d.rev * d.eurusd / d.ship
    d["freq"] = d.period.str[0].map({"H": "half", "Q": "quarter"})
    d = d.sort_values(["freq", "period"]); d.to_csv(OUT / "details/test_51_52_na_financials.csv", index=False)
    return d


def test51_52():
    d = na_fin(); h = d[d.freq == "half"].copy(); q = d[d.freq == "quarter"].copy()
    for frame, lab in [(h, "half-years 2021-2026"), (q, "quarters 2025Q1-2026Q3")]:
        frame = frame.astype({c: float for c in ["ship", "rev", "aoi", "margin", "eurusd", "ram_share_us", "rev_per_unit_usd_k"]})
        frame = frame.dropna(subset=["ram_share_us"])
        m = ols("rev_per_unit_usd_k ~ ram_share_us", frame)
        record(51, f"NA revenue per unit (USD k) ~ Ram share of US sales ({lab})", "RUN", m, ["ram_share_us"],
               spec="NA net revenue x EURUSD / NA shipments ~ Ram % of Stellantis US sales; HC1",
               data="Stellantis 6-K results (SEC EDGAR); Yahoo EURUSD; Stellantis US PDFs",
               note="Ram share of shipments is not disclosed; Ram share of US sales is the proxy. Revenue includes pricing, incentives and fleet mix.")
        m2 = ols("margin ~ ship", frame)
        record(52, f"NA AOI margin (%) ~ NA shipments (000s) ({lab})", "RUN", m2, ["ship"],
               spec="AOI margin ~ shipments; HC1", data="Stellantis 6-K results",
               note="2024-25 margins include tariffs, warranty-estimate changes and incentive spend; fixed-cost leverage is not isolated.")


def test55():
    px = pd.read_csv(P / "stock_prices_daily.csv", parse_dates=["date"]).pivot(index="date", columns="ticker", values="adjclose")
    ret = np.log(px).diff().dropna(subset=["STLA", "SPY"])
    DATES = {"2022Q3": "2022-10-03", "2022Q4": "2023-01-04", "2023Q1": "2023-04-03", "2023Q2": "2023-07-03", "2023Q3": "2023-10-03",
             "2023Q4": "2024-01-03", "2024Q1": "2024-04-03", "2024Q3": "2024-10-01", "2024Q4": "2025-01-03", "2025Q1": "2025-04-01",
             "2025Q2": "2025-07-01", "2025Q3": "2025-10-01", "2025Q4": "2026-01-05", "2026Q1": "2026-04-01", "2026Q2": "2026-07-01",
             "2026Q3": "2026-10-01"}   # release dates from media.stellantisnorthamerica.com listings
    rows = []
    for q, ds in DATES.items():
        t0 = ret.index[ret.index.get_indexer([pd.Timestamp(ds)], method="bfill")[0]]
        i0 = ret.index.get_loc(t0); est = ret.iloc[max(0, i0 - 130): i0 - 10]
        b = sm.OLS(est.STLA, sm.add_constant(est.SPY)).fit().params
        win = ret.iloc[i0: i0 + 2]; car = float((win.STLA - b["const"] - b["SPY"] * win.SPY).sum()) * 100
        py = f"{int(q[:4]) - 1}{q[4:]}"
        g_stla = 100 * (W.loc[q, "Stellantis"] / W.loc[py, "Stellantis"] - 1)
        g_ind = 100 * (IND.lv_nsa_k[q] / IND.lv_nsa_k[py] - 1) if py in IND.index and q in IND.index else np.nan
        rows.append(dict(quarter=q, date=str(t0.date()), car_0_1_pct=car, stla_yoy=g_stla, ind_yoy=g_ind, surprise=g_stla - g_ind))
    d = pd.DataFrame(rows); d.to_csv(OUT / "details/test_55_event_study.csv", index=False)
    m = ols("car_0_1_pct ~ surprise", d.dropna())
    record(55, "STLA abnormal return on US sales-release days ~ sales growth vs industry", "RUN", m, ["surprise"],
           spec="CAR[0,+1] (market model vs SPY, est. window t-130..t-10) ~ (STLA YoY - industry YoY) pp; HC1",
           data="Yahoo Finance STLA, SPY; Stellantis PDFs; BEA",
           note="Days' supply component blocked (no public Cox brand series). Q2-2024 release missing from the media archive; Q4 dates are early January.")
    record(55, "Mean CAR[0,+1] on sales-release days", "DESCRIPTIVE", n=len(d),
           extra=dict(term="mean_car_pct", coef=d.car_0_1_pct.mean(), se=d.car_0_1_pct.std(ddof=1) / np.sqrt(len(d))))


def test56():
    r = pd.read_csv(P / "nhtsa_vehicle_recalls_post2010.csv.gz", dtype=str)
    r = r[r.MFGNAME.str.contains("FCA|Chrysler|Stellantis", case=False, na=False)]
    r["YEAR"] = pd.to_numeric(r.YEARTXT, errors="coerce"); r = r[r.YEAR.between(2018, 2026)]
    MAP = {"Wrangler": r"^WRANGLER", "Gladiator": r"^GLADIATOR", "Grand Cherokee": r"^GRAND CHEROKEE", "Cherokee": r"^CHEROKEE",
           "Compass": r"^COMPASS", "Renegade": r"^RENEGADE", "Wagoneer family": r"^(GRAND )?WAGONEER$|^(GRAND )?WAGONEER L", "Ram LD PU": r"^1500",
           "Durango": r"^DURANGO", "Charger ICE": r"^CHARGER$", "Challenger": r"^CHALLENGER", "Pacifica": r"^PACIFICA", "Hornet": r"^HORNET"}
    pt = powertrains(); rows = []
    for m, rx in MAP.items():
        sub = r[r.MODELTXT.str.upper().str.contains(rx, regex=True, na=False)]
        p = pt[pt.model == m].set_index("model_year")
        for y in range(2019, 2027):
            if y not in p.index: continue
            new = len(set(p.loc[y].powertrains.split(";")) - set(p.loc[y - 1].powertrains.split(";"))) if (y - 1) in p.index else np.nan
            rows.append(dict(model=m, my=y, recalls=sub[sub.YEAR == y].CAMPNO.nunique(), n_pt=p.loc[y].n_powertrains, new_pt=new))
    d = pd.DataFrame(rows).dropna(); d["any_new"] = (d.new_pt > 0).astype(int)
    d.to_csv(OUT / "details/test_56_panel.csv", index=False)
    m = smf.poisson("recalls ~ any_new + n_pt + C(model) + C(my)", d).fit(disp=0, cov_type="cluster", cov_kwds={"groups": d.model})
    record(56, "NHTSA recall campaigns per nameplate-model-year ~ new powertrain introduced that MY", "RUN", m, ["any_new", "n_pt"],
           spec="Poisson: campaigns ~ new-powertrain dummy + # powertrains + nameplate FE + MY FE; cluster nameplate (coef = log rate ratio)",
           data="NHTSA FLAT_RCL recalls (through Nov 2026); EPA lineups",
           note="Recent model years have had less time to accumulate recalls (absorbed by MY FE). Counts campaigns, not affected units.")


def blocked_f():
    record(53, "Used values: Hemi vs Hurricane Ram 1500", "BLOCKED", note="Needs used-listing scrape (or Manheim/J.D. Power valuation data by engine); Manheim's public index is not split by engine.")
    record(54, "Used Jeep prices ~ new Jeep incentives", "BLOCKED", note="No public Jeep incentive series (see #18) and no brand-level used price index.")
    record(42, "Cherokee hybrid exit rate ~ gas prices", "BLOCKED", note="Needs listings scrape; national Cherokee hybrid sales exist for only 4 quarters.")


if __name__ == "__main__":
    for f in [test31, test32, test33, test38, test40, blocked_d, test41, test45, test43, test44, test46, test47, test48, test49, test50,
              test51_52, test55, test56, blocked_f]:
        try: f()
        except Exception as e:
            import traceback; traceback.print_exc(); print("FAILED", f.__name__)
    r = pd.DataFrame(RESULTS); print(r[["test", "title", "term", "coef", "se", "p", "n"]].to_string(max_colwidth=70))
    r.to_csv(OUT / "results_DEF.csv", index=False)
