# Litron (fase 1)

Agente mínimo en Python con memoria en markdown (compatible con Obsidian), skills que se cargan bajo demanda y modelo intercambiable mediante LiteLLM. Sin base de datos.

## Estructura

- `config.yaml`: modelo, temperatura, rutas.
- `.env`: claves de API (no se sube a Git).
- `vault/`: la memoria. Ábrela como bóveda en Obsidian.
- `skills/<nombre>/SKILL.md`: cada skill con `name` y `description` en el encabezado. Solo la descripción va siempre en contexto; el cuerpo se carga cuando hace falta.
- `litron/`: el código (memoria, skills y bucle del agente).

## Instalación en Windows (PowerShell)

```powershell
cd ruta\a\litron
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` y pega tu clave. Para Gemini, créala gratis en Google AI Studio y ponla en `GEMINI_API_KEY`. Comprueba en AI Studio el nombre vigente del modelo y ajústalo en `config.yaml`.

Arranca:

```powershell
python -m litron
```

Comandos: `/notas`, `/skills`, `/reset`, `/salir`.

## Cambiar de modelo

Solo se edita `config.yaml`.

- Gemini: `model: gemini/<modelo>` y `GEMINI_API_KEY`.
- Groq: `model: groq/<modelo>` y `GROQ_API_KEY`.
- OpenRouter: `model: openrouter/<modelo>` y `OPENROUTER_API_KEY`.
- Ollama: `model: ollama/<modelo>`, `api_base: http://localhost:11434`.
- LM Studio (Vulkan, recomendado con AMD en Windows): arranca su servidor local y usa `model: openai/<modelo>`, `api_base: http://localhost:1234/v1` y `OPENAI_API_KEY=local`.

Con 8 GB de VRAM, limítate a modelos de 7B a 8B cuantizados. Los modelos locales pequeños fallan más al usar herramientas, así que si ves que no encadena bien los pasos, vuelve a un modelo remoto.

## Cómo crear una skill

1. Crea la carpeta `skills/mi-skill/`.
2. Dentro, un `SKILL.md` con este formato:

```
---
name: mi-skill
description: Cuándo debe usarse, en una frase concreta.
---

Instrucciones paso a paso.
```

3. Reinicia Litron o usa `/reset`.

La descripción es lo más importante: es lo único que el modelo ve de entrada para decidir si carga la skill.

## Mover a otra máquina

Copia o clona la carpeta entera, crea el entorno, copia tu `.env` a mano y ajusta `config.yaml`. No hay rutas absolutas en el proyecto.
