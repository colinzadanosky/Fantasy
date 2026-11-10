"""Run every test (1-56) and write results/regression_results.csv + results/details/.
Data must already be collected (see README for the collect_* / parse_* order)."""
import shutil, warnings
warnings.filterwarnings("ignore")
from common import OUT, RESULTS, save_results

shutil.rmtree(OUT / "details", ignore_errors=True); (OUT / "details").mkdir(parents=True)
import tests_a_volume as A, tests_b_price as B, tests_c_inventory as C, tests_def as D

STEPS = [A.test1, A.test2, A.test3, A.test4, A.test5, A.test6, A.test7, A.test8, A.test9, A.test10,
         B.test11_12, B.test13, B.blocked, C.test28, C.blocked,
         D.test31, D.test32, D.test33, D.test38, D.test40, D.blocked_d, D.test41, D.test45, D.test43, D.test44, D.test46,
         D.test47, D.test48, D.test49, D.test50, D.test51_52, D.test55, D.test56, D.blocked_f]
for f in STEPS:
    f()
r = save_results().sort_values("test", kind="stable")
r.to_csv(OUT / "regression_results.csv", index=False)
status = r.groupby("test").status.first()
print(status.value_counts().to_string())
missing = sorted(set(range(1, 57)) - set(status.index)); print("tests without a row:", missing)
