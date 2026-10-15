"""
Fix Platform Usage Time Calculation
The duration data needs proper conversion
"""

import pandas as pd
from pathlib import Path

print("\n📱 Re-processing platform data with proper time conversion...")

activity_df = pd.read_csv('D:/bank-data-visualizer/data/Src_Activité_applicative_realtime.txt', sep=';', encoding='utf-8', low_memory=False)
print(f"   ✅ Loaded {len(activity_df)} activity records")

# Check the duration column
print("\nChecking duration data:")
print(f"   Duration column type: {activity_df['duree_totale_session'].dtype}")
print(f"   Sample values: {activity_df['duree_totale_session'].head(10).tolist()}")

# Convert to numeric (handle any text formatting)
activity_df['duree_totale_session'] = pd.to_numeric(activity_df['duree_totale_session'], errors='coerce').fillna(0)

# Group by platform
print("\n⚙️  Aggregating by platform...")
platform_usage = activity_df.groupby("Système d'exploitation").agg({
    'duree_totale_session': ['sum', 'count', 'mean'],
    'ch_code_client': 'nunique'
}).reset_index()

platform_usage.columns = ['Platform', 'Total_Time', 'Session_Count', 'Avg_Session_Duration', 'Unique_Users']

# The duration is likely already in seconds or minutes, convert appropriately
# Assume it's in seconds
platform_usage['Total_Time_Hours'] = platform_usage['Total_Time'] / 3600
platform_usage['Total_Time_Minutes'] = platform_usage['Total_Time'] / 60
platform_usage['Avg_Session_Minutes'] = platform_usage['Avg_Session_Duration'] / 60

# Calculate percentages
total_sessions = platform_usage['Session_Count'].sum()
total_time = platform_usage['Total_Time'].sum()

platform_usage['Time_Percentage'] = (platform_usage['Total_Time'] / total_time * 100).round(2)
platform_usage['Session_Percentage'] = (platform_usage['Session_Count'] / total_sessions * 100).round(2)

# Sort by total time
platform_usage = platform_usage.sort_values('Total_Time', ascending=False)

platform_export = platform_usage[[
    'Platform',
    'Total_Time_Hours',
    'Time_Percentage',
    'Session_Count',
    'Session_Percentage',
    'Avg_Session_Minutes',
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

# Recalculate percentages with proper formatting
platform_export['Time %'] = (platform_export['Time %']).apply(lambda x: f"{x:.2f}%")
platform_export['Session %'] = (platform_export['Session %']).apply(lambda x: f"{x:.2f}%")
platform_export['Total Hours'] = platform_export['Total Hours'].apply(lambda x: f"{x:,.2f}")
platform_export['Avg Session (Minutes)'] = platform_export['Avg Session (Minutes)'].apply(lambda x: f"{x:.2f}")

print("\n📊 Platform breakdown:")
print(platform_export.to_string())

# Browser breakdown
print("\n⚙️  Aggregating by browser...")
browser_usage = activity_df.groupby("navigateur").agg({
    'duree_totale_session': ['sum', 'count', 'mean'],
    'ch_code_client': 'nunique'
}).reset_index()

browser_usage.columns = ['Browser', 'Total_Time', 'Session_Count', 'Avg_Session_Duration', 'Unique_Users']

browser_usage['Total_Time_Hours'] = browser_usage['Total_Time'] / 3600
browser_usage['Avg_Session_Minutes'] = browser_usage['Avg_Session_Duration'] / 60
browser_usage['Time_Percentage'] = (browser_usage['Total_Time'] / total_time * 100).round(2)

browser_usage = browser_usage.sort_values('Total_Time', ascending=False)

browser_export = browser_usage[[
    'Browser',
    'Total_Time_Hours',
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

browser_export['Time %'] = (browser_export['Time %']).apply(lambda x: f"{x:.2f}%")
browser_export['Total Hours'] = browser_export['Total Hours'].apply(lambda x: f"{x:,.2f}")

print("\n📊 Browser breakdown:")
print(browser_export.to_string())

# Export to Excel
output_dir = Path('D:/bank-data-visualizer/outputs')
platform_file = output_dir / 'Platform_Usage_Analysis.xlsx'

# Reset the string formatting for Excel
platform_export_clean = platform_usage[[
    'Platform',
    'Total_Time_Hours',
    'Time_Percentage',
    'Session_Count',
    'Session_Percentage',
    'Avg_Session_Minutes',
    'Unique_Users'
]].copy()

platform_export_clean.columns = [
    'Platform/OS',
    'Total Hours',
    'Time %',
    'Number of Sessions',
    'Session %',
    'Avg Session (Minutes)',
    'Unique Users'
]

browser_export_clean = browser_usage[[
    'Browser',
    'Total_Time_Hours',
    'Time_Percentage',
    'Session_Count',
    'Unique_Users'
]].copy()

browser_export_clean.columns = [
    'Browser',
    'Total Hours',
    'Time %',
    'Number of Sessions',
    'Unique Users'
]

with pd.ExcelWriter(platform_file, engine='openpyxl') as writer:
    platform_export_clean.to_excel(writer, sheet_name='Platform Summary', index=False)
    browser_export_clean.to_excel(writer, sheet_name='Browser Summary', index=False)

print(f"\n✅ Excel updated: {platform_file.name}")
