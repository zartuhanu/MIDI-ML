#!/usr/bin/env python
"""
Scan the Lakh MIDI Dataset and copy only valid files to lmd_clean_valid/.
Invalid or unrecoverable files are listed in bad_midis.log.
"""
import os, shutil, logging, warnings
import mido, pretty_midi

SRC_DIR   = "lmd_clean"
DST_DIR   = "lmd_clean_valid"
LOG_FILE  = "bad_midis.log"

# ----------  logging / warnings  ----------
warnings.filterwarnings('ignore', category=RuntimeWarning, module='pretty_midi')
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(levelname)s: %(message)s')
os.makedirs(DST_DIR, exist_ok=True)

def is_valid_midi(fp: str) -> bool:
    """Return True if fp can be parsed; False otherwise."""
    try:
        # 1️⃣ tolerant load via mido -> PrettyMIDI
        mid = mido.MidiFile(fp, clip=True)
        pretty_midi.PrettyMIDI(mid)            # verifies musical/tempo meta too
        return True
    except Exception as e1:
        # 2️⃣ quick sanity check: are status bytes plausible?
        try:
            with open(fp, 'rb') as f:
                data = f.read()
            # all status bytes (>= 0x80) must be followed by at least 1 byte
            if any(data[i] >= 0x80 and i == len(data) - 1 for i in range(len(data))):
                raise ValueError("truncated status byte at EOF")
            return False                       # failed sanity; log below
        except Exception as e2:
            logging.warning(f"{fp} → {e1} / {e2}")
            return False

def mirror_path(src_fp: str) -> str:
    """Map source path under SRC_DIR to destination path under DST_DIR."""
    rel = os.path.relpath(src_fp, SRC_DIR)
    return os.path.join(DST_DIR, rel)

def main():
    ok, bad = 0, 0
    for dirpath, _, filenames in os.walk(SRC_DIR):
        for fn in filenames:
            if not fn.lower().endswith(".mid"):
                continue

            src_fp = os.path.join(dirpath, fn)
            if is_valid_midi(src_fp):
                dst_fp = mirror_path(src_fp)
                os.makedirs(os.path.dirname(dst_fp), exist_ok=True)
                shutil.copy2(src_fp, dst_fp)
                ok += 1
            else:
                bad += 1

    print(f"✓ {ok} valid files copied to {DST_DIR}")
    print(f"✗ {bad} bad files listed in {LOG_FILE}")

if __name__ == "__main__":
    main()
