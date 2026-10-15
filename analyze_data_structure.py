import pandas as pd
import numpy as np

# Load the savings data
print("=" * 80)
print("ANALYZING SAVINGS DATA STRUCTURE")
print("=" * 80)

savings_sample = pd.read_csv('data/Src_objectif_epargne_cmc.txt', sep=';', encoding='utf-8', nrows=50)

print("\nCOLUMNS:")
print(savings_sample.columns.tolist())

print("\nSAMPLE DATA (First 5 rows):")
print(savings_sample[['ch_code_client_hashed', 'ch_code_produit', 'CMC', 'M_1', 'M_2', 'M_3', 'M_12']].head())

print("\n" + "=" * 80)
print("LOADING FULL DATA FOR ANALYSIS...")
print("=" * 80)

all_savings = pd.read_csv('data/Src_objectif_epargne_cmc.txt', sep=';', encoding='utf-8')
print(f"Total records: {len(all_savings)}")

print("\nCMC COLUMN ANALYSIS:")
print(f"Unique values: {sorted(all_savings['CMC'].dropna().unique())}")
print(f"\nCMC value counts:")
print(all_savings['CMC'].value_counts())
print(f"\nCMC NULL count: {all_savings['CMC'].isnull().sum()}")

print("\n" + "=" * 80)
print("M_1 to M_12 NULL ANALYSIS:")
print("=" * 80)
months = [f'M_{i}' for i in range(1, 13)]
null_counts = {}
zero_counts = {}
for month in months:
    # Convert to numeric to handle commas
    month_data = pd.to_numeric(all_savings[month].astype(str).str.replace(',', '.'), errors='coerce')
    null_counts[month] = all_savings[month].isnull().sum()
    zero_counts[month] = (month_data == 0).sum()

print("\nNULL values per month:")
for month in months[:6]:
    print(f"  {month}: {null_counts[month]:,} NULLs")
print("  ...")

print("\nZERO values per month (sample):")
for month in months[:3]:
    print(f"  {month}: {zero_counts[month]:,} zeros")

print("\n" + "=" * 80)
print("SAMPLE RECORDS WITH DIFFERENT STATES:")
print("=" * 80)

# Records with NULL CMC
null_cmc_sample = all_savings[all_savings['CMC'].isnull()].head(2)
print("\nRecords with NULL CMC:")
print(null_cmc_sample[['ch_code_client_hashed', 'ch_code_produit', 'CMC', 'M_1', 'M_12']].to_string())

# Records with CMC value
has_cmc_sample = all_savings[all_savings['CMC'].notna()].head(2)
print("\n\nRecords with CMC value:")
print(has_cmc_sample[['ch_code_client_hashed', 'ch_code_produit', 'CMC', 'M_1', 'M_12']].to_string())
