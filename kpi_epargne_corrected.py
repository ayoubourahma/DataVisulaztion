"""
CORRECTED KPI CALCULATION - Takes CMC into consideration
Categorizes users based on:
1. Account status (CMC: Active, Half-Active, Abandoned)
2. Savings activity (months with savings)
"""
import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 100)
print("CORRECTED KPI CALCULATION - WITH CMC CONSIDERATION")
print("=" * 100)

# Load data
savings = pd.read_csv('data/Src_objectif_epargne_cmc.txt', sep=';', encoding='utf-8')

# Get EPARGNE products
produits = pd.read_csv('data/Src_produit.txt', sep=';', encoding='utf-8')
epargne_mask = produits['lib_produit'].str.contains('EPARGNE', case=False, na=False)
epargne_codes = produits[epargne_mask]['ch_code_produit'].astype(int).tolist()

# Filter for EPARGNE only
savings_epargne = savings[savings['ch_code_produit'].isin(epargne_codes)].copy()

# Convert months to numeric (handle comma decimals)
months = [f'M_{i}' for i in range(1, 13)]
for month in months:
    savings_epargne[month] = pd.to_numeric(
        savings_epargne[month].astype(str).str.replace(',', '.'), 
        errors='coerce'
    ).fillna(0)

print(f"\nTotal EPARGNE records: {len(savings_epargne):,}")
print(f"Unique users: {savings_epargne['ch_code_client_hashed'].nunique():,}")

# Group by user
user_data = []

for user_id, group in savings_epargne.groupby('ch_code_client_hashed'):
    # CMC status: Check if user has NULL CMC or CMC = 0
    has_active_cmc = (group['CMC'].notna() & (pd.to_numeric(group['CMC'].astype(str).str.replace(',', '.'), errors='coerce') > 0)).any()
    has_any_cmc = group['CMC'].notna().any()
    
    # Months with activity (any product with savings > 0)
    months_with_activity = []
    for month in months:
        if (group[month] > 0).any():  # If any product has savings in this month
            months_with_activity.append(month)
    
    num_active_months = len(months_with_activity)
    total_savings = group[months].sum().sum()
    
    # Categorize user
    if has_active_cmc:
        # Account is active (CMC > 0)
        if num_active_months == 12:
            category = "Active Account (Full Year)"
        elif num_active_months > 0:
            category = "Active Account (Partial Year)"
        else:
            category = "Active Account (No Recent Activity)"
    elif has_any_cmc:
        # Has CMC but it's 0 or low
        if num_active_months > 0:
            category = "Half-Active Account"
        else:
            category = "Dormant Account"
    else:
        # NULL CMC - abandoned or new
        if num_active_months > 0:
            category = "New/Abandoned (Has Activity)"
        else:
            category = "Abandoned Account (No Activity)"
    
    user_data.append({
        'user_id': user_id,
        'active_cmc': has_active_cmc,
        'has_cmc': has_any_cmc,
        'months_active': num_active_months,
        'total_savings': total_savings,
        'category': category
    })

users_df = pd.DataFrame(user_data)

print("\n" + "=" * 100)
print("CORRECTED CATEGORIZATION (WITH CMC):")
print("=" * 100)

# Summary by category
for category in sorted(users_df['category'].unique()):
    cat_data = users_df[users_df['category'] == category]
    count = len(cat_data)
    total = cat_data['total_savings'].sum()
    avg = cat_data['total_savings'].mean()
    
    print(f"\n{category}:")
    print(f"  Users: {count:,}")
    print(f"  Total Savings: {total:,.0f} DZD")
    print(f"  Average per User: {avg:,.0f} DZD")

# Grouped summary
print("\n" + "=" * 100)
print("SUMMARY BY ACCOUNT STATUS:")
print("=" * 100)

print("\n👤 ACTIVE ACCOUNTS (CMC > 0):")
active = users_df[users_df['active_cmc']]
print(f"  Total Users: {len(active):,}")
print(f"  Total Savings: {active['total_savings'].sum():,.0f} DZD")
print(f"  - Full Year: {len(active[active['months_active']==12]):,}")
print(f"  - Partial Year: {len(active[(active['months_active']>0) & (active['months_active']<12)]):,}")
print(f"  - No Recent Activity: {len(active[active['months_active']==0]):,}")

print("\n🔶 HALF-ACTIVE ACCOUNTS (CMC = 0 or exists but dormant):")
half_active = users_df[(~users_df['active_cmc']) & (users_df['has_cmc'])]
print(f"  Total Users: {len(half_active):,}")
print(f"  Total Savings: {half_active['total_savings'].sum():,.0f} DZD")
print(f"  - With Activity: {len(half_active[half_active['months_active']>0]):,}")
print(f"  - Without Activity: {len(half_active[half_active['months_active']==0]):,}")

print("\n❌ ABANDONED ACCOUNTS (CMC NULL or No Activity):")
abandoned = users_df[(~users_df['has_cmc'])]
print(f"  Total Users: {len(abandoned):,}")
print(f"  Total Savings: {abandoned['total_savings'].sum():,.0f} DZD")
print(f"  - With Historical Activity: {len(abandoned[abandoned['months_active']>0]):,}")
print(f"  - Never Active: {len(abandoned[abandoned['months_active']==0]):,}")

# Export to Excel
output_file = 'outputs/EPARGNE_KPI_Corrected.xlsx'
Path('outputs').mkdir(exist_ok=True)

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Sheet 1: Summary by category
    summary_data = []
    for category in sorted(users_df['category'].unique()):
        cat_data = users_df[users_df['category'] == category]
        summary_data.append({
            'Category': category,
            'Users': len(cat_data),
            'Total Savings (DZD)': f"{cat_data['total_savings'].sum():,.0f}",
            'Average per User (DZD)': f"{cat_data['total_savings'].mean():,.0f}",
            'Pct of Users': f"{(len(cat_data)/len(users_df)*100):.1f}%"
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    # Sheet 2: All users with details
    export_df = users_df.copy()
    export_df['total_savings'] = export_df['total_savings'].apply(lambda x: f"{x:,.0f}")
    export_df.to_excel(writer, sheet_name='All Users', index=False)

print(f"\n✅ Corrected KPI exported to: {output_file}")
