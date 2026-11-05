"""Safely append frozen namespaced QBU/B5 original source to real Binance.

Pin the newest *user-reported* native source SHA. No modification if actual
workspace diverges. AST changes forbidden to existing D1-D6/F9/B3/B4 logic.
This installs original QBU/B5 definitions + nontrading synthetic adapter;
it does NOT itself wire the currently running D3 custom node cutoff loop.
"""
from __future__ import annotations
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path

EXPECTED_CURRENT_SHA256="b272cfaba80bc1535ba45a30602ad0e813d26de992128022be769634a1ff3b1f"
EXPECTED_QBU_SINGLEFILE_SHA256="9d1ae768305555a39958586d519d535098bc3e1c247a1cbe850d72c490dc10c1"

def digest(b):
    return sha256(b).hexdigest()

def definitions(tree):
    return {n.name for n in tree.body
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))}

def prepare(src:Path,frozen:Path,bridge:Path,expected=EXPECTED_CURRENT_SHA256):
    data=src.read_bytes()
    if digest(data)!=expected:
        raise ValueError("NATIVE_CURRENT_SOURCE_SHA_MISMATCH_ABORT_NO_WRITE:"+digest(data))
    append=frozen.read_bytes()
    if digest(append)!=EXPECTED_QBU_SINGLEFILE_SHA256:
        raise ValueError("FROZEN_QBU_B5_SOURCE_SHA256_MISMATCH_NO_WRITE")
    adapter=bridge.read_bytes()
    before=ast.parse(data.decode("utf8"))
    frozen_ast=ast.parse(append.decode("utf8"))
    bridge_ast=ast.parse(adapter.decode("utf8"))
    must_preexist={
        "RuntimeB3PriceDrivenReturnProducerV1",
        "_tac_frozen_b3_update007_step",
        "produce_structural_acceptance",
        "produce_correct_side_recovery",
        "D3ReferenceSkeleton",
        "D2ReferenceSkeleton"}
    current=definitions(before)
    if not must_preexist.issubset(current):
        raise ValueError("CURRENT_ORIGINAL_B3_B4_SCIENCE_MISSING:"+
                         repr(sorted(must_preexist-current)))
    must_add={
        "TAC_BASE_produce_update008",
        "TAC_ID_project_negotiation_identity",
        "TAC_PR_project_qbu_progress_evidence",
        "TAC_ID_bind_update008_request",
        "TAC_PR_bind_update008_request"}
    fq=definitions(frozen_ast)
    if not must_add.issubset(fq):
        raise ValueError("FROZEN_QBU_ORIGINAL_SOURCE_DEFINITION_MISSING")
    if "_tac_original_qbu_b5_synthetic_cutoff_v1" not in definitions(bridge_ast):
        raise ValueError("QBU_REAL_EPOCH_GUARD_AND_BRIDGE_MISSING")
    coll=(current&fq)|(current&definitions(bridge_ast))|(fq&definitions(bridge_ast))
    if coll:
        raise ValueError("FROZEN_QBU_B5_FUNCTION_COLLISION:"+repr(sorted(coll)))
    combined=(data+b"\n# --- FROZEN ORIGINAL NAMESPACED QBU / B5 ---\n"+
              append+b"\n# --- TEST_ONLY QBU CUTOFF BRIDGE ---\n"+adapter+b"\n")
    after=ast.parse(combined.decode("utf8"))
    original=[ast.dump(n,include_attributes=False) for n in before.body]
    updated=[ast.dump(n,include_attributes=False) for n in after.body[:len(before.body)]]
    if original!=updated:
        raise ValueError("EXISTING_NATIVE_D1_D6_B3_B4_AST_CHANGED")
    compile(combined,str(src),"exec")
    return combined,{
        "source_before_sha256":digest(data),
        "source_after_sha256":digest(combined),
        "frozen_QBU_B5_source_sha256":digest(append),
        "frozen_original_QBU_B5_producer_definitions_installed":True,
        "scientific_prior_AST_unchanged":True,
        "QBU_B5_native_D3_cutoff_bound":False,
        "QBU_positive_synthetic_tests_available":True,
        "real_market_epoch_coverage_proven":False,
        "native_binance_validate_after_write":False,
        "native_binance_saved":False,"native_binance_running":False,
        "TAC_LIVE_ENABLED":0,"orders":0}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--strategy",default="strategy/strategy.py")
    p.add_argument("--frozen-qbu",required=True)
    p.add_argument("--qbu-bridge",required=True)
    p.add_argument("--commit",action="store_true")
    args=p.parse_args()
    current=Path(args.strategy)
    merged,record=prepare(current,Path(args.frozen_qbu),Path(args.qbu_bridge))
    if args.commit:
        backup=current.with_suffix(".py.pre_qbu_b5_original")
        if backup.exists():
            raise ValueError("EXISTING_QBU_BACKUP_REFUSE_OVERWRITE")
        backup.write_bytes(current.read_bytes())
        current.write_bytes(merged)
        record["source_written"]=True
    else:
        record["source_written"]=False
    print(json.dumps(record,sort_keys=True,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
