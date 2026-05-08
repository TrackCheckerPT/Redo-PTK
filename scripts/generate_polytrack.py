#!/usr/bin/env python3
"""Generate PolyTrack v0.5.2-compatible export strings.

The game expects a MessagePack-serialized metadata wrapper compressed with
Zstandard and Base64 encoded after the ``PolyTrack1`` prefix.
"""

from __future__ import annotations

import argparse
import base64
import importlib.util
import json
from collections.abc import Iterable, Sequence
from pathlib import Path


ROAD_STRAIGHT = 0
ROAD_CURVE_90 = 1
START_LINE = 5
FINISH_LINE = 6
PILLAR_SQUARE = 10
ROAD_SLOPE = 12
CHECKPOINT = 22

PREFIX = "PolyTrack1"
DEFAULT_AUTHOR = "Zawg"
DEFAULT_NAME = "AI_Wild_Build"

Block = list[int]


def require_serializer_dependencies() -> None:
    """Exit with an actionable message when serializer packages are missing."""
    missing = [
        package
        for package in ("msgpack", "zstandard")
        if importlib.util.find_spec(package) is None
    ]
    if missing:
        packages = ", ".join(missing)
        raise SystemExit(
            f"Missing serializer dependencies: {packages}. "
            "Run `python3 -m pip install -r requirements.txt` first."
        )


def generate_polytrack_code(
    blocks: Sequence[Sequence[int]],
    author: str = DEFAULT_AUTHOR,
    name: str = DEFAULT_NAME,
) -> str:
    """Return a PolyTrack export string for a validated block list."""
    require_serializer_dependencies()

    import msgpack
    import zstandard as zstd

    validate_blocks(blocks)
    track_package = {
        "v": 2,
        "a": author,
        "n": name,
        "b": [list(block) for block in blocks],
    }

    packed = msgpack.packb(track_package, use_bin_type=True)
    compressor = zstd.ZstdCompressor(level=3)
    compressed = compressor.compress(packed)
    encoded = base64.b64encode(compressed).decode("utf-8")
    return f"{PREFIX}{encoded}"


def validate_blocks(blocks: Sequence[Sequence[int]]) -> None:
    """Raise ValueError when blocks violate the required game wrapper rules."""
    if not blocks:
        raise ValueError("Track must contain at least one block.")

    start_count = 0
    finish_count = 0
    for index, block in enumerate(blocks):
        if len(block) != 5:
            raise ValueError(f"Block {index} must be [ID, X, Y, Z, Rotation].")
        if any(not isinstance(value, int) for value in block):
            raise ValueError(f"Block {index} contains a non-integer value: {block!r}")

        block_id = block[0]
        if block_id == START_LINE:
            start_count += 1
        elif block_id == FINISH_LINE:
            finish_count += 1

    if start_count != 1:
        raise ValueError(
            f"Track must contain exactly one start line; found {start_count}."
        )
    if finish_count < 1:
        raise ValueError("Track must contain at least one finish line.")


def add_bridge_segment(blocks: list[Block], x: int, y: int, z: int, block_id: int) -> None:
    """Append a road segment and a decorative support pillar underneath it."""
    blocks.append([block_id, x, y, z, 0])
    blocks.append([PILLAR_SQUARE, x, y - 1, z, 0])
    if y > 1:
        blocks.append([PILLAR_SQUARE, x, y - 2, z, 0])


def add_pillar_wall(blocks: list[Block], xs: Iterable[int], y: int, z: int) -> None:
    """Append a row of square pillars for sculptural decoration."""
    for x in xs:
        blocks.append([PILLAR_SQUARE, x, y, z, 0])


def build_wild_blocks() -> list[Block]:
    """Build a wild route with jumps, elevated bridges, curves, and supports."""
    blocks: list[Block] = [[START_LINE, 0, 0, 0, 0]]

    # Launch runway into a stepped ramp.
    for z in range(1, 7):
        add_bridge_segment(blocks, 0, 0, z, ROAD_STRAIGHT)
    for y, z in enumerate(range(7, 12), start=1):
        add_bridge_segment(blocks, 0, y, z, ROAD_SLOPE)
    blocks.append([CHECKPOINT, 0, 5, 12, 0])

    # Airborne spine with alternating side-pillars to make the jump read clearly.
    for offset, z in enumerate(range(13, 24)):
        x = -1 if offset % 2 == 0 else 1
        add_bridge_segment(blocks, x, 5, z, ROAD_STRAIGHT)
        blocks.append([PILLAR_SQUARE, -3, 3, z, 0])
        blocks.append([PILLAR_SQUARE, 3, 3, z, 0])

    # Left hook, high bridge, and mirrored return lane.
    blocks.append([ROAD_CURVE_90, -2, 5, 24, 3])
    for x in range(-3, -12, -1):
        add_bridge_segment(blocks, x, 5, 24, ROAD_STRAIGHT)
    blocks.append([CHECKPOINT, -12, 5, 24, 1])
    blocks.append([ROAD_CURVE_90, -13, 5, 23, 2])
    for z in range(22, 10, -1):
        block_id = ROAD_SLOPE if z in {20, 16, 12} else ROAD_STRAIGHT
        add_bridge_segment(blocks, -13, 4, z, block_id)
    blocks.append([ROAD_CURVE_90, -12, 3, 9, 1])

    # Fast return stretch with decorative gate arrays.
    for x in range(-11, 2):
        add_bridge_segment(blocks, x, 3, 9, ROAD_STRAIGHT)
        if x % 3 == 0:
            add_pillar_wall(blocks, range(x - 1, x + 2), 1, 7)
            add_pillar_wall(blocks, range(x - 1, x + 2), 1, 11)
    blocks.append([CHECKPOINT, 2, 3, 9, 0])

    # Final drop and sprint to finish.
    for y, z in [(2, 8), (1, 7), (0, 6)]:
        add_bridge_segment(blocks, 2, y, z, ROAD_SLOPE)
    for z in range(5, -3, -1):
        blocks.append([ROAD_STRAIGHT, 2, 0, z, 2])
    blocks.append([FINISH_LINE, 2, 0, -3, 2])

    # Monuments around the finish so the generated track looks intentionally built.
    for z in range(-4, 2):
        blocks.append([PILLAR_SQUARE, -1, 0, z, 0])
        blocks.append([PILLAR_SQUARE, 5, 0, z, 0])
    for height in range(1, 5):
        blocks.append([PILLAR_SQUARE, -1, height, -3, 0])
        blocks.append([PILLAR_SQUARE, 5, height, -3, 0])

    validate_blocks(blocks)
    return blocks


def build_bridge_blocks(length: int = 10) -> list[Block]:
    """Build the compact straight bridge example from the prompt."""
    if length < 2:
        raise ValueError("Bridge length must be at least 2 to include start and finish.")

    blocks: list[Block] = [[START_LINE, 0, 0, 0, 0]]
    for z in range(1, length):
        block_id = FINISH_LINE if z == length - 1 else ROAD_STRAIGHT
        blocks.append([block_id, 0, 0, z, 0])
        blocks.append([PILLAR_SQUARE, 0, -1, z, 0])

    validate_blocks(blocks)
    return blocks


def write_output(track_code: str, output_path: Path | None) -> None:
    """Print the track code or write it to a file when requested."""
    if output_path is None:
        print(track_code)
        return

    output_path.write_text(f"{track_code}\n", encoding="utf-8")
    print(f"Wrote PolyTrack code to {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="polytrack",
        description="Generate PolyTrack1 export strings from the Codespace terminal.",
    )
    subparsers = parser.add_subparsers(dest="command")

    wild = subparsers.add_parser(
        "go-wild",
        aliases=["wild"],
        help="Generate the complex AI_Wild_Build track code.",
    )
    wild.add_argument("--author", default=DEFAULT_AUTHOR, help="Track author metadata.")
    wild.add_argument("--name", default=DEFAULT_NAME, help="Track name metadata.")
    wild.add_argument(
        "--output",
        type=Path,
        help="Optional file path for the generated PolyTrack1 code.",
    )
    wild.add_argument(
        "--show-blocks",
        action="store_true",
        help="Print the raw validated block list instead of the encoded track code.",
    )

    bridge = subparsers.add_parser(
        "bridge",
        help="Generate a simple straight bridge track code for quick testing.",
    )
    bridge.add_argument("--author", default=DEFAULT_AUTHOR, help="Track author metadata.")
    bridge.add_argument("--name", default="AI_Bridge_Test", help="Track name metadata.")
    bridge.add_argument(
        "--length",
        type=int,
        default=10,
        help="Number of road positions including start and finish.",
    )
    bridge.add_argument(
        "--output",
        type=Path,
        help="Optional file path for the generated PolyTrack1 code.",
    )
    bridge.add_argument(
        "--show-blocks",
        action="store_true",
        help="Print the raw validated block list instead of the encoded track code.",
    )

    parser.set_defaults(
        author=DEFAULT_AUTHOR,
        command="go-wild",
        name=DEFAULT_NAME,
        output=None,
        show_blocks=False,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command in {"go-wild", "wild"}:
        blocks = build_wild_blocks()
    elif args.command == "bridge":
        blocks = build_bridge_blocks(length=args.length)
    else:
        raise ValueError(f"Unknown command: {args.command}")

    if args.show_blocks:
        print(json.dumps(blocks))
        return

    track_code = generate_polytrack_code(blocks, author=args.author, name=args.name)
    write_output(track_code, args.output)


if __name__ == "__main__":
    main()
