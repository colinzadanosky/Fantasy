"""Download Stellantis annual reports (20-F) and interim reports (6-K 'STELLANTIS N.V. H1/Q1/Q3 20xx') from SEC
EDGAR. These carry the MD&A segment AOI walks (Volume & Mix, Net price, Industrial costs, SG&A, R&D, FX & other)."""
import re, time, pathlib, requests
ROOT = pathlib.Path(__file__).resolve().parents[1]; RAW = ROOT / "data/raw/sec_mdna"; RAW.mkdir(parents=True, exist_ok=True)
H = {"User-Agent": "AutoDemandResearch research-script admin@example.org"}
sub = requests.get("https://data.sec.gov/submissions/CIK0001605484.json", headers=H, timeout=60).json()["filings"]["recent"]
for form, dt, acc, desc, doc in zip(sub["form"], sub["filingDate"], sub["accessionNumber"], sub["primaryDocDescription"], sub["primaryDocument"]):
    if dt < "2021-06-01": continue
    if form == "20-F" and "ANNUAL" in (desc or "") or form == "20-F":
        tag = f"20F_{dt[:4]}"
    elif form == "6-K" and re.fullmatch(r"6-K STELLANTIS N\.V\. (H1|Q[1-3]) 20\d\d", desc or ""):
        m = re.search(r"(H1|Q[1-3]) (20\d\d)", desc); tag = f"interim_{m.group(2)}_{m.group(1)}"
    else: continue
    base = f"https://www.sec.gov/Archives/edgar/data/1605484/{acc.replace('-', '')}"
    idx = requests.get(base + "/index.json", headers=H, timeout=60).json()["directory"]["item"]
    for it in idx:
        n = it["name"]
        if not re.search(r"\.htm$", n, re.I) or re.search(r"index|^ex\d|exhibit|^R\d+\.htm$", n, re.I): continue
        f = RAW / f"{tag}_{n}"
        if not f.exists():
            f.write_bytes(requests.get(f"{base}/{n}", headers=H, timeout=300).content); time.sleep(0.3)
        print(tag, n, f.stat().st_size)
    time.sleep(0.3)
