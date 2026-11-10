"""Monthly US and Canada model sales from GoodCarBadCar (GCBC) model pages.
Note: for automakers that report quarterly (Stellantis, GM, Toyota since 2024?, etc.) GCBC's
monthly values are estimates; analysis uses quarterly sums only."""
import re, time, pathlib, requests, io, pandas as pd
from bs4 import BeautifulSoup
ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/gcbc"; RAW.mkdir(parents=True, exist_ok=True)
SLUGS = {  # model -> (segment, slug)
 # full-size pickup
 "Ford F-Series": ("fullsize_pickup", "ford-f-series"), "Chevrolet Silverado": ("fullsize_pickup", "chevrolet-silverado"),
 "GMC Sierra": ("fullsize_pickup", "gmc-sierra"), "Toyota Tundra": ("fullsize_pickup", "toyota-tundra"),
 "Nissan Titan": ("fullsize_pickup", "nissan-titan"), "Ram pickup (GCBC)": ("fullsize_pickup", "dodge-ram"),
 # midsize pickup
 "Toyota Tacoma": ("midsize_pickup", "toyota-tacoma"), "Chevrolet Colorado": ("midsize_pickup", "chevrolet-colorado"),
 "GMC Canyon": ("midsize_pickup", "gmc-canyon"), "Ford Ranger": ("midsize_pickup", "ford-ranger"),
 "Nissan Frontier": ("midsize_pickup", "nissan-frontier"), "Jeep Gladiator": ("midsize_pickup", "jeep-gladiator"),
 # compact SUV
 "Toyota RAV4": ("compact_suv", "toyota-rav4"), "Honda CR-V": ("compact_suv", "honda-cr-v"),
 "Nissan Rogue": ("compact_suv", "nissan-rogue"), "Ford Escape": ("compact_suv", "ford-escape"),
 "Chevrolet Equinox": ("compact_suv", "chevrolet-equinox"), "Hyundai Tucson": ("compact_suv", "hyundai-tucson"),
 "Kia Sportage": ("compact_suv", "kia-sportage"), "Subaru Forester": ("compact_suv", "subaru-forester"),
 "Mazda CX-5": ("compact_suv", "mazda-cx-5"), "Jeep Compass": ("compact_suv", "jeep-compass"),
 "Jeep Cherokee": ("compact_suv", "jeep-cherokee"), "Ford Bronco Sport": ("compact_suv", "ford-bronco-sport"),
 # midsize SUV
 "Ford Explorer": ("midsize_suv", "ford-explorer"), "Toyota Highlander": ("midsize_suv", "toyota-highlander"),
 "Toyota Grand Highlander": ("midsize_suv", "toyota-grand-highlander"), "Chevrolet Traverse": ("midsize_suv", "chevrolet-traverse"),
 "Kia Telluride": ("midsize_suv", "kia-telluride"), "Hyundai Palisade": ("midsize_suv", "hyundai-palisade"),
 "Honda Pilot": ("midsize_suv", "honda-pilot"), "Toyota 4Runner": ("midsize_suv", "toyota-4runner"),
 "Jeep Grand Cherokee": ("midsize_suv", "jeep-grand-cherokee"), "Dodge Durango": ("midsize_suv", "dodge-durango"),
 # off-road
 "Jeep Wrangler": ("offroad_suv", "jeep-wrangler"), "Ford Bronco": ("offroad_suv", "ford-bronco"),
 # large SUV
 "Chevrolet Tahoe": ("large_suv", "chevrolet-tahoe"), "Chevrolet Suburban": ("large_suv", "chevrolet-suburban"),
 "Ford Expedition": ("large_suv", "ford-expedition"), "GMC Yukon": ("large_suv", "gmc-yukon"),
 "Toyota Sequoia": ("large_suv", "toyota-sequoia"), "Jeep Wagoneer": ("large_suv", "jeep-wagoneer"),
 "Jeep Grand Wagoneer": ("large_suv", "jeep-grand-wagoneer"),
 # minivan
 "Toyota Sienna": ("minivan", "toyota-sienna"), "Honda Odyssey": ("minivan", "honda-odyssey"),
 "Kia Carnival": ("minivan", "kia-carnival-sedona"), "Chrysler Pacifica": ("minivan", "chrysler-pacifica"),
 # muscle / performance car
 "Ford Mustang": ("muscle_car", "ford-mustang"), "Chevrolet Camaro": ("muscle_car", "chevrolet-camaro"),
 "Dodge Charger": ("muscle_car", "dodge-charger"), "Dodge Challenger": ("muscle_car", "dodge-challenger"),
}
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
def fetch(slug):
    f = RAW / f"{slug}.html"
    if f.exists() and f.stat().st_size > 10000: return f.read_text(encoding="utf-8", errors="ignore")
    for i in range(4):
        try:
            r = requests.get(f"https://www.goodcarbadcar.net/{slug}-sales-figures/", headers={"User-Agent": "Mozilla/5.0"}, timeout=40)
            if r.status_code == 200 and len(r.text) > 10000:
                f.write_text(r.text, encoding="utf-8"); return r.text
            return None
        except Exception: time.sleep(2 ** (i + 1))
def monthly_tables(html):
    soup = BeautifulSoup(html, "lxml"); out = {}
    for h in soup.find_all(["h2", "h3"]):
        t = h.get_text(" ", strip=True)
        country = "US" if "United States" in t else "CA" if "Canada" in t else None
        if not country or country in out: continue
        for tab in h.find_all_next("table", limit=3):
            if "Jan" in tab.find("tr").get_text():
                df = pd.read_html(io.StringIO(str(tab)))[0]; out[country] = df; break
    return out
rows, missing = [], []
for model, (seg, slug) in SLUGS.items():
    html = fetch(slug)
    if not html: missing.append(model); continue
    for country, df in monthly_tables(html).items():
        for _, r in df.iterrows():
            yr = re.match(r"\d{4}", str(r["Year"]))
            if not yr: continue
            for i, m in enumerate(MONTHS):
                v = str(r.get(m, "")).replace(",", "")
                if re.fullmatch(r"\d+", v):
                    rows.append(dict(model=model, segment=seg, country=country, year=int(yr.group()), month=i + 1, units=int(v)))
    time.sleep(0.5)
df = pd.DataFrame(rows)
df["quarter"] = df.year.astype(str) + "Q" + ((df.month - 1) // 3 + 1).astype(str)
df.to_csv(ROOT / "data/processed/gcbc_monthly_sales.csv", index=False)
q = df.groupby(["model", "segment", "country", "quarter"], as_index=False).agg(units=("units", "sum"), months=("month", "nunique"))
q = q[q.months == 3].drop(columns="months")
q.to_csv(ROOT / "data/processed/gcbc_quarterly_sales.csv", index=False)
print("missing:", missing); print(q[q.country == "US"].groupby("model").quarter.agg(["min", "max", "count"]).to_string())
