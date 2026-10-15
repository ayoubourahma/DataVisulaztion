"""
Dashboard Tab - IMPROVED UI
Fixed text cropping and better layout
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('dark_background')


class MetricCard(QFrame):
    """Professional KPI Card"""
    def __init__(self, title, value, subtext=""):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 12px;
            }
        """)
        self.setFixedWidth(280)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # Title
        t_label = QLabel(title.upper())
        t_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        t_label.setStyleSheet("color: #9ca3af;")
        layout.addWidget(t_label)
        
        # Value
        v_label = QLabel(value)
        v_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        v_label.setStyleSheet("color: #10b981;")
        layout.addWidget(v_label)
        
        # Subtext
        if subtext:
            s_label = QLabel(subtext)
            s_label.setFont(QFont("Segoe UI", 9))
            s_label.setStyleSheet("color: #6b7280;")
            layout.addWidget(s_label)


class DashboardTab(QWidget):
    """Dashboard tab with improved text handling"""
    
    def __init__(self, dataframes, analysis=None):
        super().__init__()
        self.dataframes = dataframes
        self.analysis = analysis or {}
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #0e1117;
            }
            QScrollBar:vertical {
                width: 10px;
                background: #0e1117;
            }
            QScrollBar::handle:vertical {
                background: #374151;
                border-radius: 5px;
            }
        """)
        
        content = QWidget()
        content.setStyleSheet("background-color: #0e1117;")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(25)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content.setLayout(content_layout)
        
        # Header
        header = QLabel("📊 Executive Dashboard")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: white; margin-bottom: 10px;")
        content_layout.addWidget(header)
        
        # KPIs
        self.create_kpi_row(content_layout)
        
        # Charts
        self.create_charts(content_layout)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def create_kpi_row(self, parent_layout):
        """Create KPI cards"""
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        container.setLayout(layout)
        
        try:
            # Get stats
            stats = self.analysis.get('statistics', {})
            
            # Total clients
            total_clients = stats.get('customers', {}).get('total', 0)
            layout.addWidget(MetricCard(
                "Total Clients",
                f"{total_clients:,}",
                "Active Accounts"
            ))
            
            # Savings
            if 'src_objectif_epargne_cmc' in self.dataframes:
                df = self.dataframes['src_objectif_epargne_cmc']
                month_cols = [f'M_{i}' for i in range(1, 13)]
                all_vals = []
                for col in month_cols:
                    if col in df.columns:
                        vals = pd.to_numeric(df[col], errors='coerce').dropna()
                        all_vals.extend(vals)
                
                if all_vals:
                    total_savings = sum(all_vals) / 1_000_000
                    avg_savings = np.mean(all_vals)
                    layout.addWidget(MetricCard(
                        "Total Savings",
                        f"{total_savings:.1f}M TND",
                        "Cumulative"
                    ))
                    layout.addWidget(MetricCard(
                        "Avg Savings",
                        f"{avg_savings:,.0f} TND",
                        "Per Account"
                    ))
            
            # Activity
            activity_count = stats.get('activity', {}).get('unique_users', 0)
            layout.addWidget(MetricCard(
                "Active Users",
                f"{activity_count:,}",
                "With Activity Logs"
            ))
            
        except Exception as e:
            err = QLabel(f"Error loading KPIs: {str(e)}")
            err.setStyleSheet("color: #ef4444;")
            layout.addWidget(err)
        
        layout.addStretch()
        parent_layout.addWidget(container)
    
    def create_charts(self, parent_layout):
        """Create charts with improved text sizing"""
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        container.setLayout(layout)
        
        # Chart 1: Segments (Donut) - FIXED CROPPING
        try:
            if 'src_utilisateur' in self.dataframes:
                df = self.dataframes['src_utilisateur']
                if 'segment' in df.columns:
                    segments = df['segment'].value_counts().head(5)
                    
                    # LARGER figure to prevent cropping
                    fig = Figure(figsize=(7, 5), facecolor='#0e1117')
                    ax = fig.add_subplot(111, facecolor='#0e1117')
                    
                    colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
                    
                    # Shorter labels to prevent cropping
                    short_labels = []
                    for label in segments.index:
                        if len(label) > 20:
                            short_labels.append(label[:17] + '...')
                        else:
                            short_labels.append(label)
                    
                    wedges, texts, autotexts = ax.pie(
                        segments.values,
                        labels=None,  # No labels on pie
                        autopct='%1.1f%%',
                        pctdistance=0.85,
                        colors=colors,
                        wedgeprops=dict(width=0.5, edgecolor='#0e1117')
                    )
                    
                    # Larger percentage text
                    for t in autotexts:
                        t.set_color('white')
                        t.set_fontsize(10)  # Increased from 9
                        t.set_weight('bold')
                    
                    # Legend with shorter labels and better positioning
                    ax.legend(
                        wedges, 
                        short_labels,
                        loc="center left",
                        bbox_to_anchor=(1.05, 0.5),  # Better positioning
                        frameon=False,
                        labelcolor='white',
                        fontsize=10  # Readable size
                    )
                    
                    ax.set_title("Customer Segments", color='white', fontsize=13, pad=20, weight='bold')
                    
                    # Adjust layout to prevent cropping
                    fig.tight_layout(rect=[0, 0, 0.85, 1])
                    
                    canvas = FigureCanvas(fig)
                    canvas.setStyleSheet("background-color: #0e1117; border-radius: 12px;")
                    layout.addWidget(canvas)
        except Exception as e:
            print(f"Chart error: {e}")
        
        # Chart 2: Nationalities (Horizontal Bar) - FIXED CROPPING
        try:
            if 'src_utilisateur' in self.dataframes:
                df = self.dataframes['src_utilisateur']
                if 'nationalite_client' in df.columns:
                    nat = df['nationalite_client'].value_counts().head(7)
                    nat = nat.iloc[::-1]  # Reverse
                    
                    # LARGER figure
                    fig = Figure(figsize=(7, 5), facecolor='#0e1117')
                    ax = fig.add_subplot(111, facecolor='#0e1117')
                    
                    # Shorten nationality labels if needed
                    short_nat = []
                    for label in nat.index:
                        if len(label) > 15:
                            short_nat.append(label[:12] + '...')
                        else:
                            short_nat.append(label)
                    
                    bars = ax.barh(short_nat, nat.values, color='#6366f1', height=0.6)
                    
                    ax.set_title("Top Nationalities", color='white', fontsize=13, pad=20, weight='bold')
                    ax.tick_params(axis='x', colors='#9ca3af', labelsize=10)
                    ax.tick_params(axis='y', colors='white', labelsize=11)  # Larger labels
                    
                    for spine in ax.spines.values():
                        spine.set_visible(False)
                    
                    ax.grid(axis='x', color='#374151', linestyle='--', alpha=0.3)
                    
                    # Adjust layout to prevent Y-axis cropping
                    fig.tight_layout(rect=[0.15, 0, 1, 1])
                    
                    canvas = FigureCanvas(fig)
                    canvas.setStyleSheet("background-color: #0e1117; border-radius: 12px;")
                    layout.addWidget(canvas)
        except Exception as e:
            print(f"Chart error: {e}")
        
        parent_layout.addWidget(container)
