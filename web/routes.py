# webroutes.py
from fastapi import APIRouter, Query
from typing import Optional
from strategy import scan_and_alert
from data_fetcher import fetch_market_data
import asyncio

router = APIRouter()

# Root health check
@router.get("/")
async def root():
    return {"status": "ok", "message": "Binary Options Strategy API is running"}

# Manual trigger for strategy scan
@router.get("/scan")
async def run_scan(
    timeframe: str = Query(..., regex="^(1m|2m|3m|5m)$", description="Timeframe to scan"),
    pair: Optional[str] = Query(None, description="Optional currency pair (e.g., EURUSD)")
):
    """
    Run the scan_and_alert function manually.
    If 'pair' is provided, only that pair will be scanned.
    """
    if pair:
        pairs = [pair]
    else:
        # Your 50-pair setup
        pairs = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD",
            "NZDUSD", "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", "CHFJPY",
            "EURAUD", "GBPAUD", "AUDCAD", "AUDCHF", "AUDNZD", "CADCHF",
            "CADJPY", "EURNZD", "GBPCAD", "GBPNZD", "NZDCAD", "NZDCHF",
            "NZDJPY", "USDHKD", "USDSEK", "USDNOK", "USDZAR", "USDTRY",
            "EURSEK", "EURNOK", "EURTRY", "EURZAR", "GBPSEK", "GBPNOK",
            "GBPTRY", "GBPZAR", "AUDSGD", "AUDHKD", "CADSGD", "CHFSGD",
            "EURSGD", "GBPSGD", "NZDSGD", "USDINR", "USDSGD", "USDTHB",
            "USDMXN", "USDPLN"
        ]

    market_data = await fetch_market_data(pairs, timeframe)
    alerts = scan_and_alert(market_data, timeframe)
    return {"timeframe": timeframe, "alerts": alerts}


# Endpoint to fetch raw market data
@router.get("/market-data")
async def get_market_data(
    timeframe: str = Query(..., regex="^(1m|2m|3m|5m)$"),
    pair: Optional[str] = None
):
    if pair:
        pairs = [pair]
    else:
        pairs = ["EURUSD", "GBPUSD", "USDJPY"]  # Trimmed for speed
    data = await fetch_market_data(pairs, timeframe)
    return data
