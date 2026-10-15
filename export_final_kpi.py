"""
Final KPI Export - 4 sheets:
  Sheet 1: KPI Summary           - all EPARGNE products + 096, one row per product
  Sheet 2: Detail 013 & 096      - per category breakdown (count, %, savings)
  Sheet 3: Session Analysis      - avg session duration, web vs mobile connections
  Sheet 4: Screens & Functions   - most visited screens and navigation paths (from adria file)
"""

import pandas as pd
import os
import re
from pathlib import Path
from collections import Counter

print("=" * 70)
print("FINAL KPI EXPORT")
print("=" * 70)

DATA_DIR = Path('D:/bank-data-visualizer/data')
OUTPUT_DIR = Path('D:/bank-data-visualizer/outputs')
OUTPUT_DIR.mkdir(exist_ok=True)

# Resolve actual filenames (accented chars safe via os.listdir)
all_files = os.listdir(DATA_DIR)
def find_file(keyword):
    matches = [f for f in all_files if keyword.lower() in f.lower()]
    if not matches:
        raise FileNotFoundError(f"No file matching '{keyword}' in {DATA_DIR}")
    return DATA_DIR / matches[0]

SAVINGS_FILE  = find_file('epargne_cmc')
PRODUCTS_FILE = find_file('produit')
REALTIME_FILE = find_file('realtime')
ADRIA_FILE    = find_file('adria')

print(f"  Savings file  : {SAVINGS_FILE.name}")
print(f"  Products file : {PRODUCTS_FILE.name}")
print(f"  Realtime file : {REALTIME_FILE.name}")
print(f"  Adria file    : {ADRIA_FILE.name}")

# ============================================================================
# PART A: SAVINGS DATA - KPI Summary + Detail for 013 & 096
# ============================================================================

print("\n[A] Loading savings & product data...")

products_df = pd.read_csv(PRODUCTS_FILE, sep=';', encoding='utf-8')
products_df['_code'] = products_df['ch_code_produit'].astype(str).str.strip().str.zfill(3)
code_to_name = dict(zip(products_df['_code'], products_df['lib_produit']))

savings_df = pd.read_csv(SAVINGS_FILE, sep=';', encoding='utf-8', low_memory=False)
print(f"  Total savings rows: {len(savings_df):,}")

# Fix comma-decimal monthly values
months_cols = [f'M_{i}' for i in range(1, 13)]
for col in months_cols:
    savings_df[col] = pd.to_numeric(
        savings_df[col].astype(str).str.replace(',', '.', regex=False),
        errors='coerce'
    ).fillna(0)

savings_df['CMC'] = pd.to_numeric(
    savings_df['CMC'].astype(str).str.replace(',', '.', regex=False),
    errors='coerce'
)

savings_df['ch_code_produit'] = pd.to_numeric(savings_df['ch_code_produit'], errors='coerce')
savings_df = savings_df.dropna(subset=['ch_code_produit'])
savings_df['ch_code_produit'] = savings_df['ch_code_produit'].astype(int).astype(str).str.zfill(3)

# Target: all EPARGNE-named products + 096 explicitly
epargne_by_name = products_df[
    products_df['lib_produit'].str.contains('EPARGNE', case=False, na=False)
]['_code'].tolist()
target_codes = sorted(set(epargne_by_name + ['096']))

df_target = savings_df[savings_df['ch_code_produit'].isin(target_codes)].copy()

# Categorise
df_target['months_active'] = (df_target[months_cols] > 0).sum(axis=1)
df_target['total_savings']  = df_target[months_cols].sum(axis=1)
df_target['cmc_is_null']   = df_target['CMC'].isna() | (df_target['CMC'] == 0)

def categorise(row):
    if row['months_active'] == 12:
        return 'Full Year Savers'
    elif row['months_active'] > 0:
        return 'Partial Year Savers'
    else:
        return 'Inactive/Abandoned'

df_target['category'] = df_target.apply(categorise, axis=1)

# ── Sheet 1: KPI Summary (all products) ─────────────────────────────────────
print("\n[A1] Building KPI Summary (all products)...")

kpi_rows = []
for code in target_codes:
    prod = df_target[df_target['ch_code_produit'] == code]
    total = len(prod)
    if total == 0:
        continue
    full    = (prod['category'] == 'Full Year Savers').sum()
    partial = (prod['category'] == 'Partial Year Savers').sum()
    inactive= (prod['category'] == 'Inactive/Abandoned').sum()
    inactive_null_cmc = (
        (prod['category'] == 'Inactive/Abandoned') & prod['cmc_is_null']
    ).sum()
    assert full + partial + inactive == total

    kpi_rows.append({
        'Product Code':                       code,
        'Product Name':                       code_to_name.get(code, 'Unknown'),
        'Total Accounts':                     total,
        'Full Year Savers (Count)':           int(full),
        'Full Year Savers (%)':               f"{full/total*100:.2f}%",
        'Partial Year Savers (Count)':        int(partial),
        'Partial Year Savers (%)':            f"{partial/total*100:.2f}%",
        'Inactive/Abandoned (Count)':         int(inactive),
        'Inactive/Abandoned (%)':             f"{inactive/total*100:.2f}%",
        'of which: null CMC (Count)':         int(inactive_null_cmc),
    })

kpi_df = pd.DataFrame(kpi_rows)
print(f"  {len(kpi_df)} products summarised")

# ── Sheet 2: Detail for 013 & 096 ───────────────────────────────────────────
print("\n[A2] Building category detail for products 013 and 096...")

CATEGORIES = ['Full Year Savers', 'Partial Year Savers', 'Inactive/Abandoned']
detail_rows = []
for code in ['013', '096']:
    prod = df_target[df_target['ch_code_produit'] == code]
    prod_name = code_to_name.get(code, 'Unknown')
    total = len(prod)
    for cat in CATEGORIES:
        cat_data = prod[prod['category'] == cat]
        count = len(cat_data)
        pct   = count / total * 100 if total > 0 else 0
        total_sav = cat_data['total_savings'].sum()
        avg_sav   = cat_data['total_savings'].mean() if count > 0 else 0
        detail_rows.append({
            'Product Code':       code,
            'Product Name':       prod_name,
            'User Category':      cat,
            'User Count':         count,
            'Percentage':         f"{pct:.2f}%",
            'Total Savings (DZD)': f"{total_sav:,.2f}",
            'Avg Savings per User (DZD)': f"{avg_sav:,.2f}",
        })

detail_df = pd.DataFrame(detail_rows)
print(f"  {len(detail_df)} category rows built")

# ============================================================================
# PART B: SESSION ANALYSIS (realtime file)
# ============================================================================
print("\n[B] Loading realtime session data...")

realtime_df = pd.read_csv(REALTIME_FILE, sep=';', encoding='utf-8', low_memory=False)
print(f"  Total session rows: {len(realtime_df):,}")

# Parse session duration: format is HH:MM:SS
def parse_duration_seconds(val):
    try:
        parts = str(val).strip().split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except Exception:
        pass
    return None

realtime_df['duration_sec'] = realtime_df['duree_totale_session'].apply(parse_duration_seconds)

# OS column has accented name - find it safely
os_col = [c for c in realtime_df.columns if 'exploitation' in c.lower()]
os_col = os_col[0] if os_col else None

# ── Overall session stats ────────────────────────────────────────────────────
total_sessions = len(realtime_df)
valid_dur = realtime_df['duration_sec'].dropna()
avg_sec = valid_dur.mean()
med_sec = valid_dur.median()

def sec_to_hms(s):
    s = int(s)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}h {m}m {sec}s"

session_rows = []
session_rows.append({
    'Metric': 'Total sessions recorded',
    'Value': f"{total_sessions:,}",
    'Notes': ''
})
session_rows.append({
    'Metric': 'Average session duration',
    'Value': sec_to_hms(avg_sec),
    'Notes': f"{avg_sec:.0f} seconds"
})
session_rows.append({
    'Metric': 'Median session duration',
    'Value': sec_to_hms(med_sec),
    'Notes': f"{med_sec:.0f} seconds"
})
session_rows.append({
    'Metric': 'Unique users',
    'Value': f"{realtime_df['ch_code_client'].nunique():,}",
    'Notes': ''
})

# Web vs Mobile
total_web = realtime_df['nb_connexion_web'].sum()
total_mob = realtime_df['nb_connexion_mob'].sum()
total_conn = total_web + total_mob
session_rows.append({
    'Metric': 'Total web connections',
    'Value': f"{int(total_web):,}",
    'Notes': f"{total_web/total_conn*100:.1f}% of all connections" if total_conn else ''
})
session_rows.append({
    'Metric': 'Total mobile connections',
    'Value': f"{int(total_mob):,}",
    'Notes': f"{total_mob/total_conn*100:.1f}% of all connections" if total_conn else ''
})

# By OS
if os_col:
    os_stats = realtime_df.groupby(os_col).agg(
        Sessions=('duration_sec', 'count'),
        Avg_Duration_Sec=('duration_sec', 'mean'),
        Unique_Users=('ch_code_client', 'nunique')
    ).reset_index().sort_values('Sessions', ascending=False)

    session_rows.append({'Metric': '', 'Value': '', 'Notes': ''})
    session_rows.append({'Metric': '--- BY OPERATING SYSTEM ---', 'Value': '', 'Notes': ''})
    for _, r in os_stats.iterrows():
        avg_d = r['Avg_Duration_Sec']
        session_rows.append({
            'Metric': f"  {r[os_col]}",
            'Value': f"{int(r['Sessions']):,} sessions  |  {int(r['Unique_Users']):,} users",
            'Notes': f"Avg duration: {sec_to_hms(avg_d) if pd.notna(avg_d) else 'N/A'}"
        })

# By browser
browser_stats = realtime_df.groupby('navigateur').agg(
    Sessions=('duration_sec', 'count'),
    Avg_Duration_Sec=('duration_sec', 'mean'),
    Unique_Users=('ch_code_client', 'nunique')
).reset_index().sort_values('Sessions', ascending=False).head(15)

session_rows.append({'Metric': '', 'Value': '', 'Notes': ''})
session_rows.append({'Metric': '--- BY BROWSER (top 15) ---', 'Value': '', 'Notes': ''})
for _, r in browser_stats.iterrows():
    avg_d = r['Avg_Duration_Sec']
    session_rows.append({
        'Metric': f"  {r['navigateur']}",
        'Value': f"{int(r['Sessions']):,} sessions  |  {int(r['Unique_Users']):,} users",
        'Notes': f"Avg duration: {sec_to_hms(avg_d) if pd.notna(avg_d) else 'N/A'}"
    })

session_df = pd.DataFrame(session_rows)
print(f"  Session analysis done — {total_sessions:,} sessions processed")

# ============================================================================
# PART C: SCREENS & FUNCTIONS (adria file)
# ============================================================================
print("\n[C] Loading adria navigation data...")

adria_df = pd.read_csv(ADRIA_FILE, sep=';', encoding='utf-8', low_memory=False)
print(f"  Total adria rows: {len(adria_df):,}")

# Find the screen/navigation columns safely
ecran_col = [c for c in adria_df.columns if 'cran' in c.lower()]   # Ecran_consulté
nav_col   = [c for c in adria_df.columns if 'navigation' in c.lower()]

ecran_col = ecran_col[0] if ecran_col else None
nav_col   = nav_col[0]   if nav_col   else None

print(f"  Screen column   : {ecran_col!r}")
print(f"  Nav URL column  : {nav_col!r}")

# Parse adria duration: format "0h 0m 31s 557ms"
def parse_adria_duration(val):
    try:
        s = str(val)
        h = int(re.search(r'(\d+)h', s).group(1)) if re.search(r'(\d+)h', s) else 0
        m = int(re.search(r'(\d+)m', s).group(1)) if re.search(r'(\d+)m', s) else 0
        sec = int(re.search(r'(\d+)s', s).group(1)) if re.search(r'(\d+)s', s) else 0
        return h * 3600 + m * 60 + sec
    except Exception:
        return None

adria_df['duration_sec'] = adria_df['duree_complete'].apply(parse_adria_duration)

# ── Timeline info from adria ──────────────────────────────────────────────────
adria_df['date_jour_dt'] = pd.to_datetime(adria_df['date_jour'], errors='coerce')
date_min   = adria_df['date_jour_dt'].min()
date_max   = adria_df['date_jour_dt'].max()
days_span  = (date_max - date_min).days
uniq_days  = adria_df['date_jour_dt'].nunique()
uniq_users_adria = adria_df['ch_code_client'].nunique()

# Monthly breakdown
adria_df['month'] = adria_df['date_jour_dt'].dt.to_period('M')
monthly_counts = adria_df.groupby('month').agg(
    Sessions=('nombre_sessions', 'sum'),
    Rows=(adria_df.columns[0], 'count')
).reset_index()

overall_avg_adria = adria_df['duration_sec'].mean()

# ── Top visited screens ───────────────────────────────────────────────────────
screen_counter = Counter()
if ecran_col:
    for val in adria_df[ecran_col].dropna():
        screens = [s.strip() for s in str(val).split('-') if s.strip()]
        screen_counter.update(screens)

top_screens = screen_counter.most_common(30)

# ── Top navigation paths (functions/URLs) ────────────────────────────────────
nav_counter = Counter()
if nav_col:
    for val in adria_df[nav_col].dropna():
        paths = [p.strip() for p in str(val).split('-') if p.strip()]
        nav_counter.update(paths)

top_nav = nav_counter.most_common(30)
top_5_nav = nav_counter.most_common(5)
total_nav_visits = sum(nav_counter.values())

# ── Build screens & functions sheet ──────────────────────────────────────────
screens_rows = []

# ---- TIMELINE HEADER --------------------------------------------------------
screens_rows.append({'Section': '=== DATA COVERAGE (Adria Platform) ===', 'Name / Path': '', 'Visit Count': '', 'Rank': ''})
screens_rows.append({'Section': 'Data source',            'Name / Path': 'Adria mobile/web banking app activity logs',                         'Visit Count': '', 'Rank': ''})
screens_rows.append({'Section': 'Period start',           'Name / Path': str(date_min.date()),                                                  'Visit Count': '', 'Rank': ''})
screens_rows.append({'Section': 'Period end',             'Name / Path': str(date_max.date()),                                                  'Visit Count': '', 'Rank': ''})
screens_rows.append({'Section': 'Total days covered',     'Name / Path': f"{days_span} days ({uniq_days} distinct dates with activity)",       'Visit Count': '', 'Rank': ''})
screens_rows.append({'Section': 'Total log rows',         'Name / Path': f"{len(adria_df):,}",                                                 'Visit Count': '', 'Rank': ''})
screens_rows.append({'Section': 'Unique users tracked',   'Name / Path': f"{uniq_users_adria:,}",                                              'Visit Count': '', 'Rank': ''})
screens_rows.append({'Section': 'Avg session duration',   'Name / Path': sec_to_hms(overall_avg_adria) if pd.notna(overall_avg_adria) else 'N/A', 'Visit Count': f"{overall_avg_adria:.0f} sec" if pd.notna(overall_avg_adria) else '', 'Rank': ''})
screens_rows.append({'Section': '', 'Name / Path': '', 'Visit Count': '', 'Rank': ''})

# Monthly breakdown table
screens_rows.append({'Section': '--- Monthly Activity Breakdown ---', 'Name / Path': '', 'Visit Count': '', 'Rank': ''})
screens_rows.append({'Section': 'Month', 'Name / Path': 'Log Rows', 'Visit Count': 'Note', 'Rank': ''})
for _, mr in monthly_counts.iterrows():
    note = ''
    rows_val = mr['Rows']
    if rows_val < 1000:
        note = 'Platform launch / ramp-up'
    screens_rows.append({
        'Section': str(mr['month']),
        'Name / Path': f"{int(rows_val):,}",
        'Visit Count': note,
        'Rank': ''
    })

screens_rows.append({'Section': '', 'Name / Path': '', 'Visit Count': '', 'Rank': ''})
screens_rows.append({'Section': '=== MOST VISITED SCREENS (Top 30) ===', 'Name / Path': '', 'Visit Count': '', 'Rank': ''})

for rank, (screen, count) in enumerate(top_screens, 1):
    screens_rows.append({
        'Section': 'Screen',
        'Name / Path': screen,
        'Visit Count': count,
        'Rank': rank,
    })

screens_rows.append({'Section': '', 'Name / Path': '', 'Visit Count': '', 'Rank': '', 'Percentage of Total': ''})
screens_rows.append({'Section': '=== MOST USED NAVIGATION PATHS / FUNCTIONS (Top 30) ===', 'Name / Path': '', 'Visit Count': '', 'Rank': '', 'Percentage of Total': ''})
screens_rows.append({'Section': 'Note:', 'Name / Path': f'Percentages shown for Top 5 based on {total_nav_visits:,} total navigations', 'Visit Count': '', 'Rank': '', 'Percentage of Total': ''})

for rank, (path, count) in enumerate(top_nav, 1):
    pct_str = f"{count/total_nav_visits*100:.2f}%" if rank <= 5 else ""
    screens_rows.append({
        'Section': 'Navigation Path',
        'Name / Path': path,
        'Visit Count': count,
        'Rank': rank,
        'Percentage of Total': pct_str
    })

# (Timeline and session stats already added at the top of the sheet)

screens_df = pd.DataFrame(screens_rows)
print(f"  Top screens extracted: {len(top_screens)}")
print(f"  Top nav paths extracted: {len(top_nav)}")

# ============================================================================
# EXPORT TO EXCEL
# ============================================================================
print("\n[EXPORT] Writing Excel file...")

excel_file = OUTPUT_DIR / 'KPI_Final_Export.xlsx'

with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    kpi_df.to_excel(writer,     sheet_name='KPI Summary (All Products)', index=False)
    detail_df.to_excel(writer,  sheet_name='Detail - 013 and 096',       index=False)
    session_df.to_excel(writer, sheet_name='Session Analysis',            index=False)
    screens_df.to_excel(writer, sheet_name='Screens and Functions',       index=False)

print(f"\n  Exported: {excel_file}")
print("\n  Sheets:")
print("    1. KPI Summary (All Products)  - all EPARGNE products + 096, one row each")
print("    2. Detail - 013 and 096        - Full Year / Partial / Inactive breakdown with savings")
print("    3. Session Analysis            - avg duration, web vs mobile, by OS, by browser")
print("    4. Screens and Functions       - top 30 visited screens + top 30 navigation paths")
print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
