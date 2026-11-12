"""Parse Stellantis Mexico monthly production / exports / domestic sales from INEGI RAIAVL monthly summaries
(rm_raiavlYYYY_MM.pdf, https://www.inegi.org.mx/contenidos/datosprimarios/iavl/doc/YYYY/). Each PDF gives the month
and YTD for the current and prior year; we keep the current-year month value."""
import glob, re, subprocess, pathlib, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; RAW = ROOT / "data/raw/inegi"
num = lambda s: int(s.replace(" ", "")) if s and s.strip() else None
rows = []
for f in sorted(glob.glob(str(RAW / "rm_*.pdf"))):
    y, m = re.search(r"rm_(\d{4})_(\d\d)", f).groups()
    try: t = subprocess.run(["pdftotext", "-layout", f, "-"], capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError: continue
    if f"{y}" not in t: continue
    N = r"(\d{1,3}(?: \d{3})*)"
    pat = r"Stellantis ?(\d)/\s+" + N + r"\s+" + N + r"\s+(-? ?[\d.]+)(?:\s+" + N + r"\s+" + N + r")?"
    hits = re.findall(pat, t)
    rec = {"month": f"{y}-{m}"}
    foot = pd.Series([h[0] for h in hits]).value_counts()
    fp = foot[foot >= 2].index
    if len(fp):
        pe = [h for h in hits if h[0] == fp[0]]
        rec.update(prod=num(pe[0][2]), prod_prev_year=num(pe[0][1]), exports=num(pe[1][2]), exports_prev_year=num(pe[1][1]))
        if pe[0][4]: rec.update(prod_ytd=num(pe[0][5]), prod_ytd_prev=num(pe[0][4]), exports_ytd=num(pe[1][5]), exports_ytd_prev=num(pe[1][4]))
    dom = [h for h in hits if h[0] not in set(fp)]
    if dom: rec.update(mx_sales=num(dom[0][2]), mx_sales_prev_year=num(dom[0][1]))
    rows.append(rec)
d = pd.DataFrame(rows).dropna(subset=["prod"]).drop_duplicates("month")
d.to_csv(ROOT / "data/processed/inegi_stellantis_mexico_monthly.csv", index=False); print(d.to_string())
