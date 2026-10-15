# Technical Implementation Guide - Data Explorer Selective Export

## Architecture Overview

The Data Explorer Tab now supports selective row and column export through an enhanced table display system.

```
┌─────────────────────────────────────────────────────────────┐
│ Data Explorer Tab                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Table Display with Checkboxes                       │   │
│  │  ✓  │ Column1  │ Column2  │ Column3                 │   │
│  │ ─── ├──────────┼──────────┼─────────                 │   │
│  │ ☑   │ Value1   │ Value2   │ Value3                  │   │
│  │ ☐   │ Value4   │ Value5   │ Value6                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Selection Status: 1 row(s) selected | 2 cols...    │   │
│  │                                                     │   │
│  │ [Select All] [Clear] ... [Export All] [Export Sel] │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Data Structures

### 1. **Row Selection Tracking**
```python
self.selected_rows = set()  # Set of display row indices (0-based)
self.row_checkboxes = {}    # Map: row_index -> QTableWidgetItem (checkbox)
```

### 2. **Column Selection Tracking**
```python
self.selected_columns = None  # None = all columns
                              # List[str] = specific column names
```

### 3. **Data Preservation**
```python
self.current_df = None              # Original full dataset
self.current_df_filtered = None      # Currently displayed data (search results)
```

---

## Key Methods

### Row Selection Management

#### `on_checkbox_changed(item)`
- **Triggered:** When checkbox state changes
- **Logic:**
  - If checkbox column (0) and checked → add to `selected_rows`
  - If unchecked → remove from `selected_rows`
  - Update UI status
- **Performance:** O(1) set operation

#### `select_all_rows()`
- **Action:** Programmatically check all visible row checkboxes
- **Logic:** Iterate `row_checkboxes` dict, set all to `Qt.Checked`
- **Result:** `selected_rows = set(row_checkboxes.keys())`

#### `clear_selection()`
- **Action:** Uncheck all row checkboxes
- **Result:** `selected_rows = set()` (empty)

### Column Selection Management

#### `show_column_menu(position)`
- **Triggered:** Right-click on column header
- **Flow:**
  1. Get clicked column index from header
  2. Create QMenu with column options
  3. Each column is QAction with checkable=True
  4. Show current state based on `self.selected_columns`
  5. Trigger callbacks on selection

#### `toggle_column_selection(col_name, checked)`
- **Logic:**
  ```python
  if self.selected_columns is None:
      # All currently selected, switch to list mode
      self.selected_columns = [all columns]
  
  if checked:
      add col_name to selected_columns
  else:
      remove col_name from selected_columns
  
  if len(selected_columns) == total_columns:
      # Back to "all" mode
      self.selected_columns = None
  ```
- **Purpose:** Allow toggling between "show all" and "show specific"

#### `show_all_columns()`
- **Action:** Reset `self.selected_columns = None`
- **Effect:** Next export includes all columns

### Display Management

#### `display_dataframe(df)`
- **Input:** DataFrame to display (may be filtered)
- **Process:**
  1. Store as `self.current_df_filtered`
  2. Add checkbox column (index 0)
  3. Add data columns (index 1+)
  4. Initialize `row_checkboxes` mapping
  5. Set up context menu on headers
  6. Connect checkbox change signals
- **Column Structure:**
  ```
  Index 0: Checkboxes (visual only, not in data)
  Index 1+: Actual DataFrame columns
  ```

### Export Methods

#### `export_selected()`
- **Validation:**
  1. Check `self.current_df is not None`
  2. Check `len(self.selected_rows) > 0`
- **Processing:**
  ```python
  # Get row indices in display order
  selected_indices = sorted(list(self.selected_rows))
  
  # Map display indices to original DataFrame indices
  if self.current_df_filtered is not None:
      actual_indices = self.current_df_filtered.index[selected_indices]
      df_export = self.current_df.loc[actual_indices]
  else:
      df_export = self.current_df.iloc[selected_indices]
  
  # Filter columns if specified
  if self.selected_columns is not None:
      df_export = df_export[self.selected_columns]
  ```
- **Export Flow:**
  1. Show format dialog (CSV or Excel)
  2. Route to `_export_to_csv()` or `_export_to_excel()`

#### `export_all_csv()`
- **Input:** Entire `self.current_df`
- **Output:** CSV file with all data
- **Ignores:** Selection state (always exports all)

#### `_export_to_csv(df)`
- **Steps:**
  1. Get save file path
  2. Call `df.to_csv(path, index=False, encoding='utf-8')`
  3. Show success/error message

#### `_export_to_excel(df)`
- **Steps:**
  1. Check if `openpyxl` installed
  2. Get save file path
  3. Call `df.to_excel(path, index=False, engine='openpyxl')`
  4. Handle import error gracefully

---

## UI Components

### Selection Status Label
```python
self.selection_info_label = QLabel("ℹ️ No rows selected")
# Updates with: "ℹ️ {n} row(s) selected | {m} columns selected"
```

### Control Buttons (Bottom Bar)
| Button | Action | Color |
|--------|--------|-------|
| ☑️ Select All Rows | `select_all_rows()` | Indigo (#6366f1) |
| ☐ Clear Selection | `clear_selection()` | Indigo (#6366f1) |
| 💾 Export All (CSV) | `export_all_csv()` | Green (#10b981) |
| 📤 Export Selected | `export_selected()` | Orange (#f59e0b) |

### Context Menu (Column Headers)
```
✓ Show All Columns       → self.show_all_columns()
─────────────────────
✓ Column 1               → toggle_column_selection("Column 1", checked)
✓ Column 2               → toggle_column_selection("Column 2", checked)
  Column 3               → toggle_column_selection("Column 3", checked)
```

---

## Data Flow: Export Selected

```
User clicks "📤 Export Selected"
    ↓
export_selected() validates
    ├─ current_df exists? ✓
    └─ selected_rows > 0? ✓
    ↓
Show format dialog
    ├─ User: CSV
    │  └─> _export_to_csv(df_export)
    │       ├─> File dialog
    │       ├─> df.to_csv()
    │       └─> Success message
    │
    └─ User: Excel
       └─> _export_to_excel(df_export)
           ├─> Check openpyxl
           ├─> File dialog
           ├─> df.to_excel()
           └─> Success message
```

---

## Handling Filtered Data

**Problem:** When user searches, `display_dataframe()` gets filtered data, but export needs original indices.

**Solution:** Track both:
```python
self.current_df          # Original full dataset (always present)
self.current_df_filtered # What's displayed now (may be filtered)
```

**Export Logic:**
```python
# Display row 5 might be original row 247 after filtering
selected_indices = [5, 10, 15]  # Display indices

# Get original indices from filtered data
actual_indices = self.current_df_filtered.index[selected_indices]
# actual_indices = [247, 512, 301]

# Get original rows
df_export = self.current_df.loc[actual_indices]
```

---

## Import Changes

New imports added to `data_explorer_tab.py`:
```python
from PyQt5.QtWidgets import (..., QMenu)
from PyQt5.QtCore import (..., QPoint)
```

---

## Dependencies

**New to requirements_desktop.txt:**
```
openpyxl>=3.0.0  # Excel export support
```

Fallback behavior: If not installed, shows user-friendly message.

---

## Performance Considerations

### Large Datasets (>5000 rows)
- Only **5000 rows displayed** at max
- Checkbox operations: O(n) where n ≤ 5000
- Selection tracking: O(1) set operations
- Column filtering: O(m) where m ≤ columns

### Memory Usage
- `selected_rows` set: Minimal (just indices)
- `row_checkboxes` dict: One QTableWidgetItem per visible row
- Total: ~5000 items max

### Export Performance
- CSV: `pandas.to_csv()` (native, fast)
- Excel: `pandas.to_excel()` with openpyxl (slower, but acceptable)

---

## Testing Checklist

- [ ] Single row selection → export works
- [ ] Multi-row selection → export includes all
- [ ] Select All → checks all rows
- [ ] Clear → unchecks all rows
- [ ] Right-click column → menu appears
- [ ] Toggle column → export includes/excludes correctly
- [ ] Search → selection persists on filtered data
- [ ] Switch dataset → selection clears
- [ ] Export CSV → file created with correct data
- [ ] Export Excel → file created (if openpyxl installed)
- [ ] Export without selection → warning shown
- [ ] Export empty selection → validation catches

---

## Error Handling

### No Dataset Loaded
```python
if self.current_df is None:
    QMessageBox.warning(self, "No Data", "No dataset loaded!")
    return
```

### No Selection Made
```python
if not self.selected_rows:
    QMessageBox.warning(self, "No Selection", 
        "Please select at least one row to export!")
    return
```

### Excel Support Missing
```python
try:
    import openpyxl
except ImportError:
    QMessageBox.warning(self, "Missing Package",
        "Excel export requires 'openpyxl'.\n"
        "Install it with: pip install openpyxl")
    return
```

---

## Future Enhancements

1. **Column Reordering:** Drag headers to reorder before export
2. **Row Filtering UI:** Advanced filters (numeric ranges, dates, regex)
3. **Export Templates:** Save common selections
4. **Batch Export:** Export multiple selections to separate files
5. **Data Validation:** Show data quality before export
6. **Column Sorting:** Sort by any column, persist in export
7. **Format Options:** CSV delimiters, Excel sheets, JSON support
