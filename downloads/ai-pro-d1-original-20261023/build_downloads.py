#!/usr/bin/env python3
"""Build public, byte-verified D1 download files from pinned original WP8 tar.xz.

Never import or execute TAC strategy source. Never copy host state,
credentials, private runtime files, account data or trading settings.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path, PurePosixPath
import io
import os
import tarfile
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
SRC = HERE / "_reference" / "strategy_rc1_exact.tar.xz"
MANIFEST = HERE / "_reference" / "strategy_rc1_SHA256SUMS.txt"
ZIP_NAME = "TAC_original_91_sources_verified_for_AIPro_20261023.zip"
PY_NAME = "TAC_D1_CanonicalBar_original_verified.py"
TXT_NAME = "TAC_D1_CanonicalBar_original_verified.txt"
CANON = "strategy_rc1/d1_data_math/canonical.py"
ARCHIVE_SHA256 = "36111563b5778513d5803a3ec7c2b86f967a71d915fbcfd9bee5cb4ebebf8174"
MANIFEST_SHA256 = "d997c67dd0e909c0a1b6eb849918e692cbe5739079605f3c78d96517d1f11b60"
CANON_SHA256 = "a647c3f66448dbf1cb322fd7561fdc74d3584ce2c5ef1c7450dd63837ef75b62"


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def build() -> None:
    archive = SRC.read_bytes()
    manifest_bytes = MANIFEST.read_bytes()
    if len(archive) != 53108 or digest(archive) != ARCHIVE_SHA256:
        raise RuntimeError("PINNED_XZ_ARCHIVE_IDENTITY_MISMATCH")
    if len(manifest_bytes) != 9711 or digest(manifest_bytes) != MANIFEST_SHA256:
        raise RuntimeError("PINNED_91_MEMBER_MANIFEST_MISMATCH")

    expected = {}
    for line in manifest_bytes.decode("ascii").splitlines():
        hash_value, sep, filename = line.partition("  ")
        if sep != "  " or filename in expected or len(hash_value) != 64:
            raise RuntimeError("BAD_OR_DUPLICATE_SHA256_MANIFEST_RECORD")
        expected[filename] = hash_value
    if len(expected) != 91 or expected.get(CANON) != CANON_SHA256:
        raise RuntimeError("FROZEN_91_MEMBER_INVENTORY_DRIFT")

    members = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:xz") as tar:
        for item in tar:
            path = PurePosixPath(item.name)
            if item.isdir():
                continue
            if (not item.isfile() or path.is_absolute()
                or ".." in path.parts or not path.parts
                or path.parts[0] != "strategy_rc1"
                or item.name not in expected
                or item.name in members or item.size > 1_000_000):
                raise RuntimeError("UNSAFE_OR_UNLISTED_TAR_MEMBER")
            f = tar.extractfile(item)
            if f is None:
                raise RuntimeError("TAR_MEMBER_UNREADABLE")
            data = f.read(item.size + 1)
            if len(data) != item.size or digest(data) != expected[item.name]:
                raise RuntimeError("ORIGINAL_SOURCE_MEMBER_HASH_MISMATCH:" + item.name)
            members[item.name] = data
    if set(members) != set(expected):
        raise RuntimeError("REQUIRED_91_SOURCES_MISSING")

    info = (
        "TAC-V2/A2 original WP8 strategy_rc1 source reference, 91 files.\n"
        "D1 CanonicalBar original SHA-256: " + CANON_SHA256 + "\n"
        "This is not a runnable Binance AI Pro strategy, not a trading "
        "authorization and not a replacement for science/runtime validation.\n"
        "Do not import private account credentials or run signed requests.\n"
        "TAC_LIVE_ENABLED=0; FULL TAC LIVE NO-GO.\n"
    ).encode("utf-8")
    with tempfile.NamedTemporaryFile(
        prefix=".tac-ai-pro-original-", suffix=".zip", dir=HERE,
        delete=False
    ) as tmp:
        tempname = tmp.name
    try:
        with zipfile.ZipFile(tempname, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9) as z:
            for name in sorted(members):
                item = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                item.compress_type = zipfile.ZIP_DEFLATED
                item.external_attr = 0o100644 << 16
                z.writestr(item, members[name], compress_type=zipfile.ZIP_DEFLATED,
                           compresslevel=9)
            z.writestr("SOURCE_SHA256SUMS.txt", manifest_bytes)
            z.writestr("AI_PRO_SOURCE_README.txt", info)
        with zipfile.ZipFile(tempname) as z:
            if z.testzip() is not None or len(z.namelist()) != 93:
                raise RuntimeError("GENERATED_ZIP_INTEGRITY_FAILURE")
        os.replace(tempname, HERE / ZIP_NAME)
    finally:
        if os.path.exists(tempname):
            os.unlink(tempname)

    # Publish exact canonical.py and .txt contents; no rewrite or normalization.
    (HERE / PY_NAME).write_bytes(members[CANON])
    (HERE / TXT_NAME).write_bytes(members[CANON])
    checks = []
    for name in (ZIP_NAME, PY_NAME, TXT_NAME):
        checks.append(digest((HERE / name).read_bytes()) + "  " + name)
    (HERE / "SHA256SUMS_DOWNLOADS.txt").write_text(
        "\n".join(checks) + "\n", encoding="ascii"
    )
    print("PUBLIC_TACTICAL_D1_DOWNLOADS=READY 91 verified original members")
    for line in checks:
        print(line)


if __name__ == "__main__":
    build()
