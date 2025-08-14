# Cognitive Document Reader - Technical Specifications v2.0

> **Version 2.0**: Architectural redesign based on the authentic human cognitive reading process detailed in `MOTIVATION.md`

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
1. **First pass**: Sequential processing in document order + **cumulative context**
2. **Second pass**: Re-reading with **selective enriched context** (previous summaries + glossary)

This process is **essential** for the project's core goal: generating high-quality datasets for the "3 pasos contra el sedentarismo" book that preserve the author's voice and methodology.

### **v2.0 Solution**
Implement the **authentic sequential algorithm** to demonstrate cognitive reading vs. fragmented chunks:
- ✅ Sequential reading in document order (first and second pass)
- ✅ Cumulative context (parents + previous siblings) for each section
- ✅ Incremental updates of parent levels
- ✅ Text source authority principle over any context
- ✅ Selective enrichment in second pass with glossary

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
- **pydantic v2+**: Data validation and settings management
- **docling**: Universal document parsing (current stable: v2.43.0+)
- **aiohttp**: Async HTTP client for LLM communications
- **click**: Command-line interface framework
- **langdetect**: Language detection capabilities

### **Code Quality Standards (Mandatory)**

**Type Safety:**
- **ALL** functions, methods, and class members MUST have type annotations
- Use `from __future__ import annotations` for forward references
- Prefer specific types over generic ones (`List[str]` over `List[Any]`)

**Documentation:**
- **ALL** public functions, methods, and classes MUST have Google-style docstrings
- Include purpose, parameters, return values, exceptions, and usage examples
- Code comments only in English

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
- **90% minimum coverage**: Focus on critical paths and error handling
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
- **Clear purpose**: File names should indicate functionality
- **No abbreviations**: Prefer `progressive_reader.py` over `prog_reader.py`
- **Mirror tests**: Test files mirror source structure (`test_progressive_reader.py`)

**Module Responsibilities:**
- **models/**: Only Pydantic models and data structures
- **core/**: Business logic and cognitive processing algorithms  
- **parsers/**: Document format handling and structure detection
- **llm/**: LLM communication and prompt management
- **utils/**: Pure functions with no external dependencies
- **cli/**: Command-line interface and user interaction

---

## 🎯 Main Use Cases

### **1. High-Quality Summaries for Human Reading/Study**
   - Summaries that evolve during the reading process  
   - Contextual maps showing knowledge development
   - Progressive learning paths through complex documents

### **2. Dataset Generation for Fine-tuning**
   - **Hierarchical context construction**: Book → Chapter → Section summaries for coherent training
   - **Consistent terminology**: Cognitively refined concept definitions for domain precision
   - **Rich training examples**: Use summary hierarchy to generate contextually coherent Q&A pairs

### 🧠 **Core Innovation: Two-Pass Cognitive Processing**

Unlike traditional document processors that fragment content, **Cognitive Document Reader v2** implements the complete human reading process:

#### 🔄 **First Pass: Sequential Processing with Cumulative Context**
1. **Document-order processing** following natural reading flow
2. **Context accumulation**: Each section receives context from all parents + previous siblings
3. **Incremental updates**: Parent levels evolve as children are processed
4. **Text authority principle**: Original text always takes precedence over any context
5. **Deferred synthesis**: Parent sections without content wait for all children to be processed

#### 🔍 **Second Pass: Selective Context Enrichment**
1. **Same sequential algorithm** as first pass, maintaining document order
2. **Selective enriched context**: Current parent summaries + previous summary of same node + concept glossary
3. **Authority preservation**: Text source remains supreme authority over all contextual information
4. **Conceptual integration**: Glossary provides specialized conceptual frameworks
5. **Controlled refinement**: Context informs but never contradicts the original text

### 🧠 **Dual Model Strategy: Simulating Human Reading Patterns**

Human reading naturally involves two different cognitive approaches:
- **Rapid scan**: Quick overview to get the general idea (first pass)
- **Careful analysis**: Detailed understanding with full context (second pass)

The **dual model configuration** reflects this:
- **Fast model (first pass)**: Optimized for speed, basic understanding, rapid refinement detection
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

### **Main Goal**: Demonstrate cognitive reading vs. fragmented chunks with minimal complexity

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
   - **Value focus**: Only useful information for RAG/Fine-tuning, no internal process noise

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

### **Main Principle**: Define clear contracts while allowing implementation flexibility

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
    title: str                                 # Clean section title
    content: str                               # Section text content
    level: int                                 # Hierarchical level (0=document, 1=chapter, 2=section, etc.)
    parent_id: Optional[str] = None            # Parent section ID (None for root)
    children_ids: List[str] = Field(default_factory=list)  # Child section IDs
    order_index: int                           # Order within parent

class SectionSummary(BaseModel):
    """Section summary optimized for RAG chunks"""
    section_id: str                            # Reference to DocumentSection.id
    title: str                                 # Section title
    summary: str                               # Cognitively enhanced summary (optimized for RAG chunks)
    key_concepts: List[str] = Field(default_factory=list)  # Key concept IDs relevant to this section
    summary_length: int                        # Summary length in characters

class ConceptDefinition(BaseModel):
    """Key concept with cognitively refined definition"""
    concept_id: str                            # Unique identifier (e.g., "sedentarism", "natural_movement")
    name: str                                  # Human-readable concept name
    definition: str                            # Cognitively refined definition
    first_mentioned_in: str                    # Section ID where this concept was first identified
    relevant_sections: List[str] = Field(default_factory=list)  # Section IDs where concept is relevant

class CognitiveKnowledge(BaseModel):
    """Complete cognitive knowledge extracted for RAG/Fine-tuning"""
    # Document identification
    document_title: str
    document_summary: str                      # Cognitively enhanced document-level summary
    detected_language: LanguageCode
    
    # Hierarchical summaries optimized for RAG chunks
    hierarchical_summaries: Dict[str, SectionSummary]  # Section ID -> Summary mapping
    
    # Key concepts with cognitively refined definitions
    concepts: Dict[str, ConceptDefinition]     # Concept ID -> Definition mapping
    
    # Hierarchical navigation indexes
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
    
    # Dual model strategy: fast scan + quality processing
    enable_fast_first_pass: bool = Field(default=True, description="Use fast model for initial scan")
    fast_pass_model: Optional[str] = Field(default="llama3.1:8b", description="Fast model for initial document scan")
    main_model: Optional[str] = Field(default="qwen3:8b", description="Quality model for detailed cognitive processing")
    
    # Temperature configuration
    fast_pass_temperature: Optional[float] = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for fast scan")
    main_pass_temperature: Optional[float] = Field(default=0.3, ge=0.0, le=2.0, description="Temperature for quality processing")

### **🔧 Extensible Multi-Pass Design Philosophy**

The MVP implements **2-pass reading** but is architecturally prepared for **N-pass extension**:

```python
# MVP usage (2 passes) - Ready today
config = CognitiveConfig(
    max_passes=2,
    fast_pass_model="llama3.1:8b",    # Fast initial scan
    main_model="qwen3:8b"          # Quality cognitive processing
)

# Future N-pass usage (same API) - Smooth extension
config = CognitiveConfig(
    max_passes=4,                     # Configurable depth
    convergence_threshold=0.05,       # Auto-stop optimization  
    main_model="qwen3:8b"          # Same model, richer context each pass
)
```

#### **Key Design Principles**

1. **📖 Same "Brain", Better Knowledge**: Multiple passes use the **same model** with **progressively richer context**
2. **🔄 Context Accumulation**: Each pass provides accumulated summaries, concepts, and insights to the next
3. **🏆 Original Text Authority**: **Source text always takes precedence** over summaries/previous context when conflicts arise
4. **⚡ Intelligent Speed/Quality Balance**: Fast scan (`llama3.1:8b`) + Quality processing (`qwen3:8b`) 
5. **🎯 Convergence Detection**: Future auto-stop when additional passes add minimal value
6. **🏗️ API Consistency**: Same interface scales from MVP 2-pass to advanced N-pass features

#### **🏆 Text Source Authority Principle**

**CRITICAL**: When processing each section, the **original text** is the supreme authority:

```python
# Prompting hierarchy (highest to lowest authority)
AUTHORITY_HIERARCHY = [
    "Original text content",    # 🥇 Supreme authority - always wins
    "Refined previous summaries",     # 🥈 Contextual guidance  
    "Discovered concepts",          # 🥉 Supporting information
    "Global document understanding" # 📚 Background context
]
```

**Conflict Resolution Strategy**:
- ✅ **Text contradicts summary** → Update summary to match text
- ✅ **Text adds new nuance** → Enrich summary with text perspective  
- ✅ **Text reveals concept error** → Refine concept definition
- ❌ **Never** modify text interpretation to fit previous context

#### **💭 Authority-Aware Prompting Strategy**

**Example Prompt Structure** (applying text authority):

```
CONTEXT (background information only):
- Book Summary: [previous understanding]
- Concept Definitions: [discovered so far]  
- Parent Section Summary: [if applicable]

SOURCE TEXT (AUTHORITATIVE):
[actual section content to process]

INSTRUCTIONS:
1. Read the SOURCE TEXT carefully - this is your PRIMARY source of truth
2. Use CONTEXT only as background information to inform your understanding
3. If SOURCE TEXT contradicts any CONTEXT information:
   - Trust the SOURCE TEXT completely
   - Update your understanding based on SOURCE TEXT
   - Note discrepancies for refinement
4. Generate summary that accurately reflects SOURCE TEXT
5. Identify concepts mentioned in SOURCE TEXT (not just from context)

CRITICAL: SOURCE TEXT is always correct. Previous summaries may contain errors or incomplete understanding.
```

#### **📝 Practical Example: Text Authority in Action**

**Scenario**: Processing chapter 3 of "3 pasos contra el sedentarismo"

```python
# Previous context (may contain errors)
previous_summary = {
    "sedentarism": "Lack of physical exercise in modern life"  # ← Incomplete understanding
}

# Current section text (authoritative)
source_text = """
Sedentarism, in its deepest sense, is not simply spending a lot of time sitting. 
It is a concept rooted in the lack of varied movement and specialization of postures.
"""

# Cognitive processing result (text authority applied)
refined_understanding = {
    "sedentarism": "Chronic state of physical inactivity resulting from lack of varied movement and postural specialization, not simply spending time sitting"  # ← Corrected by source text
}
```

**Key Insight**: The source text **corrected** the previous incomplete definition, demonstrating how text authority ensures evolutionary accuracy.

---

## 🔄 **Central Purpose: Error Correction & Refinement**

### **🎯 Main Justification for Multi-Pass Design**

The **primary reason** for second, third, and Nth passes is **systematic error correction and knowledge refinement**:

#### **🔍 What Gets Corrected/Refined**

1. **📝 Summary Accuracy**
   - **Initial errors**: First-pass summaries may miss key points or misinterpret concepts
   - **Progressive refinement**: Each pass corrects and enriches understanding
   - **Global coherence**: Later sections provide context that clarifies earlier misunderstandings

2. **💡 Concept Definitions**
   - **Initial approximations**: First encounters with concepts generate partial definitions
   - **Iterative precision**: Subsequent passes refine definitions with richer context
   - **Cross-validation**: Concepts mentioned in multiple sections get more precise definitions

3. **🔗 Relationship Understanding** 
   - **Missed connections**: Single-pass processing misses relationships between concepts
   - **Emergent patterns**: Multi-pass reveals how concepts relate across the document
   - **Hierarchical clarity**: Parent-child relationships between concepts become apparent

#### **📈 Real-World Correction Examples**

```python
# Pass 1: Initial understanding (often incomplete/incorrect)
first_pass_concept = {
    "sedentarism": "Lack of physical exercise"  # ← Superficial understanding
}

# Pass 2: Corrected with global context
second_pass_concept = {
    "sedentarism": "Chronic state of physical inactivity characterized by lack of varied movement and postural specialization, not simply absence of exercise"  # ← Deep and precise understanding
}

# Pass 3: Further refined with cross-references
third_pass_concept = {
    "sedentarism": "Chronic state of physical inactivity resulting from modern environments that eliminate varied movement, causing problematic body adaptations through postural specialization. Distinguished from simple lack of exercise by its focus on movement variety vs. intensity."  # ← Comprehensive and nuanced understanding
}
```

#### **✅ Success Indicators for Refinement**

- **Concept evolution**: Definitions become more precise and comprehensive across passes
- **Error detection**: System identifies and corrects previous misunderstandings  
- **Coherence improvement**: Summaries align better with document's overall message
- **Relationship clarity**: Connections between concepts become explicit and precise
    
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
        description="Threshold to trigger refinement (0.0=never, 1.0=always)"
    )
    
    # Development Features
    dry_run: bool = Field(default=False, description="Run without LLM calls")
    mock_responses: bool = Field(default=False, description="Use mock responses")
    
    # Environment variable loading
    @classmethod
    def from_env(cls) -> "CognitiveConfig":
        """Create configuration from environment variables with fallback to defaults"""
        import os
        return cls(
            # LLM configurations
            model_name=os.getenv("COGNITIVE_READER_MODEL", "qwen3:8b"),
            temperature=float(os.getenv("COGNITIVE_READER_TEMPERATURE", "0.1")),
            
            # Multi-pass configuration (extensible design)
            max_passes=int(os.getenv("COGNITIVE_READER_MAX_PASSES", "2")),
            convergence_threshold=float(os.getenv("COGNITIVE_READER_CONVERGENCE_THRESHOLD", "0.1")),
            
            # Dual model configurations (fast scan + quality processing)
            enable_fast_first_pass=os.getenv("COGNITIVE_READER_ENABLE_FAST_FIRST_PASS", "true").lower() == "true",
            fast_pass_model=os.getenv("COGNITIVE_READER_FAST_PASS_MODEL", "llama3.1:8b"),
            main_model=os.getenv("COGNITIVE_READER_MAIN_MODEL", "qwen3:8b"),
            fast_pass_temperature=float(os.getenv("COGNITIVE_READER_FAST_PASS_TEMPERATURE", "0.1")) if os.getenv("COGNITIVE_READER_FAST_PASS_TEMPERATURE") else None,
            main_pass_temperature=float(os.getenv("COGNITIVE_READER_MAIN_PASS_TEMPERATURE", "0.3")) if os.getenv("COGNITIVE_READER_MAIN_PASS_TEMPERATURE") else None,
            
            # Processing configurations
            chunk_size=int(os.getenv("COGNITIVE_READER_CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("COGNITIVE_READER_CHUNK_OVERLAP", "200")),
            context_window=int(os.getenv("COGNITIVE_READER_CONTEXT_WINDOW", "4096")),
            
            # Performance configurations
            timeout_seconds=int(os.getenv("COGNITIVE_READER_TIMEOUT_SECONDS", "120")),
            max_retries=int(os.getenv("COGNITIVE_READER_MAX_RETRIES", "3")),
            document_language=LanguageCode(os.getenv("COGNITIVE_READER_LANGUAGE", "auto")),
            
            # Cognitive features
            num_passes=int(os.getenv("COGNITIVE_READER_NUM_PASSES", "2")),
            enable_refinement=os.getenv("COGNITIVE_READER_ENABLE_REFINEMENT", "true").lower() == "true",
            refinement_threshold=float(os.getenv("COGNITIVE_READER_REFINEMENT_THRESHOLD", "0.4")),
            
            # Development features
            dry_run=os.getenv("COGNITIVE_READER_DRY_RUN", "false").lower() == "true",
            mock_responses=os.getenv("COGNITIVE_READER_MOCK_RESPONSES", "false").lower() == "true",
        )

# Environment Variables Reference
COGNITIVE_READER_ENV_VARS = {
    # LLM Configuration
    "COGNITIVE_READER_MODEL": "Default LLM model name (default: qwen3:8b)",
    "COGNITIVE_READER_TEMPERATURE": "Default LLM temperature 0.0-2.0 (default: 0.1)",
    
    # Multi-Pass Configuration (Extensible Design)
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
    "COGNITIVE_READER_NUM_PASSES": "Number of cognitive passes integer >=1 (default: 2)",
    "COGNITIVE_READER_ENABLE_REFINEMENT": "Enable refinement true/false (default: true)",
    "COGNITIVE_READER_REFINEMENT_THRESHOLD": "Refinement threshold 0.0-1.0 (default: 0.4)",
    
    # Performance and Development
    "COGNITIVE_READER_TIMEOUT_SECONDS": "Request timeout (default: 120)",
    "COGNITIVE_READER_MAX_RETRIES": "Max retries (default: 3)",
    "COGNITIVE_READER_DRY_RUN": "Dry run mode true/false (default: false)",
    "COGNITIVE_READER_MOCK_RESPONSES": "Mock responses true/false (default: false)",
}
```

### 📚 **API Requirements**

**Main Interface**:
- Primary interface: `read_document(file_path, config) -> CognitiveKnowledge`
- Configuration support via environment variables
- Simple and clean API focused on cognitive features

**Configuration Options**:
- `enable_second_pass`: Boolean to enable/disable second pass enrichment
- `enable_refinement`: Boolean to enable/disable first pass refinement  
- `refinement_threshold`: Float (0.0-1.0) to control refinement sensitivity
- Dual model configuration for fast/quality processing

**Return Data**:
- Complete cognitive processing statistics (refinements made, enrichments made)
- Clear indication of which sections were processed with cognitive features
- Processing metadata including models used for each pass
- Cognitive evolution tracking and refinement history

---

## 🏗️ Cognitive Architecture v2

### **System Components**

```
CognitiveReader (Main Engine)
├── StructureDetector (document structure analysis and detection)
├── SequentialProcessor (first pass with sequential algorithm)
├── ContextualEnricher (second pass with enriched context)
└── CognitiveSynthesizer (final synthesis with cognitive knowledge)
```

### **Component Responsibilities**

#### **CognitiveReader** (Main Orchestrator)
**Purpose**: Coordinate sequential two-pass cognitive reading process

**Responsibilities**:
- Orchestrate complete sequential two-pass reading flow
- Manage sequential algorithm configuration (second pass, dual models)
- Coordinate between first pass and second pass processing
- Provide clean API for sequential cognitive reading
- Generate final integrated cognitive knowledge

**Interface Requirements**:
- `read_document(file_path, config) -> CognitiveKnowledge`: Primary interface for cognitive reading
- Simple API focused on sequential processing with two passes
- Results that demonstrate cognitive processing benefits vs. fragmented approaches

#### **SequentialProcessor** (Sequential Algorithm)
**Purpose**: Execute first pass using sequential algorithm with cumulative context

**Responsibilities**:
- Process sections in document order (natural reading flow)
- Maintain cumulative context (parents + previous siblings) for each section
- Update parent levels incrementally in automated fashion
- Apply text source authority principle over any context
- Handle deferred synthesis for parent sections without own content

**Requirements**:
- Strictly sequential processing following document order
- Efficient cumulative context construction for each section
- Automatic incremental updates (without complex detection)
- Preservation of authority principle: text source > context
- Correct handling of parent with/without own content cases

#### **ContextualEnricher** (Second Pass Sequential)
**Purpose**: Execute second pass using same sequential algorithm + enriched context

**Responsibilities**:
- Re-process sections using same sequential algorithm as first pass
- Provide selective enriched context (current summaries + previous summary + glossary)
- Maintain text source authority principle over all enriched context
- Generate final summaries that integrate global document understanding
- Preserve sequential order and incremental updates from first pass

**Requirements**:
- Same sequential algorithm as SequentialProcessor (approach consistency)
- Enriched context: parent summaries + previous node summary + glossary
- Authority principle preserved: text source > enriched context
- Must be configurable to enable/disable second pass
- Smooth integration with first pass results

#### **CognitiveSynthesizer** (Knowledge Synthesis)
**Purpose**: Generate final cognitive knowledge optimized for RAG/Fine-tuning

**Responsibilities**:
- Create hierarchical structure of final summaries (document/section summaries)
- Extract and filter key concepts with refined definitions
- Generate hierarchical navigation indexes and parent-child maps
- Calculate processing statistics (total sections, concepts, lengths)
- Produce clean JSON optimized for RAG/Fine-tuning consumption

**Requirements**:
- Output focused on RAG/Fine-tuning value (without internal metadata)
- Evident quality that demonstrates cognitive processing benefits
- Clear and hierarchically navigable data structure
- Compatibility with versioned JSON schema for consumers

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

### **Sequential Processing Algorithm**

The cognitive reading process implements a **sequential top-down algorithm with incremental updates** that processes sections in document order, maintaining cumulative context and incrementally updating parent levels.

#### **Algorithm Overview**

```
1. Structure Analysis
   ├── Detect complete hierarchical structure
   └── Classify sections (parent with/without content, leaves)

2. First Pass: Sequential Processing
   ├── PROCESS sections in document order
   ├── FOR each section:
   │   ├── IF parent WITH content:
   │   │   ├── Process parent text → parent_summary
   │   │   └── Store as context for children
   │   ├── IF leaf:
   │   │   ├── Gather context: parents + previous siblings
   │   │   ├── Process with cumulative context → leaf_summary
   │   │   └── Update parent levels incrementally
   │   └── IF parent WITHOUT content:
   │       ├── Wait until all children processed
   │       └── Synthesize from children summaries + context

3. Second Pass: Selective Enrichment
   ├── SAME sequential order as first pass
   ├── ENRICHED context for each section:
   │   ├── Current parent summaries
   │   ├── Previous summary of same node
   │   └── Concept glossary with definitions
   └── AUTHORITY PRINCIPLE: Text source > context

4. Output Generation
   └── Cognitive Knowledge with enriched summaries
```

#### **Sequential Processing Order Example**

For a document structure like:
```
# Book Title (Parent WITH content)
## Chapter 1: Introduction (Parent WITH content)
### Section 1.1: Background (Leaf)
### Section 1.2: Purpose (Leaf)
## Chapter 2: Methods (Parent WITHOUT content)
### Section 2.1: Approach (Leaf)
```

**Sequential processing sequence (document order):**
1. **Book Title** (Parent WITH content) → `title_summary_v1`
2. **Chapter 1: Introduction** (Parent WITH content) → context: `title_summary_v1` → `ch1_summary_v1`
3. **Section 1.1: Background** (Leaf) → context: `title_summary_v1 + ch1_summary_v1` → `summary_1_1`
   - **Update Chapter 1**: `ch1_summary_v1 + summary_1_1` → `ch1_summary_v2`
   - **Update Title**: `title_summary_v1 + ch1_summary_v2` → `title_summary_v2`
4. **Section 1.2: Purpose** (Leaf) → context: `title_summary_v2 + ch1_summary_v2 + summary_1_1` → `summary_1_2`
   - **Update Chapter 1**: `ch1_summary_v2 + summary_1_2` → `ch1_summary_final`
   - **Update Title**: `title_summary_v2 + ch1_summary_final` → `title_summary_v3`
5. **Chapter 2: Methods** (Parent WITHOUT content) → proceed to children
6. **Section 2.1: Approach** (Leaf) → context: `title_summary_v3` → `summary_2_1`
   - **Synthesize Chapter 2**: `summary_2_1` + context: `title_summary_v3` → `ch2_summary_final`
   - **Update Title**: `title_summary_v3 + ch2_summary_final` → `title_summary_final`

#### **Content Composition Rules**

**For Leaf Sections:**
- Input: `section.content` (heading + following paragraphs)
- Generate: Section summary + key concepts

**For Container Sections:**
- Input: `section.content + child_summaries`
- Format: `"Section content:\n{section.content}\n\nSubsection summaries:\n{child_summaries}"`
- Generate: Container summary that synthesizes own content with children insights

**For Document Level:**
- Input: `document_title + top_level_summaries`
- Generate: Document summary + global concept glossary

#### **Technical Implementation**

```python
async def process_sequentially(sections: List[DocumentSection]) -> CognitiveKnowledge:
    """Process document using sequential algorithm with cumulative context."""
    
    # 1. Organize sections in document order
    ordered_sections = order_by_document_sequence(sections)
    
    # 2. First pass: Sequential processing
    summaries = {}
    
    for section in ordered_sections:
        # Build cumulative context
        context = build_cumulative_context(section, summaries)  # parents + previous siblings
        
        if section.has_own_content:  # Parent with content or leaf
            # AUTHORITY PRINCIPLE: text source > context
            summary = await generate_summary_with_context(
                text_source=section.content,  # SUPREME AUTHORITY
                context=context,              # SUPPORTING INFORMATION
                section_id=section.id
            )
            summaries[section.id] = summary
            
            # Update parent levels incrementally
            await update_parent_levels(section, summary, summaries)
            
        elif not section.has_own_content and section.children_processed:
            # Deferred synthesis for parents without content
            children_summaries = get_children_summaries(section, summaries)
            parent_context = get_parent_context(section, summaries)
            
            summary = await synthesize_from_children(
                children_summaries=children_summaries,
                parent_context=parent_context,
                section_id=section.id
            )
            summaries[section.id] = summary
    
    # 3. Second pass: Selective enrichment
    enriched_summaries = await second_pass_enrichment(
        sections=ordered_sections,
        first_pass_summaries=summaries,
        concept_glossary=extract_concept_glossary(summaries)
    )
    
    return CognitiveKnowledge(
        document_summary=enriched_summaries[root_section.id],
        section_summaries=enriched_summaries,
        concepts=extract_all_concepts(enriched_summaries)
    )
```

This algorithm ensures that:
- ✅ **Natural order**: Follows document sequence as a human reader would
- ✅ **Cumulative context**: Each section receives context from parents + previous siblings
- ✅ **Authority principle**: Source text always prevails over any context
- ✅ **Incremental updates**: Parent levels evolve as children are processed
- ✅ **Scalability**: Works for any depth of document structure
- ✅ **Context preservation** maintains hierarchical relationships

### **First Pass Requirements**

**Functional Requirements:**
- **Sequential Processing**: Process sections in document order following natural reading flow
- **Cumulative Context**: Each section receives context from all parents + previous siblings
- **Incremental Updates**: Parent levels evolve as children are processed
- **Authority Principle**: Original text always prevails over any context
- **Deferred Synthesis**: Parents without content wait for all children to be processed

**Technical Requirements:**
- Fast model selection and management for performance optimization
- Efficient cumulative context construction for each section
- Incremental update system without information loss
- Complete version tracking of summaries for metrics and analysis

### **Second Pass Requirements**

**Functional Requirements:**
- **Same Sequential Algorithm**: Replicate exact processing order from first pass
- **Selective Enriched Context**: Current parent summaries + previous summary of same node + concept glossary
- **Preserved Authority Principle**: Text source remains supreme authority over all contextual information
- **Conceptual Integration**: Glossary provides specialized conceptual frameworks for better understanding
- **Controlled Refinement**: Context informs but never contradicts original text

**Technical Requirements:**
- Second pass can be disabled via `enable_second_pass` configuration
- Must use quality model for deeper analysis
- Must integrate concept glossary as enriched context
- Must maintain authority hierarchy: text > current context > previous context
- Must track quality improvements over first pass

---

## 📊 Simple Output Formats v2

### **Cognitive Knowledge JSON** (Optimized for RAG/Fine-tuning)

```json
{
  "document_title": "3 Steps Against Sedentarism",
  "document_summary": "Practical guide to counter sedentarism through three fundamental movements that restore natural body functionality: walking more for base cardiovascular capacity, sitting on the floor for hip mobility, and hanging for grip strength and spinal decompression. The book explains how sedentarism causes problematic body adaptations and presents a specific methodology based on natural movements to recover health and functionality.",
  "detected_language": "en",
  
  "concepts": {
    "sedentarism": {
      "concept_id": "sedentarism",
      "name": "Sedentarism",
      "definition": "Chronic state of physical inactivity resulting from prolonged exposure to environments requiring little or no physical activity, causing body adaptations that compromise natural human health and functionality.",
      "first_mentioned_in": "introduction",
      "relevant_sections": ["introduction", "common_problems", "three_steps"]
    },
    "natural_movement": {
      "concept_id": "natural_movement",
      "name": "Natural Movement", 
      "definition": "Movement patterns for which the human body is evolutionarily adapted, including walking, sitting on the ground, hanging, and other activities that maintain optimal body functionality without requiring specialized equipment.",
      "first_mentioned_in": "introduction",
      "relevant_sections": ["introduction", "three_steps"]
    },
    "nomadic_life": {
      "concept_id": "nomadic_life",
      "name": "Ancestral Nomadic Life",
      "definition": "Lifestyle of our ancestors for over two million years, characterized by constant movement, variety of postures and diverse stimuli that shaped our body for adaptation and resilience.",
      "first_mentioned_in": "introduction",
      "relevant_sections": ["introduction"]
    },
    "three_steps": {
      "concept_id": "three_steps",
      "name": "Three-Step Methodology",
      "definition": "Specific intervention system against sedentarism consisting of: 1) Walking more to restore base functionality, 2) Sitting more on the ground to recover hip mobility, and 3) Hanging more from hands to strengthen grip and decompress spine.",
      "first_mentioned_in": "three_steps",
      "relevant_sections": ["three_steps", "step_1", "step_2", "step_3"]
    }
  },
  
  "hierarchical_summaries": {
    "book": {
      "section_id": "book",
      "title": "3 Steps Against Sedentarism",
      "summary": "Practical guide to counter sedentarism through three fundamental movements that restore natural body functionality. Explains how sedentarism causes problematic body adaptations and presents a specific methodology based on natural movements to recover health and functionality.",
      "key_concepts": ["sedentarism", "natural_movement", "nomadic_life", "three_steps"],
      "summary_length": 850
    },
    "introduction": {
      "section_id": "introduction",
      "title": "Introduction to Sedentarism",
      "summary": "Deep analysis of sedentarism as discrepancy between our nomadic ancestral biology and modern environment. Explains how our ancestors lived for over two million years in constant movement, and how the agricultural revolution 10,000 years ago transformed us into sedentary beings, creating a mismatch that generates civilization diseases and problematic cellular adaptations.",
      "key_concepts": ["sedentarism", "nomadic_life", "natural_movement"],
      "summary_length": 780
    },
    "common_problems": {
      "section_id": "common_problems",
      "title": "Common Problems: Mobility Limitations, Pain and Stress",
      "summary": "Scientific exploration of how the nervous system processes movement and pain, explaining concepts like proprioception, brain maps, nociception and sensitization. Analyzes the relationship between trunk stability and limb mobility, and how muscle rigidity acts as brain protection mechanism against movements perceived as unsafe.",
      "key_concepts": ["chronic_pain", "brain_maps", "proximal_stability"],
      "summary_length": 720
    },
    "three_steps": {
      "section_id": "three_steps", 
      "title": "3 Steps to Exit Sedentarism",
      "summary": "Presentation of the central methodology: three specific movements that address the root causes of sedentarism. Walking more as accessible natural activity, sitting more on the ground to strengthen postural musculature and hip mobility, and hanging more from hands to develop grip and decompress joints. Includes breathing as tool to control autonomic nervous system.",
      "key_concepts": ["three_steps", "walking", "floor_sitting", "hanging", "breathing"],
      "summary_length": 920
    },
    "step_1": {
      "section_id": "step_1",
      "title": "Walking More",
      "summary": "Explanation of walking as the most natural activity for humans. Requires no special equipment and is accessible to all. Benefits include improved bone density, circulation, foot health and postural muscle activation. More effective to distribute small walks throughout the day than doing one long walk.",
      "key_concepts": ["walking", "base_movement", "bone_density"],
      "summary_length": 650
    },
    "step_2": {
      "section_id": "step_2",
      "title": "Sitting More on the Ground",
      "summary": "Analysis of how chairs provide external stability that atrophies postural musculature and reduces range of motion. Sitting on the ground forces use of postural muscles, constant posture changes and joint strengthening. This practice improves strength, balance and lower body mobility, relating to greater longevity.",
      "key_concepts": ["floor_sitting", "postural_musculature", "hip_mobility"],
      "summary_length": 680
    },
    "step_3": {
      "section_id": "step_3",
      "title": "Hanging More from Hands",
      "summary": "As primates, we are biologically designed to hang. Lack of this movement weakens grip, tendons and ligaments of the upper body, creating shoulder imbalances. Progressive hanging strengthens grip, decompresses joints and improves mobility and control of shoulders and scapulae.",
      "key_concepts": ["hanging", "grip_strength", "joint_decompression"],
      "summary_length": 620
    }
  },
  
  "hierarchy_index": {
    "0": ["book"],
    "1": ["introduction", "common_problems", "three_steps", "conclusions"],
    "2": ["step_1", "step_2", "step_3", "extra_step"]
  },
  
  "parent_child_map": {
    "book": ["introduction", "common_problems", "three_steps", "conclusions"],
    "three_steps": ["step_1", "step_2", "step_3", "extra_step"]
  },
  
  "total_sections": 8,
  "avg_summary_length": 740,
  "total_concepts": 4
}
```

### **JSON Schema and Versioning**

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

**Consumer Usage**:
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
# 3 Steps Against Sedentarism - Cognitive Reading Summary

> **Processing**: Two-pass cognitive reading | 3 refinements | 5 enrichments

## 📖 Document Summary
Final enriched understanding of the complete document...

## 📄 Section Summaries

### Introduction to Sedentarism ✨ *Refined + Enriched*
Final summary incorporating understanding from later sections...

**Note**: This summary was refined during first pass when the specific 3-step method became clear.

### Common Problems: Mobility Limitations, Pain and Stress ✨ *Enriched*  
Final summary enriched with global context about how problems connect with solutions...

**Note**: This summary was enriched during second pass with complete document context about the 3 steps.

### 3 Steps to Exit Sedentarism ✨ *Refined + Enriched*
Final summary showing the three specific movements (walking more, sitting on ground, hanging) as systematic intervention...

**Note**: This summary was refined during first pass and enriched during second pass.

---

## 🔄 Cognitive Processing Notes

**Refinements made during first pass**: 3
- Introduction: Updated when specific movement solutions became clear
- 3 steps section: Updated when connection between problems and specific movements became clear

**Enrichments made during second pass**: 5  
- All sections enriched with complete document context
- Connections between movement problems and specific movement solutions became clearer

**Key insight**: The two-pass approach revealed the book's coherent methodology where each section builds toward the specific 3-step solution (walking more, sitting on ground, hanging).
```

### **CLI Output** (Show difference)

```bash
$ cognitive-reader book.md

✅ Complete Cognitive Reading

📊 Document Analysis:
- Total sections: 15
- Identified concepts: 12
- Average summary length: 740 characters

📄 Output saved to: book_cognitive_summary.json
```

---

## 🧪 Development and Testing Requirements

### **Development Mode Support**

**Required Development Features**:
- **Dry-run mode**: Enable testing without LLM API calls
- **Component isolation**: Ability to test first pass and second pass independently
- **Cognitive feature toggles**: Enable/disable refinement and second pass separately
- **Performance comparison**: Compare cognitive vs. sequential processing results
- **Processing metrics**: Clear report of cognitive processing statistics

**Configuration Requirements**:
- All cognitive features must be configurable via environment variables
- Must support incremental feature testing (enable only refinement, or only second pass)
- Must provide development-friendly defaults for testing
- Comprehensive cognitive feature configuration testing

### **Testing Strategy**

**Functional Testing Requirements**:
- **Refinement validation**: Verify refinements improve understanding quality
- **Enrichment validation**: Verify second pass adds meaningful context
- **Dual model testing**: Validate fast model for first pass, quality model for second pass
- **Cognitive benefit demonstration**: Show clear difference vs. traditional approaches

**Performance Testing Requirements**:
- **Memory usage**: No significant memory increase for basic cognitive features
- **LLM call optimization**: Efficient context reuse across passes
- **Scalability**: Performance must remain acceptable for large documents

**Quality Assurance Requirements**:
- **Author voice preservation**: Cognitive processing must maintain content fidelity
- **Coherence validation**: Refinements and enrichments must improve coherence
- **Regression testing**: Ensure cognitive features don't break existing functionality
- **Edge case handling**: Handle documents where refinement/enrichment provide minimal value

---

## 🎯 Development Phases

### **Foundation: Cognitive Data Models**

**Goals**:
- Implement complete cognitive data models
- Create cognitive feature configuration system
- Establish foundation for cognitive features

**Deliverables**:
- Enhanced `SectionSummary` model with cognitive tracking
- Updated `CognitiveKnowledge` model with processing statistics
- Extended `CognitiveConfig` with cognitive feature toggles
- Complete cognitive feature testing

### **First Pass: Progressive Refinement**

**Goals**:
- Implement refinement capability in progressive reading
- Add refinement detection and summary updates
- Implement efficient refinement detection

**Deliverables**:
- Enhanced `ProgressiveReader` with refinement capability
- Refinement detection algorithm implementation
- Refinement threshold configuration
- Unit testing for refinement features

### **Second Pass: Contextual Enrichment**

**Goals**:
- Implement enrichment capability with global context
- Add second pass processing to main reading flow
- Integrate first pass and second pass results

**Deliverables**:
- `ContextualEnricher` component implementation
- Second pass integration into main reading flow
- Enrichment detection and tracking
- Complete two-pass flow testing

### **Validation: Testing and Optimization**

**Goals**:
- Validate cognitive processing benefits with real documents
- Performance testing and optimization
- Documentation and examples creation

**Deliverables**:
- Updated output formats with cognitive metadata
- Performance benchmarking with dual model configurations
- "3 steps against sedentarism" validation testing
- User documentation and examples
- MVP v2.0 release

---

## 📈 Success Metrics (MVP Goals)

### **Proof of Concept Goals**
- ✅ **Demonstrate cognitive difference**: Clear difference between cognitive reading and traditional fragmented processing
- ✅ **Refinement validation**: Show examples where understanding improved during first pass  
- ✅ **Enrichment validation**: Show examples where second pass added value
- ✅ **"3 steps" test**: Successfully process sample chapters with cognitive approach
- ✅ **Dual model validation**: Demonstrate benefits of fast/quality model strategy

### **Technical Requirements**
- ✅ **Clean API**: Simple and focused interface for cognitive reading
- ✅ **Performance optimization**: Effective dual model strategy for speed/quality balance
- ✅ **Memory efficiency**: Efficient processing with multiple model configurations
- ✅ **Development friendly**: Comprehensive dry-run and configuration options

### **Quality Indicators**
- ✅ **Coherent refinements**: Refinements must improve summary quality
- ✅ **Valuable enrichments**: Second pass must add meaningful context
- ✅ **Author voice preservation**: Maintain fidelity to original content
- ✅ **Clear output quality**: Final summaries and concepts demonstrate superior understanding
- ✅ **Model effectiveness**: Fast model enables speed, quality model improves depth

---

## 📚 Testing with Real Document

### **Example Document for Validation**

The project includes a reduced version of the real book "3 pasos contra el sedentarismo" in `examples/3 pasos contra el sedentarismo.md` to enable **realistic testing** and **quality validation**.

#### **Document Structure** (Real Content)
```
3 pasos contra el sedentarismo.md
├── Introduction to Sedentarism
│   ├── What is Sedentarism?
│   │   ├── From Nomads to Sedentary
│   │   ├── Civilization Diseases
│   │   ├── Specialization is Key
│   │   ├── Our Cells Adapt
│   │   └── Conclusions
├── Common Problems: Mobility Limitations, Pain and Stress
│   ├── Nervous System
│   ├── Mobility  
│   └── Pain
├── 3 Steps to Exit Sedentarism
│   ├── Walking More
│   ├── Sitting More on the Ground
│   ├── Hanging More from Hands
│   ├── Extra Step: Breathing
│   └── What Now? Next Steps
└── Conclusions
```

#### **Key Testing Benefits**

1. **🎯 Authentic Content**: Real author voice and methodology
2. **🔬 Quality Validation**: Compare cognitive vs. traditional processing
3. **📊 Concept Extraction**: Validate extraction of domain-specific terms
4. **🏗️ Hierarchy Testing**: Multi-level structure with logical relationships
5. **⚡ Performance Testing**: Appropriately sized document for realistic but manageable testing

#### **Recommended Test Cases**

```python
# Test Case 1: Complete Cognitive Processing
test_file = "examples/3 pasos contra el sedentarismo.md"
result = cognitive_reader.process_document(
    file_path=test_file,
    enable_second_pass=True,
    enable_refinement=True
)

# Validate authentic concept extraction
expected_concepts = [
    "sedentarism", "nomadic_life", "natural_movement", 
    "three_steps", "chronic_pain", "brain_maps"
]

# Test Case 2: Quality Comparison
traditional_chunks = chunk_processor.process(test_file)
cognitive_summaries = result.hierarchical_summaries

# Cognitive summaries should show:
# ✅ Coherent understanding of methodology
# ✅ Logical progression from problems to solutions  
# ✅ Preserved author voice and specific terminology
# ✅ Connected concepts across sections
```

#### **Quality Indicators to Validate**

- **📖 Coherent Book Summary**: Must capture central methodology and progression
- **🔗 Connected Concepts**: The `sedentarism` → `three_steps` relationship must be clear
- **🎯 Precise Terminology**: Specific terms like "proprioception", "nociception" 
- **📚 Preserved Voice**: Maintains scientific but accessible author tone
- **🧩 Logical Hierarchy**: Flow Introduction → Problems → Solutions → Conclusions

---

## 🚀 Future Development (Post-MVP)

### **Advanced Cognitive Features**
- **Iterative multi-pass reading**: Extend beyond 2 passes to N-pass cognitive processing
  - Configurable number of passes (3, 4, 5+ re-readings)
  - Each pass deepens understanding and iteratively refines concepts
  - Diminishing returns detection to automatically optimize number of passes
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

**Minimal Cognitive Reading**: The first system to implement **basic two-pass human-like reading process** with:

1. ✅ **Progressive + Refinement**: First pass that can update understanding as context grows
2. ✅ **Global Enrichment**: Second pass that enriches with complete document context  
3. ✅ **Integrated Summaries**: Final output reflecting deep understanding without process metadata
4. ✅ **Proof of Concept**: Demonstrate clear difference from chunk-based fragmentation

**MVP v2** proves that **cognitive reading works differently** from sequential processing, establishing the foundation for more advanced cognitive features in future phases.

---

*This specification defines the minimum viable cognitive reading system that demonstrates human-like understanding evolution while maintaining simplicity and implementability.*