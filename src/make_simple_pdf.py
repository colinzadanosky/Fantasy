"""Plain-language chart report, ordered from strongest to weakest evidence.
Simple charts (sales over time, bars, labeled dots) redrawn from the same data the regressions use.
Output: results/charts/plain_language_report.pdf. Run after run_all.py."""
import textwrap, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from common import *

SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#a3a29c"
TIER = {"STRONG": ("#008300", "STRONG EVIDENCE - safe to use in a report"),
        "MODERATE": ("#c98500", "MODERATE EVIDENCE - use with a caveat"),
        "WEAK": ("#e34948", "WEAK OR MESSY - background only, not enough proof")}
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6})
W = stla_wide(); IND = industry_q(); gq = gcbc_q("US").pivot_table(index="quarter", columns="model", values="units")
D = OUT / "details"


def qlab(q): return q.replace("Q", " Q")


def dots(ax, x, y, labels=None, every=1):
    ax.scatter(x, y, s=60, color=BLUE, edgecolor=SURF, linewidth=2, zorder=3)
    b, a = np.polyfit(x, y, 1); g = np.linspace(min(x), max(x), 50)
    ax.plot(g, a + b * g, color=ORANGE, lw=2, zorder=2, label="trend line")
    if labels is not None:
        for i, (xi, yi, l) in enumerate(zip(x, y, labels)):
            if i % every == 0: ax.annotate(l, (xi, yi), xytext=(5, 4), textcoords="offset points", fontsize=7.5, color=INK2)


# ------------------------------------------------------------------ chart builders
def c_hemi(ax):
    qs = [q for q in W.index if "2024Q1" <= q <= "2026Q3"]
    ram = W.loc[qs, "Ram LD PU"]; riv = gq.loc[qs, ["Ford F-Series", "Chevrolet Silverado", "GMC Sierra", "Toyota Tundra"]].sum(axis=1)
    x = range(len(qs))
    ax.plot(x, 100 * ram / ram["2025Q2"], color=BLUE, lw=2.5, marker="o", label="Ram 1500")
    ax.plot(x, 100 * riv / riv["2025Q2"], color=GRAY, lw=2.5, marker="o", label="Rivals: F-150, Silverado, Sierra, Tundra")
    ax.axvspan(2.5, 6.5, color="#f3e3dc", zorder=0); ax.axvspan(6.5, len(qs) - 0.5, color="#dfeaf7", zorder=0)
    ax.text(4.5, ax.get_ylim()[1] * 0.98, "V8 NOT offered", ha="center", va="top", fontsize=9, color=INK2)
    ax.text(8.5, ax.get_ylim()[1] * 0.98, "V8 back", ha="center", va="top", fontsize=9, color=INK2)
    ax.set_xticks(list(x)); ax.set_xticklabels([qlab(q) for q in qs], rotation=45, fontsize=8)
    ax.set_ylabel("Sales vs mid-2025 (100 = Q2 2025 level)"); ax.legend(loc="lower left", frameon=False)


def c_margin(ax):
    d = pd.read_csv(D / "test_51_52_na_financials.csv"); d = d[d.freq == "half"].sort_values("ship")
    dots(ax, d.ship, d.margin, d.period)
    ax.axhline(0, color=MUTED, lw=1); ax.set_xlabel("Vehicles shipped to dealers in North America in that half-year (thousands)")
    ax.set_ylabel("North America profit margin (%)")


def c_premium(ax):
    d = pd.read_csv(D / "test_13_data.csv").sort_values("quarter")
    d["prem_l4"] = d.prem.shift(4); d["chg"] = d.share - d.share.shift(4); d = d.dropna(subset=["prem_l4", "chg"])
    dots(ax, d.prem_l4, d.chg, [qlab(q) for q in d.quarter])
    ax.axhline(0, color=MUTED, lw=1)
    ax.set_xlabel("How much more Stellantis vehicles cost than the average new car, one year earlier (%)")
    ax.set_ylabel("Change in Stellantis market share over the year (points)")


def c_recalls(ax):
    d = pd.read_csv(D / "test_56_panel.csv"); m = d.groupby("any_new").recalls.mean()
    bars = ax.bar(["Same engines as last year", "Added a new engine"], [m[0], m[1]], color=[GRAY, BLUE], width=0.5)
    for b in bars: ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.2, f"{b.get_height():.1f}", ha="center", fontsize=11, color=INK)
    ax.set_ylabel("Average number of safety recalls per model year"); ax.grid(axis="x", visible=False)


def c_inventory(ax):
    d = pd.read_csv(D / "test_28_shipments_vs_sales.csv").dropna(subset=["ship_minus_uscan_k"])
    cols = [ORANGE if v < 0 else BLUE for v in d.ship_minus_uscan_k]
    bars = ax.bar(d.half, d.ship_minus_uscan_k, color=cols, width=0.6)
    for b, v in zip(bars, d.ship_minus_uscan_k): ax.text(b.get_x() + b.get_width() / 2, v + (4 if v >= 0 else -12), f"{v:+.0f}k", ha="center", fontsize=9)
    ax.axhline(0, color=MUTED, lw=1); ax.set_ylabel("Shipped to dealers minus sold to customers (thousands)"); ax.grid(axis="x", visible=False)


def c_engines(ax):
    p = pd.read_csv(D / "test_03_panel.csv").sort_values(["model", "quarter"])
    p["g"] = p.groupby("model").units.transform(lambda s: s / s.shift(4) - 1); p["d"] = p.groupby("model").n_pt.diff(4)
    p = p.dropna(subset=["g", "d"]); p["grp"] = np.sign(p.d); m = p.groupby("grp").g.median() * 100
    bars = ax.bar(["Dropped an engine", "Kept the same engines", "Added an engine"], [m[-1], m[0], m[1]], color=[GRAY, GRAY, BLUE], width=0.55)
    for b in bars:
        v = b.get_height(); ax.text(b.get_x() + b.get_width() / 2, v / 2, f"{v:+.0f}%", ha="center", va="center", fontsize=12, color="white", fontweight="bold")
    ax.axhline(0, color=MUTED, lw=1); ax.set_ylabel("Typical sales change vs a year earlier (%)"); ax.grid(axis="x", visible=False)


def c_search_ram(ax):
    tr = trends_q("hemi", "Ram 1500"); d = pd.DataFrame({"s": W["Ram LD PU"] / 1000, "t": tr.shift(1)}).dropna()
    dots(ax, d.t, d.s, [qlab(q) for q in d.index])
    ax.set_xlabel('Google searches for "Ram 1500" in the PREVIOUS quarter (index, 100 = peak)'); ax.set_ylabel("Ram 1500 trucks sold this quarter (thousands)")


def c_jeep_price(ax):
    sh = trends_q("price", "Jeep price") / trends_q("price", "Jeep") * 100
    d = pd.DataFrame({"s": W["Jeep"] / 1000, "t": sh.shift(1)}).dropna()
    dots(ax, d.t, d.s, [qlab(q) for q in d.index], every=2)
    ax.set_xlabel('Share of Jeep Google searches that were "Jeep price", PREVIOUS quarter (%)'); ax.set_ylabel("Jeep vehicles sold this quarter (thousands)")


def c_states(ax):
    d = pd.read_csv(D / "test_45_state.csv")
    lab = {"TX", "WY", "MT", "CA", "NY", "MA", "NJ", "WV", "OK", "WA", "ND", "FL"}
    dots(ax, d.truck_share, d.Hemi, [s if s in lab else "" for s in d.st])
    ax.set_xlabel("Trucks and SUVs as a share of all registered vehicles in the state (%)"); ax.set_ylabel('Google interest in "Hemi" (100 = highest state)')


def c_cherokee(ax):
    qs = [q for q in W.index if "2024Q1" <= q <= "2026Q3"]; x = range(len(qs))
    ax.plot(x, W.loc[qs, "Cherokee"] / 1000, color=BLUE, lw=2.5, marker="o", label="New Cherokee (hybrid)")
    ax.plot(x, (W.loc[qs, "Compass"] + W.loc[qs, "Grand Cherokee"]) / 1000, color=GRAY, lw=2.5, marker="o", label="Compass + Grand Cherokee")
    ax.set_xticks(list(x)); ax.set_xticklabels([qlab(q) for q in qs], rotation=45, fontsize=8)
    ax.set_ylabel("Vehicles sold (thousands)"); ax.legend(frameon=False)


def c_hd(ax):
    qs = [q for q in W.index if "2024Q1" <= q <= "2026Q3"]; x = range(len(qs))
    ax.bar(x, W.loc[qs, "Ram HD PU"] / 1000, color=[BLUE if 3 <= i <= 6 else GRAY for i in x], width=0.6)
    ax.set_xticks(list(x)); ax.set_xticklabels([qlab(q) for q in qs], rotation=45, fontsize=8)
    ax.set_ylabel("Ram heavy-duty trucks sold (thousands)"); ax.grid(axis="x", visible=False)
    ax.set_ylim(0, ax.get_ylim()[1] * 1.15)
    ax.text(0.5, 0.98, "Blue bars = quarters when the Ram 1500 had NO V8", transform=ax.transAxes, ha="center", va="top", fontsize=9, color=INK2)


def c_charger(ax):
    qs = [q for q in W.index if "2025Q1" <= q <= "2026Q3"]; x = np.arange(len(qs))
    ice, bev = W.loc[qs, "Charger ICE"].fillna(0), W.loc[qs, "Charger BEV"].fillna(0)
    ax.bar(x, bev, color=BLUE, width=0.6, label="Electric Charger"); ax.bar(x, ice, bottom=bev, color=ORANGE, width=0.6, label="Gas Charger (Sixpack)")
    ax.set_xticks(x); ax.set_xticklabels([qlab(q) for q in qs], fontsize=8); ax.set_ylabel("Chargers sold"); ax.legend(frameon=False)
    ax.grid(axis="x", visible=False)


def c_rates(ax):
    r = g19_q(); d = pd.DataFrame({"share": W["Stellantis"] / (IND.lv_nsa_k * 1000) * 100, "rate": r.rate60_bank}).dropna()
    dots(ax, d.rate, d.share, [qlab(q) if q.endswith("Q1") else "" for q in d.index])
    ax.set_xlabel("Average interest rate on a 5-year new-car loan (%)"); ax.set_ylabel("Stellantis share of all US new-vehicle sales (%)")


def c_retail(ax):
    d = pd.read_csv(D / "test_10_retail_vs_total.csv"); d = d[d.launch == 1].reset_index(drop=True)
    x = np.arange(len(d)); w = 0.38
    ax.bar(x - w / 2, d.total_yoy, w, color=GRAY, label="All sales growth (incl. fleet)"); ax.bar(x + w / 2, d.retail_yoy, w, color=BLUE, label="Retail (regular buyer) growth")
    ax.set_xticks(x); ax.set_xticklabels([f"{e.replace(' LD PU', ' 1500')}\n{qlab(q)}" for e, q in zip(d.entity, d.quarter)], fontsize=7.5)
    ax.axhline(0, color=MUTED, lw=1); ax.set_ylabel("Change vs a year earlier (%)"); ax.legend(frameon=False); ax.grid(axis="x", visible=False)


def c_brand_search(ax):
    t = trends_m(); t = t[t.group == "brands"].copy(); t["quarter"] = t.date.dt.to_period("Q").map(qstr)
    p = t.pivot_table(index="quarter", columns="term", values="index", aggfunc="mean")
    ss = p[["Jeep", "Dodge", "Chrysler"]].sum(axis=1) / p.sum(axis=1) * 100
    d = pd.DataFrame({"ss": ss, "ms": W["Stellantis"] / (IND.lv_nsa_k * 1000) * 100}).dropna(); x = range(len(d))
    ax.plot(x, 100 * d.ss / d.ss.iloc[0], color=BLUE, lw=2.5, marker="o", label="Share of car-brand Google searches")
    ax.plot(x, 100 * d.ms / d.ms.iloc[0], color=GRAY, lw=2.5, marker="o", label="Share of US sales")
    ax.set_xticks(list(x)); ax.set_xticklabels([qlab(q) for q in d.index], rotation=45, fontsize=7.5)
    ax.set_ylabel(f"Stellantis level vs {qlab(d.index[0])} (= 100)"); ax.legend(frameon=False)


# ------------------------------------------------------------------ pages (strongest first)
PAGES = [
 ("STRONG", c_hemi, "When Ram brought its V8 engine back, Ram 1500 sales jumped well ahead of rival trucks",
  "Ram dropped its big V8 engine (the \"Hemi\") for about a year, then brought it back in late 2025. After it came back, Ram 1500 "
  "sales grew about 37% more than rival pickups did. Before that, Ram and its rivals had moved roughly together.",
  "Both lines start at 100 in mid-2025, so you can compare growth, not size. The blue line pulling above the gray line in the "
  "blue-shaded area is the V8 effect.",
  "Strong: clear jump, big gap, and the comparison with rivals removes normal market ups and downs. Caveat: much of the gain is "
  "Ram winning back buyers it lost when it removed the V8, and Ram cut prices at the same time."),
 ("STRONG", c_margin, "The more vehicles Stellantis ships in North America, the higher its profit margin",
  "Each dot is a half-year. When Stellantis shipped more vehicles to dealers, it kept a much bigger share of each sales dollar as "
  "profit. Factories have big fixed costs, so running them fuller pays off.",
  "Dots to the right = more vehicles shipped. Higher dots = more profit per dollar of sales. The line slopes up steeply.",
  "Strong: tight pattern (correlation 90%). About 100,000 extra vehicles per half-year goes with roughly 6.5 points more margin. "
  "Caveat: 2024-25 also had one-off costs (tariffs, warranty charges)."),
 ("STRONG", c_premium, "When Stellantis prices its vehicles far above the market, it loses market share the following year",
  "Each dot is a quarter. When Stellantis vehicles were much pricier than the average new car, its share of US sales dropped over "
  "the next year. Its price gap peaked at about 24% in early 2024, and its market share fell from about 10.6% to 7.4%.",
  "Dots to the right = Stellantis was priced further above the market. Lower dots = bigger share loss a year later.",
  "Strong for this question (correlation -66%, unlikely to be chance), but only 14 quarters of data. It is a warning sign for any "
  "plan that relies on high prices."),
 ("STRONG", c_recalls, "Model years that introduce a new engine get noticeably more safety recalls",
  "Using government recall records, model years where a Stellantis vehicle got a new engine averaged about 10 recalls, versus "
  "about 5 for model years with the same engines as before.",
  "Compare the two bars. Taller = more recalls. Recalls cost money (repairs, warranty), which eats into profit.",
  "Strong: even after comparing each model only with its own other years, new-engine years have about 1.5 times as many recalls "
  "(very unlikely to be chance). Caveat: it counts recall campaigns, not how many cars were affected."),
 ("MODERATE", c_inventory, "Stellantis is again shipping more vehicles to dealers than customers are buying",
  "In late 2024 Stellantis shipped fewer vehicles than it sold, to clear out crowded dealer lots (orange bar). Since mid-2025 it has "
  "been shipping 112,000-127,000 more vehicles than US and Canadian customers bought per half-year.",
  "Bars above zero = more shipped than sold (dealer lots filling up). Below zero = lots being cleared out.",
  "Moderate: the numbers are official, but this includes Mexico sales, which Stellantis does not report separately. Current levels "
  "are similar to 2022-2024, so this is a watch item, not proof of a problem."),
 ("MODERATE", c_engines, "Models that add an engine option tend to sell better the next year",
  "Across about 20 Stellantis models from 2021 to 2026, models that added an engine option typically grew about 14% in a year. "
  "Models that kept the same engines shrank about 8%, and models that dropped one shrank about 13%.",
  "Each bar is the typical (median) sales change for that group. Blue is the group that added an engine.",
  "Moderate: the pattern is clear, but the statistical test is borderline (about 5% chance it is luck). Stellantis may add engines "
  "to models it already expects to sell well."),
 ("MODERATE", c_search_ram, "Google searches for \"Ram 1500\" give an early read on Ram 1500 sales",
  "Each dot is a quarter. When more people searched \"Ram 1500\", more Ram 1500 trucks were sold in the following quarter. This "
  "can be checked free each month, before Stellantis reports its sales.",
  "Dots to the right = more searching last quarter. Higher dots = more trucks sold this quarter.",
  "Moderate: the pattern is strong, but there are only 10 quarters. Searches for \"Ram Hemi\" specifically did NOT predict sales."),
 ("MODERATE", c_jeep_price, "When more people google \"Jeep price\", Jeep sales tend to drop the next quarter",
  "Each dot is a quarter. When a bigger share of Jeep searches were about price, Jeep sold fewer vehicles the next quarter, about "
  "10% fewer per extra point. That suggests shoppers balking at Jeep prices.",
  "Dots to the right = more price-searching. Lower dots = fewer Jeeps sold the next quarter.",
  "Moderate: statistically solid (about 1% chance it is luck), but only 20 quarters, and searches are an indirect signal."),
 ("MODERATE", c_states, "Interest in the V8 \"Hemi\" is highest in truck-heavy states",
  "States where trucks and SUVs make up more of the vehicles on the road search much more for \"Hemi\". Lower-income states also "
  "search more. This tells you where to look for V8 buyers.",
  "Each dot is a state. Further right = more trucks registered. Higher = more Hemi interest.",
  "Moderate: a clear pattern across 50 states (correlation 67%), but it measures interest, not actual purchases. Use it to choose "
  "which cities to track dealer inventory in."),
 ("WEAK", c_cherokee, "The new Cherokee may be taking buyers from other Jeeps",
  "As the new Cherokee hybrid started selling in 2026, sales of the Compass and Grand Cherokee fell sharply. That could mean "
  "Cherokee is stealing buyers from them instead of bringing in new ones.",
  "Blue line = new Cherokee rising. Gray line = Compass + Grand Cherokee falling.",
  "Weak: Stellantis also shut down Compass and Grand Cherokee production in this period, so the drop may be supply, not "
  "lost buyers. Only 4 quarters of Cherokee sales so far."),
 ("WEAK", c_hd, "Ram's bigger heavy-duty trucks may sell slightly less when the V8 is available on the Ram 1500",
  "When the 1500 had no V8 (blue bars), some buyers who wanted a V8 may have bought the bigger, pricier heavy-duty Ram instead. "
  "Heavy-duty sales ran about 6% lower when the V8 was available.",
  "Compare blue bars (no V8 on the 1500) with gray bars (V8 offered).",
  "Weak: the difference is small and could easily be chance (only 11 quarters)."),
 ("WEAK", c_charger, "The gas-powered Charger is replacing the electric one more than it is adding buyers",
  "Dodge's new gas Charger started selling in late 2025, and electric Charger sales collapsed at the same time. The total "
  "number of Chargers sold rose only modestly.",
  "Each bar is a quarter. Blue = electric, orange = gas. Watch the blue shrink as the orange grows.",
  "Weak: only 7 quarters, and the federal EV tax credit ended at the same time (Sept 2025), which also hurt electric sales."),
 ("WEAK", c_rates, "Stellantis's market share fell as car-loan interest rates rose",
  "Each dot is a quarter. Higher loan rates went with a lower Stellantis share of US sales, which would suggest its buyers are "
  "more sensitive to borrowing costs than other brands'.",
  "Dots to the right = more expensive car loans. Lower dots = smaller Stellantis market share.",
  "Weak: Stellantis was losing share at the same time for other reasons (mainly high prices), so the two cannot be separated. "
  "When compared directly with total market sales, the rate effect disappears."),
 ("WEAK", c_retail, "When new engines launch, fleet sales may be inflating the totals",
  "For new-engine launches, total sales (which include rental and business fleets) often grew faster than sales to regular "
  "shoppers. For example, the Ram 1500 in Q3 2026: total +73%, regular shoppers +42%.",
  "Gray = all sales growth. Blue = regular-shopper growth. A gray bar much taller than blue means fleet is filling the gap.",
  "Weak: Stellantis only gives regular-shopper growth in a few press releases (hand-collected), and the difference is not "
  "statistically reliable."),
 ("WEAK", c_brand_search, "Stellantis's share of car-brand searches moves with its share of sales",
  "Stellantis's share of Google searches for car brands (vs Ford and Toyota) fell and recovered roughly in step with its share "
  "of US sales.",
  "Both lines start at 100. When they move together, search interest is tracking sales.",
  "Weak for decision-making: both were falling over the same years, so they move together without one causing the other."),
]

INTRO = ("This report checks one investment idea: that Stellantis's new and updated vehicles and engines will bring in real buyers, "
         "so it can ship more vehicles without stuffing dealer lots or offering bigger discounts, which would let profits recover.\n\n"
         "Each page has one chart and three short notes:\n"
         "  - What this shows: the finding in plain words\n"
         "  - How to read it: what the lines, dots or bars mean\n"
         "  - How strong: whether you can rely on it, and why\n\n"
         "Pages are in order of how much you can trust them:")
USE = ("How I would use this. The strong findings are the core of the case. The V8's return shows that the right engine brings Ram "
       "buyers back. Shipping more vehicles clearly lifts profit margins. Pricing too far above the market costs share. New engines "
       "bring more recalls, which cost money. The moderate findings are the early-warning gauges to check each month or quarter: "
       "\"Ram 1500\" and \"Jeep price\" Google searches, and whether shipments keep running well ahead of sales. "
       "The idea holds up if sales to regular shoppers keep growing, the gap between shipments and sales stays near its 2022-24 "
       "level, and Stellantis prices stay close to the market. It weakens if any of those reverse. The biggest missing piece is "
       "direct proof about dealer lots and discounts. The next step is to record dealer websites every week, starting in "
       "truck-heavy cities, to see which vehicles sell fast, which sit, and how big the discounts are. Weak findings stay out of the "
       "report unless that new data confirms them.")

with PdfPages(CH := OUT / "charts" / "plain_language_report.pdf") as pdf:
    fig = plt.figure(figsize=(8.5, 11)); fig.text(0.08, 0.92, "Is Stellantis's product comeback real?", fontsize=20, fontweight="bold", color=INK)
    fig.text(0.08, 0.89, "Charts in plain language, most reliable first", fontsize=12, color=INK2)
    fig.text(0.08, 0.84, "\n".join(sum([textwrap.wrap(p, 85) or [""] for p in INTRO.split("\n")], [])), fontsize=11, va="top", color=INK, linespacing=1.5)
    y = 0.47
    for k, (col, lab) in TIER.items():
        n = sum(1 for p in PAGES if p[0] == k)
        fig.patches.append(plt.Rectangle((0.08, y - 0.012), 0.025, 0.025, color=col, transform=fig.transFigure))
        fig.text(0.12, y, f"{lab}  ({n} charts)", fontsize=11, va="center", color=INK); y -= 0.045
    fig.text(0.08, 0.3, "\n".join(textwrap.wrap("\"Correlation\" is how closely two things move together, from 0% (no link) to 100% "
             "(move in perfect step). A minus sign means one goes up while the other goes down. Moving together does not by itself "
             "prove that one causes the other.", 85)), fontsize=10, va="top", color=INK2, linespacing=1.4)
    pdf.savefig(fig); plt.close(fig)
    for i, (tier, fn, title, what, how, strength) in enumerate(PAGES, 1):
        col, lab = TIER[tier]
        fig = plt.figure(figsize=(8.5, 11))
        fig.patches.append(plt.Rectangle((0, 0.955), 1, 0.045, color=col, transform=fig.transFigure))
        fig.text(0.06, 0.977, f"#{i} of {len(PAGES)}   |   {lab}", fontsize=10.5, color="white", fontweight="bold", va="center")
        fig.text(0.06, 0.925, "\n".join(textwrap.wrap(title, 62)), fontsize=15, fontweight="bold", color=INK, va="top")
        ax = fig.add_axes([0.13, 0.43, 0.8, 0.40]); fn(ax)
        yy = 0.33
        for head, body in [("What this shows", what), ("How to read it", how), ("How strong is this?", strength)]:
            fig.text(0.06, yy, head, fontsize=11.5, fontweight="bold", color=INK, va="top")
            lines = textwrap.wrap(body, 95); fig.text(0.06, yy - 0.022, "\n".join(lines), fontsize=10.5, color=INK2, va="top", linespacing=1.35)
            yy -= 0.03 + 0.0185 * len(lines) + 0.012
        pdf.savefig(fig); plt.close(fig)
    fig = plt.figure(figsize=(8.5, 11)); fig.text(0.08, 0.92, "How I would use this", fontsize=18, fontweight="bold", color=INK)
    fig.text(0.08, 0.87, "\n".join(textwrap.wrap(USE.split(". ", 1)[1], 85)), fontsize=11.5, va="top", color=INK, linespacing=1.55)
    pdf.savefig(fig); plt.close(fig)
print("wrote", CH)
