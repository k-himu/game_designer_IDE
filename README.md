# Game Designer IDE

A lightweight game-design IDE built around a custom SQL-like language for defining, querying, and managing game data.

The project combines a Python-based language engine and database layer with a web-based frontend, providing a structured environment for experimenting with game data without relying directly on conventional SQL.

## Overview

Game Designer IDE is designed as a small domain-specific development environment for game creation.

Instead of manually editing JSON files or writing raw SQL queries, users can interact with game data through a custom command language designed specifically around game-design concepts.

The application provides:

- A custom SQL-like language
- A command parser and execution engine
- Persistent SQLite-based storage
- Game data management
- A graphical/web interface
- Python backend components
- TypeScript/React frontend components
- Persistent project state

Changes made through the application are stored in the database and remain available when the application is restarted.

## Architecture

The project consists of two main layers:

### Backend

The backend is implemented in Python and contains the core language and data-management logic.

```text
game_designer/
├── commands.py
├── database.py
├── engine.py
├── gui.py
├── main.py
├── gamedesigner.db
├── requirements.txt
└── run.bat
