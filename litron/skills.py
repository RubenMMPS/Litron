from pathlib import Path

import yaml


def parse_skill(text):
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2]
    return meta, body.strip()


class Skills:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def catalog(self):
        items = []
        for file in sorted(self.root.glob("*/SKILL.md")):
            meta, _ = parse_skill(file.read_text(encoding="utf-8"))
            name = meta.get("name") or file.parent.name
            items.append({"name": name, "description": meta.get("description", "")})
        return items

    def load(self, name):
        for file in self.root.glob("*/SKILL.md"):
            meta, body = parse_skill(file.read_text(encoding="utf-8"))
            if (meta.get("name") or file.parent.name) == name:
                return body
        raise FileNotFoundError(f"la skill '{name}' no existe")
