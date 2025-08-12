# Cognitive Document Reader - Technical Specifications

## 🧠 Purpose and Vision

**Cognitive Document Reader** is a Python library that simulates human-like document reading through progressive understanding and hierarchical synthesis. The project addresses two primary use cases:

### 🎯 **Primary Uses**
1. **High-Quality Summaries for Human Reading/Study**
   - Structured summaries that preserve narrative flow
   - Conceptual maps for better understanding
   - Progressive learning paths through complex documents

2. **Enriched Metadata for AI Projects**
   - Enhanced training data for LLM fine-tuning
   - Context-rich information for RAG systems
   - Structured document knowledge for AI workflows

### 🏗️ **Design Principles**
- **Human-Like Reading**: Progressive knowledge accumulation mimicking human cognition
- **Hierarchical Understanding**: Multi-level document comprehension (document → sections → concepts)
- **Minimize LLM Calls**: Efficient batching, caching, and context reuse strategies
- **Configurability**: All settings via environment variables, no hardcoded values
- **Testability**: Comprehensive testing with mocks and fixtures
- **Simplicity**: MVP focused on essential functionality without bloat

---

## 🏗️ Development Standards

### Code Quality
- **Mandatory Type Annotations**: All functions, methods and class members MUST have type annotations using the most specific types possible
- **Complete Docstrings**: All functions, methods and classes MUST have Google-style docstrings explaining purpose, parameters, return values and exceptions
- **Test Coverage**: Minimum 90% coverage goal using `pytest`
- **Robust Exception Handling**: Use specific exception types, custom classes when needed, avoid generic `except` clauses

### Prompt Management
- **Dedicated Module**: LLM prompts must be in dedicated modules with versioning
- **Reusable Templates**: Prompts as parameterizable and testable templates
- **Context Management**: Efficient context handling using appropriate data structures
- **Multi-language**: Language-specific prompts with fallbacks

### Performance and Optimization
- **Minimize LLM Calls**: Batching, caching and context reuse strategies
- **Async Programming**: Use `async`/`await` for I/O bound operations
- **Caching Strategy**: Apply `functools.lru_cache` and `@cache` to avoid recalculations
- **Memory Efficiency**: Proper resource release to prevent memory leaks
- **Resource Monitoring**: Monitor resource usage and identify bottlenecks

### Architecture and Design
- **Single Responsibility**: Each module/file with well-defined responsibility
- **Composition over Inheritance**: Favor composition over inheritance
- **Explicit over Implicit**: Explicit code that clearly communicates intent
- **Modular Design**: Reusable and independent components

### Security
- **Input Validation**: Robust validation of user inputs
- **External Data Handling**: Secure handling of external data and documents
- **Error Information**: Informative error messages without exposing sensitive information

### Configuration and Environment
- **Environment Variables**: Everything configurable via environment variables (.env)
- **No Hard-coding**: No hardcoded values (models, temperatures, etc.)
- **Pydantic Models**: Use Pydantic for configuration and data validation
- **Flexible Configuration**: Support for .env both in standalone and module mode

### Language and Documentation
- **Code in English**: All comments, variable names, and documentation in English
- **Multi-language Templates**: Only prompts/templates can be in specific languages
- **README in English**: Main documentation in English for international audience

### Dependencies Strategy
- **Minimal Dependencies**: Only essential dependencies in MVP
- **Pydantic**: For data validation and configuration
- **LangChain Integration**: Consider LangChain for advanced prompt management (Phase 2+)
- **Vector Databases**: `faiss`/`chroma` for semantic search (Phase 3+)
- **Performance Libraries**: `psutil` for resource monitoring

### Code Management (MVP - Simplicity)
- **Simple Pre-commit**: `ruff format`, `ruff check`, `mypy`, `pytest` before commit
- **Conventional Commits**: Use standard format (`feat:`, `fix:`, `docs:`, `refactor:`) from the start
- **Dynamic Versioning**: Using `hatchling` + `hatch-vcs` (no manual bumping)
- **Basic .gitignore**: `__pycache__`, `.env`, `dist/`, `build/`, `.mypy_cache/`, `htmlcov/`

### MVP Testing
- **Unit Tests**: Basic coverage of core functionality using pytest
- **Mock LLM Calls**: Deterministic tests without real model calls
- **Simple Fixtures**: Basic setup/teardown for tests
- **Fast Tests**: Focus on speed for agile development

### AI Agent Friendly Development

#### Development Modes without LLM Calls
For **vibe coding** and development with AI agents that need to test without costs:

```bash
# Environment variables for development
COGNITIVE_READER_DRY_RUN=true           # No real LLM calls
COGNITIVE_READER_MOCK_RESPONSES=true    # Use simulated responses
COGNITIVE_READER_VALIDATE_CONFIG_ONLY=true  # Only validate configuration

# CLI flags for testing
cognitive-reader --dry-run document.md              # Simulate processing
cognitive-reader --validate-config                  # Only verify config
cognitive-reader --mock-llm-responses document.md   # Use fake responses
```

#### Agent-Friendly Use Cases
```python
# Verify configuration is valid WITHOUT LLM calls
from cognitive_reader import CognitiveReader, ReadingConfig

config = ReadingConfig.from_env()
reader = CognitiveReader(config)

# Only verify configuration - 0 LLM calls
is_valid = await reader.validate_configuration()  # ✅ Safe for agents

# Process with simulated responses - 0 LLM calls  
result = await reader.read_document("doc.md", dry_run=True)  # ✅ Safe for agents

# Process REAL - EXPENSIVE, only when necessary
result = await reader.read_document("doc.md")  # ⚠️ Makes real LLM calls
```

#### Benefits for AI Agents
- ✅ **Zero Cost Testing**: Agents can test without spending money/resources
- ✅ **Fast Validation**: Verify configurations instantly  
- ✅ **Predictable Outputs**: Deterministic simulated responses
- ✅ **Development Friendly**: Fast iteration without LLM waits

#### Specific Use Cases for Agents

**🤖 Agent Testing Framework:**
```python
# Agent can verify installation and configuration WITHOUT cost
async def test_cognitive_reader_setup():
    reader = CognitiveReader()
    
    # 1. Verify dependencies are installed
    is_available = reader.check_dependencies()  # ✅ Safe
    
    # 2. Verify configuration is valid  
    config_valid = await reader.validate_config()  # ✅ Safe
    
    # 3. Test basic parsing with mock
    result = await reader.read_document("sample.md", dry_run=True)  # ✅ Safe
    
    return all([is_available, config_valid, result.success])
```

**🔧 Agent Development Loop:**
```bash
# Typical agent development - NO expensive calls:
export COGNITIVE_READER_DEV_MODE=true

# Agent can iterate quickly:
cognitive-reader document.md  # Uses mocks, 0 cost
cognitive-reader --validate-config  # Config check only
cognitive-reader document.md --output json | jq .  # Test output parsing
```

**⚠️ When NOT to use these modes:**
- Final validation of real output quality
- Performance benchmarking with real LLMs
- Evaluation of final summary quality

### MVP Documentation
- **Simple README**: Basic installation and usage examples
- **Essential Docstrings**: Google-style for public functions  
- **Minimal Examples**: 1-2 straightforward usage examples
- **No premature documentation**: Focus on working code first

### Conventional Commits from Day One

Use standard format for commits from **day one**:

```bash
feat: add progressive reading functionality
fix: resolve memory leak in document parser
docs: update README with new CLI options
refactor: extract prompt management to separate module
test: add unit tests for hierarchical summarizer
chore: update dependencies and .gitignore

# Examples with scope (optional)
feat(reader): implement multi-pass refinement
fix(parser): handle empty sections gracefully
docs(api): add docstrings to public methods
```

**Immediate benefits:**
- ✅ More readable and professional git history
- ✅ Easy identification of change type
- ✅ Preparation for future automation (changelogs, releases)
- ✅ Industry standard without additional overhead

---

## 🚀 MVP (Phase 1) - Minimum Viable Product

### MVP Scope
The MVP implements the basic cognitive reading cycle with essential functionality:

#### Included Features
1. **Sequential Progressive Reading**
   - Processing in document appearance order
   - Immediate summaries per section
   - Progressive context accumulation

2. **Hierarchical Synthesis**
   - Automatic hierarchical structure detection
   - Parent section synthesis from children
   - Global document summary

3. **Dual API**
   - Use as Python library
   - Standalone CLI with multiple output formats

4. **Output Formats**
   - Structured JSON (for integration with other projects)
   - Enhanced Markdown (for human reading)

5. **Format Support**
   - Markdown (.md) via docling

6. **Language Support**
   - English and Spanish (auto-detection)
   - Prompts in original document language

#### Excluded from MVP
- Multi-pass refinement (Phase 2)
- Concept extraction and glossaries (Phase 2)
- PDF/DOCX/HTML support (Phase 2)
- Advanced navigation and structural maps (Phase 3)
- Web UI or REST API (Future phases)
- Real-time collaborative features

### Project Structure

```
cognitive-document-reader/
├── README.md                           # English documentation
├── README_es.md                        # Spanish documentation  
├── LICENSE                             # MIT License
├── pyproject.toml                      # Dynamic versioning + uv config
├── .env.example                        # Configuration template
├── .gitignore                          # Basic exclusions
├── 
├── src/
│   └── cognitive_reader/
│       ├── __init__.py                 # Public API
│       ├── _version.py                 # Auto-generated version
│       ├── 
│       ├── core/
│       │   ├── __init__.py
│       │   ├── progressive_reader.py   # Main reading engine
│       │   └── synthesizer.py          # Hierarchical synthesis
│       │
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── structure_detector.py   # Hierarchical structure detection
│       │   └── docling_parser.py       # Universal parser via docling
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── client.py               # LLM abstraction (Ollama focus)
│       │   └── prompts.py              # Prompt management
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── config.py               # Configuration models
│       │   ├── document.py             # Document data models
│       │   └── knowledge.py            # Knowledge structures
│       │
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── language.py             # Language detection
│       │   └── resources.py            # Resource management utilities
│       │
│       └── cli/
│           ├── __init__.py
│           └── main.py                 # CLI interface
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                     # Pytest configuration
│   ├── fixtures/                       # Test data
│   ├── unit/                           # Unit tests
│   └── integration/                    # Integration tests
│
└── examples/
    ├── basic_usage.py                  # Simple examples
    ├── library_integration.py          # Use as library
    └── sample_documents/               # Test documents
```

### Basic CLI Usage

```bash
# Install
pip install cognitive-document-reader

# Basic usage
cognitive-reader document.md

# With options  
cognitive-reader document.md --output json --language es

# Development modes
cognitive-reader document.md --dry-run  # No LLM calls
cognitive-reader --validate-config      # Config check only
```

### Library Usage

```python
from cognitive_reader import CognitiveReader
from cognitive_reader.models import ReadingConfig

# Basic usage
config = ReadingConfig(
    model_name="qwen3:8b",  # Best performance, fallback: "llama3.1:8b"
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

### Pydantic Models

```python
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class LanguageCode(str, Enum):
    AUTO = "auto"
    EN = "en"
    ES = "es"

class DocumentSection(BaseModel):
    """Individual document section with hierarchy info"""
    model_config = ConfigDict(frozen=True)
    
    id: str
    title: str
    content: str
    level: int
    parent_id: Optional[str] = None
    children_ids: List[str] = Field(default_factory=list)
    order_index: int

class SectionSummary(BaseModel):
    """Summary of a document section"""
    section_id: str
    title: str
    summary: str
    key_concepts: List[str] = Field(default_factory=list)

class DocumentKnowledge(BaseModel):
    """Complete knowledge extracted from document"""
    document_title: str
    document_summary: str
    detected_language: LanguageCode
    sections: List[DocumentSection]
    section_summaries: Dict[str, SectionSummary]
    processing_metadata: Dict[str, Any]

class ReadingConfig(BaseModel):
    """Simplified reading configuration for MVP - focus on essentials"""
    # LLM Configuration (proven models)
    model_name: str = Field(default="qwen3:8b")  # Best results, llama3.1:8b as fallback
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)  # Low for consistent summaries
    
    # Document Processing (essential settings)
    chunk_size: int = Field(default=1000, gt=100)  # Optimal for cognitive reading
    chunk_overlap: int = Field(default=200, ge=0)  # ~20% overlap maintains continuity
    context_window: int = Field(default=4096, gt=0)  # Standard limit that works
    
    # Performance Settings (simplified)
    timeout_seconds: int = Field(default=120, gt=0)  # Reasonable timeout
    max_retries: int = Field(default=3, ge=0)  # Standard retry count
    
    # Language and Output
    document_language: LanguageCode = Field(default=LanguageCode.AUTO)
    
    # Development modes (AI agent friendly)
    dry_run: bool = Field(default=False)  # Enable dry-run mode (no LLM calls)
    mock_responses: bool = Field(default=False)  # Use simulated responses for testing
    
    @classmethod
    def from_env(cls) -> "ReadingConfig":
        """Create config from environment variables with fallback to defaults"""
        import os
        return cls(
            model_name=os.getenv("COGNITIVE_READER_MODEL", "qwen3:8b"),
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

## 📈 Future Development Phases

### Phase 2: Refinement and Concepts

#### New Features
- **Second Pass Refinement**
  - Summary improvement with global context
  - Deep connection identification
  - Inconsistency correction

- **Concept Extraction**
  - Automatic contextual glossary
  - Cross-references
  - In-context definitions within document

- **Additional Formats**
  - PDF (via docling)
  - DOCX (via docling)
  - HTML (via docling)

- **Enhanced Output**
  - Markdown documents with structured summaries
  - Glossary export
  - Enriched metadata for AI projects
  - HTML

#### Extended API
```python
# Refinement
refined_knowledge = await reader.refine_knowledge(knowledge)

# Concept extraction
concepts = await reader.extract_concepts(knowledge)
print(concepts.glossary)  # Term glossary
print(concepts.references)  # References by concept
```

#### Advanced Configuration (Phase 2+)

```python
class AdvancedReadingConfig(ReadingConfig):
    """Extended configuration for advanced features - Phase 2+"""
    # Additional LLM Configuration
    llm_provider: str = Field(default="ollama")
    validation_model: str = Field(default="deepseek-r1:8b")  # Superior for analysis
    
    # Advanced Document Processing
    max_section_length: int = Field(default=2000, gt=0)  # For hierarchical context
    
    # Performance Settings (proven in production)
    enable_parallel_processing: bool = Field(default=True)
    max_parallel_tasks: int = Field(default=3, gt=0)  # Parallelism without saturation
    
    # Caching Strategy (Phase 3+ when needed)
    cache_enabled: bool = Field(default=True)
    cache_max_memory_mb: int = Field(default=100, gt=0)  # Reasonable memory limit
    cache_expiry_hours: int = Field(default=24, gt=0)  # Appropriate expiration
    cache_strategy: str = Field(default="hybrid")  # Memory + disk hybrid
    
    # Summary Generation (optimized token limits)
    document_summary_max_tokens: int = Field(default=400, gt=0)  # For complete document
    section_summary_max_tokens: int = Field(default=200, gt=0)  # For main sections
    concept_summary_max_tokens: int = Field(default=150, gt=0)  # For key concepts
    
    # Quality Controls (validated thresholds)
    min_confidence: float = Field(default=0.75, ge=0.0, le=1.0)  # Proven quality threshold
    min_coherence_score: float = Field(default=0.6, ge=0.0, le=1.0)  # Contextual validation
    max_concepts_per_document: int = Field(default=8, gt=0)  # Optimal key concepts number
    
    # Additional Development modes
    validate_config_only: bool = Field(default=False)  # Only validate config, no processing
    dev_mode: bool = Field(default=False)  # Enable development mode with all mocks
```

#### Professional Development Tools (Phase 2)
- **Complete CI/CD**
  - GitHub Actions with testing matrix (Python 3.12, 3.13)
  - Automatic pre-commit hooks
  - Dependabot for security updates
  - PyPI release automation with tags

- **Advanced Git Workflow**
  - Feature branches and PR workflow
  - Branch protection rules and code review requirements
  - Automated merge after status checks

- **Quality Assurance**
  - Automatic code coverage reporting
  - Performance benchmarks in CI
  - Dependency vulnerability scanning (safety)
  - Optional code quality gates (SonarCloud/CodeClimate)

### Phase 3: Maps and Navigation

#### New Features
- **Structural Maps**
  - Physical navigation map
  - Conceptual network
  - Idea flow visualization

- **Smart Navigation**
  - Semantic search
  - Reading recommendations
  - Learning paths

#### Extended API
```python
# Structural maps
maps = await reader.create_structural_maps(knowledge)
physical_map = maps.physical_structure
conceptual_map = maps.conceptual_network

# Navigation
navigator = knowledge.create_navigator()
related_sections = navigator.find_related("concept")
learning_path = navigator.create_learning_path(["concept1", "concept2"])
```

### Phase 4: Multi-language and Optimization

#### New Features
- **Complete Multi-language Support**
  - Improved automatic language detection
  - Support for additional languages
  - Summary translation to target languages
  - Language-optimized prompts

- **Reading Metrics**
  - Summary quality
  - Narrative coherence
  - Extraction completeness

- **Automatic Optimization**
  - Parameter adjustment by document and language
  - Optimal pattern detection
  - Continuous prompt improvement

### Phase 5: Integration and Export

#### New Features
- **Database Integration**
- **Advanced Export**
  - Multiple formats (LaTeX, EPUB, etc.)
  - Customizable templates
  - Enriched metadata for AI systems

### LLM Optimization Strategies

#### Call Minimization
- **Smart Batching**: Group related sections in single call
- **Context Reuse**: Reuse accumulated context between consecutive sections
- **Template Optimization**: Efficient templates that generate consistent results

#### Context Window Management
- **Smart Chunking**: Intelligent division respecting context limits (1000 chars proven)
- **Context Prioritization**: Prioritize most relevant context for each section
- **Hierarchical Context**: Use hierarchy to optimize context usage (2000 chars max proven)
- **Fallback Strategies**: Graceful degradation when context exceeded

#### Proven and Optimized Values
Based on successful experience from `extract-to-train`, using values that have demonstrated **excellent production performance**:

**🤖 Optimized Models:**
- **qwen3:8b**: Best results for cognitive reading tasks
- **llama3.1:8b**: Reliable fallback option for instruction following
- **deepseek-r1:8b**: Superior for analysis and quality validation  
- **Temperature 0.1**: Optimal for consistent and faithful summaries

**📄 Efficient Processing:**
- **Chunk Size 1000**: Optimal for cognitive reading - preserves better narrative coherence
- **Overlap 200**: ~20% overlap maintains continuity without excessive redundancy
- **Context Window 4096**: Standard limit that works reliably

**⚡ Validated Performance:**
- **3 parallel tasks**: Maximum parallelism without system saturation
- **120s timeout**: Sufficient time for complex operations without hangs
- **3 retries**: Optimal number to handle temporary failures

**💾 Resource Management (MVP):**
- **Simple approach**: Direct processing without complex caching
- **Memory efficiency**: Proper cleanup after processing
- **Future enhancement**: Caching strategies planned for Phase 3+

**🎯 Quality Thresholds:**
- **Confidence 0.75**: Threshold that ensures high quality without being too restrictive
- **Coherence 0.6**: Limit for contextual validation balanced
- **8 concepts max**: Optimal number of key concepts per document

---

## 🏗️ Detailed Technical Architecture

### Core Components

#### ProgressiveReader
- **Responsibility**: Main reading engine with sequential progressive processing
- **Key Methods**:
  - `read_document(file_path, config)`: Main reading method
  - `_process_section(section, accumulated_context)`: Process individual section
  - `_accumulate_context(section_summary, context)`: Build progressive context

#### StructureDetector  
- **Responsibility**: Detects hierarchical structure using docling and cleans section titles
- **Key Methods**:
  - `detect_structure(document)`: Extracts hierarchical sections
  - `_build_section_tree(elements)`: Builds tree from flat structure
  - `_identify_section_types(sections)`: Classifies content vs container sections
  - `_create_section(text, level, type)`: Creates sections with cleaned titles

**Text Cleaning Features**:
- **Automatic Internal Link Removal**: Strips markdown internal links (`{#anchor}`) from section titles
- **Smart Pattern Matching**: Handles complex anchor patterns with dashes, underscores, and numbers
- **Content Preservation**: Maintains clean, readable titles for better summary quality

#### Synthesizer
- **Responsibility**: Hierarchical synthesis from deepest to shallowest
- **Key Methods**:
  - `synthesize_document(sections, summaries)`: Complete document synthesis
  - `_synthesize_container_section(section, child_summaries)`: Container from children
  - `_synthesize_content_section(section)`: Content section summary

#### LLMClient
- **Responsibility**: Simple LLM abstraction (Ollama focus)
- **Key Methods**:
  - `generate_summary(content, context, prompt_type)`: Generate summaries
  - `_handle_retries(operation)`: Basic retry logic

#### PromptManager
- **Responsibility**: Simple prompt management
- **Key Methods**:
  - `get_prompt(type, language)`: Language-specific prompts
  - `format_prompt(section, context)`: Basic prompt formatting

#### DoclingParser
- **Responsibility**: Universal document parsing
- **Features**:
  - **MVP Support**: Markdown via docling
  - **Future Support**: PDF, DOCX, HTML via docling
  - **Structure Detection**: Hierarchical structure extraction
  - **Content Extraction**: Clean text with metadata preservation

#### Text Processing Utilities
- **Responsibility**: Clean and optimize text for cognitive analysis
- **Features**:
  - **Markdown Internal Link Cleaning**: Automatically removes `{#anchor}` patterns from section titles
  - **Pattern Recognition**: Handles complex anchor patterns (dashes, underscores, numbers)
  - **Content Focus**: Ensures summaries focus on content rather than markdown artifacts

**Supported Patterns**:
```markdown
# Before cleaning
## Introduction {#intro}
## De nómadas a sedentarios {#de-nómadas-a-sedentarios}
## Section 1.2 {#section-1_2-example}

# After cleaning
## Introduction
## De nómadas a sedentarios
## Section 1.2
```

#### Structure Formatting Utilities
- **Responsibility**: Display and analyze document structure for debugging and overview
- **Features**:
  - **Text Formatting**: Indented hierarchical structure for human reading
  - **JSON Formatting**: Structured data with statistics for integration
  - **Compact Formatting**: Single-line summary for verbose logs
  - **Structure Validation**: Integrity checks for structure detection debugging
  - **Statistical Analysis**: Section counts, depth analysis, hierarchy validation
  - **Depth Filtering**: Limit structure display to specific hierarchy levels (1-based)
  - **Headings-Only Mode**: Show only real headings (H1, H2, etc.), filter out paragraph content

**CLI Integration**:
```bash
# Show only document structure
cognitive-reader document.md --structure-only

# Show structure limited to specific depth (first 2 hierarchy levels)
cognitive-reader document.md --structure-only --max-depth 2

# Show structure in JSON format
cognitive-reader document.md --structure-only --output json

# Verbose mode shows structure preview before processing
cognitive-reader document.md --verbose

# Verbose mode with limited depth preview
cognitive-reader document.md --verbose --max-depth 2
```

**Example Output**:
```text
Introduction
  Overview
  Key Concepts
Implementation
  Architecture
    Core Components
```

**Example with `--max-depth 2`**:
```text
Introduction
  Overview
  Key Concepts
Implementation
  Architecture
```

---

## 📦 Project Configuration

### Dependencies (pyproject.toml)

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "cognitive-document-reader"
dynamic = ["version"]  # Automatic versioning from git tags

# Dynamic automatic versioning
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
description = "Advanced document reading with human-like progressive understanding"
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
    "pydantic>=2.0,<3.0",      # Data validation and settings
    "aiohttp>=3.8,<4.0",       # Async HTTP client  
    "click>=8.0,<9.0",         # CLI framework
    "docling>=2.40,<3.0",      # Universal document parsing (current stable: v2.43.0)
    "langdetect>=1.0,<2.0",    # Language detection
    "python-dotenv>=1.0,<2.0", # .env file support
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0,<8.0",
    "pytest-asyncio>=0.21,<1.0",
    "ruff>=0.1,<1.0",          # Only ruff for linting and formatting
    "mypy>=1.0,<2.0",
]
```

### Simple Dynamic Versioning

The project uses **automatic versioning** with git tags (no manual bumping):

```bash
# To create a new version:
git tag v0.1.0         # Creates version 0.1.0  
git tag v0.1.1         # Patch release
git tag v0.2.0         # Minor release

# Version auto-generates from latest git tag
# No need to edit files manually ✨
```

**MVP Benefits:**
- ✅ No manual version editing in multiple files  
- ✅ Automatic consistent versioning
- ✅ Perfect for personal projects
- ✅ Integrates perfectly with uv and PyPI

### UV Management

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy src/

# CLI usage
uv run cognitive-reader document.md

# Build package
uv build
```

### Environment Variables

```bash
# .env - MVP Essential Configuration
COGNITIVE_READER_MODEL=qwen3:8b          # Best performance for cognitive reading
COGNITIVE_READER_TEMPERATURE=0.1             # Low for consistent summaries
COGNITIVE_READER_LANGUAGE=auto

# Document processing (essential settings)
COGNITIVE_READER_CHUNK_SIZE=1000            # Optimal balance context/efficiency
COGNITIVE_READER_CHUNK_OVERLAP=200          # ~20% overlap maintains continuity
COGNITIVE_READER_CONTEXT_WINDOW=4096        # Standard limit that works well

# Performance settings (simplified)
COGNITIVE_READER_TIMEOUT_SECONDS=120        # Reasonable timeout
COGNITIVE_READER_MAX_RETRIES=3              # Standard retry count

# Development modes (AI agent friendly)
COGNITIVE_READER_DRY_RUN=false              # Enable dry-run mode (no LLM calls)
COGNITIVE_READER_MOCK_RESPONSES=false       # Use simulated responses for testing
```

---

## 🧪 Testing Plan

### Testing Standards (MVP)
- **Framework**: Pytest with simple functions
- **Target Coverage**: 80% code coverage (realistic for MVP)
- **Test Types**: Unit and basic integration tests
- **Test Isolation**: Simple fixtures for essential setup

### Test Organization (MVP)

```python
# tests/conftest.py - Simplified for MVP
import pytest
from cognitive_reader.models import ReadingConfig

@pytest.fixture
def test_config():
    """Simple test configuration with mocks enabled."""
    return ReadingConfig(
        model_name="test-model",
        dry_run=True,
        mock_responses=True
    )

@pytest.fixture  
def sample_markdown():
    """Simple markdown for testing."""
    return """
# Test Document

## Section 1
Content of section 1.

## Section 2  
Content of section 2.
    """
```

### Test Categories

#### Unit Tests (MVP)
```python
# tests/test_reading.py - Simple MVP tests
import pytest
from cognitive_reader import CognitiveReader

def test_config_creation(test_config):
    """Test configuration creation."""
    assert test_config.model_name == "test-model"
    assert test_config.dry_run is True

async def test_basic_reading(test_config, sample_markdown):
    """Test basic document reading in dry-run mode."""
    reader = CognitiveReader(test_config)
    knowledge = await reader.read_document_text(sample_markdown)
    
    assert knowledge.document_title == "Test Document"
    assert len(knowledge.sections) >= 2
    assert knowledge.detected_language in ["en", "auto"]

def test_environment_config():
    """Test configuration from environment variables."""
    config = ReadingConfig.from_env()
    assert config.model_name == "qwen3:8b"  # default
```

#### Integration Tests (MVP)
```python
# tests/test_integration.py - Essential integration tests
import pytest
import os

async def test_markdown_processing(test_config, tmp_path):
    """Test complete markdown file processing."""
    # Create temporary markdown file
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\n## Section\nContent here.")
    
    reader = CognitiveReader(test_config)
    knowledge = await reader.read_document(str(md_file))
    
    assert knowledge.document_title == "Test"
    assert len(knowledge.sections) >= 1

def test_env_config_loading(monkeypatch):
    """Test environment variable configuration."""
    monkeypatch.setenv("COGNITIVE_READER_MODEL", "custom-model")
    monkeypatch.setenv("COGNITIVE_READER_TEMPERATURE", "0.5")
    
    config = ReadingConfig.from_env()
    assert config.model_name == "custom-model"
    assert config.temperature == 0.5
```

#### Performance Tests (Basic)
```python
# tests/test_performance.py - Basic performance validation
import pytest
import time

@pytest.mark.performance
async def test_reasonable_processing_time(test_config, sample_markdown):
    """Test that processing completes in reasonable time."""
    reader = CognitiveReader(test_config)
    
    start_time = time.time()
    await reader.read_document_text(sample_markdown)
    processing_time = time.time() - start_time
    
    # In dry-run mode, should be very fast
    assert processing_time < 5.0  # seconds
```

---

## 📋 Development Roadmap

### Milestones

#### Milestone 1: MVP Foundation
- [ ] Basic project structure with uv
- [ ] Pydantic models for configuration and data
- [ ] Universal parser with docling
- [ ] Simple progressive reader
- [ ] Basic CLI interface
- [ ] Essential tests with mocks

#### Milestone 2: Core Functionality
- [ ] Hierarchical structure detection
- [ ] Sequential progressive reading
- [ ] Hierarchical synthesis
- [ ] Multi-language support (EN/ES)
- [ ] Complete environment configuration
- [ ] Agent-friendly development modes

#### Milestone 3: Phase 2 Features
- [ ] Second pass refinement
- [ ] Concept extraction and glossaries
- [ ] Complete PDF/DOCX support via docling
- [ ] Professional CI/CD pipeline
- [ ] Performance optimizations

#### Milestone 4: Phase 3 Features
- [ ] Structural and conceptual maps
- [ ] Smart navigation
- [ ] Advanced export formats
- [ ] Integration APIs

---

## 🛠️ Development & Testing Features

### Overview

The Cognitive Document Reader includes specialized features for development, testing, and debugging workflows. These features enable rapid prototyping, quality evaluation, and controlled testing with large documents.

### Partial Results Saving

**Purpose**: Save intermediate processing results for debugging and evaluation without waiting for complete document processing.

**Implementation**:
- Section-by-section JSON files with zero-padded numbering
- Comprehensive metadata including progress, context, and configuration
- Graceful error handling - failures don't crash main process
- Configurable output directory

**Configuration**:
```bash
COGNITIVE_READER_SAVE_PARTIALS=true
COGNITIVE_READER_PARTIALS_DIR=./debug_output
```

**CLI Usage**:
```bash
cognitive-reader document.md --save-partials --partials-dir ./analysis
```

**Partial Result Structure**:
```json
{
  "progress": {
    "section_index": 3,
    "total_sections": 15,
    "progress_percentage": 20.0
  },
  "section": {
    "id": "section_003",
    "title": "Implementation Details",
    "level": 2,
    "content_preview": "First 300 characters..."
  },
  "summary": {
    "summary": "Generated section summary",
    "key_concepts": ["concept1", "concept2"],
    "confidence_score": 0.95
  },
  "context": {
    "accumulated_context_length": 1250,
    "accumulated_context_preview": "Previous context..."
  },
  "config": {
    "model_used": "qwen3:8b",
    "fast_mode": false,
    "temperature": 0.1
  }
}
```

### Section Filtering

**Purpose**: Control processing scope for testing with large documents and avoiding deep hierarchical analysis.

#### Maximum Sections Limit

Process only the first N sections for rapid testing:

**Configuration**:
```bash
COGNITIVE_READER_MAX_SECTIONS=10
```

**CLI Usage**:
```bash
cognitive-reader large_document.md --max-sections 5
```

#### Maximum Depth Limit

Limit analysis to specific hierarchy levels to avoid excessive depth:

**Configuration**:
```bash
COGNITIVE_READER_MAX_DEPTH=2  # Only levels 0, 1, 2
```

**CLI Usage**:
```bash
cognitive-reader complex_doc.md --max-depth 2
```

### Development Workflow Integration

**Combined Usage Examples**:
```bash
# Quick testing: fast mode + limited sections + save progress
cognitive-reader research_paper.pdf --fast-mode --max-sections 10 --save-partials

# Deep analysis preview: limit depth but save partials for evaluation
cognitive-reader technical_manual.md --max-depth 2 --save-partials --partials-dir ./analysis

# Configuration testing: dry run with all development features
cognitive-reader document.md --dry-run --save-partials --max-sections 5
```

**Python API Usage**:
```python
from cognitive_reader.models import ReadingConfig

# Development configuration
dev_config = ReadingConfig(
    save_partial_results=True,
    partial_results_dir="./debug",
    max_sections=10,
    max_section_depth=2,
    fast_mode=True  # Use fast model for quick iteration
)

reader = CognitiveReader(dev_config)
knowledge = await reader.read_document("large_document.pdf")
```

### Use Cases

**Rapid Prototyping**:
- Test with first few sections of large documents
- Quick feedback on prompt effectiveness
- Fast iteration cycles during development

**Quality Evaluation**:
- Evaluate summary quality without full processing
- Compare different model configurations
- Analyze context accumulation patterns

**Debugging**:
- Identify specific sections causing processing issues
- Trace context evolution through document
- Monitor memory and performance patterns

**Performance Testing**:
- Controlled scope testing with large documents
- Benchmark processing speed at different depths
- Memory usage analysis with limited sections

---

## 📈 Success Metrics

### Technical Metrics (MVP)
- **Test Coverage**: >80%
- **Performance**: <30s for 50-page documents
- **Memory Usage**: <50MB processing memory (no caching)
- **API Response Time**: <200ms for basic operations
- **LLM Efficiency**: Reasonable call minimization
- **Reliability**: Basic error handling and retry logic

### Adoption Metrics
- **PyPI Downloads**: >1000/month in 6 months
- **GitHub Stars**: >100 in 1 year
- **Issues/PRs**: Consistent community activity

### Quality Metrics
- **Documentation**: Complete API docs + examples
- **User Experience**: Clear error messages and helpful warnings
- **Reliability**: <1% failure rate in document processing

---

## 🤖 AI Tools Disclaimer

This project was developed with the assistance of artificial intelligence tools:

**Tools used:**
- **Cursor**: Code editor with AI capabilities
- **Claude-4-Sonnet**: Anthropic's language model

**Division of responsibilities:**

**AI (Cursor + Claude-4-Sonnet)**:
- 🔧 Initial code prototyping
- 📝 Generation of examples and test cases
- 🐛 Assistance in debugging and error resolution
- 📚 Documentation and comments writing
- 💡 Technical implementation suggestions

**Human (Juanje Ojeda)**:
- 🎯 Specification of objectives and requirements
- 🔍 Critical review of code and documentation
- 💬 Iterative feedback and solution refinement
- 📋 Definition of project's educational structure
- ✅ Final validation of concepts and approaches

**Collaboration philosophy**: AI tools served as a highly capable technical assistant, while all design decisions, educational objectives, and project directions were defined and validated by the human.

---

## 📜 License

MIT License - See LICENSE file for details

---

*This specification provides a complete roadmap for implementing a professional-grade cognitive document reader with human-like understanding capabilities.*
