# Redo-PTK

PolyTrack export-string generator for a wild AI-built track compatible with the
PolyTrack `0.5.2` serialization format described in the prompt.

## Protocol

The generator emits a string that starts with `PolyTrack1`. The payload is:

1. A MessagePack object with this wrapper:
   - `v`: `2`
   - `a`: author metadata, defaulting to `Zawg`
   - `n`: track name metadata, defaulting to `AI_Wild_Build`
   - `b`: block list where every block is `[ID, X, Y, Z, Rotation]`
2. Zstandard-compressed at level 3.
3. Base64-encoded and appended to the `PolyTrack1` prefix.

## Block Dictionary

| ID | Block |
| --- | --- |
| `0` | `Road_Straight` |
| `1` | `Road_Curve_90` |
| `5` | `Start_Line` |
| `6` | `Finish_Line` |
| `10` | `Pillar_Square` |
| `12` | `Road_Slope` |
| `22` | `Checkpoint` |

## Usage

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Generate the wild build export string:

```bash
python scripts/generate_polytrack.py
```

The script validates that the track contains exactly one start line and at least
one finish line before it serializes the metadata wrapper.
