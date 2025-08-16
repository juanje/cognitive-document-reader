"""Specific test implementations for Aethelgard theory evaluation."""

from __future__ import annotations

from typing import Any

from .base_test import SemanticTest, TestOutcome, TestResult


class ConceptualIntegrityTest(SemanticTest):
    """Tests that verify conceptual integrity for redefined terms."""

    def __init__(self) -> None:
        super().__init__(
            name="conceptual_integrity",
            description="Verifies that redefined concepts maintain their specific definitions",
        )

    def test_empathy_redefinition(self, knowledge_data: dict[str, Any]) -> TestOutcome:
        """Test if empathy is correctly redefined as empathic resonance."""
        all_text = self._extract_summaries_text(knowledge_data)
        concepts = self._extract_concept_definitions(knowledge_data)

        # Look for key terms in the redefinition
        required_terms = ["empathic resonance", "resonancia empática"]  # EN/ES
        physical_terms = [
            "physical",
            "físico",
            "harmonic coupling",
            "acoplamiento armónico",
        ]

        # Check if empathy is mentioned as physical/resonant rather than psychological
        found_resonance = any(term in all_text.lower() for term in required_terms)
        found_physical = any(term in all_text.lower() for term in physical_terms)

        # Check concepts definitions
        empathy_concept = None
        for name, definition in concepts.items():
            if "empath" in name or "empatía" in name:
                empathy_concept = definition
                break

        # Scoring logic
        score = 0.0
        evidence_parts = []

        if found_resonance:
            score += 0.5
            evidence_parts.append("Found 'empathic resonance' terminology")

        if found_physical:
            score += 0.3
            evidence_parts.append("Found physical/harmonic descriptions")

        if empathy_concept and (
            "resonance" in empathy_concept or "resonancia" in empathy_concept
        ):
            score += 0.2
            evidence_parts.append(
                f"Concept definition includes resonance: {empathy_concept[:100]}..."
            )

        result = (
            TestResult.PASS
            if score >= 0.7
            else (TestResult.PARTIAL if score >= 0.3 else TestResult.FAIL)
        )

        return TestOutcome(
            test_name="empathy_redefinition",
            result=result,
            score=score,
            details=f"Empathy redefinition test. Score: {score:.2f}",
            expected_answer="Empathy as 'empathic resonance' - a physical phenomenon based on harmonic coupling between somatic frameworks",
            found_evidence="; ".join(evidence_parts)
            if evidence_parts
            else "No evidence found",
            failure_reason=None
            if result == TestResult.PASS
            else "Missing key empathic resonance terminology",
        )

    def test_psychopathology_redefinition(
        self, knowledge_data: dict[str, Any]
    ) -> TestOutcome:
        """Test if psychopathologies are redefined as tuning states."""
        all_text = self._extract_summaries_text(knowledge_data)

        # Look for the redefinition terms
        tuning_terms = [
            "non-standard tuning",
            "sintonización no estándar",
            "tuning states",
        ]
        harmonic_terms = [
            "harmonic dissonance",
            "disonancia armónica",
            "frequency deviation",
        ]

        found_tuning = any(term in all_text.lower() for term in tuning_terms)
        found_harmonic = any(term in all_text.lower() for term in harmonic_terms)

        # Check if traditional psychiatric terms are avoided
        psychiatric_terms = ["mental illness", "disorder", "pathology"]
        found_psychiatric = any(term in all_text.lower() for term in psychiatric_terms)

        score = 0.0
        evidence_parts = []

        if found_tuning:
            score += 0.6
            evidence_parts.append("Found tuning/sintonización terminology")

        if found_harmonic:
            score += 0.3
            evidence_parts.append("Found harmonic dissonance concepts")

        if not found_psychiatric:
            score += 0.1
            evidence_parts.append("Avoided traditional psychiatric terminology")
        else:
            evidence_parts.append("WARNING: Contains traditional psychiatric terms")

        result = (
            TestResult.PASS
            if score >= 0.6
            else (TestResult.PARTIAL if score >= 0.3 else TestResult.FAIL)
        )

        return TestOutcome(
            test_name="psychopathology_redefinition",
            result=result,
            score=score,
            details=f"Psychopathology redefinition test. Score: {score:.2f}",
            expected_answer="Psychopathologies as 'non-standard tuning states' caused by harmonic dissonance",
            found_evidence="; ".join(evidence_parts)
            if evidence_parts
            else "No evidence found",
            failure_reason=None
            if result == TestResult.PASS
            else "Missing tuning state redefinition",
        )

    def evaluate(self, knowledge_data: dict[str, Any]) -> TestOutcome:
        """Run all conceptual integrity tests."""
        empathy_test = self.test_empathy_redefinition(knowledge_data)
        psycho_test = self.test_psychopathology_redefinition(knowledge_data)

        # Combined scoring
        combined_score = (empathy_test.score + psycho_test.score) / 2
        combined_result = (
            TestResult.PASS
            if combined_score >= 0.7
            else (TestResult.PARTIAL if combined_score >= 0.4 else TestResult.FAIL)
        )

        return TestOutcome(
            test_name=self.name,
            result=combined_result,
            score=combined_score,
            details=f"Combined conceptual integrity. Empathy: {empathy_test.score:.2f}, Psychopathology: {psycho_test.score:.2f}",
            expected_answer="Proper redefinition of empathy and psychopathologies according to Aethelgard theory",
            found_evidence=f"Empathy evidence: {empathy_test.found_evidence}; Psychopathology evidence: {psycho_test.found_evidence}",
            failure_reason=None
            if combined_result == TestResult.PASS
            else "One or more concept redefinitions missing",
        )


class MetaphorFidelityTest(SemanticTest):
    """Tests that verify fidelity to central metaphors."""

    def __init__(self) -> None:
        super().__init__(
            name="metaphor_fidelity",
            description="Verifies that key metaphors (prism, tuning fork) are preserved",
        )

    def test_prism_metaphor(self, knowledge_data: dict[str, Any]) -> TestOutcome:
        """Test for prism metaphor in cognitive refraction."""
        all_text = self._extract_summaries_text(knowledge_data)

        # Look for prism metaphor elements
        prism_terms = [
            "prism",
            "prisma",
            "white light",
            "luz blanca",
            "spectrum",
            "espectro",
        ]
        refraction_terms = ["refraction", "refracción", "refracts", "refracta"]

        found_prism = any(term in all_text.lower() for term in prism_terms)
        found_refraction = any(term in all_text.lower() for term in refraction_terms)

        # Look for the complete metaphor
        metaphor_complete = found_prism and found_refraction

        score = 0.0
        evidence_parts = []

        if found_prism:
            score += 0.5
            evidence_parts.append("Found prism/light terminology")

        if found_refraction:
            score += 0.3
            evidence_parts.append("Found refraction process")

        if metaphor_complete:
            score += 0.2
            evidence_parts.append("Complete prism metaphor present")

        result = (
            TestResult.PASS
            if score >= 0.7
            else (TestResult.PARTIAL if score >= 0.3 else TestResult.FAIL)
        )

        return TestOutcome(
            test_name="prism_metaphor",
            result=result,
            score=score,
            details=f"Prism metaphor test. Score: {score:.2f}",
            expected_answer="Somatic framework as prism refracting white light of universal consciousness into spectrum",
            found_evidence="; ".join(evidence_parts)
            if evidence_parts
            else "No metaphor evidence found",
            failure_reason=None
            if result == TestResult.PASS
            else "Missing prism metaphor elements",
        )

    def test_tuning_fork_metaphor(self, knowledge_data: dict[str, Any]) -> TestOutcome:
        """Test for tuning fork metaphor in PRF explanation."""
        all_text = self._extract_summaries_text(knowledge_data)

        # Look for tuning fork metaphor elements
        fork_terms = [
            "tuning fork",
            "diapasón",
            "vibration",
            "vibración",
            "resonance",
            "resonancia",
        ]
        harmony_terms = ["harmony", "armonía", "sympathetic", "simpática", "compatible"]

        found_fork = any(term in all_text.lower() for term in fork_terms)
        found_harmony = any(term in all_text.lower() for term in harmony_terms)

        score = 0.0
        evidence_parts = []

        if found_fork:
            score += 0.6
            evidence_parts.append("Found tuning fork/vibration terminology")

        if found_harmony:
            score += 0.4
            evidence_parts.append("Found harmonic/sympathetic concepts")

        result = (
            TestResult.PASS
            if score >= 0.8
            else (TestResult.PARTIAL if score >= 0.4 else TestResult.FAIL)
        )

        return TestOutcome(
            test_name="tuning_fork_metaphor",
            result=result,
            score=score,
            details=f"Tuning fork metaphor test. Score: {score:.2f}",
            expected_answer="Tuning fork metaphor: PRF causes sympathetic vibration in compatible consciousness fields",
            found_evidence="; ".join(evidence_parts)
            if evidence_parts
            else "No metaphor evidence found",
            failure_reason=None
            if result == TestResult.PASS
            else "Missing tuning fork metaphor",
        )

    def evaluate(self, knowledge_data: dict[str, Any]) -> TestOutcome:
        """Run all metaphor fidelity tests."""
        prism_test = self.test_prism_metaphor(knowledge_data)
        fork_test = self.test_tuning_fork_metaphor(knowledge_data)

        # Combined scoring
        combined_score = (prism_test.score + fork_test.score) / 2
        combined_result = (
            TestResult.PASS
            if combined_score >= 0.7
            else (TestResult.PARTIAL if combined_score >= 0.4 else TestResult.FAIL)
        )

        return TestOutcome(
            test_name=self.name,
            result=combined_result,
            score=combined_score,
            details=f"Combined metaphor fidelity. Prism: {prism_test.score:.2f}, Tuning fork: {fork_test.score:.2f}",
            expected_answer="Both prism and tuning fork metaphors preserved in summaries",
            found_evidence=f"Prism evidence: {prism_test.found_evidence}; Fork evidence: {fork_test.found_evidence}",
            failure_reason=None
            if combined_result == TestResult.PASS
            else "One or more key metaphors missing",
        )


class CausalRelationshipTest(SemanticTest):
    """Tests that verify understanding of causal relationships."""

    def __init__(self) -> None:
        super().__init__(
            name="causal_relationships",
            description="Verifies correct understanding of cause-effect relationships between concepts",
        )

    def test_prf_somatic_causality(self, knowledge_data: dict[str, Any]) -> TestOutcome:
        """Test if PRF → somatic framework causality is understood."""
        all_text = self._extract_summaries_text(knowledge_data)

        # Look for causal language connecting PRF and somatic framework
        causal_terms = [
            "determines",
            "determina",
            "causes",
            "causa",
            "shapes",
            "forma",
            "configures",
            "configura",
        ]
        prf_terms = [
            "primordial resonant frequency",
            "frecuencia resonante primordial",
            "PRF",
            "FRP",
        ]
        somatic_terms = [
            "somatic framework",
            "entramado somático",
            "bio-energetic",
            "bio-energética",
        ]

        found_prf = any(term in all_text.lower() for term in prf_terms)
        found_somatic = any(term in all_text.lower() for term in somatic_terms)
        found_causal = any(term in all_text.lower() for term in causal_terms)

        # Look for explicit causal relationship
        causal_relationship = found_prf and found_somatic and found_causal

        score = 0.0
        evidence_parts = []

        if found_prf:
            score += 0.3
            evidence_parts.append("Found PRF terminology")

        if found_somatic:
            score += 0.3
            evidence_parts.append("Found somatic framework terminology")

        if found_causal:
            score += 0.2
            evidence_parts.append("Found causal language")

        if causal_relationship:
            score += 0.2
            evidence_parts.append(
                "Causal relationship between PRF and somatic framework identified"
            )

        result = (
            TestResult.PASS
            if score >= 0.8
            else (TestResult.PARTIAL if score >= 0.5 else TestResult.FAIL)
        )

        return TestOutcome(
            test_name="prf_somatic_causality",
            result=result,
            score=score,
            details=f"PRF-somatic causality test. Score: {score:.2f}",
            expected_answer="PRF determines/configures the somatic framework during early development",
            found_evidence="; ".join(evidence_parts)
            if evidence_parts
            else "No causal relationship evidence found",
            failure_reason=None
            if result == TestResult.PASS
            else "Missing clear PRF → somatic framework causality",
        )

    def test_hierarchical_synthesis(
        self, knowledge_data: dict[str, Any]
    ) -> TestOutcome:
        """Test if hierarchical synthesis works for parent sections without content."""
        # Look for "entramado somático" / "somatic framework" section
        somatic_section = self._find_section_by_title(
            knowledge_data, ["somatic", "entramado"]
        )

        if not somatic_section:
            return TestOutcome(
                test_name="hierarchical_synthesis",
                result=TestResult.UNABLE_TO_EVALUATE,
                score=0.0,
                details="Could not find somatic framework section",
                expected_answer="Synthesized introduction to somatic framework concept",
                found_evidence="Section not found",
                failure_reason="Missing expected section structure",
            )

        summary_text = somatic_section.get("summary", "")

        # Check if summary provides synthesis rather than just listing subsections
        synthesis_indicators = [
            "network",
            "red",
            "manifests",
            "manifiesta",
            "bio-energetic",
            "bio-energética",
            "consciousness",
            "conciencia",
        ]

        list_indicators = [
            "structure",
            "estructura",
            "empathy",
            "empatía",
            "definition",
            "definición",
        ]

        found_synthesis = any(
            term in summary_text.lower() for term in synthesis_indicators
        )
        found_listing = any(term in summary_text.lower() for term in list_indicators)

        score = 0.0
        evidence_parts = []

        if found_synthesis:
            score += 0.7
            evidence_parts.append("Found synthesized conceptual introduction")

        if found_listing and not found_synthesis:
            score = 0.2  # Penalty for just listing subsections
            evidence_parts.append(
                "WARNING: Contains subsection listing instead of synthesis"
            )
        elif found_listing:
            score += 0.1
            evidence_parts.append("Contains some structural references")

        if len(summary_text) > 100:  # Reasonable synthesis length
            score += 0.2
            evidence_parts.append("Adequate summary length for synthesis")

        result = (
            TestResult.PASS
            if score >= 0.7
            else (TestResult.PARTIAL if score >= 0.3 else TestResult.FAIL)
        )

        return TestOutcome(
            test_name="hierarchical_synthesis",
            result=result,
            score=score,
            details=f"Hierarchical synthesis test. Score: {score:.2f}",
            expected_answer="Synthesized introduction explaining somatic framework as bio-energetic network",
            found_evidence="; ".join(evidence_parts)
            if evidence_parts
            else "No synthesis evidence",
            failure_reason=None
            if result == TestResult.PASS
            else "Missing proper hierarchical synthesis",
        )

    def evaluate(self, knowledge_data: dict[str, Any]) -> TestOutcome:
        """Run all causal relationship tests."""
        causality_test = self.test_prf_somatic_causality(knowledge_data)
        synthesis_test = self.test_hierarchical_synthesis(knowledge_data)

        # Combined scoring (skip synthesis if unable to evaluate)
        if synthesis_test.result == TestResult.UNABLE_TO_EVALUATE:
            combined_score = causality_test.score
            combined_result = causality_test.result
        else:
            combined_score = (causality_test.score + synthesis_test.score) / 2
            combined_result = (
                TestResult.PASS
                if combined_score >= 0.7
                else (TestResult.PARTIAL if combined_score >= 0.4 else TestResult.FAIL)
            )

        return TestOutcome(
            test_name=self.name,
            result=combined_result,
            score=combined_score,
            details=f"Combined causal relationship. Causality: {causality_test.score:.2f}, Synthesis: {synthesis_test.score:.2f}",
            expected_answer="Correct causal relationships and hierarchical synthesis",
            found_evidence=f"Causality evidence: {causality_test.found_evidence}; Synthesis evidence: {synthesis_test.found_evidence}",
            failure_reason=None
            if combined_result == TestResult.PASS
            else "Missing causal understanding or synthesis",
        )


class NuanceAmbiguityTest(SemanticTest):
    """Tests that verify capture of nuances and ambiguity."""

    def __init__(self) -> None:
        super().__init__(
            name="nuance_ambiguity",
            description="Verifies capture of complexity, dual nature, and unresolved aspects",
        )

    def test_crystallization_duality(
        self, knowledge_data: dict[str, Any]
    ) -> TestOutcome:
        """Test if crystallization of self is presented with dual nature."""
        all_text = self._extract_summaries_text(knowledge_data)

        # Look for crystallization concept
        crystal_terms = [
            "crystallization",
            "cristalización",
            "crystallize",
            "cristaliza",
        ]

        # Look for positive aspects
        positive_terms = [
            "efficient",
            "eficiente",
            "stable",
            "estable",
            "necessary",
            "necesario",
            "development",
            "desarrollo",
        ]

        # Look for negative aspects
        negative_terms = [
            "barrier",
            "barrera",
            "rigid",
            "rígido",
            "inflexible",
            "limitation",
            "limitación",
        ]

        # Look for dual/balanced language
        dual_terms = [
            "both",
            "ambos",
            "dual",
            "balance",
            "equilibrio",
            "two",
            "dos",
            "aspect",
            "aspecto",
        ]

        found_crystal = any(term in all_text.lower() for term in crystal_terms)
        found_positive = any(term in all_text.lower() for term in positive_terms)
        found_negative = any(term in all_text.lower() for term in negative_terms)
        found_dual = any(term in all_text.lower() for term in dual_terms)

        score = 0.0
        evidence_parts = []

        if found_crystal:
            score += 0.2
            evidence_parts.append("Found crystallization concept")
        else:
            return TestOutcome(
                test_name="crystallization_duality",
                result=TestResult.UNABLE_TO_EVALUATE,
                score=0.0,
                details="Crystallization concept not found in text",
                expected_answer="Dual nature of crystallization process",
                found_evidence="Concept not discussed",
                failure_reason="Missing crystallization concept",
            )

        if found_positive and found_negative:
            score += 0.6
            evidence_parts.append("Found both positive and negative aspects")
        elif found_positive or found_negative:
            score += 0.2
            evidence_parts.append("Found only one-sided view (positive or negative)")

        if found_dual:
            score += 0.2
            evidence_parts.append("Found dual/balanced language")

        result = (
            TestResult.PASS
            if score >= 0.8
            else (TestResult.PARTIAL if score >= 0.4 else TestResult.FAIL)
        )

        return TestOutcome(
            test_name="crystallization_duality",
            result=result,
            score=score,
            details=f"Crystallization duality test. Score: {score:.2f}",
            expected_answer="Crystallization as both efficient/necessary and potentially limiting/rigid",
            found_evidence="; ".join(evidence_parts)
            if evidence_parts
            else "No duality evidence found",
            failure_reason=None
            if result == TestResult.PASS
            else "Missing dual nature of crystallization",
        )

    def test_observer_paradox_unresolved(
        self, knowledge_data: dict[str, Any]
    ) -> TestOutcome:
        """Test if observer paradox is presented as unresolved."""
        all_text = self._extract_summaries_text(knowledge_data)

        # Look for the paradox
        paradox_terms = [
            "observer paradox",
            "paradoja del observador",
            "dissonant observer",
            "observador disonante",
        ]

        # Look for resolution language (negative indicators)
        resolved_terms = [
            "resolved",
            "resuelta",
            "solved",
            "solucionada",
            "answer",
            "respuesta",
            "solution",
            "solución",
        ]

        # Look for unresolved/speculative language (positive indicators)
        unresolved_terms = [
            "unresolved",
            "no resuelta",
            "controversial",
            "controvertida",
            "speculative",
            "especulativa",
            "potential",
            "potencial",
        ]

        found_paradox = any(term in all_text.lower() for term in paradox_terms)
        found_resolved = any(term in all_text.lower() for term in resolved_terms)
        found_unresolved = any(term in all_text.lower() for term in unresolved_terms)

        score = 0.0
        evidence_parts = []

        if found_paradox:
            score += 0.3
            evidence_parts.append("Found observer paradox concept")
        else:
            return TestOutcome(
                test_name="observer_paradox_unresolved",
                result=TestResult.UNABLE_TO_EVALUATE,
                score=0.0,
                details="Observer paradox not found in text",
                expected_answer="Observer paradox presented as unresolved issue",
                found_evidence="Paradox not discussed",
                failure_reason="Missing observer paradox",
            )

        if found_unresolved:
            score += 0.5
            evidence_parts.append("Found unresolved/speculative language")

        if found_resolved and not found_unresolved:
            score = 0.1  # Penalty for presenting as resolved
            evidence_parts.append("WARNING: Paradox presented as resolved")
        elif found_resolved and found_unresolved:
            score += 0.2  # Mentions solutions but acknowledges limitations
            evidence_parts.append("Found balanced resolved/unresolved discussion")

        result = (
            TestResult.PASS
            if score >= 0.7
            else (TestResult.PARTIAL if score >= 0.3 else TestResult.FAIL)
        )

        return TestOutcome(
            test_name="observer_paradox_unresolved",
            result=result,
            score=score,
            details=f"Observer paradox unresolved test. Score: {score:.2f}",
            expected_answer="Observer paradox acknowledged as unresolved with only speculative solutions",
            found_evidence="; ".join(evidence_parts)
            if evidence_parts
            else "No paradox evidence found",
            failure_reason=None
            if result == TestResult.PASS
            else "Missing unresolved nature of paradox",
        )

    def evaluate(self, knowledge_data: dict[str, Any]) -> TestOutcome:
        """Run all nuance and ambiguity tests."""
        crystallization_test = self.test_crystallization_duality(knowledge_data)
        paradox_test = self.test_observer_paradox_unresolved(knowledge_data)

        # Combined scoring (handle unable to evaluate cases)
        evaluable_tests = []
        if crystallization_test.result != TestResult.UNABLE_TO_EVALUATE:
            evaluable_tests.append(crystallization_test)
        if paradox_test.result != TestResult.UNABLE_TO_EVALUATE:
            evaluable_tests.append(paradox_test)

        if not evaluable_tests:
            return TestOutcome(
                test_name=self.name,
                result=TestResult.UNABLE_TO_EVALUATE,
                score=0.0,
                details="No nuance concepts found in text for evaluation",
                expected_answer="Complex nuances and unresolved aspects captured",
                found_evidence="Concepts not discussed",
                failure_reason="Missing key concepts for nuance evaluation",
            )

        combined_score = sum(test.score for test in evaluable_tests) / len(
            evaluable_tests
        )
        combined_result = (
            TestResult.PASS
            if combined_score >= 0.7
            else (TestResult.PARTIAL if combined_score >= 0.4 else TestResult.FAIL)
        )

        return TestOutcome(
            test_name=self.name,
            result=combined_result,
            score=combined_score,
            details=f"Combined nuance/ambiguity. Crystallization: {crystallization_test.score:.2f}, Paradox: {paradox_test.score:.2f}",
            expected_answer="Nuanced understanding of complex and ambiguous aspects",
            found_evidence=f"Crystallization evidence: {crystallization_test.found_evidence}; Paradox evidence: {paradox_test.found_evidence}",
            failure_reason=None
            if combined_result == TestResult.PASS
            else "Missing nuanced understanding",
        )
