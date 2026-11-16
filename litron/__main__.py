import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

from .agent import Agent

BASE_DIR = Path(__file__).resolve().parent.parent


def load_config():
    with open(BASE_DIR / "config.yaml", encoding="utf-8") as file:
        return yaml.safe_load(file)


def show_tool(name, args):
    detail = args.get("name") or args.get("query") or ""
    print(f"  · {name} {detail}".rstrip())


def main():
    load_dotenv(BASE_DIR / ".env")
    agent = Agent(load_config(), BASE_DIR)
    print(f"Litron listo con {agent.config['model']}. Comandos: /reset, /notas, /skills, /salir")
    while True:
        try:
            text = input("\nTú > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text == "/salir":
            break
        if text == "/reset":
            agent.reset()
            print("Conversación reiniciada.")
            continue
        if text == "/notas":
            print("\n".join(agent.vault.list_notes()) or "(sin notas)")
            continue
        if text == "/skills":
            for item in agent.skills.catalog():
                print(f"- {item['name']}: {item['description']}")
            continue
        try:
            print("\nLitron > " + agent.run(text, on_tool=show_tool))
        except Exception as error:
            print(f"Error: {error}", file=sys.stderr)


if __name__ == "__main__":
    main()
