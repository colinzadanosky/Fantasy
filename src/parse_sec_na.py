"""Parse North America segment KPIs (shipments 000s, net revenues EUR m, AOI EUR m, AOI margin) from
Stellantis results press releases (SEC 6-K exhibits). Each block gives current and prior-year period."""
import re, glob, pathlib, pandas as pd
from bs4 import BeautifulSoup
ROOT = pathlib.Path(__file__).resolve().parents[1]
def num(s):
    s = s.strip().replace(",", "").replace("%", "")
    neg = s.startswith("(") and s.endswith(")"); s = s.strip("()")
    try: v = float(s)
    except ValueError: return None
    return -v if neg else v
PER = r"((?:Q[1-4]|H[12]|YTD|FY)?\s?20\d\d(?: Pro Forma)?(?:\s?\(\d\))?)"
rows = []
for f in sorted(glob.glob(str(ROOT / "data/raw/sec/*_press_*.htm"))):
    txt = BeautifulSoup(open(f, encoding="utf-8", errors="ignore").read(), "lxml").get_text("\n", strip=True).replace("\n", " | ")
    for m in re.finditer(r"NORTH AMERICA \| ENLARGED EUROPE \| [^|]*\| " + PER + r" \| " + PER, txt):
        p1, p0 = m.group(1).strip(), m.group(2).strip(); seg = txt[m.end(): m.end() + 900]
        rec = dict(file=pathlib.Path(f).name, period_cur=p1, period_prev=p0)
        for key, pat in [("shipments_k", r"Shipments \| \(000s\) \| ([^|]+) \| ([^|]+)"),
                         ("net_revenues_eur_m", r"Net revenues \| ([^|]+) \| ([^|]+)"),
                         ("aoi_eur_m", r"AOI \| ([^|]+) \| ([^|]+)"),
                         ("aoi_margin_pct", r"AOI margin \| ([^|]+) \| ([^|]+)")]:
            mm = re.search(pat, seg)
            if mm: rec[key + "_cur"], rec[key + "_prev"] = num(mm.group(1)), num(mm.group(2))
        rows.append(rec)
d = pd.DataFrame(rows); print(d.to_string())
d.to_csv(ROOT / "data/processed/stellantis_na_segment_raw.csv", index=False)
