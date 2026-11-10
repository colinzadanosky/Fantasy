"""Download Stellantis (FCA US / FCA Canada) quarterly sales releases and their PDF sales charts.
Source: media.stellantisnorthamerica.com (release ids found via the site's search)."""
import re, requests, pathlib, json, time
OUT = pathlib.Path(__file__).resolve().parents[1] / "data/raw/stellantis_releases"
OUT.mkdir(parents=True, exist_ok=True)
US = {"2022Q3":24347,"2022Q4":24538,"2023Q1":24781,"2023Q2":25018,"2023Q3":25346,"2023Q4":25594,
      "2024Q1":25812,"2024Q2":None,"2024Q3":26253,"2024Q4":26525,"2025Q1":26695,"2025Q2":26902,
      "2025Q3":27093,"2025Q4":27358,"2026Q1":27622,"2026Q2":27875,"2026Q3":28061}
CA = {"2022Q3":24350,"2022Q4":24539,"2023Q1":24788,"2023Q2":25022,"2023Q3":25348,"2023Q4":25593,
      "2024Q1":25814,"2024Q2":25973,"2024Q3":26250,"2024Q4":26526,"2025Q1":26697,"2025Q2":26908,
      "2025Q3":27094,"2025Q4":27360,"2026Q1":27629,"2026Q2":27876,"2026Q3":28063}
H = {"User-Agent": "Mozilla/5.0 (research script)"}
def get(url):
    for i in range(4):
        try:
            r = requests.get(url, headers=H, timeout=40); r.raise_for_status(); return r
        except Exception as e:
            time.sleep(2 ** (i + 1)); err = e
    raise err
manifest = {}
for country, ids in (("US", US), ("CA", CA)):
    for q, rid in ids.items():
        if rid is None: continue
        html = get(f"https://media.stellantisnorthamerica.com/newsrelease.do?id={rid}").text
        (OUT / f"{country}_{q}.html").write_text(html, encoding="utf-8")
        pdfs = sorted(set(re.findall(r'href="(https?://[^"]+\.pdf)"', html)))
        files = []
        for j, p in enumerate(pdfs):
            fn = OUT / f"{country}_{q}_{j}.pdf"; fn.write_bytes(get(p).content); files.append((p, fn.name))
        manifest[f"{country}_{q}"] = {"release_id": rid, "pdfs": files}
        print(country, q, rid, len(pdfs))
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
