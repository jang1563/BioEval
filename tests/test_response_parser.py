"""
Tests for the Response Parser module.

Tests regex-based extraction across all task types.
Does NOT test LLM fallback (requires API calls).
"""

import pytest
from bioeval.scoring.response_parser import (
    extract_step_ordering,
    extract_numerical_value,
    extract_categorical_label,
    extract_direction,
    extract_gene_directions,
    extract_flaw_list,
    extract_confidence_structured,
    extract_yes_no,
    extract_interaction_type,
    parse_response,
    ParseResult,
    FlawItem,
)

# =============================================================================
# STEP ORDERING TESTS
# =============================================================================


class TestStepOrdering:
    def test_comma_separated(self):
        response = "The correct order is: 3, 1, 5, 2, 4"
        result = extract_step_ordering(response, 5)
        assert result.success
        assert result.value == [3, 1, 5, 2, 4]

    def test_arrow_separated(self):
        response = "The proper sequence: 3 → 1 → 5 → 2 → 4"
        result = extract_step_ordering(response, 5)
        assert result.success
        assert result.value == [3, 1, 5, 2, 4]

    def test_standalone_line(self):
        response = """Based on my analysis, the steps should be ordered:
3, 1, 5, 2, 4

This ordering ensures proper flow."""
        result = extract_step_ordering(response, 5)
        assert result.success
        assert result.value == [3, 1, 5, 2, 4]

    def test_step_references(self):
        response = """The correct ordering:
1. Step 3 (Extract RNA)
2. Step 1 (Prepare samples)
3. Step 5 (Run qPCR)
4. Step 2 (Quantify RNA)
5. Step 4 (Add reagents)"""
        result = extract_step_ordering(response, 5)
        assert result.success
        assert result.value == [3, 1, 5, 2, 4]

    def test_twelve_steps(self):
        response = "The correct order would be: 3, 7, 1, 4, 12, 5, 8, 6, 11, 9, 2, 10"
        result = extract_step_ordering(response, 12)
        assert result.success
        assert len(result.value) == 12
        assert set(result.value) == set(range(1, 13))

    def test_invalid_response_fails(self):
        response = "I think the steps should be done carefully."
        result = extract_step_ordering(response, 5)
        assert not result.success

    def test_partial_ordering_fails(self):
        response = "The order is: 1, 2, 3"
        result = extract_step_ordering(response, 5)
        assert not result.success

    def test_fallback_extraction(self):
        """Test the last-resort strategy of collecting distinct numbers."""
        response = """First, do step 3 to prepare. Then step 1 for setup.
Next is step 5, followed by step 2. Finally, step 4."""
        result = extract_step_ordering(response, 5)
        assert result.success
        assert result.value == [3, 1, 5, 2, 4]
        assert result.confidence < 0.8  # lower confidence for fallback


# =============================================================================
# NUMERICAL VALUE TESTS
# =============================================================================


class TestNumericalValue:
    def test_answer_pattern(self):
        response = "Using the dilution formula: V1 = (500 × 1) / 10 = 50 mL of stock solution."
        result = extract_numerical_value(response, expected_value=50.0)
        assert result.success
        assert abs(result.value - 50.0) < 1.0

    def test_volume_with_unit(self):
        response = "You need to load 12 μL per well."
        result = extract_numerical_value(response, expected_value=12.0, expected_unit="μL")
        assert result.success
        assert abs(result.value - 12.0) < 0.5

    def test_scientific_notation(self):
        response = "The concentration is 1.5 x 10^6 cells/mL"
        result = extract_numerical_value(response, expected_value=1.5e6)
        assert result.success
        assert abs(result.value - 1.5e6) / 1.5e6 < 0.05

    def test_multiple_values(self):
        response = "You need 10 μL of stock and 90 μL of water."
        result = extract_numerical_value(response, expected_value=10.0)
        assert result.success
        assert abs(result.value - 10.0) < 1.0

    def test_no_numbers_fails(self):
        response = "You should use a small amount of buffer."
        result = extract_numerical_value(response)
        assert not result.success or result.confidence < 0.3

    def test_percentage(self):
        response = "The purity is approximately 95%."
        result = extract_numerical_value(response, expected_value=95.0)
        assert result.success


# =============================================================================
# CATEGORICAL LABEL TESTS
# =============================================================================


class TestCategoricalLabel:
    def test_essential_prediction(self):
        response = """Based on the oncogene addiction principle, KRAS is essential
        in A549 cells because these cells are dependent on KRAS signaling."""
        result = extract_categorical_label(response, ["essential", "non-essential"])
        assert result.success
        assert result.value == "essential"

    def test_non_essential_prediction(self):
        response = """Since TP53 is already mutated in A549 cells, the gene is
        non-essential - knocking it out has minimal additional effect."""
        result = extract_categorical_label(response, ["essential", "non-essential"])
        assert result.success
        assert result.value == "non-essential"

    def test_negation_handling(self):
        response = """KRAS is not essential in wild-type KRAS cells because there
        is no oncogene addiction."""
        result = extract_categorical_label(response, ["essential", "non-essential"])
        assert result.success
        assert result.value == "non-essential"

    def test_bold_label(self):
        response = "My prediction: the gene is **essential** in this cell line."
        result = extract_categorical_label(response, ["essential", "non-essential"])
        assert result.success
        assert result.value == "essential"

    def test_context_dependent(self):
        response = """The effect would be context-dependent, varying based on
        the specific cell line and mutation status."""
        result = extract_categorical_label(response, ["essential", "non-essential", "context-dependent"])
        assert result.success
        assert result.value == "context-dependent"

    def test_no_label_found(self):
        response = "This gene plays a role in cell signaling."
        result = extract_categorical_label(response, ["essential", "non-essential"])
        assert not result.success


# =============================================================================
# DIRECTION EXTRACTION TESTS
# =============================================================================


class TestDirection:
    def test_decreased_pathway(self):
        response = "EGFR inhibition leads to decreased MAPK/ERK signaling."
        result = extract_direction(response, target="MAPK/ERK")
        assert result.success
        assert result.value == "down"

    def test_increased_pathway(self):
        response = "mTOR inhibition results in increased autophagy activation."
        result = extract_direction(response, target="Autophagy")
        assert result.success
        assert result.value == "up"

    def test_no_change(self):
        response = "The PI3K pathway shows no change after this treatment."
        result = extract_direction(response, target="PI3K")
        assert result.success
        assert result.value == "no_change"

    def test_general_direction(self):
        response = "Overall, signaling is suppressed and activity is reduced."
        result = extract_direction(response)
        assert result.value == "down"

    def test_ambiguous(self):
        response = "Some pathways are activated while others are suppressed."
        result = extract_direction(response)
        assert result.value == "unclear"


# =============================================================================
# GENE DIRECTION TESTS
# =============================================================================


class TestGeneDirections:
    def test_explicit_sections(self):
        response = """The drug treatment results in:
Upregulated: GILZ, FKBP5, DUSP1
Downregulated: IL2, IFNG, TNF"""
        result = extract_gene_directions(response)
        assert result.success
        assert "GILZ" in result.value["upregulated"]
        assert "IL2" in result.value["downregulated"]

    def test_line_by_line(self):
        response = """Key transcriptional changes:
- FKBP5 is upregulated as a direct GR target
- MYC expression is downregulated
- BCL2 is decreased via indirect effects"""
        result = extract_gene_directions(response)
        assert result.success
        assert "FKBP5" in result.value["upregulated"]
        assert "MYC" in result.value["downregulated"] or "BCL2" in result.value["downregulated"]

    def test_no_genes(self):
        response = "The drug causes cell death through apoptosis."
        result = extract_gene_directions(response)
        assert not result.success


# =============================================================================
# FLAW LIST EXTRACTION TESTS
# =============================================================================


class TestFlawList:
    def test_numbered_flaws(self):
        response = """I identified the following flaws in this experimental design:

1. **Missing negative control** (Category: Controls, Severity: Critical)
No vehicle (DMSO) control was included to account for solvent effects.
Fix: Include DMSO-only control at the highest concentration used.

2. **Pseudoreplication** (Category: Statistics, Severity: Critical)
The 3 wells per condition are technical replicates, not biological replicates.
Fix: Repeat experiment on 3 different days with different cell passages.

3. **Missing positive control** (Category: Controls, Severity: Major)
No known cytotoxic agent was included to validate assay performance.
Fix: Include staurosporine as a positive control."""
        result = extract_flaw_list(response)
        assert result.success
        assert len(result.value) >= 3

    def test_simple_list(self):
        response = """Design flaws:
1. No control group - this is a critical problem
2. Insufficient sample size - only n=3 replicates
3. Wrong statistical test used for this type of data"""
        result = extract_flaw_list(response)
        assert result.success
        assert len(result.value) >= 2

    def test_severity_extraction(self):
        response = """1. Critical flaw: Missing negative control, no DMSO vehicle was used.
2. Major issue: The statistical analysis used t-test instead of ANOVA.
3. Minor concern: Blinding was not mentioned."""
        result = extract_flaw_list(response)
        assert result.success
        has_critical = any(f.severity == "critical" for f in result.value)
        assert has_critical

    def test_no_flaws(self):
        response = "This is a well-designed experiment with proper controls."
        result = extract_flaw_list(response)
        assert not result.success or len(result.value) == 0


# =============================================================================
# CONFIDENCE EXTRACTION TESTS
# =============================================================================


class TestConfidenceExtraction:
    def test_numeric_percent(self):
        response = "**Confidence:** 85%\nThis is well-established biology."
        result = extract_confidence_structured(response)
        assert result.success
        assert abs(result.value - 0.85) < 0.01

    def test_categorical_high(self):
        response = "**Confidence:** HIGH\nWell-documented mechanism."
        result = extract_confidence_structured(response)
        assert result.success
        assert result.value > 0.7

    def test_categorical_low(self):
        response = "**Confidence:** LOW\nNot enough evidence."
        result = extract_confidence_structured(response)
        assert result.success
        assert result.value < 0.4

    def test_categorical_medium(self):
        response = "Confidence: medium\nSome evidence supports this."
        result = extract_confidence_structured(response)
        assert result.success
        assert 0.4 <= result.value <= 0.7

    def test_no_confidence_statement(self):
        response = "The mechanism involves MAPK signaling pathway activation."
        result = extract_confidence_structured(response)
        assert not result.success


# =============================================================================
# YES/NO EXTRACTION TESTS
# =============================================================================


class TestYesNo:
    def test_yes(self):
        result = extract_yes_no("Yes, MYC is essential in K562 cells.")
        assert result.success
        assert result.value is True

    def test_no(self):
        result = extract_yes_no("No, this gene is not essential in this context.")
        assert result.success
        assert result.value is False

    def test_ambiguous(self):
        result = extract_yes_no("The effect depends on the specific cell line context.")
        assert not result.success


# =============================================================================
# INTERACTION TYPE TESTS
# =============================================================================


class TestInteractionType:
    def test_synergistic(self):
        response = "The combined loss of RB1 and TP53 shows a synergistic interaction."
        result = extract_interaction_type(response)
        assert result.success
        assert result.value == "synergistic"

    def test_suppressive(self):
        response = "53BP1 loss has a suppressive effect on BRCA1 deficiency."
        result = extract_interaction_type(response)
        assert result.success
        assert result.value == "suppressive"

    def test_synthetic_lethal(self):
        response = "PARP1 and BRCA1 exhibit synthetic lethality."
        result = extract_interaction_type(response)
        assert result.success
        assert result.value == "synthetic_lethal"

    def test_enhancing(self):
        response = "STK11 loss has an enhancing effect on KRAS-driven growth."
        result = extract_interaction_type(response)
        assert result.success
        assert result.value == "enhancing"


# =============================================================================
# UNIFIED PARSE INTERFACE TESTS
# =============================================================================


class TestParseResponse:
    def test_knockout_prediction(self):
        response = """Based on KRAS oncogene addiction, KRAS knockout would be essential
        in A549 cells. **Confidence:** HIGH"""
        results = parse_response(
            response,
            task_type="knockout_prediction",
            ground_truth={"ground_truth": {"effect": "essential"}},
        )
        assert "effect" in results
        assert results["effect"].success
        assert results["effect"].value == "essential"
        assert "confidence" in results

    def test_step_ordering(self):
        response = "The correct order is: 3, 1, 5, 2, 4"
        results = parse_response(
            response,
            task_type="step_ordering",
            ground_truth={"correct_steps": ["a", "b", "c", "d", "e"]},
        )
        assert "ordering" in results
        assert results["ordering"].success

    def test_flaw_detection(self):
        response = """1. Missing control: no DMSO vehicle control was used
2. Pseudoreplication: technical replicates treated as biological"""
        results = parse_response(response, task_type="flaw_detection")
        assert "flaws" in results
        assert results["flaws"].success

    def test_unknown_task_type(self):
        results = parse_response("some response", task_type="unknown_type")
        assert len(results) == 0


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    def test_empty_response(self):
        assert not extract_step_ordering("", 5).success
        assert not extract_categorical_label("", ["a", "b"]).success
        assert extract_direction("").value == "unclear"

    def test_very_long_response(self):
        long_response = "word " * 5000 + "The answer is essential."
        result = extract_categorical_label(long_response, ["essential", "non-essential"])
        assert result.success

    def test_special_characters(self):
        response = "The concentration is 1.5 × 10^6 cells/mL (±0.2)"
        result = extract_numerical_value(response, expected_value=1.5e6)
        assert result.success
