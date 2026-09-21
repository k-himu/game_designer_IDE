import shlex
from engine import GameEngine


CHARACTER_TEMPLATE = {
    "hp": "10",
    "max_hp": "10",
    "atk": "0",
    "vit": "0",

    "move1": "",
    "move2": "",
    "move3": "",
    "move4": "",
    "move5": "",
    "move6": "",

    "ultimate": "",
    "talent": "",

    "rarity": "⭐⭐",
    "notes": ""
}


class Action:
    def execute(self, engine: GameEngine):
        pass

    def undo(self, engine: GameEngine):
        pass


class CreateTemplateAction(Action):
    def __init__(self, name, category="Character"):
        self.name = name
        self.category = category

    def execute(self, engine):

        success, msg = engine.create_entity(self.category, self.name)

        if not success:
            return success, msg

        for key, value in CHARACTER_TEMPLATE.items():
            engine.set_attribute(self.name, key, value)

        return True, f"Created {self.category} '{self.name}' from template."

    def undo(self, engine):
        engine.delete_entity(self.name)


class CreateAction(Action):
    def __init__(self, category, name):
        self.category = category
        self.name = name

    def execute(self, engine):
        return engine.create_entity(self.category, self.name)

    def undo(self, engine):
        engine.delete_entity(self.name)


class DeleteAction(Action):
    def __init__(self, name):
        self.name = name
        self.old_category = None
        self.old_attrs = {}

    def execute(self, engine):
        entity = engine.get_entity(self.name)
        if entity:
            self.old_category = entity["category"]
            self.old_attrs = engine.get_attributes(self.name) or {}
        return engine.delete_entity(self.name)

    def undo(self, engine):
        if self.old_category:
            engine.create_entity(self.old_category, self.name)
            for k, v in self.old_attrs.items():
                engine.set_attribute(self.name, k, v)


class SetAction(Action):
    def __init__(self, name, key, value):
        self.name = name
        self.key = key
        self.value = value
        self.old_value = None
        self.had_old = False

    def execute(self, engine):
        attrs = engine.get_attributes(self.name)

        if attrs and self.key in attrs:
            self.had_old = True
            self.old_value = attrs[self.key]

        return engine.set_attribute(self.name, self.key, self.value)

    def undo(self, engine):
        if self.had_old:
            engine.set_attribute(self.name, self.key, self.old_value)
        else:
            engine.delete_attribute(self.name, self.key)


class CompositeAction(Action):
    """
    Executes multiple actions as a single undo/redo unit.
    """

    def __init__(self, actions):
        self.actions = actions

    def execute(self, engine):
        executed = []

        for action in self.actions:
            success, msg = action.execute(engine)

            if not success:
                # Roll back anything already executed
                for a in reversed(executed):
                    a.undo(engine)
                return False, msg

            executed.append(action)

        return True, "Attributes updated."

    def undo(self, engine):
        for action in reversed(self.actions):
            action.undo(engine)


class CommandParser:
    def __init__(self, engine: GameEngine):
        self.engine = engine
        self.undo_stack = []
        self.redo_stack = []

    def execute(self, cmd_str: str) -> str:
        if not cmd_str.strip():
            return ""

        try:
            parts = shlex.split(cmd_str)
        except ValueError as e:
            return f"Command syntax error: {e}"

        action = parts[0].lower()

        # -----------------------------
        # Undo / Redo
        # -----------------------------
        if action == "undo":
            if not self.undo_stack:
                return "Nothing to undo."

            last_action = self.undo_stack.pop()
            last_action.undo(self.engine)
            self.redo_stack.append(last_action)
            return "Undo successful."

        elif action == "redo":
            if not self.redo_stack:
                return "Nothing to redo."

            next_action = self.redo_stack.pop()
            success, msg = next_action.execute(self.engine)

            if success:
                self.undo_stack.append(next_action)
                return "Redo successful."

            return msg

        cmd_action = None

        # -----------------------------
        # NEW
        # -----------------------------
        if action == "new" and len(parts) >= 2:

            name = parts[1]

            category = parts[2] if len(parts) > 2 else "Character"

            if category.lower() == "character":
                cmd_action = CreateTemplateAction(name, "Character")
            else:
                cmd_action = CreateAction(category, name)

        # -----------------------------
        # DELETE
        # -----------------------------
        elif action == "delete" and len(parts) >= 2:
            cmd_action = DeleteAction(parts[1])

        # -----------------------------
        # MULTI-SET
        # -----------------------------
        elif action == "set":

            text = cmd_str[3:].strip()

            lines = [x.strip() for x in text.replace(",", "\n").splitlines() if x.strip()]

            current_entity = None

            # First line can be just the entity name
            if len(lines) > 0 and " " not in lines[0] and "." not in lines[0]:
                current_entity = lines.pop(0)

            actions = []

            for line in lines:

                tokens = shlex.split(line)

                if len(tokens) < 2:
                    return f"Invalid assignment: {line}"

                target = tokens[0]
                value = " ".join(tokens[1:])

                if "." in target:
                    current_entity, attr = target.split(".", 1)
                else:
                    if current_entity is None:
                        return "Specify entity first."
                    attr = target

                actions.append(SetAction(current_entity, attr, value))

            cmd_action = CompositeAction(actions)

        # -----------------------------
        # Execute Mutable Command
        # -----------------------------
        if cmd_action:
            success, msg = cmd_action.execute(self.engine)

            if success:
                self.undo_stack.append(cmd_action)
                self.redo_stack.clear()

            return msg

        # -----------------------------
        # SHOW
        # -----------------------------
        if action == "show" and len(parts) >= 2:
            name = parts[1]

            entity = self.engine.get_entity(name)

            if not entity:
                return f"'{name}' not found."

            attrs = self.engine.get_attributes(name)

            lines = [f"[{entity['category']}] {name}"]

            if attrs:
                for k, v in attrs.items():
                    lines.append(f"  {k}: {v}")

            return "\n".join(lines)

        # -----------------------------
        # FIND
        # -----------------------------
        elif action == "find" and len(parts) >= 2:

            results = self.engine.find_entities(parts[1])

            if not results:
                return "No matches found."

            return "\n".join(
                f"{cat}: {name}"
                for cat, name in results
            )

        # -----------------------------
        # STATS
        # -----------------------------
        elif action == "stats":

            rows = self.engine.db.query(
                """
                SELECT category,
                       COUNT(*) AS count
                FROM entities
                GROUP BY category
                """
            )

            if not rows:
                return "Database is empty."

            return "\n".join(
                f"{r['category']}: {r['count']}"
                for r in rows
            )

        return (
            f"Unknown command: '{action}'. "
            "Try 'new', 'set', 'show', 'delete', "
            "'find', 'undo', 'redo', 'stats'."
        )