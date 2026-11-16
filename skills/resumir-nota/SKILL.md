---
name: resumir-nota
description: Úsala cuando Rubén pida resumir una nota, un texto pegado o un conjunto de notas de la memoria.
---

# Resumir

1. Si Rubén nombra una nota, léela con read_note. Si habla de un tema, usa search_notes y lee las notas relevantes.
2. Escribe el resumen en español con este formato:
   - Una frase con la idea principal.
   - De tres a cinco viñetas con los puntos clave.
   - Una línea final con las acciones pendientes, si las hay.
3. No añadas información que no esté en el texto original.
4. Pregunta si quiere guardar el resumen. Si acepta, usa write_note con el nombre `resumenes/<tema>` y enlaza la nota original con [[nombre]].
