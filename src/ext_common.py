"""Small helpers shared by the ext*_ extension scripts."""
import pandas as pd


def md_table(df: pd.DataFrame, index=True, fmt="{:.3g}"):
    """DataFrame -> GitHub markdown table without the tabulate dependency."""
    d = df.reset_index() if index else df.copy()
    cell = lambda v: (fmt.format(v) if isinstance(v, float) else str(v))
    out = ["| " + " | ".join(map(str, d.columns)) + " |", "|" + "---|" * len(d.columns)]
    out += ["| " + " | ".join(cell(v) for v in row) + " |" for row in d.itertuples(index=False)]
    return "\n".join(out)
