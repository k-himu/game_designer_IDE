from database import Database

class GameEngine:
    def __init__(self, db: Database):
        self.db = db

    def create_entity(self, category: str, name: str):
        try:
            self.db.execute("INSERT INTO entities (category, name) VALUES (?, ?)", (category, name))
            return True, f"Created {category}: {name}"
        except Exception as e:
            return False, f"Failed to create '{name}' (may already exist): {e}"

    def get_entity(self, name: str):
        return self.db.query_one("SELECT * FROM entities WHERE name = ?", (name,))

    def delete_entity(self, name: str):
        entity = self.get_entity(name)
        if not entity:
            return False, f"Entity '{name}' not found."
        self.db.execute("DELETE FROM entities WHERE id = ?", (entity['id'],))
        return True, f"Deleted {name}."

    def set_attribute(self, name: str, key: str, value: str):
        entity = self.get_entity(name)
        if not entity:
            return False, f"Entity '{name}' not found."
        
        try:
            self.db.execute("""
                INSERT INTO attributes (entity_id, key, value) 
                VALUES (?, ?, ?)
                ON CONFLICT(entity_id, key) DO UPDATE SET value=excluded.value
            """, (entity['id'], key, value))
            return True, f"Set {name}.{key} = {value}"
        except Exception as e:
            return False, f"Error setting attribute: {e}"

    def get_attributes(self, name: str):
        entity = self.get_entity(name)
        if not entity:
            return None
        rows = self.db.query("SELECT key, value FROM attributes WHERE entity_id = ?", (entity['id'],))
        return {row['key']: row['value'] for row in rows}

    def delete_attribute(self, name: str, key: str):
        entity = self.get_entity(name)
        if not entity: return False
        self.db.execute("DELETE FROM attributes WHERE entity_id = ? AND key = ?", (entity['id'], key))
        return True

    def find_entities(self, search_query: str):
        rows = self.db.query("SELECT category, name FROM entities WHERE name LIKE ?", (f"%{search_query}%",))
        return [(r['category'], r['name']) for r in rows]

    def list_all(self):
        rows = self.db.query("SELECT category, name FROM entities ORDER BY category, name")
        return [(r['category'], r['name']) for r in rows]
