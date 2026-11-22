"""Command-line entry point for MarketCouncil."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from getpass import getpass
from pathlib import Path

from .auth import AuthManager
from .backtest import BacktestConfig, SmaCrossStrategy, run_backtest
from .context import load_research_context_json
from .data import DataValidationError, load_ohlcv_csv
from .execution import AlpacaPaperAdapter, BinanceSpotTestnetAdapter
from .marketdata import BinanceKlinesProvider, MarketDataRequest, TwelveDataProvider, write_ohlcv_csv
from .metrics import build_snapshot
from .orchestrator import run_council
from .providers import LiteLLMProvider, MockProvider
from .report import render_json, render_markdown
from .risk import calculate_position_size
from .storage import Database
from .skills import list_skills, read_skill, search_skills, validate_skill_library
from .workflows import list_workflows, read_workflow, validate_workflows


def _write_output(content: str, output: str | None) -> None:
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content + "\n", encoding="utf-8")
    else:
        print(content)


def _provider(name: str):
    if name == "mock":
        return MockProvider()
    if name == "litellm":
        return LiteLLMProvider()
    raise ValueError(f"unsupported provider: {name}")


def _validation_handler(errors: list[str], label: str) -> int:
    if errors:
        print(f"{label} validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"{label} validation passed")
    return 0


def _run_report(args: argparse.Namespace, demo: bool = False) -> int:
    if demo:
        # Fixed deterministic synthetic close path; not a live or historical market series.
        from datetime import UTC, datetime, timedelta

        from .models import Bar

        bars = []
        close = 100.0
        start = datetime(2026, 1, 1, 9, 15, tzinfo=UTC)
        for index in range(30):
            previous = close
            close = 100 + index * 0.23 + (index % 4 - 1.5) * 0.11
            bars.append(
                Bar(
                    timestamp=start + timedelta(days=index),
                    open=previous,
                    high=max(previous, close) + 0.35,
                    low=min(previous, close) - 0.25,
                    close=close,
                    volume=100_000 + index * 2_500,
                )
            )
        snapshot = build_snapshot("DEMO", "1d synthetic", bars, bars_per_year=252)
    else:
        bars = load_ohlcv_csv(args.csv)
        snapshot = build_snapshot(args.symbol, args.timeframe, bars, args.bars_per_year)
    research_context = (
        load_research_context_json(args.context_json)
        if getattr(args, "context_json", None)
        else None
    )
    report = run_council(
        snapshot=snapshot,
        question=args.question,
        provider=_provider(args.provider),
        max_workers=args.max_workers,
        research_context=research_context,
    )
    _write_output(
        render_json(report) if args.format == "json" else render_markdown(report),
        args.output,
    )
    return 0



def _parse_iso(value: str | None):
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone, for example 2026-01-01T00:00:00Z")
    return parsed


def _run_fetch(args: argparse.Namespace) -> int:
    request = MarketDataRequest(
        symbol=args.symbol, interval=args.interval, asset_class=args.asset_class,
        start=_parse_iso(args.start), end=_parse_iso(args.end), limit=args.limit,
        exchange=args.exchange, mic_code=args.mic_code,
    )
    if args.provider == "binance":
        provider = BinanceKlinesProvider(market=args.market)
    else:
        provider = TwelveDataProvider()
    bars = provider.fetch_bars(request)
    write_ohlcv_csv(bars, args.output)
    print(json.dumps({"provider": provider.name, "symbol": args.symbol, "asset_class": args.asset_class, "bars": len(bars), "output": args.output, "first_timestamp": bars[0].timestamp.isoformat(), "last_timestamp": bars[-1].timestamp.isoformat()}, indent=2))
    return 0


def _run_quote(args: argparse.Namespace) -> int:
    if args.provider == "binance":
        quote = BinanceKlinesProvider(market=args.market).fetch_quote(args.symbol, args.asset_class)
    else:
        quote = TwelveDataProvider().fetch_quote(args.symbol, args.asset_class, args.exchange, args.mic_code)
    print(json.dumps(quote.to_dict(), indent=2))
    return 0


def _run_stream(args: argparse.Namespace) -> int:
    from .streaming import stream_binance_trades, stream_twelvedata_prices

    async def consume() -> None:
        if args.provider == "twelvedata":
            stream = stream_twelvedata_prices(
                args.symbols, args.asset_class, max_events=args.max_events
            )
        else:
            stream = stream_binance_trades(
                args.symbols, market=args.market, max_events=args.max_events
            )
        async for tick in stream:
            print(json.dumps(tick.to_dict(), separators=(",", ":")), flush=True)

    try:
        asyncio.run(consume())
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        # Keep credential-bearing URLs, socket details and provider payloads out
        # of console errors. The exception class is enough for triage.
        if isinstance(exc, (ValueError, RuntimeError, DataValidationError, FileNotFoundError)):
            raise
        raise RuntimeError(f"market stream terminated: {type(exc).__name__}") from exc
    return 0


def _run_alpaca_paper_order(args: argparse.Namespace) -> int:
    adapter = AlpacaPaperAdapter()
    result = adapter.place_limit_order(
        symbol=args.symbol, side=args.side, quantity=args.quantity,
        limit_price=args.limit_price, time_in_force=args.time_in_force,
        client_order_id=args.client_order_id,
    )
    print(json.dumps(result.to_dict(), indent=2))
    return 0


def _run_testnet_order(args: argparse.Namespace) -> int:
    adapter = BinanceSpotTestnetAdapter()
    result = adapter.place_limit_order(
        symbol=args.symbol, side=args.side, quantity=args.quantity, price=args.price,
        time_in_force=args.time_in_force, client_order_id=args.client_order_id,
    )
    print(json.dumps(result.to_dict(), indent=2))
    return 0


def _run_backtest(args: argparse.Namespace) -> int:
    bars = load_ohlcv_csv(args.csv)
    strategy = SmaCrossStrategy(fast=args.fast, slow=args.slow)
    result = run_backtest(
        bars, strategy,
        BacktestConfig(
            initial_equity=args.initial_equity,
            commission_bps=args.commission_bps,
            slippage_bps=args.slippage_bps,
            bars_per_year=args.bars_per_year,
            allow_short=args.allow_short,
        ),
    )
    content = json.dumps(result.to_dict(), indent=2)
    _write_output(content, args.output)
    return 0


def _run_user_create(args: argparse.Namespace) -> int:
    password = getpass("Password (12+ characters): ")
    confirmation = getpass("Confirm password: ")
    if password != confirmation:
        raise ValueError("password confirmation did not match")
    database = Database(args.database)
    user = AuthManager(database).register(args.username, password)
    print(json.dumps({"id": user.id, "username": user.username, "role": user.role, "database": args.database}, indent=2))
    return 0


def _run_api(args: argparse.Namespace) -> int:
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError("API extras are optional; install with `pip install -e '.[api]'`") from exc
    if args.host not in {"127.0.0.1", "localhost", "::1"} and os.getenv("MC_ACK_PUBLIC_API_RISK") != "1":
        raise ValueError("non-local bind requires MC_ACK_PUBLIC_API_RISK=1 and a TLS/rate-limiting reverse proxy")
    from .api import create_app
    uvicorn.run(create_app(args.database), host=args.host, port=args.port, log_level=args.log_level)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="market-council",
        description="Multi-agent trading research and deterministic risk workflow toolkit.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    demo = commands.add_parser("demo", help="run the deterministic synthetic offline demo")
    demo.add_argument("--format", choices=("markdown", "json"), default="markdown")
    demo.add_argument("--output")
    demo.add_argument(
        "--question",
        default="Assess the supplied synthetic OHLCV context and identify missing evidence",
    )
    demo.add_argument("--provider", choices=("mock", "litellm"), default=os.getenv("MC_PROVIDER", "mock"))
    demo.add_argument("--max-workers", type=int, default=8)
    demo.set_defaults(handler=lambda args: _run_report(args, demo=True))

    analyze = commands.add_parser("analyze", help="analyse a user-provided OHLCV CSV")
    analyze.add_argument("--csv", required=True)
    analyze.add_argument("--symbol", required=True)
    analyze.add_argument("--context-json", help="optional JSON object with source-dated research inputs")
    analyze.add_argument("--timeframe", default="unspecified")
    analyze.add_argument("--bars-per-year", type=int)
    analyze.add_argument("--question", default="Summarise the evidence, risks, and missing inputs")
    analyze.add_argument("--provider", choices=("mock", "litellm"), default=os.getenv("MC_PROVIDER", "mock"))
    analyze.add_argument("--format", choices=("markdown", "json"), default="markdown")
    analyze.add_argument("--output")
    analyze.add_argument("--max-workers", type=int, default=8)
    analyze.set_defaults(handler=lambda args: _run_report(args))

    skills = commands.add_parser("skills", help="list or display skill playbooks")
    skill_commands = skills.add_subparsers(dest="skills_command", required=True)
    skills_list = skill_commands.add_parser("list", help="list bundled skills")
    skills_list.set_defaults(
        handler=lambda _args: (print("\n".join(f"{name}: {description}" for name, description in list_skills())) or 0)
    )
    skills_show = skill_commands.add_parser("show", help="display one skill playbook")
    skills_show.add_argument("name")
    skills_show.set_defaults(handler=lambda args: (print(read_skill(args.name)) or 0))
    skills_search = skill_commands.add_parser("search", help="search skill names and contents")
    skills_search.add_argument("query", nargs="+")
    skills_search.set_defaults(
        handler=lambda args: (
            print("\n".join(f"{name}: {description}" for name, description in search_skills(" ".join(args.query)))) or 0
        )
    )
    skills_validate = skill_commands.add_parser("validate", help="validate all skill metadata and sections")
    skills_validate.set_defaults(
        handler=lambda _args: _validation_handler(validate_skill_library(), "skill library")
    )

    workflows = commands.add_parser("workflows", help="list or display trader workflows")
    workflow_commands = workflows.add_subparsers(dest="workflow_command", required=True)
    workflows_list = workflow_commands.add_parser("list", help="list workflow manifests")
    workflows_list.set_defaults(
        handler=lambda _args: (print("\n".join(f"{name}: {title}" for name, title in list_workflows())) or 0)
    )
    workflows_show = workflow_commands.add_parser("show", help="display a workflow manifest")
    workflows_show.add_argument("name")
    workflows_show.set_defaults(
        handler=lambda args: (print(json.dumps(read_workflow(args.name), indent=2)) or 0)
    )
    workflows_validate = workflow_commands.add_parser("validate", help="validate workflow manifests")
    workflows_validate.set_defaults(
        handler=lambda _args: _validation_handler(validate_workflows(), "workflow manifests")
    )

    fetch = commands.add_parser("fetch", help="fetch historical OHLCV from a selected market-data provider")
    fetch.add_argument("--provider", choices=("twelvedata", "binance"), required=True)
    fetch.add_argument("--symbol", required=True)
    fetch.add_argument("--asset-class", choices=("equity", "fx", "crypto", "futures", "crypto_futures"), required=True)
    fetch.add_argument("--interval", default="1day", help="provider interval (e.g. 1day, 1h, 5m)")
    fetch.add_argument("--start", help="timezone-aware ISO timestamp")
    fetch.add_argument("--end", help="timezone-aware ISO timestamp")
    fetch.add_argument("--limit", type=int, default=500)
    fetch.add_argument("--market", choices=("spot", "usdm"), default="spot", help="Binance market type")
    fetch.add_argument("--exchange", help="optional Twelve Data exchange code")
    fetch.add_argument("--mic-code", help="optional ISO 10383 market identifier code")
    fetch.add_argument("--output", required=True)
    fetch.set_defaults(handler=_run_fetch)

    quote = commands.add_parser("quote", help="fetch a current quote or best bid/ask snapshot")
    quote.add_argument("--provider", choices=("twelvedata", "binance"), required=True)
    quote.add_argument("--symbol", required=True)
    quote.add_argument("--asset-class", choices=("equity", "fx", "crypto", "futures", "crypto_futures"), required=True)
    quote.add_argument("--market", choices=("spot", "usdm"), default="spot")
    quote.add_argument("--exchange")
    quote.add_argument("--mic-code")
    quote.set_defaults(handler=_run_quote)

    stream = commands.add_parser("stream", help="stream read-only live market trades or prices as JSONL")
    stream.add_argument("--provider", choices=("twelvedata", "binance"), required=True)
    stream.add_argument("--symbols", nargs="+", required=True, help="up to 50 provider symbols")
    stream.add_argument("--asset-class", choices=("equity", "fx", "crypto", "futures"), default="crypto")
    stream.add_argument("--market", choices=("spot", "usdm"), default="spot", help="Binance market type")
    stream.add_argument("--max-events", type=int, help="stop after this many normalized ticks")
    stream.set_defaults(handler=_run_stream)

    alpaca_paper = commands.add_parser("alpaca-paper-limit", help="place a LIMIT order through Alpaca PAPER account only")
    alpaca_paper.add_argument("--symbol", required=True)
    alpaca_paper.add_argument("--side", choices=("buy", "sell"), required=True)
    alpaca_paper.add_argument("--quantity", type=float, required=True)
    alpaca_paper.add_argument("--limit-price", type=float, required=True)
    alpaca_paper.add_argument("--time-in-force", choices=("day", "gtc", "ioc", "fok"), default="day")
    alpaca_paper.add_argument("--client-order-id")
    alpaca_paper.set_defaults(handler=_run_alpaca_paper_order)

    testnet = commands.add_parser("binance-testnet-limit", help="place a LIMIT order on Binance Spot testnet only")
    testnet.add_argument("--symbol", required=True)
    testnet.add_argument("--side", choices=("BUY", "SELL"), required=True)
    testnet.add_argument("--quantity", type=float, required=True)
    testnet.add_argument("--price", type=float, required=True)
    testnet.add_argument("--time-in-force", choices=("GTC", "IOC", "FOK"), default="GTC")
    testnet.add_argument("--client-order-id")
    testnet.set_defaults(handler=_run_testnet_order)

    backtest = commands.add_parser("backtest", help="run an event-time-aware SMA research backtest")
    backtest.add_argument("--csv", required=True)
    backtest.add_argument("--fast", type=int, default=10)
    backtest.add_argument("--slow", type=int, default=30)
    backtest.add_argument("--initial-equity", type=float, default=100000.0)
    backtest.add_argument("--commission-bps", type=float, default=5.0)
    backtest.add_argument("--slippage-bps", type=float, default=5.0)
    backtest.add_argument("--bars-per-year", type=int)
    backtest.add_argument("--allow-short", action="store_true")
    backtest.add_argument("--output")
    backtest.set_defaults(handler=_run_backtest)

    users = commands.add_parser("users", help="local user management")
    user_commands = users.add_subparsers(dest="user_command", required=True)
    user_create = user_commands.add_parser("create", help="create a trader account; password is prompted securely")
    user_create.add_argument("--username", required=True)
    user_create.add_argument("--database", default=os.getenv("MC_DATABASE_PATH", "./var/marketcouncil.sqlite3"))
    user_create.set_defaults(handler=_run_user_create)

    serve = commands.add_parser("serve-api", help="run the optional authenticated research/paper API")
    serve.add_argument("--database", default=os.getenv("MC_DATABASE_PATH", "./var/marketcouncil.sqlite3"))
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--log-level", choices=("critical", "error", "warning", "info", "debug", "trace"), default="info")
    serve.set_defaults(handler=_run_api)

    size = commands.add_parser("size", help="calculate risk-bounded position size")
    size.add_argument("--equity", type=float, required=True)
    size.add_argument("--risk-pct", type=float, required=True)
    size.add_argument("--entry", type=float, required=True)
    size.add_argument("--stop", type=float, required=True)
    size.add_argument("--side", choices=("long", "short"), required=True)
    size.add_argument("--fee-pct", type=float, default=0.0)
    size.add_argument("--slippage-pct", type=float, default=0.0)
    size.add_argument("--max-position-pct", type=float, default=100.0)
    size.set_defaults(
        handler=lambda args: print(
            json.dumps(
                calculate_position_size(
                    equity=args.equity,
                    risk_pct=args.risk_pct,
                    entry=args.entry,
                    stop=args.stop,
                    side=args.side,
                    fee_pct=args.fee_pct,
                    slippage_pct=args.slippage_pct,
                    max_position_pct=args.max_position_pct,
                ).to_dict(),
                indent=2,
            )
        )
        or 0
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args) or 0)
    except (ValueError, DataValidationError, FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
