"""Extension 13: North America channel-stock identity.
stock build (000s) = NA consolidated shipments (Stellantis 6-K) - US sales (Stellantis) - Canada sales - Mexico sales (INEGI).
Positive = more vehicles shipped to dealers/fleets than were reported sold in the region. Residual also contains timing
differences (shipments recognised at wholesale; sales reported at delivery) and the small non-US/CA/MX NA markets."""
import pathlib, pandas as pd
from ext_common import md_table
ROOT = pathlib.Path(__file__).resolve().parents[1]; P = ROOT / "data/processed"; OUT = ROOT / "results/extensions"
ship = {"2024H1": 838, "2024H2": 594, "2025Q1": 325, "2025Q2": 323, "2025Q3": 404, "2025Q4": 825 - 404,
        "2026Q1": 379, "2026Q2": 445, "2026Q3": 357, "2023H1": 1023, "2023H2": 880, "2022H2": 902, "2022H1": 959}
us = pd.read_csv(P / "stellantis_us_quarterly_sales.csv")
us = us[us.model == "Stellantis"].groupby("quarter").units.max()
ca = pd.read_csv(P / "stellantis_canada_quarterly_totals.csv").set_index("quarter").ca_units
mx = pd.read_csv(P / "inegi_stellantis_mexico_monthly.csv")
cur = mx[["month", "mx_sales"]]
prev = mx[["month", "mx_sales_prev_year"]].rename(columns={"mx_sales_prev_year": "mx_sales"})
prev = prev.assign(month=(pd.PeriodIndex(prev.month, freq="M") - 12).astype(str))
mxm = pd.concat([cur, prev]).drop_duplicates("month").set_index("month").mx_sales.sort_index()
# Jan 2026 report not published in the same path: impute Jan 2026 Mexico sales as the Feb-Mar 2026 average (flagged)
if "2026-01" not in mxm.index: mxm.loc["2026-01"] = round((mxm["2026-02"] + mxm["2026-03"]) / 2)
mxm = mxm.sort_index()
mxm.index = pd.PeriodIndex(mxm.index, freq="M")
mxq = mxm.groupby(mxm.index.asfreq("Q")).agg(["sum", "count"])
mxq.index = mxq.index.astype(str)
rows = []
def sales(qs):
    if any(q not in us.index or q not in ca.index or q not in mxq.index or mxq.loc[q, "count"] < 3 for q in qs): return None
    return sum(us[q] + ca[q] + mxq.loc[q, "sum"] for q in qs) / 1000
for per, s in ship.items():
    qs = [per] if "Q" in per else [f"{per[:4]}Q{i}" for i in ((1, 2) if per.endswith("H1") else (3, 4))]
    sl = sales(qs)
    if sl is None: continue
    rows.append(dict(period=per, shipments_k=s, us_ca_mx_sales_k=round(sl, 1), stock_build_k=round(s - sl, 1),
                     ship_to_sales=round(s / sl, 3)))
T = pd.DataFrame(rows).sort_values("period"); T.to_csv(OUT / "13_na_stock_identity.csv", index=False)
q = T[T.period.str.contains("Q")]
md = ["# 13. Are shipments running ahead of sales? North America channel-stock identity", "",
      "Stock build = NA shipments (Stellantis 6-K) − US sales (Stellantis releases) − Canada sales (FCA Canada releases) − "
      "Mexico sales (INEGI RAIAVL, Stellantis line; Jan 2026 imputed as the Feb-Mar average, about 8k). All in thousands.", "", md_table(T, index=False, fmt="{:.4g}"), "",
      f"Cumulative build 2025Q1-2026Q3: **{q.stock_build_k.sum():+.0f}k**; of which 2026Q1-Q3: **{q[q.period.str.startswith('2026')].stock_build_k.sum():+.0f}k**.", "",
      "Mexico exports (INEGI, Stellantis Mexico plants) for comparison: Q2+Q3 2026 = 235.9k vs 166.2k a year earlier (+42%); "
      "October 2026 exports -20% YoY after +5% production. Saltillo started Ram 1500 production and Toluca the Cherokee hybrid "
      "and Recon in 2026, so higher exports are partly new-model supply rather than stock."]
(OUT / "13_inventory_identity.md").write_text("\n".join(md) + "\n"); print("\n".join(md))
