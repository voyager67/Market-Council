# Research and Technical References

These public resources informed selected architecture and playbook design choices. They are further reading, not software dependencies, endorsements, or evidence that MarketCouncil has achieved any trading performance. The project does not copy source code or skill prose from these works.

## Multi-agent research and quantitative tooling

- TradingAgents, multi-agent financial research architecture and adversarial role decomposition: https://arxiv.org/abs/2412.20138
- Microsoft Qlib, quantitative investment research and model lifecycle toolkit: https://qlib.readthedocs.io/
- FinRL, reinforcement-learning research framework and staged trading environments: https://finrl.readthedocs.io/
- OpenBB, financial data platform and provider-oriented interfaces: https://docs.openbb.co/
- QuantConnect LEAN, algorithmic trading engine and backtest/live workflow references: https://www.quantconnect.com/docs/v2/lean-engine
- NautilusTrader, event-driven trading and simulation architecture: https://nautilustrader.io/docs/latest/

## Market data, execution and market structure

- CCXT manual, exchange API abstraction, market data, rate limits, and exchange-specific behaviour: https://docs.ccxt.com/
- Binance Spot API documentation, REST and stream contracts: https://developers.binance.com/docs/binance-spot-api-docs
- Binance Spot WebSocket Market Streams: https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/ws-streams
- Binance USD-M Futures WebSocket Market Streams: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market
- Twelve Data WebSocket documentation: https://twelvedata.com/docs/websocket/websocket-getting-started
- Twelve Data streaming quickstart: https://support.twelvedata.com/en/articles/5620516-how-to-stream-the-data
- Freqtrade lookahead analysis, a useful reference for detecting future-data leakage: https://www.freqtrade.io/en/latest/lookahead-analysis/
- Freqtrade backtesting documentation, assumptions and configuration considerations: https://www.freqtrade.io/en/latest/backtesting/

## Primary economic, issuer and positioning sources

- SEC EDGAR APIs, issuer submissions and XBRL company facts: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- Federal Reserve Bank of St. Louis FRED API: https://fred.stlouisfed.org/docs/api/fred/
- CFTC Commitments of Traders reports and explanations: https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm

## Derivatives and research methodology

- Options Industry Council, options Greeks and volatility education: https://www.optionseducation.org/advancedconcepts/volatility-and-the-greeks
- Deflated Sharpe Ratio, addressing selection bias and non-normality in performance evaluation: https://doi.org/10.3905/jpm.2014.40.5.094

## Design implications

1. Split research into explicit specialist responsibilities but preserve shared-input and correlated-model limitations.
2. Use opposing hypotheses and falsifiable evidence rather than treating model consensus as proof.
3. Preserve point-in-time source metadata and distinguish publication dates from observation dates.
4. Treat exchange adapters and feeds as venue-specific contracts; do not infer that a generic connector guarantees coverage.
5. Treat backtest validity as a research methodology problem: avoid look-ahead, survivorship, leakage, unrealistic fills, hidden costs, and multiple-testing bias.
6. Keep risk arithmetic deterministic and independent of model-authored instructions.
7. Do not overstate capabilities: references inform playbook design, not implemented market feeds, backtesting, brokerage or exchange connectivity.
