# Redo-PTK

PolyTrack export-string generator for wild AI-built tracks compatible with the
PolyTrack `0.5.2` serialization format described in the prompt.

## Quick command in Codespaces

Install the serializer dependencies once:

```bash
python3 -m pip install -r requirements.txt
```

Then generate a code from the terminal:

```bash
./polytrack go-wild
```

The command prints one importable track string that starts like this:

```text
PolyTrack1...
```

To save it to a file instead of copying from the terminal, run:

```bash
./polytrack go-wild --output wild-track.txt
```

You can also generate a small bridge test track:

```bash
./polytrack bridge --length 10
```

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

## Commands

### Wild track

```bash
./polytrack go-wild
```

Options:

- `--author Zawg` changes the author metadata.
- `--name AI_Wild_Build` changes the track name metadata.
- `--output wild-track.txt` writes the generated `PolyTrack1...` code to a file.
- `--show-blocks` prints the raw validated block list for debugging.

### Bridge test track

```bash
./polytrack bridge --length 10
```

Options:

- `--length 10` controls the bridge length, including the start and finish blocks.
- `--author Zawg` changes the author metadata.
- `--name AI_Bridge_Test` changes the track name metadata.
- `--output bridge-track.txt` writes the generated `PolyTrack1...` code to a file.
- `--show-blocks` prints the raw validated block list for debugging.

The script validates that every generated track contains exactly one start line
and at least one finish line before it serializes the metadata wrapper.
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
