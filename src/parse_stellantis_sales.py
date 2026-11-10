"""Parse Stellantis/FCA US quarterly sales chart PDFs -> long panel (model, quarter, units).
Each PDF has current-quarter and prior-year-quarter columns; the current-year figure from a
quarter's own release takes precedence, prior-year columns fill gaps (e.g. 2024Q2, 2021Q3-2022Q2)."""
import re, subprocess, pathlib, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/stellantis_releases"
NUM = r"(-?[\d,]+)"
# harmonise nameplates across release formats
ALIASES = {"Cherokee HEV": "Cherokee", "Ram P/U": "Ram PU (total)", "TOTAL Ram PU": "Ram PU (total)",
           "Charger": "Charger ICE", "FCA US LLC": "STELLANTIS US", "Alfa 4C": "4C",
           "Wagoneer": "Wagoneer family", "Grand Wagoneer": "Wagoneer family", "Wagoneer/G. Wagoneer": "Wagoneer family"}
BRAND_ROWS = {"JEEP BRAND": "Jeep", "RAM BRAND": "Ram", "CHRYSLER BRAND": "Chrysler", "DODGE BRAND": "Dodge",
              "FIAT BRAND": "Fiat", "ALFA ROMEO": "Alfa Romeo", "STELLANTIS US": "Stellantis"}
def prev_year(q): return f"{int(q[:4]) - 1}{q[4:]}"
rows = []
for pdf in sorted(RAW.glob("US_*_0.pdf")):
    q = pdf.stem.split("_")[1]
    txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    brand = "Jeep"
    for line in txt.splitlines():
        m = re.match(r"^\s*([A-Za-z0-9][A-Za-z0-9 /&.\-]*?)\s{2,}" + NUM + r"\s+" + NUM + r"(\s|$)", line)
        if not m: continue
        name = ALIASES.get(m.group(1).strip(), m.group(1).strip())
        cur, pr = (int(x.replace(",", "")) for x in (m.group(2), m.group(3)))
        is_brand = name in BRAND_ROWS
        if is_brand: bname = BRAND_ROWS[name]
        rows.append(dict(release=q, model=bname if is_brand else name, brand=BRAND_ROWS.get(name) if is_brand else brand,
                         level="brand" if is_brand else "model", quarter=q, units=cur, src="current"))
        rows.append(dict(release=q, model=bname if is_brand else name, brand=BRAND_ROWS.get(name) if is_brand else brand,
                         level="brand" if is_brand else "model", quarter=prev_year(q), units=pr, src="prior"))
        if is_brand and name != "STELLANTIS US":  # rows after a brand total belong to the next brand
            brand = {"Jeep": "Ram", "Ram": "Chrysler", "Chrysler": "Dodge", "Dodge": "Fiat", "Fiat": "Alfa Romeo"}.get(bname, brand)
df = pd.DataFrame(rows)
df = df.groupby(["release", "model", "brand", "level", "quarter", "src"], as_index=False).units.sum()
df["pri"] = (df.src == "current").astype(int)
df = df.sort_values(["model", "quarter", "pri", "release"]).groupby(["model", "quarter"]).tail(1)
# Ram pickup total = LD + HD where the total row is absent (2026 format)
ld = df[df.model.isin(["Ram LD PU", "Ram HD PU"])].groupby("quarter").units.agg(["sum", "count"])
have = set(df[df.model == "Ram PU (total)"].quarter)
add = [dict(brand="Ram", level="model", model="Ram PU (total)", quarter=q, units=r["sum"])
       for q, r in ld.iterrows() if r["count"] == 2 and q not in have]
df = pd.concat([df, pd.DataFrame(add)])
df = df[["brand", "level", "model", "quarter", "units"]].sort_values(["level", "brand", "model", "quarter"])
df.to_csv(ROOT / "data/processed/stellantis_us_quarterly_sales.csv", index=False)
wide = df.pivot_table(index="quarter", columns="model", values="units", aggfunc="sum")
print(wide[["Jeep","Ram","Dodge","Stellantis","Ram LD PU","Ram HD PU","Ram PU (total)","Cherokee","Charger ICE","Charger BEV","Durango"]].to_string())
# integrity check: brand totals vs sum of models
chk = df[(df.level=="model")&~df.model.isin(["Ram LD PU","Ram HD PU"])].groupby(["brand","quarter"]).units.sum().unstack(0)
b = wide[["Jeep","Ram","Chrysler","Dodge"]]
ram_models = df[(df.level=="model")&(df.brand=="Ram")&(df.model!="Ram PU (total)")].groupby(["quarter","model"]).units.sum().unstack()
print("max abs gap Jeep:", (chk["Jeep"]-b["Jeep"]).abs().max(), "Dodge:", (chk["Dodge"]-b["Dodge"]).abs().max(), "Chrysler:", (chk["Chrysler"]-b["Chrysler"]).abs().max())

gap = (chk["Chrysler"]-b["Chrysler"]); print(gap[gap.abs()>5])
print((chk["Jeep"]-b["Jeep"])[lambda x: x.abs()>5]); print((chk["Ram"]-b["Ram"])[lambda x: x.abs()>5])
