#!/usr/bin/env python3
import json, csv
from pathlib import Path

DATA_DIR = Path("token_dataset")
LABELS_ORIG = DATA_DIR / "labels_human_merged.csv"
LABELS_CLEAN = DATA_DIR / "labels_humans_cleaned_v1.csv"
SPLITS_ORIG = DATA_DIR / "splits.json"
SPLITS_OUT  = DATA_DIR / "splits_cleaned.json"

def main():
    # rows in original order (indices in original splits refer to this)
    rows = []
    with LABELS_ORIG.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)

    # cleaned whitelist by json_path
    kept = set()
    with LABELS_CLEAN.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            kept.add(row["json_path"])

    # load original splits
    splits = json.loads(SPLITS_ORIG.read_text(encoding="utf-8"))["indices"]

    # filter each split by kept json_paths (no reassignment!)
    def keep_idx(i):
        if i < 0 or i >= len(rows): return False
        return rows[i]["json_path"] in kept

    splits_clean = {k: [i for i in idxs if keep_idx(i)] for k, idxs in splits.items()}

    # write out
    out = {"indices": splits_clean}
    SPLITS_OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", SPLITS_OUT)

if __name__ == "__main__":
    main()
