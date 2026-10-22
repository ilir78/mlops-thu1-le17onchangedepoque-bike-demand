"""Chronological partitions; test targets are never evaluated in Week 1."""

import pandas as pd

WINDOWS = {
    "train": ("2011-01-01", "2011-12-31"),
    "validation": ("2012-01-01", "2012-06-30"),
    "test": ("2012-07-01", "2012-12-31"),
}


def split_data(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    ordered = frame.sort_values(["dteday", "hr", "instant"], kind="mergesort").copy()
    membership = pd.Series(0, index=ordered.index, dtype="int8")
    partitions = {}
    for name, (start, end) in WINDOWS.items():
        mask = ordered["dteday"].between(start, end, inclusive="both")
        membership += mask.astype("int8")
        partitions[name] = ordered.loc[mask].copy()

    if not membership.eq(1).all():
        raise ValueError("split: require complete exactly-once partition membership")
    if any(part.empty for part in partitions.values()):
        raise ValueError("split: require nonempty partitions")
    return partitions


def partition_summary(partitions: dict[str, pd.DataFrame]) -> dict:
    summary = {}
    for name, part in partitions.items():
        ordered = part.sort_values(["dteday", "hr", "instant"], kind="mergesort")
        first, last = ordered.iloc[0], ordered.iloc[-1]

        def key(row: pd.Series) -> str:
            date = row["dteday"].date().isoformat()
            return f"{date},{int(row['hr'])},{int(row['instant'])}"

        summary[name] = {
            "rows": len(ordered),
            "date_min": str(ordered["dteday"].min().date()),
            "date_max": str(ordered["dteday"].max().date()),
            "first_key": key(first),
            "last_key": key(last),
        }
    return summary
