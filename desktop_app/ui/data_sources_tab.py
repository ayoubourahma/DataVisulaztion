"""
Data Sources & Visualization Tab
Shows how data was collected and provides visual insights
"""
import os
import json
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QScrollArea,
    QLabel, QPushButton, QGridLayout, QGroupBox, QTextEdit, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd


class DataSourcesTab(QWidget):
    """Tab to show data sources and visualization"""
    
    def __init__(self, dataframes, analysis, data_folder="data"):
        super().__init__()
        self.dataframes = dataframes
        self.analysis = analysis
        self.data_folder = Path(data_folder)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #0e1117;
                color: white;
            }
            QGroupBox {
                color: white;
                border: 1px solid #374151;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QLabel {
                color: white;
            }
        """)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Main tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #374151;
                background-color: #0e1117;
            }
            QTabBar::tab {
                background: #1f2937;
                color: #9ca3af;
                padding: 10px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #3b82f6;
                color: white;
            }
        """)
        
        # Tab 1: Data Sources Overview
        tab1 = self.create_sources_tab()
        tabs.addTab(tab1, "📂 Data Sources")
        
        # Tab 2: Data Distribution Charts
        tab2 = self.create_charts_tab()
        tabs.addTab(tab2, "📊 Data Distribution")
        
        # Tab 3: Data Methodology
        tab3 = self.create_methodology_tab()
        tabs.addTab(tab3, "📋 Collection Methodology")
        
        layout.addWidget(tabs)
    
    def create_header(self):
        """Create header"""
        widget = QWidget()
        widget.setStyleSheet("background-color: #1f2937; padding: 15px; border-radius: 8px; margin: 10px;")
        layout = QHBoxLayout()
        widget.setLayout(layout)
        
        title = QLabel("📊 Data Sources & Visualization")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)
        
        subtitle = QLabel("Client Meeting - Data Collection & Analysis Overview")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #9ca3af;")
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        return widget
    
    def create_sources_tab(self):
        """Create data sources overview tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #0e1117;")
        
        # Summary stats
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #0e1117;
                border: none;
            }
        """)
        
        container = QWidget()
        container.setStyleSheet("background-color: #0e1117;")
        grid = QGridLayout()
        container.setLayout(grid)
        
        # Get data sources info
        row = 0
        
        # Title
        title_label = QLabel("📂 Data Sources Summary")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet("color: #60a5fa; padding: 10px;")
        grid.addWidget(title_label, row, 0, 1, 2)
        row += 1
        
        # Data source statistics
        sources_info = [
            ("Savings Data (Objectif Epargne)", f"{len(self.dataframes.get('src_objectif_epargne_cmc', pd.DataFrame())):,} records", "💾"),
            ("Activity Data (Real-time)", f"{len(self.dataframes.get('src_activité_applicative_realtime', pd.DataFrame())):,} records", "📈"),
            ("Products Database", f"{len(self.dataframes.get('src_produit', pd.DataFrame())):,} products", "🏷️"),
            ("Users Database", f"{len(self.dataframes.get('src_utilisateur', pd.DataFrame())):,} users", "👥"),
            ("Operations Types", f"{len(self.dataframes.get('src_type_operation', pd.DataFrame())):,} types", "⚙️"),
            ("Chapters Database", f"{len(self.dataframes.get('src_chapitre', pd.DataFrame())):,} chapters", "📚"),
        ]
        
        for label, value, emoji in sources_info:
            # Label
            lbl = QLabel(f"{emoji} {label}")
            lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
            lbl.setStyleSheet("color: #e5e7eb; padding: 8px;")
            grid.addWidget(lbl, row, 0)
            
            # Value
            val = QLabel(value)
            val.setFont(QFont("Segoe UI", 11))
            val.setStyleSheet("color: #60a5fa; padding: 8px; font-weight: bold;")
            grid.addWidget(val, row, 1)
            row += 1
        
        # File information
        grid.addWidget(QLabel(""), row, 0)  # Spacer
        row += 1
        
        files_title = QLabel("📋 Data Files Location")
        files_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        files_title.setStyleSheet("color: #60a5fa; padding: 10px;")
        grid.addWidget(files_title, row, 0, 1, 2)
        row += 1
        
        # List files
        if self.data_folder.exists():
            data_files = [
                "Src_objectif_epargne_cmc.txt",
                "Src_Activité_applicative_realtime.txt",
                "Src_produit.txt",
                "Src_utilisateur.txt",
                "Src_type_operation.txt",
                "Src_chapitre.txt",
            ]
            
            for file in data_files:
                file_path = self.data_folder / file
                if file_path.exists():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    file_label = QLabel(f"✓ {file}")
                    file_label.setStyleSheet("color: #10b981; padding: 5px;")
                    grid.addWidget(file_label, row, 0)
                    
                    size_label = QLabel(f"{size_mb:.2f} MB")
                    size_label.setStyleSheet("color: #9ca3af; padding: 5px;")
                    grid.addWidget(size_label, row, 1)
                    row += 1
        
        # Data load timestamp
        grid.addWidget(QLabel(""), row, 0)  # Spacer
        row += 1
        
        timestamp = QLabel(f"📅 Data loaded at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        timestamp.setStyleSheet("color: #6b7280; padding: 10px; font-size: 10px;")
        grid.addWidget(timestamp, row, 0, 1, 2)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        return widget
    
    def create_charts_tab(self):
        """Create charts and visualization tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #0e1117;")
        
        # Create figure with subplots
        fig = Figure(figsize=(14, 10), dpi=100, facecolor='#0e1117', edgecolor='#374151')
        fig.patch.set_alpha(0.95)
        
        # Adjust spacing
        fig.subplots_adjust(hspace=0.35, wspace=0.3, left=0.08, right=0.95, top=0.95, bottom=0.08)
        
        # Chart 1: Records by source (pie chart)
        ax1 = fig.add_subplot(2, 2, 1)
        data_counts = {}
        for key, df in self.dataframes.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                data_counts[key.capitalize()] = len(df)
        
        if data_counts:
            colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#f97316']
            try:
                wedges, texts, autotexts = ax1.pie(
                    list(data_counts.values()), 
                    labels=list(data_counts.keys()), 
                    autopct='%1.1f%%',
                    colors=colors[:len(data_counts)],
                    startangle=90
                )
                for text in texts:
                    text.set_color('white')
                    text.set_fontsize(9)
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(8)
            except:
                ax1.text(0.5, 0.5, 'Unable to load data', ha='center', va='center', color='white')
        
        ax1.set_title('Data Distribution by Source', color='white', fontsize=12, fontweight='bold', pad=20)
        
        # Chart 2: Record counts (bar chart)
        ax2 = fig.add_subplot(2, 2, 2)
        if data_counts:
            sources = list(data_counts.keys())
            counts = list(data_counts.values())
            colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#f97316']
            bars = ax2.bar(sources, counts, color=colors[:len(sources)], edgecolor='white', linewidth=1.5)
            ax2.set_ylabel('Number of Records', color='white', fontsize=10)
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height):,}',
                        ha='center', va='bottom', color='white', fontweight='bold', fontsize=8)
            ax2.grid(axis='y', alpha=0.2, color='white')
            ax2.set_facecolor('#1f2937')
            ax2.tick_params(colors='white')
        
        ax2.set_title('Records by Data Source', color='white', fontsize=12, fontweight='bold', pad=20)
        
        # Chart 3: Data quality overview
        ax3 = fig.add_subplot(2, 2, 3)
        if 'src_objectif_epargne_cmc' in self.dataframes and not self.dataframes['src_objectif_epargne_cmc'].empty:
            savings_df = self.dataframes['src_objectif_epargne_cmc']
            quality_metrics = {
                'Unique Users': savings_df['ch_code_client_hashed'].nunique() if 'ch_code_client_hashed' in savings_df.columns else 0,
                'Product Types': savings_df['ch_code_produit'].nunique() if 'ch_code_produit' in savings_df.columns else 0,
                'Data Points': len(savings_df),
            }
            
            if any(quality_metrics.values()):
                bars = ax3.barh(list(quality_metrics.keys()), list(quality_metrics.values()), 
                               color=['#3b82f6', '#10b981', '#f59e0b'], edgecolor='white', linewidth=1.5)
                ax3.set_xlabel('Count', color='white', fontsize=10)
                for bar in bars:
                    width = bar.get_width()
                    ax3.text(width, bar.get_y() + bar.get_height()/2.,
                            f'{int(width):,}',
                            ha='left', va='center', color='white', fontweight='bold', fontsize=8)
                ax3.set_facecolor('#1f2937')
                ax3.grid(axis='x', alpha=0.2, color='white')
                ax3.tick_params(colors='white')
        
        ax3.set_title('Data Complexity Metrics', color='white', fontsize=12, fontweight='bold', pad=20)
        
        # Chart 4: Dataset completeness
        ax4 = fig.add_subplot(2, 2, 4)
        completeness = []
        dataset_names = []
        
        for name, df in self.dataframes.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                # Calculate completeness (1 - null ratio)
                if len(df) > 0 and len(df.columns) > 0:
                    null_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
                    complete_ratio = (1 - null_ratio) * 100
                    completeness.append(complete_ratio)
                    dataset_names.append(name.capitalize()[:15])
        
        if completeness:
            bars = ax4.bar(dataset_names, completeness, 
                           color=['#10b981' if c > 90 else '#f59e0b' for c in completeness], 
                           edgecolor='white', linewidth=1.5)
            ax4.set_ylabel('Completeness %', color='white', fontsize=10)
            ax4.set_ylim([0, 105])
            ax4.tick_params(colors='white')
            for bar in bars:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}%',
                        ha='center', va='bottom', color='white', fontweight='bold', fontsize=8)
            ax4.grid(axis='y', alpha=0.2, color='white')
            ax4.set_facecolor('#1f2937')
        
        ax4.set_title('Data Quality - Completeness', color='white', fontsize=12, fontweight='bold', pad=20)
        
        # Set text colors for all axes
        for ax in [ax1, ax2, ax3, ax4]:
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('white')
        
        # Embed in PyQt5
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: #0e1117;")
        layout.addWidget(canvas)
        
        return widget
    
    def create_methodology_tab(self):
        """Create methodology explanation tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #0e1117;")
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #0e1117;
                border: none;
            }
        """)
        
        container = QWidget()
        container.setStyleSheet("background-color: #0e1117;")
        scroll_layout = QVBoxLayout()
        container.setLayout(scroll_layout)
        
        # Methodology sections
        sections = [
            {
                "title": "📊 Data Collection Process",
                "content": """
1. SAVINGS DATA (Src_objectif_epargne_cmc.txt)
   • Source: Bank's savings account management system
   • Records: 1,161,586 user-product combinations
   • Monthly savings data (M_1 to M_12)
   • Customer demographics and segmentation

2. ACTIVITY DATA (Src_Activité_applicative_realtime.txt)
   • Source: Real-time banking platform activity logs
   • Records: 12+ million transactions
   • Session tracking and user behavior metrics
   • Digital engagement analysis

3. PRODUCT DATABASE (Src_produit.txt)
   • Source: Product catalog and classification
   • 451 unique banking products
   • Product hierarchy and categorization
   • EPARGNE (Savings) products: 14 main types

4. USER DATABASE (Src_utilisateur.txt)
   • Source: Customer master data
   • Unique user profiles and identifiers
   • Customer segmentation and classification

5. OPERATIONS & CHAPTERS
   • Type of operations: 1,014 different categories
   • Accounting chapters for transaction classification
   • Used for detailed transaction analysis
                """
            },
            {
                "title": "🔄 Data Processing Pipeline",
                "content": """
STEP 1: DATA INGESTION
   ✓ Read all CSV/TXT files from data folder
   ✓ Handle encoding (UTF-8) and delimiter detection
   ✓ Parse numerical formats (comma decimals)

STEP 2: DATA CLEANING
   ✓ Remove duplicate records
   ✓ Handle missing values appropriately
   ✓ Standardize data types
   ✓ Hash sensitive customer information

STEP 3: DATA ENRICHMENT
   ✓ Join tables by client ID and product codes
   ✓ Aggregate monthly data into annual metrics
   ✓ Calculate derived metrics (totals, averages, trends)
   ✓ Create customer segments

STEP 4: DATA VALIDATION
   ✓ Check data quality indicators
   ✓ Identify outliers and anomalies
   ✓ Verify referential integrity
   ✓ Calculate completeness metrics

STEP 5: ANALYSIS & VISUALIZATION
   ✓ Generate dashboard summaries
   ✓ Create exploratory data views
   ✓ Enable interactive filtering and sorting
   ✓ Export results for reporting
                """
            },
            {
                "title": "📈 Key Metrics & Analysis",
                "content": """
USER SEGMENTATION:
   • Full Year Savers: Customers with savings activity all 12 months
   • Partial Year Savers: Customers with seasonal savings patterns
   • No Savings: Inactive savings accounts

PRODUCT ANALYSIS:
   • EPARGNE Products: Specialized savings products (14 types)
   • Regular Products: Standard banking products (437 types)
   • Product mix per customer
   • Product adoption rates

BEHAVIORAL METRICS:
   • Monthly savings amounts (M_1 to M_12)
   • Platform activity sessions
   • Transaction frequency and volume
   • Average savings per product

CUSTOMER INSIGHTS:
   • Customer lifetime value indicators
   • Engagement metrics
   • Risk and compliance indicators
   • Potential for cross-selling
                """
            },
            {
                "title": "🎯 Data Accuracy & Quality",
                "content": """
DATA VALIDATION CHECKS:
   ✓ Removed duplicate user-product combinations
   ✓ Validated date formats and ranges
   ✓ Cross-checked customer IDs across datasets
   ✓ Verified product code consistency
   ✓ Checked for referential integrity

DATA QUALITY METRICS:
   ✓ Completeness: % of non-null records
   ✓ Accuracy: Validation against source systems
   ✓ Consistency: Data type and format compliance
   ✓ Timeliness: Data currency and freshness

EXCLUSIONS & FILTERS:
   ✓ Test/dummy accounts removed
   ✓ Invalid customer records filtered
   ✓ Incomplete product records excluded
   ✓ Confidential information hashed

EXPORT CAPABILITIES:
   ✓ Multi-format export (Excel, CSV)
   ✓ Customizable column selection
   ✓ Filtered dataset exports
   ✓ Summary statistics
                """
            }
        ]
        
        for section in sections:
            # Section title
            title = QLabel(section["title"])
            title.setFont(QFont("Segoe UI", 12, QFont.Bold))
            title.setStyleSheet("color: #60a5fa; padding: 10px 0px 5px 0px; margin-top: 10px;")
            scroll_layout.addWidget(title)
            
            # Section content
            content = QTextEdit()
            content.setText(section["content"])
            content.setReadOnly(True)
            content.setStyleSheet("""
                QTextEdit {
                    background-color: #1f2937;
                    color: #e5e7eb;
                    border: 1px solid #374151;
                    border-radius: 4px;
                    padding: 10px;
                    font-family: 'Courier New';
                    font-size: 10px;
                    line-height: 1.5;
                }
                QScrollBar:vertical {
                    width: 10px;
                    background: #1f2937;
                }
                QScrollBar::handle:vertical {
                    background: #374151;
                    border-radius: 5px;
                }
            """)
            content.setMinimumHeight(150)
            scroll_layout.addWidget(content)
        
        scroll_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Footer note
        footer = QLabel(
            "💡 Note: All customer data is anonymized using SHA-256 hashing. "
            "This visualization is prepared for client presentation showing data collection and processing methodology."
        )
        footer.setWordWrap(True)
        footer.setStyleSheet("color: #9ca3af; padding: 10px; font-size: 9px; background-color: #1f2937; border-radius: 4px; margin: 10px;")
        layout.addWidget(footer)
        
        return widget
