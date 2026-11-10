"""Cox Automotive / Kelley Blue Book monthly report PDFs: ATP tables (brand, manufacturer, segment ATP)
and inventory (days' supply) data files, discovered from coxautoinc.com insight sitemaps."""
import re, time, pathlib, requests, json
ROOT = pathlib.Path(__file__).resolve().parents[1]; RAW = ROOT / "data/raw/cox"; RAW.mkdir(parents=True, exist_ok=True)
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0"
def get(u):
    for i in range(4):
        try:
            r = S.get(u, timeout=60)
            if r.status_code == 200: return r
            if r.status_code == 404: return None
        except Exception: pass
        time.sleep(2 ** (i + 1))
idx = get("https://www.coxautoinc.com/sitemap_index.xml").text
pages = []
for sm in re.findall(r"<loc>(https://www.coxautoinc.com/insight-sitemap\d*\.xml)</loc>", idx):
    pages += re.findall(r"<loc>([^<]+)</loc>", get(sm).text)
cand = [p for p in pages if re.search(r"(atp|transaction-price|inventory|days-supply|incentive)", p) and re.search(r"20(2[2-6])", p)]
print(len(pages), "insight pages;", len(cand), "candidates")
pdfs = {}
for p in cand:
    r = get(p)
    if not r: continue
    for u in set(re.findall(r'https://www.coxautoinc.com/wp-content/uploads/[^"\'\s]+\.pdf', r.text)):
        if re.search(r"(?i)(transaction|atp|inventory|supply)", u): pdfs[u] = p
    time.sleep(0.3)
for u in sorted(pdfs):
    f = RAW / u.split("/uploads/")[1].replace("/", "_")
    if not f.exists():
        r = get(u)
        if r: f.write_bytes(r.content)
    print(f.name)
(RAW / "manifest.json").write_text(json.dumps(pdfs, indent=1))
