"""Quick test of KPI analyzer to verify column fixes"""

import sys
sys.path.insert(0, 'D:/bank-data-visualizer')

from desktop_app.core.data_loader import BankDataLoader
from desktop_app.core.kpi_analyzer import KPIAnalyzer

try:
    print("📂 Loading data...")
    loader = BankDataLoader('D:/bank-data-visualizer/data')
    dataframes = loader.load_all_data()
    print(f"✅ Loaded {len(dataframes)} data files")
    
    print("\n🔍 Initializing KPI Analyzer...")
    analyzer = KPIAnalyzer(dataframes)
    
    print("📊 Running KPI analysis...")
    summary, details, links = analyzer.analyze()
    
    print(f"\n✅ SUCCESS! Generated {len(summary)} product KPIs")
    print("\nTop 5 products:")
    print(summary.head())
    
    print("\n✅ KPI analyzer is working correctly!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
