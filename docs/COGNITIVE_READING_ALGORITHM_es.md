# Algoritmo de Lectura Cognitiva

## Descripción General

El Lector Cognitivo de Documentos implementa un proceso de lectura que simula los patrones cognitivos humanos a través de procesamiento secuencial con contexto acumulativo. El sistema puede operar en modo de pasada única o múltiples pasadas, manteniendo siempre el principio de autoridad del texto fuente.

## Ejemplo de Estructura del Documento

Usando `examples/sample_document.md` como referencia:

> **📝 Nota**: El documento de ejemplo presenta "La teoría de la conciencia cristalina de Aethelgard" - una **teoría científica completamente ficticia** creada específicamente para probar las capacidades de lectura cognitiva. Contiene contenido semántico novedoso no presente en los datos de entrenamiento de LLM y redefine deliberadamente conceptos existentes para evaluar cómo el sistema procesa información nueva vs. conocimiento pre-entrenado.

```
📄 La teoría de la conciencia cristalina de Aethelgard (Padre con contenido)
├── 📖 Principios fundamentales (Padre con contenido)
│   ├── 🔹 La frecuencia resonante primordial (Hoja)
│   └── 🔹 La refracción cognitiva (Hoja)
├── 📁 El entramado somático (Padre sin contenido)
│   ├── 🔹 La estructura del entramado (Hoja)
│   └── 🔹 La resonancia empática: una redefinición (Hoja)
└── 📖 Aplicaciones y paradojas (Padre con contenido)
    ├── 🔹 El concepto de la cristalización del yo (Hoja)
    └── 🔹 La paradoja del observador disonante (Hoja)
```

**Patrones Identificados:**
- **📖 Padre con contenido**: Tiene texto introductorio propio + secciones hijas
- **📁 Padre sin contenido**: Solo organiza secciones hijas, requiere síntesis diferida
- **🔹 Secciones hoja**: Sin hijos, contienen contenido específico

---

## Algoritmo Secuencial con Contexto Acumulativo

### Principios Fundamentales

El algoritmo procesa las secciones en **orden del documento** (secuencial top-down), manteniendo contexto acumulativo y aplicando el **principio de autoridad del texto fuente**.

```
PARA cada documento:
    1. DETECTAR estructura jerárquica
    2. ORDENAR secciones por secuencia del documento
    3. PROCESAR cada sección con contexto acumulativo
    4. ACTUALIZAR incrementalmente niveles superiores
    5. SINTETIZAR padres sin contenido al final
```

### Algoritmo Detallado

```
PARA cada sección en orden del documento:
    
    1. CONSTRUIR contexto acumulativo:
       - Resúmenes de todos los padres
       - Resúmenes de hermanos procesados previamente
    
    SI es padre CON contenido:
        2. PROCESAR texto propio con contexto → generar resumen
        3. ACTUALIZAR incrementalmente niveles superiores
        
    SI es sección hoja:
        2. PROCESAR contenido con contexto acumulativo → generar resumen
        3. ACTUALIZAR incrementalmente padre inmediato
        4. PROPAGAR actualizaciones hacia niveles superiores
        
    SI es padre SIN contenido:
        2. DIFERIR procesamiento hasta completar todos los hijos
        3. SINTETIZAR desde resúmenes de hijos + contexto de padres
```

### Ejemplo Práctico: Procesamiento de `sample_document.md`

**1. Procesar "Cognitive Document Reader Example" (Nivel 1, Padre CON contenido)**
- Sin contexto previo (es la raíz)
- Procesar su texto introductorio → `resumen_raíz_v1`

**2. Procesar "Principios fundamentales" (Nivel 2, Padre CON contenido)**
- Contexto: `resumen_raíz_v1`
- Procesar su texto → `resumen_principios_v1`
- Actualizar raíz: `resumen_raíz_v1 + resumen_intro_v1` → `resumen_raíz_v2`

**3. Procesar "Purpose" (Nivel 3, Hoja)**
- Contexto: `resumen_raíz_v2 + resumen_intro_v1`
- Procesar contenido → `resumen_purpose`
- Actualizar "Introduction": `resumen_intro_v1 + resumen_purpose` → `resumen_intro_final`
- Actualizar raíz: `resumen_raíz_v2 + resumen_intro_final` → `resumen_raíz_v3`

**4. Procesar "Key Features" (Nivel 2, Padre SIN contenido)**
- Diferir hasta procesar todos sus hijos

**5. Procesar "1. Document Processing" (Nivel 3, Hoja)**
- Contexto: `resumen_raíz_v3` (Key Features no tiene resumen aún)
- Procesar contenido → `resumen_doc_proc`

**6. Procesar "2. Language Detection" (Nivel 3, Hoja)**
- Contexto: `resumen_raíz_v3 + resumen_doc_proc`
- Procesar contenido → `resumen_lang_det`

**7. Procesar "3. Structured Output" (Nivel 3, Hoja)**
- Contexto: `resumen_raíz_v3 + resumen_doc_proc + resumen_lang_det`
- Procesar contenido → `resumen_struct_out`

**8. Sintetizar "Key Features" (Síntesis Diferida)**
- Contexto de padres: `resumen_raíz_v3`
- Sintetizar desde hijos: `resumen_doc_proc + resumen_lang_det + resumen_struct_out` → `resumen_key_features`
- Actualizar raíz: `resumen_raíz_v3 + resumen_key_features` → `resumen_raíz_v4`

**9-11. Procesar "Technical Architecture" y sus hijos**
- Sigue el mismo patrón que "Introduction"

**12. Procesar "Conclusion" (Nivel 2, Hoja)**
- Contexto: `resumen_raíz_v5` (versión más actualizada)
- Actualización final: `resumen_raíz_v5 + resumen_conclusion` → `resumen_raíz_final`

---

## Procesamiento Multi-Pasada

### Arquitectura de Múltiples Pasadas

El sistema puede ejecutar múltiples pasadas del mismo algoritmo secuencial, enriqueciendo progresivamente el contexto:

**Pasada 1:** Algoritmo secuencial con contexto básico (padres + hermanos previos)
**Pasada 2+:** Mismo algoritmo secuencial con contexto enriquecido

### Contexto Enriquecido en Pasadas Posteriores

```
PARA cada sección en pasadas posteriores:
    
    1. CONSTRUIR contexto enriquecido:
       - Resúmenes actuales de padres (pasada actual)
       - Resumen previo del mismo nodo (pasada anterior)
       - Glosario de conceptos clave con definiciones
    
    2. APLICAR principio de autoridad:
       - TEXTO FUENTE = autoridad suprema
       - CONTEXTO ENRIQUECIDO = información de apoyo
    
    3. PROCESAR con algoritmo secuencial idéntico
```

### Ejemplo: "Purpose" en Segunda Pasada

**Contexto Enriquecido:**
- **Padres actuales**: `resumen_raíz_v2 + resumen_intro_v1` (segunda pasada)
- **Resumen previo**: `resumen_purpose_primera_pasada`
- **Conceptos**: `"progressive reading": "Técnica de procesamiento...", "hierarchical synthesis": "..."`

**Procesamiento:**
```
CONTEXTO (información de apoyo):
- Resumen Raíz: [comprensión actual de la teoría de Aethelgard]
- Resumen Principios fundamentales: [comprensión actual de la sección padre]
- Resumen Previo: [comprensión de primera pasada]
- Conceptos: [glosario con definiciones incluyendo frecuencia_resonante_primordial, refracción_cognitiva, etc.]

TEXTO FUENTE (autoridad suprema):
[contenido original de la sección "Purpose"]

El algoritmo genera un resumen refinado que integra:
- Fidelidad completa al texto fuente
- Enriquecimiento contextual de pasadas previas
- Marcos conceptuales del glosario
```

---

## Principio de Autoridad del Texto

### Jerarquía de Autoridad

```
1. 🥇 TEXTO FUENTE ORIGINAL    → Autoridad suprema, siempre prevalece
2. 🥈 CONTEXTO ACUMULATIVO     → Resúmenes de padres y hermanos previos  
3. 🥉 CONOCIMIENTO PREVIO      → Resúmenes de pasadas anteriores
4. 📚 GLOSARIO CONCEPTUAL      → Definiciones de apoyo
```

### Aplicación del Principio

- **Conflicto texto vs contexto**: El texto fuente siempre gana
- **Propósito del contexto**: Enriquecer comprensión, no contradecir
- **Fidelidad garantizada**: Los resúmenes reflejan fielmente el contenido original
- **Corrección automática**: Pasadas posteriores corrigen malentendidos previos basándose en el texto

---

## Características del Algoritmo

### Ventajas del Procesamiento Secuencial

- **Contexto Progresivo**: Cada sección se beneficia de toda la comprensión acumulada
- **Orden Natural**: Sigue la secuencia lógica del documento como un lector humano
- **Actualizaciones Coherentes**: Los niveles superiores evolucionan incrementalmente
- **Integración Semántica**: Los hermanos anteriores enriquecen el contexto de los siguientes

### Gestión de Complejidad

- **Síntesis Diferida**: Los padres sin contenido esperan a que se procesen todos sus hijos
- **Contexto Truncado**: Se gestiona la longitud del contexto para mantenerse dentro de límites
- **Glosario Dinámico**: Se generan conceptos clave que enriquecen pasadas posteriores
- **Autoridad Textual**: El principio de autoridad previene deriva semántica

---

## Resumen

El Algoritmo de Lectura Cognitiva simula la comprensión humana de documentos mediante:

1. **Procesamiento Secuencial**: Sigue el orden natural del documento
2. **Contexto Acumulativo**: Cada sección recibe contexto de padres y hermanos previos
3. **Actualizaciones Incrementales**: Los niveles superiores evolucionan conforme se procesan hijos
4. **Principio de Autoridad**: El texto fuente prevalece sobre cualquier contexto
5. **Síntesis Adaptativa**: Estrategias específicas para padres con/sin contenido
6. **Refinamiento Multi-Pasada**: Enriquecimiento progresivo manteniendo fidelidad textual

Este enfoque produce resúmenes que mantienen la riqueza semántica del documento original, preservan la estructura jerárquica del autor, y proporcionan contexto adecuado tanto para lectura humana como para procesamiento de sistemas de IA.