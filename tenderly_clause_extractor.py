import re
from tenderly_settings import MANDATORY_WORDS, CRITERIA_KEYWORDS

AMOUNT_PATTERN = re.compile(
    r"(?:rs\.?|inr|\u20b9)\s*([0-9]+(?:\.[0-9]+)?)\s*(crore|cr|lakh|lakhs|million|billion)?",
    re.IGNORECASE
)

YEAR_PATTERN = re.compile(
    r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:financial\s+)?years?",
    re.IGNORECASE
)

WORD_NUMBERS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10
}


def normalize_amount(value, unit):
    value = float(value)
    if not unit:
        return value

    unit = unit.lower()
    if unit in ["crore", "cr"]:
        return value * 10_000_000
    if unit in ["lakh", "lakhs"]:
        return value * 100_000
    if unit == "million":
        return value * 1_000_000
    if unit == "billion":
        return value * 1_000_000_000
    return value


def extract_amount(text):
    match = AMOUNT_PATTERN.search(text)
    return normalize_amount(match.group(1), match.group(2)) if match else None


def extract_years(text):
    match = YEAR_PATTERN.search(text)

    if not match:
        return None

    value = match.group(1).lower()

    if value in WORD_NUMBERS:
        return WORD_NUMBERS[value]

    return int(value)


def classify_clause(text):
    lowered = text.lower()
    for criterion, keywords in CRITERIA_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return criterion
    return "OTHER"


def is_mandatory(text):
    lowered = text.lower()
    return any(word in lowered for word in MANDATORY_WORDS)


def split_into_clauses(tender_text):
    if not tender_text or len(tender_text.strip()) < 20:
        raise ValueError("Tender text is empty or too short.")

    clauses = []
    current = ""

    for line in tender_text.splitlines():
        line = line.strip()
        if not line:
            continue

        new_clause = bool(
            re.match(r"^\d+[.)]\s+", line)
            or re.match(r"^[a-z][.)]\s+", line, re.IGNORECASE)
            or line.startswith("\u2022")
            or line.startswith("-")
        )

        if new_clause and current:
            clauses.append(current.strip())
            current = line
        else:
            current += " " + line

        if len(current.split()) > 80:
            clauses.append(current.strip())
            current = ""

    if current:
        clauses.append(current.strip())

    return clauses


def extract_clauses(tender_text):
    structured = []

    for text in split_into_clauses(tender_text):
        clause_type = classify_clause(text)
        if clause_type == "OTHER":
            continue

        structured.append({
            "text": text,
            "type": clause_type,
            "mandatory": is_mandatory(text),
            "amount": extract_amount(text),
            "years": extract_years(text)
        })

    if not structured:
        raise ValueError("No eligibility clauses could be detected.")

    return structured
