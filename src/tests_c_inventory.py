"""Section C - does it clear inventory? Tests 21-30. Only #28 is computable from public data; listing-based tests
are implemented in listings_models.py and run once the weekly scrape exists."""
import re, glob, html as H, numpy as np, pandas as pd
from common import *

W = stla_wide()


def canada_totals():
    """Quarterly Canadian sales totals quoted in FCA/Stellantis Canada releases."""
    files = sorted(glob.glob(str(ROOT / "data/raw/stellantis_releases/CA_*.html")))
    if not files: return pd.read_csv(P / "stellantis_canada_quarterly_totals.csv")
    rows = []
    for f in files:
        q = re.search(r"CA_(\d{4}Q\d)", f).group(1)
        t = H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", open(f, encoding="utf-8", errors="ignore").read())))
        m = re.search(r"(?:reports?|reported|sold|sales of)\D{0,60}?(\d{2},\d{3}) vehicles", t)
        rows.append(dict(quarter=q, ca_units=int(m.group(1).replace(",", "")) if m else np.nan, quote=m.group(0)[:120] if m else ""))
    d = pd.DataFrame(rows)
    # totals phrased differently in these releases (quoted sentences); 2024 and 2025 quarters reconcile to the stated
    # full-year totals (129,945 and 114,720)
    manual = {"2022Q3": 40958, "2022Q4": 38450, "2023Q1": 40073, "2024Q4": 30650, "2025Q4": 27340, "2026Q2": 32166}
    for k, v in manual.items(): d.loc[d.quarter == k, ["ca_units", "quote"]] = [v, "manual from release text"]
    d.to_csv(P / "stellantis_canada_quarterly_totals.csv", index=False)
    return d


def test28():
    na = pd.read_csv(P / "stellantis_na_segment_raw.csv")
    half = {}
    for _, r in na.iterrows():
        for side in ["cur", "prev"]:
            per = r[f"period_{side}"].replace(" Pro Forma", "")
            if re.match(r"^H[12] 20\d\d$", per) and per not in half:
                half[per] = r[f"shipments_k_{side}"]
    # quarterly 2025-26 -> halves
    q = {}
    for _, r in na.iterrows():
        for side in ["cur", "prev"]:
            per = r[f"period_{side}"]
            if re.match(r"^Q[1-4] 20\d\d$", per): q[per] = r[f"shipments_k_{side}"]
    if "Q1 2026" in q and "Q2 2026" in q: half["H1 2026"] = q["Q1 2026"] + q["Q2 2026"]
    ca = canada_totals().set_index("quarter").ca_units
    rows = []
    for per, ship in sorted(half.items(), key=lambda x: (x[0][3:], x[0][:2])):
        y, h = int(per[3:]), int(per[1])
        qs = [f"{y}Q{k}" for k in ((1, 2) if h == 1 else (3, 4))]
        us = sum(W.loc[x, "Stellantis"] for x in qs if x in W.index) / 1000 if all(x in W.index for x in qs) else np.nan
        cav = sum(ca.get(x, np.nan) for x in qs) / 1000
        rows.append(dict(half=per, na_shipments_k=ship, us_sales_k=us, canada_sales_k=cav, ship_minus_uscan_k=ship - us - cav))
    d = pd.DataFrame(rows); d.to_csv(OUT / "details/test_28_shipments_vs_sales.csv", index=False)
    print(d.to_string())
    record(28, "NA shipments minus US+Canada retail-reported sales, by half-year", "DESCRIPTIVE", n=len(d),
           spec="ship - (US sales + Canada sales); residual also includes Mexico sales (not reported) and fleet timing",
           data="Stellantis 6-K results (SEC EDGAR); US and Canada sales releases",
           note="See details/test_28_shipments_vs_sales.csv. A rising residual = dealer stock build (shipment push); H2 2024 shows the "
                "drawdown Stellantis described ('dealer inventory reduced by over 50,000 units' in Q3 2024).")


def blocked():
    B = {21: "VIN exit-rate hazard model ~ powertrain + price band + metro", 22: "Days listed ~ powertrain | trim, price",
         24: "Dealer inventory depth ~ powertrain mix", 26: "Prior-model-year share ~ powertrain",
         27: "Exit rate ~ price band, Stellantis vs Ford", 29: "Exit rate ~ distance from metro center",
         30: "Exit rate ~ color/package, same powertrain"}
    for k, t in B.items():
        record(k, t, "BLOCKED", note="Needs the weekly listings scrape (VIN, powertrain via NHTSA vPIC decode, price, dealer, first/last seen). "
               "Model code is ready in src/listings_models.py; it cannot be backfilled, so collection must start now. Check site terms before scraping.")
    record(23, "Days' supply by model ~ # powertrain variants", "BLOCKED", note="Cox model-level days' supply is not public (vAuto subscription).")
    record(25, "Brand days' supply ~ production cuts", "BLOCKED", note="No public brand days' supply series; production cuts appear only as text in releases.")


if __name__ == "__main__":
    test28(); blocked()
    pd.DataFrame(RESULTS).to_csv(OUT / "results_C.csv", index=False)
