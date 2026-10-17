#!/usr/bin/env python3
"""TAC-V2/A2 public-download encrypted stage decryptor; Python stdlib only.
STAGE ONLY. Never starts or modifies a running TAC process.
Authentication: RFC8439 ChaCha20-Poly1305, detached metadata via pinned hashes.
"""
from __future__ import annotations
import argparse, hashlib, hmac, json, os, struct, sys, zipfile
from pathlib import Path
from io import BytesIO

MAGIC=b'TAC-AIPRO-STAGE-CHACHA20-POLY1305-V1\n'
AAD=b'TAC-V2-A2|2026-10-17|STAGE-ONLY|528|NONTRADING'
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

def run():
 if os.environ.get('TAC_LIVE_ENABLED','0')!='0':raise ValueError('TRADING_FLAG_NOT_ZERO')
 ap=argparse.ArgumentParser()
 ap.add_argument('--encrypted-file',required=True,type=Path)
 ap.add_argument('--new-inactive-dir',required=True,type=Path)
 a=ap.parse_args()
 keyhex=os.environ.get('TAC_STAGE_DECRYPT_KEY_HEX','')
 if len(keyhex)!=64:raise ValueError('ONE_TIME_DECRYPT_KEY_REQUIRED_64_HEX')
 try:key=bytes.fromhex(keyhex)
 except ValueError as exc:raise ValueError('INVALID_KEY_HEX') from exc
 raw=a.encrypted_file.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=EXPECTED_ENCRYPTED_SHA256:
  raise ValueError('ENCRYPTED_BYTES_SHA256_MISMATCH')
 plain=_unseal(raw,key)
 if hashlib.sha256(plain).hexdigest()!=EXPECTED_PLAIN_SHA256 or len(plain)!=10163:
  raise ValueError('DECRYPTED_ORIGINAL_ZIP_IDENTITY_MISMATCH')
 with zipfile.ZipFile(BytesIO(plain)) as z:
  names=z.namelist()
  if len(names)!=len(ALLOWED) or set(names)!=ALLOWED or z.testzip() is not None:
   raise ValueError('ZIP_MEMBER_INTEGRITY_OR_IDENTITY_MISMATCH')
  for info in z.infolist():
   if info.is_dir() or info.file_size>50000 or info.filename.startswith('/') or '..' in Path(info.filename).parts:
    raise ValueError('INVALID_ARCHIVE_PATH_OR_SIZE')
   if info.external_attr>>16 & 0o170000 == 0o120000:
    raise ValueError('SYMLINK_INSIDE_ARCHIVE')
  manifest=json.loads(z.read('MANIFEST.json'))
  for f in manifest['members']:
   body=z.read(f['path'])
   if f['path'] not in ALLOWED or len(body)!=f['bytes'] or hashlib.sha256(body).hexdigest()!=f['sha256']:
    raise ValueError('MANIFEST_MEMBER_MISMATCH')
  out=a.new_inactive_dir
  if not out.is_absolute() or out.exists() or out.is_symlink():
   raise ValueError('OUTPUT_MUST_BE_NEW_ABSOLUTE_INACTIVE_PATH')
  reserved=('.tac-v2-a2-state','tac-runtime-active','tac-measurement-runtime-active','CURRENT','epoch','checkpoint')
  if any(term in out.parts for term in reserved):raise ValueError('FORBIDDEN_OUTPUT_PATH_COMPONENT')
  if not out.parent.is_dir() or out.parent.is_symlink():raise ValueError('OUTPUT_PARENT_MUST_BE_EXISTING_REGULAR_DIR')
  out.mkdir(mode=0o700)
  (out/'SOURCE_ZIP_SHA256.txt').write_text(EXPECTED_PLAIN_SHA256+'  TAC_AIPro_528_Forward_EOF_非交易离线预置包_20261017.zip\n')
  for name in names:
   f=out/name
   f.parent.mkdir(parents=True,exist_ok=True)
   with f.open('xb') as fh: fh.write(z.read(name))
  for name in names:
   if name.endswith('.py'):
    compile((out/name).read_bytes(),name,'exec')
 print(json.dumps({'status':'PASS_PUBLIC_ENCRYPTED_STAGE_DECRYPTED_NO_CUTOVER',
                   'inactive_dir':str(out),'plain_zip_sha256':EXPECTED_PLAIN_SHA256,
                   'trading':False,'orders':0,'fills':0,'execution_intents':0,
                   'host_running_processes_touched':False},ensure_ascii=False,sort_keys=True))

if __name__=='__main__':
 try:run()
 except Exception as exc:
  print(json.dumps({'status':'HOLD_STAGE_DECRYPT_OR_SOURCE_INTEGRITY','reason':str(exc) if isinstance(exc,ValueError) else type(exc).__name__,
                    'orders':0,'fills':0,'execution_intents':0},sort_keys=True))
  sys.exit(2)
