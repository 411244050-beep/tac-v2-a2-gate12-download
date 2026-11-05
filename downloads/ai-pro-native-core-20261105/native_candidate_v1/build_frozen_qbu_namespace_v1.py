"""Statically flatten frozen QBU and B5/D4 base producers without symbol collisions.

No new signal rules. Preserve original branch logic, AST source identities,
and freeze semantic IDs. Every module gets an unambiguous prefix; the
original `runtime.X` references are resolved mechanically to the prefixed
authoritative base X. This build is NOT native Binance validation or cutoff
binding. A full output differential is required before native use.
"""
from __future__ import annotations
import ast
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/"frozen_evidence_producers_v1"
BASE=HERE/"strategy/strategy.py"
B3=HERE/"RUNTIME_B3_FROZEN_ORIGINAL_PRODUCER_APPEND_V1.py"
B4=HERE/"B4_FROZEN_ORIGINAL_PRODUCER_APPEND_V1.py"
OUT=HERE/"QBU_B5_FROZEN_NAMESPACED_ORIGINAL_APPEND_V1.py"
MANIFEST=HERE/"QBU_B5_FROZEN_NAMESPACED_ORIGINAL_APPEND_V1.manifest.json"
SPEC=(
    ("authoritative_d3_b5_d4_base_runtime_producers_v1.py","TAC_BASE_",
        "6dd33000694a2f41713c9474070b6946ad23c622018bcf03fccd9d385e28cecd"),
    ("qbu_same_event_negotiation_identity_production_binding_v1.py","TAC_ID_",
        "a8510ff4f17001afe97072c8829288d5a7ba1ca20f8a60c152b1425994c780f8"),
    ("qbu_material_trend_side_minor_progress_production_binding_v1.py","TAC_PR_",
        "b63a3c24fc7111d21e9e00bc55efcdd76c41a4b8d78b4290a1b314159059c4b5"),
)

def top_names(t):
    out=set()
    for n in t.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            out.add(n.name)
        elif isinstance(n,(ast.Assign,ast.AnnAssign)):
            tgts=n.targets if isinstance(n,ast.Assign) else [n.target]
            for target in tgts:
                for x in ast.walk(target):
                    if isinstance(x,ast.Name): out.add(x.id)
    return out

class RenameModuleLocals(ast.NodeTransformer):
    def __init__(self,own_map,externals):
        self.own_map=own_map
        self.externals=externals
    def visit_Name(self,node):
        if node.id in self.own_map:
            node.id=self.own_map[node.id]
        return node
    def visit_FunctionDef(self,node):
        if node.name in self.own_map: node.name=self.own_map[node.name]
        return self.generic_visit(node)
    def visit_AsyncFunctionDef(self,node):
        if node.name in self.own_map: node.name=self.own_map[node.name]
        return self.generic_visit(node)
    def visit_ClassDef(self,node):
        if node.name in self.own_map: node.name=self.own_map[node.name]
        return self.generic_visit(node)
    def visit_Attribute(self,node):
        if (isinstance(node.value,ast.Name) and
            node.value.id=="runtime"):
            if node.attr not in self.externals:
                raise ValueError("UNRESOLVED_FROZEN_QBU_RUNTIME_ATTRIBUTE:"+node.attr)
            return ast.copy_location(ast.Name(
                id=self.externals[node.attr],ctx=ast.Load()),node)
        return self.generic_visit(node)

def original_source_ast(tree):
    return [n for n in tree.body if isinstance(n,
            (ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))]

def rewrite(module_name,prefix,bytes_data,available,base_global):
    t=ast.parse(bytes_data.decode("utf8"))
    own=top_names(t)
    mapping={x:prefix+x for x in own}
    # External B5 module symbols: anything B5 defines or B4 imports.
    ext={"EvidenceState":"EvidenceState"}
    ext.update({"MappingProxyType":"MappingProxyType"})
    ext.update(base_global)
    if prefix=="TAC_BASE_":
        ext={}
    body=[]
    adjustments=[]
    for n in t.body:
        if isinstance(n,ast.ImportFrom) and n.module=="__future__":
            adjustments.append("future annotations already present")
            continue
        if isinstance(n,ast.ImportFrom) and (
                n.module=="types" or n.module=="d2_to_b4_d4_causal_evidence_producers_v1"
                or (n.module or "").startswith("strategy_rc1")):
            if n.module=="types":
                if {x.name for x in n.names}!={"MappingProxyType"}:
                    raise ValueError("MAPPINGPROXY_UNEXPECTED_SOURCE_IMPORT")
            else:
                for alias in n.names:
                    if alias.name not in available:
                        raise ValueError("FROZEN_QBU_SCIENCE_DEPENDENCY_MISSING:"+
                                         module_name+":"+alias.name)
            adjustments.append("preexisting original source import "+str(n.module))
            continue
        if isinstance(n,ast.Import) and any(
                x.name=="authoritative_d3_b5_d4_base_runtime_producers_v1" for x in n.names):
            if len(n.names)!=1 or n.names[0].asname!="runtime":
                raise ValueError("FROZEN_QBU_RUNTIME_ALIAS_UNKNOWN")
            adjustments.append("runtime global to exact source prefix")
            continue
        if (isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant)
            and isinstance(n.value.value,str)):
            adjustments.append("inert original module docstring")
            continue
        if isinstance(n,ast.ImportFrom) and n.module=="types":
            raise ValueError("MAPPINGPROXY_MODULE_DEPENDENCY")
        body.append(n)
    prepared=ast.Module(body=body,type_ignores=[])
    renamer=RenameModuleLocals(mapping,ext)
    adjusted=renamer.visit(prepared)
    ast.fix_missing_locations(adjusted)
    # Strict rules safety: source class/function tree must be isomorphic
    # to namespace-transformed original AST. Transforming names only is
    # permitted; no branch, compare, op, call arguments or defaults removed.
    sci=original_source_ast(ast.parse(bytes_data.decode("utf8")))
    after=original_source_ast(adjusted)
    if len(sci)!=len(after):
        raise ValueError("SCIENCE_DEFINITION_COUNT_CHANGED:"+module_name)
    for raw,transformed in zip(sci,after):
        expect=RenameModuleLocals(mapping,ext).visit(
            ast.fix_missing_locations(ast.Module(body=[raw],type_ignores=[])))
        if ast.dump(expect.body[0],include_attributes=False)!=ast.dump(transformed,include_attributes=False):
            raise ValueError("FROZEN_SCIENCE_BODY_AST_CHANGED:"+module_name+":"+raw.name)
    return ast.unparse(adjusted)+"\n",mapping,adjustments,len(sci)

def build():
    already=BASE.read_text()+"\n"+B3.read_text()+"\n"+B4.read_text()
    defined=top_names(ast.parse(already))
    chunks=[]
    report=[]
    exported={}
    for filename,prefix,want in SPEC:
        raw=(SOURCE/filename).read_bytes()
        if sha256(raw).hexdigest()!=want:
            raise ValueError("PUBLIC_FROZEN_PRODUCER_SOURCE_SHA_DRIFT:"+filename)
        ext={}
        if prefix!="TAC_BASE_":
            ext=dict(exported["TAC_BASE_"])
            ext["EvidenceState"]="EvidenceState"
        out,names,removed,scientific_defs=rewrite(filename,prefix,raw,
            defined|set(exported.get("TAC_BASE_",{})),ext)
        clash=set(names.values())&defined
        if clash:
            raise ValueError("PREFIXED_GLOBAL_COLLISION:"+repr(sorted(clash)))
        defined.update(names.values())
        chunks.append("# --- EXACT SCIENCE NAMESPACE "+prefix+" ---\n"+out)
        exported[prefix]=names
        report.append({
            "frozen_original_filename":filename,
            "original_sha256":want,
            "namespace":prefix,
            "rewritten_original_definition_AST_equivalent":True,
            "scientific_definitions_preserved":scientific_defs,
            "scientific_symbols_preserved":len(names),
            "removed_only_imports_or_inert_docstrings":removed,
            "appended_chars":len(out)
        })
    code="\n".join(chunks)
    compile(already+"\n"+code,"tac_frozen_qbu_static_namespaced.py","exec")
    return code,report

def main():
    code,report=build()
    OUT.write_text(code,encoding="utf8")
    m={
        "schema":"TAC_FROZEN_QBU_B5_STATIC_NAMESPACED_ORIGINAL_SOURCE_V1",
        "modules":report,
        "code_sha256":sha256(code.encode()).hexdigest(),
        "code_chars":len(code),
        "science_AST_mapping_only":True,
        "native_binance_validated":False,
        "QBU_B5_native_cutoff_bound":False,
        "D4_F9_D5_UPDATE014_D6_native_cutoff_bound":False,
        "TAC_LIVE_ENABLED":0,
        "orders":0
    }
    MANIFEST.write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
    print("TAC_FROZEN_QBU_B5_NAMESPACED_BUILD_PASS",json.dumps(m,sort_keys=True))
if __name__=="__main__":
    main()
