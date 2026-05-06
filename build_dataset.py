from __future__ import annotations

from pathlib import Path

import pandas as pd

from dataset_catalog import core_columns


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
TRAINING_OUTPUT_CSV = PROCESSED_DIR / "training_dataset.csv"
FULL_OUTPUT_CSV = PROCESSED_DIR / "full_dataset.csv"
FULL_OUTPUT_MD = PROCESSED_DIR / "full_dataset_summary.md"
CORE_OUTPUT_CSV = PROCESSED_DIR / "core_dataset.csv"
CORE_OUTPUT_MD = PROCESSED_DIR / "core_dataset_summary.md"
TRAINING_OUTPUT_MD = PROCESSED_DIR / "training_dataset_summary.md"


FRED_SERIES = [
    "NASDAQ100",
    "NASDAQCOM",
    "SP500",
    "VIXCLS",
    "DGS10",
    "DGS2",
    "T10Y2Y",
    "DFII10",
    "T10YIE",
    "DFF",
    "DTWEXBGS",
    "DCOILWTICO",
    "BAMLH0A0HYM2",
    "WALCL",
    "M2SL",
    "RRPONTSYD",
    "WTREGEN",
    "ICSA",
    "CPIAUCSL",
    "UNRATE",
]

YAHOO_TICKERS = [
    "QQQ",
    "SMH",
    "GLD",
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "GOOGL",
    "TSLA",
]

MAG7_TICKERS = ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA"]


def load_yahoo_prices(ticker: str) -> pd.DataFrame:
    path = RAW_DIR / "yahoo" / f"{ticker}.csv"
    frame = pd.read_csv(path, parse_dates=["Date"])
    frame = frame.rename(
        columns={
            "Date": "date",
            "Open": f"{ticker.lower()}_open",
            "High": f"{ticker.lower()}_high",
            "Low": f"{ticker.lower()}_low",
            "Close": f"{ticker.lower()}_close",
            "Adj Close": f"{ticker.lower()}_adj_close",
            "Volume": f"{ticker.lower()}_volume",
        }
    )
    return frame.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)


def load_fred_series(series_id: str) -> pd.DataFrame:
    path = RAW_DIR / "fred" / f"{series_id}.csv"
    frame = pd.read_csv(path, parse_dates=["observation_date"])
    frame = frame.rename(columns={"observation_date": "date", series_id: series_id.lower()})
    frame[series_id.lower()] = pd.to_numeric(frame[series_id.lower()], errors="coerce")
    return frame.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)


def build_return_features(frame: pd.DataFrame, prefix: str, price_col: str) -> pd.DataFrame:
    price = frame[price_col]
    return pd.DataFrame(
        {
            f"{prefix}_ret_1d": price.pct_change(1, fill_method=None),
            f"{prefix}_ret_5d": price.pct_change(5, fill_method=None),
            f"{prefix}_ret_20d": price.pct_change(20, fill_method=None),
            f"{prefix}_ma50_gap": price / price.rolling(50).mean() - 1.0,
            f"{prefix}_ma200_gap": price / price.rolling(200).mean() - 1.0,
        },
        index=frame.index,
    )


def build_change_features(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    series = frame[column]
    return pd.DataFrame(
        {
            f"{column}_chg_1d": series.diff(1),
            f"{column}_chg_5d": series.diff(5),
            f"{column}_pct_5d": series.pct_change(5, fill_method=None),
        },
        index=frame.index,
    )


def build_dataset() -> pd.DataFrame:
    qqq = load_yahoo_prices("QQQ")
    dataset = qqq.copy()

    for ticker in [ticker for ticker in YAHOO_TICKERS if ticker != "QQQ"]:
        other = load_yahoo_prices(ticker)
        keep_cols = ["date", f"{ticker.lower()}_close", f"{ticker.lower()}_adj_close", f"{ticker.lower()}_volume"]
        dataset = dataset.merge(other[keep_cols], on="date", how="left")

    for series_id in FRED_SERIES:
        fred = load_fred_series(series_id)
        dataset = pd.merge_asof(
            dataset.sort_values("date"),
            fred.sort_values("date"),
            on="date",
            direction="backward",
        )

    dataset = dataset.sort_values("date").reset_index(drop=True)

    fred_cols = [series_id.lower() for series_id in FRED_SERIES]
    dataset[fred_cols] = dataset[fred_cols].ffill()

    feature_frames = [
        build_return_features(dataset, "qqq", "qqq_adj_close"),
        build_return_features(dataset, "smh", "smh_adj_close"),
        build_return_features(dataset, "gld", "gld_adj_close"),
    ]

    for ticker in MAG7_TICKERS:
        feature_frames.append(
            build_return_features(dataset, ticker.lower(), f"{ticker.lower()}_adj_close")
        )

    for column in [
        "vixcls",
        "dgs10",
        "dgs2",
        "t10y2y",
        "dfii10",
        "t10yie",
        "dff",
        "dtwexbgs",
        "dcoilwtico",
        "bamlh0a0hym2",
        "walcl",
        "m2sl",
        "rrpontsyd",
        "wtregen",
        "icsa",
        "cpiaucsl",
        "unrate",
        "nasdaq100",
        "nasdaqcom",
        "sp500",
    ]:
        feature_frames.append(build_change_features(dataset, column))

    features = pd.concat(feature_frames, axis=1)
    dataset = pd.concat([dataset, features], axis=1)

    mag7_prices = dataset[[f"{ticker.lower()}_adj_close" for ticker in MAG7_TICKERS]].mean(axis=1)
    mag7_returns = dataset[[f"{ticker.lower()}_ret_1d" for ticker in MAG7_TICKERS]]
    targets = pd.DataFrame(
        {
            "mag7_eq_ret_1d": mag7_returns.mean(axis=1),
            "mag7_eq_ret_5d": mag7_prices.pct_change(5, fill_method=None),
            "target_1d_return": dataset["qqq_adj_close"].shift(-1) / dataset["qqq_adj_close"] - 1.0,
            "target_5d_return": dataset["qqq_adj_close"].shift(-5) / dataset["qqq_adj_close"] - 1.0,
            "target_20d_return": dataset["qqq_adj_close"].shift(-20) / dataset["qqq_adj_close"] - 1.0,
        },
        index=dataset.index,
    )
    for horizon in [1, 5, 20]:
        ret_col = f"target_{horizon}d_return"
        up_col = f"target_{horizon}d_up"
        up_values = pd.Series(pd.NA, index=dataset.index, dtype="Int64")
        valid = targets[ret_col].notna()
        up_values.loc[valid] = (targets.loc[valid, ret_col] > 0).astype(int)
        targets[up_col] = up_values

    dataset = pd.concat([dataset, targets], axis=1).copy()
    return dataset


def write_summary(dataset: pd.DataFrame, output_path: Path, title: str) -> None:
    target_cols = ["target_1d_up", "target_5d_up", "target_20d_up"]
    lines = [
        f"# {title}",
        "",
        f"- Rows: {len(dataset):,}",
        f"- Columns: {len(dataset.columns):,}",
        f"- Start date: {dataset['date'].min().date()}",
        f"- End date: {dataset['date'].max().date()}",
        "",
        "## Target Balance",
        "",
    ]

    for column in target_cols:
        valid = dataset[column].dropna()
        up_rate = float(valid.mean()) if len(valid) else float("nan")
        lines.append(f"- {column}: {len(valid):,} rows, up-rate {up_rate:.4f}")

    lines.extend(["", "## Missing Values", ""])
    top_missing = dataset.isna().sum().sort_values(ascending=False).head(15)
    for column, count in top_missing.items():
        lines.append(f"- {column}: {int(count):,}")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- The dataset is aligned to QQQ trading days.",
            "- Lower-frequency FRED series are forward-filled onto the QQQ calendar.",
            "- Target columns use future QQQ adjusted close returns over 1, 5, and 20 trading days.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    full_dataset = build_dataset()
    core_dataset = full_dataset[core_columns(full_dataset.columns)].copy()

    full_dataset.to_csv(TRAINING_OUTPUT_CSV, index=False)
    full_dataset.to_csv(FULL_OUTPUT_CSV, index=False)
    core_dataset.to_csv(CORE_OUTPUT_CSV, index=False)

    write_summary(full_dataset, FULL_OUTPUT_MD, "Full Dataset Summary")
    write_summary(core_dataset, CORE_OUTPUT_MD, "Core Dataset Summary")
    write_summary(full_dataset, TRAINING_OUTPUT_MD, "Training Dataset Summary")

    print(f"Saved full dataset: {FULL_OUTPUT_CSV}")
    print(f"Saved core dataset: {CORE_OUTPUT_CSV}")
    print(f"Saved training alias: {TRAINING_OUTPUT_CSV}")
    print(f"Saved summaries: {FULL_OUTPUT_MD}, {CORE_OUTPUT_MD}")
    print(f"Full rows: {len(full_dataset):,}")
    print(f"Full columns: {len(full_dataset.columns):,}")
    print(f"Core rows: {len(core_dataset):,}")
    print(f"Core columns: {len(core_dataset.columns):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
