"""New York DMV registrations (data.ny.gov w4pv-hbkt, VIN-level snapshot, refreshed ~monthly) for full-size pickup
makes, model years 2023+. Then decode distinct VIN patterns with NHTSA vPIC (model, engine, trim).
Outputs data/raw/ny_dmv/ny_pickup_registrations.csv.gz (one row per VIN; not committed - VIN/ZIP level)."""
import pathlib, time, requests, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; RAW = ROOT / "data/raw/ny_dmv"; RAW.mkdir(parents=True, exist_ok=True)
URL = "https://data.ny.gov/resource/w4pv-hbkt.json"
MAKES = ["RAM", "FORD", "CHEVR", "GMC", "TOYOT", "NISSA"]
raw = RAW / "ny_pickups_my2023plus.csv.gz"
if not raw.exists():
    out = []
    for mk in MAKES:
        off = 0
        while True:
            q = {"$select": "vin,registration_class,county,zip,model_year,make,body_type,fuel_type,maximum_gross_weight,reg_valid_date",
                 "$where": f"record_type='VEH' and make='{mk}' and body_type='PICK' and model_year>='2023'",
                 "$order": "vin", "$limit": 50000, "$offset": off}
            r = requests.get(URL, params=q, timeout=300); r.raise_for_status(); d = r.json()
            out += d; print(mk, off, len(d)); off += 50000
            if len(d) < 50000: break
    pd.DataFrame(out).to_csv(raw, index=False)
df = pd.read_csv(raw, dtype=str)
df = df[df.vin.str.len() == 17].drop_duplicates("vin")
df["pattern"] = df.vin.str[:8] + df.vin.str[9:11]          # vPIC decodes on positions 1-8, 10-11
dec_f = RAW / "vpic_patterns.csv"
dec = pd.read_csv(dec_f, dtype=str) if dec_f.exists() else pd.DataFrame(columns=["pattern"])
todo = df.drop_duplicates("pattern")
todo = todo[~todo.pattern.isin(dec.pattern)]
print("patterns to decode", len(todo))
KEEP = ["Make", "Model", "ModelYear", "Trim", "Series", "BodyCabType", "DisplacementL", "EngineCylinders", "EngineModel",
        "FuelTypePrimary", "ElectrificationLevel", "GVWR", "DriveType"]
rows = []
for i in range(0, len(todo), 50):
    chunk = todo.iloc[i:i + 50]
    for k in range(4):
        try:
            r = requests.post("https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValuesBatch/",
                              data={"format": "json", "data": ";".join(chunk.vin)}, timeout=120); r.raise_for_status(); break
        except Exception as e:
            time.sleep(2 ** (k + 1))
    for v, res in zip(chunk.pattern, r.json()["Results"]):
        rows.append({"pattern": v, **{k: res.get(k, "") for k in KEEP}})
    if i % 1000 == 0:
        print("decoded", i); pd.concat([dec, pd.DataFrame(rows)]).to_csv(dec_f, index=False)
    time.sleep(0.2)
dec = pd.concat([dec, pd.DataFrame(rows)]); dec.to_csv(dec_f, index=False)
m = df.merge(dec, on="pattern", how="left")
m.to_csv(RAW / "ny_pickup_registrations.csv.gz", index=False)   # VIN-level: kept out of git
print(m.shape)
