"""
Quick User Behavior Analysis Script
Generates user category analysis and EPARGNE product usage
"""

import pandas as pd
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def load_data():
    """Load the data files"""
    print("\n📂 Loading data files...")
    
    # Use absolute path
    data_dir = Path('D:/bank-data-visualizer/data')
    
    # Load product data (semicolon separator)
    product_file = data_dir / 'Src_produit.txt'
    print(f"   Loading: {product_file}")
    product_df = pd.read_csv(product_file, sep=';', encoding='utf-8')
    print(f"✅ Loaded {len(product_df)} products")
    print(f"   Columns: {product_df.columns.tolist()}")
    
    # Load savings data (semicolon separator)
    savings_file = data_dir / 'Src_objectif_epargne_cmc.txt'
    print(f"   Loading: {savings_file}")
    savings_df = pd.read_csv(savings_file, sep=';', encoding='utf-8', low_memory=False)
    print(f"✅ Loaded {len(savings_df)} savings records")
    
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
    
    # Categorize users
    def categorize(row):
        months_active = row['Months_With_Savings']
        has_month_12 = row['Has_Value_At_Month_12']
        total = row['Total_Savings']
        
        # Full year savers
        if months_active == 12:
            return 'Full Year Savers'
        # No savings
        elif total == 0:
            return 'No Savings'
        # Partial year savers
        elif (3 <= months_active <= 6) or has_month_12:
            return 'Partial Year Savers'
        else:
            return 'Partial Year Savers'
    
    df['User_Category'] = df.apply(categorize, axis=1)
    
    # Generate statistics
    print("\n" + "="*70)
    print("👥 USER BEHAVIOR CATEGORIES")
    print("="*70)
    
    total_users = len(df)
    categories_data = []
    
    for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
        cat_df = df[df['User_Category'] == category]
        count = len(cat_df)
        percentage = (count / total_users * 100) if total_users > 0 else 0
        
        categories_data.append({
            'category': category,
            'count': count,
            'percentage': percentage,
            'df': cat_df,
            'avg_savings': cat_df['Total_Savings'].mean(),
            'total_savings': cat_df['Total_Savings'].sum()
        })
        
        print(f"\n📌 {category}")
        print(f"   Users: {count:,} ({percentage:.2f}%)")
        print(f"   Total Savings: {cat_df['Total_Savings'].sum():,.2f}")
        print(f"   Avg per User: {cat_df['Total_Savings'].mean():,.2f}")
        print(f"   Avg Months Active: {cat_df['Months_With_Savings'].mean():.1f}")
    
    print("\n" + "="*70)
    print(f"📊 TOTAL USERS: {total_users:,}")
    print("="*70)
    
    return df, categories_data


def analyze_epargne_products(product_df, df_behavior):
    """Find EPARGNE products and their user category distribution"""
    print("\n\n🎯 EPARGNE PRODUCT ANALYSIS")
    print("="*70)
    
    # Convert product codes to string for consistency
    product_df['ch_code_produit'] = product_df['ch_code_produit'].astype(str)
    df_behavior['ch_code_produit'] = df_behavior['ch_code_produit'].astype(str)
    
    # Find EPARGNE products
    epargne_mask = product_df['lib_produit'].str.contains('EPARGNE', case=False, na=False)
    epargne_products = product_df[epargne_mask].copy()
    
    print(f"\n✅ Found {len(epargne_products)} EPARGNE products:\n")
    
    # Merge data
    df_merged = pd.merge(
        df_behavior,
        product_df[['ch_code_produit', 'lib_produit']],
        on='ch_code_produit',
        how='left'
    )
    
    epargne_analysis = {}
    
    for idx, product in epargne_products.iterrows():
        product_code = str(product['ch_code_produit'])
        product_name = product['lib_produit']
        
        product_data = df_merged[df_merged['ch_code_produit'] == product_code]
        
        if len(product_data) == 0:
            continue
        
        total = len(product_data)
        
        print(f"📦 Product Code: {product_code} | {product_name}")
        print(f"   Total Users: {total:,}")
        
        for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
            cat_count = len(product_data[product_data['User_Category'] == category])
            cat_pct = (cat_count / total * 100) if total > 0 else 0
            print(f"   • {category}: {cat_count:,} ({cat_pct:.2f}%)")
        
        epargne_analysis[product_code] = {
            'name': product_name,
            'total': total,
            'data': product_data
        }
        print()
    
    return epargne_analysis


if __name__ == '__main__':
    try:
        # Load data
        product_df, savings_df = load_data()
        
        # Categorize users
        df_behavior, categories_data = categorize_users(savings_df)
        
        # Analyze EPARGNE products
        epargne_analysis = analyze_epargne_products(product_df, df_behavior)
        
        print("\n✅ Analysis complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
