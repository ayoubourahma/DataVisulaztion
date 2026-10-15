"""
User Behavior Analyzer Module
Analyzes user saving patterns and categorizes them into behavioral groups
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class UserBehaviorAnalyzer:
    """Analyzes user saving behavior and patterns"""
    
    def __init__(self, dataframes: Dict[str, pd.DataFrame]):
        """
        Initialize User Behavior Analyzer
        
        Args:
            dataframes: Dict of loaded dataframes from BankDataLoader
        """
        self.dataframes = dataframes
        self.behavior_data = None
        self.category_stats = {}
        
    def analyze(self) -> Tuple[Dict, pd.DataFrame]:
        """
        Categorize users by savings behavior
        
        Returns:
            Tuple of (category_stats, detailed_behavior_df)
        """
        logger.info("🔍 Starting user behavior analysis...")
        
        savings_df = self.dataframes.get('src_objectif_epargne_cmc')
        
        if savings_df is None:
            logger.error("❌ Savings data file not found")
            return {}, pd.DataFrame()
        
        # Categorize users
        self._categorize_users(savings_df)
        
        logger.info("✅ User behavior analysis complete")
        
        return self.category_stats, self.behavior_data
    
    def _categorize_users(self, df: pd.DataFrame):
        """Categorize users into 3 behavior groups"""
        logger.info("📊 Categorizing user behavior...")
        
        # Get monthly columns
        monthly_cols = sorted([col for col in df.columns if col.startswith('M_')])
        
        if not monthly_cols:
            logger.error("❌ No monthly columns found")
            return
        
        # Create behavior analysis
        df_behavior = df.copy()
        
        # Calculate metrics for each user (row)
        df_behavior['Total_Savings'] = df_behavior[monthly_cols].sum(axis=1)
        df_behavior['Months_With_Savings'] = (df_behavior[monthly_cols] > 0).sum(axis=1)
        df_behavior['Has_Value_At_Month_12'] = df_behavior['M_12'] > 0
        df_behavior['Months_With_Any_Value'] = (df_behavior[monthly_cols] > 0).sum(axis=1)
        
        # Categorize into 3 groups
        def categorize_user(row):
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
            
            # Default to partial if doesn't fit above criteria
            else:
                return 'Partial Year Savers'
        
        df_behavior['User_Category'] = df_behavior.apply(categorize_user, axis=1)
        
        self.behavior_data = df_behavior
        
        # Calculate statistics
        total_users = len(df_behavior)
        
        for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
            cat_data = df_behavior[df_behavior['User_Category'] == category]
            count = len(cat_data)
            percentage = (count / total_users * 100) if total_users > 0 else 0
            
            self.category_stats[category] = {
                'Count': count,
                'Percentage': percentage,
                'Avg_Savings': cat_data['Total_Savings'].mean(),
                'Total_Savings': cat_data['Total_Savings'].sum(),
                'Min_Savings': cat_data['Total_Savings'].min(),
                'Max_Savings': cat_data['Total_Savings'].max(),
                'Avg_Months_Active': cat_data['Months_With_Savings'].mean(),
            }
        
        logger.info(f"✅ Categorized {total_users:,} users into 3 behavior groups")
        
        # Log summary
        for category, stats in self.category_stats.items():
            logger.info(f"  {category}: {stats['Count']:,} users ({stats['Percentage']:.1f}%)")
    
    def get_category_by_product(self) -> Dict[str, Dict]:
        """
        Get category distribution by product
        
        Returns:
            Dict with product codes and their category distribution
        """
        if self.behavior_data is None or self.behavior_data.empty:
            return {}
        
        logger.info("🔗 Analyzing category distribution by product...")
        
        df = self.behavior_data.copy()
        
        # Group by product and category
        product_category = df.groupby(['ch_code_produit', 'User_Category']).size().unstack(fill_value=0)
        
        result = {}
        for product_code in product_category.index:
            total = product_category.loc[product_code].sum()
            result[product_code] = {
                'Total': total,
            }
            
            for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
                if category in product_category.columns:
                    count = product_category.loc[product_code, category]
                    percentage = (count / total * 100) if total > 0 else 0
                    result[product_code][category] = {
                        'Count': count,
                        'Percentage': percentage
                    }
        
        return result
    
    def get_epargne_products_analysis(self, product_df: pd.DataFrame) -> Dict:
        """
        Analyze EPARGNE products and their user categories
        
        Args:
            product_df: DataFrame with product information
            
        Returns:
            Dict with EPARGNE product analysis
        """
        logger.info("🎯 Analyzing EPARGNE products...")
        
        if self.behavior_data is None or self.behavior_data.empty:
            logger.error("❌ Behavior data not available")
            return {}
        
        if product_df is None or product_df.empty:
            logger.error("❌ Product data not available")
            return {}
        
        # Find EPARGNE products
        epargne_mask = product_df['lib_produit'].str.contains('EPARGNE', case=False, na=False)
        epargne_products = product_df[epargne_mask]
        
        logger.info(f"✅ Found {len(epargne_products)} EPARGNE products")
        
        # Get category data for EPARGNE products
        df_merged = pd.merge(
            self.behavior_data,
            product_df[['ch_code_produit', 'lib_produit']],
            on='ch_code_produit',
            how='left'
        )
        
        df_epargne = df_merged[df_merged['ch_code_produit'].isin(epargne_products['ch_code_produit'])]
        
        result = {}
        
        for _, product in epargne_products.iterrows():
            product_code = product['ch_code_produit']
            product_name = product['lib_produit']
            
            product_data = df_epargne[df_epargne['ch_code_produit'] == product_code]
            
            if len(product_data) == 0:
                continue
            
            total = len(product_data)
            
            categories = {}
            for category in ['Full Year Savers', 'Partial Year Savers', 'No Savings']:
                cat_count = len(product_data[product_data['User_Category'] == category])
                cat_pct = (cat_count / total * 100) if total > 0 else 0
                categories[category] = {
                    'Count': cat_count,
                    'Percentage': cat_pct
                }
            
            result[product_code] = {
                'Product Name': product_name,
                'Total Users': total,
                'Categories': categories
            }
        
        return result
    
    def export_analysis(self, output_path: str) -> bool:
        """
        Export user behavior analysis to CSV files
        
        Args:
            output_path: Directory to save exports
            
        Returns:
            True if successful
        """
        try:
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"📤 Exporting user behavior analysis to {output_path}...")
            
            # Export behavior data
            if self.behavior_data is not None and not self.behavior_data.empty:
                # Select relevant columns for export
                export_cols = ['ch_code_produit', 'CLIENT_MARQUE', 'Total_Savings', 
                              'Months_With_Savings', 'User_Category']
                
                # Add available columns
                available_cols = [col for col in export_cols if col in self.behavior_data.columns]
                
                behavior_file = output_path / 'user_behavior_detailed.csv'
                self.behavior_data[available_cols].to_csv(behavior_file, index=False, encoding='utf-8')
                logger.info(f"✅ Behavior data exported: {behavior_file}")
            
            # Export category summary
            if self.category_stats:
                summary_data = []
                for category, stats in self.category_stats.items():
                    summary_data.append({
                        'Category': category,
                        'User Count': stats['Count'],
                        'Percentage': f"{stats['Percentage']:.2f}%",
                        'Avg Savings': f"{stats['Avg_Savings']:.2f}",
                        'Total Savings': f"{stats['Total_Savings']:.2f}",
                        'Avg Months Active': f"{stats['Avg_Months_Active']:.2f}"
                    })
                
                summary_df = pd.DataFrame(summary_data)
                summary_file = output_path / 'user_category_summary.csv'
                summary_df.to_csv(summary_file, index=False, encoding='utf-8')
                logger.info(f"✅ Category summary exported: {summary_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            return False
