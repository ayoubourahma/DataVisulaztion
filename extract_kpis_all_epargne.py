"""
Fixed KPI Extraction for all EPARGNE products + product 096.

Bug fix vs export_excel_direct.py:
  - Monthly values use French locale format ("3598,357" with comma as decimal separator)
  - pd.to_numeric() without str.replace(',','.') silently coerces them to 0
  - This caused users to appear in BOTH 'Partial' and 'No Savings' at the same time
    making percentages exceed 100%

Categories are mutually exclusive and exhaustive (always sum to 100%):
  - Full Year Savers     : savings > 0 in ALL 12 months
  - Partial Year Savers  : savings > 0 in at least 1 month but not all 12
  - Inactive/Abandoned   : savings = 0 in ALL 12 months AND CMC is null or zero

Note: Product 096 (COMPTE CARTE IDDIKHAR) is included explicitly because its
name does not contain 'EPARGNE' but it was requested for analysis.
"""

import pandas as pd
from pathlib import Path

print("=" * 70)
print("KPI EXTRACTION - ALL EPARGNE PRODUCTS (FIXED)")
print("=" * 70)

# ---------------------------------------------------------------------------
# 1. Load product reference
# ---------------------------------------------------------------------------
print("\n[1] Loading product reference...")
products_df = pd.read_csv(
    'D:/bank-data-visualizer/data/Src_produit.txt',
    sep=';', encoding='utf-8'
)

# Products to analyse: all EPARGNE-named products + 096 explicitly
epargne_by_name = products_df[
    products_df['lib_produit'].str.contains('EPARGNE', case=False, na=False)
].copy()
epargne_codes_by_name = epargne_by_name['ch_code_produit'].astype(str).str.strip().str.zfill(3).tolist()

# Force-include 096
target_codes = sorted(set(epargne_codes_by_name + ['096']))

# Build code->name lookup from full product table
products_df['_code'] = products_df['ch_code_produit'].astype(str).str.strip().str.zfill(3)
code_to_name = dict(zip(products_df['_code'], products_df['lib_produit']))

print(f"   EPARGNE products by name : {epargne_codes_by_name}")
print(f"   Target products (+ 096)  : {target_codes}")

# ---------------------------------------------------------------------------
# 2. Load savings data
# ---------------------------------------------------------------------------
print("\n[2] Loading savings data...")
savings_df = pd.read_csv(
    'D:/bank-data-visualizer/data/Src_objectif_epargne_cmc.txt',
    sep=';', encoding='utf-8', low_memory=False
)
print(f"   Total rows: {len(savings_df):,}")

# ---------------------------------------------------------------------------
# 3. Parse monthly columns correctly (comma-decimal fix)
# ---------------------------------------------------------------------------
print("\n[3] Parsing monthly columns (fixing comma-decimal format)...")
months_cols = [f'M_{i}' for i in range(1, 13)]
for col in months_cols:
    savings_df[col] = pd.to_numeric(
        savings_df[col].astype(str).str.replace(',', '.', regex=False),
        errors='coerce'
    ).fillna(0)

# CMC: keep NaN as truly missing
savings_df['CMC'] = pd.to_numeric(
    savings_df['CMC'].astype(str).str.replace(',', '.', regex=False),
    errors='coerce'
)

# Standardise product code
savings_df['ch_code_produit'] = pd.to_numeric(savings_df['ch_code_produit'], errors='coerce')
savings_df = savings_df.dropna(subset=['ch_code_produit'])
savings_df['ch_code_produit'] = savings_df['ch_code_produit'].astype(int).astype(str).str.zfill(3)

# Filter to target products
df_target = savings_df[savings_df['ch_code_produit'].isin(target_codes)].copy()
print(f"   Target product rows  : {len(df_target):,}")
print(f"   Unique client IDs    : {df_target['ch_code_client_hashed'].nunique():,}")

# ---------------------------------------------------------------------------
# 4. Compute months_active and assign category (mutually exclusive)
# ---------------------------------------------------------------------------
print("\n[4] Categorising accounts...")

df_target['months_active']  = (df_target[months_cols] > 0).sum(axis=1)
df_target['total_savings']  = df_target[months_cols].sum(axis=1)
df_target['cmc_is_null']    = df_target['CMC'].isna() | (df_target['CMC'] == 0)

def categorise(row):
    if row['months_active'] == 12:
        return 'Full Year Savers'
    elif row['months_active'] > 0:
        return 'Partial Year Savers'
    else:
        if row['cmc_is_null']:
            return 'Inactive/Abandoned'
        else:
            return 'Inactive (0 savings, CMC present)'

df_target['category'] = df_target.apply(categorise, axis=1)

# ---------------------------------------------------------------------------
# 5. Build per-product KPI summary (one row per product, no combining)
# ---------------------------------------------------------------------------
print("\n[5] Building KPI summary per product...")

kpi_rows = []
for code in target_codes:
    prod = df_target[df_target['ch_code_produit'] == code]
    total = len(prod)
    if total == 0:
        print(f"   WARNING: No data found for product {code} — skipping")
        continue

    full_year = (prod['category'] == 'Full Year Savers').sum()
    partial   = (prod['category'] == 'Partial Year Savers').sum()
    inactive  = (prod['category'] == 'Inactive/Abandoned').sum()
    inactive_cmc = (prod['category'] == 'Inactive (0 savings, CMC present)').sum()
    all_inactive = inactive + inactive_cmc

    # Sanity check — must always be 100%
    assert full_year + partial + all_inactive == total, \
        f"Category counts do not sum to total for product {code}"

    kpi_rows.append({
        'Product Code':                       code,
        'Product Name':                       code_to_name.get(code, 'Unknown'),
        'Total Accounts':                     total,
        'Full Year Savers (Count)':           int(full_year),
        'Full Year Savers (%)':               f"{full_year / total * 100:.2f}%",
        'Partial Year Savers (Count)':        int(partial),
        'Partial Year Savers (%)':            f"{partial / total * 100:.2f}%",
        'Inactive/Abandoned (Count)':         int(all_inactive),
        'Inactive/Abandoned (%)':             f"{all_inactive / total * 100:.2f}%",
        '  - of which: null CMC (Count)':     int(inactive),
        '  - of which: CMC present (Count)':  int(inactive_cmc),
    })

kpi_df = pd.DataFrame(kpi_rows)

# ---------------------------------------------------------------------------
# 6. Print results to console
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("KPI RESULTS PER PRODUCT")
print("=" * 70)
for _, row in kpi_df.iterrows():
    total = row['Total Accounts']
    pct_sum = (
        float(row['Full Year Savers (%)'].rstrip('%')) +
        float(row['Partial Year Savers (%)'].rstrip('%')) +
        float(row['Inactive/Abandoned (%)'].rstrip('%'))
    )
    print(f"\n  [{row['Product Code']}] {row['Product Name']}")
    print(f"    Total Accounts      : {total:,}")
    print(f"    Full Year Savers    : {row['Full Year Savers (Count)']:,}  ({row['Full Year Savers (%)']})")
    print(f"    Partial Year Savers : {row['Partial Year Savers (Count)']:,}  ({row['Partial Year Savers (%)']})")
    print(f"    Inactive/Abandoned  : {row['Inactive/Abandoned (Count)']:,}  ({row['Inactive/Abandoned (%)']})")
    print(f"      - null CMC        : {row['  - of which: null CMC (Count)']:,}")
    print(f"      - CMC present     : {row['  - of which: CMC present (Count)']:,}")
    print(f"    [CHECK] %s sum      : {pct_sum:.2f}%  (must be 100.00%)")

# ---------------------------------------------------------------------------
# 7. Export to Excel — each product separately, no combined rows
# ---------------------------------------------------------------------------
print("\n[7] Exporting to Excel...")

output_dir = Path('D:/bank-data-visualizer/outputs')
output_dir.mkdir(exist_ok=True)
excel_file = output_dir / 'KPI_All_EPARGNE_Products_FIXED.xlsx'

with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:

    # Sheet 1: KPI summary — all products, one row each
    kpi_df.to_excel(writer, sheet_name='KPI Summary (All Products)', index=False)

    # Sheet 2: Only products 013 and 096, each on its own row
    focus_kpi = kpi_df[kpi_df['Product Code'].isin(['013', '096'])].copy()
    focus_kpi.to_excel(writer, sheet_name='Focus 013 and 096', index=False)

    # Sheet 3: Raw account-level data for product 013
    raw_cols = (
        ['ch_code_produit', 'ch_code_client_hashed', 'Id_compte_hashed',
         'CMC', 'months_active', 'total_savings', 'category']
        + months_cols
    )
    raw_cols = [c for c in raw_cols if c in df_target.columns]

    raw_013 = df_target[df_target['ch_code_produit'] == '013'][raw_cols].copy()
    raw_013 = raw_013.rename(columns={
        'ch_code_produit': 'Product Code',
        'ch_code_client_hashed': 'Client ID',
        'Id_compte_hashed': 'Account ID',
        'months_active': 'Months With Savings',
        'total_savings': 'Total Savings (DZD)',
        'category': 'Category',
    })
    raw_013.to_excel(writer, sheet_name='Raw Accounts - 013', index=False)

    # Sheet 4: Raw account-level data for product 096
    raw_096 = df_target[df_target['ch_code_produit'] == '096'][raw_cols].copy()
    raw_096 = raw_096.rename(columns={
        'ch_code_produit': 'Product Code',
        'ch_code_client_hashed': 'Client ID',
        'Id_compte_hashed': 'Account ID',
        'months_active': 'Months With Savings',
        'total_savings': 'Total Savings (DZD)',
        'category': 'Category',
    })
    raw_096.to_excel(writer, sheet_name='Raw Accounts - 096', index=False)

print(f"\n  Exported: {excel_file}")
print("\n  Sheets:")
print("    1. KPI Summary (All Products)  - one row per product, all EPARGNE + 096")
print("    2. Focus 013 and 096           - only products 013 and 096, separate rows")
print("    3. Raw Accounts - 013          - account-level detail for 013")
print("    4. Raw Accounts - 096          - account-level detail for 096")
print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
