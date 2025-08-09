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

### **2. Metadatos Enriquecidos para Proyectos de IA**
   - Datos de entrenamiento que preservan evolución de comprensión
   - Información rica en contexto con trazabilidad de refinamiento  
   - Conocimiento estructurado de documentos con relaciones emergentes

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
   - **JSON básico**: Incluir qué resúmenes fueron refinados y por qué
   - **Markdown simple**: Mostrar anotaciones de evolución donde ocurrió refinamiento
   - **Comparación**: Mostrar claramente diferencia de salida secuencial v1

#### 5. **Esenciales de Desarrollo** (Para Testing)
   - **Modo dry-run**: Probar sin costos LLM
   - **Logging simple**: Rastrear qué fue refinado
   - **Configuración**: Habilitar/deshabilitar segunda pasada y refinamiento

### 🎯 **Criterios de Éxito para MVP v2**

- ✅ **Prueba de concepto**: Demostrar claramente resultados diferentes al procesamiento secuencial
- ✅ **Test "3 pasos"**: Procesar exitosamente el libro con enfoque cognitivo
- ✅ **Ejemplos de refinamiento**: Mostrar casos donde la comprensión evolucionó durante la lectura
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
    """Resumen de sección con seguimiento de procesamiento cognitivo"""
    section_id: str                            # Referencia a DocumentSection.id
    title: str                                 # Título de sección
    summary: str                               # Resumen final (después de todo procesamiento)
    key_concepts: List[str] = Field(default_factory=list)  # Conceptos clave identificados
    
    # Flags de procesamiento cognitivo
    was_refined: bool = False                  # True si se refinó durante primera pasada
    was_enriched: bool = False                 # True si se mejoró durante segunda pasada
    
    # Contexto opcional de refinamiento (implementación puede elegir nivel de detalle)
    refinement_reason: Optional[str] = None    # Por qué se refinó (si aplica)
    enrichment_details: Optional[str] = None   # Qué se añadió durante enriquecimiento

class CognitiveKnowledge(BaseModel):
    """Conocimiento completo extraído con procesamiento cognitivo"""
    # Identificación de documento
    document_title: str
    document_summary: str                      # Resumen final a nivel documento
    detected_language: LanguageCode
    
    # Estructura y contenido del documento
    sections: List[DocumentSection]            # Estructura jerárquica del documento
    section_summaries: Dict[str, SectionSummary]  # Mapeo ID Sección -> Resumen
    
    # Metadatos de procesamiento cognitivo
    processing_approach: str = "two_pass_cognitive"  # Método de procesamiento usado
    refinements_made: int = 0                  # Número de secciones refinadas
    second_pass_enrichments: int = 0           # Número de secciones enriquecidas
    
    # Metadatos estándar de procesamiento
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)

class CognitiveConfig(BaseModel):
    """Configuración para lectura cognitiva de documentos"""
    
    # Configuración LLM
    model_name: str = Field(default="qwen3:8b", description="Nombre del modelo LLM por defecto (usado cuando no se configuran modelos duales)")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperatura LLM")
    
    # Configuración de Modelo Dual - Simula patrones de lectura humana
    first_pass_model: Optional[str] = Field(default=None, description="Modelo rápido para primera pasada (lectura rápida)")
    second_pass_model: Optional[str] = Field(default=None, description="Modelo de calidad para segunda pasada (análisis cuidadoso)")
    first_pass_temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Temperatura para primera pasada")
    second_pass_temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Temperatura para segunda pasada")
    
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
            
            # Configuraciones de modelo dual (simula patrones de lectura humana)
            first_pass_model=os.getenv("COGNITIVE_READER_FIRST_PASS_MODEL"),  # None si no está configurado
            second_pass_model=os.getenv("COGNITIVE_READER_SECOND_PASS_MODEL"),  # None si no está configurado
            first_pass_temperature=float(os.getenv("COGNITIVE_READER_FIRST_PASS_TEMPERATURE", "0.3")) if os.getenv("COGNITIVE_READER_FIRST_PASS_TEMPERATURE") else None,
            second_pass_temperature=float(os.getenv("COGNITIVE_READER_SECOND_PASS_TEMPERATURE", "0.1")) if os.getenv("COGNITIVE_READER_SECOND_PASS_TEMPERATURE") else None,
            
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
    
    # Configuración de Modelo Dual (Simula Patrones de Lectura Humana)
    "COGNITIVE_READER_FIRST_PASS_MODEL": "Modelo rápido para primera pasada de lectura rápida (opcional)",
    "COGNITIVE_READER_SECOND_PASS_MODEL": "Modelo de calidad para segunda pasada de análisis cuidadoso (opcional)",
    "COGNITIVE_READER_FIRST_PASS_TEMPERATURE": "Temperatura para modelo de primera pasada (default: 0.3 si modelo configurado)",
    "COGNITIVE_READER_SECOND_PASS_TEMPERATURE": "Temperatura para modelo de segunda pasada (default: 0.1 si modelo configurado)",
    
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
├── StructureDetector (sin cambios desde v1)
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
- Proporcionar misma interfaz API que v1 para compatibilidad
- Rastrear y reportar métricas de procesamiento cognitivo

**Requisitos de Interfaz**:
- `read_document(file_path, config) -> CognitiveKnowledge`: Interfaz primaria (igual que v1)
- Debe soportar tanto modos cognitivo (dos pasadas) como secuencial (compatible v1)
- Debe proporcionar estadísticas de procesamiento cognitivo en resultados

#### **ProgressiveReader** (Mejorado)
**Propósito**: Ejecutar primera pasada con lectura progresiva y capacidad de refinamiento

**Responsabilidades**:
- Procesar secciones secuencialmente con contexto acumulado (igual que v1)
- Detectar cuando nuevo contexto cambia significativamente comprensión de secciones previas
- Actualizar resúmenes de secciones previas cuando se necesita refinamiento
- Rastrear eventos de refinamiento y razones
- Mantener acumulación de contexto a través del procesamiento de secciones

**Requisitos**:
- Debe ser configurable para habilitar/deshabilitar capacidad de refinamiento
- Debe mantener compatibilidad v1 cuando refinamiento está deshabilitado
- Debe proporcionar configuración de umbral de refinamiento
- Debe rastrear qué secciones fueron refinadas y por qué

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
- Crear síntesis jerárquica del documento (igual que v1)
- Incorporar metadatos de procesamiento cognitivo en resultados finales
- Notar qué secciones fueron sometidas a refinamiento o enriquecimiento
- Generar resumen de procesamiento cognitivo para salida

**Requisitos**:
- Debe mantener calidad y enfoque de síntesis v1
- Debe indicar claramente eventos de procesamiento cognitivo en salida
- Debe proporcionar resumen de beneficios de procesamiento cognitivo

---

## 🔄 Requisitos de Proceso Cognitivo

### **Flujo de Procesamiento de Dos Pasadas**

```
Entrada de Documento
    ↓
Detección de Estructura (igual que v1)
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

### **Requisitos de Primera Pasada**

**Requisitos Funcionales:**
- **Lectura Progresiva**: Procesar secciones secuencialmente con contexto acumulado de secciones previas
- **Acumulación de Contexto**: Construir contexto comprehensivo mientras progresa la lectura
- **Detección de Refinamiento**: Identificar cuando nueva información cambia significativamente comprensión de secciones previas
- **Actualizaciones de Resumen**: Actualizar resúmenes de secciones previas cuando evoluciona la comprensión
- **Seguimiento de Refinamiento**: Registrar qué resúmenes fueron refinados y por qué

**Requisitos Técnicos:**
- Debe mantener compatibilidad hacia atrás con lectura progresiva v1
- Umbral de refinamiento configurable vía parámetro `refinement_threshold`
- Refinamiento puede deshabilitarse vía configuración `enable_refinement`
- Debe rastrear número de refinamientos hechos para métricas

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

### **JSON Cognitivo Básico** (Diferencia mínima de v1)

```json
{
  "document_title": "3 Pasos Contra el Sedentarismo",
  "document_summary": "Resumen final enriquecido...",
  "detected_language": "es",
  "processing_approach": "two_pass_cognitive",
  
  "cognitive_processing": {
    "refinements_made": 3,
    "second_pass_enrichments": 5,
    "sections_refined": ["seccion_1", "seccion_3"]
  },
  
  "section_summaries": {
    "seccion_1": {
      "section_id": "seccion_1",
      "title": "Introducción al sedentarismo",
      "summary": "Resumen final después de ambas pasadas...",
      "key_concepts": ["sedentarismo", "entorno_sedentario", "salud_compleja"],
      "was_refined": true,
      "was_enriched": true
    },
    "seccion_2": {
      "section_id": "seccion_2", 
      "title": "Problemas comunes: limitaciones de la movilidad, dolor y estrés",
      "summary": "Resumen final después de ambas pasadas...",
      "key_concepts": ["movilidad", "dolor", "estres", "sistema_nervioso"],
      "was_refined": false,
      "was_enriched": true
    }
  },
  
  "processing_metadata": {
    "processing_time_seconds": 45.2,
    "total_sections": 15,
    "llm_calls_made": 32
  }
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

✅ Lectura Cognitiva Completa (Procesamiento de dos pasadas)

📊 Resumen de Procesamiento:
- Enfoque: Lectura cognitiva de dos pasadas  
- Primera pasada: Lectura progresiva + 3 refinamientos
- Segunda pasada: Enriquecimiento con contexto global + 5 enriquecimientos
- Total secciones: 15
- Tiempo de procesamiento: 45.2s

💡 Beneficios Cognitivos Detectados:
- 3 secciones tuvieron comprensión mejorada durante primera pasada
- 5 secciones ganaron contexto adicional durante segunda pasada  
- Metodología del autor preservada y clarificada

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
- Debe mantener compatibilidad v1 cuando características cognitivas están deshabilitadas

### **Estrategia de Testing**

**Requisitos de Testing Funcional**:
- **Validación de refinamiento**: Verificar que refinamientos mejoran calidad de comprensión
- **Validación de enriquecimiento**: Verificar que segunda pasada añade contexto significativo
- **Testing de compatibilidad**: Asegurar que modo v1 produce resultados equivalentes a v1
- **Demostración de beneficio cognitivo**: Mostrar diferencia clara entre enfoques

**Requisitos de Testing de Rendimiento**:
- **Tiempo de procesamiento**: Procesamiento de dos pasadas debe ser <2x tiempo de procesamiento secuencial
- **Uso de memoria**: Sin aumento significativo de memoria para características cognitivas básicas
- **Optimización de llamadas LLM**: Reutilización eficiente de contexto a través de pasadas
- **Escalabilidad**: Rendimiento debe permanecer aceptable para documentos hasta 300 páginas

**Requisitos de Aseguramiento de Calidad**:
- **Preservación de voz del autor**: Procesamiento cognitivo debe mantener fidelidad de contenido
- **Validación de coherencia**: Refinamientos y enriquecimientos deben mejorar coherencia
- **Testing de regresión**: Asegurar que características cognitivas no rompan funcionalidad existente
- **Manejo de casos extremos**: Manejar documentos donde refinamiento/enriquecimiento proporcionan valor mínimo

---

## 🎯 Fases de Desarrollo: v1 → v2

### **Fase 1: Mejora de Modelo de Datos (Semanas 1-2)**

**Objetivos**:
- Extender modelos de datos existentes para soportar metadatos de procesamiento cognitivo
- Mantener compatibilidad completa hacia atrás con v1
- Añadir opciones de configuración para características cognitivas

**Entregables**:
- Modelo `SectionSummary` mejorado con seguimiento cognitivo
- Modelo `CognitiveKnowledge` actualizado con estadísticas de procesamiento
- `CognitiveConfig` extendido con toggles de características cognitivas
- Validación de compatibilidad hacia atrás

### **Fase 2: Características Cognitivas de Primera Pasada (Semanas 3-4)**

**Objetivos**:
- Implementar capacidad de refinamiento en lectura progresiva
- Añadir detección de refinamiento y actualización de resúmenes
- Mantener modo de compatibilidad v1

**Entregables**:
- `ProgressiveReader` mejorado con capacidad de refinamiento
- Implementación de algoritmo de detección de refinamiento
- Configuración de umbral de refinamiento
- Testing unitario para características de refinamiento

### **Fase 3: Implementación de Segunda Pasada (Semanas 5-6)**

**Objetivos**:
- Implementar capacidad de enriquecimiento con contexto global
- Añadir procesamiento de segunda pasada al flujo principal de lectura
- Integrar resultados de primera pasada y segunda pasada

**Entregables**:
- Implementación de componente `ContextualEnricher`
- Integración de segunda pasada en flujo principal de lectura
- Detección y seguimiento de enriquecimiento
- Testing completo de flujo de dos pasadas

### **Fase 4: Integración y Validación (Semanas 7-8)**

**Objetivos**:
- Validar beneficios de procesamiento cognitivo con documentos reales
- Testing de rendimiento y optimización
- Creación de documentación y ejemplos

**Entregables**:
- Formatos de salida actualizados con metadatos cognitivos
- Benchmarking de rendimiento vs v1
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
- ✅ **Seguimiento claro de evolución**: Comparaciones simples antes/después muestran valor
- ✅ **Efectividad de modelos**: Modelo rápido habilita velocidad, modelo de calidad mejora profundidad

---

## 🚀 Desarrollo Futuro (Post-MVP)

### **Fase 2: Características Cognitivas Mejoradas**
- **Detección compleja de conceptos emergentes**: Patrones más sofisticados de emergencia de conceptos
- **Generación de grafo de conocimiento**: Exportar relaciones a bases de datos de grafos
- **Síntesis cognitiva multi-documento**: Leer a través de documentos relacionados
- **Estrategias avanzadas de refinamiento**: Disparadores de refinamiento más inteligentes

### **Fase 3: Integración Avanzada**
- **Detección de contradicciones**: Manejar inconsistencias inteligentemente  
- **Bucles de retroalimentación experta**: Incorporar refinamientos de expertos humanos
- **Estrategias cognitivas adaptativas**: Ajustar enfoque basado en tipo de documento
- **Optimización de rendimiento**: Caching avanzado y procesamiento paralelo

---

## 💡 Innovación Clave del MVP v2

**Lectura Cognitiva Mínima**: El primer sistema en implementar **proceso básico de lectura humana de dos pasadas** con:

1. ✅ **Progresiva + Refinamiento**: Primera pasada que puede actualizar comprensión mientras crece el contexto
2. ✅ **Enriquecimiento Global**: Segunda pasada que enriquece con contexto completo del documento  
3. ✅ **Seguimiento Simple de Evolución**: Seguimiento básico antes/después de cambios de comprensión
4. ✅ **Prueba de Concepto**: Demostrar diferencia clara de fragmentación basada en chunks

**MVP v2** prueba que **la lectura cognitiva funciona diferente** al procesamiento secuencial, estableciendo la fundación para características cognitivas más avanzadas en fases futuras.

---

*Esta especificación define el sistema mínimo viable de lectura cognitiva que demuestra evolución de comprensión similar a la humana mientras mantiene simplicidad e implementabilidad.*
