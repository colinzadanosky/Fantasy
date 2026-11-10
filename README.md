# Stellantis US powertrain demand – regression suite

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
```

`data/raw/` (downloaded pages/PDFs) is not committed; `data/processed/` holds the cleaned inputs used by the tests.

## Layout

| Path | Contents |
|---|---|
| `src/collect_*.py`, `src/parse_*.py`, `src/build_powertrains.py` | data collection and cleaning |
| `src/tests_a_volume.py` … `src/tests_def.py` | tests 1–56 (one function per test) |
| `src/listings_models.py` | hazard / discount models for the listing-scrape tests (16, 17, 21, 22, 26, 27, 29, 30) – ready, awaiting data |
| `results/regression_results.csv` | every coefficient, SE, p, n, status, spec, data, caveat |
| `results/details/` | full model summaries and the data frame behind each test |
