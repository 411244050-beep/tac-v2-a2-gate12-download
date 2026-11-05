"""Pin current Binance strategy.py, append frozen original B4 with zero science edits.

This installs original producer definitions only. It MUST NOT be reported as
D3->B4 cutoff binding until the actual D3 node invokes producer calls with
authoritative D2 minor pivots and original InteractionEvent lineage.
"""
from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path

PINNED_CURRENT_NATIVE_SHA256="db5b600c047b27c0be1ae821fd2d5b285a67aa50025ea6d57ba58ba1af2cbb69"
PINNED_FROZEN_B4_APPENDED_SHA256="88b588848bad8661078ac8e928b50e49060dcb0389a0104709442e4b151984ba"
PINNED_ORIGINAL_B4_SOURCE_SHA256="acdb9f7dcac5e4dee2cf012951c8c8eff51f59dcb9811304e833666bb0d8cdd3"

def h(bytes_):
    return sha256(bytes_).hexdigest()

def definitions(tree):
    return {
        node.name for node in tree.body
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))
    }

def prepare(current:Path,b4:Path,pinned=PINNED_CURRENT_NATIVE_SHA256):
    src=current.read_bytes()
    if h(src)!=pinned:
        raise ValueError("CURRENT_NATIVE_SOURCE_SHA_CHANGED_STOP_NO_WRITE:"+h(src))
    tail=b4.read_bytes()
    if h(tail)!=PINNED_FROZEN_B4_APPENDED_SHA256:
        raise ValueError("FROZEN_B4_APPENDED_SOURCE_SHA_MISMATCH")
    base=ast.parse(src.decode("utf-8"))
    new=ast.parse(tail.decode("utf-8"))
    if not {"RuntimeB3PriceDrivenReturnProducerV1",
            "_tac_frozen_b3_update007_step"}.issubset(definitions(base)):
        raise ValueError("EXISTING_B3_NATIVE_BINDING_MISSING")
    must={"produce_structural_acceptance","produce_correct_side_recovery",
          "produce_local_trend_control_regain","LineageContext",
          "StructuralAcceptanceRequest","CorrectSideRecoveryRequest"}
    if not must.issubset(definitions(new)):
        raise ValueError("FROZEN_B4_REQUIRED_SCIENTIFIC_DEFINITIONS_MISSING")
    collisions=definitions(base)&definitions(new)
    if collisions:
        raise ValueError("B4_SCIENTIFIC_DEFINITION_COLLISION:"+str(sorted(collisions)))
    combined=src+b"\n# --- FROZEN ORIGINAL D2 TO B4 PRODUCTION SOURCE ---\n"+tail+b"\n"
    checked=ast.parse(combined.decode("utf-8"))
    original_ast=[ast.dump(x,include_attributes=False) for x in base.body]
    after_ast=[ast.dump(x,include_attributes=False) for x in checked.body[:len(base.body)]]
    if original_ast!=after_ast:
        raise ValueError("ORIGINAL_NATIVE_SCIENCE_AST_DIFFERENCE")
    compile(combined,str(current),"exec")
    return combined,{
        "source_before_sha256":h(src),"source_after_sha256":h(combined),
        "frozen_B4_source_sha256":PINNED_ORIGINAL_B4_SOURCE_SHA256,
        "B4_producer_definitions_appended":True,
        "existing_original_science_AST_unchanged":True,
        "B4_bound_to_native_D3_cutoff":False,
        "B4_unknowns_fail_closed":True,
        "QBU_B5_D4_F9_D5_UPDATE014_D6":"NOT_CONNECTED",
        "native_strategy_saved":False,"native_strategy_running":False,
        "TAC_LIVE_ENABLED":0,"orders":0}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--strategy",default="strategy/strategy.py")
    parser.add_argument("--frozen-b4",required=True)
    parser.add_argument("--commit",action="store_true")
    args=parser.parse_args()
    current=Path(args.strategy)
    prepared,report=prepare(current,Path(args.frozen_b4))
    if args.commit:
        backup=current.with_suffix(".py.pre_b4_original")
        if backup.exists():
            raise ValueError("PRE_B4_BACKUP_EXISTS_STOP")
        backup.write_bytes(current.read_bytes())
        current.write_bytes(prepared)
        report["source_written"]=True
    else:
        report["source_written"]=False
    print(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
