#!/usr/bin/env python3
"""Stream-copy the bundled entry.png to /output/entry.png.

Version 2 hardens the original copy loop:
  * checks the source exists before opening the destination,
  * copies through an explicit chunk loop that counts bytes,
  * fsyncs the destination so the bytes are durable on return,
  * verifies the destination size matches the source size and
    raises instead of silently leaving a truncated file behind.
"""

import os
import sys
from pathlib import Path

CHUNK_SIZE = 64 * 1024
OUTPUT_PATH = Path("/output/entry.png")


def copy_stream(src: Path, dst: Path) -> int:
    """Copy src to dst in chunks; return the number of bytes written."""
    written = 0
    with src.open("rb") as fin, dst.open("wb") as fout:
        while True:
            chunk = fin.read(CHUNK_SIZE)
            if not chunk:
                break
            fout.write(chunk)
            written += len(chunk)
        fout.flush()
        os.fsync(fout.fileno())
    return written


def main() -> int:
    src = Path(__file__).resolve().parent / "entry.png"
    if not src.is_file():
        print(f"error: source image not found: {src}", file=sys.stderr)
        return 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    written = copy_stream(src, OUTPUT_PATH)

    expected = src.stat().st_size
    if written != expected or OUTPUT_PATH.stat().st_size != expected:
        print(
            f"error: copy mismatch (wrote {written}, expected {expected})",
            file=sys.stderr,
        )
        return 1

    print(f"copied {written} bytes -> {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
