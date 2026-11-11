"""NHTSA owner complaints for Ram 1500 (all cab variants, excl. 1500 Classic) MY2019-2027 via api.nhtsa.gov."""
import json, pathlib, time, requests, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; RAW = ROOT / "data/raw/nhtsa"; RAW.mkdir(parents=True, exist_ok=True)
A = "https://api.nhtsa.gov"
def get(url):
    for k in range(5):
        r = requests.get(url, timeout=120)
        if r.status_code == 200: return r.json()
        time.sleep(2 ** (k + 1))
    r.raise_for_status()
rows = []
for y in range(2019, 2028):
    models = {m["model"] for m in get(f"{A}/products/vehicle/models?modelYear={y}&make=RAM&issueType=c")["results"]}
    for m in sorted(x for x in models if "1500" in x and "CLASSIC" not in x.upper() and "PROMASTER" not in x.upper()):
        f = RAW / f"complaints_{y}_{m.replace(' ', '_').replace('/', '-')}.json"
        if not f.exists():
            f.write_text(json.dumps(get(f"{A}/complaints/complaintsByVehicle?make=RAM&model={requests.utils.quote(m)}&modelYear={y}")))
            time.sleep(0.3)
        for c in json.loads(f.read_text()).get("results", []):
            rows.append(dict(model_year=y, model=m, odi=c.get("odiNumber"), date_received=c.get("dateComplaintFiled"),
                             components=c.get("components"), summary=c.get("summary"), crash=c.get("crash"), fire=c.get("fire")))
d = pd.DataFrame(rows).drop_duplicates("odi")
d.to_csv(ROOT / "data/processed/nhtsa_complaints_ram1500.csv.gz", index=False); print(d.groupby("model_year").size())
