"""
Preview the corrected Excel file with proper time values
"""

import pandas as pd
from pathlib import Path

output_dir = Path('D:/bank-data-visualizer/outputs')

print("\n" + "="*80)
print("📊 PLATFORM_USAGE_ANALYSIS.xlsx (UPDATED WITH CORRECT TIME VALUES)")
print("="*80)

excel_file = output_dir / 'Platform_Usage_Analysis.xlsx'
xls = pd.ExcelFile(excel_file)

for sheet in xls.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet)
    
    print(f"\n🔹 Sheet: {sheet}")
    print("-" * 80)
    print(df.to_string(index=False))
    print()
