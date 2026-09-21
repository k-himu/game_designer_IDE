import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLineEdit, QTextEdit, QTreeWidget, QTreeWidgetItem, 
                               QSplitter, QLabel, QCompleter)
from PySide6.QtCore import Qt, QStringListModel
from commands import CommandParser
from engine import GameEngine

class MainWindow(QMainWindow):
    def __init__(self, parser: CommandParser):
        super().__init__()
        self.parser = parser
        self.engine = parser.engine
        self.setWindowTitle("Game Designer IDE")
        self.resize(1024, 768)
        self.setup_ui()

    def setup_ui(self):
        splitter = QSplitter(Qt.Horizontal)
        
        # Left Navigation Panel
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderLabel("Database Explorer")
        self.nav_tree.itemClicked.connect(self.on_tree_click)
        splitter.addWidget(self.nav_tree)
        
        # Right Workspace
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Console Output / Data Inspector
        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)
        self.output_view.setStyleSheet("font-family: Consolas, monospace; font-size: 14px; background: #1e1e1e; color: #d4d4d4;")
        right_layout.addWidget(self.output_view)
        
        # Command Input
        input_layout = QHBoxLayout()
        prompt_label = QLabel(">")
        prompt_label.setStyleSheet("font-weight: bold; font-family: monospace; font-size: 16px;")
        
        self.console_input = QLineEdit()
        self.console_input.setPlaceholderText("Enter command (e.g. 'new Jason Character', 'set Jason.hp 150', 'undo')...")
        self.console_input.setStyleSheet("font-family: Consolas, monospace; font-size: 14px; padding: 6px;")
        self.console_input.returnPressed.connect(self.on_command)
        
        # Setup Global Autocomplete
        self.completer_model = QStringListModel()
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.console_input.setCompleter(self.completer)
        
        input_layout.addWidget(prompt_label)
        input_layout.addWidget(self.console_input)
        right_layout.addLayout(input_layout)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([250, 774])
        self.setCentralWidget(splitter)
        
        self.update_ui_state()
        self.output_view.append("<span style='color: #4fc1ff;'>Welcome to Game Designer IDE.</span>")
        self.output_view.append("Type 'stats' to see current database footprint.\n")

    def on_command(self):
        cmd = self.console_input.text()
        if not cmd.strip():
            return
        
        self.console_input.clear()
        self.output_view.append(f"<span style='color: #4fc1ff;'>> {cmd}</span>")
        
        try:
            result = self.parser.execute(cmd)
            if result:
                self.output_view.append(result.replace("\\n", "<br>"))
        except Exception as e:
            self.output_view.append(f"<span style='color: #f44747;'>Error: {str(e)}</span>")
            
        self.output_view.append("") # Spacer
        self.update_ui_state()
        
    def on_tree_click(self, item, column):
        """Simulate a 'show' command when clicking an entity in the tree."""
        if item.parent(): # Ensures it's an entity leaf node, not a category root
            name = item.text(0)
            self.console_input.setText(f"show {name}")
            self.on_command()
            
    def update_ui_state(self):
        """Refresh the navigation tree and autocomplete suggestions strictly from DB truth."""
        self.nav_tree.clear()
        entities = self.engine.list_all()
        
        categories = {}
        names = []
        for cat, name in entities:
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(name)
            names.append(name)
            
        for cat, items in categories.items():
            cat_item = QTreeWidgetItem(self.nav_tree, [cat])
            cat_item.setExpanded(True)
            for item_name in items:
                QTreeWidgetItem(cat_item, [item_name])
                
        # Re-index autocomplete dictionary
        words = ["new", "set", "show", "delete", "find", "undo", "redo", "stats"] + names
        self.completer_model.setStringList(list(set(words)))
