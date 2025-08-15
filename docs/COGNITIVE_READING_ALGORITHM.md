# Cognitive Reading Algorithm

## General Description

The Cognitive Document Reader implements a reading process that simulates human cognitive patterns through sequential processing with cumulative context. The system can operate in single-pass or multi-pass mode, always maintaining the principle of source text authority.

## Document Structure Example

Using `examples/sample_document.md` as reference:

```
📄 Cognitive Document Reader Example (Parent with content)
├── 📖 Introduction (Parent with content)
│   └── 🔹 Purpose (Leaf)
├── 📁 Key Features (Parent without content)
│   ├── 🔹 1. Document Processing (Leaf)
│   ├── 🔹 2. Language Detection (Leaf)
│   └── 🔹 3. Structured Output (Leaf)
├── 📖 Technical Architecture (Parent with content)
│   ├── 🔹 Core Components (Leaf)
│   └── 🔹 Processing Flow (Leaf)
└── 🔹 Conclusion (Leaf)
```

**Identified Patterns:**
- **📖 Parent with content**: Has its own introductory text + child sections
- **📁 Parent without content**: Only organizes child sections, requires deferred synthesis
- **🔹 Leaf sections**: No children, contain specific content

---

## Sequential Algorithm with Cumulative Context

### Fundamental Principles

The algorithm processes sections in **document order** (sequential top-down), maintaining cumulative context and applying the **principle of source text authority**.

```
FOR each document:
    1. DETECT hierarchical structure
    2. ORDER sections by document sequence
    3. PROCESS each section with cumulative context
    4. UPDATE incrementally upper levels
    5. SYNTHESIZE parents without content at the end
```

### Detailed Algorithm

```
FOR each section in document order:
    
    1. BUILD cumulative context:
       - Summaries of all parents
       - Summaries of previously processed siblings
    
    IF is parent WITH content:
        2. PROCESS own text with context → generate summary
        3. UPDATE incrementally upper levels
        
    IF is leaf section:
        2. PROCESS content with cumulative context → generate summary
        3. UPDATE incrementally immediate parent
        4. PROPAGATE updates toward upper levels
        
    IF is parent WITHOUT content:
        2. DEFER processing until completing all children
        3. SYNTHESIZE from children summaries + parent context
```

### Practical Example: Processing `sample_document.md`

**1. Process "Cognitive Document Reader Example" (Level 1, Parent WITH content)**
- No previous context (it's the root)
- Process its introductory text → `root_summary_v1`

**2. Process "Introduction" (Level 2, Parent WITH content)**
- Context: `root_summary_v1`
- Process its text → `intro_summary_v1`
- Update root: `root_summary_v1 + intro_summary_v1` → `root_summary_v2`

**3. Process "Purpose" (Level 3, Leaf)**
- Context: `root_summary_v2 + intro_summary_v1`
- Process content → `purpose_summary`
- Update "Introduction": `intro_summary_v1 + purpose_summary` → `intro_summary_final`
- Update root: `root_summary_v2 + intro_summary_final` → `root_summary_v3`

**4. Process "Key Features" (Level 2, Parent WITHOUT content)**
- Defer until processing all its children

**5. Process "1. Document Processing" (Level 3, Leaf)**
- Context: `root_summary_v3` (Key Features doesn't have summary yet)
- Process content → `doc_proc_summary`

**6. Process "2. Language Detection" (Level 3, Leaf)**
- Context: `root_summary_v3 + doc_proc_summary`
- Process content → `lang_det_summary`

**7. Process "3. Structured Output" (Level 3, Leaf)**
- Context: `root_summary_v3 + doc_proc_summary + lang_det_summary`
- Process content → `struct_out_summary`

**8. Synthesize "Key Features" (Deferred Synthesis)**
- Parent context: `root_summary_v3`
- Synthesize from children: `doc_proc_summary + lang_det_summary + struct_out_summary` → `key_features_summary`
- Update root: `root_summary_v3 + key_features_summary` → `root_summary_v4`

**9-11. Process "Technical Architecture" and its children**
- Follows the same pattern as "Introduction"

**12. Process "Conclusion" (Level 2, Leaf)**
- Context: `root_summary_v5` (most updated version)
- Final update: `root_summary_v5 + conclusion_summary` → `final_root_summary`

---

## Multi-Pass Processing

### Multi-Pass Architecture

The system can execute multiple passes of the same sequential algorithm, progressively enriching the context:

**Pass 1:** Sequential algorithm with basic context (parents + previous siblings)
**Pass 2+:** Same sequential algorithm with enriched context

### Enriched Context in Subsequent Passes

```
FOR each section in subsequent passes:
    
    1. BUILD enriched context:
       - Current parent summaries (current pass)
       - Previous summary of same node (previous pass)
       - Key concept glossary with definitions
    
    2. APPLY authority principle:
       - SOURCE TEXT = supreme authority
       - ENRICHED CONTEXT = supporting information
    
    3. PROCESS with identical sequential algorithm
```

### Example: "Purpose" in Second Pass

**Enriched Context:**
- **Current parents**: `root_summary_v2 + intro_summary_v1` (second pass)
- **Previous summary**: `purpose_summary_first_pass`
- **Concepts**: `"progressive reading": "Hierarchical processing technique...", "hierarchical synthesis": "..."`

**Processing:**
```
CONTEXT (supporting information):
- Root Summary: [current understanding of document]
- Introduction Summary: [current understanding of parent section]
- Previous Summary: [understanding from first pass]
- Concepts: [glossary with definitions]

SOURCE TEXT (supreme authority):
[original content of "Purpose" section]

The algorithm generates a refined summary that integrates:
- Complete fidelity to source text
- Contextual enrichment from previous passes
- Conceptual frameworks from glossary
```

---

## Source Text Authority Principle

### Authority Hierarchy

```
1. 🥇 ORIGINAL SOURCE TEXT      → Supreme authority, always prevails
2. 🥈 CUMULATIVE CONTEXT       → Summaries of parents and previous siblings
3. 🥉 PREVIOUS KNOWLEDGE       → Summaries from previous passes
4. 📚 CONCEPTUAL GLOSSARY      → Supporting definitions
```

### Principle Application

- **Text vs context conflict**: Source text always wins
- **Context purpose**: Enrich understanding, not contradict
- **Guaranteed fidelity**: Summaries faithfully reflect original content
- **Automatic correction**: Subsequent passes correct previous misunderstandings based on text

---

## Algorithm Characteristics

### Sequential Processing Advantages

- **Progressive Context**: Each section benefits from all accumulated understanding
- **Natural Order**: Follows logical document sequence like a human reader
- **Coherent Updates**: Upper levels evolve incrementally
- **Semantic Integration**: Previous siblings enrich context for following ones

### Complexity Management

- **Deferred Synthesis**: Parents without content wait until all children are processed
- **Truncated Context**: Context length is managed to stay within limits
- **Dynamic Glossary**: Key concepts are generated to enrich subsequent passes
- **Textual Authority**: Authority principle prevents semantic drift

---

## Summary

The Cognitive Reading Algorithm simulates human document comprehension through:

1. **Sequential Processing**: Follows natural document order
2. **Cumulative Context**: Each section receives context from parents and previous siblings
3. **Incremental Updates**: Upper levels evolve as children are processed
4. **Authority Principle**: Source text prevails over any context
5. **Adaptive Synthesis**: Specific strategies for parents with/without content
6. **Multi-Pass Refinement**: Progressive enrichment maintaining textual fidelity

This approach produces summaries that maintain the semantic richness of the original document, preserve the author's hierarchical structure, and provide appropriate context for both human reading and AI system processing.
