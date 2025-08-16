# Cognitive Reading Algorithm

## General Description

The Cognitive Document Reader implements a reading process that simulates human cognitive patterns through sequential processing with cumulative context. The system can operate in single-pass or multi-pass mode, always maintaining the principle of source text authority.

## Document Structure Example

Using `examples/sample_document.md` as reference:

> **📝 Note**: The sample document presents "Aethelgard's Crystalline Consciousness Theory" - a **completely fictional scientific theory** created specifically to test cognitive reading capabilities. It contains novel semantic content not present in LLM training data and deliberately redefines existing concepts to evaluate how the system processes new information vs. pre-trained knowledge.

```
📄 Aethelgard's Crystalline Consciousness Theory (Parent with content)
├── 📖 Fundamental Principles (Parent with content)
│   ├── 🔹 The Primordial Resonant Frequency (Leaf)
│   └── 🔹 Cognitive Refraction (Leaf)
├── 📁 The Somatic Framework (Parent without content)
│   ├── 🔹 The Structure of the Framework (Leaf)
│   └── 🔹 Empathic Resonance: A Redefinition (Leaf)
└── 📖 Applications and Paradoxes (Parent with content)
    ├── 🔹 The Concept of Self-Crystallization (Leaf)
    └── 🔹 The Dissonant Observer Paradox (Leaf)
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

**2. Process "Fundamental Principles" (Level 2, Parent WITH content)**
- Context: `root_summary_v1`
- Process its text → `principles_summary_v1`
- Update root: `root_summary_v1 + principles_summary_v1` → `root_summary_v2`

**3. Process "The Primordial Resonant Frequency" (Level 3, Leaf)**
- Context: `root_summary_v2 + principles_summary_v1`
- Process content → `prf_summary`
- Update "Fundamental Principles": `principles_summary_v1 + prf_summary` → `principles_summary_v2`
- Update root: `root_summary_v2 + principles_summary_v2` → `root_summary_v3`

**4. Process "Cognitive Refraction" (Level 3, Leaf)**
- Context: `root_summary_v3 + principles_summary_v2`
- Process content → `refraction_summary`
- Update "Fundamental Principles": `principles_summary_v2 + refraction_summary` → `principles_summary_final`
- Update root: `root_summary_v3 + principles_summary_final` → `root_summary_v4`

**5. Process "The Somatic Framework" (Level 2, Parent WITHOUT content)**
- Defer until processing all its children

**6. Process "The Structure of the Framework" (Level 3, Leaf)**
- Context: `root_summary_v4` (The Somatic Framework doesn't have summary yet)
- Process content → `structure_summary`

**7. Process "Empathic Resonance: A Redefinition" (Level 3, Leaf)**
- Context: `root_summary_v4 + structure_summary`
- Process content → `empathic_resonance_summary`

**8. Synthesize "The Somatic Framework" (Deferred Synthesis)**
- Parent context: `root_summary_v4`
- Synthesize from children: `structure_summary + empathic_resonance_summary` → `somatic_framework_summary`
- Update root: `root_summary_v4 + somatic_framework_summary` → `root_summary_v5`

**9. Process "Applications and Paradoxes" (Level 2, Parent WITH content)**
- Context: `root_summary_v5`
- Process its text → `applications_summary_v1`
- Update root: `root_summary_v5 + applications_summary_v1` → `root_summary_v6`

**10. Process "The Concept of Self-Crystallization" (Level 3, Leaf)**
- Context: `root_summary_v6 + applications_summary_v1`
- Process content → `crystallization_summary`
- Update "Applications and Paradoxes": `applications_summary_v1 + crystallization_summary` → `applications_summary_v2`
- Update root: `root_summary_v6 + applications_summary_v2` → `root_summary_v7`

**11. Process "The Dissonant Observer Paradox" (Level 3, Leaf)**
- Context: `root_summary_v7 + applications_summary_v2`
- Process content → `paradox_summary`
- Update "Applications and Paradoxes": `applications_summary_v2 + paradox_summary` → `applications_summary_final`
- Final update: `root_summary_v7 + applications_summary_final` → `final_root_summary`

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
- Root Summary: [current understanding of Aethelgard's theory]
- Fundamental Principles Summary: [current understanding of parent section]
- Previous Summary: [understanding from first pass]
- Concepts: [glossary with definitions including primordial_resonant_frequency, cognitive_refraction, etc.]

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
