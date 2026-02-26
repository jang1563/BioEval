"""
Response Parser Module

Extracts structured information from free-text LLM responses.
Primary strategy: regex/pattern-based extraction (fast, free).
Fallback strategy: LLM-based extraction via Haiku (slower, costs money).

Target: >= 85% extraction success rate across all task types.
"""

import re
import json
import logging
from typing import Optional, Literal
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ParseResult:
    """Result of a parsing attempt."""
    success: bool
    value: object  # The extracted value
    method: str  # "regex", "llm", or "failed"
    confidence: float = 1.0  # How confident we are in the extraction
    raw_match: str = ""  # The raw text that was matched


@dataclass
class FlawItem:
    """Single flaw extracted from a DesignCheck response."""
    description: str
    category: Optional[str] = None  # controls, statistics, confounders, technical, interpretation
    severity: Optional[str] = None  # critical, major, minor
    fix: Optional[str] = None


@dataclass
class GeneDirection:
    """Gene with its expression direction."""
    gene: str
    direction: Literal["up", "down", "unchanged", "unclear"]


# =============================================================================
# STEP ORDERING EXTRACTION (ProtoReason)
# =============================================================================

def extract_step_ordering(response: str, num_steps: int) -> ParseResult:
    """
    Extract step ordering from a response.

    Looks for patterns like:
    - "3, 1, 5, 2, 4"
    - "Step 3 → Step 1 → Step 5"
    - "1. Step 3\n2. Step 1\n..."
    - Numbered lists where numbers reference original step numbers

    Args:
        response: The LLM's free-text response
        num_steps: The number of steps that were shuffled

    Returns:
        ParseResult with value as list[int] (1-indexed step numbers in predicted order)
    """
    # Strategy 1: Look for explicit comma/arrow-separated ordering
    # e.g., "The correct order is: 3, 1, 5, 2, 4"
    # or "3 → 1 → 5 → 2 → 4"
    order_patterns = [
        # "correct order: 3, 1, 5, 2, 4" or "order is: 3, 1, 5, 2, 4"
        r'(?:correct|proper|right|logical)\s+(?:order|sequence)[:\s]+is[:\s]*([\d][\d\s,→\->]+[\d])',
        r'(?:correct|proper|right|logical)\s+(?:order|sequence)[:\s]*([\d][\d\s,→\->]+[\d])',
        r'(?:order|sequence)\s+(?:is|should be|would be)[:\s]*([\d][\d\s,→\->]+[\d])',
        # Standalone line of numbers: "3, 1, 5, 2, 4"
        r'^[\s]*([\d]+[\s]*[,→\->][\s]*[\d]+(?:[\s]*[,→\->][\s]*[\d]+)+)[\s]*$',
    ]

    for pattern in order_patterns:
        match = re.search(pattern, response, re.IGNORECASE | re.MULTILINE)
        if match:
            raw = match.group(1)
            numbers = [int(n) for n in re.findall(r'\d+', raw)]
            if _is_valid_ordering(numbers, num_steps):
                return ParseResult(
                    success=True,
                    value=numbers,
                    method="regex",
                    confidence=0.9,
                    raw_match=raw,
                )

    # Strategy 2: Look for numbered list referencing step numbers
    # "1. Step 5 (Extract RNA...)\n2. Step 2 (Measure RNA...)"
    # Pattern: line starts with reordered position, contains "step X"
    step_refs = re.findall(
        r'(?:^|\n)\s*\d+[\.\)]\s*.*?(?:step\s+|#)(\d+)',
        response,
        re.IGNORECASE,
    )
    if step_refs:
        numbers = [int(n) for n in step_refs]
        if _is_valid_ordering(numbers, num_steps):
            return ParseResult(
                success=True,
                value=numbers,
                method="regex",
                confidence=0.8,
                raw_match=str(numbers),
            )

    # Strategy 3: Scan for any sequence of N distinct numbers in [1, num_steps]
    # This is a fallback — less confident
    all_numbers = re.findall(r'\b(\d+)\b', response)
    all_ints = [int(n) for n in all_numbers if 1 <= int(n) <= num_steps]

    # Try to find the first contiguous window of num_steps distinct values
    seen = []
    for n in all_ints:
        if n not in seen:
            seen.append(n)
        if len(seen) == num_steps:
            break

    if len(seen) == num_steps and set(seen) == set(range(1, num_steps + 1)):
        return ParseResult(
            success=True,
            value=seen,
            method="regex",
            confidence=0.5,
            raw_match=str(seen),
        )

    return ParseResult(success=False, value=None, method="failed")


def _is_valid_ordering(numbers: list[int], num_steps: int) -> bool:
    """Check if extracted numbers form a valid permutation of 1..num_steps."""
    return (
        len(numbers) == num_steps
        and set(numbers) == set(range(1, num_steps + 1))
    )


# =============================================================================
# NUMERICAL VALUE EXTRACTION (ProtoReason calculations)
# =============================================================================

def extract_numerical_value(
    response: str,
    expected_value: Optional[float] = None,
    expected_unit: Optional[str] = None,
    tolerance: float = 0.05,
) -> ParseResult:
    """
    Extract a numerical answer from a calculation response.

    Handles:
    - "The answer is 12 uL"
    - "= 1.5 × 10^6 cells/mL"
    - "50 mL of stock and 450 mL of water"
    - Scientific notation: "1.5e6", "1.5 × 10^6"

    Args:
        response: The LLM's free-text response
        expected_value: If provided, try to match this specific value
        expected_unit: If provided, look for values near this unit
        tolerance: Relative tolerance for matching expected_value

    Returns:
        ParseResult with value as float
    """
    # Normalize response
    text = response.replace("×", "x").replace("−", "-")
    # Normalize Unicode superscript digits to ^N notation
    _super_map = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
    text = re.sub(r'10([⁰¹²³⁴⁵⁶⁷⁸⁹]+)', lambda m: f"10^{m.group(1).translate(_super_map)}", text)
    # Remove commas inside numbers (1,500,000 → 1500000)
    text = re.sub(r'(\d),(\d{3})', r'\1\2', text)
    text = re.sub(r'(\d),(\d{3})', r'\1\2', text)  # repeat for millions+

    # Strategy 1: Look for "answer is X" or "= X" patterns
    answer_patterns = [
        # 3-group patterns: number, optional exponent, unit
        r'(?:answer|result|total|volume|concentration|amount)\s+(?:is|=|:)\s*'
        r'([\d]+\.?[\d]*)\s*(?:[x×]\s*10\^?(\d+))?\s*(\S*)',
        r'(?:=|equals)\s*([\d]+\.?[\d]*)\s*(?:[x×]\s*10\^?(\d+))?\s*(\S*)',
        # 2-group pattern: number, unit (no scientific notation)
        r'(?:need|require|use)\s+([\d]+\.?[\d]*)\s*(\S*)',
    ]

    candidates = []

    for pattern in answer_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = float(match.group(1))
            # Handle scientific notation (only for 3-group patterns)
            if match.lastindex >= 3 and match.group(2):
                try:
                    exponent = int(match.group(2))
                    value *= 10 ** exponent
                except ValueError:
                    pass
            unit = match.group(match.lastindex) if match.lastindex >= 2 else ""
            candidates.append((value, unit, match.group(0)))

    # Strategy 2: Find all numbers with units
    number_unit_pattern = r'([\d]+\.?[\d]*)\s*(?:[x×]\s*10\^?(\d+))?\s*(μ[Ll]|mL|[Ll]|μg|mg|g|ng|cells?/mL|%|μM|mM|nM)'
    for match in re.finditer(number_unit_pattern, text):
        value = float(match.group(1))
        if match.group(2):
            value *= 10 ** int(match.group(2))
        unit = match.group(3)
        candidates.append((value, unit, match.group(0)))

    if not candidates:
        # Last resort: find decimal numbers, filtering out likely non-answer values
        all_nums = re.finditer(r'(?<![.\d])([\d]+\.[\d]+|[\d]+)(?![.\d])', text)
        for m in all_nums:
            n = m.group(1)
            val = float(n)
            # Filter out likely years (1900-2099)
            if 1900 <= val <= 2099 and '.' not in n:
                continue
            # Filter out figure/table/step references: "Figure 2", "Table 3", "Step 1"
            prefix_start = max(0, m.start() - 15)
            prefix = text[prefix_start:m.start()].lower()
            if re.search(r'(?:figure|fig\.|table|tab\.|step|page|reference|ref\.)\s*$', prefix):
                continue
            candidates.append((val, "", n))

    if not candidates:
        return ParseResult(success=False, value=None, method="failed")

    # If expected_value is given, find the closest match
    if expected_value is not None:
        best = None
        best_diff = float("inf")
        for val, unit, raw in candidates:
            diff = abs(val - expected_value) / max(abs(expected_value), 1e-10)
            if diff < best_diff:
                best_diff = diff
                best = (val, unit, raw)

        if best and best_diff <= tolerance:
            return ParseResult(
                success=True,
                value=best[0],
                method="regex",
                confidence=0.95 if best_diff < 0.01 else 0.7,
                raw_match=best[2],
            )

    # If expected_unit given, filter by unit
    if expected_unit:
        unit_matches = [
            (v, u, r) for v, u, r in candidates
            if _unit_matches(u, expected_unit)
        ]
        if unit_matches:
            return ParseResult(
                success=True,
                value=unit_matches[0][0],
                method="regex",
                confidence=0.7,
                raw_match=unit_matches[0][2],
            )

    # Prefer candidates with units; among those, prefer later occurrences (final answer)
    with_units = [(v, u, r) for v, u, r in candidates if u]
    chosen = with_units[-1] if with_units else candidates[-1]
    return ParseResult(
        success=True,
        value=chosen[0],
        method="regex",
        confidence=0.5,
        raw_match=chosen[2],
    )


def _unit_matches(extracted: str, expected: str) -> bool:
    """Check if extracted unit roughly matches expected unit."""
    extracted = extracted.lower().strip()
    expected = expected.lower().strip()
    if not extracted or not expected:
        return False
    # Normalize common variants
    norm = {"ul": "μl", "ml": "ml", "ug": "μg", "um": "μm", "nm": "nm"}
    e1 = norm.get(extracted, extracted)
    e2 = norm.get(expected, expected)
    return e1 == e2 or extracted in expected or expected in extracted


# =============================================================================
# LABEL EXTRACTION (CausalBio knockout — essential/non-essential)
# =============================================================================

def extract_categorical_label(
    response: str,
    labels: list[str],
    context_window: int = 200,
) -> ParseResult:
    """
    Extract a categorical prediction from response.

    Used for knockout predictions ("essential" vs "non-essential"),
    epistasis types ("synergistic", "suppressive", "enhancing"),
    and similar classification tasks.

    Args:
        response: The LLM's free-text response
        labels: List of valid label strings to look for
        context_window: How many characters of context around the match to use for disambiguation

    Returns:
        ParseResult with value as str (one of the labels)
    """
    response_lower = response.lower()
    # Strip markdown bold markers to prevent interference with regex
    response_clean = re.sub(r'\*\*', '', response_lower)

    # Sort labels longest-first so "non-essential" is checked before "essential"
    sorted_labels = sorted(labels, key=len, reverse=True)

    # Strategy 1: Look for "prediction: <label>" or "is <label>" patterns
    for label in sorted_labels:
        label_lower = label.lower()
        # Direct prediction statements
        patterns = [
            rf'(?:prediction|predict|classify|determine|conclude)[:\s]+.*?{re.escape(label_lower)}',
            rf'(?:gene\s+is|would\s+be|this\s+is|classified\s+as)\s+{re.escape(label_lower)}',
            rf'{re.escape(label_lower)}\s+(?:gene|in\s+this|for\s+this)',
        ]
        for pattern in patterns:
            if re.search(pattern, response_clean):
                return ParseResult(
                    success=True,
                    value=label,
                    method="regex",
                    confidence=0.9,
                    raw_match=label,
                )

    # Strategy 2: Count EXCLUSIVE occurrences weighted by position
    # For labels that are substrings of other labels (e.g. "essential" in
    # "non-essential"), only count occurrences that DON'T match longer labels.
    scores = {}
    # Build exclusion patterns: for each label, exclude positions where a
    # longer label also matches at the same location
    longer_patterns = {}
    for label in sorted_labels:
        label_lower = label.lower()
        longer = [l.lower() for l in sorted_labels if len(l) > len(label) and label_lower in l.lower()]
        longer_patterns[label] = longer

    for label in sorted_labels:
        label_lower = label.lower()
        positions = []
        for m in re.finditer(re.escape(label_lower), response_clean):
            pos = m.start()
            # Check if this match is part of a longer label match
            is_substring_of_longer = False
            for longer_label in longer_patterns[label]:
                # Check if a longer label spans this position
                window_start = max(0, pos - len(longer_label))
                window = response_clean[window_start:pos + len(label_lower) + len(longer_label)]
                if longer_label in window:
                    is_substring_of_longer = True
                    break
            if not is_substring_of_longer:
                positions.append(pos)

        if positions:
            resp_len = max(len(response_clean), 1)
            score = sum(1.0 - (pos / resp_len) * 0.5 for pos in positions)
            scores[label] = score

    if scores:
        best_label = max(scores, key=scores.get)
        # Check for negation: "is NOT essential" — works for any number of labels
        negation_check = _check_negation(response_clean, best_label.lower())
        if negation_check:
            # Find the negated counterpart (e.g., "essential" → "non-essential")
            negated_candidates = [l for l in labels if l != best_label
                                  and best_label.lower() in l.lower()]
            if negated_candidates:
                return ParseResult(
                    success=True,
                    value=negated_candidates[0],
                    method="regex",
                    confidence=0.7,
                    raw_match=f"negated {best_label} -> {negated_candidates[0]}",
                )
            elif len(labels) == 2:
                other = [l for l in labels if l != best_label][0]
                return ParseResult(
                    success=True,
                    value=other,
                    method="regex",
                    confidence=0.7,
                    raw_match=f"negated {best_label} -> {other}",
                )
        return ParseResult(
            success=True,
            value=best_label,
            method="regex",
            confidence=0.6 if len(scores) == 1 else 0.5,
            raw_match=best_label,
        )

    return ParseResult(success=False, value=None, method="failed")


def _check_negation(text: str, label: str) -> bool:
    """Check if a label is negated in the text (e.g., 'not essential')."""
    # Look for negation patterns near the label
    neg_patterns = [
        rf'not\s+{re.escape(label)}',
        rf'non[\s-]{re.escape(label)}',
        rf'isn\'t\s+{re.escape(label)}',
        rf'is\s+not\s+{re.escape(label)}',
    ]
    return any(re.search(p, text) for p in neg_patterns)


# =============================================================================
# DIRECTION EXTRACTION (CausalBio pathways, drug response)
# =============================================================================

def extract_direction(
    response: str,
    target: Optional[str] = None,
) -> ParseResult:
    """
    Extract directional prediction (up/down/no_change) from response.

    Optionally scoped to a specific target (pathway name, gene name).

    Args:
        response: LLM response text
        target: Optional target name to scope the extraction to

    Returns:
        ParseResult with value as "up", "down", "no_change", or "unclear"
    """
    text = response.lower()

    # If target specified, try to find direction near the target mention
    if target:
        target_lower = target.lower()
        # Also handle / separated names like "MAPK/ERK"
        target_parts = [t.strip() for t in target_lower.split("/")]
        target_pattern = "|".join(re.escape(t) for t in target_parts if t)

        # Find all positions where target is mentioned
        matches = list(re.finditer(target_pattern, text))
        if matches:
            # Check context around each mention (100 chars before and after)
            for match in matches:
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                direction = _direction_from_context(context)
                if direction != "unclear":
                    return ParseResult(
                        success=True,
                        value=direction,
                        method="regex",
                        confidence=0.8,
                        raw_match=context.strip(),
                    )

    # Fallback: general direction from entire response
    direction = _direction_from_context(text)
    return ParseResult(
        success=direction != "unclear",
        value=direction,
        method="regex",
        confidence=0.5 if direction != "unclear" else 0.0,
        raw_match="",
    )


def _direction_from_context(text: str) -> Literal["up", "down", "no_change", "unclear"]:
    """Determine direction from a text context."""
    up_indicators = [
        "increased", "upregulated", "up-regulated", "elevated", "activated",
        "enhanced", "induced", "stimulated", "higher", "increase",
        "upregulation", "up-regulation", "induction", "amplified",
        "overexpressed", "gain", "rises", "boost",
    ]
    down_indicators = [
        "decreased", "downregulated", "down-regulated", "reduced", "inhibited",
        "suppressed", "blocked", "lower", "decrease", "loss",
        "downregulation", "down-regulation", "repressed", "diminished",
        "attenuated", "impaired", "abolished", "abrogated",
    ]
    no_change_indicators = [
        "no change", "unchanged", "unaffected", "no effect", "no significant",
        "minimal effect", "negligible",
    ]

    # Use literal matching here (not synonym expansion) to count distinct signals.
    # Synonym expansion inflates counts asymmetrically, breaking ambiguity detection.
    up_count = sum(1 for w in up_indicators if w in text)
    down_count = sum(1 for w in down_indicators if w in text)
    no_change_count = sum(1 for w in no_change_indicators if w in text)

    if no_change_count > 0 and up_count == 0 and down_count == 0:
        return "no_change"
    if up_count > down_count and up_count > 0:
        return "up"
    if down_count > up_count and down_count > 0:
        return "down"
    if up_count == down_count and up_count > 0:
        # Ambiguous — both directions mentioned
        return "unclear"
    return "unclear"


# =============================================================================
# GENE LIST EXTRACTION (CausalBio drug response)
# =============================================================================

def extract_gene_directions(response: str) -> ParseResult:
    """
    Extract lists of upregulated and downregulated genes from drug response predictions.

    Returns:
        ParseResult with value as {"upregulated": [str], "downregulated": [str]}
    """
    text = response

    # Gene name pattern: uppercase letters/numbers, 2-10 chars, optionally with /alias
    gene_pattern = r'\b([A-Z][A-Z0-9]{1,9}(?:/[A-Z][A-Z0-9]{1,9})?)\b'

    result = {"upregulated": [], "downregulated": []}

    # Strategy 1: Look for explicit up/downregulated sections
    # "Upregulated genes: GENE1, GENE2, GENE3"
    up_section = re.search(
        r'(?:upregulated|up-regulated|induced|activated|increased)[:\s]*'
        r'((?:[A-Z][A-Z0-9/]{1,15}[,\s]+)+[A-Z][A-Z0-9/]{1,15})',
        text,
    )
    down_section = re.search(
        r'(?:downregulated|down-regulated|repressed|decreased|suppressed)[:\s]*'
        r'((?:[A-Z][A-Z0-9/]{1,15}[,\s]+)+[A-Z][A-Z0-9/]{1,15})',
        text,
    )

    if up_section:
        result["upregulated"] = re.findall(gene_pattern, up_section.group(1))
    if down_section:
        result["downregulated"] = re.findall(gene_pattern, down_section.group(1))

    if result["upregulated"] or result["downregulated"]:
        return ParseResult(
            success=True,
            value=result,
            method="regex",
            confidence=0.8,
            raw_match=str(result),
        )

    # Strategy 2: Section-tracking — headers set direction for subsequent lines
    # Handles the common LLM pattern:
    #   **Genes expected to be UPREGULATED:**
    #   - GILZ ...
    #   - FKBP5 ...
    #   **Genes expected to be DOWNREGULATED:**
    #   - MYC ...
    up_keywords = ["upregulated", "up-regulated", "induced", "increased", "activated"]
    down_keywords = ["downregulated", "down-regulated", "repressed", "decreased", "suppressed"]

    lines = text.split("\n")
    current_section = None  # "up" or "down" or None
    # Non-gene words that match gene pattern but should be excluded
    noise_words = {
        "KEY", "GENES", "EXPECTED", "GENE", "THE", "FOR", "AND", "ARE",
        "WITH", "FROM", "THAT", "THIS", "NOT", "BUT", "ALL", "ANY",
        "PREDICTED", "RESPONSE", "DRUG", "CELL", "TYPE", "VIA", "DUE",
        "STEP", "ALSO", "BOTH", "EACH", "INTO", "OVER", "UPON",
        "HIGH", "LOW", "NEW", "PRO", "ANTI", "TO", "BE", "OF", "OR",
        "BY", "IN", "ON", "AT", "AS", "IF", "AN", "NO", "UP", "SO",
        "MECHANISM", "ACTION", "FUNCTION", "PATHWAY", "PHENOTYPE",
        "CELLULAR", "EFFECT", "EFFECTS", "CHANGE", "CHANGES",
        "PREDICTION", "EVIDENCE", "RESULT", "RESULTS",
        "DIRECT", "NORMAL", "CHAIN", "CAUSAL",
    }

    for line in lines:
        line_lower = line.lower()
        # Check if this line is a section header (sets direction for following lines)
        is_up_header = any(w in line_lower for w in up_keywords)
        is_down_header = any(w in line_lower for w in down_keywords)

        genes_in_line = [
            g for g in re.findall(gene_pattern, line)
            if g not in noise_words and len(g) >= 2
        ]

        if is_up_header and not is_down_header:
            current_section = "up"
            # Also extract genes from this header line itself
            if genes_in_line:
                result["upregulated"].extend(genes_in_line)
        elif is_down_header and not is_up_header:
            current_section = "down"
            if genes_in_line:
                result["downregulated"].extend(genes_in_line)
        elif genes_in_line and current_section:
            # Gene line under a section header — assign to current section
            if current_section == "up":
                result["upregulated"].extend(genes_in_line)
            else:
                result["downregulated"].extend(genes_in_line)
        else:
            # Check if this line indicates we've moved past gene sections
            line_lower_stripped = line_lower.strip()
            if any(kw in line_lower_stripped for kw in [
                "mechanism", "phenotype", "cellular", "expected experimental",
                "edge case", "confidence", "validation", "step ",
            ]):
                current_section = None

    # Deduplicate
    result["upregulated"] = list(dict.fromkeys(result["upregulated"]))
    result["downregulated"] = list(dict.fromkeys(result["downregulated"]))

    success = bool(result["upregulated"] or result["downregulated"])
    return ParseResult(
        success=success,
        value=result,
        method="regex",
        confidence=0.6 if success else 0.0,
        raw_match=str(result),
    )


# =============================================================================
# FLAW LIST EXTRACTION (DesignCheck)
# =============================================================================

# Valid categories and severities for validation
VALID_CATEGORIES = {"controls", "statistics", "confounders", "technical", "interpretation"}
VALID_SEVERITIES = {"critical", "major", "minor"}

# Mapping of common phrasing to standardized categories
CATEGORY_ALIASES = {
    "control": "controls",
    "statistical": "statistics",
    "stat": "statistics",
    "confounder": "confounders",
    "confounding": "confounders",
    "batch": "confounders",
    "replicate": "technical",
    "replication": "technical",
    "sample size": "statistics",
    "p-value": "statistics",
    "multiple testing": "statistics",
    "multiple comparisons": "statistics",
    "overstatement": "interpretation",
    "correlation": "interpretation",
    "causation": "interpretation",
    "cherry": "interpretation",
}


def extract_flaw_list(response: str) -> ParseResult:
    """
    Extract structured flaw descriptions from a DesignCheck response.

    Returns:
        ParseResult with value as list[FlawItem]
    """
    flaws = []

    # Strategy 0: Handle markdown "**Flaw #N: Title**" format (common Claude pattern)
    # Capture each flaw block with its sub-lines (problem, fix, severity, etc.)
    md_flaw_pattern = re.compile(
        r'\*\*(?:Flaw|Issue|Problem)\s*#?\d+[:\s]*([^*]+?)\*\*'
        r'((?:\n(?!\*\*(?:Flaw|Issue|Problem)\s*#?\d+).+)*)',
        re.IGNORECASE,
    )
    for m in md_flaw_pattern.finditer(response):
        title = m.group(1).strip()
        body = m.group(2).strip()
        full_text = f"{title} {body}"
        severity = _extract_severity(full_text.lower())
        category = _extract_category(full_text.lower())
        fix = _extract_fix(full_text)
        flaws.append(FlawItem(
            description=full_text[:500],
            category=category,
            severity=severity,
            fix=fix,
        ))

    if flaws:
        return ParseResult(
            success=True,
            value=flaws,
            method="regex_markdown",
            confidence=0.85,
            raw_match=f"{len(flaws)} flaws extracted (markdown format)",
        )

    # Strategy 1: Look for numbered/bulleted flaw items with category and severity
    # Pattern: "1. **Category: Controls** Severity: Critical ..."
    structured_pattern = (
        r'(?:^|\n)\s*[\d]+[\.\)]\s*'
        r'(?:\*\*)?(?:(?:category|type)[:\s]*)?([^*\n]+?)(?:\*\*)?'
        r'[\s\-–]*'
        r'(?:\*\*)?(?:severity[:\s]*)?([^*\n]*?)(?:\*\*)?'
        r'[:\s\-–]*'
        r'([^\n]+(?:\n(?!\s*[\d]+[\.\)])(?!\s*$)[^\n]+)*)'
    )

    # Strategy 2: Simpler — just find numbered items and analyze each
    # Split response into numbered items
    items = re.split(r'\n\s*(?=\d+[\.\)])', response)

    for item in items:
        if not item.strip():
            continue

        # Skip items that are clearly not flaws (e.g., "Overall assessment" section)
        item_lower = item.lower()
        if any(skip in item_lower for skip in [
            "overall assessment", "in summary", "overall, ", "in conclusion",
            "the design", "to summarize", "suggested fix",
        ]):
            continue

        # Extract category
        category = _extract_category(item_lower)

        # Extract severity
        severity = _extract_severity(item_lower)

        # Extract fix/recommendation
        fix = _extract_fix(item)

        # If the item looks like a flaw description
        if _looks_like_flaw(item_lower):
            # Clean up description
            desc = item.strip()
            # Remove leading number
            desc = re.sub(r'^\d+[\.\)]\s*', '', desc)
            # Truncate if too long (take first sentence)
            if len(desc) > 500:
                sentences = re.split(r'(?<=[.!?])\s+', desc)
                desc = sentences[0] if sentences else desc[:500]

            flaws.append(FlawItem(
                description=desc,
                category=category,
                severity=severity,
                fix=fix,
            ))

    if flaws:
        return ParseResult(
            success=True,
            value=flaws,
            method="regex",
            confidence=0.7,
            raw_match=f"{len(flaws)} flaws extracted",
        )

    # Fallback: look for any flaw-like sentences
    flaw_indicators = [
        r'(?:no|missing|lacks?|without|absent)\s+(?:\w+\s+)?(?:control|replicate)',
        r'(?:pseudo)?replication',
        r'(?:un|under)powered',
        r'confound(?:ed|er|ing)',
        r'batch\s+effect',
        r'multiple\s+(?:testing|comparisons?)',
        r'overstat(?:ed|ement)',
        r'correlation.*causation',
    ]
    for pattern in flaw_indicators:
        matches = re.findall(pattern, response, re.IGNORECASE)
        for match in matches:
            flaws.append(FlawItem(
                description=match,
                category=_extract_category(match.lower()),
                severity=None,
            ))

    return ParseResult(
        success=bool(flaws),
        value=flaws,
        method="regex",
        confidence=0.4 if flaws else 0.0,
        raw_match=f"{len(flaws)} flaws extracted (fallback)",
    )


def _extract_category(text: str) -> Optional[str]:
    """Extract flaw category from text."""
    # Check for explicit category label
    cat_match = re.search(r'category[:\s]+(\w+)', text)
    if cat_match:
        cat = cat_match.group(1).lower()
        if cat in VALID_CATEGORIES:
            return cat
        for alias, standard in CATEGORY_ALIASES.items():
            if alias in cat:
                return standard

    # Infer from content
    for alias, standard in CATEGORY_ALIASES.items():
        if alias in text:
            return standard

    return None


def _extract_severity(text: str) -> Optional[str]:
    """Extract flaw severity from text."""
    sev_match = re.search(r'severity[:\s]+(\w+)', text)
    if sev_match:
        sev = sev_match.group(1).lower()
        if sev in VALID_SEVERITIES:
            return sev

    # Check for severity keywords
    for sev in ["critical", "major", "minor"]:
        if sev in text:
            return sev

    return None


def _extract_fix(text: str) -> Optional[str]:
    """Extract suggested fix from text."""
    fix_patterns = [
        r'(?:fix|suggestion|recommend(?:ation)?|solution|should)[:\s]+([^\n]+)',
        r'(?:instead|better|improve)[:\s]+([^\n]+)',
    ]
    for pattern in fix_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _looks_like_flaw(text: str) -> bool:
    """Check if text describes a flaw/issue."""
    flaw_words = [
        "flaw", "issue", "problem", "error", "missing", "lack", "no ",
        "without", "insufficient", "incorrect", "wrong", "inappropriate",
        "confound", "bias", "overstat", "underpower", "pseudorep",
        "not ", "should ", "failed", "neglect",
    ]
    return any(w in text for w in flaw_words) and len(text) > 20


# =============================================================================
# CONFIDENCE EXTRACTION (Calibration)
# =============================================================================

def extract_confidence_structured(response: str) -> ParseResult:
    """
    Extract structured confidence from response.

    Improved version of calibration.py's extract_confidence, targeting
    responses that follow the structured confidence prompt format:
      **Confidence:** HIGH/MEDIUM/LOW
      or numeric: "Confidence: 85%"

    Returns:
        ParseResult with value as float (0-1 scale)
    """
    # Strip markdown bold markers for easier parsing
    text = response.replace("*", "")

    # Strategy 1: Explicit numeric confidence
    numeric_patterns = [
        r'[Cc]onfidence[:\s]+(\d{1,3})\s*%',
        r'(\d{1,3})\s*%\s*(?:confident|confidence|certain|sure)',
        r'[Cc]onfidence[:\s]+(\d\.\d+)',
    ]
    for pattern in numeric_patterns:
        match = re.search(pattern, text)
        if match:
            value = float(match.group(1))
            if value > 1:
                value /= 100
            value = max(0.0, min(1.0, value))
            return ParseResult(
                success=True,
                value=value,
                method="regex",
                confidence=0.95,
                raw_match=match.group(0),
            )

    # Strategy 2: Explicit categorical confidence
    categorical_map = {
        "high": 0.85,
        "medium": 0.55,
        "moderate": 0.55,
        "low": 0.25,
        "very high": 0.95,
        "very low": 0.15,
    }
    cat_pattern = r'[Cc]onfidence[:\s]+(very\s+)?(high|medium|moderate|low)'
    match = re.search(cat_pattern, text, re.IGNORECASE)
    if match:
        prefix = (match.group(1) or "").strip()
        level = match.group(2).lower()
        key = f"{prefix} {level}".strip() if prefix else level
        value = categorical_map.get(key, categorical_map.get(level, 0.5))
        return ParseResult(
            success=True,
            value=value,
            method="regex",
            confidence=0.9,
            raw_match=match.group(0),
        )

    # Strategy 3: Infer from hedging language (lower confidence in extraction)
    return ParseResult(success=False, value=None, method="failed")


# =============================================================================
# YES/NO EXTRACTION (general utility)
# =============================================================================

def extract_yes_no(response: str) -> ParseResult:
    """
    Extract a yes/no answer from a response.

    Returns:
        ParseResult with value as bool (True=yes, False=no)
    """
    text = response.lower().strip()

    # Check first line or first 100 chars for explicit yes/no
    first_chunk = text[:min(200, len(text))]

    yes_patterns = [
        r'\byes\b', r'\bcorrect\b', r'\btrue\b', r'\bindeed\b',
        r'\bconfirm\b', r'\baffirmative\b',
    ]
    no_patterns = [
        r'\bno\b', r'\bincorrect\b', r'\bfalse\b', r'\bnot\s+(?:correct|true)\b',
        r'\bnegative\b', r'\bdenied?\b',
    ]

    yes_in_first = any(re.search(p, first_chunk) for p in yes_patterns)
    no_in_first = any(re.search(p, first_chunk) for p in no_patterns)

    if yes_in_first and not no_in_first:
        return ParseResult(success=True, value=True, method="regex", confidence=0.8)
    if no_in_first and not yes_in_first:
        return ParseResult(success=True, value=False, method="regex", confidence=0.8)

    return ParseResult(success=False, value=None, method="failed")


# =============================================================================
# INTERACTION TYPE EXTRACTION (CausalBio epistasis)
# =============================================================================

INTERACTION_TYPES = [
    "synthetic lethal", "synthetic lethality",
    "suppressive", "suppression",
    "enhancing", "enhancement",
    "synergistic", "synergy",
    "epistatic",
    "no interaction", "independent",
    "buffering",
]

INTERACTION_NORMALIZATION = {
    "synthetic lethal": "synthetic_lethal",
    "synthetic lethality": "synthetic_lethal",
    "suppressive": "suppressive",
    "suppression": "suppressive",
    "enhancing": "enhancing",
    "enhancement": "enhancing",
    "synergistic": "synergistic",
    "synergy": "synergistic",
    "epistatic": "epistatic",
    "no interaction": "no_interaction",
    "independent": "no_interaction",
    "buffering": "buffering",
}


def extract_interaction_type(response: str) -> ParseResult:
    """
    Extract genetic interaction type from an epistasis response.

    Returns:
        ParseResult with value as normalized interaction type string
    """
    # Strip markdown to avoid ** interference with regex
    text = re.sub(r'\*\*', '', response.lower())

    # Look for explicit type declarations
    type_patterns = [
        r'(?:type\s+of\s+)?(?:genetic\s+)?interaction[:\s]+(?:is\s+)?(\w[\w\s/]+)',
        r'(?:this\s+is\s+(?:a|an)\s+)(\w[\w\s/]+?)(?:\s+interaction)',
        r'(?:classified\s+as|considered)\s+(\w[\w\s/]+)',
        # Also match "1. Type: Enhancing" or "Answers: 1. Type: synergistic"
        r'type[:\s]+(\w[\w\s/]+)',
    ]

    # Sort INTERACTION_TYPES longest-first so "synthetic lethal" doesn't
    # shadow "synergistic" or "enhancing"
    sorted_types = sorted(INTERACTION_TYPES, key=len, reverse=True)

    for pattern in type_patterns:
        match = re.search(pattern, text)
        if match:
            found = match.group(1).strip()
            for itype in sorted_types:
                if itype in found:
                    return ParseResult(
                        success=True,
                        value=INTERACTION_NORMALIZATION[itype],
                        method="regex",
                        confidence=0.9,
                        raw_match=match.group(0),
                    )

    # Fallback: count all interaction type mentions, pick most frequent
    # (avoids the "first match wins" problem where incidental mentions
    # of "synthetic lethal" in therapeutic discussion overshadow the
    # actual prediction of "synergistic")
    type_counts = {}
    for itype in sorted_types:
        count = len(re.findall(re.escape(itype), text))
        if count > 0:
            norm = INTERACTION_NORMALIZATION[itype]
            type_counts[norm] = type_counts.get(norm, 0) + count

    if type_counts:
        best = max(type_counts, key=type_counts.get)
        return ParseResult(
            success=True,
            value=best,
            method="regex",
            confidence=0.6,
            raw_match=best,
        )

    return ParseResult(success=False, value=None, method="failed")


# =============================================================================
# LLM FALLBACK EXTRACTION
# =============================================================================

class LLMExtractor:
    """
    Fallback extractor using a small LLM (Haiku) for cases where
    regex-based extraction fails.

    Usage:
        extractor = LLMExtractor()
        result = extractor.extract_ordering(response, num_steps=12)
    """

    def __init__(self, model: str = "claude-haiku-4-5-20251001"):
        self.model = model
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from anthropic import Anthropic
            self._client = Anthropic()
        return self._client

    def _call(self, system: str, prompt: str) -> str:
        """Make a single LLM call."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def extract_ordering(self, response: str, num_steps: int) -> ParseResult:
        """Use LLM to extract step ordering."""
        system = "Extract information from text. Respond with ONLY a JSON array of integers."
        prompt = (
            f"The following response contains a predicted ordering of {num_steps} steps.\n"
            f"Extract the step numbers in the predicted order as a JSON array.\n"
            f"Example: [3, 1, 5, 2, 4]\n\n"
            f"Response:\n{response[:2000]}"
        )
        try:
            raw = self._call(system, prompt)
            # Parse JSON array
            numbers = json.loads(raw.strip())
            if isinstance(numbers, list) and _is_valid_ordering(numbers, num_steps):
                return ParseResult(
                    success=True,
                    value=numbers,
                    method="llm",
                    confidence=0.7,
                    raw_match=raw.strip(),
                )
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"LLM extraction failed: {e}")

        return ParseResult(success=False, value=None, method="failed")

    def extract_flaws(self, response: str) -> ParseResult:
        """Use LLM to extract structured flaw list."""
        system = "Extract information from text. Respond with ONLY valid JSON."
        prompt = (
            "Extract all experimental design flaws from this review response.\n"
            "Return a JSON array of objects with keys: description, category, severity, fix\n"
            "Valid categories: controls, statistics, confounders, technical, interpretation\n"
            "Valid severities: critical, major, minor\n\n"
            f"Response:\n{response[:3000]}"
        )
        try:
            raw = self._call(system, prompt)
            # Clean markdown fences if present
            clean = raw.strip()
            if clean.startswith("```"):
                clean = re.sub(r'^```\w*\n?', '', clean)
                clean = re.sub(r'```$', '', clean).strip()
            items = json.loads(clean)
            if isinstance(items, list):
                flaws = [
                    FlawItem(
                        description=item.get("description", ""),
                        category=item.get("category") if item.get("category") in VALID_CATEGORIES else None,
                        severity=item.get("severity") if item.get("severity") in VALID_SEVERITIES else None,
                        fix=item.get("fix"),
                    )
                    for item in items
                    if item.get("description")
                ]
                return ParseResult(
                    success=bool(flaws),
                    value=flaws,
                    method="llm",
                    confidence=0.7,
                    raw_match=f"{len(flaws)} flaws",
                )
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"LLM flaw extraction failed: {e}")

        return ParseResult(success=False, value=None, method="failed")


# =============================================================================
# UNIFIED PARSE INTERFACE
# =============================================================================

def parse_response(
    response: str,
    task_type: str,
    ground_truth: Optional[dict] = None,
    use_llm_fallback: bool = False,
    llm_extractor: Optional[LLMExtractor] = None,
) -> dict:
    """
    Unified parsing interface. Given a response and task type, extract all
    relevant structured information.

    Args:
        response: The LLM's free-text response
        task_type: One of the BioEval task types
        ground_truth: Optional ground truth for guided extraction
        use_llm_fallback: Whether to use LLM for failed regex extractions
        llm_extractor: Pre-initialized LLMExtractor instance

    Returns:
        dict of ParseResult objects keyed by extraction type
    """
    results = {}

    if task_type == "step_ordering":
        gt = ground_truth or {}
        num_steps = len(gt.get("correct_steps", gt.get("shuffled_steps", [])))
        if num_steps == 0:
            num_steps = 12  # default fallback
        result = extract_step_ordering(response, num_steps)
        if not result.success and use_llm_fallback:
            extractor = llm_extractor or LLMExtractor()
            result = extractor.extract_ordering(response, num_steps)
        results["ordering"] = result

    elif task_type == "calculation":
        gt = ground_truth or {}
        answer = gt.get("answer", {})
        for key, expected in answer.items():
            # Extract expected numeric value
            nums = re.findall(r'[\d.]+', str(expected))
            exp_val = float(nums[0]) if nums else None
            result = extract_numerical_value(response, expected_value=exp_val)
            results[key] = result

    elif task_type == "knockout_prediction":
        results["effect"] = extract_categorical_label(
            response, ["essential", "non-essential", "context-dependent"]
        )
        results["confidence"] = extract_confidence_structured(response)

    elif task_type == "pathway_reasoning":
        gt = ground_truth or {}
        gt_inner = gt.get("ground_truth", gt)
        pathways = gt_inner.get("affected_pathways", [])
        for pathway in pathways:
            name = pathway.get("pathway", "unknown")
            results[f"direction_{name}"] = extract_direction(response, target=name)

    elif task_type == "epistasis":
        results["interaction_type"] = extract_interaction_type(response)
        results["confidence"] = extract_confidence_structured(response)

    elif task_type == "drug_response":
        results["gene_directions"] = extract_gene_directions(response)

    elif task_type == "flaw_detection":
        result = extract_flaw_list(response)
        if not result.success and use_llm_fallback:
            extractor = llm_extractor or LLMExtractor()
            result = extractor.extract_flaws(response)
        results["flaws"] = result

    elif task_type == "troubleshooting":
        results["confidence"] = extract_confidence_structured(response)

    elif task_type == "missing_step":
        results["confidence"] = extract_confidence_structured(response)

    else:
        logger.warning(f"No specific parser for task_type={task_type}")

    return results
