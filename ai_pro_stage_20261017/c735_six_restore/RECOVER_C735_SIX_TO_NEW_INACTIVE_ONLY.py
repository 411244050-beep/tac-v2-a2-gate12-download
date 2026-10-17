#!/usr/bin/env python3
"""TAC-V2/A2 public-download encrypted stage decryptor; Python stdlib only.
STAGE ONLY. Never starts or modifies a running TAC process.
Authentication: RFC8439 ChaCha20-Poly1305, detached metadata via pinned hashes.
"""
from __future__ import annotations
import argparse, hashlib, hmac, json, os, struct, sys, zipfile
from pathlib import Path
from io import BytesIO

MAGIC=b'TAC-AIPRO-C735-SIX-CHACHA20-POLY1305-V1\n'
AAD=b'TAC-V2-A2|C735|6-FILES|NONTRADING|INACTIVE-ONLY'
EXPECTED_PLAIN_SHA256='a583976874d613ec859b10c33947ccb937ba5c5c438e49530205d8b5f2af210f'
EXPECTED_ENCRYPTED_SHA256='22730a5d22bbce455808a0e5bb193d14ff5b27bd4676dacfc647d6c4d1435eed'
ALLOWED={
 'MANIFEST.json',
 'VERIFY_PACKAGE_READONLY.py',
 'PRECHECK_C735_BASE_READONLY.py',
 'GENERATE_RUNNER_IN_UPLOAD_FOLDER_ONLY.py',
 'README_FIRST_中文.txt',
 'work/live/full_live_ai_pro_ws_transport_recovery_v1.py',
}
MASK=0xffffffff

def _rot(x,n):return ((x<<n)|(x>>(32-n))) & MASK

def _quarter(s,a,b,c,d):
 s[a]=(s[a]+s[b])&MASK;s[d]=_rot(s[d]^s[a],16)
 s[c]=(s[c]+s[d])&MASK;s[b]=_rot(s[b]^s[c],12)
 s[a]=(s[a]+s[b])&MASK;s[d]=_rot(s[d]^s[a],8)
 s[c]=(s[c]+s[d])&MASK;s[b]=_rot(s[b]^s[c],7)

def _block(key,nonce,counter):
 initial=[0x61707865,0x3320646e,0x79622d32,0x6b206574]+list(struct.unpack('<8I',key))+[counter]+list(struct.unpack('<3I',nonce))
 s=initial.copy()
 for _ in range(10):
  _quarter(s,0,4,8,12);_quarter(s,1,5,9,13);_quarter(s,2,6,10,14);_quarter(s,3,7,11,15)
  _quarter(s,0,5,10,15);_quarter(s,1,6,11,12);_quarter(s,2,7,8,13);_quarter(s,3,4,9,14)
 return struct.pack('<16I',*((s[i]+initial[i])&MASK for i in range(16)))

def _poly1305(message,once_key):
 r=int.from_bytes(once_key[:16],'little')&0x0ffffffc0ffffffc0ffffffc0fffffff
 s=int.from_bytes(once_key[16:],'little')
 total=0;p=(1<<130)-5
 for i in range(0,len(message),16):
  part=message[i:i+16]
  total=((total+int.from_bytes(part+b'\x01','little'))*r)%p
 return ((total+s)%(1<<128)).to_bytes(16,'little')

def _unseal(raw,key):
 if not raw.startswith(MAGIC) or len(raw)<len(MAGIC)+12+16:
  raise ValueError('INVALID_ENCRYPTED_HEADER')
 nonce=raw[len(MAGIC):len(MAGIC)+12]
 ciphertext=raw[len(MAGIC)+12:-16]
 tag=raw[-16:]
 polykey=_block(key,nonce,0)[:32]
 pad=lambda n: b'\x00'*((-n)%16)
 mac=AAD+pad(len(AAD))+ciphertext+pad(len(ciphertext))+struct.pack('<QQ',len(AAD),len(ciphertext))
 if not hmac.compare_digest(_poly1305(mac,polykey),tag):
  raise ValueError('STAGE_CIPHERTEXT_AUTHENTICATION_FAILED')
 out=bytearray(len(ciphertext))
 for idx in range(0,len(ciphertext),64):
  counter=1+idx//64
  if counter >= (1<<32):raise ValueError('COUNTER_OVERFLOW')
  stream=_block(key,nonce,counter)
  part=ciphertext[idx:idx+64]
  out[idx:idx+len(part)]=bytes(a^b for a,b in zip(part,stream))
 return bytes(out)


PINS={"work/live/full_live_d5_operational_risk_policy_authority_v1.json":"ba8194f3fe530a150887579f23c21dd39ad33c24","work/live/full_live_d5_risk_eligibility_authority_v1.json":"3dfec30d3f35965fbb94bf856ceed14b67e31022","work/live/full_live_execution_feasibility_policy_authority_v1.json":"152b84b00c30e0e3b16119c666e7d7d1463a4833","work/live/full_live_authoritative_entry_activation_binding_v1.py":"497e720a144050a60aa74c8d20b03e5c2ce70568","work/live/full_live_post_update014_execution_observer_v1.py":"9510849a4cbcaa00707cb007609efa421a8930bf","work/live/full_live_d6_strategy_evidence_binding_v1.py":"e186f67575e69277cb09175bbbac909cd1662d4c","work/live/full_live_d6_production_application_v1.py":"6271adb0144ae3e4f16998a0fd4c039a52d5402a","work/live/full_live_d6_production_cutoff_input_v1.py":"6effd35df81d4a0a041c1c66c1079ca1c0b9bbbb","work/live/full_live_generic_active_d4_production_binding_v1.py":"490c628ce396c47870c8c352cf8e0b38bbcb5024","work/live/full_live_batch_adoption_v1.py":"4e13855e66f5d5755094bb5db72453261c582d09","work/live/full_live_gate3_pre_adoption_source_v1.py":"af696d7e73381b7df690d7b0967bb4d7e7cf857a","work/live/full_live_gate3_natural_admission_witness_v1.py":"12717517640f705a0def5b0755bb6edebd42f8fe","work/live/full_live_forward_evidence_finite_runner_v1.py":"56008926b0ae818e151eb846e413ae72f2eaf419","work/live/full_live_persistent_supervisor_v1.sh":"f1cecfab1ee10ea2a1be333ec2b34f650f44e8a6","work/live/full_live_openclaw_recovery_assessment_v1.py":"bc04cf0d3bd048cd080a26571a5ccd63a910342b","work/live/full_live_restart_tolerant_epoch_transition_v1.py":"d81f52a99a13be134ce8b967bcf3ff045dbaa2e6","provisional_shadow_v1/prospective_usdm_universe_v1_recovered_canonical.json":"d86c13f9c4ac3f80e88eda5a1607965fb650251a"}
SIX=["work/live/full_live_post_update014_execution_observer_v1.py","work/live/full_live_generic_active_d4_production_binding_v1.py","work/live/full_live_batch_adoption_v1.py","work/live/full_live_forward_evidence_finite_runner_v1.py","work/live/full_live_gate3_pre_adoption_source_v1.py","work/live/full_live_gate3_natural_admission_witness_v1.py"]
SOURCE_COMMIT='c73522e957a77c40096ebb880529ae5cd0fc81b0'

def gitblob(raw):
 return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()

def run():
 if os.environ.get('TAC_LIVE_ENABLED','0')!='0':raise ValueError('LIVE_FLAG_MUST_BE_ZERO')
 ap=argparse.ArgumentParser()
 ap.add_argument('--encrypted-file',required=True,type=Path)
 ap.add_argument('--verified-host-base-root',required=True,type=Path)
 ap.add_argument('--new-inactive-dir',required=True,type=Path)
 a=ap.parse_args()
 keyhex=os.environ.get('TAC_C735_RESTORE_KEY_HEX','')
 if len(keyhex)!=64:raise ValueError('RECOVERY_KEY_MUST_BE_64_HEX')
 try:key=bytes.fromhex(keyhex)
 except ValueError as exc:raise ValueError('INVALID_RECOVERY_KEY') from exc
 encrypted=a.encrypted_file
 if encrypted.is_symlink() or not encrypted.is_file():raise ValueError('ENCRYPTED_INPUT_INVALID')
 data=json.loads(_unseal(encrypted.read_bytes(),key).decode('utf-8'))
 if data.get('schema')!='TAC_C735_SIX_BYTE_EXACT_INACTIVE_RECOVERY_V1' or data.get('source_commit')!=SOURCE_COMMIT:raise ValueError('UNTRUSTED_SOURCE_BUNDLE')
 rows=data.get('files')
 if not isinstance(rows,list) or len(rows)!=6 or {x.get('path') for x in rows}!=set(SIX):raise ValueError('SIX_FILE_SET_INVALID')
 patch={}
 for x in rows:
  rel=x['path']
  if x.get('blob')!=PINS[rel] or not isinstance(x.get('content'),str):raise ValueError('FROZEN_SOURCE_MANIFEST_MISMATCH')
  raw=x['content'].encode('utf-8')
  if gitblob(raw)!=PINS[rel]:raise ValueError('FROZEN_SOURCE_GIT_BLOB_MISMATCH:'+rel)
  compile(raw,rel,'exec')
  patch[rel]=raw
 base=a.verified_host_base_root
 if not base.is_absolute() or base.is_symlink() or not base.is_dir():raise ValueError('HOST_SOURCE_ROOT_INVALID')
 out=a.new_inactive_dir
 if (not out.is_absolute() or out.exists() or out.is_symlink() or
     not out.parent.is_dir() or out.parent.is_symlink() or
     not out.parent.name.startswith('tac-inactive-stage-')):
  raise ValueError('DESTINATION_MUST_BE_NEW_CHILD_OF_EXISTING_INACTIVE_STAGE')
 forbidden={'.tac-v2-a2-state','tac-runtime-active','tac-measurement-runtime-active','CURRENT','epoch','checkpoint','.git'}
 if any(x in forbidden for x in out.parts):raise ValueError('FORBIDDEN_OUTPUT_PATH')
 checked={}
 for rel,want in PINS.items():
  if rel in patch:
   raw=patch[rel]
  else:
   src=base/rel
   if src.is_symlink() or not src.is_file() or not src.is_file():raise ValueError('REMAINING_PIN_NOT_REGULAR:'+rel)
   import stat
   if not stat.S_ISREG(src.stat().st_mode):raise ValueError('REMAINING_PIN_NOT_REGULAR:'+rel)
   raw=src.read_bytes()
  if gitblob(raw)!=want:raise ValueError('REMAINING_HOST_PIN_FAILED:'+rel)
  checked[rel]=raw
 out.mkdir(mode=0o700)
 for rel,raw in checked.items():
  dest=out/rel
  dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb') as fp:fp.write(raw)
 for rel,want in PINS.items():
  if gitblob((out/rel).read_bytes())!=want:raise ValueError('RECOVERED_SNAPSHOT_POSTWRITE_MISMATCH')
 report={'status':'PASS_C735_17_RECOVERED_INACTIVE_ONLY_NOT_DEPLOYABLE',
   'original_source_commit':SOURCE_COMMIT,
   'host_matching_pins_reused':len(PINS)-len(SIX),'github_original_pins_restored':len(SIX),
   'total_frozen_pins_verified':len(PINS),'inactive_source_root':str(out),
   'source_tree_complete':False,'active_forward_changed':False,
   'measurement_changed':False,'cron_changed':False,'CURRENT_changed':False,
   'orders':0,'fills':0,'execution_intents':0,'cutover_authorized':False}
 print(json.dumps(report,ensure_ascii=False,sort_keys=True))

if __name__=='__main__':
 try:run()
 except Exception as exc:
  print(json.dumps({'status':'HOLD_C735_INACTIVE_RECOVERY','reason':str(exc) if isinstance(exc,ValueError) else type(exc).__name__,
    'orders':0,'fills':0,'execution_intents':0},ensure_ascii=False,sort_keys=True))
  sys.exit(2)
