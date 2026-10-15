"""
Direct Excel Export - KPI Data and Platform Usage
Exports data directly to Excel without running through the UI
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("📊 DIRECT EXCEL EXPORT - KPI & PLATFORM USAGE DATA")
print("="*70)

# Output directory
output_dir = Path('D:/bank-data-visualizer/outputs')
output_dir.mkdir(parents=True, exist_ok=True)

# ============================================================================
# PART 1: KPI DATA WITH PRODUCT CODES
# ============================================================================

print("\n📁 Loading KPI data files...")

# Load products
products_df = pd.read_csv('D:/bank-data-visualizer/data/Src_produit.txt', sep=';', encoding='utf-8')
print(f"   ✅ Loaded {len(products_df)} products")

# Load savings data
savings_df = pd.read_csv('D:/bank-data-visualizer/data/Src_objectif_epargne_cmc.txt', sep=';', encoding='utf-8', low_memory=False)
print(f"   ✅ Loaded {len(savings_df)} savings records")

# Get monthly columns
monthly_cols = sorted([col for col in savings_df.columns if col.startswith('M_')])

# Convert to numeric and standardize product codes
print("\n⚙️  Processing KPI data...")
for col in monthly_cols:
    savings_df[col] = pd.to_numeric(savings_df[col], errors='coerce').fillna(0)

products_df['ch_code_produit'] = products_df['ch_code_produit'].astype(str).str.strip()
savings_df['ch_code_produit_orig'] = savings_df['ch_code_produit'].copy()
savings_df['ch_code_produit'] = pd.to_numeric(savings_df['ch_code_produit'], errors='coerce')
savings_df = savings_df.dropna(subset=['ch_code_produit'])
savings_df['ch_code_produit'] = savings_df['ch_code_produit'].astype(int).astype(str).str.zfill(3)

# Calculate user categories
savings_df['Total_Savings'] = savings_df[monthly_cols].sum(axis=1)
savings_df['Months_With_Savings'] = (savings_df[monthly_cols] > 0).sum(axis=1)
savings_df['Has_Value_At_Month_12'] = savings_df['M_12'] > 0

def categorize(row):
    months_active = row['Months_With_Savings']
    total = row['Total_Savings']
    has_m12 = row['Has_Value_At_Month_12']
    
    if months_active == 12:
        return 'Full Year Savers'
    elif total == 0:
        return 'No Savings'
    elif (3 <= months_active <= 6) or has_m12:
        return 'Partial Year Savers'
    else:
        return 'Partial Year Savers'

savings_df['User_Category'] = savings_df.apply(categorize, axis=1)

# Merge with product info
merged_df = pd.merge(savings_df, products_df, on='ch_code_produit', how='left')

print("   ✅ Data processed and categorized")

# ============================================================================
# Create Excel 1: KPI DATA WITH PRODUCT CODES AND CATEGORIES
# ============================================================================

print("\n📊 Creating KPI Excel file...")

# Sheet 1: Product KPI Summary
kpi_summary = []
for prod_code in merged_df['ch_code_produit'].unique():
    prod_df = merged_df[merged_df['ch_code_produit'] == prod_code]
    prod_name = prod_df['lib_produit'].iloc[0] if 'lib_produit' in prod_df.columns else 'Unknown'
    
    for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
        cat_df = prod_df[prod_df['User_Category'] == category]
        count = len(cat_df)
        percentage = (count / len(prod_df) * 100) if len(prod_df) > 0 else 0
        total_savings = cat_df['Total_Savings'].sum()
        
        kpi_summary.append({
            'Product Code': prod_code,
            'Product Name': prod_name,
            'User Category': category,
            'User Count': count,
            'Percentage': f"{percentage:.2f}%",
            'Total Savings': f"{total_savings:,.2f}",
            'Avg Savings per User': f"{total_savings/count if count > 0 else 0:,.2f}"
        })

kpi_summary_df = pd.DataFrame(kpi_summary)

# Sheet 2: Overall Category Summary
category_summary = []
total_users = len(merged_df)
for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
    cat_df = merged_df[merged_df['User_Category'] == category]
    count = len(cat_df)
    percentage = (count / total_users * 100) if total_users > 0 else 0
    
    category_summary.append({
        'User Category': category,
        'Total Users': count,
        'Percentage': f"{percentage:.2f}%",
        'Total Savings': f"{cat_df['Total_Savings'].sum():,.2f}",
        'Avg per User': f"{cat_df['Total_Savings'].mean():,.2f}",
        'Avg Months Active': f"{cat_df['Months_With_Savings'].mean():.1f}"
    })

category_summary_df = pd.DataFrame(category_summary)

# Sheet 3: All Products with Statistics
all_products = []
for prod_code in sorted(merged_df['ch_code_produit'].unique()):
    prod_df = merged_df[merged_df['ch_code_produit'] == prod_code]
    prod_name = prod_df['lib_produit'].iloc[0] if 'lib_produit' in prod_df.columns else 'Unknown'
    
    all_products.append({
        'Product Code': prod_code,
        'Product Name': prod_name,
        'Total Users': len(prod_df),
        'Total Savings': f"{prod_df['Total_Savings'].sum():,.2f}",
        'Avg Savings': f"{prod_df['Total_Savings'].mean():,.2f}",
        'Full Year %': f"{(len(prod_df[prod_df['User_Category']=='Full Year Savers'])/len(prod_df)*100 if len(prod_df)>0 else 0):.2f}%",
        'Partial Year %': f"{(len(prod_df[prod_df['User_Category']=='Partial Year Savers'])/len(prod_df)*100 if len(prod_df)>0 else 0):.2f}%",
        'No Savings %': f"{(len(prod_df[prod_df['User_Category']=='No Savings'])/len(prod_df)*100 if len(prod_df)>0 else 0):.2f}%"
    })

all_products_df = pd.DataFrame(all_products)

# Export to Excel with multiple sheets
kpi_file = output_dir / 'KPI_Data_Export.xlsx'
with pd.ExcelWriter(kpi_file, engine='openpyxl') as writer:
    category_summary_df.to_excel(writer, sheet_name='Category Summary', index=False)
    all_products_df.to_excel(writer, sheet_name='All Products', index=False)
    kpi_summary_df.to_excel(writer, sheet_name='Product-Category Detail', index=False)

print(f"   ✅ KPI Excel created: {kpi_file.name}")

# ============================================================================
# PART 2: PLATFORM USAGE ANALYSIS
# ============================================================================

print("\n📱 Loading platform usage data...")

activity_df = pd.read_csv('D:/bank-data-visualizer/data/Src_Activité_applicative_realtime.txt', sep=';', encoding='utf-8', low_memory=False)
print(f"   ✅ Loaded {len(activity_df)} activity records")

# Extract platform from 'Système d'exploitation'
print("\n⚙️  Processing platform data...")

activity_df['duree_totale_session'] = pd.to_numeric(activity_df['duree_totale_session'], errors='coerce').fillna(0)

# Group by platform (Système d'exploitation)
platform_usage = activity_df.groupby("Système d'exploitation").agg({
    'duree_totale_session': ['sum', 'count', 'mean'],
    'ch_code_client': 'nunique'
}).reset_index()

platform_usage.columns = ['Platform', 'Total_Time_Seconds', 'Session_Count', 'Avg_Session_Duration', 'Unique_Users']

# Calculate percentages
total_time = platform_usage['Total_Time_Seconds'].sum()
platform_usage['Time_Percentage'] = (platform_usage['Total_Time_Seconds'] / total_time * 100).round(2)
platform_usage['Session_Percentage'] = (platform_usage['Session_Count'] / platform_usage['Session_Count'].sum() * 100).round(2)

# Convert seconds to readable format
platform_usage['Total_Time_Hours'] = (platform_usage['Total_Time_Seconds'] / 3600).round(2)
platform_usage['Avg_Session_Minutes'] = (platform_usage['Avg_Session_Duration'] / 60).round(2)

# Reorder columns
platform_usage_export = platform_usage[[
    'Platform',
    'Total_Time_Hours',
    'Time_Percentage',
    'Session_Count',
    'Session_Percentage',
    'Avg_Session_Minutes',
    'Unique_Users'
]].copy()

platform_usage_export.columns = [
    'Platform',
    'Total Hours Spent',
    'Time %',
    'Number of Sessions',
    'Session %',
    'Avg Session (Minutes)',
    'Unique Users'
]

# Platform breakdown by browser (if available)
browser_usage = activity_df.groupby("navigateur").agg({
    'duree_totale_session': ['sum', 'count', 'mean'],
    'ch_code_client': 'nunique'
}).reset_index()

browser_usage.columns = ['Browser', 'Total_Time_Seconds', 'Session_Count', 'Avg_Session_Duration', 'Unique_Users']
browser_usage['Time_Percentage'] = (browser_usage['Total_Time_Seconds'] / browser_usage['Total_Time_Seconds'].sum() * 100).round(2)
browser_usage['Total_Time_Hours'] = (browser_usage['Total_Time_Seconds'] / 3600).round(2)
browser_usage['Avg_Session_Minutes'] = (browser_usage['Avg_Session_Duration'] / 60).round(2)

browser_usage_export = browser_usage[[
    'Browser',
    'Total_Time_Hours',
    'Time_Percentage',
    'Session_Count',
    'Unique_Users'
]].copy()

browser_usage_export.columns = [
    'Browser',
    'Total Hours Spent',
    'Time %',
    'Number of Sessions',
    'Unique Users'
]

print("   ✅ Platform data processed")

# ============================================================================
# Create Excel 2: PLATFORM USAGE
# ============================================================================

print("\n📊 Creating Platform Usage Excel file...")

platform_file = output_dir / 'Platform_Usage_Analysis.xlsx'
with pd.ExcelWriter(platform_file, engine='openpyxl') as writer:
    platform_usage_export.to_excel(writer, sheet_name='Platform Summary', index=False)
    browser_usage_export.to_excel(writer, sheet_name='Browser Summary', index=False)

print(f"   ✅ Platform Excel created: {platform_file.name}")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "="*70)
print("✅ EXPORT COMPLETE!")
print("="*70)
print(f"\n📊 Two Excel files have been created:\n")
print(f"1️⃣  KPI_Data_Export.xlsx")
print(f"   - Sheet 1: Category Summary (Full Year, Partial, No Savings)")
print(f"   - Sheet 2: All Products (with 14 products)")
print(f"   - Sheet 3: Product-Category Detail")
print(f"\n2️⃣  Platform_Usage_Analysis.xlsx")
print(f"   - Sheet 1: Platform Summary (Operating Systems)")
print(f"   - Sheet 2: Browser Summary")
print(f"\n📁 Location: {output_dir}")
print("="*70)
