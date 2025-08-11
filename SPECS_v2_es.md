# Cognitive Document Reader - Especificaciones Técnicas v2.0

> **Versión 2.0**: Rediseño arquitectónico basado en el proceso auténtico de lectura cognitiva humana detallado en `MOTIVATION_es.md`

---

## 📚 Contexto: ¿Por Qué la Versión 2.0?

**La Versión 2.0** representa un cambio arquitectónico fundamental del enfoque de procesamiento secuencial original (v1.x) para implementar el auténtico **proceso de lectura cognitiva de dos pasadas** descrito en detalle en [`MOTIVATION_es.md`](./MOTIVATION_es.md).

### **El Problema con la v1.x**
La especificación original (preservada en el git tag `v0.1.1`) implementaba solo:
- ✅ Lectura progresiva secuencial  
- ✅ Síntesis jerárquica básica
- ❌ **Faltaba**: Refinamiento continuo durante la lectura
- ❌ **Faltaba**: Enriquecimiento contextual de segunda pasada  
- ❌ **Faltaba**: Comprensión evolutiva

### **La Brecha Cognitiva**
Como se detalla en `MOTIVATION_es.md`, la lectura humana de documentos complejos involucra:
1. **Primera pasada**: Lectura progresiva + **refinamiento continuo** de la comprensión
2. **Segunda pasada**: Re-lectura con **contexto global** para enriquecer la comprensión

Este proceso es **esencial** para el objetivo central del proyecto: generar datasets de alta calidad para el libro "3 pasos contra el sedentarismo" que preserven la voz y metodología del autor.

### **Solución v2.0**
Implementar lo **absolutamente mínimo** para demostrar lectura cognitiva vs. chunks fragmentados:
- ✅ Lectura de dos pasadas (progresiva + enriquecimiento simple)
- ✅ Refinamiento básico de resúmenes cuando la comprensión cambia significativamente
- ✅ Contexto acumulado en lugar de chunks aislados
- ✅ Enriquecimiento simple de segunda pasada con contexto global

**Todo lo demás** (detección de emergencia, seguimiento complejo de refinamiento, grafos de conocimiento) permanece en fases futuras.

---

## 🧠 Propósito y Visión

**Cognitive Document Reader v2** es una librería Python que simula auténticamente la lectura de documentos similar a la humana a través de **procesamiento cognitivo de dos pasadas** con **comprensión evolutiva**. Esta versión implementa completamente el enfoque de lectura cognitiva detallado en `MOTIVATION_es.md`.

---

## 🛠️ Stack Tecnológico y Estándares de Desarrollo

### **Stack Tecnológico Principal**

**Lenguaje y Runtime:**
- **Python 3.12+**: Características modernas de Python con excelente soporte de tipos
- **Async/Await**: Preferir programación asíncrona para operaciones limitadas por I/O

**Herramientas de Desarrollo:**
- **uv**: Gestión de dependencias y configuración de proyecto (reemplaza Poetry, pip, venv)
- **ruff**: Linting y formateo de código (reemplaza black, isort, flake8)
- **mypy**: Verificación estática de tipos con configuración estricta
- **pytest**: Framework de testing con soporte asíncrono

**Librerías de Dominio:**
- **pydantic v2+**: Validación de datos y gestión de configuración
- **docling**: Parseado universal de documentos (estable actual: v2.43.0+)
- **aiohttp**: Cliente HTTP asíncrono para comunicaciones LLM
- **click**: Framework de interfaz de línea de comandos
- **langdetect**: Capacidades de detección de idioma

### **Estándares de Calidad de Código (Obligatorios)**

**Seguridad de Tipos:**
- **TODAS** las funciones, métodos y miembros de clase DEBEN tener anotaciones de tipo
- Usar `from __future__ import annotations` para referencias futuras
- Preferir tipos específicos sobre genéricos (`List[str]` sobre `List[Any]`)

**Documentación:**
- **TODAS** las funciones, métodos y clases públicas DEBEN tener docstrings estilo Google
- Incluir propósito, parámetros, valores de retorno, excepciones y ejemplos de uso
- Comentarios de código solo en inglés

**Manejo de Excepciones:**
- Usar tipos específicos de excepción, nunca `except:` desnudo
- Crear clases de excepción personalizadas para errores específicos del dominio
- Proporcionar mensajes de error informativos sin exponer datos sensibles

### **Principios de Arquitectura y Diseño**

**Patrones de Diseño:**
- **Responsabilidad Única**: Cada módulo/clase tiene una responsabilidad clara
- **Composición sobre Herencia**: Favorecer composición e inyección de dependencias
- **Explícito sobre Implícito**: Evitar valores mágicos, ser explícito sobre dependencias
- **Async-First**: Diseñar APIs para ser compatibles con async desde el inicio

**Gestión de Configuración:**
- **Dirigido por ambiente**: Toda configuración vía variables de entorno
- **Validación Pydantic**: Usar modelos Pydantic para validación de configuración
- **Amigable para desarrollo**: Incluir modos dry-run y respuestas mock
- **Sin valores hardcodeados**: Todo configurable

**Filosofía de Testing:**
- **90% cobertura mínima**: Enfocarse en rutas críticas y manejo de errores
- **Mock de dependencias externas**: Llamadas LLM, I/O de archivos, requests de red
- **Rápido y determinista**: Tests deben ejecutarse rápidamente y consistentemente
- **Probar escenarios de éxito y fallo**

### **Estándares de Estructura de Proyecto**

**Organización de Directorios:**
```
cognitive-document-reader/
├── src/cognitive_reader/         # Paquete principal de código fuente
│   ├── __init__.py               # Exportaciones API pública
│   ├── models/                   # Modelos de datos Pydantic
│   ├── core/                     # Lógica principal de lectura cognitiva  
│   ├── parsers/                  # Componentes de parseado de documentos
│   ├── llm/                      # Integración LLM
│   ├── utils/                    # Funciones utilitarias
│   └── cli/                      # Interfaz de línea de comandos
├── tests/                        # Suite de tests
│   ├── unit/                     # Tests unitarios
│   ├── integration/              # Tests de integración
│   └── fixtures/                 # Datos de prueba y fixtures
├── examples/                     # Ejemplos de uso y demos
├── pyproject.toml                # Configuración de proyecto (formato uv)
├── README.md                     # Documentación en inglés
└── .env.example                  # Plantilla de configuración de entorno
```

**Convenciones de Nomenclatura de Archivos:**
- **Snake_case**: Todos los archivos y directorios Python
- **Propósito claro**: Los nombres de archivos deben indicar funcionalidad
- **Sin abreviaciones**: Preferir `progressive_reader.py` sobre `prog_reader.py`
- **Test espejo**: Archivos de test reflejan estructura fuente (`test_progressive_reader.py`)

**Responsabilidades de Módulos:**
- **models/**: Solo modelos Pydantic y estructuras de datos
- **core/**: Lógica de negocio y algoritmos de procesamiento cognitivo  
- **parsers/**: Manejo de formatos de documento y detección de estructura
- **llm/**: Comunicación LLM y gestión de prompts
- **utils/**: Funciones puras sin dependencias externas
- **cli/**: Interfaz de línea de comandos e interacción del usuario

---

## 🎯 Casos de Uso Principales

### **1. Resúmenes de Alta Calidad para Lectura/Estudio Humano**
   - Resúmenes que evolucionan durante el proceso de lectura  
   - Mapas contextuales mostrando desarrollo del conocimiento
   - Rutas de aprendizaje progresivo a través de documentos complejos

### **2. Generación de Dataset para Fine-tuning**
   - **Construcción de contexto jerárquico**: Resúmenes Libro → Capítulo → Sección para entrenamiento coherente
   - **Terminología consistente**: Definiciones de conceptos refinadas cognitivamente para precisión del dominio
   - **Ejemplos de entrenamiento ricos**: Usar jerarquía de resúmenes para generar pares Q&A contextualmente coherentes

### 🧠 **Innovación Principal: Procesamiento Cognitivo de Dos Pasadas**

A diferencia de los procesadores de documentos tradicionales que fragmentan contenido, **Cognitive Document Reader v2** implementa el proceso completo de lectura humana:

#### 🔄 **Primera Pasada: Construcción Progresiva + Refinamiento Continuo**
1. **Lectura progresiva secuencial** con acumulación de contexto
2. **Resúmenes evolutivos** que se actualizan cuando se encuentra nueva información
3. **Refinamiento jerárquico** donde subsecciones actualizan secciones padre
4. **Detección de conceptos emergentes** cuando las ideas se vuelven claras con contexto
5. **Procesamiento rápido** usando modelo veloz para simular "primera lectura rápida" humana

#### 🔍 **Segunda Pasada: Enriquecimiento Contextual**
1. **Re-lectura informada** con comprensión completa del documento
2. **Identificación de conexiones profundas** entre conceptos previamente separados
3. **Mejora de relaciones** que solo se vuelve visible con contexto completo
4. **Síntesis final** integrando todo el conocimiento coherentemente
5. **Procesamiento de calidad** usando modelo cuidadoso para simular "análisis reflexivo" humano

### 🧠 **Estrategia de Modelo Dual: Simulando Patrones de Lectura Humana**

La lectura humana naturalmente involucra dos enfoques cognitivos diferentes:
- **Escaneo rápido**: Vista general rápida para captar la idea general (primera pasada)
- **Análisis cuidadoso**: Comprensión detallada con contexto completo (segunda pasada)

La **configuración de modelo dual** refleja esto:
- **Modelo rápido (primera pasada)**: Optimizado para velocidad, comprensión básica, detección rápida de refinamiento
- **Modelo de calidad (segunda pasada)**: Optimizado para profundidad, comprensión matizada, enriquecimiento sofisticado

Este enfoque **mejora tanto el rendimiento como la precisión** al ajustar los recursos computacionales a los requisitos cognitivos.

---

## 🏗️ Principios de Diseño v2

- **Simulación Cognitiva Auténtica**: Proceso verdadero de lectura de dos pasadas imitando cognición humana
- **Comprensión Evolutiva**: Conocimiento que cambia y mejora durante el procesamiento
- **Refinamiento Jerárquico**: Actualización continua desde subsecciones hasta comprensión global
- **Inteligencia Emergente**: Conceptos y relaciones que aparecen con contexto acumulado
- **Trazabilidad de Refinamiento**: Historial completo de cómo evolucionó la comprensión
- **Minimizar Llamadas LLM**: Batching inteligente y reutilización de contexto a través de ambas pasadas
- **Preservación de Calidad**: Mantener fidelidad a la voz y metodología del autor original

---

## 🚀 MVP v2.0 - Lectura Cognitiva Mínima

### **Objetivo Principal**: Demostrar lectura cognitiva vs. chunks fragmentados con complejidad mínima

**Objetivo MVP**: Lectura cognitiva de dos pasadas **mínima** para probar el concepto con implementación limpia y enfocada

### ✅ **Características Principales MVP v2** (Mínimo Absoluto)

#### 1. **Lectura de Dos Pasadas** (Esencial)
   - **Primera Pasada**: Lectura progresiva con contexto acumulado (como primera lectura humana)
   - **Segunda Pasada**: Re-leer con contexto completo para enriquecer comprensión (como segunda lectura humana)
   - **Eso es todo**: Probar que funciona diferente a sistemas basados en chunks

#### 2. **Refinamiento Básico** (Cuando Obviamente se Necesita)
   - **Disparador simple**: Si nueva sección cambia significativamente comprensión de sección previa, actualizarla
   - **Sin seguimiento complejo**: Solo resúmenes "antes" y "después"
   - **Umbral manual**: Disparador simple basado en confianza

#### 3. **Contexto Acumulado** (Diferencia Principal)
   - **Contexto progresivo**: Cada sección procesada con todo el contexto previo
   - **Enriquecimiento global**: Segunda pasada usa comprensión completa del documento
   - **Sin chunks**: Evitar comprensión fragmentada

#### 4. **Salida Mínima** (Probar Concepto)
   - **JSON limpio**: Resúmenes jerárquicos y conceptos refinados sin metadata de proceso
   - **Calidad evidente**: El output debe mostrar claramente sus ventajas (resúmenes coherentes, conceptos definidos, jerarquía lógica)
   - **Enfoque en valor**: Solo la información útil para RAG/Fine-tuning, sin ruido del proceso interno

#### 5. **Esenciales de Desarrollo** (Para Testing)
   - **Modo dry-run**: Probar sin costos LLM
   - **Logging interno**: Solo para debugging durante desarrollo
   - **Configuración**: Habilitar/deshabilitar segunda pasada y refinamiento

### 🎯 **Criterios de Éxito para MVP v2**

- ✅ **Prueba de concepto**: Output que evidencie calidad superior (resúmenes coherentes vs. chunks fragmentados)
- ✅ **Test "3 pasos"**: Procesar exitosamente el libro con enfoque cognitivo
- ✅ **Calidad cognitiva**: Resúmenes que muestren comprensión profunda e integrada del contenido
- ✅ **Beneficio de contexto**: Demostrar valor del contexto acumulado vs. fragmentos

---

## 🗃️ Modelos de Datos v2

### **Principio Principal**: Definir contratos claros mientras se permite flexibilidad de implementación

```python
from __future__ import annotations
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class LanguageCode(str, Enum):
    """Idiomas soportados para procesamiento de documentos"""
    AUTO = "auto"  # Detección automática
    EN = "en"      # Inglés
    ES = "es"      # Español

class DocumentSection(BaseModel):
    """Sección de documento con estructura jerárquica"""
    model_config = ConfigDict(frozen=True)
    
    id: str                                    # Identificador único de sección
    title: str                                 # Título de sección (limpio)
    content: str                               # Contenido de texto de sección
    level: int                                 # Nivel jerárquico (0=documento, 1=capítulo, 2=sección, etc.)
    parent_id: Optional[str] = None            # ID de sección padre (None para raíz)
    children_ids: List[str] = Field(default_factory=list)  # IDs de secciones hijas
    order_index: int                           # Orden dentro del padre

class SectionSummary(BaseModel):
    """Resumen de sección optimizado para chunks RAG"""
    section_id: str                            # Referencia a DocumentSection.id
    title: str                                 # Título de sección
    summary: str                               # Resumen mejorado cognitivamente (optimizado para chunks RAG)
    key_concepts: List[str] = Field(default_factory=list)  # IDs de conceptos clave relevantes a esta sección
    summary_length: int                        # Longitud del resumen en caracteres

class ConceptDefinition(BaseModel):
    """Concepto clave con definición refinada cognitivamente"""
    concept_id: str                            # Identificador único (ej: "sedentarismo", "movimiento_natural")
    name: str                                  # Nombre legible del concepto
    definition: str                            # Definición refinada cognitivamente
    first_mentioned_in: str                    # ID de sección donde se identificó este concepto primero
    relevant_sections: List[str] = Field(default_factory=list)  # IDs de sección donde el concepto es relevante

class CognitiveKnowledge(BaseModel):
    """Conocimiento completo extraído con procesamiento cognitivo para RAG/Fine-tuning"""
    # Identificación de documento
    document_title: str
    document_summary: str                      # Resumen mejorado cognitivamente a nivel documento
    detected_language: LanguageCode
    
    # Resúmenes jerárquicos optimizados para chunks RAG
    hierarchical_summaries: Dict[str, SectionSummary]  # Mapeo ID Sección -> Resumen
    
    # Conceptos clave con definiciones refinadas cognitivamente
    concepts: Dict[str, ConceptDefinition]     # Mapeo ID Concepto -> Definición
    
    # Índices de navegación jerárquica
    hierarchy_index: Dict[str, List[str]] = Field(default_factory=dict)  # Nivel -> IDs de Sección
    parent_child_map: Dict[str, List[str]] = Field(default_factory=dict)  # ID Padre -> IDs Hijos
    
    # Estadísticas de resúmenes
    total_sections: int = 0
    avg_summary_length: int = 0
    total_concepts: int = 0
    
    # Metadatos opcionales de procesamiento
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)

class CognitiveConfig(BaseModel):
    """Configuración para lectura cognitiva de documentos"""
    
    # Configuración LLM
    model_name: str = Field(default="qwen3:8b", description="Nombre del modelo LLM por defecto (usado cuando no se configuran modelos duales)")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperatura LLM")
    
    # Configuración de Modelo Dual - Simula patrones de lectura humana
    # Configuración multi-pasada (diseño extensible)
    max_passes: int = Field(default=2, ge=1, le=10, description="Número máximo de pasadas cognitivas")
    convergence_threshold: float = Field(default=0.1, ge=0.01, le=1.0, description="Umbral para detectar cuándo pasadas adicionales añaden valor mínimo")
    
    # Estrategia de modelo dual: scan rápido + procesamiento de calidad
    enable_fast_first_pass: bool = Field(default=True, description="Usar modelo rápido para scan inicial")
    fast_pass_model: Optional[str] = Field(default="llama3.1:8b", description="Modelo rápido para scan inicial del documento")
    main_model: Optional[str] = Field(default="qwen3:8b", description="Modelo de calidad para procesamiento cognitivo detallado")
    
    # Configuración de temperatura
    fast_pass_temperature: Optional[float] = Field(default=0.1, ge=0.0, le=2.0, description="Temperatura para scan rápido")
    main_pass_temperature: Optional[float] = Field(default=0.3, ge=0.0, le=2.0, description="Temperatura para procesamiento de calidad")

### **🔧 Filosofía de Diseño Multi-Pasada Extensible**

El MVP implementa **lectura de 2 pasadas** pero está arquitecturalmente preparado para **extensión a N pasadas**:

```python
# Uso MVP (2 pasadas) - Listo hoy
config = CognitiveConfig(
    max_passes=2,
    fast_pass_model="llama3.1:8b",    # Scan inicial rápido
    main_model="qwen3:8b"          # Procesamiento cognitivo de calidad
)

# Uso futuro N-pasadas (misma API) - Extensión fluida
config = CognitiveConfig(
    max_passes=4,                     # Profundidad configurable
    convergence_threshold=0.05,       # Optimización auto-stop  
    main_model="qwen3:8b"          # Mismo modelo, contexto más rico cada pasada
)
```

#### **Principios Clave de Diseño**

1. **📖 Mismo "Cerebro", Mejor Conocimiento**: Múltiples pasadas usan el **mismo modelo** con **contexto progresivamente más rico**
2. **🔄 Acumulación de Contexto**: Cada pasada proporciona resúmenes, conceptos e insights acumulados a la siguiente
3. **🏆 Autoridad del Texto Original**: **El texto fuente siempre tiene precedencia** sobre resúmenes/contexto previo cuando hay conflictos
4. **⚡ Balance Inteligente Velocidad/Calidad**: Scan rápido (`llama3.1:8b`) + Procesamiento de calidad (`qwen3:8b`) 
5. **🎯 Detección de Convergencia**: Futuro auto-stop cuando pasadas adicionales añaden valor mínimo
6. **🏗️ Consistencia de API**: Misma interfaz escala de MVP 2-pasadas a características avanzadas N-pasadas

#### **🏆 Principio de Autoridad del Texto Fuente**

**CRÍTICO**: Al procesar cada sección, el **texto original** es la autoridad suprema:

```python
# Jerarquía de prompting (mayor a menor autoridad)
AUTHORITY_HIERARCHY = [
    "Contenido del texto original",    # 🥇 Autoridad suprema - siempre gana
    "Resúmenes refinados previos",     # 🥈 Guía contextual  
    "Conceptos descubiertos",          # 🥉 Información de apoyo
    "Comprensión global del documento" # 📚 Contexto de fondo
]
```

**Estrategia de Resolución de Conflictos**:
- ✅ **Texto contradice resumen** → Actualizar resumen para coincidir con texto
- ✅ **Texto añade nuevo matiz** → Enriquecer resumen con perspectiva del texto  
- ✅ **Texto revela error en concepto** → Refinar definición del concepto
- ❌ **Nunca** modificar interpretación del texto para ajustarse al contexto previo

#### **💭 Estrategia de Prompting Consciente de Autoridad**

**Estructura de Prompt de Ejemplo** (aplicando autoridad del texto):

```
CONTEXTO (solo para información de fondo):
- Resumen del Libro: [comprensión previa]
- Definiciones de Conceptos: [descubiertas hasta ahora]  
- Resumen de Sección Padre: [si aplica]

TEXTO FUENTE (AUTORITATIVO):
[contenido real de la sección a procesar]

INSTRUCCIONES:
1. Lee el TEXTO FUENTE cuidadosamente - esta es tu fuente PRIMARIA de verdad
2. Usa el CONTEXTO solo como información de fondo para informar tu comprensión
3. Si el TEXTO FUENTE contradice cualquier información del CONTEXTO:
   - Confía completamente en el TEXTO FUENTE
   - Actualiza tu comprensión basada en el TEXTO FUENTE
   - Nota las discrepancias para refinamiento
4. Genera resumen que refleje el TEXTO FUENTE con precisión
5. Identifica conceptos mencionados en el TEXTO FUENTE (no solo del contexto)

CRÍTICO: El TEXTO FUENTE siempre es correcto. Los resúmenes previos pueden contener errores o comprensión incompleta.
```

#### **📝 Ejemplo Práctico: Autoridad del Texto en Acción**

**Escenario**: Procesando capítulo 3 de "3 pasos contra el sedentarismo"

```python
# Contexto previo (puede contener errores)
resumen_previo = {
    "sedentarismo": "Falta de ejercicio físico en la vida moderna"  # ← Comprensión incompleta
}

# Texto de sección actual (autoritativo)
texto_fuente = """
El sedentarismo, en su sentido más profundo, no es simplemente pasar mucho tiempo sentado. 
Es un concepto arraigado en la falta de movimiento variado y en la especialización de las posturas.
"""

# Resultado del procesamiento cognitivo (autoridad del texto aplicada)
comprension_refinada = {
    "sedentarismo": "Estado crónico de inactividad física que resulta de la falta de movimiento variado y especialización de posturas, no simplemente pasar tiempo sentado"  # ← Corregido por texto fuente
}
```

**Insight Clave**: El texto fuente **corrigió** la definición previa incompleta, demostrando cómo la autoridad del texto asegura precisión evolutiva.

---

## 🔄 **Propósito Central: Corrección de Errores y Refinamiento**

### **🎯 Justificación Principal del Diseño Multi-Pasada**

La **razón principal** para segunda, tercera y N-ésima pasadas es **corrección sistemática de errores y refinamiento del conocimiento**:

#### **🔍 Qué Se Corrige/Refina**

1. **📝 Precisión de Resúmenes**
   - **Errores iniciales**: Los resúmenes de primera pasada pueden perder puntos clave o malinterpretar conceptos
   - **Refinamiento progresivo**: Cada pasada corrige y enriquece la comprensión
   - **Coherencia global**: Secciones posteriores proporcionan contexto que clarifica malentendidos previos

2. **💡 Definiciones de Conceptos**
   - **Aproximaciones iniciales**: Primeros encuentros con conceptos generan definiciones parciales
   - **Precisión iterativa**: Pasadas subsecuentes refinan definiciones con contexto más rico
   - **Validación cruzada**: Conceptos mencionados en varias secciones obtienen definiciones más precisas

3. **🔗 Comprensión de Relaciones** 
   - **Conexiones perdidas**: Procesamiento de una sola pasada pierde relaciones entre conceptos
   - **Patrones emergentes**: Multi-pasada revela cómo se relacionan conceptos a través del documento
   - **Claridad jerárquica**: Relaciones padre-hijo entre conceptos se vuelven aparentes

#### **📈 Ejemplos de Corrección en Uso Real**

```python
# Pasada 1: Comprensión inicial (a menudo incompleta/incorrecta)
concepto_primera_pasada = {
    "sedentarismo": "Falta de ejercicio físico"  # ← Comprensión superficial
}

# Pasada 2: Corregida con contexto global
concepto_segunda_pasada = {
    "sedentarismo": "Estado crónico de inactividad física caracterizado por falta de movimiento variado y especialización de posturas, no simplemente ausencia de ejercicio"  # ← Comprensión profunda y precisa
}

# Pasada 3: Refinada adicionalmenre con referencias cruzadas
concepto_tercera_pasada = {
    "sedentarismo": "Estado crónico de inactividad física que resulta de entornos modernos que eliminan movimiento variado, causando adaptaciones corporales problemáticas mediante especialización postural. Se diferencia de la simple falta de ejercicio por su enfoque en variedad de movimiento vs. intensidad."  # ← Comprensión integral y matizada
}
```

#### **✅ Indicadores de Éxito para Refinamiento**

- **Evolución de conceptos**: Definiciones se vuelven más precisas y comprehensivas entre pasadas
- **Detección de errores**: Sistema identifica y corrige malentendidos previos  
- **Mejora de coherencia**: Resúmenes se alinean mejor con mensaje general del documento
- **Claridad de relaciones**: Conexiones entre conceptos se vuelven explícitas y precisas
    
    # Procesamiento de Documentos
    chunk_size: int = Field(default=1000, gt=100, description="Tamaño de chunk de texto para procesamiento")
    chunk_overlap: int = Field(default=200, ge=0, description="Solapamiento entre chunks")
    context_window: int = Field(default=4096, gt=0, description="Límite de ventana de contexto LLM")
    
    # Configuraciones de Rendimiento
    timeout_seconds: int = Field(default=120, gt=0, description="Timeout de request")
    max_retries: int = Field(default=3, ge=0, description="Máximo intentos de retry")
    document_language: LanguageCode = Field(default=LanguageCode.AUTO, description="Idioma del documento")
    
    # Características Cognitivas
    enable_second_pass: bool = Field(default=True, description="Habilitar enriquecimiento de segunda pasada")
    enable_refinement: bool = Field(default=True, description="Habilitar refinamiento de primera pasada")
    refinement_threshold: float = Field(
        default=0.4, 
        ge=0.0, 
        le=1.0, 
        description="Umbral para disparar refinamiento (0.0=nunca, 1.0=siempre)"
    )
    
    # Características de Desarrollo
    dry_run: bool = Field(default=False, description="Ejecutar sin llamadas LLM")
    mock_responses: bool = Field(default=False, description="Usar respuestas mock")
    
    # Carga de variables de entorno
    @classmethod
    def from_env(cls) -> "CognitiveConfig":
        """Crear configuración desde variables de entorno con fallback a defaults"""
        import os
        return cls(
            # Configuraciones LLM
            model_name=os.getenv("COGNITIVE_READER_MODEL", "qwen3:8b"),
            temperature=float(os.getenv("COGNITIVE_READER_TEMPERATURE", "0.1")),
            
            # Configuración multi-pasada (diseño extensible)
            max_passes=int(os.getenv("COGNITIVE_READER_MAX_PASSES", "2")),
            convergence_threshold=float(os.getenv("COGNITIVE_READER_CONVERGENCE_THRESHOLD", "0.1")),
            
            # Configuraciones de modelo dual (scan rápido + procesamiento de calidad)
            enable_fast_first_pass=os.getenv("COGNITIVE_READER_ENABLE_FAST_FIRST_PASS", "true").lower() == "true",
            fast_pass_model=os.getenv("COGNITIVE_READER_FAST_PASS_MODEL", "llama3.1:8b"),
            main_model=os.getenv("COGNITIVE_READER_MAIN_MODEL", "qwen3:8b"),
            fast_pass_temperature=float(os.getenv("COGNITIVE_READER_FAST_PASS_TEMPERATURE", "0.1")) if os.getenv("COGNITIVE_READER_FAST_PASS_TEMPERATURE") else None,
            main_pass_temperature=float(os.getenv("COGNITIVE_READER_MAIN_PASS_TEMPERATURE", "0.3")) if os.getenv("COGNITIVE_READER_MAIN_PASS_TEMPERATURE") else None,
            
            # Configuraciones de procesamiento
            chunk_size=int(os.getenv("COGNITIVE_READER_CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("COGNITIVE_READER_CHUNK_OVERLAP", "200")),
            context_window=int(os.getenv("COGNITIVE_READER_CONTEXT_WINDOW", "4096")),
            
            # Configuraciones de rendimiento
            timeout_seconds=int(os.getenv("COGNITIVE_READER_TIMEOUT_SECONDS", "120")),
            max_retries=int(os.getenv("COGNITIVE_READER_MAX_RETRIES", "3")),
            document_language=LanguageCode(os.getenv("COGNITIVE_READER_LANGUAGE", "auto")),
            
            # Características cognitivas
            enable_second_pass=os.getenv("COGNITIVE_READER_ENABLE_SECOND_PASS", "true").lower() == "true",
            enable_refinement=os.getenv("COGNITIVE_READER_ENABLE_REFINEMENT", "true").lower() == "true",
            refinement_threshold=float(os.getenv("COGNITIVE_READER_REFINEMENT_THRESHOLD", "0.4")),
            
            # Características de desarrollo
            dry_run=os.getenv("COGNITIVE_READER_DRY_RUN", "false").lower() == "true",
            mock_responses=os.getenv("COGNITIVE_READER_MOCK_RESPONSES", "false").lower() == "true",
        )

# Referencia de Variables de Entorno
COGNITIVE_READER_ENV_VARS = {
    # Configuración LLM
    "COGNITIVE_READER_MODEL": "Nombre del modelo LLM por defecto (default: qwen3:8b)",
    "COGNITIVE_READER_TEMPERATURE": "Temperatura LLM por defecto 0.0-2.0 (default: 0.1)",
    
    # Configuración Multi-pasada (Diseño Extensible)
    "COGNITIVE_READER_MAX_PASSES": "Número máximo de pasadas cognitivas (default: 2)",
    "COGNITIVE_READER_CONVERGENCE_THRESHOLD": "Umbral para auto-detener pasadas cuando mejora mínima (default: 0.1)",
    
    # Estrategia de Modelo Dual (Scan Rápido + Procesamiento de Calidad)
    "COGNITIVE_READER_ENABLE_FAST_FIRST_PASS": "Habilitar modelo rápido para scan inicial (default: true)",
    "COGNITIVE_READER_FAST_PASS_MODEL": "Modelo rápido para scan inicial del documento (default: llama3.1:8b)",
    "COGNITIVE_READER_MAIN_MODEL": "Modelo de calidad para procesamiento cognitivo detallado (default: qwen3:8b)",
    "COGNITIVE_READER_FAST_PASS_TEMPERATURE": "Temperatura para scan rápido (default: 0.1)",
    "COGNITIVE_READER_MAIN_PASS_TEMPERATURE": "Temperatura para procesamiento de calidad (default: 0.3)",
    
    # Configuración de Procesamiento  
    "COGNITIVE_READER_CHUNK_SIZE": "Tamaño de chunk de texto (default: 1000)",
    "COGNITIVE_READER_CHUNK_OVERLAP": "Solapamiento de chunk (default: 200)",
    "COGNITIVE_READER_CONTEXT_WINDOW": "Límite de contexto LLM (default: 4096)",
    "COGNITIVE_READER_LANGUAGE": "Idioma documento auto/en/es (default: auto)",
    
    # Características Cognitivas
    "COGNITIVE_READER_ENABLE_SECOND_PASS": "Habilitar segunda pasada true/false (default: true)",
    "COGNITIVE_READER_ENABLE_REFINEMENT": "Habilitar refinamiento true/false (default: true)",
    "COGNITIVE_READER_REFINEMENT_THRESHOLD": "Umbral refinamiento 0.0-1.0 (default: 0.4)",
    
    # Rendimiento y Desarrollo
    "COGNITIVE_READER_TIMEOUT_SECONDS": "Timeout de request (default: 120)",
    "COGNITIVE_READER_MAX_RETRIES": "Max retries (default: 3)",
    "COGNITIVE_READER_DRY_RUN": "Modo dry run true/false (default: false)",
    "COGNITIVE_READER_MOCK_RESPONSES": "Respuestas mock true/false (default: false)",
}
```

### 📚 **Requisitos de API**

**Interfaz Principal**:
- Interfaz principal: `read_document(file_path, config) -> CognitiveKnowledge`
- Soporte de configuración via variables de entorno
- API simple y limpia enfocada en características cognitivas

**Opciones de Configuración**:
- `enable_second_pass`: Boolean para habilitar/deshabilitar enriquecimiento de segunda pasada
- `enable_refinement`: Boolean para habilitar/deshabilitar refinamiento de primera pasada  
- `refinement_threshold`: Float (0.0-1.0) para controlar sensibilidad de refinamiento
- Configuración de modelo dual para procesamiento rápido/calidad

**Datos de Retorno**:
- Estadísticas completas de procesamiento cognitivo (refinamientos hechos, enriquecimientos hechos)
- Indicación clara de qué secciones fueron procesadas con características cognitivas
- Metadatos de procesamiento incluyendo modelos usados para cada pasada
- Seguimiento de evolución cognitiva e historial de refinamiento

---

## 🏗️ Arquitectura Cognitiva v2

### **Componentes del Sistema**

```
CognitiveReader (Motor Principal)
├── StructureDetector (análisis y detección de estructura de documentos)
├── ProgressiveReader (mejorado con capacidad de refinamiento)
├── ContextualEnricher (nuevo componente para segunda pasada)
└── CognitiveSynthesizer (mejorado con metadatos cognitivos)
```

### **Responsabilidades de Componentes**

#### **CognitiveReader** (Orquestador Principal)
**Propósito**: Coordinar proceso de lectura cognitiva de dos pasadas

**Responsabilidades**:
- Orquestar flujo completo de lectura de dos pasadas
- Gestionar configuración para características cognitivas (refinamiento, segunda pasada)
- Coordinar entre procesamiento de primera pasada y segunda pasada
- Proporcionar API limpia enfocada en características cognitivas
- Rastrear y reportar métricas de procesamiento cognitivo

**Requisitos de Interfaz**:
- `read_document(file_path, config) -> CognitiveKnowledge`: Interfaz primaria para lectura cognitiva
- API limpia enfocada en características cognitivas
- Estadísticas comprehensivas de procesamiento cognitivo en resultados

#### **ProgressiveReader** (Mejorado)
**Propósito**: Ejecutar primera pasada con lectura progresiva y capacidad de refinamiento

**Responsabilidades**:
- Procesar secciones secuencialmente con contexto acumulado
- Detectar cuando nuevo contexto cambia significativamente comprensión de secciones previas
- Actualizar resúmenes de secciones previas cuando se necesita refinamiento
- Rastrear eventos de refinamiento y razones
- Mantener acumulación de contexto a través del procesamiento de secciones

**Requisitos**:
- Capacidad de refinamiento configurable (habilitar/deshabilitar)
- Configuración de umbral de refinamiento
- Seguimiento completo de qué secciones fueron refinadas y por qué
- Procesamiento eficiente con contexto acumulado

#### **ContextualEnricher** (Nuevo Componente)
**Propósito**: Ejecutar enriquecimiento de segunda pasada con contexto global del documento

**Responsabilidades**:
- Re-leer secciones con comprensión completa del documento
- Identificar oportunidades de enriquecimiento con contexto global
- Generar resúmenes mejorados que incorporen perspectiva completa del documento
- Distinguir entre enriquecimientos significativos y cambios triviales
- Preservar refinamientos de primera pasada mientras añade insights de segunda pasada

**Requisitos**:
- Debe ser configurable para habilitar/deshabilitar procesamiento de segunda pasada
- Debe trabajar con resultados del ProgressiveReader de primera pasada
- Debe rastrear eventos de enriquecimiento y valor añadido
- Debe mantener eficiencia de procesamiento

#### **CognitiveSynthesizer** (Mejorado)
**Propósito**: Generar síntesis final del documento con conciencia de procesamiento cognitivo

**Responsabilidades**:
- Crear síntesis jerárquica del documento
- Incorporar metadatos de procesamiento cognitivo en resultados finales
- Notar qué secciones fueron sometidas a refinamiento o enriquecimiento
- Generar resumen de procesamiento cognitivo para salida

**Requisitos**:
- Calidad superior de síntesis con características cognitivas
- Indicación clara de todos los eventos de procesamiento cognitivo en salida
- Resumen comprehensivo de beneficios y evolución del procesamiento cognitivo

---

## 🔄 Requisitos de Proceso Cognitivo

### **Flujo de Procesamiento de Dos Pasadas**

```
Entrada de Documento
    ↓
Detección de Estructura
    ↓
┌─────────────────┐
│  PRIMERA PASADA │
│ Progresiva +    │
│ Refinamiento    │
│ Básico          │
└─────────────────┘
    ↓
├── Lectura Progresiva ──→ Acumulación de Contexto
└── Refinamiento Básico ──→ Actualizar resúmenes si comprensión cambia
    ↓
Resultado Primera Pasada
    ↓
┌─────────────────┐
│  SEGUNDA PASADA │
│ Contexto Global │
│ Enriquecimiento │
└─────────────────┘
    ↓
├── Re-leer con Contexto Global ──→ Resúmenes Mejorados
└── Integración Simple ──→ Conocimiento Final
    ↓
Salida de Conocimiento Cognitivo
```

### **Algoritmo de Procesamiento Jerárquico**

El proceso de lectura cognitiva implementa un algoritmo de **síntesis jerárquica bottom-up** que procesa la estructura del documento desde las hojas hasta la raíz, combinando el contenido de cada sección con los resúmenes de sus hijos en cada nivel.

#### **Visión General del Algoritmo**

```
1. Análisis de Estructura
   ├── Detectar profundidad máxima de jerarquía (o usar límite especificado por usuario)
   └── Identificar secciones hoja (nivel más profundo, sin hijos)

2. Procesamiento Bottom-Up
   ├── PASO 1: Procesar Secciones Hoja
   │   ├── Leer contenido de sección (encabezado + párrafos)
   │   ├── Generar resumen de sección
   │   └── Extraer conceptos clave
   │
   ├── PASO 2: Procesar Secciones Contenedoras (nivel por nivel, bottom-up)
   │   ├── Combinar: Contenido propio de sección + Resúmenes de hijos
   │   ├── Generar resumen contenedor del contenido combinado
   │   └── Extraer/fusionar conceptos de contenedor + hijos
   │
   └── PASO 3: Generar Resumen de Documento
       ├── Combinar: Título del documento + Todos los resúmenes de nivel superior
       ├── Generar resumen a nivel de documento
       └── Crear glosario final de conceptos

3. Generación de Salida
   └── Conocimiento Jerárquico con árbol completo de secciones
```

#### **Ejemplo de Orden de Procesamiento**

Para una estructura de documento como:
```
# Título del Libro
## Capítulo 1: Introducción
### Sección 1.1: Antecedentes
### Sección 1.2: Propósito
## Capítulo 2: Métodos
### Sección 2.1: Enfoque
```

**Secuencia de procesamiento:**
1. **Procesamiento de hojas**: `Sección 1.1`, `Sección 1.2`, `Sección 2.1` (nivel más profundo primero)
2. **Procesamiento de contenedores**: `Capítulo 1` (contenido + resúmenes de 1.1, 1.2), `Capítulo 2` (contenido + resumen de 2.1)
3. **Procesamiento de documento**: `Título del Libro` (contenido + resúmenes de Capítulo 1, Capítulo 2)

#### **Reglas de Composición de Contenido**

**Para Secciones Hoja:**
- Entrada: `section.content` (encabezado + párrafos siguientes)
- Generar: Resumen de sección + conceptos clave

**Para Secciones Contenedoras:**
- Entrada: `section.content + child_summaries`
- Formato: `"Contenido de sección:\n{section.content}\n\nResúmenes de subsecciones:\n{child_summaries}"`
- Generar: Resumen contenedor que sintetiza contenido propio con insights de hijos

**Para Nivel de Documento:**
- Entrada: `document_title + top_level_summaries`
- Generar: Resumen de documento + glosario global de conceptos

#### **Implementación Técnica**

```python
async def process_hierarchically(sections: List[DocumentSection]) -> CognitiveKnowledge:
    """Procesar documento usando síntesis jerárquica bottom-up."""
    
    # 1. Organizar secciones por nivel de jerarquía
    levels = organize_by_level(sections)
    max_level = max(levels.keys())
    
    # 2. Procesar desde el nivel más profundo hasta la raíz
    summaries = {}
    
    for level in range(max_level, 0, -1):  # Procesamiento bottom-up
        for section in levels[level]:
            if section.children_ids:  # Sección contenedora
                content = combine_section_and_children_content(section, summaries)
            else:  # Sección hoja
                content = section.content
                
            summary = await generate_summary(content, section.title)
            summaries[section.id] = summary
    
    # 3. Generar síntesis a nivel de documento
    document_summary = await generate_document_summary(document_title, top_level_summaries)
    
    return CognitiveKnowledge(...)
```

Este algoritmo asegura que:
- ✅ **Cada sección** recibe contenido apropiado (texto propio + contexto de hijos)
- ✅ **Orden de procesamiento** sigue dependencia lógica (hijos antes que padres)
- ✅ **Escalabilidad** funciona para cualquier profundidad de estructura de documento
- ✅ **Preservación de contexto** mantiene relaciones jerárquicas

### **Requisitos de Primera Pasada**

**Requisitos Funcionales:**
- **Lectura Progresiva**: Procesar secciones secuencialmente con contexto acumulado de secciones previas
- **Acumulación de Contexto**: Construir contexto comprehensivo mientras progresa la lectura
- **Detección de Refinamiento**: Identificar cuando nueva información cambia significativamente comprensión de secciones previas
- **Actualizaciones de Resumen**: Actualizar resúmenes de secciones previas cuando evoluciona la comprensión
- **Seguimiento de Refinamiento**: Registrar qué resúmenes fueron refinados y por qué

**Requisitos Técnicos:**
- Selección y gestión de modelo rápido para optimización de rendimiento
- Umbral de refinamiento configurable vía parámetro `refinement_threshold`
- Refinamiento puede deshabilitarse vía configuración `enable_refinement`
- Seguimiento completo de refinamientos hechos para métricas y análisis

### **Requisitos de Segunda Pasada**

**Requisitos Funcionales:**
- **Re-lectura con Contexto Global**: Re-procesar cada sección con contexto completo del documento
- **Detección de Enriquecimiento**: Identificar casos donde contexto global añade insights significativos
- **Mejora de Resumen**: Mejorar resúmenes con insights solo disponibles después de lectura completa
- **Integración**: Combinar resultados de primera pasada y segunda pasada coherentemente

**Requisitos Técnicos:**
- Segunda pasada puede deshabilitarse vía configuración `enable_second_pass`
- Debe detectar y rastrear enriquecimientos significativos vs cambios triviales
- Debe preservar refinamientos de primera pasada mientras añade enriquecimientos
- Debe mantener rendimiento de procesamiento dentro de límites aceptables

---

## 📊 Formatos de Salida Simples v2

### **JSON de Conocimiento Cognitivo** (Optimizado para RAG/Fine-tuning)

```json
{
  "document_title": "3 Pasos Contra el Sedentarismo",
  "document_summary": "Guía práctica para contrarrestar el sedentarismo mediante tres movimientos fundamentales que restauran la funcionalidad corporal natural: caminar más para la capacidad cardiovascular base, sentarse en el suelo para movilidad de cadera, y colgarse para fuerza de agarre y descompresión espinal. El libro explica cómo el sedentarismo causa adaptaciones corporales problemáticas y presenta una metodología específica basada en movimientos naturales para recuperar la salud y funcionalidad.",
  "detected_language": "es",
  
  "concepts": {
    "sedentarismo": {
      "concept_id": "sedentarismo",
      "name": "Sedentarismo",
      "definition": "Estado crónico de inactividad física que resulta de la exposición prolongada a entornos que requieren poca o ninguna actividad física, causando adaptaciones corporales que comprometen la salud y funcionalidad natural del cuerpo humano.",
      "first_mentioned_in": "introduccion",
      "relevant_sections": ["introduccion", "problemas_comunes", "tres_pasos"]
    },
    "movimiento_natural": {
      "concept_id": "movimiento_natural",
      "name": "Movimiento Natural", 
      "definition": "Patrones de movimiento para los que el cuerpo humano está evolutivamente adaptado, incluyendo caminar, sentarse en el suelo, colgarse y otras actividades que mantienen la funcionalidad corporal óptima sin requerir equipamiento especializado.",
      "first_mentioned_in": "introduccion",
      "relevant_sections": ["introduccion", "tres_pasos"]
    },
    "vida_nomada": {
      "concept_id": "vida_nomada",
      "name": "Vida Nómada Ancestral",
      "definition": "Estilo de vida de nuestros ancestros durante más de dos millones de años, caracterizado por movimiento constante, variedad de posturas y estímulos diversos que moldearon nuestro cuerpo para la adaptación y resiliencia.",
      "first_mentioned_in": "introduccion",
      "relevant_sections": ["introduccion"]
    },
    "tres_pasos": {
      "concept_id": "tres_pasos",
      "name": "Metodología de Tres Pasos",
      "definition": "Sistema específico de intervención contra el sedentarismo que consiste en: 1) Caminar más para restaurar la funcionalidad base, 2) Sentarse más en el suelo para recuperar movilidad de cadera, y 3) Colgarse más de las manos para fortalecer agarre y descomprimir columna.",
      "first_mentioned_in": "tres_pasos",
      "relevant_sections": ["tres_pasos", "paso_1", "paso_2", "paso_3"]
    }
  },
  
  "hierarchical_summaries": {
    "book": {
      "section_id": "book",
      "title": "3 Pasos Contra el Sedentarismo",
      "summary": "Guía práctica para contrarrestar el sedentarismo mediante tres movimientos fundamentales que restauran la funcionalidad corporal natural. Explica cómo el sedentarismo causa adaptaciones corporales problemáticas y presenta una metodología específica basada en movimientos naturales para recuperar la salud y funcionalidad.",
      "key_concepts": ["sedentarismo", "movimiento_natural", "vida_nomada", "tres_pasos"],
      "summary_length": 850
    },
    "introduccion": {
      "section_id": "introduccion",
      "title": "Introducción al sedentarismo",
      "summary": "Análisis profundo del sedentarismo como discrepancia entre nuestra biología ancestral nómada y el entorno moderno. Explica cómo nuestros ancestros vivieron durante más de dos millones de años en movimiento constante, y cómo la revolución agrícola hace 10,000 años nos transformó en seres sedentarios, creando un desajuste que genera enfermedades de la civilización y adaptaciones celulares problemáticas.",
      "key_concepts": ["sedentarismo", "vida_nomada", "movimiento_natural"],
      "summary_length": 780
    },
    "problemas_comunes": {
      "section_id": "problemas_comunes",
      "title": "Problemas comunes: limitaciones de la movilidad, dolor y estrés",
      "summary": "Exploración científica de cómo el sistema nervioso procesa movimiento y dolor, explicando conceptos como propiocepción, mapas cerebrales, nocicepción y sensibilización. Analiza la relación entre estabilidad del tronco y movilidad de extremidades, y cómo la rigidez muscular actúa como mecanismo de protección del cerebro ante movimientos percibidos como inseguros.",
      "key_concepts": ["dolor_cronico", "mapas_cerebrales", "estabilidad_proximal"],
      "summary_length": 720
    },
    "tres_pasos": {
      "section_id": "tres_pasos", 
      "title": "3 pasos para salir del sedentarismo",
      "summary": "Presentación de la metodología central: tres movimientos específicos que abordan las causas raíz del sedentarismo. Caminar más como actividad natural accesible, sentarse más en el suelo para fortalecer musculatura postural y movilidad de cadera, y colgarse más de las manos para desarrollar agarre y descomprimir articulaciones. Incluye respiración como herramienta para controlar el sistema nervioso autónomo.",
      "key_concepts": ["tres_pasos", "caminar", "sentarse_suelo", "colgarse", "respiracion"],
      "summary_length": 920
    },
    "paso_1": {
      "section_id": "paso_1",
      "title": "Caminar más",
      "summary": "Explicación de caminar como la actividad más natural para el ser humano. No requiere equipo especial y es accesible para todos. Beneficios incluyen mejora de densidad ósea, circulación, salud de los pies y activación de músculos posturales. Más efectivo distribuir pequeñas caminatas a lo largo del día que hacer una sola caminata larga.",
      "key_concepts": ["caminar", "movimiento_base", "densidad_osea"],
      "summary_length": 650
    },
    "paso_2": {
      "section_id": "paso_2",
      "title": "Sentarse más en el suelo",
      "summary": "Análisis de cómo la silla proporciona estabilidad externa que atrofia la musculatura postural y reduce el rango de movimiento. Sentarse en el suelo obliga a usar músculos posturales, cambiar de postura constantemente y fortalecer articulaciones. Esta práctica mejora fuerza, equilibrio y movilidad del tren inferior, relacionándose con mayor longevidad.",
      "key_concepts": ["sentarse_suelo", "musculatura_postural", "movilidad_cadera"],
      "summary_length": 680
    },
    "paso_3": {
      "section_id": "paso_3",
      "title": "Colgarse más de las manos",
      "summary": "Como primates, estamos biológicamente diseñados para colgarnos. La falta de este movimiento debilita el agarre, tendones y ligamentos del tren superior, creando desequilibrios en hombros. Colgarse de forma progresiva fortalece el agarre, descomprime articulaciones y mejora movilidad y control de hombros y escápulas.",
      "key_concepts": ["colgarse", "fuerza_agarre", "descompresion_articular"],
      "summary_length": 620
    }
  },
  
  "hierarchy_index": {
    "0": ["book"],
    "1": ["introduccion", "problemas_comunes", "tres_pasos", "conclusiones"],
    "2": ["paso_1", "paso_2", "paso_3", "paso_extra"]
  },
  
  "parent_child_map": {
    "book": ["introduccion", "problemas_comunes", "tres_pasos", "conclusiones"],
    "tres_pasos": ["paso_1", "paso_2", "paso_3", "paso_extra"]
  },
  
  "total_sections": 8,
  "avg_summary_length": 740,
  "total_concepts": 4
}
```

### **Schema JSON y Versionado**

**Estrategia de Versionado del Schema**: 
- Todo output sigue un **Schema JSON versionado** para seguridad del consumidor
- Las versiones del schema usan **versionado semántico** (MAJOR.MINOR.PATCH)
- Versión actual: **v1.0.0**

**Ubicación del Schema**:
```
Repositorio GitHub: https://github.com/juanje/cognitive-document-reader/schemas/
├── v1.0.0/
│   ├── cognitive-knowledge.json       # Schema principal de output
│   ├── concept-definition.json        # Schema de concepto
│   └── section-summary.json          # Schema de resumen
└── README.md                          # Documentación de schemas
```

**Uso para Consumidores**:
```python
# Ejemplo de validación Python
import jsonschema
import requests

# Cargar schema desde GitHub
schema_url = "https://raw.githubusercontent.com/juanje/cognitive-document-reader/main/schemas/v1.0.0/cognitive-knowledge.json"
schema = requests.get(schema_url).json()

# Validar output del cognitive reader
jsonschema.validate(output_data, schema)
```

**Evolución del Schema**:
- **v1.0.0**: Release inicial (resúmenes jerárquicos + conceptos)
- **v1.1.0**: Futuro - Añadir campos opcionales (compatible hacia atrás)
- **v2.0.0**: Futuro - Cambios breaking (bump de versión mayor)

**Output Incluye Versión del Schema**:
```json
{
  "schema_version": "1.0.0",
  "document_title": "...",
  ...
}
```

### **Markdown de Evolución Básica** (Anotaciones simples)

```markdown
# 3 Pasos Contra el Sedentarismo - Resumen de Lectura Cognitiva

> **Procesamiento**: Lectura cognitiva de dos pasadas | 3 refinamientos | 5 enriquecimientos

## 📖 Resumen del Documento
Comprensión final enriquecida del documento completo...

## 📄 Resúmenes de Secciones

### Introducción al sedentarismo ✨ *Refinado + Enriquecido*
Resumen final que incorpora comprensión de secciones posteriores...

**Nota**: Este resumen fue refinado durante primera pasada cuando el método específico de 3 pasos se volvió claro.

### Problemas comunes: limitaciones de la movilidad, dolor y estrés ✨ *Enriquecido*  
Resumen final enriquecido con contexto global sobre cómo los problemas se conectan con soluciones...

**Nota**: Este resumen fue enriquecido durante segunda pasada con contexto completo del documento sobre los 3 pasos.

### 3 pasos para salir del sedentarismo ✨ *Refinado + Enriquecido*
Resumen final mostrando los tres movimientos específicos (caminar más, sentarse en el suelo, colgarse) como intervención sistemática...

**Nota**: Este resumen fue refinado durante primera pasada y enriquecido durante segunda pasada.

---

## 🔄 Notas de Procesamiento Cognitivo

**Refinamientos hechos durante primera pasada**: 3
- Introducción: Actualizado cuando las soluciones de movimiento específicas se volvieron claras
- Sección 3 pasos: Actualizado cuando la conexión entre problemas y movimientos específicos se volvió clara

**Enriquecimientos hechos durante segunda pasada**: 5  
- Todas las secciones enriquecidas con contexto completo del documento
- Conexiones entre problemas de movimiento y soluciones de movimiento específicas se volvieron más claras

**Insight clave**: El enfoque de dos pasadas reveló la metodología coherente del libro donde cada sección construye hacia la solución específica de 3 pasos (caminar más, sentarse en el suelo, colgarse).
```

### **Salida CLI** (Mostrar diferencia)

```bash
$ cognitive-reader libro.md

✅ Lectura Cognitiva Completa

📊 Análisis del Documento:
- Total secciones: 15
- Conceptos identificados: 12
- Longitud promedio de resúmenes: 740 caracteres

📄 Salida guardada en: libro_resumen_cognitivo.json
```

---

## 🧪 Requisitos de Desarrollo y Testing

### **Soporte de Modo de Desarrollo**

**Características de Desarrollo Requeridas**:
- **Modo dry-run**: Habilitar testing sin llamadas API LLM
- **Aislamiento de componentes**: Capacidad de probar primera pasada y segunda pasada independientemente
- **Toggles de características cognitivas**: Habilitar/deshabilitar refinamiento y segunda pasada por separado
- **Comparación de rendimiento**: Comparar resultados de procesamiento cognitivo vs secuencial
- **Métricas de procesamiento**: Reporte claro de estadísticas de procesamiento cognitivo

**Requisitos de Configuración**:
- Todas las características cognitivas deben ser configurables vía variables de entorno
- Debe soportar testing incremental de características (habilitar solo refinamiento, o solo segunda pasada)
- Debe proporcionar defaults amigables para desarrollo para testing
- Testing comprehensivo de configuración de características cognitivas

### **Estrategia de Testing**

**Requisitos de Testing Funcional**:
- **Validación de refinamiento**: Verificar que refinamientos mejoran calidad de comprensión
- **Validación de enriquecimiento**: Verificar que segunda pasada añade contexto significativo
- **Testing de modelo dual**: Validar modelo rápido para primera pasada, modelo de calidad para segunda pasada
- **Demostración de beneficio cognitivo**: Mostrar diferencia clara entre enfoques

**Requisitos de Testing de Rendimiento**:
- **Uso de memoria**: Sin aumento significativo de memoria para características cognitivas básicas
- **Optimización de llamadas LLM**: Reutilización eficiente de contexto a través de pasadas
- **Escalabilidad**: Rendimiento debe permanecer aceptable para documentos de gran tamaño

**Requisitos de Aseguramiento de Calidad**:
- **Preservación de voz del autor**: Procesamiento cognitivo debe mantener fidelidad de contenido
- **Validación de coherencia**: Refinamientos y enriquecimientos deben mejorar coherencia
- **Testing de regresión**: Asegurar que características cognitivas no rompan funcionalidad existente
- **Manejo de casos extremos**: Manejar documentos donde refinamiento/enriquecimiento proporcionan valor mínimo

---

## 🎯 Fases de Desarrollo

### **Fundamentos: Modelo de Datos Cognitivos**

**Objetivos**:
- Implementar modelos de datos cognitivos completos
- Crear sistema de configuración de características cognitivas
- Establecer fundación para características cognitivas

**Entregables**:
- Modelo `SectionSummary` mejorado con seguimiento cognitivo
- Modelo `CognitiveKnowledge` actualizado con estadísticas de procesamiento
- `CognitiveConfig` extendido con toggles de características cognitivas
- Testing completo de características cognitivas

### **Primera Pasada: Refinamiento Progresivo**

**Objetivos**:
- Implementar capacidad de refinamiento en lectura progresiva
- Añadir detección de refinamiento y actualización de resúmenes
- Implementar detección de refinamiento eficiente

**Entregables**:
- `ProgressiveReader` mejorado con capacidad de refinamiento
- Implementación de algoritmo de detección de refinamiento
- Configuración de umbral de refinamiento
- Testing unitario para características de refinamiento

### **Segunda Pasada: Enriquecimiento Contextual**

**Objetivos**:
- Implementar capacidad de enriquecimiento con contexto global
- Añadir procesamiento de segunda pasada al flujo principal de lectura
- Integrar resultados de primera pasada y segunda pasada

**Entregables**:
- Implementación de componente `ContextualEnricher`
- Integración de segunda pasada en flujo principal de lectura
- Detección y seguimiento de enriquecimiento
- Testing completo de flujo de dos pasadas

### **Validación: Testing y Optimización**

**Objetivos**:
- Validar beneficios de procesamiento cognitivo con documentos reales
- Testing de rendimiento y optimización
- Creación de documentación y ejemplos

**Entregables**:
- Formatos de salida actualizados con metadatos cognitivos
- Benchmarking de rendimiento con configuraciones de modelo dual
- Testing de validación "3 pasos contra el sedentarismo"
- Documentación de usuario y ejemplos
- Release MVP v2.0

---

## 📈 Métricas de Éxito (Objetivos MVP)

### **Objetivos de Prueba de Concepto**
- ✅ **Demostrar diferencia cognitiva**: Diferencia clara entre lectura cognitiva y procesamiento fragmentado tradicional
- ✅ **Validación de refinamiento**: Mostrar ejemplos donde comprensión mejoró durante primera pasada  
- ✅ **Validación de enriquecimiento**: Mostrar ejemplos donde segunda pasada añadió valor
- ✅ **Test "3 pasos"**: Procesar exitosamente capítulos de muestra con enfoque cognitivo
- ✅ **Validación de modelo dual**: Demostrar beneficios de estrategia modelo rápido/calidad

### **Requisitos Técnicos**
- ✅ **API limpia**: Interfaz simple y enfocada para lectura cognitiva
- ✅ **Optimización de rendimiento**: Estrategia efectiva de modelo dual para balance velocidad/calidad
- ✅ **Eficiencia de memoria**: Procesamiento eficiente con múltiples configuraciones de modelo
- ✅ **Amigable para desarrollo**: Opciones comprehensivas de dry-run y configuración

### **Indicadores de Calidad**
- ✅ **Refinamientos coherentes**: Refinamientos deben mejorar calidad de resumen
- ✅ **Enriquecimientos valiosos**: Segunda pasada debe añadir contexto significativo
- ✅ **Preservación de voz del autor**: Mantener fidelidad al contenido original
- ✅ **Calidad clara del output**: Resúmenes y conceptos finales demuestran comprensión superior
- ✅ **Efectividad de modelos**: Modelo rápido habilita velocidad, modelo de calidad mejora profundidad

---

## 📚 Testing con Documento Real

### **Documento de Ejemplo para Validación**

El proyecto incluye una versión reducida del libro real "3 pasos contra el sedentarismo" en `examples/3 pasos contra el sedentarismo.md` para habilitar **testing realista** y **validación de calidad**.

#### **Estructura del Documento** (Contenido Real)
```
3 pasos contra el sedentarismo.md
├── Introducción al sedentarismo
│   ├── ¿Qué es el sedentarismo?
│   │   ├── De nómadas a sedentarios
│   │   ├── Enfermedades de la civilización
│   │   ├── En la especialización está la clave
│   │   ├── Nuestras células se adaptan
│   │   └── Conclusiones
├── Problemas comunes: limitaciones de la movilidad, dolor y estrés
│   ├── Sistema nervioso
│   ├── Movilidad  
│   └── Dolor
├── 3 pasos para salir del sedentarismo
│   ├── Caminar más
│   ├── Sentarse más en el suelo
│   ├── Colgarse más de las manos
│   ├── Paso extra: respiración
│   └── ¿Y ahora qué? Siguientes pasos
└── Conclusiones
```

#### **Beneficios Clave para Testing**

1. **🎯 Contenido Auténtico**: Voz y metodología real del autor
2. **🔬 Validación de Calidad**: Comparar procesamiento cognitivo vs. tradicional
3. **📊 Extracción de Conceptos**: Validar extracción de términos específicos del dominio
4. **🏗️ Testing de Jerarquía**: Estructura multinivel con relaciones lógicas
5. **⚡ Testing de Rendimiento**: Documento de tamaño apropiado para testing realista pero manejable

#### **Casos de Prueba Recomendados**

```python
# Caso de Prueba 1: Procesamiento Cognitivo Completo
test_file = "examples/3 pasos contra el sedentarismo.md"
result = cognitive_reader.process_document(
    file_path=test_file,
    enable_second_pass=True,
    enable_refinement=True
)

# Validar que se extraen conceptos auténticos
expected_concepts = [
    "sedentarismo", "vida_nomada", "movimiento_natural", 
    "tres_pasos", "dolor_cronico", "mapas_cerebrales"
]

# Caso de Prueba 2: Comparación de Calidad
traditional_chunks = chunk_processor.process(test_file)
cognitive_summaries = result.hierarchical_summaries

# Los resúmenes cognitivos deberían mostrar:
# ✅ Comprensión coherente de la metodología
# ✅ Progresión lógica de problemas a soluciones  
# ✅ Voz del autor y terminología específica preservada
# ✅ Conceptos conectados entre secciones
```

#### **Indicadores de Calidad a Validar**

- **📖 Resumen Coherente del Libro**: Debe capturar la metodología central y progresión
- **🔗 Conceptos Conectados**: La relación `sedentarismo` → `tres_pasos` debe ser clara
- **🎯 Terminología Precisa**: Términos específicos como "propiocepción", "nocicepción" 
- **📚 Voz Preservada**: Mantiene el tono científico pero accesible del autor
- **🧩 Jerarquía Lógica**: Flujo Introducción → Problemas → Soluciones → Conclusiones

---

## 🚀 Desarrollo Futuro (Post-MVP)

### **Características Cognitivas Avanzadas**
- **Lectura iterativa multi-pasada**: Extender más allá de 2 pasadas al procesamiento cognitivo de N pasadas
  - Número configurable de pasadas (3, 4, 5+ re-lecturas)
  - Cada pasada profundiza comprensión y refina conceptos iterativamente
  - Detección de rendimientos decrecientes para optimizar número de pasadas automáticamente
  - Estrategias de prompting específicas por pasada para refinamiento progresivo
  - Acumulación avanzada de contexto a través de múltiples iteraciones
- **Detección compleja de conceptos emergentes**: Patrones más sofisticados de emergencia de conceptos
- **Generación de grafo de conocimiento**: Exportar relaciones a bases de datos de grafos
- **Síntesis cognitiva multi-documento**: Leer a través de documentos relacionados
- **Estrategias avanzadas de refinamiento**: Disparadores de refinamiento más inteligentes

### **Integración Avanzada**
- **Detección de contradicciones**: Manejar inconsistencias inteligentemente  
- **Bucles de retroalimentación experta**: Incorporar refinamientos de expertos humanos
- **Estrategias cognitivas adaptativas**: Ajustar enfoque basado en tipo de documento
- **Optimización de rendimiento**: Caching avanzado y procesamiento paralelo

---

## 💡 Innovación Clave del MVP v2

**Lectura Cognitiva Mínima**: El primer sistema en implementar **proceso básico de lectura humana de dos pasadas** con:

1. ✅ **Progresiva + Refinamiento**: Primera pasada que puede actualizar comprensión mientras crece el contexto
2. ✅ **Enriquecimiento Global**: Segunda pasada que enriquece con contexto completo del documento  
3. ✅ **Resúmenes Integrados**: Output final que refleja comprensión profunda sin metadata de proceso
4. ✅ **Prueba de Concepto**: Demostrar diferencia clara de fragmentación basada en chunks

**MVP v2** prueba que **la lectura cognitiva funciona diferente** al procesamiento secuencial, estableciendo la fundación para características cognitivas más avanzadas en fases futuras.

---

*Esta especificación define el sistema mínimo viable de lectura cognitiva que demuestra evolución de comprensión similar a la humana mientras mantiene simplicidad e implementabilidad.*
