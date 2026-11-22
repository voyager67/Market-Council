"""Small typed data contracts used across the research pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Bar:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True, slots=True)
class MarketSnapshot:
    symbol: str
    timeframe: str
    bars_count: int
    latest_timestamp: str
    latest_close: float
    change_pct: float
    realised_volatility: float | None
    annualised_volatility: float | None
    bars_per_year: int | None
    data_warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AgentReport:
    role: str
    status: str
    stance: str
    confidence: int
    summary: str
    evidence: tuple[str, ...] = ()
    counter_evidence: tuple[str, ...] = ()
    missing_data: tuple[str, ...] = ()
    invalidation: tuple[str, ...] = ()
    model: str = "mock"
    error: str | None = None
    thesis: str | None = None
    bull_case: str | None = None
    bear_case: str | None = None
    key_risks: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        for key in ("evidence", "counter_evidence", "missing_data", "invalidation", "key_risks"):
            result[key] = list(result[key])
        return result


@dataclass(frozen=True, slots=True)
class CouncilReport:
    generated_at: str
    symbol: str
    question: str
    snapshot: MarketSnapshot
    stance: str
    confidence: int
    executive_summary: str
    thesis: str
    bull_case: str
    bear_case: str
    key_risks: tuple[str, ...]
    missing_data: tuple[str, ...]
    invalidation_conditions: tuple[str, ...]
    agents: tuple[AgentReport, ...]
    review_status: str = "HUMAN_REVIEW_REQUIRED"
    execution_authorization: str = "NONE"
    research_context_attached: bool = False
    research_context_sections: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "symbol": self.symbol,
            "question": self.question,
            "snapshot": self.snapshot.to_dict(),
            "stance": self.stance,
            "confidence": self.confidence,
            "executive_summary": self.executive_summary,
            "thesis": self.thesis,
            "bull_case": self.bull_case,
            "bear_case": self.bear_case,
            "key_risks": list(self.key_risks),
            "missing_data": list(self.missing_data),
            "invalidation_conditions": list(self.invalidation_conditions),
            "agents": [agent.to_dict() for agent in self.agents],
            "review_status": self.review_status,
            "execution_authorization": self.execution_authorization,
            "research_context_attached": self.research_context_attached,
            "research_context_sections": list(self.research_context_sections),
        }
