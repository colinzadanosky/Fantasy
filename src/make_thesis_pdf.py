"""Thesis-focused chart deck: only charts that test the upside/downside of
'renewal -> sustainable retail demand -> wholesale growth without inventory build or higher incentives -> margin recovery'.
Each page: chart + ~20-word summary. Last page: how the data would be used. Run after make_charts.py."""
import textwrap, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from common import OUT

CH = OUT / "charts"
PAGES = [
 ("Retail demand from renewal", "test_01_001_ram_post.png",
  "Upside: Ram 1500 rose ~37% versus rivals after Hemi returned (partial r +68%), though partly recovering volume lost in 2025."),
 ("Retail demand from renewal", "test_03_014_dpt.png",
  "Upside: each added powertrain goes with ~22% faster nameplate growth (partial r +39%, p=0.046); breadth modestly supports retail volume."),
 ("Retail demand from renewal", "test_04_015_d_ch.png",
  "Downside: Cherokee hybrid gains coincide with larger Compass/Grand Cherokee losses (partial r -46%); new nameplates may shift, not add, demand."),
 ("Retail demand from renewal", "test_07_022_hemi.png",
  "Mild downside: Ram HD runs ~6% lower when the 1500 offers Hemi (partial r -50%, n=11, not significant); possible trade-down."),
 ("Retail demand from renewal", "test_06_021_ice.png",
  "Mixed: each Charger Sixpack ICE unit adds only ~0.43 total Chargers (r +54%, n=7); gas partly replaces EV demand."),
 ("Retail vs fleet quality", "test_10_026_launch.png",
  "Watch: launch quarters show total growth ~19pp above retail growth (r +16%, not significant); fleet may flatter launch volumes."),
 ("Leading demand indicators", "test_31_043_ltr1.png",
  "Upside indicator: prior-quarter \"Ram 1500\" searches predict Ram pickup sales (partial r +43%, p=0.01); track monthly as early signal."),
 ("Leading demand indicators", "test_40_052_ss_l1.png",
  "Indicator: Stellantis brand search share tracks next-quarter market share (r +79%); both trended down together, so co-movement, not causation."),
 ("Pricing and incentive intensity", "test_13_034_prem_l4.png",
  "Downside: each extra point of ATP premium over industry precedes 0.14pp lower market share a year later (r -66%, p=0.01)."),
 ("Pricing and incentive intensity", "test_33_048_ps_l1.png",
  "Downside signal: rising \"Jeep price\" search share precedes ~10% lower Jeep sales next quarter (partial r -41%); early price-backlash gauge."),
 ("Dealer inventory", "test_28_000_shipments_minus_sales.png",
  "Watch: shipments exceeded US+Canada sales by 112-127k per half after the 2024 destock, back near prior norms; rebuild risk."),
 ("Macro demand risk", "test_43_059_r60.png",
  "Neutral: after controlling for industry volume, Stellantis sales are no more loan-rate sensitive than the market (partial r -13%, insignificant)."),
 ("Macro demand risk", "test_44_069_sent_C_band_low.png",
  "Downside: cheaper Compass/Cherokee/Hornet sales swing with consumer sentiment beyond industry (partial r +37%); trucks do not. Affordability exposure."),
 ("Utilization and margin", "test_52_079_ship.png",
  "Upside: NA margin rises ~6.5pp per extra 100k half-year shipments (r +90%); utilization recovery strongly supports the margin forecast."),
 ("Cost execution", "test_56_083_any_new.png",
  "Downside: model years introducing new powertrains carry 1.5x recall campaigns (r +33%, p<0.001); renewal raises warranty-cost risk to margins."),
 ("Where to collect next", "test_45_056_truck_share.png",
  "Data targeting: Hemi interest concentrates in high-truck-share, lower-income states (partial r +77%); prioritize these metros for listings scraping."),
]
THESIS = ("Thesis: Stellantis can convert its North American product and powertrain renewal into sustainable retail demand, allowing "
          "wholesale volumes to grow without a renewed buildup of dealer inventory or a material increase in incentive intensity. Together "
          "with improved production utilization and cost execution, this supports the margin recovery embedded in the forecast.")
USE = ("How I would use the data: treat each chart as a monitored signal with an upside and a downside threshold. Retail demand is "
       "confirmed if Ram 1500 keeps its post-Hemi gain against rivals, \"Ram 1500\" searches stay firm, and retail growth keeps pace "
       "with total growth (fleet is not filling the gap). The no-inventory-build leg fails if shipments minus US+Canada sales move "
       "above the 2022-24 range (~130k per half). The incentive leg fails if the ATP premium widens past ~15% or \"Jeep price\" "
       "searches rise, since both have preceded share loss. Margin recovery then follows the shipment-margin slope (~6.5pp per "
       "100k units), less warranty risk from new powertrains. The gaps to close are the direct inventory and discount evidence: "
       "start the weekly VIN listing scrape now, beginning in high-truck-share metros, to measure days-to-sell, discount % and "
       "stale-model-year share by powertrain, and add a monthly incentive series (Cox/J.D. Power, or listing discount vs MSRP). "
       "Re-run the suite each quarter; if the upside signals hold while inventory and discounts stay flat, the forecast's margin "
       "recovery is supported.")

with PdfPages(CH / "thesis_charts.pdf") as pdf:
    for i, (section, fn, summary) in enumerate(PAGES, 1):
        img = plt.imread(CH / fn)
        fig = plt.figure(figsize=(11, 8.5), facecolor="#fcfcfb")
        fig.text(0.04, 0.955, f"{i}/{len(PAGES)}  |  {section}", fontsize=11, color="#52514e", fontweight="bold")
        w = 0.92; h = w * (img.shape[0] / img.shape[1]) * 11 / 8.5
        if h > 0.74: h = 0.74; w = h / ((img.shape[0] / img.shape[1]) * 11 / 8.5)
        top = 0.93; ax = fig.add_axes([(1 - w) / 2, top - h, w, h]); ax.imshow(img); ax.axis("off")
        fig.text(0.06, top - h - 0.03, "\n".join(textwrap.wrap(summary, 105)), fontsize=13, color="#0b0b0b", va="top")
        pdf.savefig(fig); plt.close(fig)
    fig = plt.figure(figsize=(11, 8.5), facecolor="#fcfcfb")
    fig.text(0.06, 0.92, "Using the data to test the thesis", fontsize=16, fontweight="bold", color="#0b0b0b")
    fig.text(0.06, 0.86, "\n".join(textwrap.wrap(THESIS, 120)), fontsize=10.5, color="#52514e", va="top", style="italic")
    fig.text(0.06, 0.74, "\n".join(textwrap.wrap(USE, 110)), fontsize=12, color="#0b0b0b", va="top", linespacing=1.5)
    pdf.savefig(fig); plt.close(fig)
print("wrote", CH / "thesis_charts.pdf")
