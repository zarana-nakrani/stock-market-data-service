# Market Data Service

- Market Data Service is an application made for fetching latest market stock price for any given Ticker Symbol from one of the 3 providers (i.e. Alpha Vantage, Yahoo Finance or Finnhub) and storing polled data for multiple symbols every 1 minute.

## API endpoints

### Get Latest Price

**Endpoint:** `GET /prices/latest`

**Query Parameters:**

- `symbol` (required): Stock ticker symbol.
- `provider` (optional): Data provider to fetch the price. If not provided, defaults to `alpha_vantage`.

**Response:**

```json
{
  "symbol": "AAPL",
  "price": 150.25,
  "timestamp": "2025-06-15T12:34:56.789Z",
  "provider": "alpha_vantage"
}
```

**Description:**
This endpoint fetches the latest price for the provided stock symbol using the specified provider. It contacts the respective data provider (Yahoo Finance, Alpha Vantage, or Finnhub), logs the raw and processed data in the database, and returns the processed information.

**Example Request:**

```
curl "http://localhost:8000/prices/latest?symbol=AAPL&provider=finnhub"
```
