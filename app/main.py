from fastapi import FastAPI
from core.config import settings
import requests
app = FastAPI()


@app.get("/")
def simple_api():
    return {"message": "Hello, World!"}

@app.get("/prices/latest")
async def get_prices(symbol: str = "BTC", provider: str = "alpha_vantage"):
    """Get latest price for a given symbol from alpha_vantage"""
    response = requests.get(f'{settings.ALPHA_VANTAGE_API_URL}?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={settings.ALPHA_VANTAGE_API_KEY}')
    data = response.json()
    return {
        "symbol": data["Meta Data"]["2. Symbol"],
        "timestamp": list(data["Time Series (1min)"].keys())[0],
        "latest_price": data["Time Series (1min)"][list(data["Time Series (1min)"].keys())[0]]["1. open"],
        "provider": "Alpha Vantage"
    }
    