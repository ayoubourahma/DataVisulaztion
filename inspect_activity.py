import pandas as pd
import os

# Find the exact filename
data_dir = 'D:/bank-data-visualizer/data'
files = os.listdir(data_dir)
activity_files = [f for f in files if 'ctivit' in f]
print("Activity files found:", activity_files)

for fname in activity_files:
    fpath = os.path.join(data_dir, fname)
    print(f"\n{'='*60}")
    print(f"FILE: {fname}")
    print(f"{'='*60}")
    try:
        df = pd.read_csv(fpath, sep=';', encoding='utf-8', low_memory=False, nrows=3)
    except Exception:
        df = pd.read_csv(fpath, sep=';', encoding='latin-1', low_memory=False, nrows=3)

    print("COLUMNS:")
    for c in df.columns:
        print(f"  {c!r}")
    print("\nSAMPLE ROW 1:")
    for k, v in df.iloc[0].items():
        print(f"  {k!r}: {v!r}")
    print("\nSAMPLE ROW 2:")
    for k, v in df.iloc[1].items():
        print(f"  {k!r}: {v!r}")
    print()
