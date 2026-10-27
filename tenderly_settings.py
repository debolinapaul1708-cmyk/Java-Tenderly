import hashlib

APP_NAME = "Tenderly"
DB_NAME = "tenderly_database.db"

MANDATORY_WORDS = ["shall", "must", "required", "essential", "mandatory"]

CRITERIA_KEYWORDS = {
    "TURNOVER": ["turnover", "annual turnover", "financial years", "revenue", "turnover of"],
    "EXPERIENCE": ["experience", "years of experience", "similar work", "similar assignment"],
    "CERT": ["iso", "certification", "certificate", "gst", "registration", "license", "licence"],
    "PROJECT": ["past projects", "work order", "completed project", "project completion", "similar project"]
}

DEFAULT_WEIGHTS = {
    "TURNOVER": 30,
    "EXPERIENCE": 25,
    "CERT": 25,
    "PROJECT": 20
}

STATUS_THRESHOLDS = {"MET": 0.70, "PARTIAL": 0.40}
COSINE_WEIGHT = 0.6
RULE_WEIGHT = 0.4


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
