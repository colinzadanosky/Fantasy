# Stellantis US powertrain demand – regression suite

**New: [`results/extensions/`](results/extensions/README.md)** — NA cost-bridge quality (€1.33bn industrial gain), fleet vs retail, Hemi vs six-cylinder
discounts from dealer listings, NY VIN-level registrations, warranty-risk tracker, resale, plant notes.

Runs the 56-test plan ("Does powertrain choice create new sales? / demand or discounting? / sell-through /
alternative data / macro & policy / financial") on public data. **Results: [`REPORT.md`](REPORT.md)**, full table
[`results/ALL_TESTS.md`](results/ALL_TESTS.md).

## Reproduce

```bash
pip install -r requirements.txt   # also needs poppler-utils (pdftotext)
cd src
python3 collect_stellantis_releases.py && python3 parse_stellantis_sales.py && python3 parse_release_text.py
python3 collect_gcbc.py
python3 collect_macro.py
python3 collect_alt.py            # Google Trends, Wikipedia pageviews, NHTSA recalls
python3 collect_sec.py && python3 parse_sec_na.py
python3 collect_cox.py && python3 parse_kbb_atp.py
python3 build_powertrains.py      # needs data/raw/epa/vehicles.csv.zip (fueleconomy.gov/feg/epadata/vehicles.csv.zip)
# state covariates: data/raw/census/{est23all.xls, 2020_UA_COUNTY.xlsx, mv1.xlsx} (Census SAIPE, Census UA, FHWA MV-1)
python3 run_all.py && python3 make_appendix.py
python3 make_charts.py            # correlation chart for every regression term -> results/charts/
# extensions (results/extensions/)
python3 collect_sec_mdna.py       # 20-F + interim reports; NA AOI waterfall values transcribed into ext04_na_bridge.py
python3 ext04_na_bridge.py
python3 collect_ny_registrations.py && python3 ext05_fleet.py   # NY DMV VIN file + NHTSA vPIC decode
python3 ext01_listings.py         # uses data/raw/listings/ (KBB pulls, 2026-11-11)
python3 collect_nhtsa_complaints.py && python3 ext08_warranty_risk.py
python3 ext09_resale.py
```

`data/raw/` (downloaded pages/PDFs) is not committed; `data/processed/` holds the cleaned inputs used by the tests.

## Layout

| Path | Contents |
|---|---|
| `src/collect_*.py`, `src/parse_*.py`, `src/build_powertrains.py` | data collection and cleaning |
| `src/tests_a_volume.py` … `src/tests_def.py` | tests 1–56 (one function per test) |
| `src/listings_models.py` | hazard / discount models for the listing-scrape tests (16, 17, 21, 22, 26, 27, 29, 30) – ready, awaiting data |
| `results/regression_results.csv` | every coefficient, SE, p, n, status, spec, data, caveat |
| `results/charts/plain_language_report.pdf` | plain-language report: 15 simple charts ranked strongest to weakest evidence (`src/make_simple_pdf.py`) |
| `results/charts/thesis_charts.pdf` | thesis-focused deck: 16 charts with 20-word summaries + how to use the data (`src/make_thesis_pdf.py`) |
| `results/charts/` | one correlation chart per regression term (raw r % and partial r % after controls), `all_charts.pdf`, `chart_index.csv` |
| `results/details/` | full model summaries and the data frame behind each test |
| `results/extensions/`, `src/ext*.py` | follow-up analyses (items 1, 4, 5, 6-12): cost bridges, fleet mix, listings, registrations, warranty risk |
