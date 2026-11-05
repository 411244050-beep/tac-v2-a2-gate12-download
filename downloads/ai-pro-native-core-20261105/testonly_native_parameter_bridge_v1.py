"""Binance AI Pro TAC original-rule TEST_ONLY parameter bridge, not a strategy.

The original D2 parser requires FROZEN in the official ParameterSnapshot.
These three theta values are NOT scientifically frozen; DO NOT patch slots,
invent a FROZEN state, or claim complete strategy/entry readiness.

Instead inject exact rational computation values through D2's *unchanged*
structural_params constructor, retaining a separate provenance-only record.
This bridge deliberately does NOT alter the original D5/D6 governance guard.
A hypothetical theta_stop readout remains non-executable and is never
supplied as a D5 InitialHardStopCandidate, trade/order or ENTRY_READY.
No environment vars, network calls, account credentials or order APIs.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Mapping

TAC_LIVE_ENABLED=0
TEST_ONLY_AUTHORISATION="USER_TEST_ONLY_NONTRADING_NOV_2026"
EXPERIMENTAL_SOURCE_PATH="work/live/experimental_operational_parameter_snapshot_v1.json"
EXPERIMENTAL_SOURCE_GIT_BLOB_SHA1="b4b00da2ce26b97f160deabfb34b3d15d9d91a12"
EXPERIMENTAL_SOURCE_THETA_ORIGIN="LATEST_LOCAL_REFINEMENT_RANK1_TRAIN_OBSERVATION_NOT_SELECTED_OR_FROZEN"
THETA_STRINGS={
    "theta_minor":"0.655417496698647720797643159793938746032740795679425",
    "theta_intermediate":"1.7477799911963939221270484261171699894206421218118",
    "theta_major":"3.4955599823927878442540968522343399788412842436236",
    "theta_stop":"1.0",
}
STRUCTURAL=("theta_minor","theta_intermediate","theta_major")


class TestOnlyParameterBlock(ValueError):
    pass


def exact(raw: str)->Fraction:
    """No float conversion or rounding of research-provenance values."""
    if type(raw) is not str:
        raise TestOnlyParameterBlock("EXACT_PARAMETER_DECIMAL_STRING_REQUIRED")
    try:
        d=Decimal(raw)
        if not d.is_finite():
            raise ValueError("not finite")
        return Fraction(d)
    except (InvalidOperation,ValueError,ZeroDivisionError) as exc:
        raise TestOnlyParameterBlock("INVALID_EXACT_PARAMETER") from exc


@dataclass(frozen=True)
class TestOnlyParameterEvidence:
    authorization: str
    source_path: str
    source_blob_sha1: str
    original_snapshot_id: str
    original_structural_slot_states: tuple[tuple[str,str],...]
    original_stop_slot_state: str
    original_runtime_usable: bool
    source_identity_sha256: str
    numeric_theta_stop_test_only: Fraction
    synthetic_mode_only: bool=True
    scientific_frozen: bool=False
    executable: bool=False
    orders_authorized: bool=False
    native_runtime_validated: bool=False


def _assert_original_source_state(core:Any,snapshot:Any)->None:
    if snapshot.complete_strategy_parameter_snapshot or snapshot.runtime_usable:
        raise TestOnlyParameterBlock("OFFICIAL_SNAPSHOT_MUST_REMAIN_NOT_USABLE")
    for name in STRUCTURAL:
        slot=snapshot.slot(name)
        if slot.state is not core.ParameterState.OPEN or slot.exact_value is not None:
            raise TestOnlyParameterBlock("ORIGINAL_STRUCTURAL_SLOT_MODIFIED:"+name)
    stop=snapshot.slot("theta_stop")
    if stop.state is not core.ParameterState.LOCKED or stop.exact_value is not None:
        raise TestOnlyParameterBlock("ORIGINAL_STOP_SLOT_NOT_LOCKED")


def build_testonly_d2(core:Any,*,symbol:str,authorized:bool)->tuple[Any,TestOnlyParameterEvidence]:
    """Construct original D2 EXACTLY, bypassing only FROZEN gate *in test mode*.

    The frozen scientific D2 parameters still come from original FROZEN slots.
    All D2 pivot/trend/leg algorithms are the unmodified source version.
    """
    if authorized is not True or TAC_LIVE_ENABLED!=0:
        raise TestOnlyParameterBlock("EXPLICIT_NONTRADING_TEST_ONLY_AUTH_REQUIRED")
    if type(symbol) is not str or not symbol or symbol!=symbol.strip():
        raise TestOnlyParameterBlock("SYMBOL_INVALID")
    snapshot=core.current_partial_parameter_snapshot()
    _assert_original_source_state(core,snapshot)
    values=tuple(exact(THETA_STRINGS[name]) for name in STRUCTURAL)
    # Original source type validates 0<minor<intermediate<major.
    structural=core.StructuralScaleParameters(*values)
    frozen=core.frozen_d2_parameters(snapshot)
    instance=core.D2ReferenceSkeleton(
        symbol=symbol,structural_params=structural,frozen_params=frozen)
    provenance={
        "auth":TEST_ONLY_AUTHORISATION,
        "mode":"TEST_ONLY_FROZEN_SCIENCE_INCOMPLETE",
        "source_path":EXPERIMENTAL_SOURCE_PATH,
        "source_git_blob_sha1":EXPERIMENTAL_SOURCE_GIT_BLOB_SHA1,
        "original_snapshot_id":snapshot.snapshot_id,
        "ordered_structural_strings":[THETA_STRINGS[name] for name in STRUCTURAL],
        "stop_string":THETA_STRINGS["theta_stop"],
        "original_slots":{name:snapshot.slot(name).state.value
                          for name in STRUCTURAL+("theta_stop",)},
    }
    token=sha256(json.dumps(provenance,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    evidence=TestOnlyParameterEvidence(
        authorization=TEST_ONLY_AUTHORISATION,source_path=EXPERIMENTAL_SOURCE_PATH,
        source_blob_sha1=EXPERIMENTAL_SOURCE_GIT_BLOB_SHA1,
        original_snapshot_id=snapshot.snapshot_id,
        original_structural_slot_states=tuple(
            (name,snapshot.slot(name).state.value) for name in STRUCTURAL),
        original_stop_slot_state=snapshot.slot("theta_stop").state.value,
        original_runtime_usable=snapshot.runtime_usable,
        source_identity_sha256=token,
        numeric_theta_stop_test_only=exact(THETA_STRINGS["theta_stop"]))
    # Neither snapshot nor class method from_parameter_snapshot is mutated.
    _assert_original_source_state(core,snapshot)
    if snapshot.slot("theta_minor").exact_value is not None:
        raise TestOnlyParameterBlock("UNAUTHORIZED_FROZEN_SNAPSHOT_MUTATION")
    return instance,evidence


def build_original_d3_with_official_frozen_slots(core:Any)->Any:
    """Original WP3 frozen theta values are authoritative, no TEST_ONLY override."""
    snapshot=core.current_partial_parameter_snapshot()
    _assert_original_source_state(core,snapshot)
    return core.D3ReferenceSkeleton.from_parameter_snapshot(snapshot)


def hypothetical_nonexecutable_stop(
    core:Any,*,provenance:TestOnlyParameterEvidence,
    risk_anchor_price:Fraction,atr_at_risk_reference:Fraction,
    direction:Any)->Mapping[str,Any]:
    """Scientific what-if output, NOT a D5 risk approval or hard-stop order.

    Actual original WP5 theta_stop stays LOCKED. This only evaluates the same
    symbolic formula in the explicit nontrading science engineering scope.
    """
    if TAC_LIVE_ENABLED!=0 or provenance.authorization!=TEST_ONLY_AUTHORISATION:
        raise TestOnlyParameterBlock("TEST_ONLY_PROVENANCE_REQUIRED")
    if provenance.executable or provenance.scientific_frozen:
        raise TestOnlyParameterBlock("EXECUTABLE_OR_FALSE_SCIENCE_PROVENANCE")
    for value in (risk_anchor_price,atr_at_risk_reference):
        if type(value) is not Fraction:
            raise TestOnlyParameterBlock("ORIGINAL_EXACT_RATIONAL_ONLY")
    if risk_anchor_price<=0 or atr_at_risk_reference<=0:
        raise TestOnlyParameterBlock("STOP_INPUTS_MUST_BE_POSITIVE")
    if direction is core.TrendDirection.LONG:
        candidate=risk_anchor_price-provenance.numeric_theta_stop_test_only*atr_at_risk_reference
    elif direction is core.TrendDirection.SHORT:
        candidate=risk_anchor_price+provenance.numeric_theta_stop_test_only*atr_at_risk_reference
    else:
        raise TestOnlyParameterBlock("UNKNOWN_DIRECTION")
    return {
        "status":"TEST_ONLY_HYPOTHETICAL_NONEXECUTABLE",
        "source_identity_sha256":provenance.source_identity_sha256,
        "stop_numerator":str(candidate.numerator),
        "stop_denominator":str(candidate.denominator),
        "original_d5_authority":"THETA_STOP_LOCKED_NO_AUTHORIZED_NUMERIC_VALUE",
        "official_d5_entry_ready_emitted":False,
        "scientific_frozen":False,
        "executability":False,"trade_authorized":False,
        "TAC_LIVE_ENABLED":0,"orders":0,
    }
