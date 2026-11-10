"""Correlation charts for every regression term reported in results/regression_results.csv.
For each term: (left) raw data, y vs x, with OLS fit and Pearson r as a percent;
(right) added-variable plot - y and x each residualised on all other regressors (controls, fixed effects,
seasonality). Its slope equals the regression coefficient exactly (Frisch-Waugh-Lovell) and its correlation
is the partial correlation the regression measures. Output: results/charts/*.png and all_charts.pdf."""
import warnings, textwrap, re
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import run_all                                   # runs every test, fills common.MODELS
from common import MODELS, OUT, P
import statsmodels.api as sm

CH = OUT / "charts"; CH.mkdir(exist_ok=True)
for f in CH.glob("*.png"): f.unlink()
SURF, INK, INK2, MUTED, GRID, DOT, FIT = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0", "#2a78d6", "#eb6834"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6})


def pct(r): return f"{100 * r:+.0f}%"


LABELS = {"ly": "log units", "lp": "log brand ATP", "lrp": "log (brand ATP / industry ATP)", "lrp_ram": "rel. price x Ram",
          "prem": "ATP premium vs industry (%)", "prem_l1": "ATP premium, prior quarter (%)", "prem_l4": "ATP premium 4 quarters earlier (%)",
          "share": "US market share (%)", "d4share": "YoY change in market share (pp)", "ram_post": "Ram x post-Hemi (>=2025Q4)",
          "ram_partial": "Ram x 2025Q3", "ram_t": "Ram x trend", "t": "quarter index", "lpt": "log powertrain offerings",
          "dlpt": "YoY change log offerings", "dly": "YoY change log Jeep units", "n_pt": "# powertrains", "dpt": "YoY change # powertrains",
          "g": "YoY log growth", "d_cg": "YoY change Compass+GC units", "d_ch": "YoY change Cherokee units", "gap": "gap (see title)",
          "miss_hybrid": "rivals have hybrid, Stellantis not", "miss_ev": "rivals have EV, Stellantis not", "bev": "Charger BEV units",
          "ice": "Charger ICE units", "total": "total Charger units", "lhd": "log Ram HD units", "hemi": "Hemi available (1/0)",
          "hd_share": "HD share of Ram pickups", "tp": "treated x post", "launch": "new powertrain launch (1/0)",
          "ltr0": "log Google Trends, same quarter", "ltr1": "log Google Trends, prior quarter", "ly_l1": "log units, prior quarter",
          "ps0": '"Jeep price" share of Jeep searches (%)', "ps_l1": '"Jeep price" search share, prior qtr (%)', "lv": "log Wikipedia pageviews",
          "lv_l1": "log pageviews, prior quarter", "ss": "Stellantis search share (%)", "ss_l1": "search share, prior quarter (%)",
          "lshare": "log Ram share of full-size pickups", "lgas": "log US gas price", "Hemi": '"Hemi" search index (state)',
          "r60": "60-month new-car loan rate (%)", "v8_share": "sales share of V8-offering nameplates (%)", "post": "post-event (1/0)",
          "latp": "log OEM ATP", "sp": "Stellantis x post-tariff", "charger_bev_share": "BEV share of Charger sales (%)",
          "bev_share_stla": "BEV share of Stellantis sales (%)", "gca": "Canada YoY log growth", "gus": "US YoY log growth",
          "rev_per_unit_usd_k": "NA revenue per unit ($k)", "ram_share_us": "Ram share of US sales (%)", "margin": "NA AOI margin (%)",
          "ship": "NA shipments (000s)", "car_0_1_pct": "2-day abnormal return (%)", "surprise": "STLA YoY minus industry YoY (pp)",
          "recalls": "recall campaigns", "any_new": "new powertrain that model year", "np.log(med_income)": "log median household income",
          "rural_share": "rural population (%)", "truck_share": "trucks share of registrations (%)", "np.log(gas)": "log PADD gas price"}


def pretty(name):
    if name in LABELS: return LABELS[name]
    m = re.match(r"sent:C\(band\)\[(\w+)\]", name)
    if m: return f"U. Mich sentiment x {m.group(1)}-price band"
    return re.sub(r"^np\.log\((.*)\)$", r"log \1", name)


def scatter(ax, x, y, title, r_label, binary=False):
    x, y = np.asarray(x, float), np.asarray(y, float)
    xs = x + (np.random.default_rng(0).uniform(-0.04, 0.04, len(x)) if binary else 0)
    ax.scatter(xs, y, s=30, color=DOT, edgecolor=SURF, linewidth=1.5, zorder=3, alpha=0.85)
    if np.ptp(x) > 0 and len(x) > 2:
        b, a = np.polyfit(x, y, 1); g = np.linspace(x.min(), x.max(), 50)
        ax.plot(g, a + b * g, color=FIT, linewidth=2, zorder=4)
    ax.set_title(title, loc="left", fontsize=8.5, color=INK2, pad=22)
    ax.text(0, 1.02, r_label.replace("\n", "    "), transform=ax.transAxes, va="bottom", ha="left", fontsize=10, color=INK, fontweight="bold")


def chart(entry, term, k):
    m = entry["model"]; mm = m.model
    exog = pd.DataFrame(mm.exog, columns=mm.exog_names); y = pd.Series(np.asarray(mm.endog, float), name=mm.endog_names)
    if term not in exog: return None
    x = exog[term]; others = exog.drop(columns=[term]); binary = set(np.unique(x)) <= {0, 1}
    r_raw = np.corrcoef(x, y)[0, 1] if np.std(x) > 0 else np.nan
    is_ols = hasattr(m, "rsquared")
    has_controls = others.shape[1] > 1
    fig, axes = plt.subplots(1, 2 if (has_controls and is_ols) else 1, figsize=(10 if has_controls and is_ols else 6.4, 4.4))
    axes = np.atleast_1d(axes)
    coef, p = m.params[term], m.pvalues[term]
    two = has_controls and is_ols
    lab0 = f"r = {pct(r_raw)}   (R² {100 * r_raw**2:.0f}%)" + ("" if two else f"\nslope = {coef:.3g}   p = {p:.3g}")
    scatter(axes[0], x, y, "Raw data", lab0, binary)
    axes[0].set_xlabel(pretty(term)); axes[0].set_ylabel(pretty(mm.endog_names))
    if two:
        ex = sm.OLS(x.values, others.values).fit().resid; ey = sm.OLS(y.values, others.values).fit().resid
        r_par = np.corrcoef(ex, ey)[0, 1]
        scatter(axes[1], ex, ey, "After controls (what the regression measures)",
                f"partial r = {pct(r_par)}   slope = {coef:.3g}   p = {p:.3g}")
        axes[1].set_xlabel(f"{pretty(term)} | controls"); axes[1].set_ylabel(f"{pretty(mm.endog_names)} | controls")
        r_reg = r_par
    else:
        r_reg = r_raw
    r2 = f"   model R² = {100 * m.rsquared:.0f}%" if is_ols else "   (Poisson model; raw counts shown)"
    W_ = 110 if two else 70
    fig.suptitle("\n".join(textwrap.wrap(f"Test {entry['test']}: {entry['title']}", W_)), x=0.01, ha="left", fontsize=11, color=INK, fontweight="bold")
    fig.text(0.01, 0.005, "\n".join(textwrap.wrap(f"{entry['spec']}   n = {int(m.nobs)}{r2}   [{entry['status']}]", 170 if two else 105)),
             fontsize=7.5, color=MUTED, ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.09, 1, 0.88))
    fn = CH / f"test_{entry['test']:02d}_{k:03d}_{re.sub(r'[^A-Za-z0-9]+', '_', term).strip('_')}.png"
    fig.savefig(fn, dpi=150); plt.close(fig)
    return dict(test=entry["test"], title=entry["title"], term=term, file=fn.name, r_raw_pct=100 * r_raw,
                r_regression_pct=100 * r_reg, coef=coef, p=p, n=int(m.nobs))


def descriptive_charts():
    out = []
    d = pd.read_csv(OUT / "details/test_28_shipments_vs_sales.csv").dropna(subset=["ship_minus_uscan_k"])
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.bar(d.half, d.ship_minus_uscan_k, color=DOT, width=0.6, edgecolor=SURF, linewidth=2)
    ax.axhline(0, color=MUTED, linewidth=1); ax.set_ylabel("NA shipments - US & Canada sales (000s)")
    ax.set_title("Test 28: shipments minus US + Canada sales by half-year (descriptive; includes unreported Mexico sales)", loc="left", fontsize=10, color=INK)
    fig.tight_layout(); fn = CH / "test_28_000_shipments_minus_sales.png"; fig.savefig(fn, dpi=150); plt.close(fig)
    out.append(dict(test=28, title="Shipments minus US+Canada sales", term="(bar chart)", file=fn.name))
    d = pd.read_csv(OUT / "details/test_32_data.csv")
    fig, ax = plt.subplots(figsize=(5.6, 4.1))
    r = np.corrcoef(d.trends_ratio, d.sales_ratio)[0, 1]
    scatter(ax, d.trends_ratio, d.sales_ratio, "Raw data (4 quarters, 2025Q4-2026Q3)", f"r = {pct(r)}")
    for _, row in d.iterrows(): ax.annotate(row.quarter, (row.trends_ratio, row.sales_ratio), fontsize=7, color=INK2, xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel('"Cherokee hybrid" / "RAV4 hybrid" searches'); ax.set_ylabel("Cherokee / RAV4 sales")
    fig.suptitle("Test 32: Cherokee vs RAV4 hybrid interest gap (descriptive, n = 4)", x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93)); fn = CH / "test_32_000_ratio.png"; fig.savefig(fn, dpi=150); plt.close(fig)
    out.append(dict(test=32, title="Cherokee/RAV4 sales vs search ratio", term="corr", file=fn.name, r_raw_pct=100 * r, r_regression_pct=100 * r, n=len(d)))
    return out


rows = []; counter = 0
for e in MODELS:
    for t in e["terms"]:
        counter += 1
        r = chart(e, t, counter)
        if r: rows.append(r)
rows += descriptive_charts()
idx = pd.DataFrame(rows).sort_values(["test", "file"]); idx.to_csv(CH / "chart_index.csv", index=False)

# one PDF with every chart, a cover page listing blocked tests
res = pd.read_csv(OUT / "regression_results.csv"); blocked = res[res.status == "BLOCKED"].drop_duplicates("test")
with PdfPages(CH / "all_charts.pdf") as pdf:
    fig = plt.figure(figsize=(11, 8.5)); fig.text(0.05, 0.94, "Stellantis powertrain demand - correlation charts for every regression", fontsize=16, fontweight="bold")
    txt = ("Each page: left = raw data with OLS line and Pearson r (as %); right = the same relationship after removing the regression's\n"
           "controls / fixed effects / seasonality - its slope is the reported coefficient and its partial r is the regression's correlation.\n"
           "r is shown as a percent (e.g. r = +62% means 0.62); R² is the share of variance explained.\n\n"
           f"{len(idx)} charts. Tests with no data (no chart possible):\n")
    txt += "\n".join(textwrap.shorten(f"  {int(b.test)}. {b.title} - {b.note}", 150) for _, b in blocked.iterrows())
    fig.text(0.05, 0.9, txt, fontsize=8, va="top", family="monospace" if False else None); pdf.savefig(fig); plt.close(fig)
    for f in idx.file:
        img = plt.imread(CH / f); fig = plt.figure(figsize=(11, 8.5)); ax = fig.add_axes([0.03, 0.03, 0.94, 0.94]); ax.imshow(img); ax.axis("off")
        pdf.savefig(fig); plt.close(fig)
print(len(idx), "charts ->", CH)
print(idx[["test", "term", "r_raw_pct", "r_regression_pct", "p", "n"]].round(1).to_string(index=False))
