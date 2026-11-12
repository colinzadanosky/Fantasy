# 15. Testing the analogs with regressions

## Bottom line

| Analog | Test | Result | Does Stellantis look like it? |
|---|---|---|---|
| Nike 2022 / GM 2005 (inventory glut -> discount) | R1: balance-sheet inventory-sales gap -> next-year gross margin, NKE/HOG/F | Null on average; Nike 2022 is an outlier | Can't tell from balance sheets. Dealer retail days' supply (152-169 vs 82) is the relevant gauge, and it is at glut levels |
| Nissan 2016-18 (bought share reverses) | R2: 2-yr share gain -> next 2-yr change, 10 groups 2005-25 | Weak reversal (-0.09, n.s.) | Share gains are not mechanically given back; it depends on how they were bought |
| Chrysler 2008 (V8 lineup vs fuel) | R3: share change on gas-price change | No significant exposure for any group; Chrysler's 2008 fall was mostly the credit crisis and bankruptcy | Fuel risk to the Hemi is real for a shock, but not visible in annual share data |
| Nissan vs Chrysler-2009 path | R4: share path since peak, indexed | Stellantis tracks Chrysler 2005-11 best (RMSE 8.4) and Nissan 2017-24 close behind (9.2) | 2026 share is rising (7.8% vs 7.4%), which leans toward the Chrysler-style rebound, *if* it is retail |
| Harley 2020+ (price up, volume down) | R5: ATP premium -> next-year share, all carmakers | Positive and significant, the opposite of the lesson, because ATP premium measures mix | Pricing power has to be measured like-for-like (item 1: Hemi about 1.7 pp smaller discount) |

**Takeaway.** The analogs split on one variable: whether the volume was retail at stable like-for-like prices (Chrysler 2010-13 rebound under Fiat, built on Ram/Jeep retail) or bought through fleet and dealer stock (Nissan 2016-18, GM 2005). The regressions cannot decide that for Stellantis, but the direct measures can. Retail days' supply about 2x industry, about half of Ram's Q3 growth non-retail, and 145k units of channel fill put Stellantis closer to the Nissan side today. The Hemi's retail skew and smaller discount are the Chrysler-side evidence.

## R1. Inventory running ahead of sales -> margin a year later (Nike, Harley-Davidson, GM, Ford; quarterly 2010-2026)

gap = YoY inventory growth − YoY trailing-4Q revenue growth (pp). Outcome = change in trailing-4Q gross margin over the next 4 quarters. Firm fixed effects; SEs clustered by firm (4 clusters, so treat p-values as indicative).

Pooled: **+0.025 pp of gross margin per pp of gap** (SE 0.022, p=0.252, n=179, R² 0.04). Next-year revenue growth: +0.210 pp per pp of gap (p=0.000).

| Firm | coef | SE (HAC) | p | n |
|---|---:|---:|---:|---:|
| F | +0.103 | 0.033 | 0.002 | 60 |
| HOG | +0.019 | 0.027 | 0.486 | 60 |
| NKE | -0.004 | 0.015 | 0.780 | 59 |

Nike's worst quarter: 2022Q3 (inventory +44% vs revenue +2%, gap +42 pp); gross margin then moved -1.9 pp over the following year.

**Result: no reliable signal.** Balance-sheet inventory running ahead of sales does not predict lower gross margin a year later in this panel. Ford's slope is positive (inventory builds ahead of launches). Instead it predicts *higher* next-year revenue growth (+0.21 pp per pp). Nike's 2022 glut (gap +42 pp, margin -1.9 pp) is the exception that made the analog famous, not the rule. GM drops out because it stopped tagging total cost of sales in 2018. **Implication:** the Stellantis risk is not 'inventory' in general. It is *dealer* stock against *retail* demand (Cox 152-169 days), which balance-sheet data cannot see. That is why the retail days' supply series (ext14) matters more than any 10-K ratio.

## R2. Do fast share gains reverse? US brand groups 2005-2025

Share change over the next 2 years on share change over the past 2 years (group FE): **-0.09** (SE 0.09, p=0.330, n=170). A negative coefficient means part of any 2-year share swing reverses in the next 2 years.

Group shares (% of the covered brands):

| year | Chrysler/FCA/Stellantis | Ford | GM | Honda | Hyundai-Kia | Mazda | Nissan | Subaru | Toyota | VW |
|---|---|---|---|---|---|---|---|---|---|---|
| 2005 | 15.5 | 18.5 | 24.6 | 8.6 | 5.3 | 1.8 | 8.0 | 1.9 | 14.3 | 1.5 |
| 2007 | 14.8 | 15.7 | 22.2 | 9.8 | 5.8 | 2.1 | 8.3 | 1.8 | 17.9 | 1.5 |
| 2009 | 10.0 | 16.7 | 19.5 | 11.3 | 8.2 | 2.2 | 8.9 | 2.3 | 18.6 | 2.2 |
| 2013 | 12.5 | 17.7 | 19.3 | 9.5 | 8.8 | 2.0 | 9.1 | 3.0 | 15.3 | 2.8 |
| 2016 | 14.0 | 16.4 | 18.8 | 9.2 | 9.1 | 1.8 | 9.7 | 3.8 | 15.0 | 2.0 |
| 2017 | 13.0 | 16.6 | 19.0 | 9.4 | 8.1 | 1.8 | 10.1 | 4.1 | 15.5 | 2.2 |
| 2019 | 14.3 | 15.7 | 18.8 | 9.5 | 8.6 | 1.8 | 8.8 | 4.6 | 15.6 | 2.4 |
| 2021 | 13.2 | 14.3 | 17.1 | 9.9 | 10.8 | 2.5 | 7.4 | 4.5 | 17.6 | 2.8 |
| 2023 | 11.4 | 14.9 | 19.4 | 8.7 | 11.9 | 2.7 | 6.8 | 4.8 | 16.9 | 2.5 |
| 2024 | 9.4 | 15.1 | 19.8 | 9.4 | 11.8 | 3.1 | 6.7 | 4.9 | 17.0 | 2.8 |
| 2025 | 8.9 | 15.5 | 20.1 | 9.2 | 12.4 | 2.9 | 6.5 | 4.5 | 17.8 | 2.3 |

## R3. Fuel-price exposure of share (Chrysler 2008 lesson)

Annual change in brand-group share on the change in log average US gasoline price, 2006-2025:

| group | beta_pp_share_per_100pct_gas | se | p | n |
|---|---|---|---|---|
| Honda | -1.25 | 1.41 | 0.375 | 20 |
| Subaru | -0.39 | 0.19 | 0.037 | 20 |
| Ford | -0.28 | 1.18 | 0.815 | 20 |
| Toyota | -0.16 | 1.5 | 0.913 | 20 |
| VW | -0.15 | 0.44 | 0.737 | 20 |
| Hyundai-Kia | 0.07 | 1.29 | 0.955 | 20 |
| GM | 0.09 | 1.78 | 0.958 | 20 |
| Mazda | 0.15 | 0.2 | 0.473 | 20 |
| Nissan | 0.46 | 0.89 | 0.603 | 20 |
| Chrysler/FCA/Stellantis | 1.45 | 1.49 | 0.33 | 20 |

## R4. Which analog is Stellantis tracking? Share paths indexed to each group's peak year = 100

| index | Stellantis (peak 2019) | Nissan (peak 2017) | GM (peak 2005) | Chrysler (peak 2005) |
|---|---|---|---|---|
| 0 | 100.0 | 100.0 | 100.0 | 100.0 |
| 1 | 96.6 | 94.1 | 92.8 | 96.4 |
| 2 | 92.4 | 86.7 | 90.0 | 95.6 |
| 3 | 90.4 | 69.2 | 85.8 | 80.9 |
| 4 | 79.8 | 72.8 | 79.3 | 64.5 |
| 5 | 66.1 | 60.5 | 83.1 | 66.0 |
| 6 | 62.1 | 66.8 | 85.7 | 74.7 |
| 7 | nan | 66.0 | 78.3 | 79.5 |
| 8 | nan | 63.6 | 78.4 | 80.9 |
| 9 | nan | nan | 78.3 | 89.1 |
| 10 | nan | nan | 77.8 | 90.6 |

| analog | years_compared | corr | rmse_index_pts | analog_index_at_year_of_stla_latest | analog_index_two_years_later |
|---|---|---|---|---|---|
| Chrysler (peak 2005) | 7 | 0.82 | 8.4 | 74.7 | 80.9 |
| Nissan (peak 2017) | 7 | 0.85 | 9.2 | 66.8 | 63.6 |
| GM (peak 2005) | 7 | 0.7 | 11.3 | 85.7 | 78.4 |

2026 is not added to the path. GCBC's 2026 year-to-date mixes quarterly reporters (Stellantis, GM: through September) with monthly reporters (through October), which biases Stellantis down. Stellantis's own figure is US share 7.8% for 9M 2026 vs 7.4% for 9M 2025 (Q3 2026 interim report): **up, which is off the Nissan path and toward the Chrysler-2010 rebound.** Two years after the matching point, the analogs imply a 2027 Stellantis share (on the GCBC basis) of Nissan 8.4%, GM 8.1%, Chrysler 9.6% (2025: 8.9%).

## R5. Does a price premium cost share the next year? All carmaker groups, KBB ATP 2022-2024 -> share 2023-2025 (the Harley lesson)

Next-year share change on ATP premium over industry (group FE, clustered): **+0.158 pp share per pp premium** (SE 0.032, p=0.000, n=30). Without FE: -0.011 (p=0.117).

Stellantis ATP premium by year: 2022 +14.4%, 2023 +18.5%, 2024 +17.8%, 2025 +9.9%, 2026 +15.6%.

**Read: across carmakers, a higher ATP premium is followed by share *gains*, the opposite of the Stellantis-only result (test 13: -0.14). With only 3 years per group, the fixed-effect slope picks up mix: premium rises when trucks and high trims sell, which is demand strength, not price discipline. The Harley lesson (price up, volume down) is therefore **not** detectable in transaction-price data. It needs like-for-like prices, as in the listings in item 1. Stellantis's 2026 premium rebound (+5.7 pp) should not be read as either pricing power or a share threat until mix is separated out.

Harley-Davidson and Nike are not in R2-R5 because they have no car-share series; they enter through R1.
