"""
KPI Dashboard Tab - Displays KPIs from Product and Savings data
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QPushButton, QMessageBox, QFileDialog,
    QFrame, QScrollArea, QTabWidget, QTextEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import pandas as pd
from pathlib import Path


class KPICalculatorThread(QThread):
    """Thread for calculating KPIs without freezing UI"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(object, dict, dict, object)  # summary, details, links, analyzer
    error = pyqtSignal(str)
    
    def __init__(self, dataframes):
        super().__init__()
        self.dataframes = dataframes
        
    def run(self):
        try:
            from desktop_app.core.kpi_analyzer import analyze_products_savings
            
            self.progress.emit("📊 Analyzing KPIs...")
            summary, details, links, analyzer = analyze_products_savings(self.dataframes)
            
            self.progress.emit("✅ KPI analysis complete!")
            self.finished.emit(summary, details, links, analyzer)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.error.emit(f"{str(e)}\n\n{error_details}")


class KPIDashboardTab(QWidget):
    """KPI Dashboard displaying product and savings analysis"""
    
    def __init__(self, dataframes):
        super().__init__()
        self.dataframes = dataframes
        self.kpi_summary = None
        self.kpi_details = None
        self.field_links = None
        self.kpi_analyzer = None
        
        self.init_ui()
        
        # Start KPI calculation
        if dataframes:
            self.calculate_kpis()
    
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
        
        title = QLabel("📊 Product & Savings KPI Dashboard")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Analysis of Product Sales and Savings Objectives")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #9ca3af;")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_frame)
        
        # Tabs for different KPI views
        self.kpi_tabs = QTabWidget()
        layout.addWidget(self.kpi_tabs)
        
        # Summary tab
        self.summary_widget = self.create_summary_tab()
        self.kpi_tabs.addTab(self.summary_widget, "📈 Summary")
        
        # Product KPIs tab
        self.product_widget = self.create_product_tab()
        self.kpi_tabs.addTab(self.product_widget, "🏆 Top Products")
        
        # Field Links tab
        self.links_widget = self.create_links_tab()
        self.kpi_tabs.addTab(self.links_widget, "🔗 Field Links")
        
        # Export buttons
        export_frame = QFrame()
        export_frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        export_layout = QHBoxLayout()
        export_frame.setLayout(export_layout)
        
        export_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh KPIs")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 10px 25px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        refresh_btn.clicked.connect(self.calculate_kpis)
        export_layout.addWidget(refresh_btn)
        
        # Export button
        export_btn = QPushButton("📤 Export KPIs")
        export_btn.setMinimumHeight(40)
        export_btn.setStyleSheet("""
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
        export_btn.clicked.connect(self.export_kpis)
        export_layout.addWidget(export_btn)
        
        layout.addWidget(export_frame)
    
    def create_summary_tab(self) -> QWidget:
        """Create summary statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Statistics display
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #1f2937;
                color: white;
                border: 1px solid #374151;
                border-radius: 4px;
                font-family: Consolas;
                font-size: 11px;
                padding: 15px;
            }
        """)
        layout.addWidget(self.summary_text)
        
        return widget
    
    def create_product_tab(self) -> QWidget:
        """Create top products table tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Table for top products
        self.product_table = QTableWidget()
        self.product_table.setAlternatingRowColors(True)
        self.product_table.setStyleSheet("""
            QTableWidget {
                background-color: #1f2937;
                alternate-background-color: #262730;
                color: white;
                gridline-color: #374151;
                border: 1px solid #374151;
                border-radius: 4px;
                font-size: 10px;
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
            }
        """)
        layout.addWidget(self.product_table)
        
        return widget
    
    def create_links_tab(self) -> QWidget:
        """Create field links tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Text area for field links
        self.links_text = QTextEdit()
        self.links_text.setReadOnly(True)
        self.links_text.setStyleSheet("""
            QTextEdit {
                background-color: #1f2937;
                color: white;
                border: 1px solid #374151;
                border-radius: 4px;
                font-family: Consolas;
                font-size: 10px;
                padding: 15px;
            }
        """)
        layout.addWidget(self.links_text)
        
        return widget
    
    def calculate_kpis(self):
        """Calculate KPIs in background thread"""
        self.calculator_thread = KPICalculatorThread(self.dataframes)
        self.calculator_thread.progress.connect(self.on_kpi_progress)
        self.calculator_thread.finished.connect(self.on_kpi_finished)
        self.calculator_thread.error.connect(self.on_kpi_error)
        self.calculator_thread.start()
    
    def on_kpi_progress(self, message):
        """Handle progress updates"""
        print(f"🔄 {message}")
    
    def on_kpi_finished(self, summary, details, links, analyzer):
        """Handle KPI calculation completion"""
        self.kpi_summary = summary
        self.kpi_details = details
        self.field_links = links
        self.kpi_analyzer = analyzer
        
        # Update displays
        self.update_summary_display()
        self.update_product_table()
        self.update_links_display()
    
    def on_kpi_error(self, error_msg):
        """Handle KPI calculation errors"""
        QMessageBox.critical(
            self,
            "KPI Calculation Error",
            f"❌ Error calculating KPIs:\n\n{error_msg}"
        )
    
    def update_summary_display(self):
        """Update summary statistics display"""
        if self.kpi_details is None:
            return
        
        text = "📊 OVERALL KPI SUMMARY\n" + "="*60 + "\n\n"
        
        if 'Overall' in self.kpi_details:
            overall = self.kpi_details['Overall']
            for key, value in overall.items():
                if isinstance(value, float):
                    text += f"{key:.<35} {value:>15,.2f}\n"
                else:
                    text += f"{key:.<35} {value:>15,}\n"
        
        # Client segments
        text += "\n📍 BY CLIENT SEGMENT\n" + "-"*60 + "\n"
        if 'By Client Segment' in self.kpi_details:
            for segment, data in self.kpi_details['By Client Segment'].items():
                text += f"\n{segment}:\n"
                for key, value in data.items():
                    if isinstance(value, float):
                        text += f"  {key}: {value:,.2f}\n"
                    else:
                        text += f"  {key}: {value:,}\n"
        
        # Activity sectors
        text += "\n🏭 BY ACTIVITY SECTOR\n" + "-"*60 + "\n"
        if 'By Activity Sector' in self.kpi_details:
            sectors = self.kpi_details['By Activity Sector']
            # Show top 10 sectors
            for idx, (sector, data) in enumerate(list(sectors.items())[:10]):
                text += f"\n{sector}:\n"
                for key, value in data.items():
                    if isinstance(value, float):
                        text += f"  {key}: {value:,.2f}\n"
                    else:
                        text += f"  {key}: {value:,}\n"
        
        self.summary_text.setText(text)
    
    def update_product_table(self):
        """Update product table with top products"""
        if self.kpi_summary is None or self.kpi_summary.empty:
            return
        
        df = self.kpi_summary.head(20)  # Top 20 products
        
        # Set table dimensions
        self.product_table.setRowCount(len(df))
        self.product_table.setColumnCount(len(df.columns))
        
        # Set headers
        headers = list(df.columns)
        self.product_table.setHorizontalHeaderLabels(headers)
        
        # Populate data
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                value = df.iloc[i, j]
                
                # Format numbers
                if isinstance(value, (int, float)):
                    if isinstance(value, float):
                        formatted = f"{value:,.2f}"
                    else:
                        formatted = f"{value:,}"
                else:
                    formatted = str(value)
                
                item = QTableWidgetItem(formatted)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                
                # Color highlighting for high values
                if isinstance(value, (int, float)) and 'Total' in col:
                    if value > df[col].quantile(0.75):
                        item.setBackground(QColor(16, 185, 129, 40))  # Green tint
                
                self.product_table.setItem(i, j, item)
        
        # Resize columns
        self.product_table.resizeColumnsToContents()
        
        # Set minimum widths
        for i in range(len(headers)):
            if self.product_table.columnWidth(i) < 100:
                self.product_table.setColumnWidth(i, 100)
    
    def update_links_display(self):
        """Update field links display"""
        if self.field_links is None:
            return
        
        text = "🔗 FIELD LINKS BETWEEN DATASETS\n" + "="*70 + "\n\n"
        
        for section, content in self.field_links.items():
            text += f"\n{'■ ' + section}\n" + "-"*70 + "\n"
            
            if isinstance(content, dict):
                for key, value in content.items():
                    if isinstance(value, dict):
                        text += f"\n  {key}:\n"
                        for k, v in value.items():
                            text += f"    • {k}: {v}\n"
                    else:
                        text += f"  • {key}: {value}\n"
            else:
                text += f"  {content}\n"
        
        self.links_text.setText(text)
    
    def export_kpis(self):
        """Export KPIs to CSV files"""
        if self.kpi_analyzer is None:
            QMessageBox.warning(self, "No Data", "No KPI data to export!")
            return
        
        # Get export directory
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Export KPIs",
            str(Path.cwd())
        )
        
        if not output_dir:
            return
        
        # Export
        success = self.kpi_analyzer.export_kpis(output_dir)
        
        if success:
            QMessageBox.information(
                self,
                "Export Successful",
                f"✅ KPIs exported successfully!\n\n"
                f"Location: {output_dir}\n\n"
                f"Files created:\n"
                f"  • kpi_summary.csv\n"
                f"  • kpi_monthly_trend.csv\n"
                f"  • kpi_segment_distribution.csv\n"
                f"  • field_links.txt"
            )
        else:
            QMessageBox.critical(
                self,
                "Export Failed",
                "❌ Error exporting KPIs"
            )
