"""
Complete User Behavior and EPARGNE Product Analysis
Analyzes user categories and maps to EPARGNE products
"""

import pandas as pd
import numpy as np
from pathlib import Path

def load_and_prepare_data():
    """Load and prepare data with proper type conversions"""
    print("\n📂 Loading data files...")
    
    # Load product data
    product_df = pd.read_csv('D:/bank-data-visualizer/data/Src_produit.txt', sep=';', encoding='utf-8')
    print(f"✅ Loaded {len(product_df)} products")
    
    # Load savings data
    savings_df = pd.read_csv('D:/bank-data-visualizer/data/Src_objectif_epargne_cmc.txt', sep=';', encoding='utf-8', low_memory=False)
    print(f"✅ Loaded {len(savings_df)} savings records")
    
    # Standardize product codes:
    # Product file has: "013", "014", etc (strings)
    # Savings file has: 13, 14, etc (floats/ints) + some NaNs
    # Solution: Pad savings product codes to 3 digits, remove NaNs
    
    product_df['ch_code_produit'] = product_df['ch_code_produit'].astype(str).str.strip()
    savings_df['ch_code_produit_orig'] = savings_df['ch_code_produit'].copy()
    
    # Convert to string, fill NaNs, then pad to 3 digits
    savings_df['ch_code_produit'] = pd.to_numeric(savings_df['ch_code_produit'], errors='coerce')
    savings_df = savings_df.dropna(subset=['ch_code_produit'])  # Remove NaN product codes
    savings_df['ch_code_produit'] = savings_df['ch_code_produit'].astype(int).astype(str).str.zfill(3)
    
    print(f"✅ Standardized product codes")
    
    return product_df, savings_df


def categorize_users(savings_df):
    """Categorize users into 3 behavior groups"""
    print("\n📊 Analyzing user behavior patterns...")
    
    # Get monthly columns
    monthly_cols = sorted([col for col in savings_df.columns if col.startswith('M_')])
    print(f"✅ Found {len(monthly_cols)} monthly columns")
    
    df = savings_df.copy()
    
    # Convert monthly columns to numeric
    for col in monthly_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calculate metrics
    df['Total_Savings'] = df[monthly_cols].sum(axis=1)
    df['Months_With_Savings'] = (df[monthly_cols] > 0).sum(axis=1)
    df['Has_Value_At_Month_12'] = df['M_12'] > 0
    
    # Categorize into 3 groups
    def categorize(row):
        months_active = row['Months_With_Savings']
        has_month_12 = row['Has_Value_At_Month_12']
        total = row['Total_Savings']
        
        # Category 1: Full year savers (savings in all 12 months)
        if months_active == 12:
            return 'Full Year Savers'
        
        # Category 3: No savings (0 throughout year)
        elif total == 0:
            return 'No Savings'
        
        # Category 2: Partial year savers (3-6 months OR have money at month 12)
        elif (3 <= months_active <= 6) or has_month_12:
            return 'Partial Year Savers'
        
        else:
            return 'Partial Year Savers'
    
    df['User_Category'] = df.apply(categorize, axis=1)
    
    return df


def print_user_summary(df_behavior):
    """Print user category summary"""
    print("\n" + "="*70)
    print("👥 USER BEHAVIOR CATEGORIES")
    print("="*70)
    
    total_users = len(df_behavior)
    categories_list = []
    
    for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
        cat_df = df_behavior[df_behavior['User_Category'] == category]
        count = len(cat_df)
        percentage = (count / total_users * 100) if total_users > 0 else 0
        
        categories_list.append({
            'category': category,
            'count': count,
            'percentage': percentage,
            'total_savings': cat_df['Total_Savings'].sum(),
            'avg_savings': cat_df['Total_Savings'].mean(),
            'avg_months': cat_df['Months_With_Savings'].mean()
        })
        
        print(f"\n📌 {category}")
        print(f"   Users: {count:,} ({percentage:.2f}%)")
        print(f"   Total Savings: {cat_df['Total_Savings'].sum():,.2f}")
        print(f"   Avg per User: {cat_df['Total_Savings'].mean():,.2f}")
        print(f"   Avg Months Active: {cat_df['Months_With_Savings'].mean():.1f}")
    
    print("\n" + "="*70)
    print(f"📊 TOTAL USERS: {total_users:,}")
    print("="*70)
    
    return categories_list


def analyze_epargne_products(product_df, df_behavior):
    """Find EPARGNE products and their user category distribution"""
    print("\n\n🎯 EPARGNE PRODUCT ANALYSIS")
    print("="*70)
    
    # Find EPARGNE products
    epargne_mask = product_df['lib_produit'].str.contains('EPARGNE', case=False, na=False)
    epargne_products = product_df[epargne_mask].copy()
    
    print(f"\n✅ Found {len(epargne_products)} EPARGNE products:\n")
    
    epargne_analysis = []
    
    for idx, product in epargne_products.iterrows():
        product_code = product['ch_code_produit'].strip()
        product_name = product['lib_produit']
        
        # Filter behavior data for this product
        product_data = df_behavior[df_behavior['ch_code_produit'] == product_code]
        
        if len(product_data) == 0:
            continue
        
        total = len(product_data)
        
        print(f"📦 Product Code: {product_code} | {product_name}")
        print(f"   Total Users: {total:,}")
        
        category_breakdown = {}
        for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
            cat_count = len(product_data[product_data['User_Category'] == category])
            cat_pct = (cat_count / total * 100) if total > 0 else 0
            category_breakdown[category] = {
                'count': cat_count,
                'percentage': cat_pct
            }
            print(f"   • {category}: {cat_count:,} ({cat_pct:.2f}%)")
        
        epargne_analysis.append({
            'code': product_code,
            'name': product_name,
            'total_users': total,
            'categories': category_breakdown
        })
        print()
    
    return epargne_analysis


def export_results(df_behavior, categories_list, epargne_analysis):
    """Export analysis results to CSV files"""
    print("\n📤 Exporting results...")
    
    output_dir = Path('D:/bank-data-visualizer/outputs')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export category summary
    summary_data = []
    for cat in categories_list:
        summary_data.append({
            'Category': cat['category'],
            'User_Count': cat['count'],
            'Percentage': f"{cat['percentage']:.2f}%",
            'Total_Savings': f"{cat['total_savings']:,.2f}",
            'Avg_Savings_per_User': f"{cat['avg_savings']:,.2f}",
            'Avg_Months_Active': f"{cat['avg_months']:.1f}"
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_file = output_dir / 'user_categories_summary.csv'
    summary_df.to_csv(summary_file, index=False, encoding='utf-8')
    print(f"✅ Category summary: {summary_file}")
    
    # Export EPARGNE product analysis
    epargne_data = []
    for prod in epargne_analysis:
        epargne_data.append({
            'Product_Code': prod['code'],
            'Product_Name': prod['name'],
            'Total_Users': prod['total_users'],
            'Full_Year_Savers': prod['categories'].get('Full Year Savers', {}).get('count', 0),
            'Full_Year_Savers_Pct': f"{prod['categories'].get('Full Year Savers', {}).get('percentage', 0):.2f}%",
            'Partial_Year_Savers': prod['categories'].get('Partial Year Savers', {}).get('count', 0),
            'Partial_Year_Savers_Pct': f"{prod['categories'].get('Partial Year Savers', {}).get('percentage', 0):.2f}%",
            'No_Savings': prod['categories'].get('No Savings', {}).get('count', 0),
            'No_Savings_Pct': f"{prod['categories'].get('No Savings', {}).get('percentage', 0):.2f}%"
        })
    
    epargne_df = pd.DataFrame(epargne_data)
    epargne_file = output_dir / 'epargne_products_analysis.csv'
    epargne_df.to_csv(epargne_file, index=False, encoding='utf-8')
    print(f"✅ EPARGNE analysis: {epargne_file}")
    
    return summary_file, epargne_file


if __name__ == '__main__':
    try:
        # Load and prepare data
        product_df, savings_df = load_and_prepare_data()
        
        # Categorize users
        df_behavior = categorize_users(savings_df)
        
        # Print user summary
        categories_list = print_user_summary(df_behavior)
        
        # Analyze EPARGNE products
        epargne_analysis = analyze_epargne_products(product_df, df_behavior)
        
        # Export results
        summary_file, epargne_file = export_results(df_behavior, categories_list, epargne_analysis)
        
        print("\n✅ Analysis complete!")
        print(f"\n📊 Results exported to: D:/bank-data-visualizer/outputs/")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
