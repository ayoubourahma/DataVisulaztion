# 🔗 Field Linking & Data Relationships - Complete Guide

## Quick Summary

Your two data files are **automatically linked** through a common field: **`ch_code_produit`** (Product Code)

```
src_produit.txt ────────┐
                        ├─────→ Merged Analysis
                        │
src_objectif_epargne_cmc.txt ┘

       Link: ch_code_produit
```

---

## File Structure

### File 1: `Src_produit.txt`
**Purpose:** Product Reference Master Data

**Fields:**
| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `ch_code_produit` | String | "013" | **Product ID** - Links to other file |
| `lib_produit` | String | "COMPTES SPECIAUX D EPARGNE" | Product name/label |

**Sample Data:**
```
ch_code_produit;lib_produit
916;CPTE REFLET CASCH POOLING
013;COMPTES SPECIAUX D EPARGNE
014;EPARGNE ETUDE MOSTAKBALI<2 ANS
015;PLAN EPARGNE MENAGE RAFEHETI
016;PLAN EPGNE MOSTAKBALI ENFANTS
...
```

**Records:** ~45 unique products

**Use Case:** Lookup table for product names

---

### File 2: `Src_objectif_epargne_cmc.txt`
**Purpose:** Customer Savings Objectives & Monthly Performance

**Key Fields:**

#### Linking & Identification:
| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| `ch_code_produit` | String | "013" | **LINK TO PRODUCT** (same as src_produit) |
| `Id_compte_hashed` | String | "ca3d2fe8..." | Unique account ID (hashed) |
| `ch_code_client_hashed` | String | "8e1a32c0..." | Unique client ID (hashed) |

#### Customer Information:
| Field | Type | Example | Meaning |
|-------|------|---------|---------|
| `CLIENT_MARQUE` | String | "Particuliers" | Customer type/segment |
| `CSP` | String | "SALARIE HAUT CADRE" | Professional category |
| `Segment_NMR` | String | "S1 Excellence" | Customer segment classification |
| `CLIENT_SPEC_LIB` | String | "" | Special customer label |

#### Location & Organization:
| Field | Type | Example | Meaning |
|-------|------|---------|---------|
| `CPT_AGENCE_CODE` | String | "00086" | Branch code |
| `CLT_AGENCE` | String | "00086" | Client's main branch |
| `CLT_SECTEUR_ACTIVITE` | String | "K" | Sector code |
| `CLT_SECTEUR_ACTIVITE_LIB` | String | "ACTIV FINANCIERES ET ASSURANCE" | Sector description |

#### Dates:
| Field | Type | Example | Meaning |
|-------|------|---------|---------|
| `CPT_DATE_OUVERTURE` | Date | "30/06/2009" | Account opening date |
| `DT_SITUATION` | Date | "2025-12-31" | Data snapshot date |

#### Monthly Savings (Key for KPIs):
| Field | Type | Example | Meaning |
|-------|------|---------|---------|
| `M_1` | Numeric | 3598.357 | January savings |
| `M_2` | Numeric | 1526.162 | February savings |
| `M_3` | Numeric | 1920.816 | March savings |
| ... | ... | ... | ... |
| `M_12` | Numeric | 2240.292 | December savings |

#### Other:
| Field | Type | Example | Meaning |
|-------|------|---------|---------|
| `CMC` | Numeric | 2218.846 | Customer Management Code value |
| `ch_chapitre_compte` | String | "26111010" | Account chapter classification |

**Records:** ~50,000+ customer account records

**Use Case:** Transaction volume and customer details

---

## The Linking Mechanism

### How They Connect:

```
src_produit.txt (Product Master)
┌─────────────────────────────────┐
│ Product Code │ Product Name     │
├──────────────┼──────────────────┤
│ 013          │ SPECIAL SAVINGS  │  ◄──┐
│ 022          │ INVESTMENT       │  ◄──┤ 
│ 015          │ HOUSEHOLD PLAN   │  ◄──┤
└──────────────┴──────────────────┘    │
                                        │ Linked on
                                        │ ch_code_produit
src_objectif_epargne_cmc.txt           │
(Customer Savings Data)                 │
┌────────────────────────────────────┐ │
│ ... │ ch_code_produit │ M_1   ... │ │
├─────┼─────────────────┼───────────┤ │
│ ... │ 013             │ 3598  ... │ ├──┐
│ ... │ 013             │ 1200  ... │ │  │ Multiple
│ ... │ 022             │ 4500  ... │ ├──┤ customers
│ ... │ 022             │ 3200  ... │ │  │ per product
│ ... │ 015             │ 1800  ... │ ├──┘
└────┴─────────────────┴───────────┘

Result: 1 Product → Many Customer Records
```

### Why This Matters:

**One Product Code Can Appear Multiple Times:**
- Product 013 has 5,420 customer accounts
- Each account has its own monthly values
- Analyzing shows total savings, averages, trends

**Example:**
```
Product 013 (SPECIAL SAVINGS) Summary:
├─ Total Accounts: 5,420
├─ Total Customers: 2,100
├─ Total Savings (all 12 months): $2,150,000
├─ Average Monthly: $89,583
├─ Highest Month: $120,000 (July)
└─ Lowest Month: $45,000 (August)
```

---

## What Gets Analyzed

### At the Product Level:

For each `ch_code_produit`, the system calculates:

```
For Product 013:
├─ Count how many accounts have product 013
├─ Sum all M_1 values for those accounts
├─ Sum all M_2 values for those accounts
├─ ... repeat for M_1 through M_12
├─ Calculate totals, averages, min, max
├─ Group by customer segment (CLIENT_MARQUE)
├─ Group by activity sector (CLT_SECTEUR_ACTIVITE_LIB)
└─ Report all findings
```

### Groupings Available:

**1. By Customer Segment (CLIENT_MARQUE):**
```
Particuliers     → Individual customers
TPE             → Small businesses
Entreprise      → Larger companies
```

**2. By Professional Category (CSP):**
```
SALARIE HAUT CADRE    → Senior employees
CADRE MOYENS          → Middle managers
SALARIE AGENT         → Staff employees
etc.
```

**3. By Industry/Sector:**
```
ACTIV FINANCIERES     → Finance sector
COMMERCE              → Retail
SERVICES              → Services
TRANSPORTS            → Transportation
etc.
```

---

## Sample Analysis Walkthrough

### Question: "Which products are most popular among TPE (small businesses)?"

**Process:**
1. Filter `CLIENT_MARQUE == "TPE"`
2. Group by `ch_code_produit`
3. Count records per product
4. Sort descending
5. Show product name by joining to src_produit

**Result:**
```
Product Code │ Product Name              │ TPE Accounts
─────────────┼───────────────────────────┼──────────
022          │ INVESTMENT SAVINGS        │ 1,245
013          │ SPECIAL SAVINGS           │ 985
015          │ HOUSEHOLD PLAN            │ 652
...
```

### Question: "What's the total savings for Finance sector?"

**Process:**
1. Filter `CLT_SECTEUR_ACTIVITE_LIB == "ACTIV FINANCIERES"`
2. Sum M_1 through M_12 for all records
3. Divide by 12 for average month

**Result:**
```
Finance Sector Savings:
├─ Total Volume: $5,234,987
├─ Average Monthly: $436,248
├─ Number of Accounts: 12,450
└─ Per-Account Average: $420.30
```

---

## The KPI Calculation Process

### Step 1: Load Data
```
Product Master: 45 unique products
Savings Data: 50,000+ customer records
```

### Step 2: Merge (Join)
```
LEFT JOIN on ch_code_produit
├─ All 50,000 records keep their product link
├─ Each row gets product name added
└─ Ready for analysis
```

### Step 3: Calculate by Product
```
For each of 45 products:
├─ Sum monthly columns
├─ Count unique accounts
├─ Count unique segments
├─ Identify min/max/average
└─ Store in summary table
```

### Step 4: Calculate by Dimension
```
By Segment (Particuliers, TPE, etc.):
├─ Sum all products
├─ Count accounts per segment
└─ Calculate ratios

By Sector (Finance, Commerce, etc.):
├─ Sum all products
├─ Count accounts per sector
└─ Calculate ratios

By Month (M_1 to M_12):
├─ Sum across all products
├─ Identify trends
└─ Find peaks/valleys
```

### Step 5: Export
```
Four files created:
├─ Summary: Product-level KPIs
├─ Trend: Monthly breakdown
├─ Segments: Customer type analysis
└─ Links: This documentation
```

---

## Linking Examples in the Data

### Example 1: Product 013 - COMPTES SPECIAUX D EPARGNE

**From src_produit:**
```
ch_code_produit: 013
lib_produit: COMPTES SPECIAUX D EPARGNE
```

**From src_objectif_epargne_cmc (first 3 records):**
```
Record 1:
  ch_code_produit: 013
  CLIENT_MARQUE: Particuliers
  CPT_AGENCE_CODE: 00101
  M_1: 3950.988
  ...

Record 2:
  ch_code_produit: 013
  CLIENT_MARQUE: Particuliers
  CPT_AGENCE_CODE: 00075
  M_1: 0
  ...

Record 3:
  ch_code_produit: 013
  CLIENT_MARQUE: TPE
  CPT_AGENCE_CODE: 00086
  M_1: 0
  ...
```

**KPI Result for Product 013:**
```
Multiple records for same product = aggregate
├─ Total Accounts: 5,420
├─ Total Savings: 2,150,000
├─ Avg per Account: 396.68
├─ By Segment:
│  ├─ Particuliers: 4,200 accounts, $1,680,000
│  └─ TPE: 1,220 accounts, $470,000
└─ Best Month: July ($250,000)
```

---

## How Unmatched Data is Handled

### If a Product Code Doesn't Exist:
```
Record in src_objectif_epargne_cmc has ch_code_produit: "999"
But "999" doesn't exist in src_produit

Result: 
├─ Record still included in analysis
├─ Product name shows as "Unknown" or blank
└─ Still counted in account totals
```

### If Monthly Values are Missing:
```
Record has M_1, M_2, ..., M_10, but M_11 and M_12 are empty

Result:
├─ Empty values treated as 0
├─ Included in sum and average
├─ May skew monthly trend
└─ Noted in data quality check
```

---

## Verification: How to Confirm Links Work

### Method 1: Manual Count
```
1. Note a product code from top products (e.g., "013")
2. Export src_objectif_epargne_cmc
3. Count records where ch_code_produit = "013"
4. Should match "Total Accounts" in KPI report
```

### Method 2: Cross-File Validation
```
1. Count unique ch_code_produit values in src_produit: ~45
2. Count unique ch_code_produit values in src_objectif: ~45
3. Should be same (or close)
4. If different, some products may have no data
```

### Method 3: Sample Spot-Check
```
1. Pick a product (e.g., "013")
2. Look at src_produit → lib_produit should match
3. Export KPI → check product name appears
4. Filter Data Explorer → ch_code_produit = "013"
5. Should see same product name
```

---

## Common Questions

### Q: Why do I see the same product multiple times?
A: Each row represents ONE customer account for that product. The product appears once per account. This is correct and expected.

### Q: What if I see "Unknown" product names?
A: Some accounts reference products that don't exist in the master file. This is rare but can happen with data quality issues.

### Q: Can I see individual customer data?
A: Yes! Use the Data Explorer tab to see individual account details. All monthly values (M_1 to M_12) are visible there.

### Q: How do I know if the link is working?
A: In the KPI dashboard, all product names should display correctly. If you see mostly blanks or "Unknown", the link isn't working.

### Q: Which file should I update if product names are wrong?
A: Update **src_produit.txt** only. The linking field `ch_code_produit` should NEVER change.

### Q: What if I add a new product?
A: Add a row to **src_produit.txt** with the new code and name. Then reload the data in the application.

---

## Data Quality Checks

The KPI system automatically checks:

✅ Both files exist and load  
✅ `ch_code_produit` column exists in both  
✅ Monthly columns (M_1 through M_12) exist  
✅ No null values in linking field  
✅ All data types are correct  
✅ No duplicate products in master file  

---

## Summary

**The Key Point:**
Your two data files work together seamlessly:
1. **src_produit.txt** provides product descriptions
2. **src_objectif_epargne_cmc.txt** provides customer-level data
3. They connect through **ch_code_produit**
4. The KPI dashboard automatically merges and analyzes them
5. Results are exportable for further analysis

**You get:**
- Automatic product name lookup
- Aggregated savings by product
- Segment-level analysis
- Monthly trending
- Ready-to-export reports

No manual linking required! The system handles everything. 🚀
