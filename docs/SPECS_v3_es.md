# Cognitive Document Reader - Especificaciones Técnicas v3.0

> Especificaciones técnicas completas basadas en ingeniería inversa del proyecto implementado

---

## 🎯 Resumen Ejecutivo

**Cognitive Document Reader** es una librería Python que implementa procesamiento cognitivo de documentos que simula los patrones de lectura humana a través de un algoritmo secuencial multi-pasada con contexto acumulativo y principio de autoridad del texto fuente.

### Propósito Principal

Generar resúmenes jerárquicos de alta calidad y datasets contextualizados para:
- **Fine-tuning de LLMs**: Datasets que preserven la voz y metodología del autor original
- **Sistemas RAG**: Chunks enriquecidos con contexto jerárquico y conceptos clave
- **Lectura humana**: Resúmenes estructurados que respetan el flujo narrativo

### Diferenciación Técnica

A diferencia de los sistemas tradicionales de fragmentación de documentos, implementa:
- **Algoritmo secuencial** que procesa secciones en orden del documento
- **Contexto acumulativo** (padres + hermanos previos) para cada sección
- **Principio de autoridad** del texto fuente sobre cualquier información contextual
- **Procesamiento multi-pasada** con enriquecimiento contextual progresivo
- **Modelo dual** optimizado para velocidad vs. calidad según la pasada

---

## 🏗️ Arquitectura del Sistema

### Estructura de Módulos

```
src/cognitive_reader/
├── __init__.py                # API pública y exportaciones
├── _version.py                # Versionado automático
├── cli/
│   ├── __init__.py
│   └── main.py                # Interfaz de línea de comandos completa
├── core/
│   ├── __init__.py
│   ├── progressive_reader.py  # Motor principal de lectura cognitiva
│   └── synthesizer.py         # Síntesis jerárquica y generación de conocimiento
├── llm/
│   ├── __init__.py
│   ├── client.py              # Cliente LLM abstracto con LangChain
│   └── prompts.py             # Gestión centralizada de prompts
├── models/
│   ├── __init__.py
│   ├── config.py              # Configuración con Pydantic v2
│   ├── document.py            # Estructuras de documentos y secciones
│   ├── knowledge.py           # Definiciones de conceptos y lenguajes
│   └── llm_responses.py       # Modelos de respuesta estructurada
├── parsers/
│   ├── __init__.py
│   ├── docling_parser.py      # Parser universal con docling
│   └── structure_detector.py  # Detección de estructura jerárquica
└── utils/
    ├── __init__.py
    ├── language.py            # Detección de idioma
    ├── structure_formatter.py # Formateo y filtrado de estructura
    ├── text_cleaning.py       # Limpieza de texto
    └── tokens.py              # Utilities para contexto y tokens
```

### Patrón de Responsabilidades

#### **CognitiveReader** (Motor Principal)
- Orquestar el flujo completo de lectura cognitiva
- Gestionar procesamiento multi-pasada
- Coordinar entre componentes (parser, synthesizer, llm client)
- Aplicar filtros de desarrollo (max-depth, max-sections)

#### **DoclingParser** (Parsing Universal)
- Soporte multi-formato: PDF, DOCX, HTML, Markdown
- Conversión unificada a Markdown interno
- Extracción de metadatos de estructura jerárquica
- Configuración optimizada para diferentes tipos de documento

#### **StructureDetector** (Análisis Jerárquico)
- Detección automática de estructura jerárquica
- Construcción de relaciones padre-hijo
- Identificación de secciones con/sin contenido propio
- Asignación de índices de orden del documento

#### **LLMClient** (Abstracción LLM)
- Integración con LangChain para múltiples proveedores
- Gestión de modelos duales (fast/main)
- Respuestas estructuradas con Pydantic
- Manejo de errores y reintentos
- Modos de desarrollo (dry-run, mock)

#### **Synthesizer** (Generación de Conocimiento)
- Síntesis jerárquica bottom-up
- Generación de glosario de conceptos
- Filtrado inteligente de conceptos
- Construcción de metadata navegacional

#### **PromptManager** (Gestión de Prompts)
- Templates versionados y consistentes
- Soporte multi-idioma (EN/ES)
- Prompts optimizados por tipo de operación
- Integración del principio de autoridad

---

## 🔄 Algoritmo de Lectura Cognitiva

### Visión General del Procesamiento

```
[Documento] → [Parsing] → [Detección Estructura] → [Procesamiento Multi-pasada] → [Síntesis] → [Conocimiento Cognitivo]
                                                           ↓
                                                    ┌──────────────────┐
                                                    │   PASADA 1:      │
                                                    │   Secuencial +   │
                                                    │   Contexto       │
                                                    │   Acumulativo    │
                                                    └──────────────────┘
                                                           ↓
                                                    ┌──────────────────┐
                                                    │   PASADA 2:      │
                                                    │   Secuencial +   │
                                                    │   Contexto       │
                                                    │   Enriquecido    │
                                                    └──────────────────┘
```

### Algoritmo Secuencial Detallado

#### **Fase 1: Procesamiento Secuencial Básico**

1. **Ordenación por Secuencia del Documento**
   ```python
   ordered_sections = sorted(sections, key=lambda s: s.order_index)
   ```

2. **Procesamiento Secuencial con Contexto Acumulativo**
   ```python
   for section in ordered_sections:
       # Construir contexto acumulativo
       cumulative_context = build_cumulative_context(section, summaries)
       
       if section.has_content and not section.children_ids:
           # Sección hoja: procesar directamente
           summary = process_section_with_authority(section, cumulative_context)
           summaries[section.id] = summary
           
           # Actualizar niveles superiores incrementalmente
           update_parent_levels_incrementally(section, summary, summaries)
           
       elif section.has_content and section.children_ids:
           # Padre con contenido: procesar contenido propio
           summary = process_section_with_authority(section, cumulative_context)
           summaries[section.id] = summary
           
       else:
           # Padre sin contenido: diferir hasta que todos los hijos estén procesados
           pending_parents[section.id] = section
   ```

3. **Construcción de Contexto Acumulativo**
   ```python
   def build_cumulative_context(section, summaries):
       context_parts = []
       
       # 1. Contextos de todos los niveles padre
       parent_contexts = get_parent_contexts(section, summaries)
       if parent_contexts:
           context_parts.append("PARENT CONTEXT:\n" + "\n\n".join(parent_contexts))
       
       # 2. Contextos de hermanos anteriores (mismo nivel, orden menor)
       sibling_contexts = get_previous_sibling_contexts(section, summaries)
       if sibling_contexts:
           context_parts.append("PREVIOUS SIBLINGS:\n" + "\n\n".join(sibling_contexts))
       
       return "\n\n".join(context_parts)
   ```

4. **Principio de Autoridad del Texto Fuente**
   ```python
   def process_section_with_authority(section, cumulative_context):
       authority_content = f"""CONTEXT (background information only):
{cumulative_context}

SOURCE TEXT (AUTHORITATIVE - supreme authority):
{section.content}

CRITICAL INSTRUCTIONS:
1. The SOURCE TEXT is your PRIMARY source of truth
2. Use CONTEXT only as background information to inform understanding
3. If SOURCE TEXT contradicts any CONTEXT information:
   - Trust the SOURCE TEXT completely
   - Update your understanding based on SOURCE TEXT
4. Generate summary that accurately reflects the SOURCE TEXT"""
       
       return process_with_llm(authority_content, language)
   ```

#### **Fase 2: Procesamiento Secuencial Enriquecido**

1. **Mismo Orden Secuencial**
   - Replica exactamente el mismo orden de la Pasada 1
   - Mantiene la consistencia del algoritmo secuencial

2. **Contexto Selectivo Enriquecido**
   ```python
   def build_enriched_cumulative_context(section, current_summaries, previous_summaries, concept_glossary):
       # Contexto base de pasada actual
       base_context = build_cumulative_context(section, current_summaries)
       
       enriched_parts = []
       if base_context:
           enriched_parts.append(f"CURRENT CONTEXT:\n{base_context}")
       
       # Resumen previo del mismo nodo (de Pasada 1)
       if section.id in previous_summaries:
           prev_summary = previous_summaries[section.id]
           enriched_parts.append(f"PREVIOUS SUMMARY OF THIS SECTION:\n{prev_summary.title}: {prev_summary.summary}")
       
       # Glosario de conceptos (limitado a 10 para contexto manejable)
       if concept_glossary:
           glossary_entries = [f"{concept}: {definition}" for concept, definition in list(concept_glossary.items())[:10]]
           enriched_parts.append("CONCEPT GLOSSARY:\n" + "\n".join(glossary_entries))
       
       return "\n\n".join(enriched_parts)
   ```

3. **Preservación del Principio de Autoridad**
   ```python
   def process_section_with_enriched_authority(section, enriched_context):
       authority_content = f"""ENRICHED CONTEXT (background information only):
{enriched_context}

SOURCE TEXT (AUTHORITATIVE - supreme authority):
{section.content}

CRITICAL INSTRUCTIONS:
1. The SOURCE TEXT is your PRIMARY source of truth
2. Use ENRICHED CONTEXT only as background information
3. The enriched context includes previous summaries and concept definitions
4. If SOURCE TEXT contradicts any ENRICHED CONTEXT information:
   - Trust the SOURCE TEXT completely
5. Use concept definitions to enhance understanding but never override text meaning"""
       
       return process_with_llm(authority_content, language, model=main_model)
   ```

### Estrategia de Modelo Dual

#### **Configuración de Modelos**

```python
class CognitiveConfig:
    # Modelo rápido para escaneo inicial (Pasada 1)
    fast_pass_model: str = "llama3.1:8b"
    fast_pass_temperature: float = 0.05  # Muy conservador para fidelidad
    
    # Modelo de calidad para procesamiento profundo (Pasada 2+)
    main_model: str = "qwen3:8b"
    main_pass_temperature: float = 0.05  # Muy conservador para fidelidad
    
    def get_model_for_pass(self, pass_number: int) -> str:
        if pass_number == 1 and self.enable_fast_first_pass:
            return self.fast_pass_model
        return self.main_model
```

#### **Beneficios de la Estrategia Dual**

- **Pasada 1 (Rápida)**: Scan inicial eficiente para construir comprensión base
- **Pasada 2+ (Calidad)**: Análisis profundo con contexto enriquecido
- **Optimización de Costos**: Balance inteligente entre velocidad y calidad
- **Escalabilidad**: Procesa documentos grandes eficientemente

---

## 📊 Estructuras de Datos

### Modelos Fundamentales

#### **DocumentSection** (Inmutable)
```python
@dataclass(frozen=True)
class DocumentSection:
    id: str                    # Identificador único
    title: str                 # Título limpio de la sección
    content: str               # Contenido de texto completo
    level: int                 # Nivel jerárquico (0=root, 1=chapter, etc.)
    parent_id: Optional[str]   # ID de sección padre
    children_ids: List[str]    # IDs de secciones hijas
    order_index: int           # Orden de aparición en documento
    is_heading: bool = False   # True si representa encabezado real
```

#### **SectionSummary** (Resultado de Procesamiento)
```python
class SectionSummary(BaseModel):
    section_id: str           # Referencia a DocumentSection.id
    title: str                # Título de sección
    summary: str              # Resumen cognitivo refinado
    key_concepts: List[str]   # Lista de conceptos clave (max 5)
    parent_id: Optional[str]  # ID de sección padre
    children_ids: List[str]   # IDs de secciones hijas
    level: int                # Nivel jerárquico
    order_index: int          # Orden de aparición
```

#### **ConceptDefinition** (Glosario Cognitivo)
```python
class ConceptDefinition(BaseModel):
    concept_id: str           # ID único (ej: "sedentarismo")
    name: str                 # Nombre legible
    definition: str           # Definición refinada cognitivamente
    first_mentioned_in: str   # ID de sección donde se identificó primero
    relevant_sections: List[str]  # IDs donde el concepto es relevante
```

#### **CognitiveKnowledge** (Output Final)
```python
class CognitiveKnowledge(BaseModel):
    # Metadatos de documento
    document_title: str
    document_summary: str     # Resumen a nivel documento
    detected_language: LanguageCode
    
    # Resúmenes jerárquicos (optimizados para RAG)
    hierarchical_summaries: Dict[str, SectionSummary]
    
    # Glosario de conceptos clave
    concepts: List[ConceptDefinition]
    
    # Índices de navegación
    hierarchy_index: Dict[str, List[str]]      # Nivel -> IDs de sección
    parent_child_map: Dict[str, List[str]]     # Padre -> Hijos
    
    # Estadísticas
    total_sections: int
    avg_summary_length: float
    total_concepts: int
```

### Configuración del Sistema

#### **CognitiveConfig** (Configuración Completa)
```python
class CognitiveConfig(BaseModel):
    # Configuración LLM
    model_name: str = "qwen3:8b"              # Modelo por defecto
    temperature: float = 0.1                  # Temperatura base
    
    # Estrategia de modelo dual
    enable_fast_first_pass: bool = True       # Usar modelo rápido para Pasada 1
    fast_pass_model: str = "llama3.1:8b"      # Modelo rápido
    main_model: str = "qwen3:8b"              # Modelo de calidad
    fast_pass_temperature: float = 0.05       # Temperatura para scan rápido
    main_pass_temperature: float = 0.05       # Temperatura para calidad
    
    # Configuración multi-pasada
    num_passes: int = 2                       # Número de pasadas cognitivas
    max_passes: int = 2                       # Máximo pasadas (extensibilidad)
    convergence_threshold: float = 0.1        # Umbral de convergencia
    
    # Procesamiento de documentos
    chunk_size: int = 1000                    # Tamaño de chunk
    chunk_overlap: int = 200                  # Solapamiento de chunks
    context_window: int = 16384               # Ventana de contexto LLM
    document_language: LanguageCode = AUTO    # Idioma del documento
    
    # Optimización de resúmenes (basado en palabras para control natural)
    target_summary_words: int = 250           # Objetivo para resúmenes de sección
    min_summary_words: int = 150              # Mínimo palabras
    max_summary_words: int = 400              # Máximo palabras
    target_document_summary_words: int = 400  # Objetivo para resumen de documento
    max_hierarchy_depth: int = 10             # Profundidad máxima de jerarquía
    
    # Características cognitivas
    enable_refinement: bool = True            # Habilitar refinamiento
    refinement_threshold: float = 0.4         # Umbral para refinamiento
    
    # Configuración de proveedor LLM
    llm_provider: str = "ollama"              # Proveedor (ollama, openai, etc.)
    ollama_base_url: str = "http://localhost:11434"  # URL base de Ollama
    timeout_seconds: int = 120                # Timeout de requests
    max_retries: int = 3                      # Máximos reintentos
    
    # Filtrado de glosario
    max_glossary_concepts: int = 50           # Máximo conceptos en glosario
    min_glossary_concepts: int = 10           # Mínimo conceptos
    cross_section_score_cap: float = 0.5     # Cap para relevancia multi-sección
    complexity_score_multiplier: float = 0.2 # Multiplicador de complejidad
    complexity_score_cap: float = 0.3        # Cap de puntuación de complejidad
    base_concept_score: float = 0.2           # Puntuación base para conceptos LLM
    
    # Características de desarrollo
    dry_run: bool = False                     # Modo dry-run (sin llamadas LLM)
    mock_responses: bool = False              # Usar respuestas mock
    validate_config_only: bool = False        # Solo validar configuración
    save_partial_results: bool = False        # Guardar resultados parciales
    partial_results_dir: str = "./partial_results"  # Directorio de parciales
    single_pass: bool = False                 # Forzar procesamiento de una pasada
    save_intermediate: bool = False           # Guardar estado entre pasadas
    intermediate_dir: str = "./intermediate_passes"  # Directorio intermedio
    max_sections: Optional[int] = None        # Máximo secciones (desarrollo)
    disable_reasoning: bool = False           # Desactivar modo reasoning
    skip_glossary: bool = False               # Saltar generación de glosario
    show_context_usage: bool = False          # Mostrar uso de ventana de contexto
    
    @classmethod
    def from_env(cls) -> "CognitiveConfig":
        """Cargar configuración desde variables de entorno con fallback a defaults."""
```

---

## 🔧 Stack Tecnológico y Dependencias

### Lenguaje y Runtime

#### **Python 3.12+**
- **Características modernas**: Type annotations, pattern matching, improved error messages
- **Async/await nativo**: Soporte completo para operaciones asíncronas
- **Compatibilidad**: 3.12+ requerido para características de typing modernas

### Dependencias Principales

#### **Gestión de Datos y Validación**
```toml
pydantic = ">=2.0,<3.0"      # Validación de datos y configuración
```
- Validación automática de tipos
- Configuración desde variables de entorno
- Serialización JSON
- Modelos immutables con `frozen=True`

#### **Cliente HTTP Asíncrono**
```toml
aiohttp = ">=3.8,<4.0"       # Cliente HTTP async (backup para llamadas directas)
```
- Soporte para operaciones concurrentes
- Timeout y retry handling
- Context managers para gestión de recursos

#### **Framework CLI**
```toml
click = ">=8.0,<9.0"         # Framework para interfaz de línea de comandos
```
- Comandos complejos con múltiples opciones
- Validación automática de parámetros
- Help text generado automáticamente
- Manejo de archivos y paths

#### **Procesamiento de Documentos**
```toml
docling = ">=2.40,<3.0"      # Parser universal de documentos
```
- Soporte para PDF, DOCX, HTML, Markdown
- Extracción de estructura jerárquica
- Configuraciones optimizadas por formato
- Conversión unificada a Markdown interno

#### **Detección de Idioma**
```toml
langdetect = ">=1.0,<2.0"    # Detección automática de idioma
```
- Auto-detección de español/inglés
- Fallback configurable

#### **Configuración de Entorno**
```toml
python-dotenv = ">=1.0,<2.0" # Soporte para archivos .env
```
- Carga automática de .env
- No sobrescribe variables existentes

#### **Integración LLM**
```toml
langchain-core = ">=0.3,<1.0"    # Funcionalidad core de LangChain
langchain-ollama = ">=0.2,<1.0"  # Integración con Ollama
```
- Abstracción de múltiples proveedores LLM
- Respuestas estructuradas con Pydantic
- Manejo de errores y reintentos integrado

### Herramientas de Desarrollo

#### **Testing**
```toml
pytest = ">=7.0,<8.0"           # Framework de testing
pytest-asyncio = ">=0.21,<1.0"  # Soporte async para pytest
```

#### **Linting y Formateo**
```toml
ruff = ">=0.1,<1.0"             # Linting y formateo ultra-rápido
```
- Configuración:
  ```toml
  [tool.ruff]
  target-version = "py312"
  line-length = 88
  
  [tool.ruff.lint]
  select = ["E", "F", "I", "N", "W", "UP"]
  ignore = ["E501"]
  
  [tool.ruff.format]
  quote-style = "double"
  indent-style = "space"
  ```

#### **Verificación de Tipos**
```toml
mypy = ">=1.0,<2.0"             # Verificación estática de tipos
```
- Configuración estricta:
  ```toml
  [tool.mypy]
  python_version = "3.12"
  strict = true
  warn_return_any = true
  warn_unused_configs = true
  disallow_untyped_defs = true
  disallow_any_generics = true
  ```

### Gestión de Dependencias

#### **uv** (Herramienta Principal)
```bash
# Instalación del proyecto
uv sync

# Comandos de desarrollo
uv run ruff check .
uv run ruff format .
uv run mypy src/
uv run pytest
uv run cognitive-reader --help
```

#### **Configuración pyproject.toml**
```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "cognitive-document-reader"
dynamic = ["version"]
requires-python = ">=3.12"

[project.scripts]
cognitive-reader = "cognitive_reader.cli.main:cli"

[tool.hatch.version]
source = "vcs"
tag-regex = "^v(?P<version>\\d+\\.\\d+\\.\\d+)$"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0,<8.0",
    "pytest-asyncio>=0.21,<1.0",
    "ruff>=0.1,<1.0",
    "mypy>=1.0,<2.0",
]
```

---

## 🌐 Interfaz de Usuario

### API de Programación

#### **Interfaz Pública Principal**
```python
from cognitive_reader import CognitiveReader, CognitiveConfig

# Configuración desde entorno
config = CognitiveConfig.from_env()

# Inicialización
reader = CognitiveReader(config)

# Procesamiento de archivos
knowledge = await reader.read_document("document.pdf")

# Procesamiento de texto directo
knowledge = await reader.read_document_text(text_content, "Document Title")

# Acceso a resultados
print(knowledge.document_title)
print(knowledge.document_summary)
for section_id, summary in knowledge.hierarchical_summaries.items():
    print(f"{summary.title}: {summary.summary}")
```

#### **Configuración Programática**
```python
# Configuración de desarrollo
config = CognitiveConfig(
    dry_run=True,
    mock_responses=True,
    save_partial_results=True,
    max_sections=5
)

# Configuración de producción
config = CognitiveConfig(
    fast_pass_model="llama3.1:8b",
    main_model="qwen3:8b",
    num_passes=2,
    document_language=LanguageCode.ES
)

# Configuración personalizada
config = CognitiveConfig(
    target_summary_words=300,
    max_glossary_concepts=30,
    context_window=32768
)
```

### Interfaz de Línea de Comandos

#### **Comando Principal**
```bash
cognitive-reader [DOCUMENT] [OPTIONS]
```

#### **Opciones de Salida**
```bash
# Formatos de salida
--output, -o [json|markdown]        # Formato de output (default: markdown)
--output-file, -f PATH              # Guardar a archivo en lugar de stdout

# Configuración de idioma
--language, -l [auto|en|es]         # Idioma del documento (default: auto)
```

#### **Configuración de Modelo**
```bash
# Configuración básica
--model, -m MODEL                   # Modelo LLM a usar
--temperature, -t FLOAT             # Temperatura LLM (0.0-2.0)

# Modos de procesamiento
--fast-mode                         # Usar modelo rápido (optimiza velocidad)
--single-pass                       # Forzar procesamiento de una pasada
--disable-reasoning                 # Desactivar modo reasoning
```

#### **Características de Desarrollo**
```bash
# Modos de testing
--dry-run                          # Ejecutar sin llamadas LLM reales
--mock-responses                   # Usar respuestas mock para testing
--validate-config                  # Solo validar configuración

# Control de procesamiento
--max-sections INT                 # Máximo secciones a procesar
--max-depth INT                    # Máximo nivel jerárquico
--structure-only                   # Mostrar solo estructura sin procesamiento

# Guardado de resultados
--save-partials                    # Guardar resultados parciales
--partials-dir PATH                # Directorio para resultados parciales
--save-intermediate                # Guardar estado entre pasadas

# Configuración de resúmenes
--target-words INT                 # Objetivo palabras para resúmenes
--min-words INT                    # Mínimo palabras
--max-words INT                    # Máximo palabras
--skip-glossary                    # Saltar generación de glosario

# Debugging y optimización
--show-context-usage               # Mostrar uso de ventana de contexto
--verbose, -v                      # Logging detallado
--quiet, -q                        # Suprimir output excepto resultados
```

#### **Ejemplos de Uso**
```bash
# Uso básico
cognitive-reader document.pdf

# Desarrollo y testing
cognitive-reader document.md --dry-run --save-partials --max-sections 5

# Configuración personalizada
cognitive-reader document.pdf --output json --language es --target-words 300

# Análisis rápido
cognitive-reader large_doc.pdf --fast-mode --max-depth 2 --skip-glossary

# Testing de estructura
cognitive-reader document.md --structure-only --max-depth 3
```

### Configuración via Variables de Entorno

#### **Variables Principales**
```bash
# Configuración LLM
COGNITIVE_READER_MODEL=qwen3:8b                    # Modelo por defecto
COGNITIVE_READER_TEMPERATURE=0.1                  # Temperatura base

# Estrategia dual
COGNITIVE_READER_FAST_PASS_MODEL=llama3.1:8b      # Modelo rápido
COGNITIVE_READER_MAIN_MODEL=qwen3:8b               # Modelo principal
COGNITIVE_READER_FAST_PASS_TEMPERATURE=0.05       # Temperatura scan rápido
COGNITIVE_READER_MAIN_PASS_TEMPERATURE=0.05       # Temperatura calidad

# Multi-pasada
COGNITIVE_READER_NUM_PASSES=2                     # Número de pasadas
COGNITIVE_READER_ENABLE_FAST_FIRST_PASS=true      # Habilitar dual model
COGNITIVE_READER_SINGLE_PASS=false                # Forzar single-pass
COGNITIVE_READER_SAVE_INTERMEDIATE=false          # Guardar intermedio

# Procesamiento
COGNITIVE_READER_CONTEXT_WINDOW=16384             # Ventana de contexto
COGNITIVE_READER_TARGET_SUMMARY_WORDS=250         # Palabras objetivo
COGNITIVE_READER_MAX_GLOSSARY_CONCEPTS=50         # Max conceptos glosario
COGNITIVE_READER_LANGUAGE=auto                    # Idioma (auto/en/es)

# Desarrollo
COGNITIVE_READER_DRY_RUN=false                    # Modo dry-run
COGNITIVE_READER_MOCK_RESPONSES=false             # Respuestas mock
COGNITIVE_READER_SAVE_PARTIAL_RESULTS=false      # Guardar parciales
COGNITIVE_READER_SHOW_CONTEXT_USAGE=false        # Mostrar uso contexto

# Proveedor LLM
COGNITIVE_READER_LLM_PROVIDER=ollama              # Proveedor
COGNITIVE_READER_OLLAMA_BASE_URL=http://localhost:11434  # URL Ollama
```

#### **Archivo .env de Ejemplo**
```bash
# Copia env.example a .env y modifica según necesidades
cp env.example .env
```

---

## 📄 Formatos de Entrada y Salida

### Formatos de Documento Soportados

#### **Formatos Principales** (con docling)
- **PDF** (.pdf): Preserva layout y estructura
- **DOCX** (.docx): Documentos Microsoft Word
- **HTML** (.html): Páginas web y contenido HTML
- **Markdown** (.md, .markdown): Soporte nativo optimizado

#### **Estrategia de Procesamiento**
- Docling integrado para todos los formatos soportados
- Conversión interna unificada a Markdown para procesamiento consistente
- Detección automática de formato basada en extensión
- Configuraciones optimizadas por tipo de documento

### Formato de Salida JSON

#### **Estructura Completa**
```json
{
  "document_title": "Título del Documento",
  "document_summary": "Resumen cognitivo a nivel documento...",
  "detected_language": "es",
  
  "hierarchical_summaries": {
    "section_1": {
      "section_id": "section_1",
      "title": "Introducción",
      "summary": "Resumen cognitivo refinado de la sección...",
      "key_concepts": ["concepto1", "concepto2", "concepto3"],
      "parent_id": null,
      "children_ids": ["section_1_1", "section_1_2"],
      "level": 1,
      "order_index": 0
    },
    "section_1_1": {
      "section_id": "section_1_1",
      "title": "Antecedentes",
      "summary": "Contexto histórico y marco teórico...",
      "key_concepts": ["concepto_historico", "marco_teorico"],
      "parent_id": "section_1",
      "children_ids": [],
      "level": 2,
      "order_index": 1
    }
  },
  
  "concepts": [
    {
      "concept_id": "concepto1",
      "name": "Concepto Principal",
      "definition": "Definición cognitiva refinada con contexto específico del documento...",
      "first_mentioned_in": "section_1",
      "relevant_sections": ["section_1", "section_2", "section_3"]
    }
  ],
  
  "hierarchy_index": {
    "0": ["root"],
    "1": ["section_1", "section_2", "section_3"],
    "2": ["section_1_1", "section_1_2", "section_2_1"]
  },
  
  "parent_child_map": {
    "root": ["section_1", "section_2", "section_3"],
    "section_1": ["section_1_1", "section_1_2"]
  },
  
  "total_sections": 8,
  "avg_summary_length": 247.5,
  "total_concepts": 12
}
```

### Formato de Salida Markdown

#### **Estructura Markdown**
```markdown
# Título del Documento - Análisis Cognitivo

> **Procesamiento**: Lectura cognitiva de 2 pasadas | 8 secciones | 12 conceptos

## 📖 Resumen del Documento
Resumen cognitivo completo que integra comprensión de todas las secciones...

## 📄 Resúmenes de Secciones

### 1. Introducción
**Resumen**: Resumen cognitivo refinado de la sección...
**Conceptos Clave**: concepto1, concepto2, concepto3

#### 1.1. Antecedentes
**Resumen**: Contexto histórico y marco teórico...
**Conceptos Clave**: concepto_historico, marco_teorico

## 📚 Glosario de Conceptos

### concepto1 - Concepto Principal
Definición cognitiva refinada con contexto específico del documento...
*Primera mención*: Introducción
*Relevante en*: Introducción, Desarrollo, Conclusiones

## 📊 Estadísticas de Procesamiento
- **Total de secciones**: 8
- **Promedio longitud resúmenes**: 247.5 caracteres
- **Total conceptos identificados**: 12
```

### Formatos de Desarrollo

#### **Resultados Parciales** (JSON)
```json
{
  "progress": {
    "section_index": 3,
    "total_sections": 8,
    "progress_percentage": 37.5
  },
  "section": {
    "id": "section_3",
    "title": "Metodología",
    "level": 1,
    "order_index": 2,
    "content_preview": "La metodología empleada en este estudio..."
  },
  "summary": {
    "title": "Metodología",
    "summary": "Descripción detallada del enfoque metodológico...",
    "key_concepts": ["metodologia", "enfoque_cuantitativo", "analisis_estadistico"],
    "level": 1,
    "order_index": 2
  },
  "context": {
    "accumulated_context_length": 1247,
    "accumulated_context_preview": "Introducción: Contexto general del problema..."
  },
  "config": {
    "model_used": "llama3.1:8b",
    "enable_fast_first_pass": true,
    "temperature": 0.05
  }
}
```

#### **Resultados Intermedios** (JSON)
```json
{
  "pass_number": 1,
  "description": "Sequential processing with cumulative context",
  "language": "es",
  "timestamp": "20241215_143052",
  "total_sections": 8,
  "total_summaries": 8,
  "sections": [...],
  "summaries": {...}
}
```

---

## 🔍 Gestión de Prompts

### Arquitectura de Prompts

#### **PromptManager** (Centralizado)
```python
class PromptManager:
    PROMPT_VERSION = "v1.4.0"  # Versionado de prompts
    
    LANGUAGE_NAMES = {
        LanguageCode.EN: "English",
        LanguageCode.ES: "Spanish",
        LanguageCode.AUTO: "English"
    }
    
    def get_prompt(self, prompt_type: str, language: LanguageCode) -> str:
        # Template unificado con reemplazo de {{language}}
        
    def format_section_summary_prompt(
        self, section_title: str, section_content: str, 
        accumulated_context: str, language: LanguageCode,
        target_words: int, min_words: int, max_words: int
    ) -> str:
        # Prompt para resúmenes de sección con parámetros de longitud
```

#### **Templates de Prompts Principales**

**1. Resumen de Sección**
```
You are an expert document analyzer specializing in creating high-quality summaries in {{language}}.

CONTEXT FROM PREVIOUS SECTIONS:
{accumulated_context}

SECTION TO ANALYZE:
Title: {section_title}
Content: {section_content}

INSTRUCTIONS:
Create a comprehensive summary in {{language}} that:
1. Captures the main ideas and key points
2. Maintains context from previous sections
3. Identifies important concepts and terminology
4. Length: {target_words} words (min: {min_words}, max: {max_words})

Provide:
1. A clear, informative summary
2. Up to 5 key concepts found in this section
```

**2. Resumen de Documento**
```
You are an expert document analyzer creating a comprehensive document summary in {{language}}.

DOCUMENT TITLE: {document_title}

SECTION SUMMARIES:
{section_summaries}

INSTRUCTIONS:
Create a comprehensive document-level summary in {{language}} that:
1. Integrates insights from all sections
2. Captures the document's main thesis and conclusions
3. Maintains coherence and logical flow
4. Length: {target_words} words (min: {min_words}, max: {max_words})

Focus on the document's primary contributions and key insights.
```

**3. Definición de Conceptos**
```
You are an expert in {{language}} specialized in creating precise concept definitions.

DOCUMENT CONTEXT:
{document_summary}

CONCEPT TO DEFINE: {concept_name}

SECTIONS WHERE MENTIONED:
{relevant_sections}

INSTRUCTIONS:
Create a precise definition in {{language}} for this concept that:
1. Is accurate based on how it's used in this document
2. Captures the specific meaning in this context
3. Is clear and informative
4. Avoids generic definitions - focus on document-specific usage

Provide only the definition, no meta-commentary.
```

### Principio de Autoridad en Prompts

#### **Template de Autoridad para Contexto**
```
CONTEXT (background information only):
{cumulative_context}

SOURCE TEXT (AUTHORITATIVE - supreme authority):
{section_content}

CRITICAL INSTRUCTIONS:
1. The SOURCE TEXT is your PRIMARY source of truth
2. Use CONTEXT only as background information to inform understanding
3. If SOURCE TEXT contradicts any CONTEXT information:
   - Trust the SOURCE TEXT completely
   - Update your understanding based on SOURCE TEXT
   - The SOURCE TEXT is always correct
4. Generate summary that accurately reflects the SOURCE TEXT
5. Identify concepts mentioned in SOURCE TEXT (not just from context)

Remember: SOURCE TEXT has supreme authority over all context information.
```

#### **Template de Autoridad para Contexto Enriquecido**
```
ENRICHED CONTEXT (background information only):
{enriched_context}

SOURCE TEXT (AUTHORITATIVE - supreme authority):
{section_content}

CRITICAL INSTRUCTIONS:
1. The SOURCE TEXT is your PRIMARY source of truth
2. Use ENRICHED CONTEXT only as background information
3. The enriched context includes previous summaries and concept definitions
4. If SOURCE TEXT contradicts any ENRICHED CONTEXT information:
   - Trust the SOURCE TEXT completely
   - Update your understanding based on SOURCE TEXT
5. Generate summary that accurately reflects the SOURCE TEXT
6. Use concept definitions to enhance understanding but never override text meaning

Remember: SOURCE TEXT has supreme authority over all enriched context information.
```

### Respuestas Estructuradas

#### **Modelos de Respuesta LLM**
```python
class SectionSummaryResponse(BaseModel):
    summary: str = Field(description="Clear, concise summary of the section content")
    key_concepts: List[str] = Field(
        max_length=5,
        description="List of up to 5 key concepts found in the section"
    )

class ConceptDefinitionResponse(BaseModel):
    definition: str = Field(
        description="Clear, direct definition of the concept without meta-references"
    )
```

---

## ⚙️ Requisitos No Funcionales

### Rendimiento

#### **Requisitos de Velocidad**
- **Tiempo de procesamiento**: <2 minutos para documentos de 50 páginas en modo dual
- **Tiempo de scan inicial**: <30 segundos para documentos de 50 páginas en modo rápido
- **Paralelización**: Soporte para procesamiento concurrente de múltiples documentos
- **Memoria**: <500MB de RAM para documentos típicos (<100 páginas)

#### **Optimizaciones**
- **Modelo dual**: Balance automático entre velocidad (fast model) y calidad (main model)
- **Contexto inteligente**: Truncado automático de contexto cuando excede límites
- **Caching**: Reutilización de contexto entre pasadas
- **Batching**: Agrupación eficiente de requests LLM cuando sea posible

### Escalabilidad

#### **Límites de Documento**
- **Tamaño máximo**: 500 páginas (configurable)
- **Secciones máximas**: 1000 secciones (configurable via `max_sections`)
- **Profundidad jerárquica**: 10 niveles (configurable via `max_hierarchy_depth`)
- **Conceptos en glosario**: 50 conceptos (configurable via `max_glossary_concepts`)

#### **Gestión de Recursos**
- **Ventana de contexto**: Manejo dinámico según modelo LLM (default 16384 tokens)
- **Límites de memoria**: Procesamiento streaming para documentos grandes
- **Timeout inteligente**: Incremento automático de timeout para documentos complejos
- **Fallback graceful**: Degradación elegante ante errores de recursos

### Confiabilidad

#### **Manejo de Errores**
- **Reintentos automáticos**: Hasta 3 reintentos con backoff exponencial
- **Fallback de modelos**: Cambio automático a modelo alternativo ante fallos
- **Validación de entrada**: Validación exhaustiva de documentos antes del procesamiento
- **Recuperación parcial**: Continuación desde último estado válido en caso de fallo

#### **Tolerancia a Fallos**
- **Guardar estado intermedio**: Checkpoints automáticos entre pasadas
- **Validación de salida**: Verificación de integridad de resultados
- **Logs detallados**: Trazabilidad completa de errores para debugging
- **Modo degradado**: Funcionamiento con funcionalidades reducidas ante fallos parciales

### Mantenibilidad

#### **Versionado y Evolución**
- **API estable**: Compatibilidad hacia atrás de interfaces principales
- **Schema versionado**: JSON output con versioning para consumidores
- **Prompts versionados**: Control de versión de templates con números de versión
- **Configuración extensible**: Adición de nuevos parámetros sin romper compatibilidad

#### **Debugging y Monitoreo**
- **Modos de desarrollo**: dry-run, mock responses, partial saves
- **Logs estructurados**: Información detallada para troubleshooting
- **Métricas de rendimiento**: Tracking de tiempo, memoria, y uso de contexto
- **Validación de configuración**: Verificación completa de setup antes de procesamiento

### Seguridad

#### **Protección de Datos**
- **Procesamiento local**: LLMs locales por defecto (Ollama)
- **Sin persistencia**: Datos no almacenados permanentemente salvo configuración explícita
- **Sanitización de entrada**: Limpieza de contenido potencialmente problemático
- **Aislamiento de procesos**: Separación entre procesamiento y almacenamiento

#### **Configuración Segura**
- **Variables de entorno**: Configuración sensible via environment variables
- **Validación estricta**: Pydantic validation para todos los inputs
- **URLs configurables**: No hardcoding de endpoints
- **Timeouts apropiados**: Protección contra hanging requests

### Usabilidad

#### **Experiencia de Desarrollo**
- **Documentación completa**: Ejemplos, guías, y API reference
- **Mensajes de error claros**: Información específica y accionable
- **Configuración flexible**: Multiple métodos de configuración
- **Testing integrado**: Modos mock para desarrollo sin dependencias

#### **Experiencia de Usuario Final**
- **CLI intuitiva**: Comandos claros con help integrado
- **Feedback de progreso**: Indicadores de avance para documentos largos
- **Múltiples formatos**: Salida en JSON y Markdown según necesidades
- **Validación temprana**: Detección de problemas antes del procesamiento completo

---

## 🧪 Estrategia de Testing

### Arquitectura de Testing

#### **Organización de Tests**
```
tests/
├── conftest.py                    # Fixtures compartidas
├── fixtures/                     # Datos de prueba
│   ├── sample_documents/
│   ├── expected_outputs/
│   └── mock_responses/
├── unit/                         # Tests unitarios
│   ├── test_cognitive_models.py  # Models y validación
│   ├── test_cli.py              # Interfaz CLI
│   ├── test_concept_filtering.py # Filtrado de conceptos
│   ├── test_language_detection.py # Detección de idioma
│   ├── test_structure_formatter.py # Formateo de estructura
│   └── test_text_cleaning.py     # Utilidades de texto
└── integration/                  # Tests de integración
    ├── test_fast_first_pass.py   # Testing de modelo dual
    ├── test_multi_pass_features.py # Testing multi-pasada
    └── test_end_to_end.py         # Flujo completo
```

### Tipos de Tests

#### **Tests Unitarios**
```python
# test_cognitive_models.py
def test_cognitive_config_from_env():
    """Test configuration loading from environment variables."""
    
def test_document_section_immutability():
    """Test that DocumentSection is properly frozen."""
    
def test_concept_definition_validation():
    """Test ConceptDefinition validation rules."""

# test_structure_detector.py  
def test_hierarchy_detection():
    """Test detection of hierarchical document structure."""
    
def test_parent_child_relationships():
    """Test correct parent-child relationship building."""

# test_text_cleaning.py
def test_section_title_cleaning():
    """Test section title cleaning and normalization."""
```

#### **Tests de Integración**
```python
# test_multi_pass_features.py
@pytest.mark.asyncio
async def test_dual_pass_processing():
    """Test complete dual-pass processing workflow."""
    
@pytest.mark.asyncio 
async def test_enriched_context_integration():
    """Test that second pass uses enriched context correctly."""

# test_fast_first_pass.py
@pytest.mark.asyncio
async def test_model_selection_per_pass():
    """Test that correct models are used for each pass."""
```

#### **Tests End-to-End**
```python
# test_end_to_end.py
@pytest.mark.asyncio
async def test_complete_document_processing():
    """Test complete processing from file to CognitiveKnowledge."""
    
@pytest.mark.asyncio
async def test_authority_principle_preservation():
    """Test that text authority principle is maintained throughout."""
```

### Estrategias de Mocking

#### **Mock de LLM Responses**
```python
# conftest.py
@pytest.fixture
def mock_llm_responses():
    return {
        "section_summary": SectionSummaryResponse(
            summary="Mock section summary",
            key_concepts=["concept1", "concept2"]
        ),
        "concept_definition": ConceptDefinitionResponse(
            definition="Mock concept definition"
        )
    }

@pytest.fixture
def mock_llm_client(mock_llm_responses):
    """Mock LLM client that returns predefined responses."""
    with patch('cognitive_reader.llm.client.LLMClient') as mock:
        mock_instance = mock.return_value.__aenter__.return_value
        mock_instance.generate_structured_summary.return_value = mock_llm_responses["section_summary"]
        yield mock_instance
```

#### **Mock de Document Parser**
```python
@pytest.fixture
def mock_docling_parser():
    """Mock docling parser with sample document structure."""
    with patch('cognitive_reader.parsers.docling_parser.DoclingParser') as mock:
        mock_instance = mock.return_value
        mock_instance.parse_document.return_value = (
            "Sample Document",
            [
                DocumentSection(
                    id="section_1",
                    title="Introduction", 
                    content="This is the introduction content.",
                    level=1,
                    order_index=0
                )
            ]
        )
        yield mock_instance
```

### Fixtures de Testing

#### **Documentos de Prueba**
```python
# conftest.py
@pytest.fixture
def sample_markdown_document():
    """
    Fictional sample document designed for cognitive reading evaluation.
    
    Note: 'Aethelgard's Crystalline Consciousness Theory' is completely fictional,
    created specifically to test:
    - Novel semantic content processing (not in LLM training data)
    - Concept redefinition handling (e.g., empathy redefined as physical resonance)
    - Structural hierarchy processing (parents with/without content)
    - Title cleaning and normalization
    """
    return """# Aethelgard's Crystalline Consciousness Theory

## Fundamental Principles
The crystalline consciousness theory, proposed by xenophysicist Elara Aethelgard...

### Background
Historical context and previous work.

## Methodology  
Description of approach used.

## Results
Key findings and analysis.

## Conclusion
Summary and implications."""

@pytest.fixture  
def sample_document_sections():
    """Sample DocumentSection objects for testing."""
    return [
        DocumentSection(
            id="root",
            title="Aethelgard's Crystalline Consciousness Theory",
            content="# Aethelgard's Crystalline Consciousness Theory",
            level=0,
            order_index=0
        ),
        DocumentSection(
            id="principles",
            title="Fundamental Principles", 
            content="The crystalline consciousness theory, proposed by xenophysicist Elara Aethelgard...",
            level=1,
            parent_id="root",
            order_index=1
        )
        # ... más secciones
    ]
```

#### **Configuraciones de Testing**
```python
@pytest.fixture
def test_config():
    """Basic test configuration with development features."""
    return CognitiveConfig(
        dry_run=True,
        mock_responses=True,
        save_partial_results=False,
        max_sections=5,
        target_summary_words=100,
        max_glossary_concepts=10
    )

@pytest.fixture
def production_config():
    """Production-like configuration for integration tests."""
    return CognitiveConfig(
        fast_pass_model="llama3.1:8b",
        main_model="qwen3:8b", 
        num_passes=2,
        dry_run=False,  # Para tests de integración real
        target_summary_words=250
    )
```

### Métricas de Calidad

#### **Cobertura de Código**
- **Objetivo**: 90% cobertura mínima
- **Herramienta**: pytest-cov
- **Comando**: `pytest --cov=cognitive_reader --cov-report=html`

#### **Testing de Características Críticas**
- **Principio de autoridad**: Verificar que texto fuente prevalece sobre contexto
- **Contexto acumulativo**: Validar construcción correcta de contexto
- **Algoritmo secuencial**: Confirmar orden correcto de procesamiento
- **Modelo dual**: Verificar selección correcta de modelo por pasada

#### **Testing de Casos Edge**
- **Documentos vacíos**: Manejo de documentos sin contenido
- **Estructura malformada**: Documentos con jerarquía inconsistente
- **Contenido muy largo**: Documentos que excedan límites de contexto
- **Errores de LLM**: Fallos y timeouts de modelos LLM

#### **Performance Testing**
```python
@pytest.mark.performance
def test_processing_time_limits():
    """Test that processing completes within acceptable time limits."""
    
@pytest.mark.performance
def test_memory_usage_bounds():
    """Test that memory usage stays within expected bounds."""
```

---

## 📋 Checklist de Implementación

### Fase 1: Fundamentos y Configuración

#### **Setup de Proyecto**
- [ ] Configurar estructura de proyecto con src/ layout
- [ ] Configurar pyproject.toml con dependencias correctas
- [ ] Implementar _version.py con versionado automático
- [ ] Configurar herramientas de desarrollo (ruff, mypy, pytest)
- [ ] Implementar gestión de .env con python-dotenv

#### **Modelos de Datos**
- [ ] Implementar LanguageCode enum
- [ ] Crear DocumentSection como dataclass inmutable
- [ ] Implementar SectionSummary con Pydantic
- [ ] Crear ConceptDefinition para glosario
- [ ] Implementar CognitiveKnowledge como output final
- [ ] Implementar CognitiveConfig con from_env()

#### **Sistema de Configuración**
- [ ] Mapeo completo de variables de entorno
- [ ] Validación con Pydantic v2
- [ ] Métodos auxiliares (get_model_for_pass, get_temperature_for_pass)
- [ ] Soporte para .env file loading

### Fase 2: Parsing y Estructura

#### **Parser Universal**
- [ ] Implementar DoclingParser para todos los formatos
- [ ] Soporte para PDF, DOCX, HTML, Markdown
- [ ] Detección automática de formato por extensión
- [ ] Integración con StructureDetector

#### **Detección de Estructura**
- [ ] Algoritmo de detección de jerarquía
- [ ] Construcción de relaciones padre-hijo
- [ ] Asignación de order_index secuencial
- [ ] Identificación de secciones con/sin contenido

#### **Utilidades de Texto**
- [ ] Implementar text_cleaning.py
- [ ] Implementar structure_formatter.py
- [ ] Implementar language.py con langdetect
- [ ] Implementar tokens.py para gestión de contexto

### Fase 3: Cliente LLM y Prompts

#### **Cliente LLM Abstracto**
- [ ] Integración con LangChain
- [ ] Soporte para modelos Ollama
- [ ] Respuestas estructuradas con Pydantic
- [ ] Manejo de errores y reintentos
- [ ] Context manager para gestión de recursos

#### **Gestión de Prompts**
- [ ] Implementar PromptManager con versionado
- [ ] Templates para resúmenes de sección
- [ ] Templates para resúmenes de documento
- [ ] Templates para definiciones de conceptos
- [ ] Prompts con principio de autoridad
- [ ] Soporte multi-idioma (EN/ES)

#### **Modos de Desarrollo**
- [ ] Implementar dry-run mode
- [ ] Implementar mock responses
- [ ] Implementar show_context_usage
- [ ] Validación de configuración

### Fase 4: Motor de Lectura Cognitiva

#### **Algoritmo Secuencial**
- [ ] Implementar _order_by_document_sequence()
- [ ] Implementar _build_cumulative_context()
- [ ] Implementar _get_parent_contexts()
- [ ] Implementar _get_previous_sibling_contexts()
- [ ] Implementar _process_section_with_authority()

#### **Procesamiento Multi-pasada**
- [ ] Implementar _multi_pass_processing()
- [ ] Implementar _sequential_processing_with_enriched_context()
- [ ] Implementar _build_enriched_cumulative_context()
- [ ] Implementar _process_section_with_enriched_authority()
- [ ] Implementar _save_intermediate_pass()

#### **Manejo de Secciones Especiales**
- [ ] Implementar _update_parent_levels_incrementally()
- [ ] Implementar _process_pending_parents()
- [ ] Implementar _synthesize_parent_from_children()
- [ ] Implementar _finalize_pending_parents()

#### **Características de Desarrollo**
- [ ] Implementar _apply_section_filters()
- [ ] Implementar _filter_by_depth()
- [ ] Implementar _save_partial_result()
- [ ] Implementar filtros max_sections

### Fase 5: Synthesizer y Generación de Conocimiento

#### **Síntesis Jerárquica**
- [ ] Implementar synthesize_document()
- [ ] Implementar _generate_document_summary()
- [ ] Implementar _synthesize_container_sections()

#### **Generación de Glosario**
- [ ] Implementar _generate_concept_definitions()
- [ ] Implementar _filter_concepts_for_glossary()
- [ ] Implementar scoring algoritm para conceptos
- [ ] Soporte para skip_glossary

#### **Output Final**
- [ ] Construcción de CognitiveKnowledge
- [ ] Generación de hierarchy_index
- [ ] Generación de parent_child_map
- [ ] Cálculo de estadísticas

### Fase 6: CLI y Interfaces

#### **Comando Principal**
- [ ] Implementar cli() con click
- [ ] Manejo de argumentos y opciones completas
- [ ] Validación de entrada y paths
- [ ] Manejo de errores user-friendly

#### **Modos de Operación**
- [ ] Implementar --structure-only
- [ ] Implementar --validate-config
- [ ] Implementar --fast-mode
- [ ] Implementar todas las opciones de desarrollo

#### **Formatos de Salida**
- [ ] Implementar output JSON completo
- [ ] Implementar output Markdown con formato
- [ ] Implementar --output-file
- [ ] Soporte para --verbose y --quiet

### Fase 7: Testing y Calidad

#### **Setup de Testing**
- [ ] Configurar pytest con asyncio
- [ ] Implementar conftest.py con fixtures
- [ ] Crear documentos de prueba
- [ ] Configurar pytest.ini_options

#### **Tests Unitarios**
- [ ] Tests de modelos de datos
- [ ] Tests de configuración
- [ ] Tests de utilidades
- [ ] Tests de parsers
- [ ] Tests de prompts

#### **Tests de Integración**
- [ ] Tests de flujo completo
- [ ] Tests de modelo dual
- [ ] Tests de multi-pasada
- [ ] Tests de principio de autoridad

#### **Mocking y Fixtures**
- [ ] Mock de LLM responses
- [ ] Mock de docling parser
- [ ] Fixtures de configuración
- [ ] Fixtures de documentos de prueba

### Fase 8: Documentación y Packaging

#### **Documentación**
- [ ] README.md completo con ejemplos
- [ ] Documentación de API
- [ ] Guías de configuración
- [ ] Ejemplos de uso

#### **Packaging**
- [ ] Configuración de build con hatchling
- [ ] Entry points para CLI
- [ ] Versionado automático con hatch-vcs
- [ ] Configuración de distribución

#### **Scripts y Herramientas**
- [ ] Scripts de desarrollo
- [ ] Configuración de CI/CD
- [ ] Herramientas de análisis de código

---

## 🎯 Consideraciones de Implementación

### Principios de Diseño Técnico

#### **Principio de Autoridad del Texto Fuente**
- **CRÍTICO**: Implementar en todos los prompts la jerarquía: Texto Original > Contexto Actual > Contexto Previo
- **Validación**: Tests específicos que verifiquen que el texto fuente prevalece sobre información contextual conflictiva
- **Prompts**: Estructurar todos los prompts con instrucciones explícitas sobre autoridad

#### **Algoritmo Secuencial Auténtico**
- **CRÍTICO**: Procesar secciones en order_index (orden del documento), NO por nivel jerárquico
- **Contexto Acumulativo**: Construir contexto de padres + hermanos previos para cada sección
- **Actualizaciones Incrementales**: Los niveles superiores evolucionan conforme se procesan hijos

#### **Inmutabilidad de Estructuras Básicas**
- **DocumentSection**: Frozen dataclass para prevenir modificaciones accidentales
- **Configuración**: Pydantic models para validación automática
- **Thread Safety**: Estructuras inmutables facilitan procesamiento concurrente

### Optimizaciones de Rendimiento

#### **Gestión de Memoria**
- **Streaming**: Procesar documentos grandes por secciones sin cargar todo en memoria
- **Context Truncation**: Truncado inteligente de contexto cuando excede límites del modelo
- **Garbage Collection**: Liberar referencias a secciones procesadas cuando sea posible

#### **Paralelización**
- **Concurrent Processing**: Posibilidad de procesar múltiples documentos concurrentemente
- **Async I/O**: Todas las operaciones LLM deben ser asíncronas
- **Batching**: Agrupar requests LLM similares cuando sea posible

#### **Caching Inteligente**
- **Context Reuse**: Reutilizar contexto construido entre pasadas cuando sea apropiado
- **Model Warming**: Mantener modelos LLM "warm" para requests subsecuentes
- **Response Caching**: Cache opcional para respuestas LLM idénticas (desarrollo)

### Manejo de Errores y Robustez

#### **Estrategia de Fallback**
- **Model Fallback**: Si fast_model falla, usar main_model como backup
- **Format Fallback**: Si un formato específico falla, intentar procesamiento como texto plano
- **Partial Processing**: Continuar procesamiento aún con secciones que fallan

#### **Recuperación de Estado**
- **Checkpointing**: Guardar estado entre pasadas para recuperación
- **Incremental Processing**: Posibilidad de continuar desde última sección exitosa
- **Error Context**: Logging detallado de contexto cuando ocurren errores

#### **Validación Exhaustiva**
- **Input Validation**: Validar documentos antes del procesamiento
- **Output Validation**: Verificar integridad de CognitiveKnowledge antes de retornar
- **Configuration Validation**: Verificación temprana de configuración

### Extensibilidad y Evolución

#### **Arquitectura Pluggable**
- **LLM Providers**: Interfaz abstracta para añadir nuevos proveedores (OpenAI, Anthropic)
- **Document Parsers**: Sistema de plugins para nuevos formatos
- **Prompt Templates**: Sistema de templates extensible con versionado

#### **Backward Compatibility**
- **API Versioning**: Mantener compatibilidad de API pública
- **Configuration Migration**: Migración automática de configuraciones obsoletas
- **Schema Evolution**: Versionado de JSON output schema

#### **Multi-pass Extension**
- **N-pass Architecture**: Diseño preparado para más de 2 pasadas
- **Convergence Detection**: Detectar cuándo pasadas adicionales no aportan valor
- **Specialized Passes**: Framework para pasadas especializadas (fact-checking, etc.)

---

*Este documento de especificaciones técnicas v3.0 representa una ingeniería inversa completa del proyecto Cognitive Document Reader implementado, proporcionando todas las especificaciones técnicas necesarias para reimplementar el proyecto desde cero con la misma funcionalidad y arquitectura.*
