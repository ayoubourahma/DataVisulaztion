"""
Optimized EPARGNE products and user behavior analysis
Focuses on 14 EPARGNE products only
Samples 2,500 users per category for detailed analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("\n" + "="*80)
print("🔍 STEP 1: Identify 14 EPARGNE Products")
print("="*80)

# Load product data
produits_df = pd.read_csv('D:/bank-data-visualizer/data/Src_produit.txt', sep=';', encoding='utf-8')
print(f"   Total products in database: {len(produits_df)}")

# Filter for EPARGNE products
epargne_produits = produits_df[produits_df['lib_produit'].str.contains('EPARGNE', case=False, na=False)]
print(f"   ✅ Found {len(epargne_produits)} EPARGNE products")

epargne_codes = epargne_produits['ch_code_produit'].astype(int).tolist()
print(f"   Product codes: {epargne_codes}")

print("\n" + "="*80)
print("🔍 STEP 2: Load and Filter Savings Data (EPARGNE only)")
print("="*80)

# Load savings data
savings_df = pd.read_csv('D:/bank-data-visualizer/data/Src_objectif_epargne_cmc.txt', sep=';', encoding='utf-8', low_memory=False)
print(f"   Total savings records: {len(savings_df):,}")

# Convert product code and monthly data
savings_df['ch_code_produit'] = pd.to_numeric(savings_df['ch_code_produit'], errors='coerce')
savings_df = savings_df.dropna(subset=['ch_code_produit'])
savings_df['ch_code_produit'] = savings_df['ch_code_produit'].astype(int)

# Convert monthly columns to numeric
months_cols = [f'M_{i}' for i in range(1, 13)]
for col in months_cols:
    savings_df[col] = pd.to_numeric(savings_df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

# Filter for EPARGNE products
savings_epargne = savings_df[savings_df['ch_code_produit'].isin(epargne_codes)].copy()
print(f"   ✅ Savings records for EPARGNE: {len(savings_epargne):,}")
print(f"   ✅ Unique users with EPARGNE: {savings_epargne['ch_code_client_hashed'].nunique():,}")

print("\n" + "="*80)
print("🔍 STEP 3: Categorize Users (Vectorized - FAST)")
print("="*80)

# Efficient vectorized calculation
def check_month_has_savings(row):
    for month in months_cols:
        if row[month] > 0:
            return 1
    return 0

# Mark rows with any savings
savings_epargne['has_savings'] = savings_epargne[months_cols].apply(lambda row: (row > 0).any(), axis=1).astype(int)

# Group by user
user_groups = savings_epargne.groupby('ch_code_client_hashed')

# Calculate metrics per user
user_savings = user_groups[months_cols].apply(lambda df: (df > 0).any()).sum(axis=1).reset_index()
user_savings.columns = ['ch_code_client_hashed', 'months_active']

# Total savings
total_savings_data = user_groups[months_cols].sum().sum(axis=1).reset_index()
total_savings_data.columns = ['ch_code_client_hashed', 'total_savings']

user_savings = user_savings.merge(total_savings_data, on='ch_code_client_hashed')

# Categorize
def categorize(months):
    if months == 12:
        return 'Full Year Savers'
    elif months > 0:
        return 'Partial Year Savers'
    else:
        return 'No Savings'

user_savings['category'] = user_savings['months_active'].apply(categorize)

print("   User categories:")
for cat in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
    count = (user_savings['category'] == cat).sum()
    pct = count / len(user_savings) * 100
    print(f"      {cat:25s}: {count:8,d} users ({pct:5.2f}%)")

print("\n" + "="*80)
print("🔍 STEP 4: Sample 2,500 users per category")
print("="*80)

sampled_users_list = []
sampled_data = []
for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
    cat_users = user_savings[user_savings['category'] == category]
    sample_size = min(2500, len(cat_users))
    sampled_idx = np.random.choice(len(cat_users), size=sample_size, replace=False)
    sampled = cat_users.iloc[sampled_idx].copy()
    sampled_data.append(sampled)
    sampled_users_list.extend(sampled['ch_code_client_hashed'].tolist())
    print(f"   {category:25s}: {sample_size:,d} users sampled")

user_sample = pd.concat(sampled_data, ignore_index=True)
print(f"   ✅ Total sampled users: {len(user_sample):,}")

print("\n" + "="*80)
print("🔍 STEP 5: Get activity data for sampled users")
print("="*80)

# Load activity data
activity_df = pd.read_csv('D:/bank-data-visualizer/data/Src_Activité_applicative_realtime.txt', sep=';', encoding='utf-8', low_memory=False)
print(f"   Total activity records: {len(activity_df):,}")

# Convert time
def time_to_seconds(time_str):
    try:
        parts = str(time_str).split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except:
        pass
    return 0

activity_df['duration_seconds'] = activity_df['duree_totale_session'].apply(time_to_seconds)

# Filter for sampled users
activity_sampled = activity_df[activity_df['ch_code_client'].isin(sampled_users_list)].copy()
print(f"   Activity records for sampled: {len(activity_sampled):,}")

# Aggregate per user - simpler approach
activity_agg = activity_sampled.groupby('ch_code_client')['duration_seconds'].agg(['sum', 'count']).reset_index()
activity_agg.columns = ['ch_code_client_hashed', 'total_seconds', 'session_count']
user_activity = activity_agg.copy()
user_activity['total_hours'] = user_activity['total_seconds'] / 3600
user_activity['avg_minutes_per_session'] = user_activity['total_seconds'] / user_activity['session_count'] / 60

print(f"   ✅ Users with activity: {len(user_activity):,}")

print("\n" + "="*80)
print("🔍 STEP 6: Get product codes per user")
print("="*80)

# Get product codes for each user
user_products_data = savings_epargne[savings_epargne['ch_code_client_hashed'].isin(sampled_users_list)]
user_products = user_products_data.groupby('ch_code_client_hashed')['ch_code_produit'].apply(
    lambda x: ', '.join(map(str, sorted(x.unique())))
).reset_index()
user_products.columns = ['ch_code_client_hashed', 'product_codes']

print(f"   ✅ Product codes retrieved")

print("\n" + "="*80)
print("🔍 STEP 7: Combine all user data")
print("="*80)

# Merge all data
user_detail = user_sample[['ch_code_client_hashed', 'total_savings', 'months_active', 'category']].copy()
user_detail = user_detail.merge(user_activity, on='ch_code_client_hashed', how='left')
user_detail = user_detail.merge(user_products, on='ch_code_client_hashed', how='left')

# Fill NaN
user_detail['total_seconds'] = user_detail['total_seconds'].fillna(0)
user_detail['session_count'] = user_detail['session_count'].fillna(0).astype(int)
user_detail['total_hours'] = user_detail['total_hours'].fillna(0)
user_detail['avg_minutes_per_session'] = user_detail['avg_minutes_per_session'].fillna(0)

# Rename and select columns
user_detail = user_detail.rename(columns={
    'ch_code_client_hashed': 'User ID',
    'total_savings': 'Total Savings (DZD)',
    'months_active': 'Months Active',
    'category': 'Category',
    'session_count': 'Sessions',
    'total_hours': 'Total Hours',
    'avg_minutes_per_session': 'Avg Min/Session',
    'product_codes': 'EPARGNE Products'
})

user_detail = user_detail[['User ID', 'Category', 'Months Active', 'Total Savings (DZD)', 
                           'Total Hours', 'Sessions', 'Avg Min/Session', 'EPARGNE Products']]

# Sort
cat_order = {'Full Year Savers': 0, 'Partial Year Savers': 1, 'No Savings': 2}
user_detail['sort_key'] = user_detail['Category'].map(cat_order)
user_detail = user_detail.sort_values(['sort_key', 'Total Hours'], ascending=[True, False]).drop('sort_key', axis=1)

print(f"   ✅ Combined data for {len(user_detail):,} users")

print("\n" + "="*80)
print("🔍 STEP 8: Create KPI Summary")
print("="*80)

kpi_summary = []
for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
    cat_data = user_detail[user_detail['Category'] == category]
    
    kpi_summary.append({
        'Category': category,
        'User Count': len(cat_data),
        'Percentage': f"{len(cat_data)/len(user_detail)*100:.1f}%",
        'Total Savings (DZD)': f"{cat_data['Total Savings (DZD)'].sum():,.0f}",
        'Avg per User (DZD)': f"{cat_data['Total Savings (DZD)'].mean():,.0f}",
        'Total App Hours': f"{cat_data['Total Hours'].sum():,.0f}",
        'Avg per User (Hours)': f"{cat_data['Total Hours'].mean():.2f}",
        'Total Sessions': f"{cat_data['Sessions'].sum():,.0f}",
        'Avg Sessions': f"{cat_data['Sessions'].mean():.1f}",
        'Avg Min/Session': f"{cat_data['Avg Min/Session'].mean():.2f}"
    })

kpi_df = pd.DataFrame(kpi_summary)
print("\n   KPI Summary (EPARGNE Products Only):")
print(kpi_df.to_string(index=False))

print("\n" + "="*80)
print("🔍 STEP 9: Product analysis by category")
print("="*80)

product_analysis = []
epargne_list = sorted(epargne_codes)

for product_code in epargne_list:
    prod_match = produits_df[produits_df['ch_code_produit'] == product_code]
    if len(prod_match) == 0:
        continue
    product_name = prod_match.iloc[0]['lib_produit']
    
    # Users in sample using this product
    users_with_product = savings_epargne[savings_epargne['ch_code_produit'] == product_code]['ch_code_client_hashed'].unique()
    
    for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
        cat_users = set(user_detail[user_detail['Category'] == category]['User ID'].tolist())
        users_in_cat = len([u for u in users_with_product if u in cat_users])
        
        product_analysis.append({
            'Code': str(product_code),
            'Product Name': product_name[:35],
            'Category': category,
            'Count': users_in_cat
        })

product_df = pd.DataFrame(product_analysis)

print("\n   Product Usage Summary:")
for product_code in epargne_list:
    prod_match = produits_df[produits_df['ch_code_produit'] == product_code]
    if len(prod_match) == 0:
        continue
    pname = prod_match.iloc[0]['lib_produit']
    print(f"\n   {str(product_code):>5s} - {pname[:40]}")
    for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
        matching = product_df[(product_df['Code'] == str(product_code)) & (product_df['Category'] == category)]
        if len(matching) > 0:
            count = matching.iloc[0]['Count']
            print(f"         {category:20s}: {count:5d} users")

print("\n" + "="*80)
print("📊 STEP 10: Export to Excel")
print("="*80)

output_dir = Path('D:/bank-data-visualizer/outputs')
excel_file = output_dir / 'EPARGNE_Analysis_Complete.xlsx'

with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    kpi_df.to_excel(writer, sheet_name='KPI Summary', index=False)
    user_detail.to_excel(writer, sheet_name='User Detail', index=False)
    product_df.to_excel(writer, sheet_name='Products by Category', index=False)

print(f"\n✅ Excel file created: {excel_file.name}")
print(f"   📁 Location: {output_dir}")
print(f"\n   📊 Sheets included:")
print(f"      1. KPI Summary - 3 categories with overall metrics")
print(f"      2. User Detail - {len(user_detail):,} sampled users with individual metrics")
print(f"      3. Products by Category - Product usage by category")
print(f"\n✅ ANALYSIS COMPLETE!")
