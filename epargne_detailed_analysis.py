"""
Analyze EPARGNE products and user behavior
Focus on 14 EPARGNE products only
Sample 2,500 users per category for detailed analysis
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
print(f"\n   ✅ Found {len(epargne_produits)} EPARGNE products")
print("\n   Product List:")
for idx, row in epargne_produits.iterrows():
    print(f"      {str(row['ch_code_produit']):>5s} - {row['lib_produit']}")

epargne_codes = epargne_produits['ch_code_produit'].astype(int).tolist()
print(f"\n   EPARGNE Product Codes: {epargne_codes}")

print("\n" + "="*80)
print("🔍 STEP 2: Load and Filter Savings Data (EPARGNE only)")
print("="*80)

# Load savings data
savings_df = pd.read_csv('D:/bank-data-visualizer/data/Src_objectif_epargne_cmc.txt', sep=';', encoding='utf-8', low_memory=False)
print(f"   Total savings records: {len(savings_df)}")

# Convert product code to int for matching (handle NaN values)
savings_df['ch_code_produit'] = pd.to_numeric(savings_df['ch_code_produit'], errors='coerce')
savings_df = savings_df.dropna(subset=['ch_code_produit'])
savings_df['ch_code_produit'] = savings_df['ch_code_produit'].astype(int)

# Filter for EPARGNE products only
savings_epargne = savings_df[savings_df['ch_code_produit'].isin(epargne_codes)].copy()
print(f"   ✅ Savings records for EPARGNE products: {len(savings_epargne)}")

# Get unique users in EPARGNE products
unique_users_epargne = savings_epargne['ch_code_client_hashed'].nunique()
print(f"   ✅ Unique users with EPARGNE products: {unique_users_epargne:,}")

print("\n" + "="*80)
print("🔍 STEP 3: Categorize Users (EPARGNE only)")
print("="*80)

# Calculate months active and total savings per user
months_cols = [f'M_{i}' for i in range(1, 13)]

# Convert monthly columns to numeric (handle comma as decimal separator)
for col in months_cols:
    savings_epargne[col] = pd.to_numeric(savings_epargne[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

user_data = []

for user_id in savings_epargne['ch_code_client_hashed'].unique():
    user_records = savings_epargne[savings_epargne['ch_code_client_hashed'] == user_id]
    
    # Count months with savings (any product with non-zero value)
    months_active = 0
    for month in months_cols:
        if (user_records[month] > 0).any():
            months_active += 1
    
    # Total savings across all months and products
    total_savings = user_records[months_cols].sum().sum()
    
    # Categorize
    if months_active == 12:
        category = 'Full Year Savers'
    elif months_active > 0:
        category = 'Partial Year Savers'
    else:
        category = 'No Savings'
    
    user_data.append({
        'ch_code_client_hashed': user_id,
        'months_active': months_active,
        'total_savings': total_savings,
        'category': category
    })

user_savings = pd.DataFrame(user_data)

print("   User categories:")
for cat in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
    count = (user_savings['category'] == cat).sum()
    pct = count / len(user_savings) * 100
    print(f"      {cat:25s}: {count:8,d} users ({pct:5.2f}%)")

print("\n" + "="*80)
print("🔍 STEP 4: Sample 2,500 users per category")
print("="*80)

sampled_users_list = []
for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
    cat_users = user_savings[user_savings['category'] == category]['ch_code_client_hashed'].tolist()
    sample_size = min(2500, len(cat_users))
    sampled = np.random.choice(cat_users, size=sample_size, replace=False)
    sampled_users_list.extend(sampled)
    print(f"   {category:25s}: {sample_size:,d} users sampled")

print(f"   ✅ Total sampled users: {len(sampled_users_list):,}")

print("\n" + "="*80)
print("🔍 STEP 5: Get activity data for sampled users")
print("="*80)

# Load activity data
activity_df = pd.read_csv('D:/bank-data-visualizer/data/Src_Activité_applicative_realtime.txt', sep=';', encoding='utf-8', low_memory=False)
print(f"   Total activity records: {len(activity_df):,}")

# Convert time format HH:MM:SS to seconds
def time_to_seconds(time_str):
    if pd.isna(time_str) or time_str == '':
        return 0
    try:
        parts = str(time_str).split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except:
        pass
    return 0

activity_df['duration_seconds'] = activity_df['duree_totale_session'].apply(time_to_seconds)

# Filter activity for sampled users
activity_sampled = activity_df[activity_df['ch_code_client'].isin(sampled_users_list)].copy()
print(f"   Activity records for sampled users: {len(activity_sampled):,}")

# Aggregate activity per user
user_activity = activity_sampled.groupby('ch_code_client').agg({
    'duration_seconds': 'sum',
    'ch_code_client': 'count'  # number of sessions
}).reset_index()

user_activity.columns = ['ch_code_client_hashed', 'total_seconds', 'session_count']
user_activity['total_hours'] = user_activity['total_seconds'] / 3600
user_activity['avg_minutes_per_session'] = user_activity['total_seconds'] / user_activity['session_count'] / 60

print(f"   ✅ Users with activity data: {len(user_activity):,}")

print("\n" + "="*80)
print("🔍 STEP 6: Get product codes per user (EPARGNE only)")
print("="*80)

# Get product codes for each user (EPARGNE only)
user_products = savings_epargne.groupby('ch_code_client')['ch_code_produit'].apply(lambda x: ', '.join(map(str, sorted(x.unique())))).reset_index()
user_products.columns = ['ch_code_client', 'product_codes']

print(f"   ✅ Product codes retrieved for sampled users")

print("\n" + "="*80)
print("🔍 STEP 7: Combine all user data")
print("="*80)

# Merge all data
user_detail = user_savings[user_savings['ch_code_client'].isin(sampled_users_list)][['ch_code_client', 'total_savings', 'months_active', 'category']].copy()
user_detail = user_detail.merge(user_activity, on='ch_code_client', how='left')
user_detail = user_detail.merge(user_products, on='ch_code_client', how='left')

# Fill NaN values for users with no activity
user_detail['total_seconds'] = user_detail['total_seconds'].fillna(0)
user_detail['session_count'] = user_detail['session_count'].fillna(0)
user_detail['total_hours'] = user_detail['total_hours'].fillna(0)
user_detail['avg_minutes_per_session'] = user_detail['avg_minutes_per_session'].fillna(0)

# Rename columns for export
user_detail = user_detail.rename(columns={
    'ch_code_client_hashed': 'User ID (Hashed)',
    'total_savings': 'Total Savings (DZD)',
    'months_active': 'Months Active',
    'category': 'Category',
    'session_count': 'Session Count',
    'total_hours': 'Total Hours',
    'avg_minutes_per_session': 'Avg Minutes/Session',
    'product_codes': 'EPARGNE Product Codes'
})

# Remove total_seconds for export (keep only hours)
user_detail = user_detail[['User ID (Hashed)', 'Category', 'Months Active', 'Total Savings (DZD)', 
                           'Total Hours', 'Session Count', 'Avg Minutes/Session', 'EPARGNE Product Codes']]

# Sort by category and total hours
category_order = {'Full Year Savers': 0, 'Partial Year Savers': 1, 'No Savings': 2}
user_detail['sort_key'] = user_detail['Category'].map(category_order)
user_detail = user_detail.sort_values(['sort_key', 'Total Hours'], ascending=[True, False]).drop('sort_key', axis=1)

print(f"   Combined detail for {len(user_detail):,} users")
print("\n   Sample of Full Year Savers:")
fys = user_detail[user_detail['Category'] == 'Full Year Savers'].head(5)
for idx, row in fys.iterrows():
    print(f"      {row['User ID (Hashed)'][:20]}... | {row['Category']:20s} | Savings: {row['Total Savings (DZD)']:12,.0f} | Hours: {row['Total Hours']:8.1f} | Sessions: {row['Session Count']:5.0f}")

print("\n" + "="*80)
print("🔍 STEP 8: Create KPI summary for EPARGNE products")
print("="*80)

# KPI by category for EPARGNE products
kpi_summary = []
for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
    cat_data = user_detail[user_detail['Category'] == category]
    kpi_summary.append({
        'Category': category,
        'User Count': len(cat_data),
        'Percentage': f"{len(cat_data)/len(user_detail)*100:.2f}%",
        'Total Savings (DZD)': cat_data['Total Savings (DZD)'].sum(),
        'Avg Savings per User': cat_data['Total Savings (DZD)'].mean(),
        'Total App Hours': cat_data['Total Hours'].sum(),
        'Avg App Hours per User': cat_data['Total Hours'].mean(),
        'Total Sessions': cat_data['Session Count'].sum(),
        'Avg Sessions per User': cat_data['Session Count'].mean(),
        'Avg Minutes per Session': cat_data['Avg Minutes/Session'].mean()
    })

kpi_df = pd.DataFrame(kpi_summary)
print("\n   KPI Summary (EPARGNE Products Only):")
for idx, row in kpi_df.iterrows():
    print(f"\n   {row['Category']}:")
    print(f"      Users: {row['User Count']:,} ({row['Percentage']})")
    print(f"      Total Savings: {row['Total Savings (DZD)']:,.0f} DZD")
    print(f"      Avg per User: {row['Avg Savings per User']:,.0f} DZD")
    print(f"      Total App Hours: {row['Total App Hours']:,.0f}")
    print(f"      Avg App Hours per User: {row['Avg App Hours per User']:.2f}")
    print(f"      Total Sessions: {row['Total Sessions']:,.0f}")
    print(f"      Avg Sessions per User: {row['Avg Sessions per User']:.1f}")
    print(f"      Avg Minutes per Session: {row['Avg Minutes per Session']:.2f}")

print("\n" + "="*80)
print("🔍 STEP 9: Product-level analysis (EPARGNE only)")
print("="*80)

# Analyze which EPARGNE products users are using by category
product_analysis = []
for product_code in sorted(epargne_codes):
    product_name = produits_df[produits_df['ch_code_produit'] == product_code]['lib_produit'].values[0]
    
    # Users using this product in our sample
    users_with_product = savings_epargne[savings_epargne['ch_code_produit'] == product_code]['ch_code_client_hashed'].unique()
    
    # Count by category
    for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
        cat_users = set(user_detail[user_detail['Category'] == category]['User ID (Hashed)'].tolist())
        users_in_cat = len([u for u in users_with_product if u in cat_users])
        
        product_analysis.append({
            'Product Code': str(product_code),
            'Product Name': product_name,
            'Category': category,
            'User Count': users_in_cat
        })

product_df = pd.DataFrame(product_analysis)

print("\n   EPARGNE Products by Category (Sampled Users):")
for product_code in sorted(epargne_codes):
    pname = produits_df[produits_df['ch_code_produit'] == product_code]['lib_produit'].values[0]
    print(f"\n   {str(product_code):>5s} - {pname}")
    for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
        count = product_df[(product_df['Product Code'] == str(product_code)) & (product_df['Category'] == category)]['User Count'].values[0]
        print(f"         {category:25s}: {count:6,d} users")

print("\n" + "="*80)
print("📊 STEP 10: Export to Excel")
print("="*80)

output_dir = Path('D:/bank-data-visualizer/outputs')
excel_file = output_dir / 'EPARGNE_Analysis_Complete.xlsx'

with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    kpi_df.to_excel(writer, sheet_name='KPI Summary', index=False)
    user_detail.to_excel(writer, sheet_name='User Detail (Sample)', index=False)
    product_df.to_excel(writer, sheet_name='Products by Category', index=False)

print(f"\n   ✅ Excel file created: {excel_file.name}")
print(f"   📁 Location: {output_dir}")
print(f"\n   Sheets:")
print(f"      1. KPI Summary - Overall metrics by category")
print(f"      2. User Detail (Sample) - {len(user_detail):,} individual users with time/sessions/savings")
print(f"      3. Products by Category - How many users per EPARGNE product per category")
print(f"\n✅ ANALYSIS COMPLETE!")
