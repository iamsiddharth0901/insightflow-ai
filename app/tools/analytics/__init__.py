from dataclasses import asdict, dataclass

import pandas as pd


@dataclass(frozen=True)
class Fact:
    fact_id: str
    statement: str
    value: float
    source: dict

    def as_dict(self) -> dict:
        return asdict(self)


def period_over_period(df: pd.DataFrame, metric: str = "revenue") -> tuple[float, float]:
    ordered = df.sort_values("period")
    if len(ordered) < 2:
        return 0.0, 0.0
    before, after = float(ordered.iloc[-2][metric]), float(ordered.iloc[-1][metric])
    return after - before, ((after - before) / before if before else 0.0)


def contribution_analysis(df: pd.DataFrame, dimension: str, metric: str = "revenue") -> pd.DataFrame:
    pivoted = df.pivot(index=dimension, columns="period", values=metric).fillna(0)
    if len(pivoted.columns) < 2:
        return pd.DataFrame(columns=[dimension, "delta", "contribution"])
    pivoted["delta"] = pivoted.iloc[:, -1] - pivoted.iloc[:, -2]
    total = float(pivoted["delta"].sum())
    result = pivoted[["delta"]].reset_index()
    result["contribution"] = result["delta"] / total if total else 0.0
    return result.sort_values("delta")
