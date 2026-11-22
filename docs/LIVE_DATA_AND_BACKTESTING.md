# Market data and historical backtesting

## Market data connectors

MarketCouncil includes explicit opt-in REST adapters:

| Provider | Supported use | Data path | Credential requirement |
|---|---|---|---|
| Twelve Data | Equities, FX, crypto, selected listed futures/instruments subject to catalogue and plan | Historical OHLCV and current `/quote` snapshots | `TWELVEDATA_API_KEY` |
| Binance Spot | Crypto spot | Historical klines and current best bid/ask snapshot | Public endpoints do not require a key |
| Binance USD-M | Crypto perpetual/futures contracts | Historical klines and current best bid/ask snapshot | Public endpoints do not require a key |
| CSV | Any supported instrument with a user-exported OHLCV history | Local historical bars | None |

The Twelve Data adapter uses its HTTPS `/time_series` and `/quote` endpoints, `Authorization: apikey ...` authentication, provider-declared intervals, optional exchange/MIC filters, and explicit date bounds. The `timezone=UTC` parameter applies to intraday intervals; Twelve Data documents that daily, weekly and monthly bars retain exchange-local timestamps and ignore this parameter. For date-bounded daily/weekly/monthly queries, preserve the supplied wall-clock boundary because Twelve Data interprets these in exchange-local time; supply exchange-local boundary times for listed stocks (UTC is the default for FX and cryptocurrencies). Date-only daily bars are normalised internally to midnight UTC as a session-date label, not as an exact exchange-open timestamp. Check the symbol catalogue, exchange, real-time entitlement, quota, and data redistribution terms for the account before use. Official documentation: <https://twelvedata.com/docs>, <https://support.twelvedata.com/en/articles/5214728-getting-historical-data>, and <https://support.twelvedata.com/en/articles/5745849-timezones>.

The Binance REST adapter uses public market-data endpoints only (`/api/v3/klines`, `/fapi/v1/klines`, and their `ticker/bookTicker` counterparts). It never calls private account endpoints from the data connector. Binance API documentation: <https://developers.binance.com/en/docs/products/spot/rest-api>, <https://developers.binance.com/en/docs/introduction>, and endpoint catalogue: <https://developers.binance.com/en/docs/catalog>.

### Fetch historical bars

```bash
# Equity history and optional exchange hint
export TWELVEDATA_API_KEY="<load-from-secret-manager>"
market-council fetch --provider twelvedata --asset-class equity \
  --symbol AAPL --exchange NASDAQ --interval 1day --limit 500 \
  --output ./data/AAPL.csv

# FX history using a full bounded date range
market-council fetch --provider twelvedata --asset-class fx \
  --symbol EUR/USD --interval 1day \
  --start 2024-01-01T00:00:00Z --end 2025-01-01T00:00:00Z \
  --output ./data/EURUSD.csv

# Crypto spot history
market-council fetch --provider binance --market spot --asset-class crypto \
  --symbol BTCUSDT --interval 1h --limit 1000 --output ./data/BTCUSDT.csv

# USD-M perpetual/futures history
market-council fetch --provider binance --market usdm --asset-class crypto_futures \
  --symbol BTCUSDT --interval 15m --limit 1000 --output ./data/BTCUSDT-PERP.csv
```

### Get current quote snapshots

```bash
market-council quote --provider twelvedata --asset-class equity \
  --symbol AAPL --exchange NASDAQ
market-council quote --provider binance --market spot \
  --asset-class crypto --symbol BTCUSDT
market-council quote --provider binance --market usdm \
  --asset-class crypto_futures --symbol BTCUSDT
```

### Stream live price/trade events

Install the optional stream dependency:

```bash
python -m pip install -e ".[stream]"
```

Twelve Data streams price events for supported stocks, FX, crypto and selected other instruments, subject to symbol catalogue and account entitlement. The API key is sent in the `X-TD-APIKEY` connection header rather than embedded in the URL. The client sends the provider heartbeat approximately every 10 seconds, validates each event, and prints normalized JSON Lines:

```bash
export TWELVEDATA_API_KEY="<load-from-secret-manager>"
market-council stream --provider twelvedata --asset-class equity --symbols AAPL MSFT
market-council stream --provider twelvedata --asset-class fx --symbols EUR/USD USD/JPY
market-council stream --provider twelvedata --asset-class crypto --symbols BTC/USD ETH/USD
# Use only futures symbols covered by your Twelve Data catalogue/subscription.
market-council stream --provider twelvedata --asset-class futures --symbols "<provider-futures-symbol>"
```

Twelve Data's WebSocket documentation describes multi-market subscriptions and a 10-second heartbeat. Each successful subscription consumes WebSocket credits; plans, permitted symbols, exchange entitlements and connection limits vary. The CLI conservatively caps each invocation at 50 symbols. Check your account before subscribing. Sources: <https://twelvedata.com/docs/websocket/websocket-getting-started> and <https://support.twelvedata.com/en/articles/5620516-how-to-stream-the-data>.

Binance public trade streams require no API key:

```bash
market-council stream --provider binance --market spot --symbols BTCUSDT ETHUSDT
market-council stream --provider binance --market usdm --symbols BTCUSDT ETHUSDT
```

Spot uses combined `@trade` streams; USD-M uses the documented `/market/stream` endpoint with `@aggTrade` events. The WebSocket client handles protocol ping/pong, but a connection can expire or close and the CLI intentionally does not reconnect or resubscribe. Binance documents connection lifetimes and stream limits; production consumers must implement reconnect, resubscription and gap recovery before relying on continuous data. Sources: <https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/ws-streams> and <https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market>.

The stream command is read-only and writes ticks to stdout as JSONL. It does not persist ticks, build candles, maintain a full order book, or trigger trading actions. A disconnected feed is an observable interruption, not a silent continuity guarantee. Timestamps are provider event timestamps when supplied; `received_at` is the local UTC observation time. REST quotes remain snapshots and a midpoint is not necessarily an executable fill. Automatic reconnect/resubscribe, sequence-gap recovery, multi-provider failover, corporate-action adjustment and guaranteed real-time coverage are not included.

The Twelve Data catalogue and entitlements determine whether a given futures contract, market, interval, or quote is available on your subscription. The project does not guarantee every symbol or real-time entitlement. The free/paid provider tiers and exchange licensing can differ.

## Backtesting engine

MarketCouncil includes a pluggable single-instrument OHLCV backtesting engine and a reference SMA-cross strategy. The strategy sees only bars available through the current completed bar; signal changes are executed on the next bar's open. It reports terminal equity, total/annualised return (when `bars_per_year` is provided), annualised Sharpe (when mathematically available), maximum drawdown, exposure, turnover, estimated costs and fills.

```bash
market-council backtest --csv ./data/AAPL.csv \
  --fast 10 --slow 30 --initial-equity 100000 \
  --commission-bps 5 --slippage-bps 5 --bars-per-year 252 \
  --output ./reports/AAPL-sma-backtest.json
```

A strategy implements `name` and `target_exposure(history)`, returning an exposure between `-1` and `1`. Short exposure is rejected unless `allow_short=True` is explicitly supplied to the engine. The CLI reference strategy is long/cash only.

The engine is deliberately a transparent starting point. It does not model intrabar order simulation, stops, partial fills, queue priority, bid/ask spread, market impact, funding, borrow availability/cost, futures multipliers, option Greeks/payoff, margin/liquidation, taxes, corporate actions, delisting/survivorship, point-in-time universe construction, or walk-forward optimisation. Do not compare results to a broker statement as though this were a venue-level simulator. Require independently sourced point-in-time data and strategy-specific validation before relying on an experiment.

A successful backtest is not evidence of future profitability. Include data provenance, hypothesis timestamp, universe definition, parameter search history, costs, benchmark, out-of-sample period, sensitivity analysis, and rejected variants in the research record.
