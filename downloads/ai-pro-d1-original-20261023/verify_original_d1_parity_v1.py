#!/usr/bin/env python3
"""Read-only exact D1 parity gate: runs the original 91-source ZIP, no native SDK."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import zipfile

HERE=Path(__file__).resolve().parent
BUNDLE=HERE/"TAC_original_91_sources_verified_for_AIPro_20261023.zip"
VECTORS=HERE/"TAC_D1_original_exact_parity_vectors_synthetic_v1.json"
ORIGINAL="strategy_rc1/d1_data_math/canonical.py"
EXPECTED_SHA="a647c3f66448dbf1cb322fd7561fdc74d3584ce2c5ef1c7450dd63837ef75b62"

def require(ok,reason):
    if not ok: raise RuntimeError(reason)

def fraction_pair(value):
    if value is None: return None
    return {"numerator":value.numerator,"denominator":value.denominator}

def serialize(result):
    return {
        "information_cutoff":result.information_cutoff,
        "identical_duplicates_deduplicated":result.identical_duplicates_deduplicated,
        "records":[{
            "symbol":r.bar.symbol,"open_time":r.bar.open_time,
            "close_time":r.bar.close_time,
            "canonical_segment_id":r.canonical_segment_id,
            **{key:fraction_pair(getattr(r.bar,key)) for key in
                ("open","high","low","close","base_volume","quote_volume")}
        } for r in result.records],
        "issues":[{"code":i.code,"severity":i.severity.value,
                   "detail":i.detail,"open_time":i.open_time}
                  for i in result.issues]
    }

def run():
    require(BUNDLE.is_file() and VECTORS.is_file(),"PUBLIC_DOWNLOAD_FILES_NOT_PRESENT")
    with zipfile.ZipFile(BUNDLE) as z:
        names=z.namelist()
        require(len([x for x in names if x.startswith("strategy_rc1/")
                     and x.endswith(".py")])==91,"ORIGINAL_MEMBER_COUNT_NOT_91")
        require(hashlib.sha256(z.read(ORIGINAL)).hexdigest()==EXPECTED_SHA,
                "ORIGINAL_CANONICAL_SHA256_MISMATCH")
    data=json.loads(VECTORS.read_text(encoding="utf-8"))
    require(data["reference_sha256"]==EXPECTED_SHA and data["is_synthetic"] is True,
            "VECTOR_SOURCE_OR_SYNTHETIC_IDENTITY_DRIFT")
    sys.path.insert(0,str(BUNDLE))
    try:
        from strategy_rc1.d1_data_math.canonical import CanonicalBar,canonicalize_15m
        from strategy_rc1.runtime_guards.continuity_guard import DataIntegrityBlock

        def evaluate(bars):
            return canonicalize_15m([CanonicalBar.from_values(**bar) for bar in bars])

        templates=data["bar_templates"]
        for case in data["positive_cases"]:
            selected=[dict(templates[i]) for i in case["bar_template_indices"]]
            actual=serialize(evaluate(selected))
            require(actual==case["expected"],"POSITIVE_PARITY_FAIL:"+case["name"])
        for case in data["negative_cases"]:
            selected=[dict(templates[i]) for i in case["bar_template_indices"]]
            mutation=case["mutation"]
            index=mutation.get("index",0)
            value=mutation["value"]
            if mutation["type"]=="float":
                value=float(value)  # deliberately invalid input for negative test only
            selected[index][mutation["field"]]=value
            try:
                evaluate(selected)
            except (TypeError,DataIntegrityBlock) as exc:
                require(type(exc).__name__==case["expected_exception"],
                        "NEGATIVE_WRONG_EXCEPTION:"+case["name"])
                require(case["expected_message_contains"] in str(exc),
                        "NEGATIVE_WRONG_ERROR_TEXT:"+case["name"])
            else:
                raise RuntimeError("NEGATIVE_PARITY_FAIL:"+case["name"])
        print(json.dumps({
            "source":"EXACT_FROZEN_91_SOURCE_PYTHON_IMPORT",
            "status":"D1_ORIGINAL_EXACT_PARITY_PASS",
            "positive_cases":len(data["positive_cases"]),
            "negative_cases":len(data["negative_cases"]),
            "native_ai_pro_runtime_equivalence":False,
            "accounts_read":False,"orders":0,
            "TAC_LIVE_ENABLED":0,
        },ensure_ascii=False,sort_keys=True))
    finally:
        sys.path.pop(0)

if __name__=="__main__":
    run()
