# Litron

Asistente personal propio, escrito en Python. Combina un modelo de lenguaje intercambiable (en la nube o en local), una memoria en markdown compatible con Obsidian y skills que se cargan solo cuando hacen falta. Sin base de datos.

## Cómo funciona

1. Escribes un mensaje en la consola.
2. Litron lo envía al modelo junto con la lista de herramientas, el catálogo de skills y el índice de la memoria.
3. Si el modelo pide una herramienta (leer una nota, buscar, escribir, cargar una skill), Litron la ejecuta y le devuelve el resultado.
4. El ciclo se repite hasta que el modelo responde con texto o se alcanza `max_steps`.

Si el modelo principal falla por saturación, límite de cuota o falta de conexión, Litron pasa automáticamente al siguiente de la lista.

## Estructura

```
Litron/
├── config.yaml
├── .env
├── litron/
│   ├── __main__.py
│   ├── agent.py
│   ├── memory.py
│   └── skills.py
├── skills/
│   └── <nombre>/SKILL.md
└── vault/
    ├── index.md
    └── ...
```

- `config.yaml`: modelos, número máximo de pasos y rutas.
- `.env`: claves de API. No se sube a Git.
- `litron/agent.py`: bucle del agente, herramientas y respaldo entre modelos.
- `litron/memory.py`: lectura, escritura, búsqueda y enlaces de la bóveda.
- `litron/skills.py`: catálogo y carga de skills.
- `vault/`: la memoria. Se puede abrir como bóveda en Obsidian.
- `skills/`: una carpeta por skill, cada una con su `SKILL.md`.

## Instalación (Windows, PowerShell)

```powershell
cd ruta\a\Litron
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` y añade las claves que vayas a usar. Después:

```powershell
python -m litron
```

Comandos dentro de Litron: `/notas`, `/skills`, `/reset` y `/salir`.

## Configurar modelos

`config.yaml` contiene una lista ordenada. Litron usa el primero y, si falla con un error recuperable (servicio saturado, límite de cuota, tiempo agotado o conexión caída), prueba el siguiente.

```yaml
models:
  - name: gemini/<modelo>
  - name: openai/google/gemma-4-e4b
    api_base: http://localhost:1234/v1
max_steps: 8
vault_path: vault
skills_path: skills
index_note: index
```

Cada entrada admite opcionalmente `api_base`, `temperature` y `timeout` (60 segundos por defecto).

Los errores que no se resuelven cambiando de modelo, como una clave inválida o un nombre de modelo inexistente, no activan el respaldo y se muestran tal cual.

### Gemini

1. Crea una clave en Google AI Studio.
2. Guárdala en `.env` como `GEMINI_API_KEY`.
3. Usa `name: gemini/<modelo>`. Comprueba en AI Studio qué modelos tienes disponibles, porque los nombres cambian y los más antiguos dejan de estar disponibles para cuentas nuevas.

### Modelo local con LM Studio

1. En LM Studio, abre la pestaña Developer, carga el modelo y activa el servidor local (puerto 1234 por defecto).
2. Ajusta el contexto a unos 8192 y deja el offload a GPU al máximo.
3. Copia el identificador del modelo, que puedes ver con `curl http://localhost:1234/v1/models`.
4. En `config.yaml`, usa `name: openai/<identificador>` y `api_base: http://localhost:1234/v1`.
5. En `.env`, añade `OPENAI_API_KEY=local`. El servidor local no la valida, pero LiteLLM la exige.

Con 8 GB de VRAM, usa modelos de entre 7B y 8B cuantizados. Los modelos pequeños fallan más al encadenar herramientas, por lo que conviene que el principal sea uno remoto y el local quede como respaldo, o al revés si prefieres privacidad y coste cero.

### Otros proveedores

Con LiteLLM basta con cambiar `name` y la clave correspondiente en `.env`:

- Groq: `groq/<modelo>` y `GROQ_API_KEY`.
- OpenRouter: `openrouter/<modelo>` y `OPENROUTER_API_KEY`.
- Ollama: `ollama/<modelo>` con `api_base: http://localhost:11434`.

## Memoria

La memoria son notas `.md` dentro de `vault/`. Litron puede listarlas, leerlas, buscarlas, escribirlas, añadirles contenido y consultar sus enlaces `[[...]]`.

- `vault/index.md` se incluye en cada conversación. Mantenlo corto y enlaza desde él lo importante.
- Las notas se pueden organizar en subcarpetas (`proyectos/`, `diario/`).
- Litron no puede leer ni escribir fuera de `vault/`.
- La búsqueda separa la consulta en palabras y devuelve las notas que las contienen todas, ya sea en el nombre o en el contenido.
- La conversación no se guarda entre sesiones: solo persiste lo que se escriba en las notas.

## Skills

Una skill es una carpeta dentro de `skills/` con un `SKILL.md`:

```
---
name: mi-skill
description: Cuándo debe usarse, en una frase concreta.
---

Instrucciones paso a paso.
```

Al arrancar solo se muestran al modelo el nombre y la descripción. Cuando una descripción encaja con la tarea, el modelo carga el contenido completo con `load_skill`. Por eso la descripción es la parte más importante: es lo único que el modelo ve para decidir.

Reinicia Litron o usa `/reset` después de crear o modificar una skill.

## Mover a otra máquina

1. Copia o clona el proyecto.
2. Crea un entorno virtual nuevo e instala `requirements.txt`.
3. Crea el `.env` a mano con tus claves.
4. Ajusta `api_base` si el servidor local está en otra dirección.

El proyecto no usa rutas absolutas.

## Seguridad

- Nunca subas `.env` a Git. Está incluido en `.gitignore`.
- Litron puede escribir y sobrescribir notas sin pedir confirmación.
- No guardes contraseñas ni datos sensibles en la bóveda si el repositorio es público.

## Limitaciones actuales

- La conversación no persiste entre sesiones.
- Los modelos pequeños pueden equivocarse al elegir herramientas.
- No hay confirmación antes de escribir en la memoria.
- Solo interfaz de texto.

## Próximos pasos

- MCP de solo lectura para conectar herramientas externas.
- Voz local.
- HUD.