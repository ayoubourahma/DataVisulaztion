"""
KPI Analyzer Module
Analyzes Product and Savings Objectives data to generate KPIs
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, List
import logging

logger = logging.getLogger(__name__)


class KPIAnalyzer:
    """Analyzes KPIs from product and savings objectives data"""
    
    def __init__(self, dataframes: Dict[str, pd.DataFrame]):
        """
        Initialize KPI Analyzer
        
        Args:
            dataframes: Dict of loaded dataframes from BankDataLoader
        """
        self.dataframes = dataframes
        self.kpi_data = None
        self.product_savings_merged = None
        self.field_links = {}
        
    def analyze(self) -> Tuple[pd.DataFrame, Dict, Dict]:
        """
        Perform comprehensive KPI analysis
        
        Returns:
            Tuple of (kpi_summary_df, kpi_details, field_links)
        """
        logger.info("🔍 Starting KPI analysis...")
        
        # Get required dataframes
        product_df = self.dataframes.get('src_produit')
        savings_df = self.dataframes.get('src_objectif_epargne_cmc')
        
        if product_df is None or savings_df is None:
            logger.error("❌ Required data files not found")
            return pd.DataFrame(), {}, {}
        
        # Merge datasets
        self._merge_data(product_df, savings_df)
        
        # Identify field links
        self._identify_field_links(product_df, savings_df)
        
        # Calculate KPIs
        kpi_summary = self._calculate_kpi_summary()
        kpi_details = self._calculate_kpi_details()
        
        logger.info("✅ KPI analysis complete")
        
        return kpi_summary, kpi_details, self.field_links
    
    def _merge_data(self, product_df: pd.DataFrame, savings_df: pd.DataFrame):
        """Merge product and savings data on product code"""
        logger.info("🔗 Merging product and savings data...")
        
        # Merge on product code
        merged = pd.merge(
            savings_df,
            product_df,
            on='ch_code_produit',
            how='left'
        )
        
        self.product_savings_merged = merged
        logger.info(f"✅ Merged data: {len(merged):,} records")
    
    def _identify_field_links(self, product_df: pd.DataFrame, savings_df: pd.DataFrame):
        """Identify linked fields between datasets"""
        logger.info("🔍 Identifying linked fields...")
        
        self.field_links = {
            'Primary Link': {
                'Field': 'ch_code_produit',
                'Description': 'Product Code',
                'src_produit': 'Identifier for each product',
                'src_objectif_epargne_cmc': 'Links to product details'
            },
            'Product Fields': {
                'ch_code_produit': 'Product Code (Link Key)',
                'lib_produit': 'Product Label/Name'
            },
            'Savings Fields': {
                'CPT_AGENCE_CODE': 'Branch Code',
                'CLIENT_MARCHE': 'Client Market Segment',
                'CSP': 'Customer Category (Profession)',
                'Segment_NMR': 'Customer Segment',
                'CLIENT_SPEC_LIB': 'Special Client Label',
                'CLT_AGENCE': 'Client Branch',
                'CPT_DATE_OUVERTURE': 'Account Opening Date',
                'CLT_SECTEUR_ACTIVITE': 'Activity Sector',
                'M_1 to M_12': 'Monthly Savings Values',
                'CMC': 'Customer Management Code',
                'ch_chapitre_compte': 'Account Chapter',
                'DT_SITUATION': 'Situation Date'
            },
            'Field Statistics': {
                'Product Records': len(product_df),
                'Savings Records': len(savings_df),
                'Unique Products': product_df['ch_code_produit'].nunique() if 'ch_code_produit' in product_df.columns else 0,
                'Unique Savings Products': savings_df['ch_code_produit'].nunique() if 'ch_code_produit' in savings_df.columns else 0
            }
        }
    
    def _calculate_kpi_summary(self) -> pd.DataFrame:
        """Calculate summary KPIs by product (OPTIMIZED with vectorized operations)"""
        if self.product_savings_merged is None or self.product_savings_merged.empty:
            return pd.DataFrame()
        
        logger.info("📊 Calculating KPI summary (optimized)...")
        
        df = self.product_savings_merged.copy()
        
        # Get monthly columns
        monthly_cols = [col for col in df.columns if col.startswith('M_')]
        
        if not monthly_cols:
            logger.warning("⚠️ No monthly columns found")
            return pd.DataFrame()
        
        # Add monthly totals per row (vectorized)
        df['Monthly_Total'] = df[monthly_cols].sum(axis=1)
        
        # Use vectorized groupby operations (much faster)
        summary = df.groupby('ch_code_produit').agg({
            'lib_produit': 'first',
            'CLIENT_MARCHE': 'nunique',
            'Monthly_Total': ['sum', 'mean', 'max', 'min', 'count']
        }).reset_index()
        
        # Flatten column names
        summary.columns = ['Product Code', 'Product Name', 'Unique Clients', 
                          'Total Savings', 'Avg Monthly', 'Max Month', 'Min Month', 'Total Accounts']
        
        # Calculate per-account metrics (vectorized)
        summary['Savings per Account'] = summary['Total Savings'] / summary['Total Accounts']
        summary['Avg Clients per Account'] = summary['Unique Clients'] / summary['Total Accounts']
        
        # Sort and reorder columns
        summary = summary[['Product Code', 'Product Name', 'Total Accounts', 'Unique Clients',
                          'Total Savings', 'Avg Monthly', 'Max Month', 'Min Month',
                          'Savings per Account', 'Avg Clients per Account']]
        summary = summary.sort_values('Total Savings', ascending=False)
        
        logger.info(f"✅ Generated {len(summary)} product KPIs (fast)")
        
        return summary
    
    def _calculate_kpi_details(self) -> Dict:
        """Calculate detailed KPIs"""
        if self.product_savings_merged is None or self.product_savings_merged.empty:
            return {}
        
        logger.info("📈 Calculating detailed KPIs...")
        
        df = self.product_savings_merged.copy()
        monthly_cols = [col for col in df.columns if col.startswith('M_')]
        
        details = {}
        
        # Overall statistics
        details['Overall'] = {
            'Total Records': len(df),
            'Total Unique Products': df['ch_code_produit'].nunique(),
            'Total Unique Clients': df['CLIENT_MARCHE'].nunique() if 'CLIENT_MARCHE' in df.columns else 0,
        }
        
        if monthly_cols:
            all_monthly = df[monthly_cols].sum()
            details['Overall']['Total Savings All Time'] = all_monthly.sum()
            details['Overall']['Average Monthly Total'] = all_monthly.mean()
            details['Overall']['Highest Month'] = all_monthly.max()
            details['Overall']['Lowest Month'] = all_monthly.min()
            
            # Monthly breakdown
            details['Monthly Trend'] = all_monthly.to_dict()
        
        # By Client Segment
        if 'CLIENT_MARCHE' in df.columns:
            details['By Client Segment'] = {}
            for segment in df['CLIENT_MARCHE'].unique():
                segment_data = df[df['CLIENT_MARCHE'] == segment]
                if monthly_cols:
                    total = segment_data[monthly_cols].sum().sum()
                else:
                    total = 0
                details['By Client Segment'][segment] = {
                    'Records': len(segment_data),
                    'Total Savings': total,
                    'Avg Savings per Account': total / len(segment_data) if len(segment_data) > 0 else 0
                }
        
        # By Activity Sector
        if 'CLT_SECTEUR_ACTIVITE_LIB' in df.columns:
            details['By Activity Sector'] = {}
            for sector in df['CLT_SECTEUR_ACTIVITE_LIB'].unique():
                sector_data = df[df['CLT_SECTEUR_ACTIVITE_LIB'] == sector]
                if monthly_cols:
                    total = sector_data[monthly_cols].sum().sum()
                else:
                    total = 0
                details['By Activity Sector'][str(sector)] = {
                    'Records': len(sector_data),
                    'Total Savings': total,
                    'Avg Savings per Account': total / len(sector_data) if len(sector_data) > 0 else 0
                }
        
        logger.info("✅ Generated detailed KPIs")
        
        return details
    
    def get_top_products(self, n: int = 10) -> pd.DataFrame:
        """Get top N products by savings"""
        if self.kpi_data is None:
            return pd.DataFrame()
        return self.kpi_data.head(n)
    
    def get_monthly_trend(self) -> pd.DataFrame:
        """Get monthly savings trend"""
        if self.product_savings_merged is None:
            return pd.DataFrame()
        
        monthly_cols = [col for col in self.product_savings_merged.columns if col.startswith('M_')]
        if not monthly_cols:
            return pd.DataFrame()
        
        monthly_data = self.product_savings_merged[monthly_cols].sum()
        return pd.DataFrame({
            'Month': [f'Month {i+1}' for i in range(len(monthly_data))],
            'Total Savings': monthly_data.values
        })
    
    def get_segment_distribution(self) -> pd.DataFrame:
        """Get savings distribution by client segment"""
        if self.product_savings_merged is None or 'CLIENT_MARCHE' not in self.product_savings_merged.columns:
            return pd.DataFrame()
        
        monthly_cols = [col for col in self.product_savings_merged.columns if col.startswith('M_')]
        df = self.product_savings_merged.copy()
        
        if monthly_cols:
            df['Total'] = df[monthly_cols].sum(axis=1)
        else:
            df['Total'] = 0
        
        segment_dist = df.groupby('CLIENT_MARCHE')['Total'].agg(['sum', 'count', 'mean']).reset_index()
        segment_dist.columns = ['Segment', 'Total Savings', 'Account Count', 'Avg per Account']
        segment_dist = segment_dist.sort_values('Total Savings', ascending=False)
        
        return segment_dist
    
    def export_kpis(self, output_path: str, include_details: bool = True) -> bool:
        """
        Export KPIs to CSV files
        
        Args:
            output_path: Directory to save exports
            include_details: Include detailed analysis sheets
            
        Returns:
            True if successful
        """
        try:
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"📤 Exporting KPIs to {output_path}...")
            
            # Export summary
            if self.kpi_data is not None and not self.kpi_data.empty:
                summary_file = output_path / 'kpi_summary.csv'
                self.kpi_data.to_csv(summary_file, index=False, encoding='utf-8')
                logger.info(f"✅ Summary exported: {summary_file}")
            
            # Export monthly trend
            monthly_trend = self.get_monthly_trend()
            if not monthly_trend.empty:
                trend_file = output_path / 'kpi_monthly_trend.csv'
                monthly_trend.to_csv(trend_file, index=False, encoding='utf-8')
                logger.info(f"✅ Trend exported: {trend_file}")
            
            # Export segment distribution
            segment_dist = self.get_segment_distribution()
            if not segment_dist.empty:
                segment_file = output_path / 'kpi_segment_distribution.csv'
                segment_dist.to_csv(segment_file, index=False, encoding='utf-8')
                logger.info(f"✅ Segment dist exported: {segment_file}")
            
            # Export field links
            if self.field_links:
                links_file = output_path / 'field_links.txt'
                with open(links_file, 'w', encoding='utf-8') as f:
                    f.write("=== FIELD LINKS BETWEEN DATASETS ===\n\n")
                    for category, details in self.field_links.items():
                        f.write(f"\n{category}:\n")
                        if isinstance(details, dict):
                            for key, value in details.items():
                                f.write(f"  {key}: {value}\n")
                logger.info(f"✅ Field links exported: {links_file}")
            
            logger.info("✅ All KPI exports completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exporting KPIs: {str(e)}")
            return False


def analyze_products_savings(dataframes: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, Dict, Dict]:
    """
    Convenience function to analyze KPIs
    
    Args:
        dataframes: Loaded dataframes
        
    Returns:
        Tuple of (summary, details, field_links)
    """
    analyzer = KPIAnalyzer(dataframes)
    summary, details, links = analyzer.analyze()
    
    # Store for later export
    analyzer.kpi_data = summary
    
    return summary, details, links, analyzer
