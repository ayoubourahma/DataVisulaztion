# Data Explorer - Enhanced Features Guide

## 🎯 What's New

Your Data Explorer now has powerful selective data export capabilities. Instead of always exporting entire datasets, you can now:
- ✅ Select specific rows
- ✅ Choose which columns to include
- ✅ Export to CSV or Excel
- ✅ Work with filtered search results

---

## 📋 How to Use

### 1️⃣ **Select Rows** - Using Checkboxes

The table now has a **✓ checkbox column** on the left:

```
✓  | Client ID    | Amount  | Date
─────────────────────────────────────
☑  | C001         | 1000    | 2024-01
☐  | C002         | 2000    | 2024-01
☐  | C003         | 1500    | 2024-01
```

**To select rows:**
1. Click the checkbox (☑/☐) next to each row you want
2. Use **"☑️ Select All Rows"** button to select all visible rows
3. Use **"☐ Clear Selection"** button to deselect all

**Note:** Selection persists when you search/filter!

---

### 2️⃣ **Select Columns** - Using Right-Click Menu

**To choose which columns to export:**
1. Right-click on any column header
2. A menu appears with all available columns
3. Uncheck columns you want to exclude
4. Check columns you want to include
5. Use **"Show All Columns"** to reset and include all

```
✓ Client ID
✓ Amount
✓ Date
  Interest Rate    ← Click to toggle
✓ Status
```

---

### 3️⃣ **Export Options** - Two Export Buttons

#### 💾 **"Export All (CSV)"** - Green Button
- Exports the **entire current dataset** to CSV
- Ignores row/column selections
- Useful for complete backups
- Format: CSV only

#### 📤 **"Export Selected"** - Orange Button
- Exports **only checked rows** and **selected columns**
- Lets you choose format: **CSV or Excel**
- Shows a dialog to pick format
- Validates that you have selections

---

## 📊 Real-World Example

**Scenario:** You have 50,000 bank transactions. You want to export only high-value transactions for specific clients.

### Steps:
1. **Load dataset** via dropdown (e.g., "Transactions")
2. **Search** for key clients: Type "VIP_" in search box
3. **Filter results** show 1,200 matching rows
4. **Select rows** you care about (e.g., amounts > $5000)
   - Use "Select All Rows" if all filtered results are good
5. **Choose columns** via right-click:
   - Keep: Client, Amount, Date
   - Remove: Internal Notes, Processing Code
6. **Export Selected**:
   - Click orange "📤 Export Selected" button
   - Choose "📊 Excel" for better formatting
   - Save as `VIP_transactions_summary.xlsx`

✅ **Result:** Clean Excel file with exactly what you need!

---

## 🎨 Selection Display

The bottom of the Data Explorer shows your current selections:

```
ℹ️ 5 row(s) selected | 4 columns selected
```

Updates in real-time as you make changes.

---

## ⚡ Performance Tips

### For Large Datasets:
- Use **Search/Filter first** to reduce visible rows
- Then select from filtered results
- Faster than selecting from 50,000 rows!

### Export Limits:
- Max **5,000 rows** displayed at once
- To export more: Reload dataset without search

---

## 🔄 Export Formats

### CSV
- Universal format
- Works in Excel, Python, R, databases
- Lightweight, no special dependencies
- Click: **"💾 Export All"** or choose CSV in "📤 Export Selected"

### Excel (.xlsx)
- Rich formatting support
- Requires `openpyxl` package (included in requirements)
- Better for presentations
- Choose when prompted: **"📊 Excel"**

If Excel export fails, ensure openpyxl is installed:
```bash
pip install openpyxl
```

---

## 🚨 Important Notes

### Row Selection State:
- Selections are **cleared** when you switch datasets
- Selections **persist** during search/filter
- Checkbox state shows in real-time

### Column Selection State:
- Column choices **reset** when you load a new dataset
- Right-click menu always available
- "Show All Columns" resets all columns to visible

### Search & Filter:
- Selection works on **filtered results**
- Export always uses correct original data
- Can't export rows you haven't selected, even if filtered

---

## ✅ Checklist Before Exporting

- [ ] Dataset loaded (dropdown shows selection)
- [ ] Search/filter applied if needed
- [ ] Rows selected (selection count > 0)
- [ ] Columns chosen via right-click (optional)
- [ ] Export format decided (CSV or Excel)
- [ ] File location ready

---

## 🎓 Quick Reference

| Action | Button/Menu | Keyboard | Effect |
|--------|------------|----------|--------|
| Select all visible | ☑️ Select All Rows | - | Checks all rows |
| Clear selection | ☐ Clear Selection | - | Unchecks all rows |
| Toggle column | Right-click header | Context Menu | Show/hide column |
| Export all data | 💾 Export All (CSV) | - | Full dataset to CSV |
| Export selection | 📤 Export Selected | - | Selected data to CSV/Excel |

---

## 🆘 Troubleshooting

### "Please select at least one row to export!"
- **Problem:** Clicked "Export Selected" without checking rows
- **Solution:** Check boxes next to rows you want, then click export

### Excel export shows error
- **Problem:** openpyxl not installed
- **Solution:** Run `pip install openpyxl` in terminal

### Selection cleared when switching datasets
- **Problem:** Loading different dataset
- **Solution:** This is normal - selections don't carry between datasets

### Columns not showing in export
- **Problem:** Columns were hidden via right-click menu
- **Solution:** Right-click header → "Show All Columns" to restore

---

## 💡 Pro Tips

1. **Quick select pattern:** Use search to find similar rows, then "Select All Rows"
2. **Minimize file size:** Uncheck unnecessary columns before export
3. **Audit trail:** Export different selections separately for analysis
4. **Backup first:** Keep "Export All" copies before selective exports

---

Happy exporting! 🚀
