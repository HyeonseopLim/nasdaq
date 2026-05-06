from __future__ import annotations

from typing import Iterable


FRED_SERIES_INFO = {
    "nasdaq100": {
        "label": "Nasdaq-100 Index",
        "cadence": "Daily",
        "description": (
            "나스닥100 지수의 수준이다. 애플, 마이크로소프트, 엔비디아 같은 대형 비금융 기술주가 "
            "많이 들어 있어서, 기술주 전체 분위기를 보여주는 대표 지표다. 숫자 자체보다도 "
            "최근 며칠 또는 몇 주 동안 얼마나 올랐는지가 더 중요하다."
        ),
    },
    "nasdaqcom": {
        "label": "NASDAQ Composite Index",
        "cadence": "Daily",
        "description": (
            "나스닥 종합지수 수준이다. 나스닥100보다 더 넓은 범위의 나스닥 상장 종목을 담는다. "
            "기술주 중심 시장의 전체 체력을 보는 데 쓴다."
        ),
    },
    "sp500": {
        "label": "S&P 500 Index",
        "cadence": "Daily",
        "description": (
            "미국 대형주 전체를 넓게 보여주는 S&P 500 지수다. 나스닥만 볼 때 생기는 편향을 줄이고, "
            "미국 주식시장 전체 분위기와 비교할 때 쓴다."
        ),
    },
    "vixcls": {
        "label": "VIX",
        "cadence": "Daily",
        "description": (
            "VIX는 흔히 '공포지수'라고 불린다. 투자자들이 앞으로 시장이 얼마나 크게 흔들릴지 "
            "두려워하는지를 숫자로 보여준다. 일반적으로 높을수록 불안이 크고, 낮을수록 시장이 "
            "차분하다고 해석한다."
        ),
    },
    "dgs10": {
        "label": "10Y Treasury Yield",
        "cadence": "Daily",
        "description": (
            "미국 10년 국채 금리다. 시장이 장기적으로 요구하는 기본 수익률에 가깝다. "
            "기술주는 미래 이익 기대가 큰 편이라 장기금리가 오르면 가치평가에 부담이 되기 쉽다."
        ),
    },
    "dgs2": {
        "label": "2Y Treasury Yield",
        "cadence": "Daily",
        "description": (
            "미국 2년 국채 금리다. 연준의 금리 정책 기대를 더 민감하게 반영하는 편이다. "
            "단기 정책 변화 기대가 커질 때 빠르게 움직인다."
        ),
    },
    "t10y2y": {
        "label": "10Y-2Y Treasury Spread",
        "cadence": "Daily",
        "description": (
            "10년 금리에서 2년 금리를 뺀 값이다. 장단기 금리차라고 부른다. "
            "이 값이 작아지거나 음수가 되면 경기 둔화 우려로 해석되는 경우가 많다."
        ),
    },
    "dfii10": {
        "label": "10Y Real Yield",
        "cadence": "Daily",
        "description": (
            "물가 영향을 뺀 10년 실질금리다. 투자자 입장에서는 '진짜 금리'에 가깝다. "
            "실질금리가 오르면 성장주 밸류에이션이 압박받는 경우가 많다."
        ),
    },
    "t10yie": {
        "label": "10Y Breakeven Inflation",
        "cadence": "Daily",
        "description": (
            "시장 참가자들이 보는 10년 기대 인플레이션이다. 앞으로 물가가 얼마나 오를 것으로 "
            "보는지의 대략적인 기대치를 나타낸다."
        ),
    },
    "dff": {
        "label": "Effective Fed Funds Rate",
        "cadence": "Daily",
        "description": (
            "미국 기준금리에 가장 가까운 단기 정책금리다. 연준이 돈의 가격을 얼마나 높게 유지하는지 "
            "보는 기본 지표다."
        ),
    },
    "dtwexbgs": {
        "label": "Broad Dollar Index",
        "cadence": "Daily",
        "description": (
            "달러 강세/약세를 넓게 보여주는 지수다. 달러가 너무 강하면 글로벌 유동성과 위험자산 "
            "선호에 부담이 될 수 있어서 나스닥과 함께 보는 경우가 많다."
        ),
    },
    "dcoilwtico": {
        "label": "WTI Crude Oil",
        "cadence": "Daily",
        "description": (
            "미국 기준 유가인 WTI 원유 가격이다. 유가 급등은 인플레이션 압력을 키우고, "
            "시장 금리 기대를 흔들 수 있다."
        ),
    },
    "bamlh0a0hym2": {
        "label": "High Yield OAS",
        "cadence": "Daily",
        "description": (
            "신용등급이 낮은 회사채가 국채보다 얼마나 더 높은 금리를 요구받는지 보여주는 스프레드다. "
            "값이 커지면 시장이 위험한 기업을 더 불안하게 본다는 뜻이라서 위험회피 신호로 쓰인다."
        ),
    },
    "walcl": {
        "label": "Fed Total Assets",
        "cadence": "Weekly",
        "description": (
            "연준 대차대조표 규모다. 아주 거칠게 보면 시중 유동성이 얼마나 넉넉한지 보는 데 쓰인다. "
            "증가하면 완화적, 감소하면 긴축적 해석을 하는 경우가 많다."
        ),
    },
    "m2sl": {
        "label": "M2 Money Stock",
        "cadence": "Monthly",
        "description": (
            "현금, 요구불예금, 저축성 예금 등을 포함한 넓은 의미의 통화량이다. "
            "시장에 돈이 얼마나 풀려 있는지 보는 장기 지표로 자주 쓰인다."
        ),
    },
    "rrpontsyd": {
        "label": "Reverse Repo",
        "cadence": "Daily",
        "description": (
            "역레포 잔액이다. 금융시스템 안의 단기 유동성이 어디에 머물고 있는지 보는 데 도움을 준다. "
            "값 자체는 낯설 수 있지만 유동성 해석에서는 자주 쓰인다."
        ),
    },
    "wtregen": {
        "label": "Treasury General Account",
        "cadence": "Weekly",
        "description": (
            "미국 재무부의 현금 계좌 잔액이다. 정부 자금이 민간 시스템에서 빠져 있느냐 들어오느냐를 "
            "간접적으로 보여줘서 유동성 분석에 쓰인다."
        ),
    },
    "icsa": {
        "label": "Initial Jobless Claims",
        "cadence": "Weekly",
        "description": (
            "신규 실업수당 청구 건수다. 고용시장이 갑자기 식고 있는지 가장 빠르게 보는 주간 지표 중 하나다. "
            "급증하면 경기 둔화 신호로 해석될 수 있다."
        ),
    },
    "cpiaucsl": {
        "label": "CPI",
        "cadence": "Monthly",
        "description": (
            "소비자물가지수다. 일반 사람들이 체감하는 물가 흐름을 대표하는 지표라서 금리 기대와 시장 변동성에 "
            "직접 영향을 주는 경우가 많다."
        ),
    },
    "unrate": {
        "label": "Unemployment Rate",
        "cadence": "Monthly",
        "description": (
            "미국 실업률이다. 경기와 고용시장의 큰 흐름을 보여주는 대표 지표다. "
            "너무 빠르게 올라가면 경기 둔화 우려가 커질 수 있다."
        ),
    },
}

YAHOO_TICKER_INFO = {
    "qqq": {
        "label": "QQQ",
        "description": (
            "나스닥100을 따라가는 ETF다. 이 프로젝트에서는 사실상 '예측 대상 그 자체'에 가깝다."
        ),
    },
    "smh": {
        "label": "SMH",
        "description": (
            "반도체 업종 ETF다. 반도체는 나스닥의 핵심 엔진 중 하나라서 기술주 열기를 빠르게 반영하는 편이다."
        ),
    },
    "gld": {
        "label": "GLD",
        "description": (
            "금 가격을 따라가는 ETF다. 금은 위험회피, 달러, 실질금리 흐름과 함께 해석하는 경우가 많다."
        ),
    },
    "aapl": {"label": "AAPL", "description": "애플 주가 데이터다. 대형 기술주 중 대표 종목이다."},
    "msft": {"label": "MSFT", "description": "마이크로소프트 주가 데이터다. 클라우드와 AI 기대를 크게 반영한다."},
    "nvda": {"label": "NVDA", "description": "엔비디아 주가 데이터다. AI와 반도체 열기를 강하게 반영하는 핵심 종목이다."},
    "amzn": {"label": "AMZN", "description": "아마존 주가 데이터다. 소비와 클라우드 두 축을 함께 반영한다."},
    "meta": {"label": "META", "description": "메타 주가 데이터다. 광고 경기와 대형 기술주 심리를 함께 보여준다."},
    "googl": {"label": "GOOGL", "description": "알파벳 주가 데이터다. 검색 광고와 AI 기대를 반영한다."},
    "tsla": {"label": "TSLA", "description": "테슬라 주가 데이터다. 성장주 선호와 위험선호 심리를 강하게 반영하는 편이다."},
}

CORE_EXCLUDED_PREFIXES = (
    "aapl_",
    "msft_",
    "nvda_",
    "amzn_",
    "meta_",
    "googl_",
    "tsla_",
)

CORE_EXCLUDED_COLUMNS = {
    "sp500",
    "mag7_eq_ret_1d",
    "mag7_eq_ret_5d",
}

CORE_EXCLUDED_FEATURE_PREFIXES = (
    "sp500_",
    "bamlh0a0hym2",
)


def is_core_column(column: str) -> bool:
    if column == "date":
        return True
    if column.startswith(("qqq_", "smh_", "gld_")):
        return True
    if column in FRED_SERIES_INFO and column not in {"sp500", "bamlh0a0hym2"}:
        return True
    if column.startswith("target_"):
        return True
    if column in CORE_EXCLUDED_COLUMNS:
        return False
    if column.startswith(CORE_EXCLUDED_PREFIXES):
        return False
    if column.startswith(CORE_EXCLUDED_FEATURE_PREFIXES):
        return False
    if column.startswith(
        (
            "vixcls_",
            "dgs10_",
            "dgs2_",
            "t10y2y_",
            "dfii10_",
            "t10yie_",
            "dff_",
            "dtwexbgs_",
            "dcoilwtico_",
            "walcl_",
            "m2sl_",
            "rrpontsyd_",
            "wtregen_",
            "icsa_",
            "cpiaucsl_",
            "unrate_",
            "nasdaq100_",
            "nasdaqcom_",
        )
    ):
        return True
    return False


def core_columns(columns: Iterable[str]) -> list[str]:
    return [column for column in columns if is_core_column(column)]


def column_category(column: str) -> str:
    if column == "date":
        return "key"
    if column.startswith("target_"):
        return "target"
    if column.endswith("_ret_1d") or column.endswith("_ret_5d") or column.endswith("_ret_20d"):
        return "return_feature"
    if column.endswith("_ma50_gap") or column.endswith("_ma200_gap"):
        return "trend_feature"
    if column.endswith("_chg_1d") or column.endswith("_chg_5d") or column.endswith("_pct_5d"):
        return "change_feature"
    if column.endswith(("_open", "_high", "_low", "_close", "_adj_close", "_volume")):
        return "market_raw"
    if column in FRED_SERIES_INFO:
        return "macro_raw"
    if column.startswith("mag7_"):
        return "composite_feature"
    return "other"


def describe_column(column: str) -> str:
    if column == "date":
        return (
            "이 테이블의 기준 날짜다. 모든 데이터는 QQQ가 거래된 날짜를 중심으로 맞춰져 있다. "
            "즉 한 행은 '그날 장 마감 시점까지 알 수 있었던 정보'라고 생각하면 된다."
        )
    if column.startswith("target_"):
        if column.endswith("_up"):
            horizon = column.split("_")[1].replace("d", "")
            return (
                f"{horizon}거래일 뒤 QQQ 조정종가가 오늘보다 높으면 1, 아니면 0이다. "
                "모델이 맞혀야 하는 정답 라벨이다."
            )
        if column.endswith("_return"):
            horizon = column.split("_")[1].replace("d", "")
            return (
                f"앞으로 {horizon}거래일 동안 QQQ 조정종가가 얼마나 올랐거나 내렸는지를 수익률로 나타낸 값이다. "
                "양수면 상승, 음수면 하락이다."
            )
    if column.startswith("mag7_eq_ret_"):
        horizon = column.rsplit("_", 1)[-1]
        return (
            f"매그니피센트7을 같은 비중으로 놓고 계산한 {horizon} 기준 수익률이다. "
            "대형 기술주 분위기를 한 숫자로 압축한 보조 지표다."
        )

    parts = column.split("_")
    prefix = parts[0]
    suffix = "_".join(parts[1:])

    if prefix in YAHOO_TICKER_INFO:
        asset_label = YAHOO_TICKER_INFO[prefix]["label"]
        if suffix == "open":
            return f"{asset_label}의 시가다. 그날 거래가 시작될 때 첫 가격이다."
        if suffix == "high":
            return f"{asset_label}의 고가다. 그날 장중 가장 높았던 가격이다."
        if suffix == "low":
            return f"{asset_label}의 저가다. 그날 장중 가장 낮았던 가격이다."
        if suffix == "close":
            return f"{asset_label}의 종가다. 그날 거래가 끝났을 때 가격이다."
        if suffix == "adj_close":
            return (
                f"{asset_label}의 조정종가다. 배당이나 분할 같은 이벤트를 반영해서 "
                "과거와 현재를 더 공정하게 비교할 수 있게 만든 가격이다."
            )
        if suffix == "volume":
            return f"{asset_label}의 거래량이다. 얼마나 많이 거래됐는지를 보여준다."
        if suffix in {"ret_1d", "ret_5d", "ret_20d"}:
            horizon = suffix.split("_")[1].replace("d", "")
            return (
                f"{asset_label} 조정종가가 최근 {horizon}거래일 동안 몇 퍼센트 변했는지 보여준다. "
                "모멘텀, 즉 최근 상승/하락 흐름을 보는 기본 지표다."
            )
        if suffix in {"ma50_gap", "ma200_gap"}:
            window = "50" if suffix == "ma50_gap" else "200"
            return (
                f"{asset_label} 가격이 {window}일 이동평균보다 얼마나 위나 아래에 있는지 보여준다. "
                "양수면 평균보다 위, 음수면 평균보다 아래다. 추세가 강한지 보는 데 자주 쓴다."
            )

    if column in FRED_SERIES_INFO:
        return FRED_SERIES_INFO[column]["description"]

    for base_column, info in FRED_SERIES_INFO.items():
        if column.startswith(f"{base_column}_"):
            metric = column[len(base_column) + 1 :]
            if metric == "chg_1d":
                return (
                    f"{info['label']}이 하루 전보다 얼마나 변했는지 절대값으로 보여준다. "
                    "예를 들어 금리면 몇 %p 움직였는지, 지수면 몇 포인트 움직였는지다."
                )
            if metric == "chg_5d":
                return (
                    f"{info['label']}이 5거래일 전보다 얼마나 변했는지 절대값으로 보여준다. "
                    "조금 더 느린 방향성을 보는 데 쓴다."
                )
            if metric == "pct_5d":
                return (
                    f"{info['label']}의 5거래일 퍼센트 변화율이다. 값의 크기가 다른 지표끼리도 "
                    "변화 강도를 비교하기 쉽게 해준다."
                )

    return (
        "모델링을 위해 만든 파생 컬럼이거나 원본 컬럼이다. 이름을 보면 보통 "
        "'무슨 자산/지표인지 + 어떤 계산을 했는지'가 같이 들어 있다."
    )


def column_source(column: str) -> str:
    if column == "date":
        return "QQQ calendar"
    if column.startswith("target_") or column.startswith("mag7_"):
        return "Derived from merged dataset"

    parts = column.split("_")
    prefix = parts[0]
    if prefix in YAHOO_TICKER_INFO:
        return f"Yahoo chart / {YAHOO_TICKER_INFO[prefix]['label']}"
    if prefix in FRED_SERIES_INFO:
        return f"FRED / {FRED_SERIES_INFO[prefix]['label']}"
    for base_column, info in FRED_SERIES_INFO.items():
        if column.startswith(f"{base_column}_"):
            return f"FRED / {info['label']}"
    return "Derived"
