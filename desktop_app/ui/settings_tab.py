"""
Settings Tab
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QFormLayout, QLineEdit, QFrame
from PyQt5.QtGui import QFont

class SettingsTab(QWidget):
    """Settings tab"""
    
    def __init__(self):
        super().__init__()
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
        
        title = QLabel("⚙️ Settings")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Configure your application")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #9ca3af;")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_frame)
        
        # AI Configuration
        group = QGroupBox("AI Configuration")
        group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #374151;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 15px;
                background-color: #1f2937;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        form = QFormLayout()
        
        model_inp = QLineEdit("llama3.2:1b")
        model_inp.setStyleSheet("""
            QLineEdit {
                background: #374151;
                color: white;
                padding: 8px;
                border: 1px solid #4b5563;
                border-radius: 4px;
            }
        """)
        form.addRow("Ollama Model:", model_inp)
        
        info = QLabel(
            "Recommended models:\n"
            "• llama3.2:1b (Fast, 1.3GB)\n"
            "• llama3.2:3b (Balanced, 2GB)\n\n"
            "Make sure Ollama is running:\n"
            "Run 'ollama serve' in terminal"
        )
        info.setStyleSheet("color: #9ca3af; margin-top: 10px;")
        form.addRow("", info)
        
        group.setLayout(form)
        layout.addWidget(group)
        
        # Data Settings
        group2 = QGroupBox("Data Settings")
        group2.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #374151;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 15px;
                background-color: #1f2937;
            }
        """)
        form2 = QFormLayout()
        
        info2 = QLabel(
            "Data Folder: ./data\n"
            "Loaded Files: 7 datasets\n"
            "Total Records: Use Dashboard for stats\n\n"
            "To reload data:\n"
            "Click 'Reload Data' button in header"
        )
        info2.setStyleSheet("color: #9ca3af;")
        form2.addRow("", info2)
        
        group2.setLayout(form2)
        layout.addWidget(group2)
        
        layout.addStretch()
