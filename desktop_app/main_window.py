"""
Main Window - WITH TAB COMMUNICATION
Connects Data Explorer to AI Chat tab
"""
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QTabWidget, QPushButton, QLabel, QFileDialog, 
    QStatusBar, QHBoxLayout, QMessageBox, QProgressDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

# Import our modules
from desktop_app.core.data_loader import BankDataLoader
from desktop_app.core.data_analyzer import analyze_data_background
from desktop_app.ui.dashboard_tab import DashboardTab
from desktop_app.ui.ai_chat_tab import AIChatTab
from desktop_app.ui.data_explorer_tab import DataExplorerTab
from desktop_app.ui.data_sources_tab import DataSourcesTab
from desktop_app.ui.settings_tab import SettingsTab


class DataLoaderThread(QThread):
    """Thread for loading data without freezing UI"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict, dict)  # dataframes, analysis
    error = pyqtSignal(str)
    
    def __init__(self, data_folder):
        super().__init__()
        self.folder = data_folder
        
    def run(self):
        try:
            self.progress.emit("📄 Loading data files...")
            
            # Load data
            loader = BankDataLoader(self.folder, remove_duplicates=True)
            dataframes = loader.load_all_data()
            
            if not dataframes:
                self.error.emit("No data loaded. Check your data folder.")
                return
            
            self.progress.emit("🔍 Analyzing data...")
            
            # Run analysis
            analysis = analyze_data_background(dataframes, self.folder)
            
            self.progress.emit("✅ Complete!")
            self.finished.emit(dataframes, analysis)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.error.emit(f"{str(e)}\n\n{error_details}")


class MainWindow(QMainWindow):
    """Main application window with tab communication"""
    
    def __init__(self):
        super().__init__()
        self.dataframes = {}
        self.analysis = {}
        self.data_folder = Path("data")
        
        # Store tab references
        self.dashboard_tab = None
        self.data_sources_tab = None
        self.ai_chat_tab = None
        self.data_explorer_tab = None
        self.settings_tab = None
        
        self.init_ui()
        
        # Auto-load if data folder exists
        if self.data_folder.exists():
            self.start_loading()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("🏦 Bank Data Visualizer - Professional Edition")
        self.setGeometry(100, 100, 1400, 900)
        
        # Dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0e1117;
            }
            QLabel {
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #374151;
                background-color: #0e1117;
            }
            QTabBar::tab {
                background: #1f2937;
                color: #9ca3af;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background: #3b82f6;
                color: white;
            }
            QTabBar::tab:hover {
                background: #374151;
                color: white;
            }
        """)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setEnabled(False)  # Disabled until data loads
        layout.addWidget(self.tabs)
        
        # Status bar
        self.status = QStatusBar()
        self.status.setStyleSheet("""
            QStatusBar {
                color: white;
                background: #1f2937;
                padding: 5px;
                font-size: 11px;
            }
        """)
        self.setStatusBar(self.status)
        self.status.showMessage("⏳ Waiting for data...")
    
    def create_header(self):
        """Create header with title and buttons"""
        widget = QWidget()
        widget.setStyleSheet("background-color: #1f2937; padding: 15px; border-radius: 8px;")
        layout = QHBoxLayout()
        widget.setLayout(layout)
        
        # Title
        title = QLabel("🏦 Bank Data Visualizer")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        subtitle = QLabel("Professional Banking Analytics & AI Advisor")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #9ca3af;")
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        # Load button
        self.load_btn = QPushButton("🔄 Reload Data")
        self.load_btn.setMinimumHeight(40)
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #6b7280;
            }
        """)
        self.load_btn.clicked.connect(self.start_loading)
        layout.addWidget(self.load_btn)
        
        return widget
    
    def start_loading(self):
        """Start data loading process"""
        # Check if folder exists
        if not self.data_folder.exists():
            folder = QFileDialog.getExistingDirectory(
                self,
                "Select Data Folder",
                str(Path.cwd())
            )
            if not folder:
                return
            self.data_folder = Path(folder)
        
        # Disable controls
        self.load_btn.setEnabled(False)
        self.tabs.setEnabled(False)
        self.status.showMessage("⏳ Loading data...")
        
        # Create progress dialog
        self.progress_dialog = QProgressDialog(
            "Loading bank data...",
            "Cancel",
            0, 0,
            self
        )
        self.progress_dialog.setWindowTitle("Loading Data")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)
        
        # Start thread
        self.loader_thread = DataLoaderThread(str(self.data_folder))
        self.loader_thread.progress.connect(self.on_progress)
        self.loader_thread.finished.connect(self.on_load_finished)
        self.loader_thread.error.connect(self.on_load_error)
        self.loader_thread.start()
    
    def on_progress(self, message):
        """Update progress"""
        self.status.showMessage(message)
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setLabelText(message)
    
    def on_load_finished(self, dataframes, analysis):
        """Handle successful data load"""
        self.dataframes = dataframes
        self.analysis = analysis
        
        # Close progress dialog
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        # Initialize tabs
        self.init_tabs()
        
        # Connect Data Explorer to AI Chat
        self.connect_tabs()
        
        # Enable controls
        self.tabs.setEnabled(True)
        self.load_btn.setEnabled(True)
        self.status.showMessage("✅ Data loaded successfully!")
        
        # Show summary
        total_rows = sum(len(df) for df in dataframes.values())
        QMessageBox.information(
            self,
            "Data Loaded Successfully",
            f"✅ Loaded {len(dataframes)} datasets\n"
            f"📊 Total records: {total_rows:,}\n\n"
            f"Ready to analyze!"
        )
    
    def on_load_error(self, error_msg):
        """Handle loading error"""
        # Close progress dialog
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        # Enable controls
        self.tabs.setEnabled(False)
        self.load_btn.setEnabled(True)
        self.status.showMessage("❌ Error loading data")
        
        # Show error
        QMessageBox.critical(
            self,
            "Loading Error",
            f"Failed to load data:\n\n{error_msg}"
        )
    
    def init_tabs(self):
        """Initialize all tabs with data"""
        self.tabs.clear()
        
        # Dashboard tab
        self.dashboard_tab = DashboardTab(self.dataframes, self.analysis)
        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        
        # Data Sources & Visualization tab
        self.data_sources_tab = DataSourcesTab(self.dataframes, self.analysis)
        self.tabs.addTab(self.data_sources_tab, "📈 Data Sources")
        
        # AI Chat tab
        self.ai_chat_tab = AIChatTab(self.dataframes, self.analysis)
        self.tabs.addTab(self.ai_chat_tab, "💬 AI Advisor")
        
        # Data Explorer tab
        self.data_explorer_tab = DataExplorerTab(self.dataframes)
        self.tabs.addTab(self.data_explorer_tab, "🔍 Data Explorer")
        
        # Settings tab
        self.settings_tab = SettingsTab()
        self.tabs.addTab(self.settings_tab, "⚙️ Settings")
    
    def connect_tabs(self):
        """Connect Data Explorer to AI Chat for communication"""
        if self.data_explorer_tab and self.ai_chat_tab:
            # When user clicks "Ask AI" in Data Explorer, switch to AI tab and query
            self.data_explorer_tab.ask_ai_about_id.connect(self.on_ask_ai_about_id)
    
    def on_ask_ai_about_id(self, client_id):
        """Handle request from Data Explorer to query AI about a client ID"""
        # Switch to AI Chat tab
        self.tabs.setCurrentWidget(self.ai_chat_tab)
        
        # Set the query in the AI chat input
        query = f"Look up client {client_id}"
        self.ai_chat_tab.input_field.setText(query)
        
        # Auto-send the message
        self.ai_chat_tab.send_message()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
