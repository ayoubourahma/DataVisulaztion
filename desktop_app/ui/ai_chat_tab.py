"""
AI Chat Tab - IMPROVED UI
Larger text, better suggestions with real user IDs
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QFrame, QComboBox, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import random

from desktop_app.core.ai_chat import BankDataAI, check_ollama_status


class ChatThread(QThread):
    """Thread for AI chat"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ai_chat, message):
        super().__init__()
        self.ai_chat = ai_chat
        self.message = message
    
    def run(self):
        try:
            response = self.ai_chat.chat(self.message)
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))


class AIChatTab(QWidget):
    """AI chat interface with improved UI"""
    
    def __init__(self, dataframes, analysis=None):
        super().__init__()
        self.dataframes = dataframes
        self.analysis = analysis
        self.ai_chat = None
        self.sample_user_ids = []
        self.init_ui()
        self.check_ollama()
        self.load_sample_users()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Chat history - LARGER TEXT
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: #1f2937;
                color: white;
                border: 1px solid #374151;
                border-radius: 4px;
                padding: 15px;
                font-size: 15px;  /* INCREASED from 12px */
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.chat_history)
        
        # Input area
        input_area = self.create_input_area()
        layout.addWidget(input_area)
        
        # User ID Picker
        user_picker = self.create_user_picker()
        layout.addWidget(user_picker)
        
        # Suggestions
        suggestions = self.create_suggestions()
        layout.addWidget(suggestions)
    
    def create_header(self):
        """Create header"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout()
        frame.setLayout(layout)
        
        title = QLabel("💬 AI Banking Advisor")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        self.status_label = QLabel()
        self.status_label.setFont(QFont("Segoe UI", 11))  # Larger status text
        layout.addWidget(self.status_label)
        
        return frame
    
    def create_input_area(self):
        """Create input area"""
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)
        
        # Input field - LARGER
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask about clients, savings, sectors...")
        self.input_field.setMinimumHeight(50)  # Taller input
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #374151;
                color: white;
                border: 1px solid #4b5563;
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;  /* LARGER TEXT */
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)
        
        # Send button
        self.send_btn = QPushButton("💬 Send")
        self.send_btn.setMinimumWidth(120)
        self.send_btn.setMinimumHeight(50)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:disabled {
                background-color: #6b7280;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        layout.addWidget(self.send_btn)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setMinimumHeight(50)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        clear_btn.clicked.connect(self.clear_chat)
        layout.addWidget(clear_btn)
        
        return widget
    
    def create_user_picker(self):
        """Create user ID picker with dropdown"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 15px;
                margin-top: 8px;
            }
        """)
        layout = QHBoxLayout()
        frame.setLayout(layout)
        
        label = QLabel("🔍 Quick Client Lookup:")
        label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        label.setStyleSheet("color: #10b981;")
        layout.addWidget(label)
        
        # Dropdown with user IDs
        self.user_combo = QComboBox()
        self.user_combo.setMinimumWidth(500)
        self.user_combo.setMinimumHeight(40)
        self.user_combo.setStyleSheet("""
            QComboBox {
                background-color: #374151;
                color: white;
                border: 1px solid #4b5563;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                font-family: 'Courier New', monospace;
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
        layout.addWidget(self.user_combo)
        
        # "Ask AI" button
        ask_btn = QPushButton("🤖 Ask AI About This Client")
        ask_btn.setMinimumHeight(40)
        ask_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        ask_btn.clicked.connect(self.ask_about_selected_user)
        layout.addWidget(ask_btn)
        
        layout.addStretch()
        
        return frame
    
    def create_suggestions(self):
        """Create suggestion buttons"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 12px;
                margin-top: 8px;
            }
        """)
        layout = QVBoxLayout()
        frame.setLayout(layout)
        
        label = QLabel("💡 Quick Actions:")
        label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        label.setStyleSheet("color: #9ca3af;")
        layout.addWidget(label)
        
        # Suggestion buttons - SAVINGS FOCUSED
        suggestions_layout = QHBoxLayout()
        
        suggestions = [
            ("📊 Analyze by Sector", "Analyze average account balances by sector"),
            ("💰 Savings Statistics", "Show me savings statistics"),
            ("👥 Top Segments", "Show me the top customer segments"),
            ("🔍 Random Client", "Pick a random user and analyze them"),
        ]
        
        for label_text, query in suggestions:
            btn = QPushButton(label_text)
            btn.setMinimumHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #374151;
                    color: white;
                    border: 1px solid #4b5563;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #10b981;
                    border-color: #10b981;
                }
            """)
            btn.clicked.connect(lambda checked, q=query: self.input_field.setText(q))
            suggestions_layout.addWidget(btn)
        
        suggestions_layout.addStretch()
        layout.addLayout(suggestions_layout)
        
        return frame
    
    def load_sample_users(self):
        """Load sample user IDs for the dropdown"""
        try:
            if 'src_utilisateur' in self.dataframes:
                df = self.dataframes['src_utilisateur']
                if 'ch_code_client' in df.columns:
                    # Get 20 random user IDs
                    all_ids = df['ch_code_client'].dropna().unique()
                    sample_size = min(20, len(all_ids))
                    self.sample_user_ids = random.sample(list(all_ids), sample_size)
                    
                    # Add to combo box with index
                    self.user_combo.clear()
                    self.user_combo.addItem("-- Select a Client ID --")
                    for i, user_id in enumerate(self.sample_user_ids, 1):
                        # Show first 48 chars of ID
                        display_id = user_id[:48] + "..." if len(user_id) > 48 else user_id
                        self.user_combo.addItem(f"Client {i}: {display_id}", user_id)
        except Exception as e:
            print(f"Error loading user IDs: {e}")
    
    def ask_about_selected_user(self):
        """Ask AI about the selected user from dropdown"""
        if self.user_combo.currentIndex() == 0:
            self.add_message("System", "Please select a client from the dropdown first.")
            return
        
        # Get the full user ID from the data
        user_id = self.user_combo.currentData()
        if user_id:
            query = f"Look up client {user_id}"
            self.input_field.setText(query)
            self.send_message()
    
    def check_ollama(self):
        """Check Ollama status"""
        status = check_ollama_status()
        
        if status.get('available'):
            self.status_label.setText("✅ AI Online & Ready")
            self.status_label.setStyleSheet("color: #10b981;")
            
            try:
                self.ai_chat = BankDataAI(
                    self.dataframes,
                    model="llama3.2:1b",
                    analysis=self.analysis
                )
                self.send_btn.setEnabled(True)
                
                welcome = "👋 **Welcome to AI Banking Advisor!**\n\n"
                if self.analysis and 'summary' in self.analysis:
                    total_rows = self.analysis['summary']['total_rows']
                    welcome += f"📊 Database: {total_rows:,} records loaded\n\n"
                
                welcome += (
                    "**I can help you:**\n"
                    "• 🔍 Analyze specific clients\n"
                    "• 💰 Review savings patterns\n"
                    "• 📊 Compare sectors and segments\n"
                    "• 🎯 Identify opportunities\n\n"
                    "**Try the dropdown above** to pick a client!"
                )
                
                self.add_message("System", welcome)
                
            except Exception as e:
                self.status_label.setText(f"❌ AI Error: {str(e)}")
                self.status_label.setStyleSheet("color: #ef4444;")
                self.send_btn.setEnabled(False)
        else:
            self.status_label.setText("❌ Ollama Not Running")
            self.status_label.setStyleSheet("color: #ef4444;")
            self.send_btn.setEnabled(False)
            self.add_message(
                "System",
                "⚠️ Ollama is not running.\n\n"
                "To enable AI:\n"
                "1. Open terminal\n"
                "2. Run: ollama serve\n"
                "3. Restart this app"
            )
    
    def send_message(self):
        """Send message to AI"""
        message = self.input_field.text().strip()
        if not message:
            return
        
        if not self.ai_chat:
            self.add_message("System", "⚠️ AI is offline. Check Ollama status.")
            return
        
        # Add user message
        self.add_message("You", message)
        self.input_field.clear()
        
        # Disable while processing
        self.send_btn.setEnabled(False)
        self.send_btn.setText("⏳ Thinking...")
        
        # Start thread
        self.chat_thread = ChatThread(self.ai_chat, message)
        self.chat_thread.response_ready.connect(self.on_response)
        self.chat_thread.error_occurred.connect(self.on_error)
        self.chat_thread.start()
    
    def on_response(self, response):
        """Handle AI response"""
        self.add_message("AI Advisor", response)
        self.send_btn.setEnabled(True)
        self.send_btn.setText("💬 Send")
    
    def on_error(self, error):
        """Handle error"""
        self.add_message("Error", f"❌ Failed: {error}")
        self.send_btn.setEnabled(True)
        self.send_btn.setText("💬 Send")
    
    def add_message(self, sender, message):
        """Add message with LARGER TEXT"""
        colors = {
            "You": "#3b82f6",
            "AI Advisor": "#10b981",
            "System": "#f59e0b",
            "Error": "#ef4444"
        }
        color = colors.get(sender, "#9ca3af")
        
        # Format with markdown-style bold
        formatted_message = message.replace('**', '</b><b>').replace('\n', '<br>')
        
        html = f"""
        <div style='margin-bottom: 20px; border-left: 3px solid {color}; padding-left: 15px;'>
            <div style='color: {color}; font-weight: bold; margin-bottom: 10px; font-size: 15px;'>{sender}</div>
            <div style='color: white; line-height: 1.7; font-size: 14px;'>{formatted_message}</div>
        </div>
        """
        
        self.chat_history.append(html)
        
        # Scroll to bottom
        scrollbar = self.chat_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_chat(self):
        """Clear chat"""
        self.chat_history.clear()
        if self.ai_chat:
            self.ai_chat.clear_history()
            self.add_message("System", "✨ Chat cleared! Ready for new questions.")
