"""Emit exact scientific AST for frozen B4 producer into one native module.

The source D2-B4 producer is publicly hash-pinned and mechanically flattened.
Imported symbols from strategy_rc1 already exist in the 243k original TAC
core; never replace them. MappingProxyType uses Python's identical builtin
read-only-mapping class because AI Pro blocked the types import previously.
Remove a single identical 15m observer constant already defined in B3.
This does NOT bind B4 to the real D3 cutoff loop or grant execution.
"""
from __future__ import annotations

import ast
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ORIGINAL=HERE.parent/"frozen_evidence_producers_v1"/"d2_to_b4_d4_causal_evidence_producers_v1.py"
B3=HERE/"RUNTIME_B3_FROZEN_ORIGINAL_PRODUCER_APPEND_V1.py"
BASIS=HERE/"strategy/strategy.py"
OUT=HERE/"B4_FROZEN_ORIGINAL_PRODUCER_APPEND_V1.py"
MANIFEST=HERE/"B4_FROZEN_ORIGINAL_PRODUCER_APPEND_V1.manifest.json"
FROZEN_SHA256="acdb9f7dcac5e4dee2cf012951c8c8eff51f59dcb9811304e833666bb0d8cdd3"

def names(tree):
    out=set()
    for item in tree.body:
        if isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            out.add(item.name)
        elif isinstance(item,ast.Assign):
            for t in item.targets:
                if isinstance(t,ast.Name): out.add(t.id)
    return out

def frozen_int_expression(node):
    # Permit only frozen integer constants and exact multiplication.
    if isinstance(node,ast.Constant) and type(node.value) is int:
        return node.value
    if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Mult):
        return frozen_int_expression(node.left)*frozen_int_expression(node.right)
    raise ValueError("B4_UNSUPPORTED_OBSERVER_CONSTANT_EXPRESSION")

def flatten_source():
    raw=ORIGINAL.read_bytes()
    if sha256(raw).hexdigest()!=FROZEN_SHA256:
        raise ValueError("B4_FROZEN_SOURCE_SHA256_MISMATCH")
    original=ast.parse(raw.decode())
    basis=ast.parse(BASIS.read_text()+"\n"+B3.read_text())
    b3=ast.parse(B3.read_text())
    if ("OBSERVER_TIMEFRAME_MS" not in names(b3)
        or "OBSERVER_TIMEFRAME_MS" in names(ast.parse(BASIS.read_text()))):
        raise ValueError("B4_EXPECTED_ORIGINAL_B3_OBSERVER_CONSTANT_MISSING")
    blocks=[]
    removed=[]
    for node in original.body:
        if isinstance(node,ast.ImportFrom) and node.module=="__future__":
            removed.append("future annotations")
            continue
        if isinstance(node,ast.ImportFrom) and node.module and node.module.startswith("strategy_rc1"):
            for alias in node.names:
                if alias.name not in names(basis):
                    raise ValueError("B4_ORIGINAL_TYPE_OR_FUNCTION_MISSING:"+alias.name)
            removed.append("strategy_rc1."+node.module)
            continue
        if isinstance(node,ast.ImportFrom) and node.module=="types":
            if len(node.names)!=1 or node.names[0].name!="MappingProxyType":
                raise ValueError("B4_UNEXPECTED_TYPES_IMPORT")
            blocks.append(ast.parse("MappingProxyType = type(type.__dict__)").body[0])
            removed.append("types.MappingProxyType = identical_builtin_type")
            continue
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="OBSERVER_TIMEFRAME_MS" for t in node.targets):
            if frozen_int_expression(node.value)!=900000:
                raise ValueError("B4_OBSERVER_15M_CONSTANT_CHANGED")
            b3constant=next(n for n in b3.body
                if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="OBSERVER_TIMEFRAME_MS" for t in n.targets))
            if frozen_int_expression(b3constant.value)!=900000:
                raise ValueError("ORIGINAL_B3_OBSERVER_MISMATCH")
            removed.append("duplicate frozen OBSERVER_TIMEFRAME_MS=900000")
            continue
        if isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
            continue
        blocks.append(node)
    combined=ast.Module(body=blocks,type_ignores=[])
    overlaps=names(combined)&names(basis)
    if overlaps:
        raise ValueError("ORIGINAL_B4_SYMBOL_COLLISION:"+str(sorted(overlaps)))
    for kind in (ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef):
        expected={
            node.name:ast.dump(node,include_attributes=False)
            for node in original.body if isinstance(node,kind)}
        observed={
            node.name:ast.dump(node,include_attributes=False)
            for node in combined.body if isinstance(node,kind)}
        if expected!=observed:
            raise ValueError("B4_SCIENTIFIC_DEFINITION_AST_CHANGED:"+kind.__name__)
    original_code=BASIS.read_text()+"\n"+B3.read_text()
    adapter=ast.unparse(combined)+"\n"
    compile(original_code+"\n"+adapter,"tac_original_b4_unified.py","exec")
    return adapter,raw,removed

def main():
    adapter,original,removed=flatten_source()
    OUT.write_text(adapter)
    m={
        "schema":"TAC_FROZEN_D2_TO_B4_ORIGINAL_PRODUCER_SINGLE_SOURCE_V1",
        "source":"provisional_shadow_v1/d2_to_b4_d4_causal_evidence_producers_v1.py",
        "source_sha256":sha256(original).hexdigest(),
        "appended_sha256":sha256(adapter.encode()).hexdigest(),
        "original_definitions_ast_unchanged":True,
        "imports_or_duplicate_constant_normalized":removed,
        "appended_chars":len(adapter),
        "original_d1d2d3d4d5d6_f9_definitions_preserved":True,
        "runtime_b3_original_definitions_preserved":True,
        "B4_native_node_connected":False,
        "B4_true_evidence_eligible_to_trade":False,
        "QBU_B5_D4_F9_D5_UPDATE014_D6_native_connected":False,
        "TAC_LIVE_ENABLED":0,
        "orders":0
    }
    MANIFEST.write_text(json.dumps(m,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print("B4_FROZEN_SINGLE_MODULE_AST_VERIFIED",json.dumps(m,sort_keys=True))

if __name__=="__main__":
    main()
