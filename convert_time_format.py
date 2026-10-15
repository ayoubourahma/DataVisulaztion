"""
Convert HH:MM:SS time format to hours and minutes
"""

import pandas as pd
from pathlib import Path

print("\n📱 Converting HH:MM:SS time format to hours...")

activity_df = pd.read_csv('D:/bank-data-visualizer/data/Src_Activité_applicative_realtime.txt', sep=';', encoding='utf-8', low_memory=False)
print(f"   ✅ Loaded {len(activity_df)} activity records")

# Convert HH:MM:SS to seconds
def time_to_seconds(time_str):
    if pd.isna(time_str) or time_str == '':
        return 0
    try:
        parts = str(time_str).split(':')
        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            return hours * 3600 + minutes * 60 + seconds
    except:
        pass
    return 0

print("   Converting time format...")
activity_df['duration_seconds'] = activity_df['duree_totale_session'].apply(time_to_seconds)

# Group by platform
print("⚙️  Aggregating by platform...")
platform_usage = activity_df.groupby("Système d'exploitation").agg({
    'duration_seconds': ['sum', 'count', 'mean'],
    'ch_code_client': 'nunique'
}).reset_index()

platform_usage.columns = ['Platform', 'Total_Seconds', 'Session_Count', 'Avg_Seconds', 'Unique_Users']

# Convert to hours and minutes
platform_usage['Total_Hours'] = platform_usage['Total_Seconds'] / 3600
platform_usage['Total_Minutes'] = platform_usage['Total_Seconds'] / 60
platform_usage['Avg_Minutes'] = platform_usage['Avg_Seconds'] / 60

# Calculate percentages
total_seconds = platform_usage['Total_Seconds'].sum()
total_sessions = platform_usage['Session_Count'].sum()

platform_usage['Time_Percentage'] = (platform_usage['Total_Seconds'] / total_seconds * 100).round(2)
platform_usage['Session_Percentage'] = (platform_usage['Session_Count'] / total_sessions * 100).round(2)

# Sort by total time
platform_usage = platform_usage.sort_values('Total_Hours', ascending=False)

print("\n📊 Platform usage by time:")
for idx, row in platform_usage.head(15).iterrows():
    print(f"   {row['Platform']:20s} - {row['Total_Hours']:10.2f} hrs ({row['Time_Percentage']:6.2f}%) - {row['Session_Count']:8d} sessions - {row['Unique_Users']:6d} users")

# Browser breakdown
print("\n⚙️  Aggregating by browser...")
browser_usage = activity_df.groupby("navigateur").agg({
    'duration_seconds': ['sum', 'count', 'mean'],
    'ch_code_client': 'nunique'
}).reset_index()

browser_usage.columns = ['Browser', 'Total_Seconds', 'Session_Count', 'Avg_Seconds', 'Unique_Users']

browser_usage['Total_Hours'] = browser_usage['Total_Seconds'] / 3600
browser_usage['Avg_Minutes'] = browser_usage['Avg_Seconds'] / 60
browser_usage['Time_Percentage'] = (browser_usage['Total_Seconds'] / total_seconds * 100).round(2)

browser_usage = browser_usage.sort_values('Total_Hours', ascending=False)

print("\n📊 Browser usage by time:")
for idx, row in browser_usage.head(15).iterrows():
    print(f"   {row['Browser']:20s} - {row['Total_Hours']:10.2f} hrs ({row['Time_Percentage']:6.2f}%) - {row['Session_Count']:8d} sessions")

# Create export dataframes with proper formatting
platform_export = platform_usage[[
    'Platform',
    'Total_Hours',
    'Time_Percentage',
    'Session_Count',
    'Session_Percentage',
    'Avg_Minutes',
    'Unique_Users'
]].copy()

platform_export.columns = [
    'Platform/OS',
    'Total Hours',
    'Time %',
    'Number of Sessions',
    'Session %',
    'Avg Session (Minutes)',
    'Unique Users'
]

browser_export = browser_usage[[
    'Browser',
    'Total_Hours',
    'Time_Percentage',
    'Session_Count',
    'Unique_Users'
]].copy()

browser_export.columns = [
    'Browser',
    'Total Hours',
    'Time %',
    'Number of Sessions',
    'Unique Users'
]

# Export to Excel
output_dir = Path('D:/bank-data-visualizer/outputs')
platform_file = output_dir / 'Platform_Usage_Analysis.xlsx'

with pd.ExcelWriter(platform_file, engine='openpyxl') as writer:
    platform_export.to_excel(writer, sheet_name='Platform Summary', index=False)
    browser_export.to_excel(writer, sheet_name='Browser Summary', index=False)

print(f"\n✅ Platform Usage Excel created: {platform_file.name}")

# Summary stats
print("\n" + "="*70)
print("📊 SUMMARY")
print("="*70)
print(f"Total session time: {total_seconds/3600:,.2f} hours ({total_seconds/86400:,.2f} days)")
print(f"Total sessions: {total_sessions:,}")
print(f"Average session: {total_seconds/total_sessions/60:.2f} minutes")
print(f"Unique users: {activity_df['ch_code_client'].nunique():,}")
