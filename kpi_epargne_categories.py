"""
TASK 1: KPI Analysis for EPARGNE Products Only
Shows 3 categories with their product codes
"""

import pandas as pd
from pathlib import Path

print("\n" + "="*80)
print("📊 KPI ANALYSIS - EPARGNE PRODUCTS ONLY")
print("="*80)

print("\n🔍 STEP 1: Load and filter EPARGNE products")
produits_df = pd.read_csv('D:/bank-data-visualizer/data/Src_produit.txt', sep=';', encoding='utf-8')
epargne_produits = produits_df[produits_df['lib_produit'].str.contains('EPARGNE', case=False, na=False)].copy()

print(f"   ✅ Found {len(epargne_produits)} EPARGNE products")
epargne_codes = epargne_produits['ch_code_produit'].astype(int).tolist()
print(f"   Codes: {epargne_codes}")

print("\n🔍 STEP 2: Load savings data")
savings_df = pd.read_csv('D:/bank-data-visualizer/data/Src_objectif_epargne_cmc.txt', sep=';', encoding='utf-8', low_memory=False)

# Convert product code
savings_df['ch_code_produit'] = pd.to_numeric(savings_df['ch_code_produit'], errors='coerce')
savings_df = savings_df.dropna(subset=['ch_code_produit'])
savings_df['ch_code_produit'] = savings_df['ch_code_produit'].astype(int)

# Convert monthly columns
months_cols = [f'M_{i}' for i in range(1, 13)]
for col in months_cols:
    savings_df[col] = pd.to_numeric(savings_df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

# Filter EPARGNE only
savings_epargne = savings_df[savings_df['ch_code_produit'].isin(epargne_codes)].copy()
print(f"   ✅ EPARGNE records: {len(savings_epargne):,}")

print("\n🔍 STEP 3: Categorize users")
user_data = []

for user_id in savings_epargne['ch_code_client_hashed'].unique():
    user_records = savings_epargne[savings_epargne['ch_code_client_hashed'] == user_id]
    
    # Count months with savings
    months_active = 0
    for month in months_cols:
        if (user_records[month] > 0).any():
            months_active += 1
    
    # Total savings
    total_savings = user_records[months_cols].sum().sum()
    
    # Category
    if months_active == 12:
        category = 'Full Year Savers'
    elif months_active > 0:
        category = 'Partial Year Savers'
    else:
        category = 'No Savings'
    
    user_data.append({
        'user_id': user_id,
        'months_active': months_active,
        'total_savings': total_savings,
        'category': category
    })

users_df = pd.DataFrame(user_data)

print("   User categories:")
for cat in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
    count = (users_df['category'] == cat).sum()
    pct = count / len(users_df) * 100
    print(f"      {cat:25s}: {count:8,d} users ({pct:5.2f}%)")

print("\n🔍 STEP 4: Analyze products by category")
kpi_data = []

for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
    cat_users = set(users_df[users_df['category'] == category]['user_id'].tolist())
    
    # Get products for this category
    cat_savings = savings_epargne[savings_epargne['ch_code_client_hashed'].isin(cat_users)]
    cat_user_count = len(cat_users)
    total_savings_cat = cat_savings[months_cols].sum().sum()
    avg_savings_per_user = total_savings_cat / cat_user_count if cat_user_count > 0 else 0
    
    # Product codes used in this category
    products_in_cat = sorted(cat_savings['ch_code_produit'].unique())
    product_codes_str = ', '.join(map(str, products_in_cat))
    
    # Get product names
    product_names = []
    for code in products_in_cat:
        name = produits_df[produits_df['ch_code_produit'] == code]['lib_produit'].values
        if len(name) > 0:
            product_names.append(name[0][:30])
    
    kpi_data.append({
        'Category': category,
        'User Count': cat_user_count,
        'Percentage': f"{cat_user_count/len(users_df)*100:.2f}%",
        'Total Savings (DZD)': f"{total_savings_cat:,.0f}",
        'Avg per User (DZD)': f"{avg_savings_per_user:,.0f}",
        'Product Codes': product_codes_str,
        'Product Count': len(products_in_cat)
    })

kpi_df = pd.DataFrame(kpi_data)

print("\n   KPI SUMMARY:")
print(kpi_df.to_string(index=False))

print("\n🔍 STEP 5: Detailed product breakdown by category")
product_detail = []

for product_code in sorted(epargne_codes):
    prod_name = produits_df[produits_df['ch_code_produit'] == product_code]['lib_produit'].values[0]
    
    for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
        cat_users = set(users_df[users_df['category'] == category]['user_id'].tolist())
        cat_savings = savings_epargne[savings_epargne['ch_code_client_hashed'].isin(cat_users)]
        
        # Users using this product in this category
        prod_users = cat_savings[cat_savings['ch_code_produit'] == product_code]['ch_code_client_hashed'].unique()
        user_count_prod = len(prod_users)
        
        if user_count_prod > 0:
            # Total savings for this product in this category
            prod_savings = cat_savings[cat_savings['ch_code_produit'] == product_code][months_cols].sum().sum()
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
    prod_name = produits_df[produits_df['ch_code_produit'] == product_code]['lib_produit'].values[0]
    print(f"\n   {str(product_code):>5s} - {prod_name[:45]}")
    for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
        match = product_detail_df[(product_detail_df['Product Code'] == str(product_code)) & 
                                 (product_detail_df['Category'] == category)]
        if len(match) > 0:
            count = match.iloc[0]['User Count']
            print(f"         {category:20s}: {count:6d} users")
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
