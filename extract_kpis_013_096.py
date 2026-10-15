import pandas as pd
from pathlib import Path

print("Loading Savings Data...")
savings_df = pd.read_csv('D:/bank-data-visualizer/data/Src_objectif_epargne_cmc.txt', sep=';', encoding='utf-8', low_memory=False)

# Clean ch_code_produit
savings_df['ch_code_produit'] = pd.to_numeric(savings_df['ch_code_produit'], errors='coerce')
savings_df = savings_df.dropna(subset=['ch_code_produit'])
savings_df['ch_code_produit'] = savings_df['ch_code_produit'].astype(int)

target_products = [13, 96]
df_target = savings_df[savings_df['ch_code_produit'].isin(target_products)].copy()

months_cols = [f'M_{i}' for i in range(1, 13)]
for col in months_cols:
    df_target[col] = pd.to_numeric(df_target[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

df_target['CMC'] = pd.to_numeric(df_target['CMC'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

results = []

for prod in target_products:
    df_prod = df_target[df_target['ch_code_produit'] == prod].copy()
    
    total_accounts = len(df_prod)
    if total_accounts == 0:
        continue
    
    df_prod['months_active'] = (df_prod[months_cols] > 0).sum(axis=1)
    df_prod['is_yearly_saver'] = df_prod['months_active'] == 12
    df_prod['is_partial_saver'] = (df_prod['months_active'] > 0) & (df_prod['months_active'] < 12)
    df_prod['is_inactive'] = (df_prod['months_active'] == 0) & (df_prod['CMC'] == 0)
    
    yearly_count = df_prod['is_yearly_saver'].sum()
    partial_count = df_prod['is_partial_saver'].sum()
    inactive_count = df_prod['is_inactive'].sum()
    
    results.append({
        'Product Code': f"{prod:03d}",
        'Total Accounts': total_accounts,
        'Yearly Saving Accounts (Count)': yearly_count,
        'Yearly Saving Accounts (%)': yearly_count / total_accounts,
        'Partly Saving Accounts (Count)': partial_count,
        'Partly Saving Accounts (%)': partial_count / total_accounts,
        'Inactive/Abandoned Accounts (Count)': inactive_count,
        'Inactive/Abandoned Accounts (%)': inactive_count / total_accounts
    })

df_combined = df_target.copy()
total_accounts = len(df_combined)
df_combined['months_active'] = (df_combined[months_cols] > 0).sum(axis=1)
yearly_count = (df_combined['months_active'] == 12).sum()
partial_count = ((df_combined['months_active'] > 0) & (df_combined['months_active'] < 12)).sum()
inactive_count = ((df_combined['months_active'] == 0) & (df_combined['CMC'] == 0)).sum()

results.append({
    'Product Code': "Combined (013 & 096)",
    'Total Accounts': total_accounts,
    'Yearly Saving Accounts (Count)': yearly_count,
    'Yearly Saving Accounts (%)': yearly_count / total_accounts,
    'Partly Saving Accounts (Count)': partial_count,
    'Partly Saving Accounts (%)': partial_count / total_accounts,
    'Inactive/Abandoned Accounts (Count)': inactive_count,
    'Inactive/Abandoned Accounts (%)': inactive_count / total_accounts
})

results_df = pd.DataFrame(results)

# Format the percentage strings for console output
print_df = results_df.copy()
for col in ['Yearly Saving Accounts (%)', 'Partly Saving Accounts (%)', 'Inactive/Abandoned Accounts (%)']:
    print_df[col] = (print_df[col] * 100).map("{:.2f}%".format)

print("\n" + "="*80)
print(" KPI Results for Products 013 and 096")
print("="*80)
print(print_df.to_string(index=False))

output_dir = Path('D:/bank-data-visualizer/outputs')
output_dir.mkdir(exist_ok=True)
excel_file = output_dir / 'KPI_Products_013_096.xlsx'

print_df.to_excel(excel_file, index=False)
print(f"\n Exported to {excel_file}")
