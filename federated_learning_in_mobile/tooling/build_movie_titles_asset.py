import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
source = ROOT / "ml-100k" / "u.item"
out_dir = ROOT / "federated_learning_in_mobile" / "assets"
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "movielens_titles.csv"

with source.open("r", encoding="latin-1") as src, out_file.open("w", encoding="utf-8", newline="") as dst:
    writer = csv.writer(dst)
    writer.writerow(["item_id", "title"])
    count = 0
    for line in src:
        parts = line.rstrip("\n").split("|")
        if len(parts) < 2 or not parts[0].isdigit():
            continue
        item_id = int(parts[0]) - 1
        writer.writerow([item_id, parts[1]])
        count += 1

print(f"Wrote {count} movie titles to {out_file}")

