"""
Examine how I calculated the savings and identify the issue
"""

import pandas as pd
import numpy as np

print("="*80)
print("UNDERSTANDING DATA STRUCTURE - DIAGNOSIS")
print("="*80)

print("\n🔍 STEP 1: Load the savings data")
savings_full = pd.read_csv('D:/bank-data-visualizer/data/Src_objectif_epargne_cmc.txt', sep=';', encoding='utf-8', low_memory=False)
print(f"   Total records: {len(savings_full):,}")
print(f"   Unique users: {savings_full['ch_code_client_hashed'].nunique():,}")
print(f"   Columns: {savings_full.columns.tolist()}")

print("\n🔍 STEP 2: Data structure analysis")
sample_user = savings_full['ch_code_client_hashed'].iloc[0]
print(f"   Example user ID: {sample_user}")
user_records = savings_full[savings_full['ch_code_client_hashed'] == sample_user]
print(f"   This user has {len(user_records)} product records")
print("\n   Sample of one user's data:")
print(user_records[['ch_code_client_hashed', 'ch_code_produit', 'M_1', 'M_2', 'M_3', 'M_12']].to_string())

print("\n" + "="*80)
print("HOW I CALCULATED (MY PREVIOUS METHOD):")
print("="*80)

# Explain my method
print("\n1. FILTERED for EPARGNE products only:")
print("   - Found 14 EPARGNE products by lib_produit containing 'EPARGNE'")

produits = pd.read_csv('D:/bank-data-visualizer/data/Src_produit.txt', sep=';', encoding='utf-8')
epargne = produits[produits['lib_produit'].str.contains('EPARGNE', case=False, na=False)]
print(f"   - Result: {len(epargne)} EPARGNE products")

epargne_codes = epargne['ch_code_produit'].astype(int).tolist()
savings_epargne = savings_full[savings_full['ch_code_produit'].isin(epargne_codes)].copy()
print(f"   - Result: {len(savings_epargne):,} records for EPARGNE products")
print(f"   - Unique users in EPARGNE: {savings_epargne['ch_code_client_hashed'].nunique():,}")

print("\n2. CONVERTED monthly columns to numeric:")
months_cols = [f'M_{i}' for i in range(1, 13)]
for col in months_cols:
    savings_epargne[col] = pd.to_numeric(savings_epargne[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

print("   - Replaced commas with periods (European decimal format)")

print("\n3. CATEGORIZED users by 'months active':")
print("   - For each USER, checked if ANY month had savings > 0 in ANY product")

user_groups = savings_epargne.groupby('ch_code_client_hashed')
months_by_user = user_groups[months_cols].apply(lambda df: (df > 0).any()).sum(axis=1)
print(f"   - 'months_active' = count of months with ANY savings")

print("\n4. SUMMED TOTAL SAVINGS:")
total_savings_by_user = user_groups[months_cols].sum().sum(axis=1)
print(f"   - Summed M_1 through M_12 for all products per user")

users_df = pd.DataFrame({
    'user_id': months_by_user.index,
    'months_active': months_by_user.values,
    'total_savings': total_savings_by_user.values
})

print("\n5. CATEGORIZED USERS:")
def categorize(months):
    if months == 12:
        return 'Full Year Savers'
    elif months > 0:
        return 'Partial Year Savers'
    else:
        return 'No Savings'

users_df['category'] = users_df['months_active'].apply(categorize)

print("   - Full Year Savers: months_active == 12")
print("   - Partial Year Savers: 0 < months_active < 12")
print("   - No Savings: months_active == 0")

print("\n" + "="*80)
print("RESULTS FROM MY CALCULATION:")
print("="*80)

for cat in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
    cat_data = users_df[users_df['category'] == cat]
    count = len(cat_data)
    total = cat_data['total_savings'].sum()
    avg = cat_data['total_savings'].mean()
    print(f"\n{cat}:")
    print(f"   Users: {count:,}")
    print(f"   Total Savings: {total:,.0f} DZD")
    print(f"   Average per User: {avg:,.0f} DZD")

print("\n" + "="*80)
print("POSSIBLE ISSUES WITH MY CALCULATION:")
print("="*80)

print("\n❌ Issue 1: Definition of 'months active'")
print("   - I counted if ANY product had savings in a month")
print("   - Bank may want: ALL products, or PRIMARY product only, or something else")

print("\n❌ Issue 2: Decimal handling")
print("   - Values use comma as decimal separator (e.g., '3598,357')")
print("   - I replaced with periods for numeric conversion")
print("   - May have introduced rounding errors")

print("\n❌ Issue 3: Summing method")
print("   - I summed M_1 through M_12 for EACH product row, then summed across products")
print("   - Bank may want different aggregation logic")

print("\n❌ Issue 4: Including zero values")
print("   - I treated '0' and missing/empty same as no savings")
print("   - Bank's definition may differ")

print("\n" + "="*80)
print("TO FIX THIS:")
print("="*80)

print("\n✓ Please clarify:")
print("   1. How should 'months active' be determined?")
print("   2. How should total savings be calculated?")
print("   3. What's the rule for Full Year vs Partial Year vs No Savings?")
print("   4. Should we include/exclude zero values?")
print("   5. Any specific threshold amounts?")
print("   6. Should it be based on total per user or per product?")

print("\n" + "="*80)
