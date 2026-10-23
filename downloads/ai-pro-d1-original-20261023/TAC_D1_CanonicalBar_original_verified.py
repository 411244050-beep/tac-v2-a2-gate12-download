from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import Iterable

from ..ids import deterministic_id
from ..result_types import IntegrityIssue, IntegritySeverity
from ..runtime_guards.continuity_guard import DataIntegrityBlock

TF_15M_MS = 15 * 60 * 1000


def parse_exact_number(value: str | int | Decimal | Fraction) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        raise TypeError("bool is not a valid market number")
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, Decimal):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(Decimal(value))
    if isinstance(value, float):
        raise TypeError("float market inputs are forbidden; provide exact decimal string/int/Decimal/Fraction")
    raise TypeError(f"Unsupported market number type: {type(value)!r}")


@dataclass(frozen=True)
class CanonicalBar:
    symbol: str
    open_time: int
    close_time: int
    open: Fraction
    high: Fraction
    low: Fraction
    close: Fraction
    base_volume: Fraction | None = None
    quote_volume: Fraction | None = None
    is_closed: bool = True

    @classmethod
    def from_values(
        cls,
        *,
        symbol: str,
        open_time: int,
        close_time: int,
        open: str | int | Decimal | Fraction,
        high: str | int | Decimal | Fraction,
        low: str | int | Decimal | Fraction,
        close: str | int | Decimal | Fraction,
        base_volume: str | int | Decimal | Fraction | None = None,
        quote_volume: str | int | Decimal | Fraction | None = None,
        is_closed: bool = True,
    ) -> "CanonicalBar":
        return cls(
            symbol=symbol,
            open_time=open_time,
            close_time=close_time,
            open=parse_exact_number(open),
            high=parse_exact_number(high),
            low=parse_exact_number(low),
            close=parse_exact_number(close),
            base_volume=None if base_volume is None else parse_exact_number(base_volume),
            quote_volume=None if quote_volume is None else parse_exact_number(quote_volume),
            is_closed=is_closed,
        )


@dataclass(frozen=True)
class CanonicalRecord:
    bar: CanonicalBar
    canonical_segment_id: str


@dataclass(frozen=True)
class CanonicalizationResult:
    records: tuple[CanonicalRecord, ...]
    issues: tuple[IntegrityIssue, ...]
    identical_duplicates_deduplicated: int

    @property
    def information_cutoff(self) -> int | None:
        return self.records[-1].bar.close_time if self.records else None


def _validate_bar(bar: CanonicalBar) -> None:
    if not bar.symbol:
        raise DataIntegrityBlock("EMPTY_SYMBOL")
    if not bar.is_closed:
        raise DataIntegrityBlock(f"OPEN_BAR_FORBIDDEN open_time={bar.open_time}")
    if bar.open_time % TF_15M_MS != 0:
        raise DataIntegrityBlock(f"OPEN_TIME_NOT_15M_ALIGNED open_time={bar.open_time}")
    if bar.close_time <= bar.open_time:
        raise DataIntegrityBlock(f"IMPOSSIBLE_CLOSE_TIME open_time={bar.open_time} close_time={bar.close_time}")
    if bar.high < max(bar.open, bar.close, bar.low):
        raise DataIntegrityBlock(f"INVALID_HIGH open_time={bar.open_time}")
    if bar.low > min(bar.open, bar.close, bar.high):
        raise DataIntegrityBlock(f"INVALID_LOW open_time={bar.open_time}")
    if bar.base_volume is not None and bar.base_volume < 0:
        raise DataIntegrityBlock(f"NEGATIVE_BASE_VOLUME open_time={bar.open_time}")
    if bar.quote_volume is not None and bar.quote_volume < 0:
        raise DataIntegrityBlock(f"NEGATIVE_QUOTE_VOLUME open_time={bar.open_time}")


def canonicalize_15m(bars: Iterable[CanonicalBar]) -> CanonicalizationResult:
    ordered = sorted(bars, key=lambda b: (b.open_time, b.close_time))
    if not ordered:
        return CanonicalizationResult((), (), 0)

    by_open: dict[int, CanonicalBar] = {}
    dedup = 0
    for bar in ordered:
        _validate_bar(bar)
        prior = by_open.get(bar.open_time)
        if prior is None:
            by_open[bar.open_time] = bar
        elif prior == bar:
            dedup += 1
        else:
            raise DataIntegrityBlock(f"CONFLICTING_DUPLICATE open_time={bar.open_time}")

    unique = [by_open[k] for k in sorted(by_open)]
    symbols = {b.symbol for b in unique}
    if len(symbols) != 1:
        raise DataIntegrityBlock("MIXED_SYMBOL_INPUT")
    symbol = unique[0].symbol

    records: list[CanonicalRecord] = []
    issues: list[IntegrityIssue] = []
    segment_id: str | None = None
    prev_open: int | None = None

    for bar in unique:
        if prev_open is None or bar.open_time - prev_open != TF_15M_MS:
            if prev_open is not None:
                delta = bar.open_time - prev_open
                if delta <= 0:
                    raise DataIntegrityBlock("NON_MONOTONIC_OPEN_TIME")
                issues.append(
                    IntegrityIssue(
                        code="DATA_GAP_NEW_CANONICAL_SEGMENT",
                        severity=IntegritySeverity.BLOCK,
                        detail=f"gap_ms={delta - TF_15M_MS}; no forward fill; recursive state must reset",
                        open_time=bar.open_time,
                    )
                )
            segment_id = deterministic_id("canonical_segment", symbol, bar.open_time)
        records.append(CanonicalRecord(bar=bar, canonical_segment_id=segment_id))  # type: ignore[arg-type]
        prev_open = bar.open_time

    return CanonicalizationResult(tuple(records), tuple(issues), dedup)
