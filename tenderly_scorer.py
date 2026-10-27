import pandas as pd
from tenderly_matcher import match_clause_with_evidence
from tenderly_settings import DEFAULT_WEIGHTS, STATUS_THRESHOLDS


def get_status(score):
    if score >= STATUS_THRESHOLDS["MET"]:
        return "Met"
    if score >= STATUS_THRESHOLDS["PARTIAL"]:
        return "Partial"
    return "Missing"


def calculate_results(clauses, evidence_documents, weights=None):
    weights = weights or DEFAULT_WEIGHTS
    results = []
    mandatory_missing = False
    total_weight = 0
    weighted_score = 0

    for clause in clauses:
        matched_document, score = match_clause_with_evidence(clause, evidence_documents)
        status = get_status(score)
        weight = weights.get(clause["type"], 10)

        total_weight += weight
        weighted_score += weight * score

        if clause["mandatory"] and status == "Missing":
            mandatory_missing = True

        results.append({
            "Type": clause["type"],
            "Clause": clause["text"][:250],
            "Mandatory": "Yes" if clause["mandatory"] else "No",
            "Matched Document": matched_document["name"] if matched_document else "None",
            "Score": round(score, 2),
            "Status": status,
            "Evidence Snippet": matched_document["text"][:250] if matched_document else "No matching evidence found"
        })

    eligibility_score = weighted_score / total_weight if total_weight else 0
    verdict = "Eligible"

    if mandatory_missing:
        verdict = "Not Eligible"
    elif eligibility_score < STATUS_THRESHOLDS["PARTIAL"]:
        verdict = "Not Eligible"
    elif eligibility_score < STATUS_THRESHOLDS["MET"]:
        verdict = "Partially Eligible"

    return pd.DataFrame(results), eligibility_score, verdict
