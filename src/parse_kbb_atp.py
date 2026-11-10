"""Parse KBB monthly ATP data-table PDFs -> long table (month, table, entity, atp). Uses the current-month
column; year-ago column fills months before the first report (back to 2022)."""
import re, glob, subprocess, pathlib, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
MON = {m: i + 1 for i, m in enumerate(["January","February","March","April","May","June","July","August","September","October","November","December"])}
rows = []
for f in sorted(glob.glob(str(ROOT / "data/raw/cox/*.pdf"))):
    t = subprocess.run(["pdftotext", "-layout", f, "-"], capture_output=True, text=True).stdout
    m = re.search(r"Data Tables for (\w+)\s+(20\d\d)", t)
    if not m: print("no title", f); continue
    y, mo = int(m.group(2)), MON[m.group(1)]
    table = None
    for line in t.splitlines():
        h = re.match(r"^\s*(Manufacturer|Make|Category|Segment)\s", line)
        if h: table = {"Manufacturer": "manufacturer", "Make": "make", "Category": "segment", "Segment": "segment"}[h.group(1)]; continue
        r = re.match(r"^\s*([A-Za-z][A-Za-z0-9 ./&\-]+?)\s+\$([\d,]+)\s+\$([\d,]+)\s+\$?([\d,]+)", line)
        if r and table:
            ent = r.group(1).strip(); ent = "Industry Average" if ent == "Industry" else ent; cur, prv, ya = (int(x.replace(",", "")) for x in r.group(2, 3, 4))
            rows.append(dict(month=f"{y}-{mo:02d}", table=table, entity=ent, atp=cur, src="current", file=pathlib.Path(f).name))
            rows.append(dict(month=f"{y - 1}-{mo:02d}", table=table, entity=ent, atp=ya, src="year_ago", file=pathlib.Path(f).name))
d = pd.DataFrame(rows)
d["pri"] = (d.src == "current").astype(int)
d = d.sort_values(["table", "entity", "month", "pri"]).groupby(["table", "entity", "month"]).tail(1).drop(columns="pri")
d.to_csv(ROOT / "data/processed/kbb_atp_monthly.csv", index=False)
w = d[d.entity.isin(["Stellantis", "Jeep", "Ram", "Dodge", "Chrysler", "Industry Average"]) & d.table.isin(["make", "manufacturer"])]
w = w.pivot_table(index="month", columns=["table", "entity"], values="atp")
print(w.to_string()); print(sorted(d[d.table == "segment"].entity.unique()))
