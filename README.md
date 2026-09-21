# Game Designer IDE

A lightweight game-design IDE built around a custom command language and a persistent SQLite database. It allows game entities such as characters to be created, edited, searched, inspected, deleted, and restored through simple commands.

## Commands

### Create a Character

```text
new Aria
```

Creates a new character using the default character template.

### Set Attributes

Set multiple attributes for an entity:

```text
set Aria
hp 120
atk 35
vit 20
ultimate "Celestial Break"
talent "Lightborn"
```

Attributes can also be set directly:

```text
set Aria.hp 120
set Aria.atk 35
set Aria.vit 20
```

### Show an Entity

```text
show Aria
```

Displays the entity and its stored attributes.

### Find Entities

```text
find Aria
```

Searches for entities by name.

### Delete an Entity

```text
delete Aria
```

Deletes an entity.

### Undo / Redo

```text
undo
redo
```

Undo or redo the most recent operation.

### Database Statistics

```text
stats
```

Displays the number of entities stored in each category.

## Running the Project

### Prerequisites

- Python 3.x
- Node.js
- npm

### Install Python Dependencies

```bash
cd game_designer
pip install -r requirements.txt
```

### Install Frontend Dependencies

From the project root:

```bash
npm install
```

### Start the Frontend

```bash
npm run dev
```

### Windows

The project also includes a launcher:

```text
game_designer/run.bat
```

The SQLite database is stored at:

```text
game_designer/gamedesigner.db
```

Changes made through the IDE are persisted in the database and remain available after restarting the project.
