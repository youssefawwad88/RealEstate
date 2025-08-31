import pandas as pd
from utils.market_loader import filter_allowed_markets

def test_filter_allowed_markets_simple():
    df = pd.DataFrame({"city_key": ["Dubai","Paris","Greece","Cyprus"]})
    out = filter_allowed_markets(df)
    assert set(out["city_key"].str.lower()) == {"dubai","greece","cyprus"}