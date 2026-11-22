import json

from marketcouncil.cli import main


def test_demo_command_runs_and_keeps_human_review_boundary(capsys):
    assert main(["demo", "--format", "json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert len(report["agents"]) == 15
    assert report["review_status"] == "HUMAN_REVIEW_REQUIRED"
    assert report["execution_authorization"] == "NONE"


def test_skills_cli_lists_all_playbooks(capsys):
    assert main(["skills", "list"]) == 0
    assert len(capsys.readouterr().out.strip().splitlines()) == 74


def test_skill_search_finds_playbooks_by_domain(capsys):
    assert main(["skills", "search", "commitments", "traders"]) == 0
    output = capsys.readouterr().out
    assert "cot-positioning" in output


def test_skill_and_workflow_validation_commands(capsys):
    assert main(["skills", "validate"]) == 0
    assert "passed" in capsys.readouterr().out
    assert main(["workflows", "validate"]) == 0
    assert "passed" in capsys.readouterr().out


def test_workflow_catalog_has_thirteen_manifests(capsys):
    assert main(["workflows", "list"]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 13


def test_provider_default_can_be_selected_from_environment(monkeypatch):
    from marketcouncil.cli import build_parser

    monkeypatch.setenv("MC_PROVIDER", "litellm")
    args = build_parser().parse_args(["analyze", "--csv", "fixture.csv", "--symbol", "TEST"])
    assert args.provider == "litellm"


def test_backtest_command_smoke(tmp_path, capsys):
    from pathlib import Path
    sample = Path(__file__).parents[1] / "examples" / "synthetic-bars.csv"
    assert main(["backtest", "--csv", str(sample), "--fast", "3", "--slow", "5", "--bars-per-year", "252"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["strategy"] == "sma-cross"
    assert result["observations"] > 0
    assert any("next bar open" in item for item in result["warnings"])


def test_new_provider_and_execution_commands_are_exposed():
    from marketcouncil.cli import build_parser
    parser = build_parser()
    assert parser.parse_args(["quote", "--provider", "binance", "--asset-class", "crypto", "--symbol", "BTCUSDT"]).command == "quote"
    assert parser.parse_args(["alpaca-paper-limit", "--symbol", "AAPL", "--side", "buy", "--quantity", "1", "--limit-price", "100"]).command == "alpaca-paper-limit"
    assert parser.parse_args(["binance-testnet-limit", "--symbol", "BTCUSDT", "--side", "BUY", "--quantity", "0.1", "--price", "50000"]).command == "binance-testnet-limit"


def test_stream_cli_parser_accepts_twelvedata_symbols():
    from marketcouncil.cli import build_parser

    args = build_parser().parse_args([
        "stream", "--provider", "twelvedata", "--asset-class", "fx",
        "--symbols", "EUR/USD", "USD/JPY", "--max-events", "10",
    ])
    assert args.command == "stream"
    assert args.symbols == ["EUR/USD", "USD/JPY"]
    assert args.max_events == 10
