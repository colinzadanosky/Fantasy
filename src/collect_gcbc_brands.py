"""Annual US sales and share by brand from GoodCarBadCar brand pages (goodcarbadcar.net/<brand>-us-sales-figures/).
Collected 2026-11-12. Output: data/processed/gcbc_brand_annual.csv."""
import io, time, pathlib, requests, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; RAW = ROOT / "data/raw/gcbc_brand"; RAW.mkdir(parents=True, exist_ok=True)
BR = ["nissan", "infiniti", "chevrolet", "gmc", "buick", "cadillac", "pontiac", "saturn", "hummer", "jeep", "ram", "dodge",
      "chrysler", "fiat", "ford", "lincoln", "mercury", "toyota", "lexus", "honda", "hyundai", "kia", "subaru", "mazda", "volkswagen"]
rows = []
for b in BR:
    f = RAW / f"{b}.html"
    if not f.exists():
        r = requests.get(f"https://www.goodcarbadcar.net/{b}-us-sales-figures/", timeout=60)
        if r.status_code != 200: print(b, r.status_code); continue
        f.write_text(r.text); time.sleep(0.5)
    try: t = pd.read_html(io.StringIO(f.read_text()))
    except ValueError: print(b, "no table"); continue
    a = [x for x in t if "Year" in x.columns and "Sales" in x.columns]
    if not a: continue
    d = a[0].rename(columns=lambda c: "share" if "share" in c.lower() and "change" not in c.lower() else c)[["Year", "Sales", "share"]]
    d["brand"] = b; rows.append(d)
out = pd.concat(rows).rename(columns={"Year": "year", "Sales": "units"})
out.to_csv(ROOT / "data/processed/gcbc_brand_annual.csv", index=False)
print(out.pivot_table(index="year", columns="brand", values="units").loc[2004:].to_string())
