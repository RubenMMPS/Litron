---
name: nota-diaria
description: Úsala cuando Rubén quiera apuntar algo del día, hacer un registro diario, o pregunte qué hizo o qué quedó pendiente un día concreto.
---

# Nota diaria

Las notas del diario viven en `diario/AAAA-MM-DD`, usando la fecha actual que aparece en tu contexto.

Para apuntar algo:
1. Comprueba con list_notes si existe la nota de hoy.
2. Si no existe, créala con write_note con este contenido inicial:
   - Título `# AAAA-MM-DD`
   - Secciones `## Hecho`, `## Pendiente` y `## Notas`
3. Añade el apunte en la sección que corresponda con append_note, en forma de viñeta corta.
4. Si el apunte menciona un proyecto o persona con nota propia, enlázalo con [[nombre]].

Para consultar un día:
1. Lee la nota de esa fecha con read_note.
2. Si no existe, dilo sin inventar nada.
