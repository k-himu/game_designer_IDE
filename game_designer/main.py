import sys
from PySide6.QtWidgets import QApplication
from database import Database
from engine import GameEngine
from commands import CommandParser
from gui import MainWindow

def main():
    # 1. Initialize strictly local SQLite Database
    db = Database("gamedesigner.db")
    
    # 2. Initialize Game Engine wrapper
    engine = GameEngine(db)
    
    # 3. Initialize Command Parser and Action History
    parser = CommandParser(engine)
    
    # 4. Boot Native UI
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow(parser)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
