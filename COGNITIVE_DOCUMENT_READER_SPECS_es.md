# Cognitive Document Reader - Especificaciones Técnicas

## 🧠 Propósito y Visión

**Cognitive Document Reader** es una biblioteca de Python que simula la lectura de documentos similar a la humana a través de comprensión progresiva y síntesis jerárquica. El proyecto aborda dos casos de uso principales:

### 🎯 **Usos Principales**
1. **Resúmenes de Alta Calidad para Lectura/Estudio Humano**
   - Resúmenes estructurados que preservan el flujo narrativo
   - Mapas conceptuales para mejor comprensión
   - Rutas de aprendizaje progresivo a través de documentos complejos

2. **Metadatos Enriquecidos para Proyectos de IA**
   - Datos de entrenamiento mejorados para fine-tuning de LLM
   - Información rica en contexto para sistemas RAG
   - Conocimiento estructurado de documentos para flujos de trabajo de IA

### 🏗️ **Principios de Diseño**
- **Lectura Similar a la Humana**: Acumulación progresiva de conocimiento imitando la cognición humana
- **Comprensión Jerárquica**: Comprensión de documentos en múltiples niveles (documento → secciones → conceptos)
- **Minimizar Llamadas LLM**: Estrategias eficientes de agrupación, caché y reutilización de contexto
- **Configurabilidad**: Todas las configuraciones vía variables de entorno, sin valores hardcodeados
- **Testabilidad**: Pruebas exhaustivas con mocks y fixtures
- **Simplicidad**: MVP enfocado en funcionalidad esencial sin excesos

---

## 🏗️ Estándares de Desarrollo

### Calidad del Código
- **Anotaciones de Tipo Obligatorias**: Todas las funciones, métodos y miembros de clase DEBEN tener anotaciones de tipo usando los tipos más específicos posibles
- **Docstrings Completos**: Todas las funciones, métodos y clases DEBEN tener docstrings estilo Google explicando propósito, parámetros, valores de retorno y excepciones
- **Cobertura de Pruebas**: Objetivo mínimo del 90% de cobertura usando `pytest`
- **Manejo Robusto de Excepciones**: Usar tipos específicos de excepción, clases personalizadas cuando sea necesario, evitar cláusulas `except` genéricas

### Gestión de Prompts
- **Módulo Dedicado**: Los prompts LLM deben estar en módulos dedicados con versionado
- **Plantillas Reutilizables**: Prompts como plantillas parametrizables y testeables
- **Gestión de Contexto**: Manejo eficiente de contexto usando estructuras de datos apropiadas
- **Multi-idioma**: Prompts específicos por idioma con respaldos

### Rendimiento y Optimización
- **Minimizar Llamadas LLM**: Estrategias de agrupación, caché y reutilización de contexto
- **Programación Asíncrona**: Usar `async`/`await` para operaciones I/O bound
- **Estrategia de Caché**: Aplicar `functools.lru_cache` y `@cache` para evitar recálculos
- **Eficiencia de Memoria**: Liberación adecuada de recursos para prevenir memory leaks
- **Monitoreo de Recursos**: Monitorear uso de recursos e identificar cuellos de botella

### Arquitectura y Diseño
- **Responsabilidad Única**: Cada módulo/archivo con responsabilidad bien definida
- **Composición sobre Herencia**: Favorecer composición sobre herencia
- **Explícito sobre Implícito**: Código explícito que comunique claramente la intención
- **Diseño Modular**: Componentes reutilizables e independientes

### Seguridad
- **Validación de Entrada**: Validación robusta de entradas de usuario
- **Manejo de Datos Externos**: Manejo seguro de datos externos y documentos
- **Información de Error**: Mensajes de error informativos sin exponer información sensible

### Configuración y Entorno
- **Variables de Entorno**: Todo configurable vía variables de entorno (.env)
- **Sin Hard-coding**: Sin valores hardcodeados (modelos, temperaturas, etc.)
- **Modelos Pydantic**: Usar Pydantic para configuración y validación de datos
- **Configuración Flexible**: Soporte para .env tanto en modo standalone como módulo

### Idioma y Documentación
- **Código en Inglés**: Todos los comentarios, nombres de variables y documentación en inglés
- **Plantillas Multi-idioma**: Solo prompts/plantillas pueden estar en idiomas específicos
- **README en Inglés**: Documentación principal en inglés para audiencia internacional

### Estrategia de Dependencias
- **Dependencias Mínimas**: Solo dependencias esenciales en MVP
- **Pydantic**: Para validación de datos y configuración
- **Integración LangChain**: Considerar LangChain para gestión avanzada de prompts (Fase 2+)
- **Bases de Datos Vectoriales**: `faiss`/`chroma` para búsqueda semántica (Fase 3+)
- **Librerías de Rendimiento**: `psutil` para monitoreo de recursos

### Gestión de Código (MVP - Simplicidad)
- **Pre-commit Simple**: `ruff format`, `ruff check`, `mypy`, `pytest` antes del commit
- **Commits Convencionales**: Usar formato estándar (`feat:`, `fix:`, `docs:`, `refactor:`) desde el inicio
- **Versionado Dinámico**: Usando `hatchling` + `hatch-vcs` (sin bumping manual)
- **.gitignore Básico**: `__pycache__`, `.env`, `dist/`, `build/`, `.mypy_cache/`, `htmlcov/`

### Pruebas MVP
- **Pruebas Unitarias**: Cobertura básica de funcionalidad core usando pytest
- **Mock de Llamadas LLM**: Pruebas determinísticas sin llamadas reales a modelos
- **Fixtures Simples**: Setup/teardown básico para pruebas
- **Pruebas Rápidas**: Enfoque en velocidad para desarrollo ágil

### Desarrollo Amigable con Agentes de IA

#### Modos de Desarrollo sin Llamadas LLM
Para **vibe coding** y desarrollo con agentes de IA que necesitan probar sin costos:

```bash
# Variables de entorno para desarrollo
COGNITIVE_READER_DRY_RUN=true           # Sin llamadas LLM reales
COGNITIVE_READER_MOCK_RESPONSES=true    # Usar respuestas simuladas
COGNITIVE_READER_VALIDATE_CONFIG_ONLY=true  # Solo validar configuración

# Flags CLI para pruebas
cognitive-reader --dry-run document.md              # Simular procesamiento
cognitive-reader --validate-config                  # Solo verificar config
cognitive-reader --mock-llm-responses document.md   # Usar respuestas falsas
```

#### Casos de Uso Amigables con Agentes
```python
# Verificar configuración válida SIN llamadas LLM
from cognitive_reader import CognitiveReader, ReadingConfig

config = ReadingConfig.from_env()
reader = CognitiveReader(config)

# Solo verificar configuración - 0 llamadas LLM
is_valid = await reader.validate_configuration()  # ✅ Seguro para agentes

# Procesar con respuestas simuladas - 0 llamadas LLM  
result = await reader.read_document("doc.md", dry_run=True)  # ✅ Seguro para agentes

# Procesar REAL - COSTOSO, solo cuando sea necesario
result = await reader.read_document("doc.md")  # ⚠️ Hace llamadas LLM reales
```

#### Beneficios para Agentes de IA
- ✅ **Pruebas Sin Costo**: Los agentes pueden probar sin gastar dinero/recursos
- ✅ **Validación Rápida**: Verificar configuraciones instantáneamente  
- ✅ **Salidas Predecibles**: Respuestas simuladas determinísticas
- ✅ **Amigable con Desarrollo**: Iteración rápida sin esperas de LLM

#### Casos de Uso Específicos para Agentes

**🤖 Framework de Pruebas para Agentes:**
```python
# El agente puede verificar instalación y configuración SIN costo
async def test_cognitive_reader_setup():
    reader = CognitiveReader()
    
    # 1. Verificar dependencias instaladas
    is_available = reader.check_dependencies()  # ✅ Seguro
    
    # 2. Verificar configuración válida  
    config_valid = await reader.validate_config()  # ✅ Seguro
    
    # 3. Probar parsing básico con mock
    result = await reader.read_document("sample.md", dry_run=True)  # ✅ Seguro
    
    return all([is_available, config_valid, result.success])
```

**🔧 Bucle de Desarrollo de Agentes:**
```bash
# Desarrollo típico de agentes - SIN llamadas costosas:
export COGNITIVE_READER_DEV_MODE=true

# El agente puede iterar rápidamente:
cognitive-reader document.md  # Usa mocks, 0 costo
cognitive-reader --validate-config  # Solo verificación de config
cognitive-reader document.md --output json | jq .  # Probar parsing de salida
```

**⚠️ Cuándo NO usar estos modos:**
- Validación final de calidad de salida real
- Benchmarking de rendimiento con LLMs reales
- Evaluación de calidad final de resúmenes

### Documentación MVP
- **README Simple**: Ejemplos básicos de instalación y uso
- **Docstrings Esenciales**: Estilo Google para funciones públicas  
- **Ejemplos Mínimos**: 1-2 ejemplos de uso directo
- **Sin documentación prematura**: Enfoque en código funcionando primero

### Commits Convencionales desde el Día Uno

Usar formato estándar para commits desde **día uno**:

```bash
feat: add progressive reading functionality
fix: resolve memory leak in document parser
docs: update README with new CLI options
refactor: extract prompt management to separate module
test: add unit tests for hierarchical summarizer
chore: update dependencies and .gitignore

# Ejemplos con scope (opcional)
feat(reader): implement multi-pass refinement
fix(parser): handle empty sections gracefully
docs(api): add docstrings to public methods
```

**Beneficios inmediatos:**
- ✅ Historial de git más legible y profesional
- ✅ Identificación fácil del tipo de cambio
- ✅ Preparación para futura automatización (changelogs, releases)
- ✅ Estándar de industria sin overhead adicional

---

## 🚀 MVP (Fase 1) - Producto Mínimo Viable

### Alcance del MVP
El MVP implementa el ciclo básico de lectura cognitiva con funcionalidad esencial:

#### Características Incluidas
1. **Lectura Progresiva Secuencial**
   - Procesamiento en orden de aparición del documento
   - Resúmenes inmediatos por sección
   - Acumulación progresiva de contexto

2. **Síntesis Jerárquica**
   - Detección automática de estructura jerárquica
   - Síntesis de sección padre desde hijos
   - Resumen global del documento

3. **API Dual**
   - Uso como biblioteca de Python
   - CLI standalone con múltiples formatos de salida

4. **Formatos de Salida**
   - JSON estructurado (para integración con otros proyectos)
   - Markdown mejorado (para lectura humana)

5. **Soporte de Formatos**
   - Markdown (.md) vía docling

6. **Soporte de Idiomas**
   - Inglés y español (auto-detección)
   - Prompts en idioma original del documento

#### Excluido del MVP
- Refinamiento multi-pasada (Fase 2)
- Extracción de conceptos y glosarios (Fase 2)
- Soporte PDF/DOCX/HTML (Fase 2)
- Mapas avanzados de navegación y estructura (Fase 3)
- UI web o API REST (Fases futuras)
- Características colaborativas en tiempo real

### Estructura del Proyecto

```
cognitive-document-reader/
├── README.md                           # Documentación en inglés
├── README_es.md                        # Documentación en español  
├── LICENSE                             # Licencia MIT
├── pyproject.toml                      # Versionado dinámico + configuración uv
├── .env.example                        # Plantilla de configuración
├── .gitignore                          # Exclusiones básicas
├── 
├── src/
│   └── cognitive_reader/
│       ├── __init__.py                 # API pública
│       ├── _version.py                 # Versión auto-generada
│       ├── 
│       ├── core/
│       │   ├── __init__.py
│       │   ├── progressive_reader.py   # Motor principal de lectura
│       │   └── synthesizer.py          # Síntesis jerárquica
│       │
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── structure_detector.py   # Detección de estructura jerárquica
│       │   └── docling_parser.py       # Parser universal vía docling
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── client.py               # Abstracción LLM (enfoque Ollama)
│       │   └── prompts.py              # Gestión de prompts
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── config.py               # Modelos de configuración
│       │   ├── document.py             # Modelos de datos de documento
│       │   └── knowledge.py            # Estructuras de conocimiento
│       │
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── language.py             # Detección de idioma
│       │   └── resources.py            # Utilidades de gestión de recursos
│       │
│       └── cli/
│           ├── __init__.py
│           └── main.py                 # Interfaz CLI
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                     # Configuración de Pytest
│   ├── fixtures/                       # Datos de prueba
│   ├── unit/                           # Pruebas unitarias
│   └── integration/                    # Pruebas de integración
│
└── examples/
    ├── basic_usage.py                  # Ejemplos simples
    ├── library_integration.py          # Uso como biblioteca
    └── sample_documents/               # Documentos de prueba
```

### Uso Básico del CLI

```bash
# Instalar
pip install cognitive-document-reader

# Uso básico
cognitive-reader document.md

# Con opciones  
cognitive-reader document.md --output json --language es

# Modos de desarrollo
cognitive-reader document.md --dry-run  # Sin llamadas LLM
cognitive-reader --validate-config      # Solo verificación de config
```

### Uso como Biblioteca

```python
from cognitive_reader import CognitiveReader
from cognitive_reader.models import ReadingConfig

# Uso básico
config = ReadingConfig(
    model_name="llama3.1:8b",
    temperature=0.1,
    language="auto"
)

reader = CognitiveReader(config)
knowledge = await reader.read_document("document.md")

print(knowledge.document_summary)
for section in knowledge.sections:
    print(f"Section: {section.title}")
    print(f"Summary: {section.summary}")
```

### Modelos Pydantic

```python
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class LanguageCode(str, Enum):
    AUTO = "auto"
    EN = "en"
    ES = "es"

class DocumentSection(BaseModel):
    """Sección individual del documento con información de jerarquía"""
    model_config = ConfigDict(frozen=True)
    
    id: str
    title: str
    content: str
    level: int
    parent_id: Optional[str] = None
    children_ids: List[str] = Field(default_factory=list)
    order_index: int

class SectionSummary(BaseModel):
    """Resumen de una sección del documento"""
    section_id: str
    title: str
    summary: str
    key_concepts: List[str] = Field(default_factory=list)

class DocumentKnowledge(BaseModel):
    """Conocimiento completo extraído del documento"""
    document_title: str
    document_summary: str
    detected_language: LanguageCode
    sections: List[DocumentSection]
    section_summaries: Dict[str, SectionSummary]
    processing_metadata: Dict[str, Any]

class ReadingConfig(BaseModel):
    """Configuración simplificada de lectura para MVP - enfoque en esenciales"""
    # Configuración LLM (modelos probados)
    model_name: str = Field(default="llama3.1:8b")  # Probado mejor para seguimiento de instrucciones
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)  # Bajo para resúmenes consistentes
    
    # Procesamiento de Documentos (configuraciones esenciales)
    chunk_size: int = Field(default=1000, gt=100)  # Óptimo para lectura cognitiva
    chunk_overlap: int = Field(default=200, ge=0)  # ~20% overlap mantiene continuidad
    context_window: int = Field(default=4096, gt=0)  # Límite estándar que funciona
    
    # Configuraciones de Rendimiento (simplificadas)
    timeout_seconds: int = Field(default=120, gt=0)  # Timeout razonable
    max_retries: int = Field(default=3, ge=0)  # Conteo estándar de reintentos
    
    # Idioma y Salida
    document_language: LanguageCode = Field(default=LanguageCode.AUTO)
    
    # Modos de desarrollo (amigables con agentes IA)
    dry_run: bool = Field(default=False)  # Habilitar modo dry-run (sin llamadas LLM)
    mock_responses: bool = Field(default=False)  # Usar respuestas simuladas para pruebas
    
    @classmethod
    def from_env(cls) -> "ReadingConfig":
        """Crear config desde variables de entorno con respaldo a defaults"""
        import os
        return cls(
            model_name=os.getenv("COGNITIVE_READER_MODEL", "llama3.1:8b"),
            temperature=float(os.getenv("COGNITIVE_READER_TEMPERATURE", "0.1")),
            chunk_size=int(os.getenv("COGNITIVE_READER_CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("COGNITIVE_READER_CHUNK_OVERLAP", "200")),
            context_window=int(os.getenv("COGNITIVE_READER_CONTEXT_WINDOW", "4096")),
            timeout_seconds=int(os.getenv("COGNITIVE_READER_TIMEOUT_SECONDS", "120")),
            max_retries=int(os.getenv("COGNITIVE_READER_MAX_RETRIES", "3")),
            document_language=LanguageCode(os.getenv("COGNITIVE_READER_LANGUAGE", "auto")),
            dry_run=os.getenv("COGNITIVE_READER_DRY_RUN", "false").lower() == "true",
            mock_responses=os.getenv("COGNITIVE_READER_MOCK_RESPONSES", "false").lower() == "true",
        )
```

---

## 📈 Fases de Desarrollo Futuro

### Fase 2: Refinamiento y Conceptos

#### Nuevas Características
- **Refinamiento de Segunda Pasada**
  - Mejora de resúmenes con contexto global
  - Identificación de conexiones profundas
  - Corrección de inconsistencias

- **Extracción de Conceptos**
  - Glosario contextual automático
  - Referencias cruzadas
  - Definiciones en contexto dentro del documento

- **Formatos Adicionales**
  - PDF (vía docling)
  - DOCX (vía docling)
  - HTML (vía docling)

- **Salida Mejorada**
  - Documentos Markdown con resúmenes estructurados
  - Exportación de glosario
  - Metadatos enriquecidos para proyectos de IA
  - HTML

#### API Extendida
```python
# Refinamiento
refined_knowledge = await reader.refine_knowledge(knowledge)

# Extracción de conceptos
concepts = await reader.extract_concepts(knowledge)
print(concepts.glossary)  # Glosario de términos
print(concepts.references)  # Referencias por concepto
```

#### Configuración Avanzada (Fase 2+)

```python
class AdvancedReadingConfig(ReadingConfig):
    """Configuración extendida para características avanzadas - Fase 2+"""
    # Configuración LLM Adicional
    llm_provider: str = Field(default="ollama")
    validation_model: str = Field(default="deepseek-r1:8b")  # Superior para análisis
    
    # Procesamiento Avanzado de Documentos
    max_section_length: int = Field(default=2000, gt=0)  # Para contexto jerárquico
    
    # Configuraciones de Rendimiento (probadas en producción)
    enable_parallel_processing: bool = Field(default=True)
    max_parallel_tasks: int = Field(default=3, gt=0)  # Paralelismo sin saturación
    
    # Estrategia de Caché (Fase 3+ cuando se necesite)
    cache_enabled: bool = Field(default=True)
    cache_max_memory_mb: int = Field(default=100, gt=0)  # Límite razonable de memoria
    cache_expiry_hours: int = Field(default=24, gt=0)  # Expiración apropiada
    cache_strategy: str = Field(default="hybrid")  # Híbrido memoria + disco
    
    # Generación de Resúmenes (límites de tokens optimizados)
    document_summary_max_tokens: int = Field(default=400, gt=0)  # Para documento completo
    section_summary_max_tokens: int = Field(default=200, gt=0)  # Para secciones principales
    concept_summary_max_tokens: int = Field(default=150, gt=0)  # Para conceptos clave
    
    # Controles de Calidad (umbrales validados)
    min_confidence: float = Field(default=0.75, ge=0.0, le=1.0)  # Umbral de calidad probado
    min_coherence_score: float = Field(default=0.6, ge=0.0, le=1.0)  # Validación contextual
    max_concepts_per_document: int = Field(default=8, gt=0)  # Número óptimo de conceptos clave
    
    # Modos de desarrollo adicionales
    validate_config_only: bool = Field(default=False)  # Solo validar config, sin procesamiento
    dev_mode: bool = Field(default=False)  # Habilitar modo desarrollo con todos los mocks
```

#### Herramientas de Desarrollo Profesional (Fase 2)
- **CI/CD Completo**
  - GitHub Actions con matriz de pruebas (Python 3.12, 3.13)
  - Hooks automáticos de pre-commit
  - Dependabot para actualizaciones de seguridad
  - Automatización de releases a PyPI con tags

- **Flujo de Trabajo Git Avanzado**
  - Ramas de características y flujo de PR
  - Reglas de protección de ramas y requisitos de code review
  - Merge automático después de verificaciones de estado

- **Aseguramiento de Calidad**
  - Reporte automático de cobertura de código
  - Benchmarks de rendimiento en CI
  - Escaneo de vulnerabilidades de dependencias (safety)
  - Gates opcionales de calidad de código (SonarCloud/CodeClimate)

### Fase 3: Mapas y Navegación

#### Nuevas Características
- **Mapas Estructurales**
  - Mapa de navegación física
  - Red conceptual
  - Visualización de flujo de ideas

- **Navegación Inteligente**
  - Búsqueda semántica
  - Recomendaciones de lectura
  - Rutas de aprendizaje

#### API Extendida
```python
# Mapas estructurales
maps = await reader.create_structural_maps(knowledge)
physical_map = maps.physical_structure
conceptual_map = maps.conceptual_network

# Navegación
navigator = knowledge.create_navigator()
related_sections = navigator.find_related("concept")
learning_path = navigator.create_learning_path(["concept1", "concept2"])
```

### Fase 4: Multi-idioma y Optimización

#### Nuevas Características
- **Soporte Multi-idioma Completo**
  - Detección automática mejorada de idioma
  - Soporte para idiomas adicionales
  - Traducción de resúmenes a idiomas objetivo
  - Prompts optimizados por idioma

- **Métricas de Lectura**
  - Calidad del resumen
  - Coherencia narrativa
  - Completitud de extracción

- **Optimización Automática**
  - Ajuste de parámetros por documento e idioma
  - Detección de patrones óptimos
  - Mejora continua de prompts

### Fase 5: Integración y Exportación

#### Nuevas Características
- **Integración con Bases de Datos**
- **Exportación Avanzada**
  - Múltiples formatos (LaTeX, EPUB, etc.)
  - Plantillas personalizables
  - Metadatos enriquecidos para sistemas de IA

### Estrategias de Optimización LLM

#### Minimización de Llamadas
- **Agrupación Inteligente**: Agrupar secciones relacionadas en una sola llamada
- **Reutilización de Contexto**: Reutilizar contexto acumulado entre secciones consecutivas
- **Optimización de Plantillas**: Plantillas eficientes que generen resultados consistentes

#### Gestión de Ventana de Contexto
- **Chunking Inteligente**: División inteligente respetando límites de contexto (1000 chars probado)
- **Priorización de Contexto**: Priorizar contexto más relevante para cada sección
- **Contexto Jerárquico**: Usar jerarquía para optimizar uso de contexto (2000 chars max probado)
- **Estrategias de Respaldo**: Degradación elegante cuando se excede el contexto

#### Valores Probados y Optimizados
Basado en experiencia exitosa de `extract-to-train`, usando valores que han demostrado **excelente rendimiento en producción**:

**🤖 Modelos Optimizados:**
- **llama3.1:8b**: Probado mejor para seguimiento de instrucciones y generación de resúmenes
- **deepseek-r1:8b**: Superior para análisis y validación de calidad  
- **Temperatura 0.1**: Óptima para resúmenes consistentes y fieles

**📄 Procesamiento Eficiente:**
- **Tamaño de Chunk 1000**: Óptimo para lectura cognitiva - preserva mejor coherencia narrativa
- **Overlap 200**: ~20% overlap mantiene continuidad sin redundancia excesiva
- **Ventana de Contexto 4096**: Límite estándar que funciona confiablemente

**⚡ Rendimiento Validado:**
- **3 tareas paralelas**: Máximo paralelismo sin saturación del sistema
- **Timeout 120s**: Tiempo suficiente para operaciones complejas sin colgarse
- **3 reintentos**: Número óptimo para manejar fallos temporales

**💾 Gestión de Recursos (MVP):**
- **Enfoque simple**: Procesamiento directo sin caché complejo
- **Eficiencia de memoria**: Limpieza adecuada después del procesamiento
- **Mejora futura**: Estrategias de caché planificadas para Fase 3+

**🎯 Umbrales de Calidad:**
- **Confianza 0.75**: Umbral que asegura alta calidad sin ser demasiado restrictivo
- **Coherencia 0.6**: Límite para validación contextual balanceada
- **8 conceptos max**: Número óptimo de conceptos clave por documento

---

## 🏗️ Arquitectura Técnica Detallada

### Componentes Core

#### ProgressiveReader
- **Responsabilidad**: Motor principal de lectura con procesamiento progresivo secuencial
- **Métodos Clave**:
  - `read_document(file_path, config)`: Método principal de lectura
  - `_process_section(section, accumulated_context)`: Procesar sección individual
  - `_accumulate_context(section_summary, context)`: Construir contexto progresivo

#### StructureDetector  
- **Responsabilidad**: Detecta estructura jerárquica usando docling
- **Métodos Clave**:
  - `detect_structure(document)`: Extrae secciones jerárquicas
  - `_build_section_tree(elements)`: Construye árbol desde estructura plana
  - `_identify_section_types(sections)`: Clasifica secciones de contenido vs contenedor

#### Synthesizer
- **Responsabilidad**: Síntesis jerárquica desde el más profundo al más superficial
- **Métodos Clave**:
  - `synthesize_document(sections, summaries)`: Síntesis completa del documento
  - `_synthesize_container_section(section, child_summaries)`: Contenedor desde hijos
  - `_synthesize_content_section(section)`: Resumen de sección de contenido

#### LLMClient
- **Responsabilidad**: Abstracción simple de LLM (enfoque Ollama)
- **Métodos Clave**:
  - `generate_summary(content, context, prompt_type)`: Generar resúmenes
  - `_handle_retries(operation)`: Lógica básica de reintentos

#### PromptManager
- **Responsabilidad**: Gestión simple de prompts
- **Métodos Clave**:
  - `get_prompt(type, language)`: Prompts específicos por idioma
  - `format_prompt(section, context)`: Formateo básico de prompts

#### DoclingParser
- **Responsabilidad**: Parsing universal de documentos
- **Características**:
  - **Soporte MVP**: Markdown vía docling
  - **Soporte Futuro**: PDF, DOCX, HTML vía docling
  - **Detección de Estructura**: Extracción de estructura jerárquica
  - **Extracción de Contenido**: Texto limpio con preservación de metadatos

---

## 📦 Configuración del Proyecto

### Dependencias (pyproject.toml)

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "cognitive-document-reader"
dynamic = ["version"]  # Versionado automático desde git tags

# Versionado automático dinámico
[tool.hatch.version]
source = "vcs"
tag-regex = "^v(?P<version>\\d+\\.\\d+\\.\\d+)$"

[tool.hatch.build.hooks.vcs]
version-file = "src/cognitive_reader/_version.py"

[tool.uv]
python-version = "3.12"
index-strategy = "unsafe-best-match"

[project.scripts]
cognitive-reader = "cognitive_reader.cli.main:cli"

authors = [{name = "Juanje Ojeda", email = "juanje@redhat.com"}]
description = "Lectura avanzada de documentos con comprensión progresiva similar a la humana"
readme = "README.md"
license = {text = "MIT"}
keywords = ["llm", "document-processing", "cognitive-reading", "summarization"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers", 
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
requires-python = ">=3.12"

dependencies = [
    "pydantic>=2.0,<3.0",      # Validación de datos y configuraciones
    "aiohttp>=3.8,<4.0",       # Cliente HTTP asíncrono  
    "click>=8.0,<9.0",         # Framework CLI
    "docling>=2.40,<3.0",      # Parsing universal de documentos (estable actual: v2.43.0)
    "langdetect>=1.0,<2.0",    # Detección de idioma
    "python-dotenv>=1.0,<2.0", # Soporte de archivos .env
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0,<8.0",
    "pytest-asyncio>=0.21,<1.0",
    "ruff>=0.1,<1.0",          # Solo ruff para linting y formateo
    "mypy>=1.0,<2.0",
]
```

### Versionado Dinámico Simple

El proyecto usa **versionado automático** con tags de git (sin bumping manual):

```bash
# Para crear una nueva versión:
git tag v0.1.0         # Crea versión 0.1.0  
git tag v0.1.1         # Release de parche
git tag v0.2.0         # Release menor

# La versión se auto-genera desde el último tag de git
# No necesidad de editar archivos manualmente ✨
```

**Beneficios MVP:**
- ✅ Sin edición manual de versión en múltiples archivos  
- ✅ Versionado automático consistente
- ✅ Perfecto para proyectos personales
- ✅ Se integra perfectamente con uv y PyPI

### Gestión UV

```bash
# Instalar dependencias
uv sync

# Ejecutar pruebas
uv run pytest

# Ejecutar linting
uv run ruff check .
uv run ruff format .

# Verificación de tipos
uv run mypy src/

# Uso del CLI
uv run cognitive-reader document.md

# Construir paquete
uv build
```

### Variables de Entorno

```bash
# .env - Configuración Esencial MVP
COGNITIVE_READER_MODEL=llama3.1:8b          # Probado mejor para seguimiento de instrucciones
COGNITIVE_READER_TEMPERATURE=0.1             # Bajo para resúmenes consistentes
COGNITIVE_READER_LANGUAGE=auto

# Procesamiento de documentos (configuraciones esenciales)
COGNITIVE_READER_CHUNK_SIZE=1000            # Balance óptimo contexto/eficiencia
COGNITIVE_READER_CHUNK_OVERLAP=200          # ~20% overlap mantiene continuidad
COGNITIVE_READER_CONTEXT_WINDOW=4096        # Límite estándar que funciona bien

# Configuraciones de rendimiento (simplificadas)
COGNITIVE_READER_TIMEOUT_SECONDS=120        # Timeout razonable
COGNITIVE_READER_MAX_RETRIES=3              # Conteo estándar de reintentos

# Modos de desarrollo (amigables con agentes IA)
COGNITIVE_READER_DRY_RUN=false              # Habilitar modo dry-run (sin llamadas LLM)
COGNITIVE_READER_MOCK_RESPONSES=false       # Usar respuestas simuladas para pruebas
```

---

## 🧪 Plan de Pruebas

### Estándares de Pruebas (MVP)
- **Framework**: Pytest con funciones simples
- **Cobertura Objetivo**: 80% cobertura de código (realista para MVP)
- **Tipos de Pruebas**: Pruebas unitarias y de integración básicas
- **Aislamiento de Pruebas**: Fixtures simples para setup esencial

### Organización de Pruebas (MVP)

```python
# tests/conftest.py - Simplificado para MVP
import pytest
from cognitive_reader.models import ReadingConfig

@pytest.fixture
def test_config():
    """Configuración simple de prueba con mocks habilitados."""
    return ReadingConfig(
        model_name="test-model",
        dry_run=True,
        mock_responses=True
    )

@pytest.fixture  
def sample_markdown():
    """Markdown simple para pruebas."""
    return """
# Test Document

## Section 1
Content of section 1.

## Section 2  
Content of section 2.
    """
```

### Categorías de Pruebas

#### Pruebas Unitarias (MVP)
```python
# tests/test_reading.py - Pruebas simples MVP
import pytest
from cognitive_reader import CognitiveReader

def test_config_creation(test_config):
    """Probar creación de configuración."""
    assert test_config.model_name == "test-model"
    assert test_config.dry_run is True

async def test_basic_reading(test_config, sample_markdown):
    """Probar lectura básica de documento en modo dry-run."""
    reader = CognitiveReader(test_config)
    knowledge = await reader.read_document_text(sample_markdown)
    
    assert knowledge.document_title == "Test Document"
    assert len(knowledge.sections) >= 2
    assert knowledge.detected_language in ["en", "auto"]

def test_environment_config():
    """Probar configuración desde variables de entorno."""
    config = ReadingConfig.from_env()
    assert config.model_name == "llama3.1:8b"  # default
```

#### Pruebas de Integración (MVP)
```python
# tests/test_integration.py - Pruebas de integración esenciales
import pytest
import os

async def test_markdown_processing(test_config, tmp_path):
    """Probar procesamiento completo de archivo markdown."""
    # Crear archivo markdown temporal
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\n## Section\nContent here.")
    
    reader = CognitiveReader(test_config)
    knowledge = await reader.read_document(str(md_file))
    
    assert knowledge.document_title == "Test"
    assert len(knowledge.sections) >= 1

def test_env_config_loading(monkeypatch):
    """Probar carga de configuración desde variables de entorno."""
    monkeypatch.setenv("COGNITIVE_READER_MODEL", "custom-model")
    monkeypatch.setenv("COGNITIVE_READER_TEMPERATURE", "0.5")
    
    config = ReadingConfig.from_env()
    assert config.model_name == "custom-model"
    assert config.temperature == 0.5
```

#### Pruebas de Rendimiento (Básicas)
```python
# tests/test_performance.py - Validación básica de rendimiento
import pytest
import time

@pytest.mark.performance
async def test_reasonable_processing_time(test_config, sample_markdown):
    """Probar que el procesamiento se complete en tiempo razonable."""
    reader = CognitiveReader(test_config)
    
    start_time = time.time()
    await reader.read_document_text(sample_markdown)
    processing_time = time.time() - start_time
    
    # En modo dry-run, debería ser muy rápido
    assert processing_time < 5.0  # segundos
```

---

## 📋 Hoja de Ruta de Desarrollo

### Hitos

#### Hito 1: Base MVP
- [ ] Estructura básica del proyecto con uv
- [ ] Modelos Pydantic para configuración y datos
- [ ] Parser universal con docling
- [ ] Lector progresivo simple
- [ ] Interfaz CLI básica
- [ ] Pruebas esenciales con mocks

#### Hito 2: Funcionalidad Core
- [ ] Detección de estructura jerárquica
- [ ] Lectura progresiva secuencial
- [ ] Síntesis jerárquica
- [ ] Soporte multi-idioma (EN/ES)
- [ ] Configuración completa de entorno
- [ ] Modos de desarrollo amigables con agentes

#### Hito 3: Características de Fase 2
- [ ] Refinamiento de segunda pasada
- [ ] Extracción de conceptos y glosarios
- [ ] Soporte completo PDF/DOCX vía docling
- [ ] Pipeline profesional CI/CD
- [ ] Optimizaciones de rendimiento

#### Hito 4: Características de Fase 3
- [ ] Mapas estructurales y conceptuales
- [ ] Navegación inteligente
- [ ] Formatos de exportación avanzados
- [ ] APIs de integración

---

## 📈 Métricas de Éxito

### Métricas Técnicas (MVP)
- **Cobertura de Pruebas**: >80%
- **Rendimiento**: <30s para documentos de 50 páginas
- **Uso de Memoria**: <50MB memoria de procesamiento (sin caché)
- **Tiempo de Respuesta API**: <200ms para operaciones básicas
- **Eficiencia LLM**: Minimización razonable de llamadas
- **Confiabilidad**: Manejo básico de errores y lógica de reintentos

### Métricas de Adopción
- **Descargas PyPI**: >1000/mes en 6 meses
- **Estrellas GitHub**: >100 en 1 año
- **Issues/PRs**: Actividad consistente de la comunidad

### Métricas de Calidad
- **Documentación**: Docs completos de API + ejemplos
- **Experiencia de Usuario**: Mensajes de error claros y advertencias útiles
- **Confiabilidad**: <1% tasa de fallo en procesamiento de documentos

---

## 🤖 Disclaimer de Herramientas de IA

Este proyecto fue desarrollado con la asistencia de herramientas de inteligencia artificial:

**Herramientas utilizadas:**
- **Cursor**: Editor de código con capacidades de IA
- **Claude-4-Sonnet**: Modelo de lenguaje de Anthropic

**División de responsabilidades:**

**IA (Cursor + Claude-4-Sonnet)**:
- 🔧 Prototipado inicial de código
- 📝 Generación de ejemplos y casos de prueba
- 🐛 Asistencia en debugging y resolución de errores
- 📚 Escritura de documentación y comentarios
- 💡 Sugerencias de implementación técnica

**Humano (Juanje Ojeda)**:
- 🎯 Especificación de objetivos y requisitos
- 🔍 Revisión crítica de código y documentación
- 💬 Retroalimentación iterativa y refinamiento de soluciones
- 📋 Definición de estructura educativa del proyecto
- ✅ Validación final de conceptos y enfoques

**Filosofía de colaboración**: Las herramientas de IA sirvieron como un asistente técnico altamente capaz, mientras que todas las decisiones de diseño, objetivos educativos y direcciones del proyecto fueron definidas y validadas por el humano.

---

## 📜 Licencia

Licencia MIT - Ver archivo LICENSE para detalles

---

*Esta especificación proporciona una hoja de ruta completa para implementar un lector cognitivo de documentos de grado profesional con capacidades de comprensión similar a la humana.*
