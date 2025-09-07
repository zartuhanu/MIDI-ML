#!/usr/bin/env python3
# sample_for_manual_labeling.py
import csv, random
from pathlib import Path
from collections import defaultdict


LABELS_CSV = Path("token_dataset/labels.csv")
NEUT_PRED  = Path("token_dataset/neutral_predictions.csv")
OUT_POOL   = Path("token_dataset/labeling_pool.csv")
POOL_SIZE  = 3000             # how many to hand-label this round
CONF_LO, CONF_HI = 0.35, 0.67  # pick uncertain ones
RNG_SEED = 42


def main():
    if not LABELS_CSV.exists() or not NEUT_PRED.exists():
        raise SystemExit("Missing labels.csv or neutral_predictions.csv")

    # Load neutral predictions keyed by json_path
    preds = {}
    with NEUT_PRED.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            row["confidence"] = float(row["confidence"])
            preds[row["json_path"]] = row

    # Load labels and match neutrals
    items = []
    with LABELS_CSV.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if (row.get("mood","").lower() == "neutral") and (row["json_path"] in preds):
                p = preds[row["json_path"]]
                c = p["confidence"]
                if CONF_LO <= c <= CONF_HI:
                    row["_predicted_mood"] = p["predicted_mood"]
                    row["_confidence"] = c
                    items.append(row)

    if not items:
        raise SystemExit("No uncertain neutral rows found. Widen CONF_LO/CONF_HI or check inputs.")

    # diversify by artist
    def artist_from_path(p):
        parts = Path(p).parts
        return parts[-2] if len(parts) >= 2 else "UNKNOWN"

    by_artist = defaultdict(list)
    for it in items:
        it["_artist"] = artist_from_path(it["json_path"])
        by_artist[it["_artist"]].append(it)

    random.Random(RNG_SEED).shuffle(items)
    # round-robin across artists until we reach POOL_SIZE
    pool = []
    buckets = list(by_artist.values())
    idxs = [0]*len(buckets)
    while len(pool) < min(POOL_SIZE, len(items)):
        advanced = False
        for bi, bucket in enumerate(buckets):
            if idxs[bi] < len(bucket):
                pool.append(bucket[idxs[bi]])
                idxs[bi] += 1
                advanced = True
                if len(pool) >= POOL_SIZE: break
        if not advanced: break

    # write pool file with an empty 'human_mood' column for you to fill in
    cols = ["json_path","tempo","mode","tonic","density","_predicted_mood","_confidence","human_mood","notes"]
    with OUT_POOL.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for it in pool:
            w.writerow({
                "json_path": it["json_path"],
                "tempo": it["tempo"],
                "mode": it["mode"],
                "tonic": it["tonic"],
                "density": it["density"],
                "_predicted_mood": it["_predicted_mood"],
                "_confidence": f'{it["_confidence"]:.3f}',
                "human_mood": "",   # <-- you fill this (joyful, angry, content, moody, calm, melancholic)
                "notes": ""
            })

    print(f"✅ Wrote labeling pool: {OUT_POOL}  ({len(pool)} rows)")
    print("Fill 'human_mood' and save as e.g. token_dataset/human_labels.csv")

if __name__ == "__main__":
    main()
