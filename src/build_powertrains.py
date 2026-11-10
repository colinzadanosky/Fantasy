"""Powertrain lineups by nameplate x model year from EPA fueleconomy.gov vehicles.csv.
A powertrain = (electrification type, displacement, cylinders). Count + flags (hybrid, PHEV, EV, V8, diesel).
Heavy-duty pickups (Ram 2500/3500) are not EPA-rated, so Ram HD is not covered."""
import zipfile, re, pathlib, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
z = zipfile.ZipFile(ROOT / "data/raw/epa/vehicles.csv.zip"); d = pd.read_csv(z.open("vehicles.csv"), low_memory=False)
d = d[d.year >= 2018]
MAP = {  # sales nameplate -> (make, regex on EPA model)
 "Wrangler": ("Jeep", r"^Wrangler"), "Gladiator": ("Jeep", r"^Gladiator"), "Grand Cherokee": ("Jeep", r"^Grand Cherokee"),
 "Cherokee": ("Jeep", r"^Cherokee"), "Compass": ("Jeep", r"^Compass"), "Renegade": ("Jeep", r"^Renegade"),
 "Wagoneer family": ("Jeep", r"^(Grand )?Wagoneer(?! S)"), "Wagoneer S": ("Jeep", r"^Wagoneer S"), "Recon": ("Jeep", r"^Recon"),
 "Ram LD PU": ("Ram", r"^(Ram )?1500"), "ProMaster Van": ("Ram", r"ProMaster(?! City)"), "ProMaster City": ("Ram", r"ProMaster City"),
 "Durango": ("Dodge", r"^Durango"), "Hornet": ("Dodge", r"^Hornet"), "Charger ICE": ("Dodge", r"^Charger(?!.*Daytona)"),
 "Charger BEV": ("Dodge", r"^Charger.*Daytona"), "Challenger": ("Dodge", r"^Challenger"),
 "Pacifica": ("Chrysler", r"^Pacifica"), "Voyager": ("Chrysler", r"^Voyager"), "300": ("Chrysler", r"^300"),
 "Giulia": ("Alfa Romeo", r"^Giulia"), "Stelvio": ("Alfa Romeo", r"^Stelvio"), "Tonale": ("Alfa Romeo", r"^Tonale"),
 "500X": ("Fiat", r"^500X"), "500e": ("Fiat", r"^500e"),
 # rivals (for segment coverage)
 "Ford F-Series": ("Ford", r"^F150"), "Chevrolet Silverado": ("Chevrolet", r"^Silverado.*(1500|EV)|^Silverado (2WD|4WD)"),
 "GMC Sierra": ("GMC", r"^Sierra.*(1500|EV)|^Sierra (2WD|4WD)"), "Toyota Tundra": ("Toyota", r"^Tundra"),
 "Toyota Tacoma": ("Toyota", r"^Tacoma"), "Chevrolet Colorado": ("Chevrolet", r"^Colorado"), "GMC Canyon": ("GMC", r"^Canyon"),
 "Ford Ranger": ("Ford", r"^Ranger"), "Nissan Frontier": ("Nissan", r"^Frontier"),
 "Toyota RAV4": ("Toyota", r"^RAV4"), "Honda CR-V": ("Honda", r"^CR-V"), "Nissan Rogue": ("Nissan", r"^Rogue(?! Sport)"),
 "Ford Escape": ("Ford", r"^Escape"), "Chevrolet Equinox": ("Chevrolet", r"^Equinox"), "Hyundai Tucson": ("Hyundai", r"^Tucson"),
 "Kia Sportage": ("Kia", r"^Sportage"), "Subaru Forester": ("Subaru", r"^Forester"), "Mazda CX-5": ("Mazda", r"^CX-5"),
 "Ford Bronco Sport": ("Ford", r"^Bronco Sport"), "Ford Explorer": ("Ford", r"^Explorer"), "Toyota Highlander": ("Toyota", r"^Highlander"),
 "Toyota Grand Highlander": ("Toyota", r"^Grand Highlander"), "Chevrolet Traverse": ("Chevrolet", r"^Traverse"),
 "Kia Telluride": ("Kia", r"^Telluride"), "Hyundai Palisade": ("Hyundai", r"^Palisade"), "Honda Pilot": ("Honda", r"^Pilot"),
 "Toyota 4Runner": ("Toyota", r"^4Runner"), "Ford Bronco": ("Ford", r"^Bronco(?! Sport)"),
 "Chevrolet Tahoe": ("Chevrolet", r"^Tahoe"), "Chevrolet Suburban": ("Chevrolet", r"^Suburban"), "Ford Expedition": ("Ford", r"^Expedition"),
 "GMC Yukon": ("GMC", r"^Yukon"), "Toyota Sequoia": ("Toyota", r"^Sequoia"),
 "Toyota Sienna": ("Toyota", r"^Sienna"), "Honda Odyssey": ("Honda", r"^Odyssey"), "Kia Carnival": ("Kia", r"^Carnival"),
 "Ford Mustang": ("Ford", r"^Mustang(?! Mach)"), "Chevrolet Camaro": ("Chevrolet", r"^Camaro"),
}
def etype(r):
    a = str(r.atvType)
    if a == "EV": return "EV"
    if a == "Plug-in Hybrid": return "PHEV"
    if a == "Hybrid": return "HEV"
    if a == "Diesel" or "Diesel" in str(r.fuelType): return "Diesel"
    return "ICE"
rows = []
for name, (make, rx) in MAP.items():
    s = d[(d.make == make) & d.model.astype(str).map(lambda m: bool(re.search(rx, m)))].copy()
    if s.empty: print("no EPA match:", name); continue
    s["etype"] = s.apply(etype, axis=1)
    s["pt"] = s.etype + "_" + s.displ.fillna(0).round(1).map(str) + "L_" + s.cylinders.fillna(0).astype(int).astype(str) + "cyl"
    for y, g in s.groupby("year"):
        pts = sorted(g.pt.unique())
        rows.append(dict(model=name, model_year=y, n_powertrains=len(pts), powertrains=";".join(pts),
                         has_hev=int((g.etype == "HEV").any()), has_phev=int((g.etype == "PHEV").any()), has_ev=int((g.etype == "EV").any()),
                         has_v8=int(((g.cylinders == 8) & (g.etype != "EV")).any()), has_diesel=int((g.etype == "Diesel").any())))
pt = pd.DataFrame(rows); pt.to_csv(ROOT / "data/processed/powertrains_by_model_year.csv", index=False)
print(pt[pt.model.isin(["Wrangler", "Grand Cherokee", "Cherokee", "Compass", "Ram LD PU", "Charger ICE", "Durango", "Pacifica", "Gladiator", "Wagoneer family"])]
      .query("model_year>=2021")[["model", "model_year", "n_powertrains", "powertrains"]].to_string(max_colwidth=110))
