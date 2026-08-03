#!/usr/bin/env python3
"""Subset Noto Sans Symbols 2 to the Unicode blocks listed in unicode-blocks.txt.

Usage:
  python3 subset_symbols.py
  python3 subset_symbols.py --blocks unicode-blocks.txt --source NotoSansSymbols2-Regular-hinted.ttf \\
                            --output stage/fonts/NotoSansSymbols2-Regular.ttf

Add blocks by editing unicode-blocks.txt, then re-run this script (or rebuild the package).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from fontTools.subset import Options, Subsetter
    from fontTools.ttLib import TTFont
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        "error: fontTools is required to subset fonts.\n"
        "  pip install fonttools\n"
    )
    raise SystemExit(1) from exc

HERE = Path(__file__).resolve().parent
DEFAULT_BLOCKS = HERE / "unicode-blocks.txt"
DEFAULT_SOURCE = HERE / "NotoSansSymbols2-Regular-hinted.ttf"
# Default output is outside the source tree; build-cmd.sh writes into stage/fonts/.
DEFAULT_OUTPUT = HERE.parent / "stage" / "fonts" / "NotoSansSymbols2-Regular.ttf"

# Accept: 1F780, 0x1F780, U+1F780, u+1f780
_HEX_RE = re.compile(r"^(?:0x|U\+|u\+)?([0-9A-Fa-f]+)$")


def parse_codepoint(token: str) -> int:
    m = _HEX_RE.match(token.strip())
    if not m:
        raise ValueError(f"invalid code point: {token!r}")
    return int(m.group(1), 16)


def load_blocks(path: Path) -> list[tuple[str, int, int]]:
    """Return list of (name, start, end) inclusive ranges."""
    blocks: list[tuple[str, int, int]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # Allow: NAME START END  (NAME may contain spaces if we take last two tokens as range)
        parts = line.split()
        if len(parts) < 3:
            raise ValueError(f"{path}:{lineno}: expected 'NAME START END', got: {raw!r}")
        start = parse_codepoint(parts[-2])
        end = parse_codepoint(parts[-1])
        name = " ".join(parts[:-2])
        if end < start:
            raise ValueError(f"{path}:{lineno}: END {end:#x} < START {start:#x}")
        blocks.append((name, start, end))
    if not blocks:
        raise ValueError(f"{path}: no blocks defined")
    return blocks


def unicodes_from_blocks(blocks: list[tuple[str, int, int]]) -> set[int]:
    cps: set[int] = set()
    for _name, start, end in blocks:
        cps.update(range(start, end + 1))
    return cps


def subset_font(source: Path, output: Path, unicodes: set[int]) -> dict:
    font = TTFont(str(source))
    cmap = font.getBestCmap() or {}
    present = sorted(cp for cp in unicodes if cp in cmap)
    missing_slots = len(unicodes) - len(present)

    if not present:
        font.close()
        raise SystemExit(
            f"error: none of the requested code points exist in {source.name}"
        )

    options = Options()
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.name_legacy = True
    options.notdef_outline = True
    options.recalc_bounds = True
    options.recalc_timestamp = False
    options.retain_gids = False

    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=set(present))
    subsetter.subset(font)

    output.parent.mkdir(parents=True, exist_ok=True)
    font.save(str(output))
    font.close()

    return {
        "requested_slots": len(unicodes),
        "glyphs_kept": len(present),
        "empty_slots_skipped": missing_slots,
        "output_bytes": output.stat().st_size,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blocks", type=Path, default=DEFAULT_BLOCKS)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="only print errors",
    )
    args = parser.parse_args(argv)

    if not args.blocks.is_file():
        sys.stderr.write(f"error: blocks file not found: {args.blocks}\n")
        return 1
    if not args.source.is_file():
        sys.stderr.write(f"error: source font not found: {args.source}\n")
        return 1

    blocks = load_blocks(args.blocks)
    unicodes = unicodes_from_blocks(blocks)
    stats = subset_font(args.source, args.output, unicodes)

    if not args.quiet:
        print(f"source:  {args.source}")
        print(f"blocks:  {args.blocks}")
        for name, start, end in blocks:
            print(f"  - {name}: U+{start:04X}–U+{end:04X}")
        print(
            f"kept {stats['glyphs_kept']} glyphs "
            f"({stats['empty_slots_skipped']} unassigned/missing slots skipped)"
        )
        print(
            f"wrote {args.output} "
            f"({stats['output_bytes'] / 1024:.1f} KB)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
