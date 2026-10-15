# 🎯 KPI Analysis Dashboard - User Guide

## Overview

Your Bank Data Visualizer now includes a comprehensive **KPI Analysis Dashboard** that automatically analyzes relationships between Product and Savings Objectives data, extracts key performance indicators, and enables export.

---

## 📊 What You Can See

### 1️⃣ **Summary Tab** - Overall Statistics

Displays high-level metrics:

```
📊 OVERALL KPI SUMMARY
======================================================
Total Records........................ 50,000
Total Unique Products............... 45
Total Unique Clients................ 12,500
Total Savings All Time.............. 5,234,987.50
Average Monthly Total............... 436,248.96
Highest Month....................... 612,487.23
Lowest Month........................ 234,156.78

📍 BY CLIENT SEGMENT
────────────────────────────────────
Particuliers:
  Records: 35,000
  Total Savings: 3,500,000.00
  Avg Savings per Account: 100.00

TPE:
  Records: 15,000
  Total Savings: 1,734,987.50
  Avg Savings per Account: 115.66

🏭 BY ACTIVITY SECTOR
────────────────────────────────────
ACTIV FINANCIERES (Finance):
  Records: 5,200
  Total Savings: 1,250,000.00
  Avg Savings per Account: 240.38
  ...
```

**Key Metrics Included:**
- Total savings volume
- Monthly trends
- Client segment breakdown
- Activity sector analysis

---

### 2️⃣ **Top Products Tab** - Product Rankings

Table showing the best-performing products:

| Product Code | Product Name | Total Accounts | Total Savings | Avg Monthly | Per Account |
|---|---|---|---|---|---|
| 013 | SPECIAL SAVINGS | 5,420 | 2,150,000 | 89,583 | 396.68 |
| 022 | INVESTMENT SAVINGS | 3,200 | 1,875,000 | 78,125 | 586.72 |
| 016 | CHILDREN SAVINGS | 2,100 | 924,500 | 38,542 | 440.24 |
| 015 | HOUSEHOLD PLAN | 1,950 | 856,320 | 35,680 | 439.14 |

**Highlighted** (green) = Top 25% products by savings

**Columns Explained:**
- **Product Code**: ID from src_produit
- **Product Name**: Description of product
- **Total Accounts**: Number of customer accounts
- **Total Savings**: Sum of all monthly values
- **Avg Monthly**: Average monthly volume
- **Per Account**: Savings divided by accounts

---

### 3️⃣ **Field Links Tab** - Data Relationships

Shows how the two data files are connected:

```
🔗 FIELD LINKS BETWEEN DATASETS
═══════════════════════════════════════════

■ PRIMARY LINK
────────────────────────────────────────────
Field: ch_code_produit
Description: Product Code
  src_produit: Identifier for each product
  src_objectif_epargne_cmc: Links to product details

■ PRODUCT FIELDS
────────────────────────────────────────────
• ch_code_produit: Product Code (Link Key)
• lib_produit: Product Label/Name

■ SAVINGS FIELDS
────────────────────────────────────────────
• CPT_AGENCE_CODE: Branch Code
• CLIENT_MARQUE: Client Market Segment
• CSP: Customer Category (Profession)
• Segment_NMR: Customer Segment
• CLIENT_SPEC_LIB: Special Client Label
• CLT_AGENCE: Client Branch
• CPT_DATE_OUVERTURE: Account Opening Date
• CLT_SECTEUR_ACTIVITE: Activity Sector
• M_1 to M_12: Monthly Savings Values
• CMC: Customer Management Code
  ...

■ FIELD STATISTICS
────────────────────────────────────────────
• Product Records: 45
• Savings Records: 50,000
• Unique Products: 45
• Unique Savings Products: 45
```

---

## 🔄 How Data is Linked

### Connection Flow:

```
src_produit.txt                src_objectif_epargne_cmc.txt
┌──────────────────┐          ┌──────────────────────────┐
│ ch_code_produit  │◄─────────│ ch_code_produit          │
│ lib_produit      │          │ (Monthly data M_1-M_12)  │
│                  │          │ (Client info)            │
│ 013 → Savings    │◄─ LINK ──│ 013 → Particuliers       │
│ 022 → Investment │◄─ LINK ──│ 022 → TPE                │
│ ...              │          │ ...                      │
└──────────────────┘          └──────────────────────────┘
   Product Reference             Savings Objectives
```

**The Link:**
- `ch_code_produit` appears in both files
- One product can have multiple savings records
- Each record has monthly data (M_1 through M_12)

---

## 📤 How to Export KPIs

### Step-by-Step:

1. **Navigate** to "🎯 KPI Analysis" tab
2. **Wait** for analysis to complete (shows "Analyzing KPIs..." message)
3. **Click** the "📤 Export KPIs" button
4. **Select** a directory to save files
5. **Confirm** - Files are created automatically

### Files Created:

```
your_export_folder/
├── kpi_summary.csv
│   └─ Top products by savings, accounts, metrics
├── kpi_monthly_trend.csv
│   └─ Total savings per month (M_1 to M_12)
├── kpi_segment_distribution.csv
│   └─ Savings by client segment
└── field_links.txt
    └─ Documentation of data relationships
```

### Using Exported Files:

**kpi_summary.csv** - Open in Excel for:
- Sorting by different metrics
- Creating additional charts
- Sharing with stakeholders

**kpi_monthly_trend.csv** - Create line chart:
- Shows seasonal patterns
- Identifies peaks and valleys

**kpi_segment_distribution.csv** - Pie chart analysis:
- See which client types drive savings
- Target high-value segments

---

## 📊 KPI Definitions

### Product Level KPIs:

| KPI | Calculation | Use |
|-----|-----------|-----|
| **Total Accounts** | Count of records | Market size |
| **Total Savings** | Sum of M_1 to M_12 | Revenue generation |
| **Avg Monthly** | Mean of monthly values | Volume consistency |
| **Max Month** | Highest single month | Peak capacity |
| **Min Month** | Lowest single month | Floor performance |
| **Per Account** | Total ÷ Accounts | Efficiency metric |

### Segment Level KPIs:

| KPI | Meaning |
|-----|---------|
| **Total Savings** | Sum for that segment |
| **Account Count** | Penetration in segment |
| **Avg per Account** | Engagement quality |

### Monthly Analysis:

- Track from **M_1 (January)** to **M_12 (December)**
- Identify trends and seasonality
- Compare year-over-year if data spans multiple years

---

## 🔍 Data Quality Notes

### What's Included:
✅ All products with savings data  
✅ All client segments (Particuliers, TPE, etc.)  
✅ All activity sectors  
✅ Monthly values with nulls handled  

### What's Excluded:
- Empty or null product codes
- Records with no matching product
- Duplicate records (cleaned during load)

### Data Integrity:
- Linked on `ch_code_produit` (Product Code)
- Automatic handling of missing values
- Validation of joined datasets

---

## ⚡ Tips & Best Practices

### 1. **Refresh KPIs**
- Click "🔄 Refresh KPIs" if data updates
- Recalculates all metrics

### 2. **Combine with Other Tools**
- Export KPIs to Excel
- Combine with dashboard tab insights
- Use with AI Advisor for deep analysis

### 3. **Track Trends**
- Export monthly trend CSV
- Create line chart in Excel
- Identify growth/decline patterns

### 4. **Segment Analysis**
- Use segment distribution export
- Target marketing to high-value groups
- Allocate resources efficiently

### 5. **Sharing Reports**
- Export all files together
- Provide field_links.txt for context
- Includes data dictionary

---

## 🎯 Common Use Cases

### Scenario 1: Which Products are Most Popular?
1. Go to "Top Products" tab
2. Sort by "Total Accounts"
3. Highest = Most accounts held

### Scenario 2: Which Segments Contribute Most Savings?
1. Go to "Summary" tab → "By Client Segment"
2. Look for highest "Total Savings"
3. Or export segment distribution for chart

### Scenario 3: Monthly Trends - Growing or Declining?
1. Export KPIs → Download `kpi_monthly_trend.csv`
2. Open in Excel
3. Create line chart of "Total Savings"

### Scenario 4: Efficiency by Product
1. "Top Products" tab
2. Look at "Per Account" column
3. High value = Efficient product

### Scenario 5: Understand Data Relationships
1. Go to "Field Links" tab
2. Read "Primary Link" section
3. Use to explain data structure to others

---

## 🆘 Troubleshooting

### "KPI Tab Not Showing Data"
- **Check:** Are you on the "🎯 KPI Analysis" tab?
- **Wait:** Analysis may still be calculating
- **Try:** Click "🔄 Refresh KPIs"

### Export Files Not Created
- **Check:** Did you select a valid directory?
- **Check:** Do you have write permissions?
- **Try:** Save to Documents folder instead

### Numbers Seem Wrong
- **Check:** Are monthly values in original data?
- **Note:** Null values are treated as 0
- **Try:** Review field_links.txt for clarity

### Missing Some Products
- **Check:** Does src_produit have all products?
- **Check:** Do all records have ch_code_produit?
- **Note:** Unmatched products won't appear

### Export Takes a Long Time
- **This is normal** for large datasets
- **Wait patiently** - Files are being written
- **Don't** click Export again

---

## 📋 Data Dictionary

### Key Fields Used:

**From src_produit.txt:**
- `ch_code_produit` - Product identifier
- `lib_produit` - Product name/label

**From src_objectif_epargne_cmc.txt:**
- `ch_code_produit` - Links to product
- `CLIENT_MARQUE` - Customer segment (Particuliers, TPE, etc.)
- `CSP` - Professional category (Cadre, Salarié, etc.)
- `M_1` through `M_12` - Monthly savings values
- `CLT_SECTEUR_ACTIVITE_LIB` - Industry/sector
- `CPT_DATE_OUVERTURE` - Account opening date

---

## ✅ What's Next?

1. ✅ View KPI summary
2. ✅ Analyze top products
3. ✅ Understand field relationships
4. ✅ Export for further analysis
5. → Consider combining with:
   - Dashboard insights
   - AI Advisor queries
   - Data Explorer deep dives

---

Happy analyzing! 📊🚀
