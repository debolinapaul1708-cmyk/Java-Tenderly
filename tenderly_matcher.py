import re
import math
from collections import Counter
from tenderly_clause_extractor import extract_amount, extract_years
from tenderly_settings import COSINE_WEIGHT, RULE_WEIGHT

STOPWORDS = {
    "the", "and", "of", "in", "to", "for", "a", "an", "is", "are",
    "shall", "must", "be", "with", "by", "on", "at", "or", "as",
    "that", "this", "from", "will", "should", "may"
}


def tokenize(text):
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [token for token in tokens if token not in STOPWORDS]


def cosine_similarity(text1, text2):
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)

    if not tokens1 or not tokens2:
        return 0.0

    counter1 = Counter(tokens1)
    counter2 = Counter(tokens2)
    common = set(counter1) & set(counter2)

    numerator = sum(counter1[token] * counter2[token] for token in common)

    denominator = math.sqrt(
        sum(value ** 2 for value in counter1.values())
    ) * math.sqrt(
        sum(value ** 2 for value in counter2.values())
    )

    if denominator == 0:
        return 0.0

    return numerator / denominator


def has_negative_statement(text, keyword):
    lowered = text.lower()

    negative_patterns = [
        "no " + keyword,
        "not " + keyword,
        keyword + " not available",
        keyword + " is not available",
        "not registered",
        "not obtained",
        "expired"
    ]

    return any(pattern in lowered for pattern in negative_patterns)


def keyword_rule_score(clause_text, all_evidence_text):
    clause = clause_text.lower()
    evidence = all_evidence_text.lower()
    score = 0.0

    # ISO certificate rule
    if "iso" in clause:
        iso_match = re.search(r"iso\s*(\d{4,5})", clause)

        if iso_match:
            required_iso = iso_match.group(1)

            if (
                required_iso in evidence
                and not has_negative_statement(evidence, "iso")
                and "expired" not in evidence
            ):
                score += 1.0

    # GST registration rule
    if "gst" in clause:
        if (
            "gst" in evidence
            and not has_negative_statement(evidence, "gst")
        ):
            if "gst registration" in evidence or "gstin" in evidence:
                score += 1.0

    # Turnover rule
    if "turnover" in clause:
        clause_amount = extract_amount(clause_text)

        evidence_amounts = [
            extract_amount(item)
            for item in re.findall(
                r"(?:rs\.?|inr|₹)\s*([0-9]+(?:\.[0-9]+)?)\s*(crore|cr|lakh|lakhs)?",
                all_evidence_text,
                re.IGNORECASE
            )
        ]

        evidence_amounts = [
            amount for amount in evidence_amounts if amount is not None
        ]

        if clause_amount and evidence_amounts:
            highest_amount = max(evidence_amounts)

            if highest_amount >= clause_amount:
                score += 1.0

    # Experience rule
    if "experience" in clause:
        clause_years = extract_years(clause_text)

        evidence_years = [
            extract_years(item)
            for item in re.findall(
                r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:financial\s+)?years?",
                all_evidence_text,
                re.IGNORECASE
            )
        ]

        evidence_years = [
            years for years in evidence_years if years is not None
        ]

        if clause_years and evidence_years:
            highest_years = max(evidence_years)

            if highest_years >= clause_years:
                score += 1.0

    # Past project / work order rule
    if "work order" in clause or "past project" in clause:
        work_orders = len(re.findall(r"work order\s*\d+", evidence))

        if work_orders >= 3:
            score += 1.0
        elif work_orders > 0:
            score += 0.2

    return min(score, 1.0)


def match_clause_with_evidence(clause, evidence_documents):
    all_evidence_text = "\n".join(
        document["text"]
        for document in evidence_documents
    )

    cosine_scores = [
        cosine_similarity(clause["text"], document["text"])
        for document in evidence_documents
    ]

    best_cosine = max(cosine_scores) if cosine_scores else 0.0
    rule = keyword_rule_score(clause["text"], all_evidence_text)

    hybrid = COSINE_WEIGHT * best_cosine + RULE_WEIGHT * rule

    final_score = max(hybrid, rule * 0.95)

    best_document = evidence_documents[
        cosine_scores.index(best_cosine)
    ] if evidence_documents else None

    return best_document, final_score
