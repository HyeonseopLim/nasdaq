from __future__ import annotations

import argparse
import json
from functools import lru_cache
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pandas as pd

from dataset_catalog import column_category, column_source, describe_column


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
SOURCE_REPORT_PATH = DATA_DIR / "source_check_report.json"
FULL_DATASET_PATH = PROCESSED_DIR / "full_dataset.csv"
CORE_DATASET_PATH = PROCESSED_DIR / "core_dataset.csv"

DATASET_PATHS = {
    "full": FULL_DATASET_PATH,
    "core": CORE_DATASET_PATH,
}


def ensure_datasets_exist() -> None:
    missing = [name for name, path in DATASET_PATHS.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing dataset file(s): "
            + ", ".join(missing)
            + ". Run build_dataset.py first."
        )


@lru_cache(maxsize=2)
def load_dataset(name: str) -> pd.DataFrame:
    path = DATASET_PATHS[name]
    return pd.read_csv(path, low_memory=False)


@lru_cache(maxsize=1)
def load_source_report() -> dict:
    return json.loads(SOURCE_REPORT_PATH.read_text(encoding="utf-8"))


def dataset_overview(name: str) -> dict[str, object]:
    frame = load_dataset(name)
    return {
        "name": name,
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "path": str(DATASET_PATHS[name]),
        "download_url": "/" + DATASET_PATHS[name].relative_to(ROOT).as_posix(),
    }


def source_rows() -> list[dict[str, object]]:
    report = load_source_report()
    rows: list[dict[str, object]] = []
    for item in report["results"]:
        subdir = "fred" if item["source"] == "FRED" else "yahoo"
        filename = f"{item['id']}.csv"
        local_file = DATA_DIR / "raw" / subdir / filename
        rows.append(
            {
                "source": item["source"],
                "id": item["id"],
                "label": item["label"],
                "status": "CACHED" if item.get("cache_used") else ("OK" if item.get("ok") else "FAIL"),
                "rows": item.get("valid_rows"),
                "first_date": item.get("first_date"),
                "latest_date": item.get("latest_date"),
                "latest_value": item.get("latest_value"),
                "url": item.get("url"),
                "local_file": str(local_file),
                "download_url": "/" + local_file.relative_to(ROOT).as_posix(),
            }
        )
    rows.sort(key=lambda row: (row["source"], row["id"]))
    return rows


def glossary_rows(dataset_name: str) -> list[dict[str, str]]:
    frame = load_dataset(dataset_name)
    rows = []
    for column in frame.columns:
        rows.append(
            {
                "column": column,
                "category": column_category(column),
                "source": column_source(column),
                "description": describe_column(column),
            }
        )
    return rows


def paged_table(dataset_name: str, page: int, page_size: int, date_query: str) -> dict[str, object]:
    frame = load_dataset(dataset_name)
    if date_query:
        filtered = frame[frame["date"].astype(str).str.contains(date_query, case=False, na=False)].copy()
    else:
        filtered = frame

    total_rows = len(filtered)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size

    page_frame = filtered.iloc[start:end].copy()
    page_frame = page_frame.astype(object).where(pd.notna(page_frame), None)
    records = page_frame.to_dict(orient="records")

    return {
        "dataset": dataset_name,
        "columns": list(filtered.columns),
        "page": page,
        "page_size": page_size,
        "total_rows": int(total_rows),
        "total_pages": int(total_pages),
        "records": records,
    }


class DatasetViewerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/overview":
            self.send_json(
                {
                    "datasets": {name: dataset_overview(name) for name in DATASET_PATHS},
                    "report_generated_at": load_source_report().get("generated_at"),
                }
            )
            return

        if parsed.path == "/api/sources":
            self.send_json({"rows": source_rows()})
            return

        if parsed.path == "/api/glossary":
            params = parse_qs(parsed.query)
            dataset_name = params.get("dataset", ["full"])[0]
            self.send_json({"rows": glossary_rows(dataset_name)})
            return

        if parsed.path == "/api/table":
            params = parse_qs(parsed.query)
            dataset_name = params.get("dataset", ["full"])[0]
            page = int(params.get("page", ["1"])[0])
            page_size = max(10, min(int(params.get("page_size", ["50"])[0]), 200))
            date_query = params.get("date_query", [""])[0].strip()
            self.send_json(paged_table(dataset_name, page, page_size, date_query))
            return

        if parsed.path == "/":
            self.path = "/viewer/index.html"
        super().do_GET()

    def send_json(self, payload: dict[str, object]) -> None:
        body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local dataset viewer server.")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    ensure_datasets_exist()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), DatasetViewerHandler)
    print(f"Dataset viewer running at http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
