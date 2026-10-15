"""
Get operations for 10,000 users
List all operations per user separated by /
"""

import pandas as pd
from pathlib import Path

print("\n" + "="*80)
print("📊 USER OPERATIONS ANALYSIS")
print("="*80)

print("\n🔍 STEP 1: Load the 10,000 users from Excel")
output_dir = Path('D:/bank-data-visualizer/outputs')
user_excel = output_dir / 'EPARGNE_Users_Session_Data.xlsx'
users_df = pd.read_excel(user_excel, sheet_name='User Session Data')

user_ids = users_df['User ID'].tolist()
print(f"   ✅ Loaded {len(user_ids):,} users from Excel")

print("\n🔍 STEP 2: Load operation types")
operations_df = pd.read_csv('D:/bank-data-visualizer/data/Src_type_operation.txt', sep=';', encoding='utf-8')
print(f"   ✅ Found {len(operations_df)} operation types")
print(f"   Columns: {operations_df.columns.tolist()}")
print(f"   Sample operations:\n{operations_df.head()}")

# Create operation code to name mapping
if 'ch_code_operation' in operations_df.columns and 'lib_operation' in operations_df.columns:
    op_map = dict(zip(operations_df['ch_code_operation'], operations_df['lib_operation']))
    print(f"   ✅ Operation mapping ready: {len(op_map)} operations")
else:
    print(f"   Columns: {operations_df.columns.tolist()}")

print("\n🔍 STEP 3: Load savings data to get operations")
savings_df = pd.read_csv('D:/bank-data-visualizer/data/Src_objectif_epargne_cmc.txt', sep=';', encoding='utf-8', low_memory=False)
print(f"   ✅ Loaded {len(savings_df):,} savings records")
print(f"   Columns: {savings_df.columns.tolist()}")

print("\n🔍 STEP 4: Get operations for each user")
user_operations = []

for user_id in user_ids[:50]:  # Start with first 50 to test
    # Get all records for this user
    user_records = savings_df[savings_df['ch_code_client_hashed'] == user_id]
    
    if len(user_records) == 0:
        user_operations.append({
            'User ID': user_id,
            'Operations': 'No operations found'
        })
    else:
        # Get unique values that might represent operations
        # Check available columns for operation-like data
        potential_op_cols = [col for col in user_records.columns 
                            if 'operation' in col.lower() or 'chapitre' in col.lower() or 'type' in col.lower()]
        
        ops_set = set()
        for col in potential_op_cols:
            unique_vals = user_records[col].dropna().unique()
            ops_set.update(str(v) for v in unique_vals)
        
        ops_list = sorted(list(ops_set))
        ops_str = ' / '.join(ops_list)
        
        user_operations.append({
            'User ID': user_id,
            'Operations': ops_str
        })

ops_df = pd.DataFrame(user_operations)
print(f"\n   Sample of first 10 users:")
print(ops_df.head(10).to_string(index=False))

print("\n🔍 STEP 5: Analyze all 10k users")
user_operations_all = []

for idx, user_id in enumerate(user_ids):
    if idx % 1000 == 0:
        print(f"   Processing user {idx+1}/{len(user_ids)}")
    
    user_records = savings_df[savings_df['ch_code_client_hashed'] == user_id]
    
    if len(user_records) == 0:
        user_operations_all.append({
            'User ID': user_id,
            'Operations': 'No operations'
        })
    else:
        # Get all potential operation identifiers
        potential_op_cols = [col for col in user_records.columns 
                            if 'operation' in col.lower() or 'chapitre' in col.lower() or 'type' in col.lower()]
        
        ops_set = set()
        for col in potential_op_cols:
            unique_vals = user_records[col].dropna().unique()
            ops_set.update(str(v) for v in unique_vals)
        
        ops_list = sorted(list(ops_set))
        
        # Try to map to operation names if mapping exists
        if 'op_map' in locals():
            ops_names = []
            for op in ops_list:
                if op in op_map:
                    ops_names.append(op_map[op])
                else:
                    ops_names.append(op)
            ops_str = ' / '.join(ops_names)
        else:
            ops_str = ' / '.join(ops_list)
        
        user_operations_all.append({
            'User ID': user_id,
            'Operations': ops_str
        })

ops_all_df = pd.DataFrame(user_operations_all)

print(f"\n✅ Processed all {len(ops_all_df):,} users")
print(f"\nSample of users with operations:")
print(ops_all_df.head(20).to_string(index=False))

print("\n" + "="*80)
print("📊 STEP 6: Export to Excel")
print("="*80)

output_file = output_dir / 'Users_Operations_List.xlsx'
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    ops_all_df.to_excel(writer, sheet_name='User Operations', index=False)

print(f"\n✅ Operations file created: {output_file.name}")
print(f"   📁 Location: {output_dir}")
print(f"   📊 Total users: {len(ops_all_df):,}")
print(f"\n✅ OPERATIONS ANALYSIS COMPLETE!")
