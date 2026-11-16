import re
from pathlib import Path

LINK_PATTERN = re.compile(r"\[\[([^\]|#]+)")


class Vault:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, name):
        name = name.strip().replace("\\", "/")
        if not name:
            raise ValueError("nombre de nota vacío")
        rel = name if name.endswith(".md") else name + ".md"
        path = (self.root / rel).resolve()
        if self.root not in path.parents:
            raise ValueError("ruta fuera de la bóveda")
        return path

    def list_notes(self):
        return sorted(
            p.relative_to(self.root).with_suffix("").as_posix()
            for p in self.root.rglob("*.md")
            if ".obsidian" not in p.parts
        )

    def exists(self, name):
        return self._resolve(name).is_file()

    def read(self, name):
        path = self._resolve(name)
        if not path.is_file():
            raise FileNotFoundError(f"la nota '{name}' no existe")
        return path.read_text(encoding="utf-8")

    def write(self, name, content):
        path = self._resolve(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path.relative_to(self.root).as_posix()

    def append(self, name, content):
        path = self._resolve(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = path.read_text(encoding="utf-8") if path.is_file() else ""
        separator = "" if not existing or existing.endswith("\n") else "\n"
        path.write_text(existing + separator + content.rstrip("\n") + "\n", encoding="utf-8")
        return path.relative_to(self.root).as_posix()

    def search(self, query, limit=15):
        words = query.lower().split()
        if not words:
            return []
        results = []
        for note in self.list_notes():
            text = self._resolve(note).read_text(encoding="utf-8")
            haystack = (note + "\n" + text).lower()
            if not all(word in haystack for word in words):
                continue
            snippet = next(
                (line.strip() for line in text.splitlines() if any(w in line.lower() for w in words)),
                "",
            )
            results.append(f"{note}: {snippet}")
            if len(results) >= limit:
                break
        return results

    def links(self, name):
        text = self.read(name)
        found = []
        for target in LINK_PATTERN.findall(text):
            target = target.strip()
            if target not in found:
                found.append(target)
        return found

    def backlinks(self, name):
        target = name.strip().removesuffix(".md")
        short = target.split("/")[-1]
        sources = []
        for note in self.list_notes():
            if note == target:
                continue
            for link in self.links(note):
                if link.removesuffix(".md") in (target, short):
                    sources.append(note)
                    break
        return sources
