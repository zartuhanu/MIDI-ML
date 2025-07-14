#!/usr/bin/env python3
"""Extract bass line notes from MIDI files in a directory.

For each MIDI file, instruments that look like bass (program 32-39 or
name containing "bass") are scanned.  Notes are written to a JSON file
with relative file paths as keys.
"""

import argparse
import json
import os
import sys

import pretty_midi


def find_bass_instruments(pm: pretty_midi.PrettyMIDI):
    """Return a list of instruments likely to contain the bass line."""
    bass_instrs = []
    for inst in pm.instruments:
        if inst.is_drum:
            continue
        name = inst.name.lower()
        if 32 <= inst.program <= 39 or "bass" in name:
            bass_instrs.append(inst)
    return bass_instrs


def extract_notes(insts):
    """Return a list of note dictionaries from instruments."""
    notes = []
    for inst in insts:
        for n in inst.notes:
            notes.append({
                "start": float(n.start),
                "end": float(n.end),
                "pitch": int(n.pitch),
                "velocity": int(n.velocity),
                "program": int(inst.program),
            })
    return notes


def process_file(fp, root_dir):
    try:
        pm = pretty_midi.PrettyMIDI(fp)
    except Exception as e:
        print(f"Failed to parse {fp}: {e}", file=sys.stderr)
        return None
    bass_inst = find_bass_instruments(pm)
    if not bass_inst:
        return None
    rel = os.path.relpath(fp, root_dir)
    return rel, extract_notes(bass_inst)


def main():
    p = argparse.ArgumentParser(description="Extract bass lines from MIDI files")
    p.add_argument("src_dir", nargs="?", default="lmd_clean",
                   help="Directory containing MIDI files")
    p.add_argument("--out", default="basslines.json",
                   help="Output JSON file")
    args = p.parse_args()

    result = {}
    for dirpath, _, files in os.walk(args.src_dir):
        for fn in files:
            if fn.lower().endswith(".mid"):
                fp = os.path.join(dirpath, fn)
                out = process_file(fp, args.src_dir)
                if out:
                    key, notes = out
                    result[key] = notes

    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Bass lines for {len(result)} files written to {args.out}")


if __name__ == "__main__":
    main()
