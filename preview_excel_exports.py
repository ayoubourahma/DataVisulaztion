"""Preview the exported Excel files"""

import pandas as pd

print("\n" + "="*80)
print("📊 EXCEL FILE 1: KPI_Data_Export.xlsx")
print("="*80)

# Read each sheet
xl_file = pd.ExcelFile('D:/bank-data-visualizer/outputs/KPI_Data_Export.xlsx')
print(f"\nSheets in file: {xl_file.sheet_names}\n")

for sheet in xl_file.sheet_names:
    print(f"\n🔹 Sheet: {sheet}")
    print("-" * 80)
    df = pd.read_excel('D:/bank-data-visualizer/outputs/KPI_Data_Export.xlsx', sheet_name=sheet)
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    print(df.head(12).to_string())

print("\n\n" + "="*80)
print("📱 EXCEL FILE 2: Platform_Usage_Analysis.xlsx")
print("="*80)

xl_file2 = pd.ExcelFile('D:/bank-data-visualizer/outputs/Platform_Usage_Analysis.xlsx')
print(f"\nSheets in file: {xl_file2.sheet_names}\n")

for sheet in xl_file2.sheet_names:
    print(f"\n🔹 Sheet: {sheet}")
    print("-" * 80)
    df = pd.read_excel('D:/bank-data-visualizer/outputs/Platform_Usage_Analysis.xlsx', sheet_name=sheet)
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    print(df.to_string())
