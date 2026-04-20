from __future__ import annotations

import csv
import http.client
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
REPORT_JSON = DATA_DIR / "source_check_report.json"
REPORT_MD = DATA_DIR / "source_check_report.md"

START_DATE = "2010-01-01"

FRED_SERIES = {
    "NASDAQ100": "Nasdaq-100 Index",
    "NASDAQCOM": "NASDAQ Composite Index",
    "SP500": "S&P 500 Index",
    "VIXCLS": "CBOE Volatility Index: VIX",
    "DGS10": "10-Year Treasury Yield",
    "DGS2": "2-Year Treasury Yield",
    "T10Y2Y": "10Y minus 2Y Treasury Spread",
    "DFII10": "10-Year TIPS Real Yield",
    "T10YIE": "10-Year Breakeven Inflation",
    "DFF": "Effective Federal Funds Rate",
    "DTWEXBGS": "Nominal Broad U.S. Dollar Index",
    "DCOILWTICO": "WTI Crude Oil",
    "BAMLH0A0HYM2": "High Yield Option-Adjusted Spread",
    "WALCL": "Fed Total Assets",
    "M2SL": "M2 Money Stock",
    "RRPONTSYD": "Overnight Reverse Repo",
    "WTREGEN": "Treasury General Account",
    "ICSA": "Initial Claims",
    "CPIAUCSL": "Consumer Price Index",
    "UNRATE": "Unemployment Rate",
}

YAHOO_TICKERS = {
    "QQQ": "Invesco QQQ Trust",
    "SMH": "VanEck Semiconductor ETF",
    "GLD": "SPDR Gold Shares",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "AMZN": "Amazon",
    "META": "Meta Platforms",
    "GOOGL": "Alphabet Class A",
    "TSLA": "Tesla",
}


def fetch_bytes(
    url: str,
    *,
    timeout: int = 20,
    retries: int = 1,
    headers: dict[str, str] | None = None,
) -> bytes:
    headers = headers or {"User-Agent": "Python-urllib/3"}
    last_error: Exception | None = None
    for attempt in range(retries):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            http.client.RemoteDisconnected,
        ) as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}") from last_error


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def summarize_csv_rows(rows: list[dict[str, str]], date_key: str, value_key: str) -> dict[str, object]:
    valid = [
        row
        for row in rows
        if row.get(date_key) and row.get(value_key) not in ("", ".", "null", "None", None)
    ]
    missing = len(rows) - len(valid)
    if not valid:
        return {
            "ok": False,
            "rows": len(rows),
            "valid_rows": 0,
            "missing_rows": missing,
            "first_date": None,
            "latest_date": None,
            "latest_value": None,
        }

    return {
        "ok": True,
        "rows": len(rows),
        "valid_rows": len(valid),
        "missing_rows": missing,
        "first_date": valid[0][date_key],
        "latest_date": valid[-1][date_key],
        "latest_value": valid[-1][value_key],
    }


def check_fred_series(series_id: str, label: str) -> dict[str, object]:
    params = urllib.parse.urlencode(
        {
            "id": series_id,
            "cosd": START_DATE,
        }
    )
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?{params}"
    out_path = RAW_DIR / "fred" / f"{series_id}.csv"
    cache_used = False
    fetch_error = None

    try:
        raw = fetch_bytes(url)
        csv_text = raw.decode("utf-8-sig")
        write_text(out_path, csv_text)
    except Exception as exc:
        if not out_path.exists():
            raise
        cache_used = True
        fetch_error = repr(exc)
        csv_text = out_path.read_text(encoding="utf-8-sig")

    reader = csv.DictReader(csv_text.splitlines())
    rows = list(reader)
    summary = summarize_csv_rows(rows, "observation_date", series_id)
    summary.update(
        {
            "source": "FRED",
            "id": series_id,
            "label": label,
            "raw_file": str(out_path),
            "url": url,
            "cache_used": cache_used,
            "fetch_error": fetch_error,
        }
    )
    return summary


def yahoo_period1() -> int:
    dt = datetime.fromisoformat(START_DATE).replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def check_yahoo_ticker(ticker: str, label: str) -> dict[str, object]:
    period1 = yahoo_period1()
    period2 = int(time.time())
    params = urllib.parse.urlencode(
        {
            "period1": period1,
            "period2": period2,
            "interval": "1d",
            "events": "history",
            "includeAdjustedClose": "true",
        }
    )
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?{params}"
    out_path = RAW_DIR / "yahoo" / f"{ticker}.csv"
    cache_used = False
    fetch_error = None

    try:
        raw = fetch_bytes(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"
                )
            },
        )
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        if not out_path.exists():
            raise
        cache_used = True
        fetch_error = repr(exc)
        csv_text = out_path.read_text(encoding="utf-8")
        rows = list(csv.DictReader(csv_text.splitlines()))
        summary = summarize_csv_rows(rows, "Date", "Close")
        summary.update(
            {
                "source": "Yahoo chart",
                "id": ticker,
                "label": label,
                "raw_file": str(out_path),
                "url": url,
                "cache_used": cache_used,
                "fetch_error": fetch_error,
            }
        )
        return summary

    result = payload.get("chart", {}).get("result") or []
    if not result:
        error = payload.get("chart", {}).get("error")
        raise RuntimeError(f"Yahoo returned no result for {ticker}: {error}")

    chart = result[0]
    timestamps = chart.get("timestamp") or []
    quote = (chart.get("indicators", {}).get("quote") or [{}])[0]
    adjclose = (chart.get("indicators", {}).get("adjclose") or [{}])[0].get("adjclose") or []

    fields = ["open", "high", "low", "close", "volume"]
    rows: list[dict[str, str]] = []
    for index, ts in enumerate(timestamps):
        row = {
            "Date": datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat(),
            "Open": value_at(quote.get("open"), index),
            "High": value_at(quote.get("high"), index),
            "Low": value_at(quote.get("low"), index),
            "Close": value_at(quote.get("close"), index),
            "Adj Close": value_at(adjclose, index),
            "Volume": value_at(quote.get("volume"), index, integer=True),
        }
        if any(row[name.title()] for name in fields if name != "volume") or row["Volume"]:
            rows.append(row)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"],
        )
        writer.writeheader()
        writer.writerows(rows)

    summary = summarize_csv_rows(rows, "Date", "Close")
    summary.update(
        {
            "source": "Yahoo chart",
            "id": ticker,
            "label": label,
            "raw_file": str(out_path),
            "url": url,
            "cache_used": cache_used,
            "fetch_error": fetch_error,
        }
    )
    return summary


def value_at(values: list[object] | None, index: int, *, integer: bool = False) -> str:
    if not values or index >= len(values) or values[index] is None:
        return ""
    value = values[index]
    if integer:
        return str(int(value))
    return f"{float(value):.6f}"


def build_markdown(report: dict[str, object]) -> str:
    generated_at = report["generated_at"]
    lines = [
        "# Data Source Check Report",
        "",
        f"- Generated at: {generated_at}",
        f"- Start date: {START_DATE}",
        "",
        "## Summary",
        "",
        "| Source | ID | Label | Status | Rows | First | Latest | Latest value |",
        "|---|---|---|---:|---:|---|---|---:|",
    ]

    for item in report["results"]:
        if item.get("ok") and item.get("cache_used"):
            status = "CACHED"
        elif item.get("ok"):
            status = "OK"
        else:
            status = "FAIL"
        latest_value = item.get("latest_value")
        lines.append(
            "| {source} | {id} | {label} | {status} | {rows} | {first} | {latest} | {value} |".format(
                source=item.get("source"),
                id=item.get("id"),
                label=item.get("label"),
                status=status,
                rows=item.get("valid_rows"),
                first=item.get("first_date") or "",
                latest=item.get("latest_date") or "",
                value=latest_value if latest_value is not None else "",
            )
        )

    failures = [item for item in report["results"] if not item.get("ok")]
    if failures:
        lines.extend(["", "## Failures", ""])
        for item in failures:
            lines.append(f"- {item.get('source')} {item.get('id')}: {item.get('error')}")

    cached = [item for item in report["results"] if item.get("ok") and item.get("cache_used")]
    if cached:
        lines.extend(["", "## Cached Sources", ""])
        for item in cached:
            lines.append(
                f"- {item.get('source')} {item.get('id')}: reused {item.get('raw_file')} "
                f"because the refresh failed with {item.get('fetch_error')}"
            )

    return "\n".join(lines) + "\n"


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []

    for series_id, label in FRED_SERIES.items():
        print(f"Checking FRED {series_id}...", flush=True)
        try:
            results.append(check_fred_series(series_id, label))
        except Exception as exc:
            results.append(
                {
                    "ok": False,
                    "source": "FRED",
                    "id": series_id,
                    "label": label,
                    "error": repr(exc),
                }
            )

    for ticker, label in YAHOO_TICKERS.items():
        print(f"Checking Yahoo {ticker}...", flush=True)
        try:
            results.append(check_yahoo_ticker(ticker, label))
        except Exception as exc:
            results.append(
                {
                    "ok": False,
                    "source": "Yahoo chart",
                    "id": ticker,
                    "label": label,
                    "error": repr(exc),
                }
            )
        time.sleep(0.8)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "start_date": START_DATE,
        "results": results,
    }
    write_text(REPORT_JSON, json.dumps(report, indent=2))
    write_text(REPORT_MD, build_markdown(report))

    ok_count = sum(1 for item in results if item.get("ok"))
    print(f"\nFinished: {ok_count}/{len(results)} sources OK")
    print(f"JSON report: {REPORT_JSON}")
    print(f"Markdown report: {REPORT_MD}")
    return 0 if ok_count == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
