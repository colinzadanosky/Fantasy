"""Extract release body text and sentences mentioning retail / fleet / conquest / inventory / Hemi."""
import re, glob, html as H, pathlib, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
rows = []
for f in sorted(glob.glob(str(ROOT / "data/raw/stellantis_releases/*_20*.html"))):
    h = open(f, encoding="utf-8", errors="ignore").read()
    t = H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", h))))
    s0 = t.find("Report"); e = t.find("About Stellantis"); t = t[max(0, s0 - 400): e if e > 0 else s0 + 20000]
    key = pathlib.Path(f).stem
    for s in re.split(r"(?<=[.!?])\s+|\s{2,}", t):
        if re.search(r"(?i)\bfleet|\bretail|conquest|inventory|days.? supply|market share|HEMI|Hurricane|hybrid", s):
            rows.append(dict(release=key, sentence=s.strip()[:500]))
d = pd.DataFrame(rows).drop_duplicates(); d.to_csv(ROOT / "data/processed/release_text_mentions.csv", index=False)
for k, g in d.groupby("release"):
    print("==", k); [print("  -", s[:230]) for s in g.sentence if re.search(r"(?i)fleet|retail|conquest|inventory", s)][:12]
