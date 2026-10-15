"""
TASK 2: User Session Data Analysis
Pick 10,000 users and show their app usage metrics
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("\n" + "="*80)
print("👥 USER SESSION DATA - 10,000 USERS")
print("="*80)

print("\n🔍 STEP 1: Load all users from activity data")
activity_df = pd.read_csv('D:/bank-data-visualizer/data/Src_Activité_applicative_realtime.txt', sep=';', encoding='utf-8', low_memory=False)
print(f"   Total activity records: {len(activity_df):,}")

# Get unique users
unique_users = activity_df['ch_code_client'].unique()
print(f"   Unique users in activity: {len(unique_users):,}")

print("\n🔍 STEP 2: Sample 10,000 users")
sample_size = min(10000, len(unique_users))
sampled_users = np.random.choice(unique_users, size=sample_size, replace=False)
print(f"   ✅ Sampled: {sample_size:,} users")

print("\n🔍 STEP 3: Convert time format HH:MM:SS to seconds")
def time_to_seconds(time_str):
    try:
        parts = str(time_str).split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except:
        pass
    return 0

activity_df['duration_seconds'] = activity_df['duree_totale_session'].apply(time_to_seconds)

print("\n🔍 STEP 4: Get activity data for sampled users")
activity_sampled = activity_df[activity_df['ch_code_client'].isin(sampled_users)].copy()
print(f"   Activity records: {len(activity_sampled):,}")

print("\n🔍 STEP 5: Aggregate per user")
user_activity = activity_sampled.groupby('ch_code_client')['duration_seconds'].agg(['sum', 'count']).reset_index()
user_activity.columns = ['User ID', 'Total Seconds', 'Session Count']
user_activity['Total Hours'] = user_activity['Total Seconds'] / 3600
user_activity['Avg Minutes/Session'] = user_activity['Total Seconds'] / user_activity['Session Count'] / 60

# Select and rename columns
user_activity = user_activity[['User ID', 'Total Hours', 'Session Count', 'Avg Minutes/Session']]

print(f"   ✅ {len(user_activity):,} users with activity data")
print(f"\n   Sample data:")
print(user_activity.head(10).to_string(index=False))

print("\n" + "="*80)
print("📊 STATISTICS")
print("="*80)

print(f"\n   Total Hours (all users): {user_activity['Total Hours'].sum():,.0f}")
print(f"   Average Hours/user: {user_activity['Total Hours'].mean():.2f}")
print(f"   Total Sessions: {user_activity['Session Count'].sum():,.0f}")
print(f"   Average Sessions/user: {user_activity['Session Count'].mean():.1f}")
print(f"   Average Minutes/Session: {user_activity['Avg Minutes/Session'].mean():.2f}")

print("\n" + "="*80)
print("📊 STEP 6: Export to Excel")
print("="*80)

output_dir = Path('D:/bank-data-visualizer/outputs')
user_file = output_dir / 'EPARGNE_Users_Session_Data.xlsx'

with pd.ExcelWriter(user_file, engine='openpyxl') as writer:
    user_activity.to_excel(writer, sheet_name='User Session Data', index=False)

print(f"\n✅ User Session Excel created: {user_file.name}")
print(f"   📁 Location: {output_dir}")
print(f"   📊 Rows: {len(user_activity):,} users")
print(f"\n✅ USER SESSION ANALYSIS COMPLETE!")
