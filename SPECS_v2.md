# Cognitive Document Reader - Technical Specifications v2.0

> **Version 2.0**: Architectural redesign based on authentic human cognitive reading process detailed in `MOTIVATION.md`

---

## 📚 Context: Why Version 2.0?

**Version 2.0** represents a fundamental architectural shift from the original sequential processing approach (v1.x) to implement the authentic **two-pass cognitive reading process** described in detail in [`MOTIVATION.md`](./MOTIVATION.md).

### **The Problem with v1.x**
The original specification (preserved in git tag `v0.1.1`) implemented only:
- ✅ Sequential progressive reading  
- ✅ Basic hierarchical synthesis
- ❌ **Missing**: Continuous refinement during reading
- ❌ **Missing**: Second pass contextual enrichment  
- ❌ **Missing**: Evolutionary understanding

### **The Cognitive Gap**
As detailed in `MOTIVATION.md`, human reading of complex documents involves:
1. **First pass**: Progressive reading + **continuous refinement** of understanding
2. **Second pass**: Re-reading with **global context** to enrich comprehension

This process is **essential** for the project's core goal: generating high-quality datasets for the "3 pasos contra el sedentarismo" book that preserve the author's voice and methodology.

### **v2.0 Solution**
Implement **cognitive reading from scratch** with the absolute minimum to demonstrate cognitive reading vs. fragmented chunks:
- ✅ Two-pass reading (progressive + simple enrichment)
- ✅ Basic summary refinement when understanding significantly changes
- ✅ Accumulated context instead of isolated chunks
- ✅ Simple second-pass enrichment with global context
- ✅ Clean, simple architecture focused on cognitive features

**Everything else** (emergence detection, complex refinement tracking, knowledge graphs) remains in future phases.

---

## 🧠 Purpose and Vision

**Cognitive Document Reader v2** is a Python library that authentically simulates human-like document reading through **two-pass cognitive processing** with **evolutionary understanding**. This version fully implements the cognitive reading approach detailed in `MOTIVATION.md`.

---

## 🛠️ Technology Stack & Development Standards

### **Core Technology Stack**

**Language & Runtime:**
- **Python 3.12+**: Modern Python features with excellent type support
- **Async/Await**: Prefer async programming for I/O bound operations

**Development Tools:**
- **uv**: Dependency management and project setup (replaces Poetry, pip, venv)
- **ruff**: Code linting and formatting (replaces black, isort, flake8)
- **mypy**: Static type checking with strict configuration
- **pytest**: Testing framework with async support

**Domain Libraries:**
- **pydantic v2+**: Data validation and configuration management
- **docling**: Universal document parsing (current stable: v2.43.0+)
- **aiohttp**: Async HTTP client for LLM communications
- **click**: Command-line interface framework
- **langdetect**: Language detection capabilities

### **Code Quality Standards (Mandatory)**

**Type Safety:**
- **ALL** functions, methods, and class members MUST have type annotations
- Use `from __future__ import annotations` for forward references
- Prefer specific types over generic (`List[str]` over `List[Any]`)

**Documentation:**
- **ALL** public functions, methods, and classes MUST have Google-style docstrings
- Include purpose, parameters, return values, exceptions, and usage examples
- Code comments in English only

**Exception Handling:**
- Use specific exception types, never bare `except:`
- Create custom exception classes for domain-specific errors
- Provide informative error messages without exposing sensitive data

### **Architecture & Design Principles**

**Design Patterns:**
- **Single Responsibility**: Each module/class has one clear responsibility
- **Composition over Inheritance**: Favor composition and dependency injection
- **Explicit over Implicit**: Avoid magic values, be explicit about dependencies
- **Async-First**: Design APIs to be async-compatible from the start

**Configuration Management:**
- **Environment-driven**: All configuration via environment variables
- **Pydantic validation**: Use Pydantic models for configuration validation
- **Development-friendly**: Include dry-run modes and mock responses
- **No hardcoded values**: Everything configurable

**Testing Philosophy:**
- **90% coverage minimum**: Focus on critical paths and error handling
- **Mock external dependencies**: LLM calls, file I/O, network requests
- **Fast and deterministic**: Tests should run quickly and consistently
- **Test both success and failure scenarios**

### **Project Structure Standards**

**Directory Organization:**
```
cognitive-document-reader/
├── src/cognitive_reader/         # Main source code package
│   ├── __init__.py               # Public API exports
│   ├── models/                   # Pydantic data models
│   ├── core/                     # Core cognitive reading logic  
│   ├── parsers/                  # Document parsing components
│   ├── llm/                      # LLM integration
│   ├── utils/                    # Utility functions
│   └── cli/                      # Command-line interface
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data and fixtures
├── examples/                     # Usage examples and demos
├── pyproject.toml                # Project configuration (uv format)
├── README.md                     # English documentation
└── .env.example                  # Environment configuration template
```

**File Naming Conventions:**
- **Snake_case**: All Python files and directories
- **Clear purpose**: Filenames should indicate functionality
- **No abbreviations**: Prefer `progressive_reader.py` over `prog_reader.py`
- **Test mirrors**: Test files mirror source structure (`test_progressive_reader.py`)

**Module Responsibilities:**
- **models/**: Only Pydantic models and data structures
- **core/**: Business logic and cognitive processing algorithms  
- **parsers/**: Document format handling and structure detection
- **llm/**: LLM communication and prompt management
- **utils/**: Pure functions with no external dependencies
- **cli/**: Command-line interface and user interaction

---

## 🎯 Primary Use Cases

### **1. RAG (Retrieval Augmented Generation) Optimization**
   - **Hierarchical summaries as semantic chunks**: Replace arbitrary text chunks with cognitive-enhanced summaries
   - **Concept definitions as specialized chunks**: Add domain-specific concepts for precise retrieval
   - **Contextual coherence**: Maintain author's voice and methodology vs. fragmented understanding
   - **Direct integration**: Summaries ready for embedding and vector database ingestion

### **2. Fine-tuning Dataset Generation**
   - **Hierarchical context building**: Book → Chapter → Section summaries for coherent training
   - **Consistent terminology**: Cognitive-refined concept definitions for domain accuracy
   - **Rich training examples**: Use summary hierarchy to generate contextually coherent Q&A pairs
   - **Quality validation**: Use concept definitions to validate synthetic data consistency

### **3. High-Quality Document Understanding**
   - **Two-pass cognitive processing**: Summaries that evolve during reading like human comprehension
   - **Emergent insights**: Understanding that emerges only with complete document context
   - **Author voice preservation**: Maintain original methodology and tone

### 🧠 **Core Innovation: Two-Pass Cognitive Processing**

Unlike traditional document processors that fragment content, **Cognitive Document Reader v2** implements the complete human reading process:

#### 🔄 **First Pass: Progressive Construction + Continuous Refinement**
1. **Sequential progressive reading** with context accumulation
2. **Evolutionary summaries** that update as new information is encountered
3. **Hierarchical refinement** where subsections update parent sections
4. **Emergent concept detection** as ideas become clear with context
5. **Fast processing** using rapid model to simulate human "quick first read"

#### 🔍 **Second Pass: Contextual Enrichment**
1. **Informed re-reading** with complete document understanding
2. **Deep connection identification** between previously separate concepts
3. **Relationship enhancement** that only becomes visible with full context
4. **Final synthesis** integrating all knowledge coherently
5. **Quality processing** using careful model to simulate human "thoughtful analysis"

### 🧠 **Dual Model Strategy: Simulating Human Reading Patterns**

Human reading naturally involves two different cognitive approaches:
- **Rapid scan**: Quick overview to get the general idea (first pass)
- **Careful analysis**: Detailed understanding with full context (second pass)

The **dual model configuration** mirrors this:
- **Fast model (first pass)**: Optimized for speed, basic comprehension, rapid refinement detection
- **Quality model (second pass)**: Optimized for depth, nuanced understanding, sophisticated enrichment

This approach **improves both performance and accuracy** by matching computational resources to cognitive requirements.

---

## 🏗️ Design Principles v2

- **Authentic Cognitive Simulation**: True two-pass reading process mimicking human cognition
- **Evolutionary Understanding**: Knowledge that changes and improves during processing
- **Hierarchical Refinement**: Continuous updating from subsections to global understanding
- **Emergent Intelligence**: Concepts and relationships that appear with accumulated context
- **Refinement Traceability**: Complete history of how understanding evolved
- **Minimize LLM Calls**: Intelligent batching and context reuse across both passes
- **Quality Preservation**: Maintain fidelity to original author's voice and methodology

---

## 🚀 MVP v2.0 - Minimal Cognitive Reading

### **Core Goal**: Demonstrate cognitive reading vs. fragmented chunks with minimum complexity

**MVP Goal**: **Minimal** two-pass cognitive reading to prove the concept with clean, focused implementation

### ✅ **MVP v2 Core Features** (Absolute Minimum)

#### 1. **Two-Pass Reading** (Essential)
   - **First Pass**: Progressive reading with accumulated context (like human first reading)
   - **Second Pass**: Re-read with complete context to enrich understanding (like human second reading)
   - **That's it**: Prove it works differently than chunk-based systems

#### 2. **Basic Refinement** (When Obviously Needed)
   - **Simple trigger**: If new section significantly changes understanding of previous section, update it
   - **No complex tracking**: Just "before" and "after" summaries
   - **Manual threshold**: Simple confidence-based trigger

#### 3. **Accumulated Context** (Core Difference)
   - **Progressive context**: Each section processed with all previous context
   - **Global enrichment**: Second pass uses complete document understanding
   - **No chunks**: Avoid fragmented understanding

#### 4. **Minimal Output** (Prove Concept)
   - **Clean JSON**: Hierarchical summaries and refined concepts without process metadata
   - **Evident quality**: Output should clearly show its advantages (coherent summaries, defined concepts, logical hierarchy)
   - **Value-focused**: Only information useful for RAG/Fine-tuning, no internal process noise

#### 5. **Development Essentials** (For Testing)
   - **Dry-run mode**: Test without LLM costs
   - **Internal logging**: Only for debugging during development
   - **Configuration**: Enable/disable second pass and refinement

### 🎯 **Success Criteria for MVP v2**

- ✅ **Proof of concept**: Output that evidences superior quality (coherent summaries vs. fragmented chunks)
- ✅ **"3 pasos" test**: Successfully process the book with cognitive approach
- ✅ **Cognitive quality**: Summaries that show deep and integrated understanding of content
- ✅ **Context benefit**: Demonstrate value of accumulated context vs. fragments

---

## 🗃️ Data Models v2

### **Core Principle**: Define clear contracts while allowing implementation flexibility

```python
from __future__ import annotations
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class LanguageCode(str, Enum):
    """Supported languages for document processing"""
    AUTO = "auto"  # Automatic detection
    EN = "en"      # English
    ES = "es"      # Spanish

class DocumentSection(BaseModel):
    """Document section with hierarchical structure"""
    model_config = ConfigDict(frozen=True)
    
    id: str                                    # Unique section identifier
    title: str                                 # Section title (cleaned)
    content: str                               # Section text content
    level: int                                 # Hierarchy level (0=document, 1=chapter, 2=section, etc.)
    parent_id: Optional[str] = None            # Parent section ID (None for root)
    children_ids: List[str] = Field(default_factory=list)  # Child section IDs
    order_index: int                           # Order within parent

class SectionSummary(BaseModel):
    """Section summary optimized for RAG chunks"""
    section_id: str                            # Reference to DocumentSection.id
    title: str                                 # Section title
    summary: str                               # Cognitive-enhanced summary (optimized for RAG chunks)
    key_concepts: List[str] = Field(default_factory=list)  # Key concept IDs relevant to this section
    summary_length: int                        # Length of summary in characters

class ConceptDefinition(BaseModel):
    """Key concept with cognitive-refined definition"""
    concept_id: str                            # Unique identifier (e.g., "sedentarismo", "movimiento_natural")
    name: str                                  # Human-readable name of the concept
    definition: str                            # Cognitive-refined definition
    first_mentioned_in: str                    # Section ID where this concept was first identified
    relevant_sections: List[str] = Field(default_factory=list)  # Section IDs where concept is relevant

class CognitiveKnowledge(BaseModel):
    """Complete knowledge extracted with cognitive processing for RAG/Fine-tuning"""
    # Document identification
    document_title: str
    document_summary: str                      # Cognitive-enhanced document-level summary
    detected_language: LanguageCode
    
    # Hierarchical summaries optimized for RAG chunks
    hierarchical_summaries: Dict[str, SectionSummary]  # Section ID -> Summary mapping
    
    # Key concepts with cognitive-refined definitions
    concepts: Dict[str, ConceptDefinition]     # Concept ID -> Definition mapping
    
    # Hierarchy navigation indices
    hierarchy_index: Dict[str, List[str]] = Field(default_factory=dict)  # Level -> Section IDs
    parent_child_map: Dict[str, List[str]] = Field(default_factory=dict)  # Parent ID -> Child IDs
    
    # Summary statistics
    total_sections: int = 0
    avg_summary_length: int = 0
    total_concepts: int = 0
    
    # Optional processing metadata
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)

class CognitiveConfig(BaseModel):
    """Configuration for cognitive document reading"""
    
    # LLM Configuration
    model_name: str = Field(default="qwen3:8b", description="Default LLM model name (used when dual models not configured)")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="LLM temperature")
    
    # Dual Model Configuration - Simulates human reading patterns
    # Multi-pass configuration (extensible design)
    max_passes: int = Field(default=2, ge=1, le=10, description="Maximum number of cognitive passes")
    convergence_threshold: float = Field(default=0.1, ge=0.01, le=1.0, description="Threshold to detect when additional passes add minimal value")
    
    # Dual model strategy: fast first scan + quality processing  
    enable_fast_first_pass: bool = Field(default=True, description="Use fast model for initial scan")
    fast_pass_model: Optional[str] = Field(default="llama3.1:8b", description="Fast model for initial document scan")
    main_model: Optional[str] = Field(default="qwen3:8b", description="Quality model for detailed cognitive processing")
    
    # Temperature settings
    fast_pass_temperature: Optional[float] = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for fast scan")
    main_pass_temperature: Optional[float] = Field(default=0.3, ge=0.0, le=2.0, description="Temperature for quality processing")

### **🔧 Extensible Multi-Pass Design Philosophy**

The MVP implements **2-pass reading** but is architecturally prepared for **N-pass extension**:

```python
# MVP Usage (2 passes) - Ready today
config = CognitiveConfig(
    max_passes=2,
    fast_pass_model="llama3.1:8b",    # Quick initial scan
    main_model="qwen3:8b"          # Quality cognitive processing
)

# Future N-pass Usage (same API) - Seamless extension
config = CognitiveConfig(
    max_passes=4,                     # Configurable depth
    convergence_threshold=0.05,       # Auto-stop optimization  
    main_model="qwen3:8b"          # Same model, richer context each pass
)
```

#### **Key Design Principles**

1. **📖 Same "Brain", Better Knowledge**: Multiple passes use the **same model** with **progressively richer context**
2. **🔄 Context Accumulation**: Each pass provides accumulated summaries, concepts, and insights to the next
3. **🏆 Original Text Authority**: **Source text always takes precedence** over previous summaries/context when conflicts arise
4. **⚡ Smart Speed/Quality Balance**: Fast scan (`llama3.1:8b`) + Quality processing (`qwen3:8b`) 
5. **🎯 Convergence Detection**: Future auto-stop when additional passes add minimal value
6. **🏗️ API Consistency**: Same interface scales from 2-pass MVP to N-pass advanced features

#### **🏆 Source Text Authority Principle**

**CRITICAL**: When processing each section, the **original text** is the ultimate authority:

```python
# Prompting hierarchy (highest to lowest authority)
AUTHORITY_HIERARCHY = [
    "Original text content",           # 🥇 Supreme authority - always wins
    "Previous refined summaries",      # 🥈 Contextual guidance  
    "Discovered concepts",             # 🥉 Supporting information
    "Global document understanding"    # 📚 Background context
]
```

**Conflict Resolution Strategy**:
- ✅ **Text contradicts summary** → Update summary to match text
- ✅ **Text adds new nuance** → Enrich summary with text's perspective  
- ✅ **Text reveals error in concept** → Refine concept definition
- ❌ **Never** modify text interpretation to fit previous context

#### **💭 Authority-Aware Prompting Strategy**

**Example Prompt Structure** (enforcing text authority):

```
CONTEXT (for background only):
- Book Summary: [previous understanding]
- Concept Definitions: [discovered so far]  
- Parent Section Summary: [if applicable]

SOURCE TEXT (AUTHORITATIVE):
[actual section content to process]

INSTRUCTIONS:
1. Read the SOURCE TEXT carefully - this is your PRIMARY source of truth
2. Use CONTEXT only as background information to inform your understanding
3. If the SOURCE TEXT contradicts any CONTEXT information:
   - Trust the SOURCE TEXT completely
   - Update your understanding based on the SOURCE TEXT
   - Note discrepancies for refinement
4. Generate summary that reflects the SOURCE TEXT accurately
5. Identify concepts mentioned in SOURCE TEXT (not just from context)

CRITICAL: The SOURCE TEXT is always correct. Previous summaries may contain errors or incomplete understanding.
```

#### **📝 Practical Example: Text Authority in Action**

**Scenario**: Processing chapter 3 of "3 pasos contra el sedentarismo"

```python
# Previous context (may contain errors)
previous_summary = {
    "sedentarismo": "Lack of physical exercise in modern life"  # ← Incomplete understanding
}

# Current section text (authoritative)
source_text = """
El sedentarismo, en su sentido más profundo, no es simplemente pasar mucho tiempo sentado. 
Es un concepto arraigado en la falta de movimiento variado y en la especialización de las posturas.
"""

# Cognitive processing result (text authority applied)
refined_understanding = {
    "sedentarismo": "Estado crónico de inactividad física que resulta de la falta de movimiento variado y especialización de posturas, no simplemente pasar tiempo sentado"  # ← Corrected by source text
}
```

**Key Insight**: The source text **corrected** the previous incomplete definition, demonstrating how text authority ensures evolving accuracy.

---

## 🔄 **Core Purpose: Error Correction & Refinement**

### **🎯 Primary Justification for Multi-Pass Design**

The **main reason** for second, third, and N-th passes is **systematic error correction and knowledge refinement**:

#### **🔍 What Gets Corrected/Refined**

1. **📝 Summary Accuracy**
   - **Initial errors**: First-pass summaries may miss key points or misinterpret concepts
   - **Progressive refinement**: Each pass corrects and enriches understanding
   - **Global coherence**: Later sections provide context that clarifies earlier misunderstandings

2. **💡 Concept Definitions**
   - **Initial approximations**: First encounters with concepts yield partial definitions
   - **Iterative precision**: Subsequent passes refine definitions with richer context
   - **Cross-reference validation**: Concepts mentioned across sections get more accurate definitions

3. **🔗 Relationship Understanding** 
   - **Missing connections**: Single-pass processing misses concept relationships
   - **Emergent patterns**: Multi-pass reveals how concepts relate across the document
   - **Hierarchical clarity**: Parent-child concept relationships become apparent

#### **📈 Correction Examples from Real Usage**

```python
# Pass 1: Initial understanding (often incomplete/incorrect)
first_pass_concept = {
    "sedentarismo": "Lack of physical exercise"  # ← Surface-level understanding
}

# Pass 2: Corrected with global context
second_pass_concept = {
    "sedentarismo": "Estado crónico de inactividad física caracterizado por falta de movimiento variado y especialización de posturas, no simplemente ausencia de ejercicio"  # ← Deep, accurate understanding
}

# Pass 3: Further refined with cross-references
third_pass_concept = {
    "sedentarismo": "Estado crónico de inactividad física que resulta de entornos modernos que eliminan movimiento variado, causando adaptaciones corporales problemáticas mediante especialización postural. Se diferencia de la simple falta de ejercicio por su enfoque en variedad de movimiento vs. intensidad."  # ← Comprehensive, nuanced understanding
}
```

#### **✅ Success Indicators for Refinement**

- **Concept evolution**: Definitions become more precise and comprehensive across passes
- **Error detection**: System identifies and corrects previous misunderstandings  
- **Coherence improvement**: Summaries align better with document's overall message
- **Relationship clarity**: Connections between concepts become explicit and accurate
    
    # Document Processing
    chunk_size: int = Field(default=1000, gt=100, description="Text chunk size for processing")
    chunk_overlap: int = Field(default=200, ge=0, description="Overlap between chunks")
    context_window: int = Field(default=4096, gt=0, description="LLM context window limit")
    
    # Performance Settings
    timeout_seconds: int = Field(default=120, gt=0, description="Request timeout")
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    document_language: LanguageCode = Field(default=LanguageCode.AUTO, description="Document language")
    
    # Cognitive Features
    enable_second_pass: bool = Field(default=True, description="Enable second pass enrichment")
    enable_refinement: bool = Field(default=True, description="Enable first pass refinement")
    refinement_threshold: float = Field(
        default=0.4, 
        ge=0.0, 
        le=1.0, 
        description="Threshold for triggering refinement (0.0=never, 1.0=always)"
    )
    
    # Summary Optimization for RAG/Fine-tuning
    target_summary_length: int = Field(default=800, gt=100, description="Target summary length in characters")
    min_summary_length: int = Field(default=400, gt=50, description="Minimum summary length in characters")
    max_summary_length: int = Field(default=1200, gt=100, description="Maximum summary length in characters")
    max_hierarchy_depth: int = Field(default=3, ge=1, description="Maximum hierarchy depth (0=book, 1=chapter, 2=section)")
    
    # Development Features
    dry_run: bool = Field(default=False, description="Run without LLM calls")
    mock_responses: bool = Field(default=False, description="Use mock responses")
    
    # Environment variable loading
    @classmethod
    def from_env(cls) -> "CognitiveConfig":
        """Create configuration from environment variables with fallback to defaults"""
        import os
        return cls(
            # LLM settings
            model_name=os.getenv("COGNITIVE_READER_MODEL", "qwen3:8b"),
            temperature=float(os.getenv("COGNITIVE_READER_TEMPERATURE", "0.1")),
            
            # Multi-pass configuration (extensible design)
            max_passes=int(os.getenv("COGNITIVE_READER_MAX_PASSES", "2")),
            convergence_threshold=float(os.getenv("COGNITIVE_READER_CONVERGENCE_THRESHOLD", "0.1")),
            
            # Dual model settings (fast scan + quality processing)
            enable_fast_first_pass=os.getenv("COGNITIVE_READER_ENABLE_FAST_FIRST_PASS", "true").lower() == "true",
            fast_pass_model=os.getenv("COGNITIVE_READER_FAST_PASS_MODEL", "llama3.1:8b"),
            main_model=os.getenv("COGNITIVE_READER_MAIN_MODEL", "qwen3:8b"),
            fast_pass_temperature=float(os.getenv("COGNITIVE_READER_FAST_PASS_TEMPERATURE", "0.1")) if os.getenv("COGNITIVE_READER_FAST_PASS_TEMPERATURE") else None,
            main_pass_temperature=float(os.getenv("COGNITIVE_READER_MAIN_PASS_TEMPERATURE", "0.3")) if os.getenv("COGNITIVE_READER_MAIN_PASS_TEMPERATURE") else None,
            
            # Processing settings
            chunk_size=int(os.getenv("COGNITIVE_READER_CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("COGNITIVE_READER_CHUNK_OVERLAP", "200")),
            context_window=int(os.getenv("COGNITIVE_READER_CONTEXT_WINDOW", "4096")),
            
            # Performance settings
            timeout_seconds=int(os.getenv("COGNITIVE_READER_TIMEOUT_SECONDS", "120")),
            max_retries=int(os.getenv("COGNITIVE_READER_MAX_RETRIES", "3")),
            document_language=LanguageCode(os.getenv("COGNITIVE_READER_LANGUAGE", "auto")),
            
            # Cognitive features
            enable_second_pass=os.getenv("COGNITIVE_READER_ENABLE_SECOND_PASS", "true").lower() == "true",
            enable_refinement=os.getenv("COGNITIVE_READER_ENABLE_REFINEMENT", "true").lower() == "true",
            refinement_threshold=float(os.getenv("COGNITIVE_READER_REFINEMENT_THRESHOLD", "0.4")),
            
            # Summary optimization for RAG/Fine-tuning
            target_summary_length=int(os.getenv("COGNITIVE_READER_TARGET_SUMMARY_LENGTH", "800")),
            min_summary_length=int(os.getenv("COGNITIVE_READER_MIN_SUMMARY_LENGTH", "400")),
            max_summary_length=int(os.getenv("COGNITIVE_READER_MAX_SUMMARY_LENGTH", "1200")),
            max_hierarchy_depth=int(os.getenv("COGNITIVE_READER_MAX_HIERARCHY_DEPTH", "3")),
            
            # Development features
            dry_run=os.getenv("COGNITIVE_READER_DRY_RUN", "false").lower() == "true",
            mock_responses=os.getenv("COGNITIVE_READER_MOCK_RESPONSES", "false").lower() == "true",
        )

# Environment Variables Reference
COGNITIVE_READER_ENV_VARS = {
    # LLM Configuration
    "COGNITIVE_READER_MODEL": "Default LLM model name (default: qwen3:8b)",
    "COGNITIVE_READER_TEMPERATURE": "Default LLM temperature 0.0-2.0 (default: 0.1)",
    
    # Multi-pass Configuration (Extensible Design)
    "COGNITIVE_READER_MAX_PASSES": "Maximum number of cognitive passes (default: 2)",
    "COGNITIVE_READER_CONVERGENCE_THRESHOLD": "Threshold to auto-stop passes when minimal improvement (default: 0.1)",
    
    # Dual Model Strategy (Fast Scan + Quality Processing)
    "COGNITIVE_READER_ENABLE_FAST_FIRST_PASS": "Enable fast model for initial scan (default: true)",
    "COGNITIVE_READER_FAST_PASS_MODEL": "Fast model for initial document scan (default: llama3.1:8b)",
    "COGNITIVE_READER_MAIN_MODEL": "Quality model for detailed cognitive processing (default: qwen3:8b)",
    "COGNITIVE_READER_FAST_PASS_TEMPERATURE": "Temperature for fast scan (default: 0.1)",
    "COGNITIVE_READER_MAIN_PASS_TEMPERATURE": "Temperature for quality processing (default: 0.3)",
    
    # Processing Configuration  
    "COGNITIVE_READER_CHUNK_SIZE": "Text chunk size (default: 1000)",
    "COGNITIVE_READER_CHUNK_OVERLAP": "Chunk overlap (default: 200)",
    "COGNITIVE_READER_CONTEXT_WINDOW": "LLM context limit (default: 4096)",
    "COGNITIVE_READER_LANGUAGE": "Document language auto/en/es (default: auto)",
    
    # Cognitive Features
    "COGNITIVE_READER_ENABLE_SECOND_PASS": "Enable second pass true/false (default: true)",
    "COGNITIVE_READER_ENABLE_REFINEMENT": "Enable refinement true/false (default: true)",
    "COGNITIVE_READER_REFINEMENT_THRESHOLD": "Refinement threshold 0.0-1.0 (default: 0.4)",
    
    # Summary Optimization for RAG/Fine-tuning
    "COGNITIVE_READER_TARGET_SUMMARY_LENGTH": "Target summary length in characters (default: 800)",
    "COGNITIVE_READER_MIN_SUMMARY_LENGTH": "Minimum summary length in characters (default: 400)",
    "COGNITIVE_READER_MAX_SUMMARY_LENGTH": "Maximum summary length in characters (default: 1200)",
    "COGNITIVE_READER_MAX_HIERARCHY_DEPTH": "Maximum hierarchy depth 0-N (default: 3)",
    
    # Performance & Development
    "COGNITIVE_READER_TIMEOUT_SECONDS": "Request timeout (default: 120)",
    "COGNITIVE_READER_MAX_RETRIES": "Max retries (default: 3)",
    "COGNITIVE_READER_DRY_RUN": "Dry run mode true/false (default: false)",
    "COGNITIVE_READER_MOCK_RESPONSES": "Mock responses true/false (default: false)",
}
```

### 📚 **API Requirements**

**Primary Interface**:
- Main interface: `read_document(file_path, config) -> CognitiveKnowledge`
- Environment variable configuration support
- Simple, clean API focused on cognitive features

**Configuration Options**:
- `enable_second_pass`: Boolean to enable/disable second pass enrichment
- `enable_refinement`: Boolean to enable/disable first pass refinement  
- `refinement_threshold`: Float (0.0-1.0) to control refinement sensitivity
- Dual model configuration for fast/quality processing

**Return Data**:
- Complete cognitive processing statistics (refinements made, enrichments made)
- Clear indication of which sections were processed with cognitive features
- Processing metadata including models used for each pass
- Clean output focused on final knowledge without process tracking

---

## 🏗️ Cognitive Architecture v2

### **System Components**

```
CognitiveReader (Main Engine)
├── StructureDetector (document parsing and structure detection)
├── ProgressiveReader (first pass with refinement capability)
├── ContextualEnricher (second pass with global context)
└── CognitiveSynthesizer (final synthesis with cognitive metadata)
```

### **Component Responsibilities**

#### **CognitiveReader** (Main Orchestrator)
**Purpose**: Coordinate two-pass cognitive reading process

**Responsibilities**:
- Orchestrate complete two-pass reading workflow
- Manage configuration for cognitive features (refinement, second pass, dual models)
- Coordinate between first pass and second pass processing
- Select appropriate models for each pass (fast/quality)
- Track and report cognitive processing metrics

**Interface Requirements**:
- `read_document(file_path, config) -> CognitiveKnowledge`: Primary interface
- Clean, focused API for cognitive reading
- Comprehensive cognitive processing statistics in results

#### **ProgressiveReader**
**Purpose**: Execute first pass with progressive reading and refinement capability

**Responsibilities**:
- Process sections sequentially with accumulated context
- Use fast model (if configured) for rapid first-pass processing
- Detect when new context significantly changes understanding of previous sections
- Update previous section summaries when refinement is needed
- Track refinement events and reasons
- Maintain context accumulation across section processing

**Requirements**:
- Configurable refinement capability (enable/disable)
- Fast model selection for performance optimization
- Refinement threshold configuration
- Complete tracking of which sections were refined and why

#### **ContextualEnricher**
**Purpose**: Execute second pass enrichment with global document context

**Responsibilities**:
- Re-read sections with complete document understanding
- Use quality model (if configured) for sophisticated second-pass analysis
- Identify opportunities for enrichment with global context
- Generate enhanced summaries that incorporate full document perspective
- Distinguish between meaningful enrichments and trivial changes
- Preserve first pass refinements while adding second pass insights

**Requirements**:
- Configurable to enable/disable second pass processing
- Quality model selection for enhanced analysis
- Integration with ProgressiveReader first pass results
- Track enrichment events and added value
- Maintain processing efficiency

#### **CognitiveSynthesizer**
**Purpose**: Generate final document synthesis with cognitive processing awareness

**Responsibilities**:
- Create hierarchical document synthesis
- Incorporate cognitive processing metadata into final results
- Note which sections underwent refinement or enrichment
- Track which models were used for each processing step
- Generate comprehensive cognitive processing summary for output

**Requirements**:
- Clear indication of all cognitive processing events in output
- Complete summary of cognitive processing benefits and evolution
- Model usage statistics and performance metrics

---

## 🔄 Cognitive Process Requirements

### **Two-Pass Processing Flow**

```
Document Input
    ↓
Structure Detection
    ↓
┌─────────────────┐
│   FIRST PASS    │
│ Progressive +   │
│ Basic Refinement│
└─────────────────┘
    ↓
├── Progressive Reading ──→ Context Accumulation
└── Basic Refinement ──→ Update summaries if understanding changes
    ↓
First Pass Result
    ↓
┌─────────────────┐
│  SECOND PASS    │
│ Global Context  │
│ Enrichment      │
└─────────────────┘
    ↓
├── Re-read with Global Context ──→ Enhanced Summaries
└── Simple Integration ──→ Final Knowledge
    ↓
Cognitive Knowledge Output
```

### **First Pass Requirements**

**Functional Requirements:**
- **Progressive Reading**: Process sections sequentially with accumulated context from previous sections
- **Fast Model Usage**: Use fast model (if configured) for rapid processing
- **Context Accumulation**: Build comprehensive context as reading progresses
- **Refinement Detection**: Identify when new information significantly changes understanding of previous sections
- **Summary Updates**: Update previous section summaries when understanding evolves
- **Refinement Tracking**: Record which summaries were refined and why

**Technical Requirements:**
- Fast model selection and management for performance optimization
- Refinement threshold configurable via `refinement_threshold` parameter
- Refinement can be disabled via `enable_refinement` configuration
- Complete tracking of refinements made for metrics and analysis

### **Second Pass Requirements**

**Functional Requirements:**
- **Global Context Re-reading**: Re-process each section with complete document context
- **Quality Model Usage**: Use quality model (if configured) for sophisticated analysis
- **Enrichment Detection**: Identify cases where global context adds meaningful insights
- **Summary Enhancement**: Improve summaries with insights only available after complete reading
- **Integration**: Combine first pass and second pass results coherently

**Technical Requirements:**
- Quality model selection and management for enhanced analysis
- Second pass can be disabled via `enable_second_pass` configuration
- Intelligent detection and tracking of meaningful enrichments vs trivial changes
- Preservation of refinements from first pass while adding enrichments
- Optimized processing performance with dual model strategy

---

## 📊 Simple Output Formats v2

### **Cognitive Knowledge JSON Output** (Optimized for RAG/Fine-tuning)

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

### **JSON Schema & Versioning**

**Schema Versioning Strategy**: 
- All output follows a **versioned JSON Schema** for consumer safety
- Schema versions use **semantic versioning** (MAJOR.MINOR.PATCH)
- Current version: **v1.0.0**

**Schema Location**:
```
GitHub Repository: https://github.com/juanje/cognitive-document-reader/schemas/
├── v1.0.0/
│   ├── cognitive-knowledge.json       # Main output schema
│   ├── concept-definition.json        # Concept schema
│   └── section-summary.json          # Summary schema
└── README.md                          # Schema documentation
```

**Usage for Consumers**:
```python
# Python validation example
import jsonschema
import requests

# Load schema from GitHub
schema_url = "https://raw.githubusercontent.com/juanje/cognitive-document-reader/main/schemas/v1.0.0/cognitive-knowledge.json"
schema = requests.get(schema_url).json()

# Validate cognitive reader output
jsonschema.validate(output_data, schema)
```

**Schema Evolution**:
- **v1.0.0**: Initial release (hierarchical summaries + concepts)
- **v1.1.0**: Future - Add optional fields (backward compatible)
- **v2.0.0**: Future - Breaking changes (major version bump)

**Output Includes Schema Version**:
```json
{
  "schema_version": "1.0.0",
  "document_title": "...",
  ...
}
```

### **Basic Evolution Markdown** (Simple annotations)

```markdown
# 3 Pasos Contra el Sedentarismo - Cognitive Reading Summary

> **Processing**: Two-pass cognitive reading | 3 refinements | 5 enrichments

## 📖 Document Summary
Final enriched understanding of the complete document...

## 📄 Section Summaries

### Introducción al sedentarismo ✨ *Refined + Enriched*
Final summary that incorporates understanding from later sections...

**Note**: This summary was refined during first pass when the specific 3-step method became clear.

### Problemas comunes: limitaciones de la movilidad, dolor y estrés ✨ *Enriched*  
Final summary enriched with global context about how problems connect to solutions...

**Note**: This summary was enriched during second pass with complete document context about the 3 steps.

### 3 pasos para salir del sedentarismo ✨ *Refined + Enriched*
Final summary showing the three specific movements (caminar más, sentarse en el suelo, colgarse) as systematic intervention...

**Note**: This summary was refined during first pass and enriched during second pass.

---

## 🔄 Cognitive Processing Notes

**Refinements made during first pass**: 3
- Introducción: Updated when specific movement solutions became clear
- 3 pasos section: Updated when connection between problems and specific movements became clear

**Enrichments made during second pass**: 5  
- All sections enriched with complete document context
- Connections between movement problems and specific movement solutions became clearer

**Key insight**: The two-pass approach revealed the book's coherent methodology where each section builds toward the specific 3-step solution (caminar más, sentarse en el suelo, colgarse).
```

### **CLI Output** (Show difference)

```bash
$ cognitive-reader book.md

✅ Cognitive Reading Complete

📊 Document Analysis:
- Total sections: 15
- Concepts identified: 12
- Average summary length: 740 characters

📄 Output saved to: book_cognitive_summary.json
```

---

## 🧪 Development & Testing Requirements

### **Development Mode Support**

**Required Development Features**:
- **Dry-run mode**: Enable testing without LLM API calls
- **Component isolation**: Ability to test first pass and second pass independently
- **Cognitive feature toggles**: Enable/disable refinement and second pass separately
- **Model testing**: Test dual model configurations independently
- **Processing metrics**: Clear reporting of cognitive processing statistics

**Configuration Requirements**:
- All cognitive features must be configurable via environment variables
- Support incremental feature testing (enable only refinement, or only second pass)
- Development-friendly defaults for testing
- Comprehensive model configuration testing (single vs dual models)

### **Testing Strategy**

**Functional Testing Requirements**:
- **Refinement validation**: Verify refinements improve understanding quality
- **Enrichment validation**: Verify second pass adds meaningful context
- **Dual model testing**: Validate fast model for first pass, quality model for second pass
- **Cognitive benefit demonstration**: Show clear difference vs. traditional fragmented approaches

**Performance Testing Requirements**:
- **Dual model performance**: Optimize performance with fast/quality model strategy
- **Memory usage**: Efficient memory management with different model configurations
- **LLM call optimization**: Efficient context reuse across passes and models
- **Scalability**: Performance must remain acceptable for large documents

**Quality Assurance Requirements**:
- **Author voice preservation**: Cognitive processing must maintain content fidelity
- **Coherence validation**: Refinements and enrichments must improve coherence
- **Model selection validation**: Ensure appropriate model selection for each cognitive task
- **Edge case handling**: Handle documents where refinement/enrichment provide minimal value

---

## 🎯 Development Phases

### **Foundation: Cognitive Data Models**

**Objectives**:
- Implement cognitive processing data models
- Create dual model configuration system
- Establish clean API for cognitive features

**Deliverables**:
- Complete `SectionSummary` model with cognitive tracking
- `CognitiveKnowledge` model with processing statistics
- `CognitiveConfig` with cognitive feature toggles and dual model support
- Clean API design focused on cognitive reading

### **First Pass: Progressive Refinement**

**Objectives**:
- Implement refinement capability in progressive reading
- Add fast model support for rapid first-pass processing
- Implement refinement detection and summary updating

**Deliverables**:
- `ProgressiveReader` with refinement capability
- Fast model integration and selection
- Refinement detection algorithm implementation
- Refinement threshold configuration
- Unit testing for refinement features

### **Second Pass: Contextual Enrichment**

**Objectives**:
- Implement global context enrichment capability
- Add quality model support for sophisticated second-pass analysis
- Integrate first pass and second pass results

**Deliverables**:
- `ContextualEnricher` component implementation
- Quality model integration and selection
- Second pass integration in main reading workflow
- Enrichment detection and tracking
- Complete two-pass flow testing

### **Validation: Testing & Optimization**

**Objectives**:
- Validate cognitive processing benefits with real documents
- Performance testing and optimization with dual model strategy
- Documentation and example creation

**Deliverables**:
- Updated output formats with cognitive metadata and model usage statistics
- Performance benchmarking with dual model configurations
- "3 pasos contra el sedentarismo" validation testing
- User documentation and examples
- MVP v2.0 release

---

## 📈 Success Metrics (MVP Goals)

### **Proof of Concept Goals**
- ✅ **Demonstrate cognitive difference**: Clear difference between cognitive reading and traditional fragmented processing
- ✅ **Refinement validation**: Show examples where understanding improved during first pass  
- ✅ **Enrichment validation**: Show examples where second pass added value
- ✅ **"3 pasos" test**: Successfully process sample chapters with cognitive approach
- ✅ **Dual model validation**: Demonstrate benefits of fast/quality model strategy

### **Technical Requirements**
- ✅ **Clean API**: Simple, focused interface for cognitive reading
- ✅ **Performance optimization**: Effective dual model strategy for speed/quality balance
- ✅ **Memory efficiency**: Efficient processing with multiple model configurations
- ✅ **Development friendly**: Comprehensive dry-run and configuration options

### **Quality Indicators**
- ✅ **Coherent refinements**: Refinements should improve summary quality
- ✅ **Valuable enrichments**: Second pass should add meaningful context
- ✅ **Author voice preservation**: Maintain fidelity to original content
- ✅ **Clear output quality**: Final summaries and concepts demonstrate superior understanding
- ✅ **Model effectiveness**: Fast model enables speed, quality model enhances depth

---

## 📚 Testing with Real Document

### **Example Document for Validation**

The project includes a reduced version of the actual book "3 pasos contra el sedentarismo" in `examples/3 pasos contra el sedentarismo.md` to enable **realistic testing** and **quality validation**.

#### **Document Structure** (Real Content)
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

#### **Key Testing Benefits**

1. **🎯 Authentic Content**: Real author voice and methodology
2. **🔬 Quality Validation**: Compare cognitive vs. traditional processing
3. **📊 Concept Extraction**: Validate extraction of domain-specific terms
4. **🏗️ Hierarchy Testing**: Multi-level structure with logical relationships
5. **⚡ Performance Testing**: Appropriately sized document for realistic but manageable testing

#### **Recommended Test Cases**

```python
# Test Case 1: Full Cognitive Processing
test_file = "examples/3 pasos contra el sedentarismo.md"
result = cognitive_reader.process_document(
    file_path=test_file,
    enable_second_pass=True,
    enable_refinement=True
)

# Validate authentic concepts are extracted
expected_concepts = [
    "sedentarismo", "vida_nomada", "movimiento_natural", 
    "tres_pasos", "dolor_cronico", "mapas_cerebrales"
]

# Test Case 2: Quality Comparison
traditional_chunks = chunk_processor.process(test_file)
cognitive_summaries = result.hierarchical_summaries

# Cognitive summaries should show:
# ✅ Coherent understanding of methodology
# ✅ Logical progression from problems to solutions  
# ✅ Preserved author's voice and specific terminology
# ✅ Connected concepts across sections
```

#### **Quality Indicators to Validate**

- **📖 Coherent Book Summary**: Should capture the core methodology and progression
- **🔗 Connected Concepts**: `sedentarismo` → `tres_pasos` relationship should be clear
- **🎯 Accurate Terminology**: Domain-specific terms like "propiocepción", "nocicepción" 
- **📚 Preserved Voice**: Maintains author's scientific yet accessible tone
- **🧩 Logical Hierarchy**: Introduction → Problems → Solutions → Conclusions flow

---

## 🚀 Future Development (Post-MVP)

### **Enhanced Cognitive Features**
- **Multi-pass iterative reading**: Extend beyond 2-pass to N-pass cognitive processing
  - Configurable number of passes (3, 4, 5+ re-readings)
  - Each pass deepens understanding and refines concepts iteratively
  - Diminishing returns detection to optimize pass count automatically
  - Pass-specific prompting strategies for progressive refinement
  - Advanced context accumulation across multiple iterations
- **Complex emergent concept detection**: More sophisticated concept emergence patterns
- **Knowledge graph generation**: Export relationships to graph databases
- **Multi-document cognitive synthesis**: Read across related documents
- **Advanced refinement strategies**: More intelligent refinement triggers

### **Advanced Integration**
- **Contradiction detection**: Handle inconsistencies intelligently  
- **Expert feedback loops**: Incorporate human expert refinements
- **Adaptive cognitive strategies**: Adjust approach based on document type
- **Performance optimization**: Advanced caching and parallel processing

---

## 💡 Key Innovation of MVP v2

**Minimal Cognitive Reading**: The first system to implement **basic two-pass human reading process** with:

1. ✅ **Progressive + Refinement**: First pass that can update understanding as context grows
2. ✅ **Global Enrichment**: Second pass that enriches with complete document context  
3. ✅ **Integrated Summaries**: Final output that reflects deep understanding without process metadata
4. ✅ **Proof of Concept**: Demonstrate clear difference from chunk-based fragmentation

**MVP v2** proves that **cognitive reading works differently** than sequential processing, establishing the foundation for more advanced cognitive features in future phases.

---

*This specification defines the minimal viable cognitive reading system that demonstrates human-like understanding evolution while maintaining simplicity and implementability.*
