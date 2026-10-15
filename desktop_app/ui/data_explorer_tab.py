"""
Data Explorer Tab - WITH AI INTEGRATION & SELECTIVE EXPORT
Click on any client ID to ask AI about them
Select rows & columns to export selectively
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QPushButton, QFileDialog,
    QMessageBox, QLineEdit, QFrame, QCheckBox, QMenu
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QFont, QColor
import pandas as pd


class DataExplorerTab(QWidget):
    """Data explorer with AI integration and selective export"""
    
    # Signal to communicate with AI tab
    ask_ai_about_id = pyqtSignal(str)
    
    def __init__(self, dataframes):
        super().__init__()
        self.dataframes = dataframes
        self.current_df = None
        self.current_df_filtered = None  # Track filtered/displayed data
        self.max_display_rows = 5000
        self.selected_client_id = None
        
        # Selection tracking
        self.selected_rows = set()  # Track which display rows are selected
        self.selected_columns = None  # None = all columns, or list of column names
        self.row_checkboxes = {}  # Map row index to checkbox item
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        header_layout = QVBoxLayout()
        header_frame.setLayout(header_layout)
        
        title = QLabel("🔍 Data Explorer")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Browse, search, and ask AI about your data")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #9ca3af;")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_frame)
        
        # Controls
        controls = self.create_controls()
        layout.addWidget(controls)
        
        # AI Action Bar (shows when ID is selected)
        self.ai_action_bar = self.create_ai_action_bar()
        self.ai_action_bar.setVisible(False)
        layout.addWidget(self.ai_action_bar)
        
        # Info label
        self.info_label = QLabel()
        self.info_label.setFont(QFont("Arial", 10))
        self.info_label.setStyleSheet("color: #9ca3af; padding: 8px;")
        layout.addWidget(self.info_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1f2937;
                alternate-background-color: #262730;
                color: white;
                gridline-color: #374151;
                border: 1px solid #374151;
                border-radius: 4px;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #3b82f6;
            }
            QHeaderView::section {
                background-color: #374151;
                color: white;
                padding: 10px;
                border: 1px solid #4b5563;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        self.table.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.table)
        
        # Buttons
        buttons = self.create_buttons()
        layout.addWidget(buttons)
        
        # Load first dataset
        if self.dataframes:
            first_key = list(self.dataframes.keys())[0]
            self.dataset_combo.setCurrentText(first_key)
            self.load_dataset(first_key)
    
    def create_controls(self):
        """Create control section"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout = QHBoxLayout()
        widget.setLayout(layout)
        
        # Dataset selector
        label = QLabel("Dataset:")
        label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        label.setStyleSheet("color: white;")
        layout.addWidget(label)
        
        self.dataset_combo = QComboBox()
        self.dataset_combo.addItems(list(self.dataframes.keys()))
        self.dataset_combo.currentTextChanged.connect(self.load_dataset)
        self.dataset_combo.setMinimumWidth(350)
        self.dataset_combo.setStyleSheet("""
            QComboBox {
                background-color: #374151;
                color: white;
                border: 1px solid #4b5563;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
            }
            QComboBox QAbstractItemView {
                background-color: #374151;
                color: white;
                selection-background-color: #3b82f6;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.dataset_combo)
        
        layout.addStretch()
        
        # Search box
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: white; font-size: 11px;")
        layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search in table...")
        self.search_box.setMinimumWidth(200)
        self.search_box.textChanged.connect(self.filter_table)
        self.search_box.setStyleSheet("""
            QLineEdit {
                background-color: #374151;
                color: white;
                border: 1px solid #4b5563;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.search_box)
        
        return widget
    
    def create_ai_action_bar(self):
        """Create AI action bar (shown when ID is selected)"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #3b82f6;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        layout = QHBoxLayout()
        widget.setLayout(layout)
        
        # Info icon
        icon = QLabel("🤖")
        icon.setFont(QFont("Segoe UI", 20))
        layout.addWidget(icon)
        
        # Selected ID label
        self.selected_id_label = QLabel("No ID selected")
        self.selected_id_label.setFont(QFont("Segoe UI", 11))
        self.selected_id_label.setStyleSheet("color: white;")
        self.selected_id_label.setWordWrap(True)
        layout.addWidget(self.selected_id_label, 1)
        
        # Ask AI button
        ask_ai_btn = QPushButton("🧠 Ask AI About This Client")
        ask_ai_btn.setMinimumHeight(40)
        ask_ai_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 25px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        ask_ai_btn.clicked.connect(self.ask_ai_about_selected)
        layout.addWidget(ask_ai_btn)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setMaximumWidth(40)
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        close_btn.clicked.connect(lambda: self.ai_action_bar.setVisible(False))
        layout.addWidget(close_btn)
        
        return widget
    
    def create_buttons(self):
        """Create button section with selection controls and export options"""
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)
        
        # Selection Info Label
        self.selection_info_label = QLabel("ℹ️ No rows selected")
        self.selection_info_label.setStyleSheet("color: #9ca3af; font-size: 11px;")
        layout.addWidget(self.selection_info_label)
        
        layout.addSpacing(10)
        
        # Select All button
        select_all_btn = QPushButton("☑️ Select All Rows")
        select_all_btn.setMinimumHeight(40)
        select_all_btn.setMaximumWidth(150)
        select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        select_all_btn.clicked.connect(self.select_all_rows)
        layout.addWidget(select_all_btn)
        
        # Clear Selection button
        clear_btn = QPushButton("☐ Clear Selection")
        clear_btn.setMinimumHeight(40)
        clear_btn.setMaximumWidth(150)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        clear_btn.clicked.connect(self.clear_selection)
        layout.addWidget(clear_btn)
        
        layout.addStretch()
        
        # Export All button
        export_all_btn = QPushButton("💾 Export All (CSV)")
        export_all_btn.setMinimumHeight(40)
        export_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                padding: 10px 25px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        export_all_btn.clicked.connect(self.export_all_csv)
        layout.addWidget(export_all_btn)
        
        # Export Selected button
        export_sel_btn = QPushButton("📤 Export Selected")
        export_sel_btn.setMinimumHeight(40)
        export_sel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                padding: 10px 25px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        export_sel_btn.clicked.connect(self.export_selected)
        layout.addWidget(export_sel_btn)
        
        return widget
    
    def on_item_clicked(self, item):
        """Handle item click - detect if it's a client ID"""
        # Skip checkbox column
        if item.column() == 0:
            return
        
        # Get column name (adjust for checkbox column)
        col_idx = item.column() - 1  # Subtract 1 for checkbox column
        header = self.table.horizontalHeaderItem(item.column())
        if not header:
            return
        
        col_name = header.text()
        
        # Check if this is a client ID column
        if 'client' in col_name.lower() or 'ch_code' in col_name.lower():
            client_id = item.text()
            
            # Ignore NULL/EMPTY values
            if client_id in ['[NULL]', '[EMPTY]', 'nan', 'None', '']:
                return
            
            # Store and show AI action bar
            self.selected_client_id = client_id
            display_id = client_id[:48] + "..." if len(client_id) > 48 else client_id
            self.selected_id_label.setText(f"Selected: {display_id}")
            self.ai_action_bar.setVisible(True)
    
    def ask_ai_about_selected(self):
        """Send selected client ID to AI tab"""
        if not self.selected_client_id:
            QMessageBox.warning(self, "No Selection", "Please click on a client ID first.")
            return
        
        # Emit signal to switch to AI tab and query
        self.ask_ai_about_id.emit(self.selected_client_id)
        
        QMessageBox.information(
            self,
            "Switched to AI Tab",
            f"Asking AI about client:\n{self.selected_client_id[:48]}...\n\n"
            f"Check the AI Advisor tab for the response!"
        )
    
    def load_dataset(self, dataset_name):
        """Load selected dataset into table"""
        if not dataset_name or dataset_name not in self.dataframes:
            return
        
        df = self.dataframes[dataset_name]
        self.current_df = df.copy()
        self.selected_columns = None  # Reset column selection
        
        # Show info
        display_rows = min(len(df), self.max_display_rows)
        null_count = df.isnull().sum().sum()
        memory_mb = df.memory_usage(deep=True).sum() / 1024**2
        
        # Check if this dataset has client IDs
        has_client_id = any('client' in col.lower() or 'ch_code' in col.lower() 
                           for col in df.columns)
        
        info_text = (
            f"📊 Total: {len(df):,} rows × {len(df.columns)} columns | "
            f"Displaying: {display_rows:,} rows | "
            f"Null values: {null_count:,} | "
            f"Memory: {memory_mb:.2f} MB"
        )
        
        if has_client_id:
            info_text += " | 🤖 Click on any Client ID to ask AI about them!"
        
        self.info_label.setText(info_text)
        
        # Clear search
        self.search_box.clear()
        
        # Hide AI bar
        self.ai_action_bar.setVisible(False)
        
        # Display data
        self.display_dataframe(df.head(display_rows))
    
    def filter_table(self, search_text):
        """Filter table based on search text"""
        if self.current_df is None:
            return
        
        if not search_text:
            # Show all data
            self.display_dataframe(self.current_df.head(self.max_display_rows))
            return
        
        # Filter dataframe
        mask = self.current_df.astype(str).apply(
            lambda x: x.str.contains(search_text, case=False, na=False)
        ).any(axis=1)
        
        filtered = self.current_df[mask].head(self.max_display_rows)
        
        # Update info
        self.info_label.setText(
            f"🔍 Search results: {len(filtered):,} rows matching '{search_text}'"
        )
        
        # Display filtered data
        self.display_dataframe(filtered)
    
    def display_dataframe(self, df):
        """Display dataframe in table with row selection checkboxes"""
        # Store filtered data for later use
        self.current_df_filtered = df.copy()
        
        # Clean data for display
        df_display = df.copy()
        df_display = df_display.fillna('[NULL]')
        df_display = df_display.replace('', '[EMPTY]')
        
        # Convert to string
        for col in df_display.columns:
            df_display[col] = df_display[col].astype(str)
        
        # Set dimensions (add 1 for checkbox column)
        self.table.clear()
        self.row_checkboxes = {}
        self.selected_rows = set()
        
        self.table.setRowCount(len(df_display))
        self.table.setColumnCount(len(df_display.columns) + 1)  # +1 for checkbox
        
        # Set headers (with checkbox header)
        headers = ['✓'] + list(df_display.columns)
        self.table.setHorizontalHeaderLabels(headers)
        
        # Set up context menu for headers
        self.table.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self.show_column_menu)
        
        # Populate data
        for i in range(len(df_display)):
            # Checkbox column (column 0)
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(checkbox_item.flags() | Qt.ItemIsUserCheckable)
            checkbox_item.setCheckState(Qt.Unchecked)
            checkbox_item.setFlags(checkbox_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, checkbox_item)
            self.row_checkboxes[i] = checkbox_item
            
            # Data columns (starting from column 1)
            for j, col in enumerate(df_display.columns):
                value = str(df_display.iloc[i, j])
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                
                # Color code null values
                if value in ['[NULL]', '[EMPTY]', 'nan', 'None']:
                    item.setForeground(QColor(239, 68, 68))
                
                # Highlight client ID columns
                if 'client' in col.lower() or 'ch_code' in col.lower():
                    if value not in ['[NULL]', '[EMPTY]', 'nan', 'None']:
                        item.setBackground(QColor(59, 130, 246, 40))  # Light blue background
                
                self.table.setItem(i, j + 1, item)
        
        # Connect checkbox changes
        self.table.itemChanged.connect(self.on_checkbox_changed)
        
        # Resize columns
        self.table.resizeColumnsToContents()
        
        # Set minimum widths
        self.table.setColumnWidth(0, 35)  # Checkbox column
        for i in range(1, len(headers)):
            if self.table.columnWidth(i) < 120:
                self.table.setColumnWidth(i, 120)
        
        # Update selection display
        self.update_selection_info()
    
    def on_checkbox_changed(self, item):
        """Handle checkbox state changes for row selection"""
        # Only process checkbox items (column 0)
        if item.column() != 0:
            return
        
        row = item.row()
        if item.checkState() == Qt.Checked:
            self.selected_rows.add(row)
        else:
            self.selected_rows.discard(row)
        
        # Update selection display
        self.update_selection_info()
    
    def update_selection_info(self):
        """Update the selection info label"""
        if not self.selected_rows:
            self.selection_info_label.setText("ℹ️ No rows selected")
        else:
            col_info = ""
            if self.selected_columns is not None:
                col_info = f" | {len(self.selected_columns)} columns selected"
            self.selection_info_label.setText(
                f"ℹ️ {len(self.selected_rows)} row(s) selected{col_info}"
            )
    
    def select_all_rows(self):
        """Select all visible rows"""
        for row_idx in self.row_checkboxes:
            self.row_checkboxes[row_idx].setCheckState(Qt.Checked)
        self.selected_rows = set(self.row_checkboxes.keys())
        self.update_selection_info()
    
    def clear_selection(self):
        """Clear all row selections"""
        for row_idx in self.row_checkboxes:
            self.row_checkboxes[row_idx].setCheckState(Qt.Unchecked)
        self.selected_rows = set()
        self.update_selection_info()
    
    def show_column_menu(self, position):
        """Show right-click context menu for columns"""
        menu = QMenu(self)
        
        # Get clicked column
        col_idx = self.table.horizontalHeader().logicalIndexAt(position)
        
        if col_idx == 0:  # Checkbox column
            return
        
        # Get all columns (excluding checkbox column)
        all_columns = [self.table.horizontalHeaderItem(i).text() 
                      for i in range(1, self.table.columnCount())]
        
        # Show all / Hide specific column options
        show_all_action = menu.addAction("Show All Columns")
        show_all_action.triggered.connect(self.show_all_columns)
        
        menu.addSeparator()
        
        # List of columns
        for col_name in all_columns:
            action = menu.addAction(f"✓ {col_name}")
            action.setCheckable(True)
            # Check if this column is in selected columns
            if self.selected_columns is None:
                action.setChecked(True)
            else:
                action.setChecked(col_name in self.selected_columns)
            
            # Create a closure to capture col_name
            def make_toggle(name):
                def toggle_column(checked):
                    self.toggle_column_selection(name, checked)
                return toggle_column
            
            action.triggered.connect(make_toggle(col_name))
        
        # Show menu
        menu.exec_(self.table.horizontalHeader().mapToGlobal(position))
    
    def toggle_column_selection(self, col_name, checked):
        """Toggle a column's selection state"""
        if self.selected_columns is None:
            # If all columns are selected, start with all and remove this one
            all_cols = [self.table.horizontalHeaderItem(i).text() 
                       for i in range(1, self.table.columnCount())]
            self.selected_columns = all_cols.copy()
        
        if checked:
            if col_name not in self.selected_columns:
                self.selected_columns.append(col_name)
        else:
            if col_name in self.selected_columns:
                self.selected_columns.remove(col_name)
        
        # If all columns are selected again, reset to None (all)
        all_cols = [self.table.horizontalHeaderItem(i).text() 
                   for i in range(1, self.table.columnCount())]
        if len(self.selected_columns) == len(all_cols):
            self.selected_columns = None
        
        self.update_selection_info()
    
    def show_all_columns(self):
        """Show all columns"""
        self.selected_columns = None
        self.update_selection_info()
    
    def export_all_csv(self):
        """Export entire current dataset to CSV"""
        if self.current_df is None:
            QMessageBox.warning(self, "No Data", "No dataset loaded!")
            return
        
        # Get file path
        dataset_name = self.dataset_combo.currentText()
        default_name = f"{dataset_name}_export_all.csv"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export All Data to CSV",
            default_name,
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                self.current_df.to_csv(file_path, index=False, encoding='utf-8')
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"✅ Data exported successfully!\n\n"
                    f"File: {file_path}\n"
                    f"Rows: {len(self.current_df):,}\n"
                    f"Columns: {len(self.current_df.columns)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"❌ Error exporting data:\n\n{str(e)}"
                )
    
    def export_selected(self):
        """Export selected rows and columns"""
        if self.current_df is None:
            QMessageBox.warning(self, "No Data", "No dataset loaded!")
            return
        
        if not self.selected_rows:
            QMessageBox.warning(self, "No Selection", 
                "Please select at least one row to export!")
            return
        
        # Get selected data
        selected_indices = sorted(list(self.selected_rows))
        
        # Get actual dataframe indices (from filtered data)
        if self.current_df_filtered is not None:
            actual_indices = self.current_df_filtered.index[selected_indices].tolist()
            df_export = self.current_df.loc[actual_indices].copy()
        else:
            df_export = self.current_df.iloc[selected_indices].copy()
        
        # Filter columns if needed
        if self.selected_columns is not None:
            df_export = df_export[self.selected_columns]
        
        if df_export.empty:
            QMessageBox.warning(self, "No Data", 
                "No data selected for export!")
            return
        
        # Ask for export format
        msg = QMessageBox()
        msg.setWindowTitle("Export Selected Data")
        msg.setText("Choose export format:")
        csv_btn = msg.addButton("📄 CSV", QMessageBox.AcceptRole)
        excel_btn = msg.addButton("📊 Excel", QMessageBox.AcceptRole)
        msg.addButton("❌ Cancel", QMessageBox.RejectRole)
        
        msg.exec_()
        
        if msg.clickedButton() == csv_btn:
            self._export_to_csv(df_export)
        elif msg.clickedButton() == excel_btn:
            self._export_to_excel(df_export)
    
    def _export_to_csv(self, df):
        """Export dataframe to CSV"""
        dataset_name = self.dataset_combo.currentText()
        default_name = f"{dataset_name}_selected.csv"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Selected Data to CSV",
            default_name,
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                df.to_csv(file_path, index=False, encoding='utf-8')
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"✅ Selected data exported successfully!\n\n"
                    f"File: {file_path}\n"
                    f"Rows: {len(df):,}\n"
                    f"Columns: {len(df.columns)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"❌ Error exporting data:\n\n{str(e)}"
                )
    
    def _export_to_excel(self, df):
        """Export dataframe to Excel"""
        try:
            import openpyxl
        except ImportError:
            QMessageBox.warning(self, "Missing Package",
                "Excel export requires 'openpyxl'.\n"
                "Install it with: pip install openpyxl")
            return
        
        dataset_name = self.dataset_combo.currentText()
        default_name = f"{dataset_name}_selected.xlsx"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Selected Data to Excel",
            default_name,
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                df.to_excel(file_path, index=False, engine='openpyxl')
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"✅ Selected data exported successfully!\n\n"
                    f"File: {file_path}\n"
                    f"Rows: {len(df):,}\n"
                    f"Columns: {len(df.columns)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"❌ Error exporting data:\n\n{str(e)}"
                )
