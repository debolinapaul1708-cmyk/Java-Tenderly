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
    denominator = math.sqrt(sum(v ** 2 for v in counter1.values())) * math.sqrt(
        sum(v ** 2 for v in counter2.values())
    )

    return numerator / denominator if denominator else 0.0


def keyword_rule_score(clause_text, evidence_text):
    clause = clause_text.lower()
    evidence = evidence_text.lower()
    score = 0.0

    if "iso" in clause:
        match = re.search(r"iso\s*(\d{4,5})", clause)
        if match and match.group(1) in evidence:
            score += 0.6

    if "gst" in clause and "gst" in evidence:
        score += 0.6

    if "turnover" in clause:
        clause_amount = extract_amount(clause_text)
        evidence_amount = extract_amount(evidence_text)
        if clause_amount and evidence_amount and evidence_amount >= clause_amount:
            score += 0.8

    if "experience" in clause:
        clause_years = extract_years(clause_text)
        evidence_years = extract_years(evidence_text)
        if clause_years and evidence_years and evidence_years >= clause_years:
            score += 0.8

    return min(score, 1.0)


def match_clause_with_evidence(clause, evidence_documents):
    best_document = None
    best_score = 0.0

    for document in evidence_documents:
        cosine = cosine_similarity(clause["text"], document["text"])
        rule = keyword_rule_score(clause["text"], document["text"])
        hybrid = COSINE_WEIGHT * cosine + RULE_WEIGHT * rule

        if hybrid > best_score:
            best_score = hybrid
            best_document = document

    return best_document, best_score
