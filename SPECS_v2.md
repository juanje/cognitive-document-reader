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
Implement the **absolute minimum** to demonstrate cognitive reading vs. fragmented chunks:
- ✅ Two-pass reading (progressive + simple enrichment)
- ✅ Basic summary refinement when understanding significantly changes
- ✅ Accumulated context instead of isolated chunks
- ✅ Simple second-pass enrichment with global context

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
├── src/cognitive_reader/          # Main source code package
│   ├── __init__.py               # Public API exports
│   ├── models/                   # Pydantic data models
│   ├── core/                     # Core cognitive reading logic  
│   ├── parsers/                  # Document parsing components
│   ├── llm/                      # LLM integration
│   ├── utils/                    # Utility functions
│   └── cli/                      # Command-line interface
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/             # Integration tests
│   └── fixtures/                # Test data and fixtures
├── examples/                     # Usage examples and demos
├── pyproject.toml               # Project configuration (uv format)
├── README.md                    # English documentation
└── .env.example                 # Environment configuration template
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

### **1. High-Quality Summaries for Human Reading/Study**
   - Summaries that evolve during reading process  
   - Contextual maps showing knowledge development
   - Progressive learning paths through complex documents

### **2. Enriched Metadata for AI Projects**
   - Training data that preserves evolution of understanding
   - Context-rich information with refinement traceability  
   - Structured document knowledge with emergent relationships

### 🧠 **Core Innovation: Two-Pass Cognitive Processing**

Unlike traditional document processors that fragment content, **Cognitive Document Reader v2** implements the complete human reading process:

#### 🔄 **First Pass: Progressive Construction + Continuous Refinement**
1. **Sequential progressive reading** with context accumulation
2. **Evolutionary summaries** that update as new information is encountered
3. **Hierarchical refinement** where subsections update parent sections
4. **Emergent concept detection** as ideas become clear with context

#### 🔍 **Second Pass: Contextual Enrichment**
1. **Informed re-reading** with complete document understanding
2. **Deep connection identification** between previously separate concepts
3. **Relationship enhancement** that only becomes visible with full context
4. **Final synthesis** integrating all knowledge coherently

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

**Previous MVP (v1)**: Sequential processing with basic synthesis  
**New MVP (v2)**: **Minimal** two-pass cognitive reading to prove the concept

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
   - **Basic JSON**: Include which summaries got refined and why
   - **Simple Markdown**: Show evolution annotations where refinement occurred
   - **Comparison**: Clearly show difference from v1 sequential output

#### 5. **Development Essentials** (For Testing)
   - **Dry-run mode**: Test without LLM costs
   - **Simple logging**: Track what got refined
   - **Configuration**: Enable/disable second pass and refinement

### 🎯 **Success Criteria for MVP v2**

- ✅ **Proof of concept**: Clearly demonstrate different results than sequential processing
- ✅ **"3 pasos" test**: Successfully process the book with cognitive approach
- ✅ **Refinement examples**: Show cases where understanding evolved during reading
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
    """Document section with hierarchical structure (unchanged from v1)"""
    model_config = ConfigDict(frozen=True)
    
    id: str                                    # Unique section identifier
    title: str                                 # Section title (cleaned)
    content: str                               # Section text content
    level: int                                 # Hierarchy level (0=document, 1=chapter, 2=section, etc.)
    parent_id: Optional[str] = None            # Parent section ID (None for root)
    children_ids: List[str] = Field(default_factory=list)  # Child section IDs
    order_index: int                           # Order within parent

class SectionSummary(BaseModel):
    """Section summary with cognitive processing tracking"""
    section_id: str                            # Reference to DocumentSection.id
    title: str                                 # Section title
    summary: str                               # Final summary (after all processing)
    key_concepts: List[str] = Field(default_factory=list)  # Identified key concepts
    
    # Cognitive processing flags
    was_refined: bool = False                  # True if refined during first pass
    was_enriched: bool = False                 # True if enhanced during second pass
    
    # Optional refinement context (implementation can choose level of detail)
    refinement_reason: Optional[str] = None    # Why it was refined (if applicable)
    enrichment_details: Optional[str] = None   # What was added during enrichment

class CognitiveKnowledge(BaseModel):
    """Complete knowledge extracted with cognitive processing"""
    # Document identification
    document_title: str
    document_summary: str                      # Final document-level summary
    detected_language: LanguageCode
    
    # Document structure and content
    sections: List[DocumentSection]            # Hierarchical document structure
    section_summaries: Dict[str, SectionSummary]  # Section ID -> Summary mapping
    
    # Cognitive processing metadata
    processing_approach: str = "two_pass_cognitive"  # Processing method used
    refinements_made: int = 0                  # Number of sections refined
    second_pass_enrichments: int = 0           # Number of sections enriched
    
    # Standard processing metadata
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)

class CognitiveConfig(BaseModel):
    """Configuration for cognitive document reading"""
    
    # LLM Configuration (compatible with v1)
    model_name: str = Field(default="qwen3:8b", description="LLM model name")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="LLM temperature")
    
    # Document Processing (compatible with v1)
    chunk_size: int = Field(default=1000, gt=100, description="Text chunk size for processing")
    chunk_overlap: int = Field(default=200, ge=0, description="Overlap between chunks")
    context_window: int = Field(default=4096, gt=0, description="LLM context window limit")
    
    # Performance Settings (compatible with v1)
    timeout_seconds: int = Field(default=120, gt=0, description="Request timeout")
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    document_language: LanguageCode = Field(default=LanguageCode.AUTO, description="Document language")
    
    # Cognitive Features (new in v2)
    enable_second_pass: bool = Field(default=True, description="Enable second pass enrichment")
    enable_refinement: bool = Field(default=True, description="Enable first pass refinement")
    refinement_threshold: float = Field(
        default=0.4, 
        ge=0.0, 
        le=1.0, 
        description="Threshold for triggering refinement (0.0=never, 1.0=always)"
    )
    
    # Development Features (compatible with v1)
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
            
            # Development features
            dry_run=os.getenv("COGNITIVE_READER_DRY_RUN", "false").lower() == "true",
            mock_responses=os.getenv("COGNITIVE_READER_MOCK_RESPONSES", "false").lower() == "true",
        )

# Environment Variables Reference
COGNITIVE_READER_ENV_VARS = {
    # LLM Configuration
    "COGNITIVE_READER_MODEL": "LLM model name (default: qwen3:8b)",
    "COGNITIVE_READER_TEMPERATURE": "LLM temperature 0.0-2.0 (default: 0.1)",
    
    # Processing Configuration  
    "COGNITIVE_READER_CHUNK_SIZE": "Text chunk size (default: 1000)",
    "COGNITIVE_READER_CHUNK_OVERLAP": "Chunk overlap (default: 200)",
    "COGNITIVE_READER_CONTEXT_WINDOW": "LLM context limit (default: 4096)",
    "COGNITIVE_READER_LANGUAGE": "Document language auto/en/es (default: auto)",
    
    # Cognitive Features
    "COGNITIVE_READER_ENABLE_SECOND_PASS": "Enable second pass true/false (default: true)",
    "COGNITIVE_READER_ENABLE_REFINEMENT": "Enable refinement true/false (default: true)",
    "COGNITIVE_READER_REFINEMENT_THRESHOLD": "Refinement threshold 0.0-1.0 (default: 0.4)",
    
    # Performance & Development
    "COGNITIVE_READER_TIMEOUT_SECONDS": "Request timeout (default: 120)",
    "COGNITIVE_READER_MAX_RETRIES": "Max retries (default: 3)",
    "COGNITIVE_READER_DRY_RUN": "Dry run mode true/false (default: false)",
    "COGNITIVE_READER_MOCK_RESPONSES": "Mock responses true/false (default: false)",
}
```

### 📚 **API Requirements**

**Interface Compatibility**:
- Must maintain same primary interface as v1: `read_document(file_path, config) -> Knowledge`
- Must support same configuration patterns as v1 via environment variables
- Must provide backward compatibility when cognitive features are disabled

**New Configuration Options**:
- `enable_second_pass`: Boolean to enable/disable second pass enrichment
- `enable_refinement`: Boolean to enable/disable first pass refinement  
- `refinement_threshold`: Float (0.0-1.0) to control refinement sensitivity

**Enhanced Return Data**:
- Must include cognitive processing statistics (refinements made, enrichments made)
- Must indicate which sections were processed with cognitive features
- Must preserve all v1 return data for compatibility
- Must clearly distinguish cognitive vs sequential processing approach

---

## 🏗️ Cognitive Architecture v2

### **System Components**

```
CognitiveReader (Main Engine)
├── StructureDetector (unchanged from v1)
├── ProgressiveReader (enhanced with refinement capability)
├── ContextualEnricher (new component for second pass)
└── CognitiveSynthesizer (enhanced with cognitive metadata)
```

### **Component Responsibilities**

#### **CognitiveReader** (Main Orchestrator)
**Purpose**: Coordinate two-pass cognitive reading process

**Responsibilities**:
- Orchestrate complete two-pass reading workflow
- Manage configuration for cognitive features (refinement, second pass)
- Coordinate between first pass and second pass processing
- Provide same API interface as v1 for compatibility
- Track and report cognitive processing metrics

**Interface Requirements**:
- `read_document(file_path, config) -> CognitiveKnowledge`: Primary interface (same as v1)
- Must support both cognitive (two-pass) and sequential (v1-compatible) modes
- Must provide cognitive processing statistics in results

#### **ProgressiveReader** (Enhanced)
**Purpose**: Execute first pass with progressive reading and refinement capability

**Responsibilities**:
- Process sections sequentially with accumulated context (same as v1)
- Detect when new context significantly changes understanding of previous sections
- Update previous section summaries when refinement is needed
- Track refinement events and reasons
- Maintain context accumulation across section processing

**Requirements**:
- Must be configurable to enable/disable refinement capability
- Must maintain v1 compatibility when refinement is disabled
- Must provide refinement threshold configuration
- Must track which sections were refined and why

#### **ContextualEnricher** (New Component)
**Purpose**: Execute second pass enrichment with global document context

**Responsibilities**:
- Re-read sections with complete document understanding
- Identify opportunities for enrichment with global context
- Generate enhanced summaries that incorporate full document perspective
- Distinguish between meaningful enrichments and trivial changes
- Preserve first pass refinements while adding second pass insights

**Requirements**:
- Must be configurable to enable/disable second pass processing
- Must work with results from ProgressiveReader first pass
- Must track enrichment events and added value
- Must maintain processing efficiency

#### **CognitiveSynthesizer** (Enhanced)
**Purpose**: Generate final document synthesis with cognitive processing awareness

**Responsibilities**:
- Create hierarchical document synthesis (same as v1)
- Incorporate cognitive processing metadata into final results
- Note which sections underwent refinement or enrichment
- Generate cognitive processing summary for output

**Requirements**:
- Must maintain v1 synthesis quality and approach
- Must clearly indicate cognitive processing events in output
- Must provide summary of cognitive processing benefits

---

## 🔄 Cognitive Process Requirements

### **Two-Pass Processing Flow**

```
Document Input
    ↓
Structure Detection (same as v1)
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
- **Context Accumulation**: Build comprehensive context as reading progresses
- **Refinement Detection**: Identify when new information significantly changes understanding of previous sections
- **Summary Updates**: Update previous section summaries when understanding evolves
- **Refinement Tracking**: Record which summaries were refined and why

**Technical Requirements:**
- Must maintain backward compatibility with v1 progressive reading
- Refinement threshold configurable via `refinement_threshold` parameter
- Refinement can be disabled via `enable_refinement` configuration
- Must track number of refinements made for metrics

### **Second Pass Requirements**

**Functional Requirements:**
- **Global Context Re-reading**: Re-process each section with complete document context
- **Enrichment Detection**: Identify cases where global context adds meaningful insights
- **Summary Enhancement**: Improve summaries with insights only available after complete reading
- **Integration**: Combine first pass and second pass results coherently

**Technical Requirements:**
- Second pass can be disabled via `enable_second_pass` configuration
- Must detect and track meaningful enrichments vs trivial changes
- Should preserve refinements from first pass while adding enrichments
- Must maintain processing performance within acceptable bounds

---

## 📊 Simple Output Formats v2

### **Basic Cognitive JSON** (Minimal difference from v1)

```json
{
  "document_title": "3 Pasos Contra el Sedentarismo",
  "document_summary": "Final enriched summary...",
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
      "summary": "Final summary after both passes...",
      "key_concepts": ["sedentarismo", "entorno_sedentario", "salud_compleja"],
      "was_refined": true,
      "was_enriched": true
    },
    "seccion_2": {
      "section_id": "seccion_2", 
      "title": "Problemas comunes: limitaciones de la movilidad, dolor y estrés",
      "summary": "Final summary after both passes...",
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

✅ Cognitive Reading Complete (Two-pass processing)

📊 Processing Summary:
- Approach: Two-pass cognitive reading  
- First pass: Progressive reading + 3 refinements
- Second pass: Global context enrichment + 5 enrichments
- Total sections: 15
- Processing time: 45.2s

💡 Cognitive Benefits Detected:
- 3 sections had improved understanding during first pass
- 5 sections gained additional context during second pass  
- Author's methodology preserved and clarified

📄 Output saved to: book_cognitive_summary.json
```

---

## 🧪 Development & Testing Requirements

### **Development Mode Support**

**Required Development Features**:
- **Dry-run mode**: Enable testing without LLM API calls
- **Component isolation**: Ability to test first pass and second pass independently
- **Cognitive feature toggles**: Enable/disable refinement and second pass separately
- **Performance comparison**: Compare cognitive vs sequential processing results
- **Processing metrics**: Clear reporting of cognitive processing statistics

**Configuration Requirements**:
- All cognitive features must be configurable via environment variables
- Must support incremental feature testing (enable only refinement, or only second pass)
- Must provide development-friendly defaults for testing
- Must maintain v1 compatibility when cognitive features are disabled

### **Testing Strategy**

**Functional Testing Requirements**:
- **Refinement validation**: Verify refinements improve understanding quality
- **Enrichment validation**: Verify second pass adds meaningful context
- **Compatibility testing**: Ensure v1 mode produces equivalent results to v1
- **Cognitive benefit demonstration**: Show clear difference between approaches

**Performance Testing Requirements**:
- **Processing time**: Two-pass processing should be <2x sequential processing time
- **Memory usage**: No significant memory increase for basic cognitive features
- **LLM call optimization**: Efficient context reuse across passes
- **Scalability**: Performance must remain acceptable for documents up to 300 pages

**Quality Assurance Requirements**:
- **Author voice preservation**: Cognitive processing must maintain content fidelity
- **Coherence validation**: Refinements and enrichments must improve coherence
- **Regression testing**: Ensure cognitive features don't break existing functionality
- **Edge case handling**: Handle documents where refinement/enrichment provide minimal value

---

## 🎯 Development Phases: v1 → v2

### **Phase 1: Data Model Enhancement (Weeks 1-2)**

**Objectives**:
- Extend existing data models to support cognitive processing metadata
- Maintain full backward compatibility with v1
- Add configuration options for cognitive features

**Deliverables**:
- Enhanced `SectionSummary` model with cognitive tracking
- Updated `CognitiveKnowledge` model with processing statistics
- Extended `CognitiveConfig` with cognitive feature toggles
- Backward compatibility validation

### **Phase 2: First Pass Cognitive Features (Weeks 3-4)**

**Objectives**:
- Implement refinement capability in progressive reading
- Add refinement detection and summary updating
- Maintain v1 compatibility mode

**Deliverables**:
- Enhanced `ProgressiveReader` with refinement capability
- Refinement detection algorithm implementation
- Refinement threshold configuration
- Unit testing for refinement features

### **Phase 3: Second Pass Implementation (Weeks 5-6)**

**Objectives**:
- Implement global context enrichment capability
- Add second pass processing to main reading workflow
- Integrate first pass and second pass results

**Deliverables**:
- `ContextualEnricher` component implementation
- Second pass integration in main reading workflow
- Enrichment detection and tracking
- Complete two-pass flow testing

### **Phase 4: Integration & Validation (Weeks 7-8)**

**Objectives**:
- Validate cognitive processing benefits with real documents
- Performance testing and optimization
- Documentation and example creation

**Deliverables**:
- Updated output formats with cognitive metadata
- Performance benchmarking vs v1
- "3 pasos contra el sedentarismo" validation testing
- User documentation and examples
- MVP v2.0 release

---

## 📈 Success Metrics v2 (Minimal)

### **Proof of Concept Goals**
- ✅ **Demonstrate cognitive difference**: Clear difference between v1 sequential and v2 cognitive output
- ✅ **Refinement validation**: Show examples where understanding improved during first pass  
- ✅ **Enrichment validation**: Show examples where second pass added value
- ✅ **"3 pasos" test**: Successfully process sample chapters with cognitive approach

### **Technical Requirements**
- ✅ **API compatibility**: Same simple API as v1 (minimal breaking changes)
- ✅ **Performance acceptability**: <2x processing time vs v1 for cognitive features
- ✅ **Memory efficiency**: No significant memory increase for basic two-pass processing
- ✅ **Development friendly**: Dry-run and configuration options work correctly

### **Quality Indicators**
- ✅ **Coherent refinements**: Refinements should improve summary quality
- ✅ **Valuable enrichments**: Second pass should add meaningful context
- ✅ **Author voice preservation**: Maintain fidelity to original content
- ✅ **Clear evolution tracking**: Simple before/after comparisons show value

---

## 🚀 Future Development (Post-MVP)

### **Phase 2: Enhanced Cognitive Features**
- **Complex emergent concept detection**: More sophisticated concept emergence patterns
- **Knowledge graph generation**: Export relationships to graph databases
- **Multi-document cognitive synthesis**: Read across related documents
- **Advanced refinement strategies**: More intelligent refinement triggers

### **Phase 3: Advanced Integration**
- **Contradiction detection**: Handle inconsistencies intelligently  
- **Expert feedback loops**: Incorporate human expert refinements
- **Adaptive cognitive strategies**: Adjust approach based on document type
- **Performance optimization**: Advanced caching and parallel processing

---

## 💡 Key Innovation of MVP v2

**Minimal Cognitive Reading**: The first system to implement **basic two-pass human reading process** with:

1. ✅ **Progressive + Refinement**: First pass that can update understanding as context grows
2. ✅ **Global Enrichment**: Second pass that enriches with complete document context  
3. ✅ **Simple Evolution Tracking**: Basic before/after tracking of understanding changes
4. ✅ **Proof of Concept**: Demonstrate clear difference from chunk-based fragmentation

**MVP v2** proves that **cognitive reading works differently** than sequential processing, establishing the foundation for more advanced cognitive features in future phases.

---

*This specification defines the minimal viable cognitive reading system that demonstrates human-like understanding evolution while maintaining simplicity and implementability.*
