"""
Get operations for 10,000 users (OPTIMIZED - VECTORIZED)
List all operations per user separated by /
"""

import pandas as pd
from pathlib import Path

print("\n" + "="*80)
print("📊 USER OPERATIONS ANALYSIS (OPTIMIZED)")
print("="*80)

print("\n🔍 STEP 1: Load the 10,000 users from Excel")
output_dir = Path('D:/bank-data-visualizer/outputs')
user_excel = output_dir / 'EPARGNE_Users_Session_Data.xlsx'
users_df = pd.read_excel(user_excel, sheet_name='User Session Data')

user_ids_list = users_df['User ID'].tolist()
user_ids_set = set(user_ids_list)
print(f"   ✅ Loaded {len(user_ids_list):,} users")

print("\n🔍 STEP 2: Load savings data")
savings_df = pd.read_csv('D:/bank-data-visualizer/data/Src_objectif_epargne_cmc.txt', sep=';', encoding='utf-8', low_memory=False)
print(f"   ✅ Loaded {len(savings_df):,} records")

print("\n🔍 STEP 3: Filter data for 10k users")
savings_10k = savings_df[savings_df['ch_code_client_hashed'].isin(user_ids_set)].copy()
print(f"   ✅ Filtered to {len(savings_10k):,} records for 10k users")

print("\n🔍 STEP 4: Extract operations (ch_chapitre_compte) for each user")
# Group by user and collect unique operations
user_ops = savings_10k.groupby('ch_code_client_hashed')['ch_chapitre_compte'].apply(
    lambda x: ' / '.join(str(v) for v in sorted(x.dropna().unique()))
).reset_index()

user_ops.columns = ['User ID', 'Operations']

print(f"   ✅ Extracted operations for {len(user_ops):,} users")

print("\n   Sample of users with operations:")
print(user_ops.head(30).to_string(index=False))

print("\n📊 OPERATIONS SUMMARY:")
print(f"   Users with 1 operation: {(user_ops['Operations'].str.count('/') == 0).sum():,}")
print(f"   Users with 2+ operations: {(user_ops['Operations'].str.count('/') > 0).sum():,}")

# Count operations per user
user_ops['Op Count'] = user_ops['Operations'].str.count('/') + 1
print(f"\n   Average operations per user: {user_ops['Op Count'].mean():.2f}")
print(f"   Max operations: {user_ops['Op Count'].max()}")
print(f"   Min operations: {user_ops['Op Count'].min()}")

# Remove the helper column for export
user_ops_export = user_ops[['User ID', 'Operations']].copy()

print("\n" + "="*80)
print("📊 STEP 5: Export to Excel")
print("="*80)

output_file = output_dir / 'Users_Operations_List.xlsx'
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    user_ops_export.to_excel(writer, sheet_name='User Operations', index=False)

print(f"\n✅ Operations file created: {output_file.name}")
print(f"   📁 Location: {output_dir}")
print(f"   📊 Total users: {len(user_ops_export):,}")
print(f"\n✅ OPERATIONS ANALYSIS COMPLETE!")
