# Operating Model for Trading Teams

## Intended users

MarketCouncil is a research assistant for discretionary traders, buy-side and sell-side research teams, portfolio/risk professionals, options/futures participants, macro and FX traders, digital-asset researchers, and systematic strategy developers. It is not general-purpose chat and does not replace a firm's investment process, supervisory controls, compliance function, or broker.

## Suggested research loop

1. Define instrument, venue, timeframe, trading session, universe, and research question.
2. Assemble timestamped OHLCV and a source-dated context packet, documenting currency, units, reporting period, and publication lag.
3. Validate source coverage and stale/missing inputs before model analysis.
4. Run the council using a selected provider/model configuration.
5. Review specialist abstentions, bear/bull disagreements, evidence quality, and invalidation conditions.
6. Verify important claims against primary sources and apply firm-approved risk policies separately.
7. Record the human decision and realised outcome in approved systems.

## Responsibility model

- **Trader / portfolio owner:** defines scope, supplies authorised inputs, and remains accountable for decisions.
- **Research lead:** verifies primary evidence, assumptions, source timestamps, and analyst disagreements.
- **Risk reviewer:** independently evaluates position sizing, liquidity, portfolio exposure, and firm limits.
- **Engineering owner:** manages credentials, data lineage, provider configuration, security reviews, and runtime reliability.
- **Compliance / supervision:** determines whether and how the tool may be used in the relevant regulated environment.

## Provider governance

The optional LiteLLM adapter transmits the prompt, market snapshot, and attached research context to the selected provider. Review applicable privacy, retention, region, and training policies. Never include client-identifying or confidential information unless explicitly authorised.

## No autonomous execution

Workflow manifests are operator-led research plans; the CLI does not autonomously execute every workflow step or place orders from council output. Separate, explicit CLI commands are available for local paper simulation, Alpaca Paper LIMIT orders and Binance Spot Testnet LIMIT orders. The multi-agent research report's `execution_authorization` remains `NONE`; it cannot trigger broker execution.
