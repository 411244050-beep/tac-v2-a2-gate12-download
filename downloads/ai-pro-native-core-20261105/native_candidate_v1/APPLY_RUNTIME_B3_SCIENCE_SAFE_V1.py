"""Source-preserving producer install in the user's CURRENT Binance workspace.

Only append exact original frozen Runtime-B3 science and its tested bridge;
never rewrite the existing validated D3 multi-timeframe cutoff methods.
Do not count this install as D3 cutoff integration until the native node
actually calls _tac_frozen_b3_update007_step with verified epoch lineage.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path

BASELINE="ccd0a505729d0060d987f523ffa967d0c738586a4bf88019064177c8da012249"
PRODUCER_AST="d8dec00ab2d5d9c5723dd041b21ad95a1d83dcb244ee83a1558bd631607399cc"

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def declared(tree):
    result=set()
    for obj in tree.body:
        if isinstance(obj,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            result.add(obj.name)
    return result

def prepare(current, producer, bridge):
    source=current.read_bytes()
    if digest(source)!=BASELINE:
        raise ValueError("CURRENT_NATIVE_BASELINE_SHA_CHANGED_STOP_NO_WRITE:"+digest(source))
    b3=producer.read_bytes()
    adapter=bridge.read_bytes()
    bt=ast.parse(b3.decode("utf-8"))
    actual=hashlib.sha256(ast.dump(bt,include_attributes=False).encode()).hexdigest()
    if actual!=PRODUCER_AST:
        raise ValueError("FROZEN_ORIGINAL_B3_AST_SHA_MISMATCH")
    before=ast.parse(source.decode("utf-8"))
    adapt=ast.parse(adapter.decode("utf-8"))
    old=declared(before)
    new=declared(bt)|declared(adapt)
    if old & new:
        raise ValueError("ORIGINAL_SOURCE_TOPLEVEL_NAME_COLLISION:"+str(sorted(old&new)))
    if not {"RuntimeB3PriceDrivenReturnProducerV1"}.issubset(declared(bt)):
        raise ValueError("FROZEN_RUNTIME_B3_PRODUCER_MISSING")
    if not {"_tac_frozen_b3_update007_step"}.issubset(declared(adapt)):
        raise ValueError("ORIGINAL_D3_BRIDGE_MISSING")
    combined=source+b"\n\n# --- FROZEN RUNTIME-B3 ORIGINAL SCIENCE ---\n"+b3+b"\n\n# --- ORIGINAL UPDATE007/008 ADAPTER ---\n"+adapter+b"\n"
    after=ast.parse(combined.decode("utf-8"))
    original=[ast.dump(obj,include_attributes=False) for obj in before.body]
    following=[ast.dump(obj,include_attributes=False) for obj in after.body[:len(before.body)]]
    if original!=following:
        raise ValueError("EXISTING_SCIENTIFIC_OR_BINDING_AST_MODIFIED")
    compile(combined,str(current),"exec")
    return combined,{
        "original_strategy_sha256":digest(source),
        "new_strategy_sha256":digest(combined),
        "frozen_producer_ast_sha256":actual,
        "original_definitions_unchanged":True,
        "original_D3_multitf_loop_modified":False,
        "original_frozen_B3_producer_added":True,
        "B3_adapter_added":True,
        "real_native_cutoff_B3_called":False,
        "native_spec_validated_after_patch":False,
        "native_strategy_saved":False,
        "native_strategy_running":False,
        "TAC_LIVE_ENABLED":0,"orders":0,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--strategy",default="strategy/strategy.py")
    parser.add_argument("--producer",required=True)
    parser.add_argument("--bridge",required=True)
    parser.add_argument("--commit",action="store_true")
    args=parser.parse_args()
    strategy=Path(args.strategy)
    combined,receipt=prepare(strategy,Path(args.producer),Path(args.bridge))
    if args.commit:
        backup=strategy.with_suffix(".py.pre_b3_original")
        if backup.exists():
            raise ValueError("BACKUP_EXISTS_REFUSE_OVERWRITE")
        backup.write_bytes(strategy.read_bytes())
        strategy.write_bytes(combined)
        receipt["source_written"]=True
    else:
        receipt["source_written"]=False
    print(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2))

if __name__=="__main__":
    main()
