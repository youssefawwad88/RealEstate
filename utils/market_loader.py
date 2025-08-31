from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional, Tuple, List
import pandas as pd

# default focus markets
ALLOWED_MARKETS_DEFAULT: Tuple[str, ...] = ("dubai", "greece", "cyprus")

# allow overriding the CSV path via env
REFERENCE_PATH = os.getenv(
    "MARKET_RESEARCH_PATH",
    os.path.join("data", "reference", "market_research.csv")
)

EXPECTED_COLS: List[str] = [
    "city_key",
    "land_comp_min",
    "land_comp_avg",
    "land_comp_max",
    "sale_price_min",
    "sale_price_avg",
    "sale_price_max",
    "construction_cost_min",
    "construction_cost_avg",
    "construction_cost_max",
    "soft_cost_pct_typical",
    "absorption_rate",
    "land_gdv_benchmark",
    "profit_margin_benchmark",
    "demand_score",
    "liquidity_score",
    "volatility_score",
    "last_updated",
]

def load_market_benchmarks(path: Optional[str] = None) -> pd.DataFrame:
    """Load benchmarks CSV; return empty DF with schema if missing."""
    csv_path = path or REFERENCE_PATH
    if not os.path.exists(csv_path):
        return pd.DataFrame(columns=EXPECTED_COLS)
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]
    # ensure columns exist & order them
    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = pd.NA
    return df[EXPECTED_COLS].copy()

def filter_allowed_markets(
    df: pd.DataFrame,
    allowed: Optional[Tuple[str, ...]] = None
) -> pd.DataFrame:
    """Filter rows by allowed city keys (case-insensitive)."""
    if df is None or df.empty:
        return df
    if "city_key" not in df.columns:
        return df.iloc[0:0]
    allowed = tuple(a.lower() for a in (allowed or ALLOWED_MARKETS_DEFAULT))
    out = df[df["city_key"].astype(str).str.lower().isin(allowed)].copy()
    return out


def get_available_cities() -> List[str]:
    """Get list of available cities from market data."""
    df = load_market_benchmarks()
    if df.empty or "city_key" not in df.columns:
        return list(ALLOWED_MARKETS_DEFAULT)
    return df["city_key"].tolist()