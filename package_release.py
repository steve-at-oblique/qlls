# Copyright (c) 2026 Steve Jennen
# SPDX-License-Identifier: BSD-2-Clause
"""Package the shipped QDOS job and resident extension for QL UnZip."""

from pathlib import Path
from struct import pack
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent
INLINE_HEADER_SIZE = 30
QDOS_MAGIC = b"]!QDOS File Header"


def qdos_extra(name, size, file_type, dataspace):
    filename = name.encode("ascii")
    header = pack(">IBBIIH36s12x", size, 0, file_type, dataspace, 0,
                  len(filename), filename)
    # Info-ZIP's SMS/QDOS field contains a QDOS02 marker and a 64-byte header.
    data = b"QDOS02\0\0" + header
    return pack("<HH", 0xFB4A, len(data)) + data


def package():
    job = (ROOT / "ls").read_bytes()
    if (
        len(job) <= INLINE_HEADER_SIZE
        or not job.startswith(QDOS_MAGIC)
        or job[18:20] != b"\0\x0f"
        or job[21] != 1
        or not any(job[22:26])
    ):
        raise ValueError("ls must have a 30-byte QDOS executable header")

    extension = (ROOT / "ls_rext").read_bytes()
    if not extension or extension.startswith(QDOS_MAGIC):
        raise ValueError("ls_rext must be a raw resident extension")

    members = (
        ("ls", job[INLINE_HEADER_SIZE:], job[21], int.from_bytes(job[22:26], "big")),
        ("ls_rext", extension, 0, 0),
        ("LICENSE", (ROOT / "LICENSE").read_bytes(), 0, 0),
    )
    with TemporaryDirectory(dir=ROOT) as temporary:
        output = Path(temporary) / "ls.zip"
        with ZipFile(output, "w") as archive:
            for name, payload, file_type, dataspace in members:
                entry = ZipInfo(name)
                entry.create_system = 0
                entry.external_attr = 0o600 << 16
                entry.compress_type = ZIP_DEFLATED
                entry.extra = qdos_extra(name, len(payload), file_type, dataspace)
                archive.writestr(entry, payload)
        output.replace(ROOT / "ls.zip")


if __name__ == "__main__":
    package()
