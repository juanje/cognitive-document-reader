# Cognitive Document Reader

> Human-like document understanding through multi-pass cognitive processing

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🧠 Overview

**Cognitive Document Reader** is a Python library that simulates authentic human-like document reading through **multi-pass cognitive processing**. Unlike traditional document processors that fragment content, it reads documents sequentially with progressively richer context across multiple passes, just like humans do. It addresses two primary use cases:

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

- **🧠 Multi-Pass Cognitive Reading**: Multiple reading passes with progressively richer context for deep understanding
- **📖 Sequential Processing**: Reads documents in natural order with cumulative context
- **🎯 Text Authority**: Original text always takes precedence over contextual information
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
cognitive-reader examples/sample_document.md --format json

# Save JSON output to file
cognitive-reader examples/sample_document.md --format json --output-file analysis.json

# Development mode (no LLM calls)
cognitive-reader examples/sample_document.md --dry-run

# Validate configuration only
cognitive-reader --validate-config

# Multi-pass processing (default: 2 passes)
cognitive-reader examples/sample_document.md

# Single-pass mode (fast testing)
cognitive-reader examples/sample_document.md --single-pass

# Save intermediate results between passes (debugging)
cognitive-reader examples/sample_document.md --save-intermediate

# Show processing statistics (performance monitoring)
cognitive-reader examples/sample_document.md --stats

# Spanish document processing
cognitive-reader examples/sample_document_es.md --language es
```

#### Key CLI Options

**Output Control:**
- `-f, --format [json|markdown]`: Output format (default: markdown)
- `-o, --output-file PATH`: Save output to file instead of stdout
- `--log PATH`: Redirect logs to file (separate from results)

**Processing Modes:**
- `--dry-run`: No actual LLM calls (for testing)
- `--fast-mode`: Single pass with fast model (speed over quality)
- `--stats`: Show processing statistics after completion

**Document Control:**
- `-l, --language [auto|en|es]`: Document language (default: auto-detect)
- `--max-sections N`: Limit number of sections processed
- `--max-depth N`: Limit section depth processed

#### Python Library

```python
from pathlib import Path
from cognitive_reader import CognitiveReader
from cognitive_reader.models import CognitiveConfig
from cognitive_reader.utils.logging_config import configure_logging

# Configure logging to file (optional)
configure_logging(verbose=True, log_file=Path("processing.log"))

# Basic usage with auto-configuration
config = CognitiveConfig.from_env()  # Can set COGNITIVE_READER_LOG_FILE env var
reader = CognitiveReader(config)

# Process a document
knowledge = await reader.read_document("examples/sample_document.md")

print(f"Title: {knowledge.document_title}")
print(f"Summary: {knowledge.document_summary}")

# Access section summaries
for section_id, summary in knowledge.hierarchical_summaries.items():
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

Configure via environment variables or Python. All settings have sensible defaults and are optional.

### Environment Variables

**📄 Complete Reference**: See `env.example` for all available variables with documentation.

```bash
# Copy the example configuration
cp env.example .env

# Edit with your preferred values
nano .env
```

**🔧 Key Settings:**

```bash
# Multi-Pass Cognitive Reading (default: 2 passes)
COGNITIVE_READER_FAST_PASS_MODEL=llama3.1:8b    # Fast first pass
COGNITIVE_READER_MAIN_MODEL=qwen3:8b            # Quality subsequent passes
COGNITIVE_READER_NUM_PASSES=2                   # Number of cognitive passes (1=single, 2=dual, 3+=multi)

# Processing control
COGNITIVE_READER_SINGLE_PASS=false             # Force single-pass mode (fast testing)
COGNITIVE_READER_SAVE_INTERMEDIATE=false       # Save intermediate results between passes
COGNITIVE_READER_INTERMEDIATE_DIR=./intermediate_passes  # Directory for intermediate files

# Development modes
COGNITIVE_READER_DRY_RUN=false                  # Use mock responses for testing
COGNITIVE_READER_LANGUAGE=auto                  # auto, en, es
COGNITIVE_READER_LOG_FILE=./logs/processing.log # Redirect logs to file (optional)
```

### Python Configuration

```python
from cognitive_reader.models import CognitiveConfig

# Multi-pass cognitive reading (default: 2 passes)
config = CognitiveConfig(
    num_passes=2,                       # Number of cognitive passes
    fast_pass_model="llama3.1:8b",      # Fast first pass
    main_model="qwen3:8b",              # Quality subsequent passes
    document_language="auto"            # auto, en, es
)

# Processing control
control_config = CognitiveConfig(
    single_pass=True,                   # Force single-pass mode (fast testing)
    save_intermediate=True,             # Save intermediate results for debugging
    intermediate_dir="./debug_passes"  # Custom directory for intermediate files
)

# Development & testing
dev_config = CognitiveConfig(
    dry_run=True,                       # No real LLM calls
    mock_responses=True                 # Use mock data for testing
)
```

## 🏗️ Architecture

### Document Flow

1. **Parse**: Extract structure and content from document
2. **Multi-Pass Reading**: Progressive understanding through multiple sequential passes
   - **Pass 1**: Initial reading with cumulative context
   - **Pass 2+**: Re-reading with progressively enriched understanding
3. **Synthesize**: Generate final knowledge optimized for RAG/Fine-tuning

The system follows natural human reading patterns: understanding builds progressively through sequential processing, with each pass benefiting from richer context than the previous one.

## 📚 Examples

See the `examples/` directory for comprehensive usage examples:

- `basic_usage.py`: Core functionality demonstration with simple document processing
- `advanced_parsing.py`: Multi-format parsing with docling integration and capability detection
- `sample_document.md`: **Fictional test document** designed specifically to evaluate cognitive reading capabilities
- `sample_document_es.md`: Spanish version of the test document for multilingual evaluation

**About the Sample Documents:**
The sample documents present "Aethelgard's Crystalline Consciousness Theory" - a **completely fictional scientific theory** created specifically to test the cognitive reader's capabilities:

- 📊 **Structural Testing**: Contains both parent sections with content and parent sections without content to test hierarchical processing
- 🧪 **Novel Semantic Content**: Introduces concepts and terminology not present in LLM training data to evaluate how the system processes genuinely new information  
- 🔄 **Concept Redefinition**: Deliberately redefines existing concepts (like "empathy") to test whether the system prioritizes the document's semantic meaning over pre-trained knowledge
- 🌐 **Multilingual Evaluation**: Available in English and Spanish with identical structure and semantic content
- 🧹 **Title Cleaning**: Includes various formatting patterns to test automatic title normalization

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
cognitive-reader your_document.pdf --dry-run               # PDF processing
cognitive-reader your_document.docx --dry-run              # DOCX processing 
cognitive-reader your_document.html --dry-run              # HTML processing
cognitive-reader examples/sample_document.md --dry-run     # Markdown processing

# Automatic format detection and processing
cognitive-reader your_document.pdf --format json              # JSON output for any format
cognitive-reader examples/sample_document.md --format json    # Consistent processing
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

The system processes multiple document formats using the **docling** library for universal document parsing:

- **PDF** (.pdf) - Preserves layout and structure
- **DOCX** (.docx) - Microsoft Word documents  
- **HTML** (.html) - Web pages and HTML content
- **Markdown** (.md, .markdown) - Native support with optimized processing

All formats are converted to a unified Markdown structure internally for consistent cognitive processing.

### 🎯 Processing Strategy

- **Multi-format input**: Docling handles PDF, DOCX, HTML conversion
- **Unified processing**: All content processed as structured Markdown
- **Consistent output**: Same high-quality results regardless of input format

## 🌐 Language Support

- **English** (en)
- **Spanish** (es)
- **Auto-detection** (auto)

## ⚙️ LLM Integration

The system uses **LangChain** for LLM interactions and supports a **multi-model approach** that mirrors human reading patterns:

- **First Pass:** `llama3.1:8b` for quick initial understanding
- **Subsequent Passes:** `qwen3:8b` for deep analysis and progressive refinement

### **Local Models via Ollama**

The system is designed for **local LLM usage** through **Ollama**, ensuring privacy and control:

```bash
# Install recommended models
ollama pull llama3.1:8b    # Fast model for first pass
ollama pull qwen3:8b       # Quality model for subsequent passes
```

### **Usage Examples**

```bash
# Default: multi-pass cognitive processing
cognitive-reader document.md

# Fast mode: single pass with fast model
cognitive-reader document.md --fast-mode

# Disable reasoning mode (for performance/comparison)
cognitive-reader document.md --disable-reasoning

# Development: no LLM calls
cognitive-reader document.md --dry-run
```

**Primary Support:** Ollama with local models for privacy and performance

## 🛠️ Development & Testing Features

### Partial Results Saving

Save intermediate results as sections are processed for debugging and evaluation:

```bash
# Save partial results for debugging
cognitive-reader document.md --save-partials

# Custom output directory
cognitive-reader document.md --save-partials --partials-dir ./debug_output
```

**Partial results include:**
- Section-by-section processing progress
- Generated summaries and key concepts
- Accumulated context evolution
- Model configuration and performance metadata

### Section Limiting

Control processing scope for testing with large documents:

```bash
# Process only first 5 sections
cognitive-reader large_document.md --max-sections 5

# Limit analysis to depth level 2 (avoid deep hierarchies)
cognitive-reader complex_doc.md --max-depth 2

# Combined: fast testing with partials
cognitive-reader document.md --fast-mode --max-sections 3 --save-partials
```

### Log File Output

Redirect logs to files instead of terminal output for better debugging and analysis:

```bash
# Basic log file output
cognitive-reader document.md --log processing.log

# Verbose logs to file for debugging
cognitive-reader document.md --log debug.log --verbose

# Quiet processing with logs saved to file
cognitive-reader document.md --log background.log --quiet

# Environment variable configuration
export COGNITIVE_READER_LOG_FILE="./logs/app.log"
cognitive-reader document.md  # Logs automatically saved to file

# Development workflow with comprehensive logging
cognitive-reader document.md --log analysis.log --save-partials --stats --verbose
```

**Use cases:**
- 🔍 **Debugging**: Keep detailed processing logs while maintaining clean terminal output
- 📊 **Analysis**: Separate application logs from results for easier data analysis
- 🤖 **CI/CD**: Capture logs in automated testing and deployment pipelines
- 📚 **Library Usage**: Configure logging when using cognitive-reader as a Python library

**Note**: The `--log` flag redirects *all* application logs to the specified file. Output results (summaries, JSON) still go to stdout unless `--output-file` is also used.

### Development Workflow Examples

```bash
# Quick testing: fast mode + limited sections + save progress
cognitive-reader research_paper.pdf --fast-mode --max-sections 10 --save-partials

# Deep analysis preview: limit depth but save partials for evaluation
cognitive-reader technical_manual.md --max-depth 2 --save-partials --partials-dir ./analysis

# Configuration testing: dry run with all development features
cognitive-reader document.md --dry-run --save-partials --max-sections 5
```

**Perfect for:**
- 🚀 **Rapid prototyping** with large documents
- 🔍 **Quality evaluation** of summaries without full processing
- 🐛 **Debugging** processing issues at specific sections
- ⚡ **Performance testing** with controlled scope

### Processing Statistics

Monitor performance and resource usage with detailed statistics:

```bash
# Basic statistics
cognitive-reader document.md --stats

# Statistics with development modes
cognitive-reader document.md --stats --dry-run
cognitive-reader document.md --stats --fast-mode

# Combined with other features
cognitive-reader large_doc.md --stats --max-sections 10 --save-partials

# JSON output with stats
cognitive-reader document.md --format json --stats --output-file results.json
```

**Statistics include:**
- 📊 **LLM Calls**: Total calls, breakdown by type (summary/concepts)
- 🔢 **Token Usage**: Total tokens sent, averages per call type
- ⏱️ **Timing**: Duration per processing pass, total processing time
- 📄 **Content**: Sections processed, concepts generated
- 🧮 **Efficiency**: Average tokens per section processed

**Example output:**
```
      Processing Statistics
 LLM Calls                5 calls
   Summary Calls          2 calls
   Concept Calls          3 calls

 Total Tokens Sent   5,162 tokens
   Avg Summary         530 tokens
   Avg Concepts       1368 tokens
   Avg per Section    1721 tokens

 Pass 1 Duration         1m 55s
 Pass 2 Duration         1m 45s
 Total Duration          3m 40s

 Sections Processed  3 sections
 Concepts Generated  3 concepts
```

## 📊 Output Formats

> **📝 Note**: The examples below use "Aethelgard's Crystalline Consciousness Theory" - a **completely fictional scientific theory** created specifically to demonstrate the cognitive reader's capabilities with novel semantic content.

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

**Aethelgard's Crystalline Consciousness Theory** explores the revolutionary theory proposed by xenophysicist Elara Aethelgard, which postulates that consciousness is not created by neural complexity but is a fundamental universal property received through biological resonance mechanisms...

## Section Analysis

### The Primordial Resonant Frequency
**Summary**: Detailed explanation of the PRF as the basal subatomic vibration that determines an organism's affinity with consciousness patterns. Measured in states of total somatic deprivation using gravito-quantum field sensors...

**Key Concepts**: primordial_resonant_frequency, gravito_quantum_vibration, harmonic_dissonance

### Empathic Resonance: A Redefinition
**Summary**: Revolutionary redefinition of empathy as a measurable physical phenomenon of harmonic coupling between somatic frameworks, explaining instant connections and antipathy through PRF compatibility...

**Key Concepts**: empathic_resonance, somatic_framework, harmonic_coupling
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


## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Juanje Ojeda** - [juanje@redhat.com](mailto:juanje@redhat.com)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📚 Documentation

For detailed documentation, examples, and API reference, visit the [project documentation](https://github.com/juanje/cognitive-document-reader).