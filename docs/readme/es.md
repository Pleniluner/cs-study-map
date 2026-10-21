# cs-study-map · Material de informática para estudiar por cuenta propia

| [简体中文](../../README.md) | [繁體中文](zh-TW.md) | [English](en.md) | [日本語](ja.md) | [Русский](ru.md) | [Français](fr.md) | [Deutsch](de.md) | [Italiano](it.md) | [Português](pt.md) | [Español](es.md) | [العربية](ar.md) | [한국어](ko.md) |

El proyecto está pensado sobre todo para el aprendizaje de quien lo mantiene: selecciona temas de [REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT), los reorganiza en material en chino según sus requisitos previos y añade explicaciones, ejemplos originales, ejercicios resueltos y autoevaluaciones. La sincronización, clasificación con IA y guías de fuentes ayudan a elegir y actualizar el contenido.

**[Material didáctico](../textbook/index.md)** · [Mapa de estudio](../index.md) · [Cobertura](../status.md) · [Uso](../usage.md) · [Fuentes y licencias](../../ATTRIBUTION.md)

Es un proyecto personal de Pleniluner, sin vínculo oficial con la Universidad de Tsinghua ni con quienes mantienen el repositorio original. El repositorio público incluye herramientas propias, borradores, índices de fuentes y guías de IA. No publica materiales originales, diapositivas, tareas, código de estudiantes ni texto extraído completo.

## Estudia doce capítulos en orden

| # | Tema | Actividad |
| --- | --- | --- |
| 1 | [Binario, bytes y orden little-endian](../textbook/01-data-and-bytes.md) | Dividir un número en bytes y reconstruirlo desde la memoria |
| 2 | [Registros, memoria y pila](../textbook/02-execution-and-stack.md) | Seguir paso a paso el estado de una máquina simplificada |
| 3 | [Primer ajuste, división y fusión](../textbook/03-first-fit.md) | Simular asignación y liberación y explicar la fragmentación externa |
| 4 | [Secuencias, condiciones y bucles](../textbook/04-control-flow.md) | Seguir variables y comprobar límites y condiciones de terminación |
| 5 | [Parámetros, valores de retorno y funciones](../textbook/05-functions.md) | Combinar funciones y distinguir impresión, retorno y nombres locales |
| 6 | [Arreglos y listas secuenciales](../textbook/06-arrays.md) | Seguir índices, capacidad, listas compartidas y desplazamientos |
| 7 | [Listas enlazadas simples](../textbook/07-linked-lists.md) | Seguir referencias y realizar inserciones, eliminaciones e inversiones |
| 8 | [Pilas](../textbook/08-stacks.md) | Aplicar LIFO al historial de deshacer y a la comprobación de paréntesis |
| 9 | [Colas y arreglos circulares](../textbook/09-queues.md) | Comprobar FIFO, el retorno al inicio y los estados vacío o lleno |
| 10 | [Análisis de algoritmos](../textbook/10-algorithm-analysis.md) | Contar operaciones, comparar el crecimiento y evaluar la memoria adicional |
| 11 | [Búsqueda secuencial y binaria](../textbook/11-searching.md) | Seguir límites, duplicados y valores ausentes |
| 12 | [Ordenación por selección, inserción y mezcla](../textbook/12-sorting.md) | Comprobar orden, multiplicidades, estabilidad y búsqueda tras ordenar |

Los capítulos del 4 al 12 utilizan Python 3.11 o posterior e incluyen 90 programas independientes con sus salidas esperadas. Consulta las guías de [programación](../programming-practice.md), [estructuras de datos](../data-structures-practice.md) y [algoritmos](../algorithms-practice.md), en chino.

Cada capítulo incluye explicaciones detalladas, 2 ejemplos originales, 3 ejercicios con soluciones desplegables, una autoevaluación y las fuentes de los temas. Es un primer borrador de IA, sin revisión de especialistas ni pruebas con estudiantes; no significa que todos los cursos tengan un manual terminado.

## Qué puedes hacer

Estudia por capítulos y guarda notas privadas en `.local/`, excluido de Git. Crea capítulos originales a partir de temas identificados y conserva las versiones de las fuentes. Busca materiales por área, curso o tema identificado por IA y abre una revisión fija del repositorio original. Consulta temas, requisitos, sugerencias y ubicaciones de las evidencias; reutiliza análisis sin cambios y corrige la clasificación automática con reglas manuales.

Las guías de IA indican el alcance de la extracción, el modelo y su estado sin revisión humana. La integridad del catálogo y la cobertura de las guías se miden por separado. Se indican las extracciones parciales, los formatos no admitidos y los errores.

## Inicio rápido

Requiere Python 3.11 o posterior. Estos pasos obtienen metadatos y generan la navegación, sin clave de modelo ni descarga del contenido de las fuentes.

```bash
git clone https://github.com/Pleniluner/cs-study-map.git
cd cs-study-map
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
python -m pip install -e .
cs-study-map run --limit 0
```

## Ejecución de IA

Ambos modos comparten la validación y generación de guías. Para una API configura `CS_STUDY_API_BASE`, `CS_STUDY_MODEL` y `CS_STUDY_API_KEY`. Para Codex CLI local configura `CS_STUDY_PROVIDER=codex` y `CS_STUDY_MODEL`, y opcionalmente `CS_STUDY_CODEX_BIN`. La API admite Chat Completions y Responses: el valor predeterminado es `chat`; `CS_STUDY_API_STYLE=responses` selecciona Responses. Usa un modelo admitido por el servicio. La versión de Codex CLI debe admitir el modelo elegido y gestiona sus propias credenciales.

```bash
cs-study-map analyze --course 程序设计基础 --limit 2 --require-ai
cs-study-map write --limit 1 --require-ai
cs-study-map build
cs-study-map validate
```

Consulta la [guía de uso](../usage.md) para la configuración, los ejemplos de PowerShell y los ajustes de GitHub.

## Sincronización programada

GitHub Actions comprueba las fuentes cada día y permite iniciar **Sync study map** manualmente. Con un modelo configurado, genera guías y capítulos dentro del presupuesto, valida los resultados y registra los cambios. Los límites predeterminados son 6 materiales analizados y 1 capítulo escrito al día. El alcance se define en `config/curriculum.json`.

Sin modelo, el catálogo se sincroniza y se informa `not-configured`. Las guías existentes siguen disponibles y las fuentes modificadas esperan análisis. Las reglas de nombres y las salidas simuladas no se presentan como trabajo de IA terminado. No hace falta una cuenta de modelo para consultar el mapa. Los forks necesitan su propia configuración API; el inicio de sesión local de Codex no se sube a GitHub. GitHub puede desactivar la programación tras una inactividad prolongada; se reactiva en Actions.

## Estructura

```text
config/                  rutas, fuentes, clasificación, correspondencias y correcciones
catalog/                 metadatos, análisis, borradores y cobertura
docs/textbook/           Material legible en GitHub (actualmente en chino)
docs/                    navegación de cursos y áreas, plantilla de notas e instrucciones
src/cs_study_map/        sincronización, extracción, clasificación IA y redacción
tests/                   comprobaciones de sincronización, recuperación, procedencia y publicación
.github/workflows/       sincronización programada e integración continua
.cache/                  archivos locales y caché extraída; no publicar
.local/                  notas privadas; no publicar
```

La traducción del README no significa que el material didáctico esté traducido; actualmente está en chino.

Las correspondencias iniciales proceden de la organización personal del mantenedor y pueden corregirse. No son categorías oficiales del proyecto original ni un plan universitario. Los cursos nuevos quedan pendientes de clasificación. Se admite texto, código habitual, PDF con texto extraíble, DOCX, PPTX y Notebook. No se han implementado OCR, DOC/PPT antiguos ni análisis de archivos comprimidos. La extracción PDF se limita por defecto a 8 páginas y 10.000 caracteres; un documento largo puede leerse solo parcialmente.

## Validación y contribuciones

Ejecuta `python -m unittest discover -s tests -v` y `cs-study-map validate --tracked`. Informa de errores mediante Issues. Las PR pueden mejorar código, correspondencias y reglas manuales; consulta la [guía de contribución](../../CONTRIBUTING.md).

Los programas originales, el texto del manual y la documentación de mantenimiento usan la licencia MIT. Los derechos de los materiales fuente no cambian; consulta [fuentes y licencias](../../ATTRIBUTION.md).

Trabajo previo: [mapa general y 60 guías de cursos](../early-work/index.md), con el resumen de categorías y el README del manual. Los documentos existentes se incorporaron a Git conservando el contenido didáctico y eliminando las rutas locales absolutas.
