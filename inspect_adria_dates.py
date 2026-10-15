import pandas as pd
import os

DATA_DIR = 'D:/bank-data-visualizer/data'
all_files = os.listdir(DATA_DIR)
adria_file = [f for f in all_files if 'adria' in f.lower()][0]
fpath = os.path.join(DATA_DIR, adria_file)

print(f"File: {adria_file}")

df = pd.read_csv(fpath, sep=';', encoding='utf-8', low_memory=False)

print(f"Total rows       : {len(df):,}")
print(f"Columns          : {list(df.columns)}")
print()

# Date column
df['date_jour'] = pd.to_datetime(df['date_jour'], errors='coerce')
print(f"Date range       : {df['date_jour'].min().date()} --> {df['date_jour'].max().date()}")
print(f"Total days span  : {(df['date_jour'].max() - df['date_jour'].min()).days} days")
print(f"Unique days      : {df['date_jour'].nunique()} distinct dates")
print(f"Unique users     : {df['ch_code_client'].nunique():,}")
print()

# DT_SITUATION
print(f"DT_SITUATION values: {df['DT_SITUATION'].unique()}")
print()

# Rows per month
df['month'] = df['date_jour'].dt.to_period('M')
monthly = df.groupby('month').size().reset_index(name='rows')
print("Rows per month:")
print(monthly.to_string(index=False))
