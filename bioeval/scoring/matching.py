"""
Robust text matching utilities for BioEval scoring.

Replaces fragile `term in response_lower` with:
- Simple suffix-based stemming
- Word-boundary awareness for short terms
- Biology-specific synonym expansion
- Multi-word phrase matching with stemmed fallback

All functions are deterministic and dependency-free.
"""

import re
from contextlib import contextmanager
from dataclasses import dataclass
from functools import lru_cache

# =============================================================================
# MATCH CONFIGURATION (for ablation studies)
# =============================================================================


@dataclass
class MatchConfig:
    """Configuration flags for phrase_match behavior.

    Used in ablation studies to measure the contribution of each feature.
    """

    use_stemming: bool = True  # Phase 2: stemmed token matching
    use_synonyms: bool = True  # Phase 3: synonym expansion
    use_word_boundary: bool = True  # Word-boundary guard for short terms


# Module-level config (default: all features on)
_active_config = MatchConfig()


def get_match_config() -> MatchConfig:
    """Return the current active matching configuration."""
    return _active_config


@contextmanager
def match_config(config: MatchConfig):
    """Context manager to temporarily override matching configuration.

    Usage:
        with match_config(MatchConfig(use_synonyms=False)):
            score = phrase_match("reduce", text)
    """
    global _active_config
    old = _active_config
    _active_config = config
    try:
        yield config
    finally:
        _active_config = old


# =============================================================================
# SIMPLE STEMMER (no NLTK dependency)
# =============================================================================

# Order matters — try longer suffixes first
_SUFFIXES = [
    "isation",
    "ization",
    "ational",
    "fulness",
    "iously",
    "lessly",
    "ments",
    "ation",
    "ement",
    "iness",
    "ously",
    "ively",
    "ional",
    "ness",
    "ment",
    "tion",
    "sion",
    "ible",
    "able",
    "ious",
    "eous",
    "ical",
    "ally",
    "ated",
    "ting",
    "ling",
    "ence",
    "ance",
    "ment",
    "ity",
    "ous",
    "ive",
    "ing",
    "ful",
    "ism",
    "ist",
    "ary",
    "ory",
    "ant",
    "ent",
    "ial",
    "ure",
    "ise",
    "ize",
    "ify",
    "ate",
    "ble",
    "ive",
    "ly",
    "ed",
    "er",
    "al",
    "es",
]

# Minimum stem length after stripping
_MIN_STEM = 3


_VOWELS = set("aeiou")


@lru_cache(maxsize=4096)
def stem(word: str) -> str:
    """Strip common English suffixes to produce a rough stem.

    >>> stem("reduction")
    'reduc'
    >>> stem("essential")
    'essent'
    >>> stem("inhibited")
    'inhibit'
    >>> stem("reduce")
    'reduc'
    >>> stem("decrease")
    'decreas'
    """
    w = word.lower().strip()
    if len(w) <= _MIN_STEM:
        return w
    for sfx in _SUFFIXES:
        if w.endswith(sfx) and len(w) - len(sfx) >= _MIN_STEM:
            return w[: -len(sfx)]
    # Strip trailing 'e' after a consonant (reduc-e, decreas-e, promot-e)
    if w.endswith("e") and len(w) - 1 >= _MIN_STEM and w[-2] not in _VOWELS:
        return w[:-1]
    return w


# =============================================================================
# BIOLOGY SYNONYM GROUPS
# =============================================================================

# Each tuple is a synonym group: if any member is queried, all are checked.
_SYNONYM_GROUPS: list[tuple[str, ...]] = [
    # Directionality
    ("decrease", "reduce", "inhibit", "suppress", "downregulate", "attenuate", "diminish", "lower", "block"),
    ("increase", "enhance", "activate", "upregulate", "promote", "elevate", "stimulate", "induce", "amplify"),
    # Essentiality
    ("essential", "required", "necessary", "critical", "indispensable", "vital"),
    ("dispensable", "non-essential", "nonessential", "unnecessary", "redundant", "expendable"),
    # Experimental
    ("replicate", "repeat", "reproduce", "independent experiment"),
    ("control", "vehicle", "untreated", "baseline", "reference"),
    # Effects
    ("lethal", "cell death", "kill", "apoptosis", "cytotoxic"),
    ("resistance", "refractory", "insensitive", "non-responsive", "unresponsive"),
    ("sensitive", "responsive", "susceptible", "vulnerable"),
    # Uncertainty
    ("uncertain", "unsure", "unclear", "ambiguous", "indeterminate"),
    ("confident", "certain", "definite", "conclusive", "unambiguous"),
    # Statistical
    ("significant", "statistically significant", "p-value", "p value"),
    ("underpowered", "insufficient sample", "low power", "small sample"),
    ("pseudoreplication", "pseudo-replication", "technical replicate"),
    # Design
    ("confound", "confounder", "confounding", "confounded"),
    ("batch effect", "batch confound", "batch variation"),
    ("overstatement", "overclaim", "overinterpret", "exaggerate"),
    # Mechanisms
    ("gain-of-function", "gain of function", "neomorphic", "gof"),
    ("loss-of-function", "loss of function", "lof", "null"),
    ("mutually exclusive", "mutual exclusivity", "co-exclusive"),
    # Correction language
    ("incorrect", "wrong", "false", "erroneous", "mistaken", "inaccurate"),
    ("actually", "in fact", "contrary", "however", "rather"),
]

# Build a lookup: key → set of synonym stems
# Keys include BOTH the raw lowercase word AND its stem, so that
# get_synonyms() works whether called with an original word or a stem.
_SYNONYM_MAP: dict[str, set[str]] = {}

for _group in _SYNONYM_GROUPS:
    # Collect all stems in this group (skip very short tokens like "in", "of", "a"
    # which are too generic and cause false positives when used as synonym lookups)
    _stems_in_group: set[str] = set()
    _raw_words: set[str] = set()
    for _phrase in _group:
        for _token in _phrase.lower().split():
            if len(_token) > 2:
                _stems_in_group.add(stem(_token))
                _raw_words.add(_token)

    # Map each stem AND each raw word to the whole group's stems
    for _key in _stems_in_group | _raw_words:
        if _key in _SYNONYM_MAP:
            _SYNONYM_MAP[_key] = _SYNONYM_MAP[_key] | _stems_in_group
        else:
            _SYNONYM_MAP[_key] = set(_stems_in_group)


def get_synonyms(word: str) -> set[str]:
    """Return stemmed synonyms for a word (including itself).

    Looks up both the raw word and its stem to avoid double-stemming issues.
    """
    w = word.lower().strip()
    s = stem(w)
    # Try raw word first, then stem
    result = _SYNONYM_MAP.get(w) or _SYNONYM_MAP.get(s)
    if result:
        return result
    return {s}


# =============================================================================
# TOKENIZER
# =============================================================================

_TOKEN_RE = re.compile(r"[a-z0-9](?:[a-z0-9'-]*[a-z0-9])?", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    """Split text into lowercase word tokens."""
    return [m.group().lower() for m in _TOKEN_RE.finditer(text)]


@lru_cache(maxsize=512)
def _stem_tokens(text_key: str) -> list[str]:
    """Stem all tokens in text (cached for repeated calls on same response)."""
    return [stem(t) for t in tokenize(text_key)]


# =============================================================================
# CORE MATCHING FUNCTIONS
# =============================================================================


def phrase_match(query: str, text: str) -> bool:
    """Check if a query phrase matches in text.

    Strategy (tried in order, subject to MatchConfig):
    1. Exact substring match (always on)
    2. Stemmed token overlap — all stemmed query tokens appear in stemmed text
    3. Synonym-expanded match — query tokens or their synonyms in text

    For single-word queries with len <= 4, uses word-boundary matching to
    prevent "ERK" matching "CLERK".
    """
    cfg = _active_config
    text_lower = text.lower()
    query_lower = query.lower().strip()

    if not query_lower:
        return False

    # ── Phase 1: Exact substring (always on) ─────────────────────────
    if query_lower in text_lower:
        # Word boundary guard for very short terms (<=4 chars)
        if cfg.use_word_boundary and len(query_lower) <= 4 and " " not in query_lower:
            pattern = r"\b" + re.escape(query_lower) + r"\b"
            if re.search(pattern, text_lower):
                return True
            # Fall through to stemmed matching
        else:
            return True

    # ── Phase 2: Stemmed token matching ──────────────────────────────
    if not cfg.use_stemming:
        return False

    query_tokens = tokenize(query_lower)
    if not query_tokens:
        return False

    query_stems = [stem(t) for t in query_tokens]
    # Cache-friendly: use full text as key
    text_stems_set = set(_stem_tokens(text_lower[:5000]))  # cap for cache key

    if all(qs in text_stems_set for qs in query_stems):
        return True

    # ── Phase 3: Synonym expansion ───────────────────────────────────
    if not cfg.use_synonyms:
        return False

    # Use original tokens (not pre-stemmed) to avoid double-stemming in get_synonyms
    for qt in query_tokens:
        synonyms = get_synonyms(qt)  # returns stems of synonym group
        if not synonyms.intersection(text_stems_set):
            return False
    return True


def count_matches(terms: list[str], text: str) -> int:
    """Count how many terms match in text using phrase_match."""
    return sum(1 for t in terms if phrase_match(t, text))


def any_match(indicators: list[str], text: str) -> bool:
    """Return True if any indicator matches in text."""
    return any(phrase_match(ind, text) for ind in indicators)


def matched_list(indicators: list[str], text: str) -> list[str]:
    """Return list of indicators that matched."""
    return [ind for ind in indicators if phrase_match(ind, text)]


# =============================================================================
# SPECIALIZED HELPERS
# =============================================================================


def term_overlap_score(terms: list[str], text: str, min_matches: int = 2) -> float:
    """Fraction of terms that match, with a minimum threshold.

    Returns 0.0 if fewer than min_matches found.
    """
    if not terms:
        return 0.0
    hits = count_matches(terms, text)
    if hits < min_matches:
        return 0.0
    return hits / len(terms)


def extract_key_terms(
    text: str,
    min_length: int = 5,
    max_terms: int = 5,
    stop_words: set[str] | None = None,
) -> list[str]:
    """Extract key terms from a text (for building match queries).

    Filters by length and stop words, returns up to max_terms.
    """
    if stop_words is None:
        stop_words = {
            "about",
            "after",
            "their",
            "there",
            "these",
            "those",
            "which",
            "would",
            "could",
            "should",
            "being",
            "other",
            "where",
            "while",
            "using",
            "first",
            "based",
            "known",
            "shown",
            "given",
            "since",
            "might",
            "could",
        }

    tokens = tokenize(text)
    seen: set[str] = set()
    result: list[str] = []
    for t in tokens:
        if len(t) >= min_length and t not in stop_words and t not in seen:
            seen.add(t)
            result.append(t)
            if len(result) >= max_terms:
                break
    return result
