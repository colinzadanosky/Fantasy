"""Macro / market series (FRED is unreachable from this environment, so primary publishers are used):
- BEA 'Motor Vehicle Unit Retail Sales' (gap_hist.xlsx, Table 6): light-vehicle sales NSA and SAAR, monthly
- Federal Reserve G.19 terms of credit: 60-/72-month new-car loan rates at commercial banks, quarterly
- University of Michigan Index of Consumer Sentiment, monthly
- EIA weekly retail regular gasoline, US and PADD 1-5
- Yahoo Finance daily adjusted close: STLA, F, GM, TM, SPY"""
import pathlib, time, io, requests, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; RAW = ROOT / "data/raw/macro"; RAW.mkdir(parents=True, exist_ok=True)
P = ROOT / "data/processed"; H = {"User-Agent": "Mozilla/5.0"}
def get(url, **kw):
    for i in range(5):
        try:
            r = requests.get(url, headers=H, timeout=60, **kw); r.raise_for_status(); return r
        except Exception as e: err = e; time.sleep(2 ** (i + 1))
    raise err
MON = {m: i + 1 for i, m in enumerate(["January","February","March","April","May","June","July","August","September","October","November","December"])}
# BEA
b = get("https://apps.bea.gov/national/xls/gap_hist.xlsx").content; (RAW / "bea_gap_hist.xlsx").write_bytes(b)
d = pd.read_excel(io.BytesIO(b), sheet_name="Table 6", header=None).iloc[5:, :10]
d.columns = ["month", "year", "autos_nsa_k", "ltrucks_nsa_k", "lv_nsa_k", "total_nsa_k", "autos_saar_m", "ltrucks_saar_m", "lv_saar_m", "total_saar_m"]
d = d.dropna(subset=["month", "year", "lv_nsa_k"]); d["year"] = d.year.astype(int); d["month"] = d.month.str.strip().map(MON)
d = d.dropna(subset=["month"]); d["date"] = pd.to_datetime(dict(year=d.year, month=d.month, day=1))
d[["date"] + list(d.columns[2:10])].to_csv(P / "bea_light_vehicle_sales_monthly.csv", index=False); print("BEA", d.date.max())
# G.19 terms of credit
h = get("https://www.federalreserve.gov/releases/g19/HIST/cc_hist_tc_levels.html").text; (RAW / "g19_terms.html").write_text(h)
t = pd.read_html(io.StringIO(h))[0]; t.columns = [" | ".join(c) for c in t.columns]
t = t.rename(columns={t.columns[0]: "period"}); t = t[t.period.str.match(r"^\d{4} Q\d$", na=False)]
for c in t.columns[1:]: t[c] = pd.to_numeric(t[c], errors="coerce")
t["quarter"] = t.period.str.replace(" ", ""); t.to_csv(P / "g19_terms_of_credit_quarterly.csv", index=False); print("G19", t.quarter.max())
# UMich
u = pd.read_csv(io.StringIO(get("https://www.sca.isr.umich.edu/files/tbmics.csv").text))
u["date"] = pd.to_datetime(dict(year=u.YYYY, month=u.Month.map(MON), day=1)); u[["date", "ICS_ALL"]].rename(columns={"ICS_ALL": "umich_sentiment"}).to_csv(P / "umich_sentiment_monthly.csv", index=False); print("UMich", u.date.max())
# EIA weekly gasoline
EIA = {"US": "EMM_EPMR_PTE_NUS_DPG", "PADD1_EastCoast": "EMM_EPMR_PTE_R10_DPG", "PADD2_Midwest": "EMM_EPMR_PTE_R20_DPG",
       "PADD3_GulfCoast": "EMM_EPMR_PTE_R30_DPG", "PADD4_Rockies": "EMM_EPMR_PTE_R40_DPG", "PADD5_WestCoast": "EMM_EPMR_PTE_R50_DPG"}
eia = []
for k, code in EIA.items():
    raw = get(f"https://www.eia.gov/dnav/pet/hist_xls/{code}w.xls").content; (RAW / f"eia_{code}.xls").write_bytes(raw)
    x = pd.read_excel(io.BytesIO(raw), sheet_name="Data 1", skiprows=2); x.columns = ["date", "price"]; x["region"] = k; eia.append(x)
eia = pd.concat(eia); eia.to_csv(P / "eia_weekly_gas_by_padd.csv", index=False); print("EIA", eia.date.max())
# Yahoo
px = []
for tk in ["STLA", "F", "GM", "TM", "SPY"]:
    j = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{tk}", params={"range": "10y", "interval": "1d"}).json()["chart"]["result"][0]
    px.append(pd.DataFrame({"date": pd.to_datetime(j["timestamp"], unit="s").normalize(), "ticker": tk, "adjclose": j["indicators"]["adjclose"][0]["adjclose"]}))
px = pd.concat(px); px.to_csv(P / "stock_prices_daily.csv", index=False); print("px", px.date.min(), px.date.max())
# EUR/USD (NA segment revenue is reported in EUR)
j = get("https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X", params={"range": "10y", "interval": "1d"}).json()["chart"]["result"][0]
pd.DataFrame({"date": pd.to_datetime(j["timestamp"], unit="s").normalize(), "eurusd": j["indicators"]["quote"][0]["close"]}).to_csv(P / "eurusd_daily.csv", index=False)
