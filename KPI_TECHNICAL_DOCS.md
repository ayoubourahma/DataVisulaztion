# 🔧 KPI Implementation - Technical Documentation

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│ Main Window (main_window.py)                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ KPI Dashboard Tab (kpi_dashboard_tab.py)         │  │
│  │  • Summary Display                               │  │
│  │  • Product Rankings                              │  │
│  │  • Field Links Documentation                     │  │
│  └──────────────────────────────────────────────────┘  │
│           │                                              │
│           ▼                                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ KPI Analyzer (kpi_analyzer.py)                   │  │
│  │  • Data Merging                                  │  │
│  │  • KPI Calculations                              │  │
│  │  • Export Management                             │  │
│  └──────────────────────────────────────────────────┘  │
│           │                                              │
│           ▼                                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Data Loader (data_loader.py)                     │  │
│  │  • Loads src_produit.txt                         │  │
│  │  • Loads src_objectif_epargne_cmc.txt            │  │
│  │  • Data cleaning & validation                    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Module: kpi_analyzer.py

### Class: `KPIAnalyzer`

**Purpose:** Main analysis engine for KPI generation

#### Constructor:
```python
def __init__(self, dataframes: Dict[str, pd.DataFrame])
```

**Parameters:**
- `dataframes`: Dict of loaded DataFrames from BankDataLoader

#### Public Methods:

##### `analyze()` → Tuple[DataFrame, Dict, Dict]
Main entry point for KPI analysis

**Returns:**
- `kpi_summary`: DataFrame with product-level KPIs
- `kpi_details`: Dict with detailed analysis
- `field_links`: Dict describing data relationships

**Process:**
1. Merges datasets on `ch_code_produit`
2. Identifies field links
3. Calculates summary KPIs
4. Calculates detailed KPIs
5. Returns results

**Example:**
```python
analyzer = KPIAnalyzer(dataframes)
summary, details, links = analyzer.analyze()
```

##### `get_top_products(n: int) → DataFrame`
Returns top N products by total savings

**Parameters:**
- `n`: Number of products to return (default: 10)

**Returns:** DataFrame sorted by savings (descending)

##### `get_monthly_trend() → DataFrame`
Returns monthly savings trend

**Returns:** DataFrame with columns:
- `Month`: Month name (M_1 to M_12)
- `Total Savings`: Sum for that month

##### `get_segment_distribution() → DataFrame`
Returns savings by client segment

**Returns:** DataFrame with columns:
- `Segment`: Client segment name
- `Total Savings`: Sum for segment
- `Account Count`: Number of accounts
- `Avg per Account`: Efficiency metric

##### `export_kpis(output_path: str, include_details: bool) → bool`
Exports KPIs to CSV files

**Parameters:**
- `output_path`: Directory to save files
- `include_details`: Include detailed sheets (default: True)

**Returns:** True if successful

**Files Created:**
- `kpi_summary.csv` - Product-level KPIs
- `kpi_monthly_trend.csv` - Monthly aggregation
- `kpi_segment_distribution.csv` - Segment breakdown
- `field_links.txt` - Data relationship documentation

### Private Methods:

#### `_merge_data(product_df, savings_df)`
Merges product and savings data

**Logic:**
```python
merged = pd.merge(
    savings_df,
    product_df,
    on='ch_code_produit',
    how='left'
)
```

**Result stored in:** `self.product_savings_merged`

#### `_identify_field_links(product_df, savings_df)`
Documents field relationships

**Creates:** `self.field_links` dict with:
- Primary Link info
- Product Fields description
- Savings Fields description
- Field Statistics

#### `_calculate_kpi_summary() → DataFrame`
Product-level KPI calculations

**For each product, calculates:**
- Product Code & Name
- Total Accounts (count)
- Unique Clients (count distinct CLIENT_MARQUE)
- Total Savings (sum of M_1:M_12)
- Avg Monthly (mean)
- Max Month (max value)
- Min Month (min value)
- Per Account (total ÷ accounts)
- Avg Clients per Account

#### `_calculate_kpi_details() → Dict`
Detailed breakdowns by segment and sector

**Structure:**
```python
{
    'Overall': {...},
    'Monthly Trend': {...},
    'By Client Segment': {...},
    'By Activity Sector': {...}
}
```

### Convenience Function:

#### `analyze_products_savings(dataframes) → Tuple`
Quick analysis without explicit class usage

```python
summary, details, links, analyzer = analyze_products_savings(dataframes)
```

---

## Module: kpi_dashboard_tab.py

### Class: `KPICalculatorThread`

**Purpose:** Background thread for KPI calculations

**Signals:**
- `progress(str)`: Status message
- `finished(summary, details, links, analyzer)`: Calculation complete
- `error(str)`: Error message

**Methods:**
- `run()`: Executes KPI analysis in background

---

### Class: `KPIDashboardTab`

**Purpose:** PyQt5 UI for KPI display and export

#### Constructor:
```python
def __init__(self, dataframes: Dict[str, pd.DataFrame])
```

#### Key Methods:

##### `calculate_kpis()`
Triggers KPI calculation in background thread

**Process:**
1. Creates KPICalculatorThread
2. Connects signals to handlers
3. Starts thread

##### `update_summary_display()`
Updates text display in Summary tab

**Displays:**
- Overall statistics
- By Client Segment breakdown
- By Activity Sector breakdown

##### `update_product_table()`
Populates Product Rankings table

**Features:**
- Top 20 products
- Column sorting available
- Green highlighting for top 25%

##### `update_links_display()`
Updates Field Links documentation

**Shows:**
- Primary linking field
- Product fields
- Savings fields
- Statistics

##### `export_kpis()`
Handles KPI export

**Process:**
1. Shows directory picker
2. Calls `analyzer.export_kpis()`
3. Shows success/error message

#### UI Components:

**Tabs:**
- Summary - Text statistics
- Top Products - Table view
- Field Links - Documentation

**Buttons:**
- Refresh KPIs - Recalculate
- Export KPIs - Save to files

---

## Data Flow

### 1. Initialization
```
MainWindow.init_tabs()
  → Creates KPIDashboardTab(dataframes)
    → Calls __init__()
      → Calls init_ui()
      → Calls calculate_kpis()
```

### 2. KPI Calculation
```
calculate_kpis()
  → Creates KPICalculatorThread
  → Thread.run() in background
    → Imports KPIAnalyzer
    → Calls analyze_products_savings()
      → KPIAnalyzer.analyze()
        → _merge_data()
        → _identify_field_links()
        → _calculate_kpi_summary()
        → _calculate_kpi_details()
      → Returns (summary, details, links, analyzer)
    → Emits finished signal
  → on_kpi_finished() handler
    → update_summary_display()
    → update_product_table()
    → update_links_display()
```

### 3. Export Process
```
export_kpis() button click
  → Show directory picker
  → Call analyzer.export_kpis(directory)
    → Create summary CSV
    → Create trend CSV
    → Create segment CSV
    → Create links TXT
    → Return True/False
  → Show success/error message
```

---

## Key Calculations

### Total Savings by Product
```python
df[df['ch_code_produit'] == product_code][['M_1', 'M_2', ..., 'M_12']].sum()
```

### Average Monthly
```python
df[monthly_cols].sum().mean()
```

### Per Account Efficiency
```python
total_savings / number_of_accounts
```

### Segment Distribution
```python
df.groupby('CLIENT_MARQUE')[monthly_cols].sum().sum()
```

---

## Integration with Main Window

### Changes to main_window.py:

1. **Import:**
   ```python
   from desktop_app.ui.kpi_dashboard_tab import KPIDashboardTab
   ```

2. **Add attribute:**
   ```python
   self.kpi_dashboard_tab = None
   ```

3. **Create tab in init_tabs():**
   ```python
   self.kpi_dashboard_tab = KPIDashboardTab(self.dataframes)
   self.tabs.addTab(self.kpi_dashboard_tab, "🎯 KPI Analysis")
   ```

---

## Data Requirements

### Required Files:
1. `src_produit.txt`
   - Must have: `ch_code_produit`, `lib_produit`

2. `src_objectif_epargne_cmc.txt`
   - Must have: `ch_code_produit`, `M_1` through `M_12`
   - Should have: `CLIENT_MARQUE`, `CLT_SECTEUR_ACTIVITE_LIB`

### Error Handling:
- Missing files: Returns empty KPI data with warning
- Missing columns: Gracefully handles using `.get()`
- No data: Shows empty tables/text
- Export errors: Shows error dialog

---

## Performance Considerations

### Data Loading:
- Runs in background thread
- Doesn't freeze UI during calculation

### Memory Usage:
- Stores merged DataFrame in memory
- Typical for 50k records: ~20MB
- Can handle 1M+ records (may be slow)

### Calculation Speed:
- Product summary: ~100ms
- Segment breakdown: ~50ms
- Export: Depends on disk speed (~1-5 seconds)

### Optimization Opportunities:
- Cache calculations between renders
- Use numpy for larger datasets
- Lazy-load segment details
- Stream export for very large files

---

## Testing Checklist

- [ ] Tab appears after data loads
- [ ] "Analyzing KPIs..." message shows
- [ ] Summary tab populates with data
- [ ] Top products table shows top 20
- [ ] Field links show linking information
- [ ] Green highlighting on high-value products
- [ ] Export button saves all 4 files
- [ ] Refresh button recalculates
- [ ] No errors in console
- [ ] Handles missing data gracefully
- [ ] Large datasets (1M+) still work
- [ ] Export with special characters works

---

## Future Enhancements

### Visualizations:
- Add charts (matplotlib/plotly)
- Pie chart for segments
- Line chart for trends
- Bar chart for top products

### Interactivity:
- Click product to drill down
- Filter by segment
- Date range selection
- Custom KPI definitions

### Export Formats:
- Excel with multiple sheets
- JSON for APIs
- PDF reports with charts
- Database insert scripts

### Analysis:
- Predictive trends
- Anomaly detection
- Cohort analysis
- Product recommendations

---

## Logging

All operations logged via Python `logging` module:

```python
logger.info("✅ KPI analysis complete")
logger.error("❌ Error loading data")
```

Check application logs for troubleshooting.

---

## Code Examples

### Using KPI Analyzer Standalone:
```python
from desktop_app.core.kpi_analyzer import KPIAnalyzer
from desktop_app.core.data_loader import BankDataLoader

# Load data
loader = BankDataLoader("data")
dataframes = loader.load_all_data()

# Analyze
analyzer = KPIAnalyzer(dataframes)
summary, details, links = analyzer.analyze()

# Export
analyzer.export_kpis("output")

# Get specifics
top_10 = analyzer.get_top_products(10)
monthly = analyzer.get_monthly_trend()
segments = analyzer.get_segment_distribution()
```

### Accessing Results:
```python
# Top 5 products
print(summary.head(5))

# Overall stats
print(details['Overall'])

# Segment details
print(details['By Client Segment'])

# Monthly data
print(details['Monthly Trend'])
```

---

This documentation covers the complete KPI implementation. For questions about specific calculations, refer to the relevant method documentation.
