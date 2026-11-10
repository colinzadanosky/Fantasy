"""Download Stellantis results press-release / supplemental 6-K exhibits from SEC EDGAR (CIK 1605484)."""
import json, re, time, pathlib, requests
ROOT = pathlib.Path(__file__).resolve().parents[1]; RAW = ROOT / "data/raw/sec"; RAW.mkdir(parents=True, exist_ok=True)
H = {"User-Agent": "AutoDemandResearch research-script admin@example.org"}
sub = requests.get("https://data.sec.gov/submissions/CIK0001605484.json", headers=H, timeout=60).json()["filings"]["recent"]
for form, dt, acc, desc in zip(sub["form"], sub["filingDate"], sub["accessionNumber"], sub["primaryDocDescription"]):
    if dt < "2021-04-01" or form != "6-K" or not re.search(r"(PRESS RELEASE|SUPPLEMENTAL)", desc or ""): continue
    tag = re.search(r"(Q[1-4]|H1|FY) (20\d\d)", desc); tag = f"{tag.group(2)}_{tag.group(1)}" if tag else dt
    kind = "press" if "PRESS" in desc else "supp"
    base = f"https://www.sec.gov/Archives/edgar/data/1605484/{acc.replace('-', '')}"
    idx = requests.get(base + "/index.json", headers=H, timeout=60).json()["directory"]["item"]
    for it in idx:
        n = it["name"]
        if re.search(r"\.htm$", n, re.I) and not re.search(r"index|^a6-?k", n, re.I):
            f = RAW / f"{tag}_{kind}_{n}"
            if not f.exists(): f.write_bytes(requests.get(f"{base}/{n}", headers=H, timeout=120).content); time.sleep(0.3)
            print(tag, kind, n, f.stat().st_size)
    time.sleep(0.3)
