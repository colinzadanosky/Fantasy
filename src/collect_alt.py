"""Alternative data: Google Trends (pytrends), Wikipedia pageviews (Wikimedia REST), NHTSA recalls (flat file)."""
import pathlib, time, io, zipfile, requests, pandas as pd, sys
from pytrends.request import TrendReq
ROOT = pathlib.Path(__file__).resolve().parents[1]; RAW = ROOT / "data/raw/alt"; RAW.mkdir(parents=True, exist_ok=True); P = ROOT / "data/processed"
which = set(sys.argv[1:]) or {"trends", "wiki", "nhtsa"}
TF = "2021-01-01 2026-10-31"
if "trends" in which:
    p = TrendReq(hl="en-US", tz=300, timeout=(10, 30))
    GROUPS = {"hemi": ["Ram Hemi", "Ram 1500", "Hemi", "Ram Hurricane"],
              "hybrid": ["Cherokee hybrid", "RAV4 hybrid", "Jeep Cherokee", "CR-V hybrid"],
              "price": ["Jeep price", "Jeep too expensive", "Jeep", "Jeep deals"],
              "brands": ["Jeep", "Dodge", "Chrysler", "Ford", "Toyota"],
              "brands2": ["Jeep", "Ram trucks", "Chevrolet", "Honda"],
              "charger": ["Dodge Charger", "Charger Daytona", "Charger Sixpack", "Jeep"]}
    out = []
    for g, kw in GROUPS.items():
        for i in range(4):
            try:
                p.build_payload(kw, timeframe=TF, geo="US"); d = p.interest_over_time(); break
            except Exception as e: print(g, "retry", e); time.sleep(20 * (i + 1))
        d = d.drop(columns="isPartial", errors="ignore").reset_index().melt("date", var_name="term", value_name="index"); d["group"] = g; out.append(d)
        time.sleep(8)
    # state-level interest in "Hemi" (relative within-state share of search)
    p.build_payload(["Hemi"], timeframe="2025-06-01 2026-10-31", geo="US")
    st = p.interest_by_region(resolution="REGION", inc_low_vol=True).reset_index(); st.to_csv(P / "trends_state_hemi.csv", index=False)
    pd.concat(out).to_csv(P / "google_trends_monthly.csv", index=False); print("trends ok")
if "wiki" in which:
    ARTS = {"Ram pickup": "Ram_pickup", "Wrangler": "Jeep_Wrangler", "Grand Cherokee": "Jeep_Grand_Cherokee",
            "Compass": "Jeep_Compass", "Cherokee": "Jeep_Cherokee", "Gladiator": "Jeep_Gladiator_(JT)",
            "Wagoneer family": "Jeep_Wagoneer_(WS)", "Durango": "Dodge_Durango", "Charger": "Dodge_Charger",
            "Hornet": "Dodge_Hornet", "Pacifica": "Chrysler_Pacifica_(minivan)", "Wagoneer S": "Jeep_Wagoneer_S",
            "ProMaster Van": "Ram_ProMaster", "Ford F-Series": "Ford_F-Series", "Chevrolet Silverado": "Chevrolet_Silverado",
            "Toyota RAV4": "Toyota_RAV4", "Ford Bronco": "Ford_Bronco"}
    S = requests.Session(); S.headers["User-Agent"] = "AutoDemandResearch/0.1 (academic research script; python-requests)"
    rows = []
    for k, a in ARTS.items():
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{a}/monthly/2016010100/2026103100"
        for i in range(6):
            r = S.get(url, timeout=60)
            if r.status_code == 200: break
            time.sleep(15 * (i + 1))
        if r.status_code != 200: print("wiki fail", k, r.status_code); continue
        for it in r.json()["items"]: rows.append(dict(model=k, article=a, month=it["timestamp"][:6], views=it["views"]))
        time.sleep(2)
    pd.DataFrame(rows).to_csv(P / "wikipedia_pageviews_monthly.csv", index=False); print("wiki rows", len(rows))
if "nhtsa" in which:
    z = RAW / "FLAT_RCL_POST_2010.zip"
    if not z.exists(): z.write_bytes(requests.get("https://static.nhtsa.gov/odi/ffdd/rcl/FLAT_RCL_POST_2010.zip", timeout=300).content)
    with zipfile.ZipFile(z) as zf:
        name = zf.namelist()[0]; raw = zf.read(name).decode("latin-1")
    cols = ["RECORD_ID","CAMPNO","MAKETXT","MODELTXT","YEARTXT","MFGCAMPNO","COMPNAME","MFGNAME","BGMAN","ENDMAN","RCLTYPECD","POTAFF",
            "ODATE","INFLUENCED_BY","MFGTXT","RCDATE","DATEA","RPNO","FMVSS","DESC_DEFECT","CONEQUENCE_DEFECT","CORRECTIVE_ACTION","NOTES","RCL_CMPT_ID",
            "MFR_COMP_NAME","MFR_COMP_DESC","MFR_COMP_PTNO","DO_NOT_DRIVE","PARK_OUTSIDE"]
    d = pd.read_csv(io.StringIO(raw), sep="\t", header=None, names=cols, dtype=str, on_bad_lines="skip", quoting=3)
    d = d[d.RCLTYPECD == "V"]
    d.to_csv(P / "nhtsa_vehicle_recalls_post2010.csv.gz", index=False, compression="gzip"); print("nhtsa rows", len(d), d.RCDATE.max())
