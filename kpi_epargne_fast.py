"""
TASK 1 (OPTIMIZED): KPI Analysis for EPARGNE Products Only
Vectorized for speed
"""

import pandas as pd
from pathlib import Path

print("\n" + "="*80)
print("📊 KPI ANALYSIS - EPARGNE PRODUCTS ONLY")
print("="*80)

print("\n🔍 STEP 1: Load EPARGNE products")
produits_df = pd.read_csv('D:/bank-data-visualizer/data/Src_produit.txt', sep=';', encoding='utf-8')
epargne_produits = produits_df[produits_df['lib_produit'].str.contains('EPARGNE', case=False, na=False)].copy()

epargne_codes = epargne_produits['ch_code_produit'].astype(int).tolist()
print(f"   ✅ {len(epargne_produits)} EPARGNE products: {epargne_codes}")

print("\n🔍 STEP 2: Load and filter savings data")
savings_df = pd.read_csv('D:/bank-data-visualizer/data/Src_objectif_epargne_cmc.txt', sep=';', encoding='utf-8', low_memory=False)

# Convert product code and monthly data
savings_df['ch_code_produit'] = pd.to_numeric(savings_df['ch_code_produit'], errors='coerce')
savings_df = savings_df.dropna(subset=['ch_code_produit'])
savings_df['ch_code_produit'] = savings_df['ch_code_produit'].astype(int)

months_cols = [f'M_{i}' for i in range(1, 13)]
for col in months_cols:
    savings_df[col] = pd.to_numeric(savings_df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

savings_epargne = savings_df[savings_df['ch_code_produit'].isin(epargne_codes)].copy()
print(f"   ✅ {len(savings_epargne):,} EPARGNE records")
print(f"   ✅ {savings_epargne['ch_code_client_hashed'].nunique():,} unique users")

print("\n🔍 STEP 3: Categorize users (vectorized)")
# Check if month has any savings
def has_savings(months_data):
    return (months_data > 0).any()

# Count months active per user
user_groups = savings_epargne.groupby('ch_code_client_hashed')
months_by_user = user_groups[months_cols].apply(lambda df: (df > 0).any()).sum(axis=1)
total_savings_by_user = user_groups[months_cols].sum().sum(axis=1)

users_df = pd.DataFrame({
    'user_id': months_by_user.index,
    'months_active': months_by_user.values,
    'total_savings': total_savings_by_user.values
})

# Categorize
def categorize(months):
    if months == 12:
        return 'Full Year Savers'
    elif months > 0:
        return 'Partial Year Savers'
    else:
        return 'No Savings'

users_df['category'] = users_df['months_active'].apply(categorize)

print("   User categories:")
for cat in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
    count = (users_df['category'] == cat).sum()
    pct = count / len(users_df) * 100
    print(f"      {cat:25s}: {count:8,d} users ({pct:5.2f}%)")

print("\n🔍 STEP 4: Build KPI summary")
kpi_data = []

for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
    cat_users_set = set(users_df[users_df['category'] == category]['user_id'].tolist())
    cat_savings = savings_epargne[savings_epargne['ch_code_client_hashed'].isin(cat_users_set)]
    
    cat_user_count = len(cat_users_set)
    total_savings_cat = cat_savings[months_cols].sum().sum()
    avg_savings = total_savings_cat / cat_user_count if cat_user_count > 0 else 0
    
    # Get unique product codes
    products_in_cat = sorted(cat_savings['ch_code_produit'].unique())
    product_codes_str = ', '.join(map(str, products_in_cat))
    
    kpi_data.append({
        'Category': category,
        'User Count': cat_user_count,
        'Percentage': f"{cat_user_count/len(users_df)*100:.2f}%",
        'Total Savings (DZD)': f"{total_savings_cat:,.0f}",
        'Avg per User (DZD)': f"{avg_savings:,.0f}",
        'Product Codes': product_codes_str,
        'Product Count': len(products_in_cat)
    })

kpi_df = pd.DataFrame(kpi_data)

print("\n   KPI SUMMARY:")
print(kpi_df.to_string(index=False))

print("\n🔍 STEP 5: Detailed product breakdown by category")
product_detail = []

for product_code in sorted(epargne_codes):
    prod_row = produits_df[produits_df['ch_code_produit'] == product_code]
    if len(prod_row) == 0:
        continue
    prod_name = prod_row.iloc[0]['lib_produit']
    
    for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
        cat_users_set = set(users_df[users_df['category'] == category]['user_id'].tolist())
        cat_savings = savings_epargne[savings_epargne['ch_code_client_hashed'].isin(cat_users_set)]
        
        prod_cat_savings = cat_savings[cat_savings['ch_code_produit'] == product_code]
        user_count_prod = prod_cat_savings['ch_code_client_hashed'].nunique()
        
        if user_count_prod > 0:
            prod_savings = prod_cat_savings[months_cols].sum().sum()
            avg_per_user_prod = prod_savings / user_count_prod
            
            product_detail.append({
                'Product Code': str(product_code),
                'Product Name': prod_name[:40],
                'Category': category,
                'User Count': user_count_prod,
                'Total Savings (DZD)': f"{prod_savings:,.0f}",
                'Avg per User (DZD)': f"{avg_per_user_prod:,.0f}"
            })

product_detail_df = pd.DataFrame(product_detail)

print("\n   PRODUCTS BY CATEGORY:")
for product_code in sorted(epargne_codes):
    prod_row = produits_df[produits_df['ch_code_produit'] == product_code]
    if len(prod_row) == 0:
        continue
    prod_name = prod_row.iloc[0]['lib_produit']
    print(f"\n   {str(product_code):>5s} - {prod_name[:45]}")
    for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
        match = product_detail_df[(product_detail_df['Product Code'] == str(product_code)) & 
                                 (product_detail_df['Category'] == category)]
        if len(match) > 0:
            count = match.iloc[0]['User Count']
            print(f"         {category:20s}: {count:6,d} users")
        else:
            print(f"         {category:20s}: {0:6d} users")

print("\n" + "="*80)
print("📊 STEP 6: Export to Excel")
print("="*80)

output_dir = Path('D:/bank-data-visualizer/outputs')
kpi_file = output_dir / 'EPARGNE_KPI_Categories.xlsx'

with pd.ExcelWriter(kpi_file, engine='openpyxl') as writer:
    kpi_df.to_excel(writer, sheet_name='Category Summary', index=False)
    product_detail_df.to_excel(writer, sheet_name='Products by Category', index=False)

print(f"\n✅ KPI Excel created: {kpi_file.name}")
print(f"   📁 Location: {output_dir}")
print(f"\n   Sheets:")
print(f"      1. Category Summary - 3 categories with products")
print(f"      2. Products by Category - Each product's usage by category")
print(f"\n✅ KPI ANALYSIS COMPLETE!")
