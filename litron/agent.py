import json
from datetime import datetime

import litellm

from .memory import Vault
from .skills import Skills

litellm.drop_params = True


def tool(name, description, properties, required):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


NAME = {"type": "string", "description": "Ruta de la nota sin extensión, por ejemplo proyectos/inspiria"}
TEXT = {"type": "string", "description": "Contenido en markdown"}

TOOLS = [
    tool("list_notes", "Lista todas las notas de la memoria.", {}, []),
    tool("read_note", "Lee una nota de la memoria.", {"name": NAME}, ["name"]),
    tool(
        "search_notes",
        "Busca texto en todas las notas de la memoria.",
        {"query": {"type": "string", "description": "Texto a buscar"}},
        ["query"],
    ),
    tool("note_links", "Devuelve los enlaces [[...]] de una nota y las notas que la enlazan.", {"name": NAME}, ["name"]),
    tool(
        "write_note",
        "Crea o reemplaza una nota completa. Usa [[enlaces]] para conectarla con otras notas.",
        {"name": NAME, "content": TEXT},
        ["name", "content"],
    ),
    tool(
        "append_note",
        "Añade contenido al final de una nota, creándola si no existe.",
        {"name": NAME, "content": TEXT},
        ["name", "content"],
    ),
    tool(
        "load_skill",
        "Carga las instrucciones completas de una skill del catálogo.",
        {"name": {"type": "string", "description": "Nombre de la skill"}},
        ["name"],
    ),
]

SYSTEM_TEMPLATE = """Eres Litron, el asistente personal de Rubén. Respondes siempre en español, de forma directa y breve.

Tu memoria es una bóveda de notas en markdown enlazadas con [[enlaces]]. No inventes datos sobre Rubén: si necesitas algo, búscalo en la memoria con search_notes o read_note. Cuando aprendas algo duradero y útil sobre él, guárdalo con write_note o append_note, enlazando las notas relacionadas. No guardes contraseñas, claves ni números de cuentas.

Tienes un catálogo de skills. Cuando una tarea encaje con la descripción de una skill, cárgala con load_skill antes de actuar y sigue sus instrucciones.

Fecha y hora actuales: {now}

Skills disponibles:
{skills}

Índice de la memoria:
{index}
"""


class Agent:
    def __init__(self, config, base_dir):
        self.config = config
        self.vault = Vault(base_dir / config["vault_path"])
        self.skills = Skills(base_dir / config["skills_path"])
        self.messages = []
        self.reset()

    def system_prompt(self):
        catalog = self.skills.catalog()
        skills = "\n".join(f"- {s['name']}: {s['description']}" for s in catalog) or "(ninguna)"
        index_name = self.config.get("index_note", "index")
        index = self.vault.read(index_name)[:4000] if self.vault.exists(index_name) else "(vacío)"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return SYSTEM_TEMPLATE.format(now=now, skills=skills, index=index)

    def reset(self):
        self.messages = [{"role": "system", "content": self.system_prompt()}]

    def dispatch(self, name, args):
        try:
            match name:
                case "list_notes":
                    return "\n".join(self.vault.list_notes()) or "(sin notas)"
                case "read_note":
                    return self.vault.read(args["name"])
                case "search_notes":
                    return "\n".join(self.vault.search(args["query"])) or "(sin resultados)"
                case "note_links":
                    out = self.vault.links(args["name"])
                    back = self.vault.backlinks(args["name"])
                    return json.dumps({"enlaza_a": out, "enlazada_desde": back}, ensure_ascii=False)
                case "write_note":
                    return "guardada: " + self.vault.write(args["name"], args["content"])
                case "append_note":
                    return "añadido a: " + self.vault.append(args["name"], args["content"])
                case "load_skill":
                    return self.skills.load(args["name"])
                case _:
                    return f"herramienta desconocida: {name}"
        except Exception as error:
            return f"error: {error}"

    def complete(self):
        kwargs = {
            "model": self.config["model"],
            "messages": self.messages,
            "tools": TOOLS,
        }
        if self.config.get("temperature") is not None:
            kwargs["temperature"] = self.config["temperature"]
        if self.config.get("api_base"):
            kwargs["api_base"] = self.config["api_base"]
        return litellm.completion(**kwargs).choices[0].message

    def run(self, user_text, on_tool=None):
        self.messages.append({"role": "user", "content": user_text})
        for _ in range(self.config.get("max_steps", 8)):
            message = self.complete()
            entry = {"role": "assistant", "content": message.content or ""}
            calls = message.tool_calls or []
            if calls:
                entry["tool_calls"] = [
                    {
                        "id": c.id,
                        "type": "function",
                        "function": {"name": c.function.name, "arguments": c.function.arguments},
                    }
                    for c in calls
                ]
            self.messages.append(entry)
            if not calls:
                return message.content or ""
            for call in calls:
                try:
                    args = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                if on_tool:
                    on_tool(call.function.name, args)
                result = self.dispatch(call.function.name, args)
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "name": call.function.name,
                        "content": result,
                    }
                )
        return "Me quedé sin pasos antes de terminar. Reformula o divide la petición."
