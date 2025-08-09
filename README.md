# Cognitive Document Reader

> Human-like document understanding through progressive reading and hierarchical synthesis

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🧠 Overview

**Cognitive Document Reader** is a Python library that simulates human-like document reading through progressive understanding and hierarchical synthesis. It addresses two primary use cases:

### 🎯 Primary Uses

1. **High-Quality Summaries for Human Reading/Study**
   - Structured summaries that preserve narrative flow
   - Conceptual maps for better understanding
   - Progressive learning paths through complex documents

2. **Enriched Metadata for AI Projects**
   - Enhanced training data for LLM fine-tuning
   - Context-rich information for RAG systems
   - Structured document knowledge for AI workflows

## ✨ Key Features

- **🔄 Progressive Reading**: Processes documents in order, accumulating context like human reading
- **🏗️ Hierarchical Synthesis**: Builds understanding from sections to complete document
- **🌐 Multi-language Support**: English and Spanish with auto-detection
- **⚡ Development Friendly**: Dry-run and mock modes for testing without LLM costs
- **🛠️ Dual Interface**: Use as Python library or standalone CLI tool
- **📊 Multiple Outputs**: JSON for integration, Markdown for human reading

## 🚀 Quick Start

### Installation

```bash
pip install cognitive-document-reader
```

### Basic Usage

#### Command Line

```bash
# Basic document processing
cognitive-reader examples/sample_document.md

# JSON output for integration
cognitive-reader examples/sample_document.md --output json

# Development mode (no LLM calls)
cognitive-reader examples/sample_document.md --dry-run

# Validate configuration only
cognitive-reader --validate-config
```

#### Python Library

```python
from cognitive_reader import CognitiveReader
from cognitive_reader.models import ReadingConfig

# Basic usage with auto-configuration
config = ReadingConfig.from_env()
reader = CognitiveReader(config)

# Process a document
knowledge = await reader.read_document("examples/sample_document.md")

print(f"Title: {knowledge.document_title}")
print(f"Summary: {knowledge.document_summary}")

# Access section summaries
for section_id, summary in knowledge.section_summaries.items():
    print(f"Section: {summary.title}")
    print(f"Summary: {summary.summary}")
    print(f"Concepts: {summary.key_concepts}")
```

### Development Mode

Perfect for AI agents and testing:

```python
# No LLM calls, uses mock responses
config = ReadingConfig(
    dry_run=True,
    mock_responses=True
)

reader = CognitiveReader(config)
knowledge = await reader.read_document_text(text, title)
```

## 📋 Configuration

Configure via environment variables or Python:

### Environment Variables

```bash
# LLM Configuration
COGNITIVE_READER_MODEL=llama3.1:8b
COGNITIVE_READER_TEMPERATURE=0.1
COGNITIVE_READER_LANGUAGE=auto

# Document Processing
COGNITIVE_READER_CHUNK_SIZE=1000
COGNITIVE_READER_CHUNK_OVERLAP=200
COGNITIVE_READER_CONTEXT_WINDOW=4096

# Performance
COGNITIVE_READER_TIMEOUT_SECONDS=120
COGNITIVE_READER_MAX_RETRIES=3

# Development Modes
COGNITIVE_READER_DRY_RUN=false
COGNITIVE_READER_MOCK_RESPONSES=false
```

### Python Configuration

```python
from cognitive_reader.models import ReadingConfig
from cognitive_reader.models.knowledge import LanguageCode

config = ReadingConfig(
    model_name="llama3.1:8b",
    temperature=0.1,
    chunk_size=1000,
    document_language=LanguageCode.AUTO,
    dry_run=False  # Set to True for development
)
```

## 🏗️ Architecture

### Core Components

- **Progressive Reader**: Main engine for sequential document processing
- **Structure Detector**: Extracts hierarchical document structure
- **Synthesizer**: Performs bottom-up knowledge synthesis
- **LLM Client**: Abstraction for language model interactions
- **Prompt Manager**: Manages multi-language prompts with versioning

### Document Flow

1. **Parse**: Extract structure and content from document
2. **Detect**: Identify language and hierarchical relationships
3. **Read**: Process sections progressively, accumulating context
4. **Synthesize**: Build complete understanding from parts to whole

## 📚 Examples

See the `examples/` directory for comprehensive usage examples:

- `basic_usage.py`: Core functionality demonstration with simple document processing
- `advanced_parsing.py`: Multi-format parsing with docling integration and capability detection
- `sample_document.md`: Example Markdown document for testing and demonstrations

### 🔧 Parser Capabilities Detection

```python
from cognitive_reader.parsers.docling_parser import DoclingParser

# Check parser capabilities
parser = DoclingParser()
print(f"Enhanced parsing: {parser.is_docling_available()}")
print(f"Supported formats: {parser.get_supported_formats()}")

# Get detailed info
info = parser.get_parser_info()
print(f"Parser info: {info}")
```

### 📄 Multi-Format Processing

```bash
# Works with any supported format
cognitive-reader your_document.pdf --dry-run    # PDF (requires docling)
cognitive-reader your_document.docx --dry-run   # DOCX (requires docling) 
cognitive-reader your_document.html --dry-run   # HTML (requires docling)
cognitive-reader examples/sample_document.md --dry-run     # Markdown (always works)

# Automatic format detection and processing
cognitive-reader your_document.pdf --output json   # Enhanced parsing with docling
cognitive-reader examples/sample_document.md --output json    # Fallback parsing (built-in)
```

## 🧪 Testing

The library includes comprehensive testing with mocks:

```bash
# Install with development dependencies
pip install cognitive-document-reader[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=cognitive_reader --cov-report=html

# Type checking
mypy src/

# Linting and formatting
ruff check .
ruff format .
```

## 🛠️ Development

### Prerequisites

- Python 3.12+
- `uv` for dependency management

### Setup

```bash
# Clone repository
git clone https://github.com/juanje/cognitive-document-reader.git
cd cognitive-document-reader

# Install dependencies
uv sync

# Install in development mode
uv pip install -e .
```

### Running Examples

```bash
# Basic example with mock responses
uv run python examples/basic_usage.py

# CLI examples  
uv run cognitive-reader examples/sample_document.md --dry-run
```

## 📖 Supported Formats

### Enhanced Mode (with docling)
- **PDF** (.pdf) - Full document parsing with layout preservation
- **DOCX** (.docx) - Microsoft Word document processing
- **HTML** (.html) - Web page content extraction
- **Markdown** (.md, .markdown) - Native and enhanced processing

### Fallback Mode (MVP)
- **Markdown** (.md, .markdown) - Built-in parser

### 🔧 Installation for Enhanced Support

```bash
# For full multi-format support, install docling
pip install 'docling>=2.40'

# The system automatically detects and enables enhanced capabilities
# No configuration required - it just works!
```

### 🎯 Intelligent Parser Strategy

The parser uses an intelligent fallback approach:
- **Primary**: Uses docling for PDF, DOCX, HTML when available
- **Fallback**: Built-in Markdown parser (always works)
- **Output**: Consistent Markdown structure for all formats
- **Detection**: Automatic library detection and graceful degradation

## 🌐 Language Support

- **English** (en)
- **Spanish** (es)
- **Auto-detection** (auto)

## ⚙️ LLM Integration

### Supported Models

- **Ollama**: Primary integration (llama3.1:8b recommended)
- **Future**: OpenAI, Anthropic, and other providers

### Optimization Features

- Smart batching to minimize API calls
- Context window management
- Retry logic with exponential backoff
- Development modes for cost-free testing

## 📊 Output Formats

### JSON (for integration)
```json
{
  "document_title": "Sample Document",
  "document_summary": "...",
  "detected_language": "en",
  "sections": [...],
  "section_summaries": {...},
  "processing_metadata": {...}
}
```

### Markdown (for humans)
```markdown
# Document Title

## Document Summary
...

## Section Analysis
### Section Title
**Summary**: ...
**Key Concepts**: concept1, concept2, concept3
```

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

## 🔮 Roadmap

### Phase 1: MVP (Current)
- ✅ Basic progressive reading
- ✅ Hierarchical synthesis
- ✅ Markdown support
- ✅ CLI and library interfaces
- ✅ Development modes

### Phase 2: Enhanced Features
- 🔄 Second-pass refinement
- 📚 Concept extraction and glossaries
- 📄 PDF/DOCX support
- 🔍 Advanced export formats

### Phase 3: Advanced Navigation
- 🗺️ Structural maps
- 🧭 Smart navigation
- 🔍 Semantic search
- 📈 Learning paths

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Juanje Ojeda** - [juanje@redhat.com](mailto:juanje@redhat.com)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📚 Documentation

For detailed documentation, examples, and API reference, visit the [project documentation](https://github.com/juanje/cognitive-document-reader).

---

*Built with ❤️ for better document understanding*
