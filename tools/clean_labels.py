#!/usr/bin/env python3
"""
Clean labels_human_merged.csv:
- Filter out rows with low-confidence predicted_mood
- Merge moods: calm+easygoing, melancholic+wistful
- Keep neutral rows (training script already excludes them)

Outputs: token_dataset/labels_humans_cleaned_v1.csv
"""

import argparse
from pathlib import Path
import sys
import pandas as pd

DATA_DIR = Path("token_dataset")
IN_CSV = DATA_DIR / "labels_human_merged.csv"
OUT_CSV = DATA_DIR / "labels_humans_cleaned_v1.csv"

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", type=str, default=str(IN_CSV),
                    help="Input labels CSV (default: token_dataset/labels_human_merged.csv)")
    ap.add_argument("--out_csv", type=str, default=str(OUT_CSV),
                    help="Output cleaned CSV (default: token_dataset/labels_humans_cleaned_v1.csv)")
    ap.add_argument("--pred_conf_thresh", type=float, default=0.60,
                    help="Drop rows where predicted_mood is present and pred_confidence < this (default: 0.60)")
    return ap.parse_args()

def main():
    args = parse_args()
    inp = Path(args.in_csv)
    outp = Path(args.out_csv)

    if not inp.exists():
        print(f"❌ Input not found: {inp}")
        sys.exit(1)

    df = pd.read_csv(inp)

    # Basic validation
    if "json_path" not in df.columns or "mood" not in df.columns:
        print("❌ Input CSV must contain at least 'json_path' and 'mood' columns")
        sys.exit(1)

    print("=== BEFORE ===")
    print("rows:", len(df))
    print("mood counts:\n", df["mood"].value_counts(dropna=False).sort_index())

    # 1) Filter low-confidence predictions
    if "predicted_mood" in df.columns and "pred_confidence" in df.columns:
        mask_low_pred = df["predicted_mood"].notna() & (df["pred_confidence"].fillna(0) < args.pred_conf_thresh)
        dropped = int(mask_low_pred.sum())
        if dropped > 0:
            df = df.loc[~mask_low_pred].reset_index(drop=True)
        print(f"\nFiltered low-confidence predicted rows (< {args.pred_conf_thresh:.2f}): {dropped}")
    else:
        print("\n(predicted_mood/pred_confidence not found — skipping filter)")

    # 2) Merge classes
    df["mood_raw"] = df["mood"]  # keep original for reference
    df.loc[df["mood"].isin(["calm", "easygoing"]), "mood"] = "calm_easygoing"
    df.loc[df["mood"].isin(["melancholic", "wistful"]), "mood"] = "melancholic_wistful"

    print("Merged classes:")
    print("  calm + easygoing → calm_easygoing")
    print("  melancholic + wistful → melancholic_wistful")

    # 3) Save
    front = ["json_path", "mood", "mood_raw"]
    cols = front + [c for c in df.columns if c not in front]
    df = df[cols]

    outp.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(outp, index=False, encoding="utf-8")

    print("\n=== AFTER ===")
    print("rows:", len(df))
    print("mood counts:\n", df["mood"].value_counts(dropna=False).sort_index())
    print(f"\n✅ Wrote cleaned labels to: {outp}")

if __name__ == "__main__":
    main()
