"""
Search terms + filtering/classification logic.
"""
import re

# Terms used to QUERY each company's search API / search box
SEARCH_TERMS = [
    "intern",
    "internship",
    "graduate",
    "entry level",
    "fresher",
    "early career",
    "new grad",
]

# A title must contain at least one of these to count as "entry-level / student"
ENTRY_SIGNALS = [
    "intern", "internship", "co-op", "apprentice", "apprenticeship",
    "graduate", "new grad", "entry level", "entry-level", "fresher",
    "campus", "early career", "university", "trainee", "associate engineer",
    "junior", "ge program", "rotational",
]

# A title containing any of these is treated as NOT entry-level, even if it
# also matches an entry signal (filters out "Senior Intern Program Manager" etc.)
SENIORITY_BLOCKLIST = [
    "senior", "sr.", "sr ", "staff", "principal", "director", " vp ",
    "vice president", "head of", " lead ", "manager", "architect",
    "chief", "executive",
]

# A title must contain at least one of these to count as an IT / tech / student role
IT_SIGNALS = [
    "software", "developer", "engineer", "engineering", "data", "cloud",
    "devops", "sde", "programmer", " it ", "information technology",
    "cyber", "security", "network", "web", "full stack", "fullstack",
    "front end", "frontend", "back end", "backend", "machine learning",
    " ai ", "artificial intelligence", "qa ", "quality assurance", "test",
    "analyst", "database", "system", "technical", "tech ", "application",
    "computer science", "coding", "python", "java", "ux", "ui ",
    "product", "research scientist", "infrastructure",
]


def is_relevant(title: str) -> bool:
    """True if title looks like an entry-level / student IT role."""
    if not title:
        return False
    t = f" {title.lower()} "
    if not any(sig in t for sig in ENTRY_SIGNALS):
        return False
    if any(sig in t for sig in SENIORITY_BLOCKLIST):
        return False
    if not any(sig in t for sig in IT_SIGNALS):
        return False
    return True


def is_location_relevant(loc_str: str) -> bool:
    """Filter jobs by location to only include India/target cities."""
    if not loc_str or loc_str == "N/A":
        return True
    loc = loc_str.lower()
    valid_terms = ["india", "hyderabad", "bengaluru", "bangalore", "hyd", "blr", ", ind", ", in"]
    return any(term in loc for term in valid_terms)


def classify_type(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ("intern", "co-op", "apprentice")):
        return "Internship"
    if any(k in t for k in ("graduate", "new grad", "campus", "early career", "rotational")):
        return "Graduate / Fresher Program"
    if "trainee" in t:
        return "Trainee"
    return "Entry-level Job"


_STIPEND_PATTERNS = [
    r"(?:stipend|compensation|pay)[^.\n]{0,40}?(?:₹|rs\.?|inr)\s?[\d,]+(?:\s?-\s?(?:₹|rs\.?|inr)?\s?[\d,]+)?(?:\s?/?\s?(?:month|mo|year|annum|lpa))?",
    r"\$\s?[\d,]+(?:\.\d+)?\s?(?:/|per)\s?(?:hour|hr|month|year)",
    r"₹\s?[\d,]+(?:\s?-\s?₹?\s?[\d,]+)?(?:\s?/?\s?(?:month|mo|year|annum|lpa))?",
    r"(?:USD|\$)\s?[\d,]+\s?-\s?(?:USD|\$)?\s?[\d,]+",
]


def extract_stipend(text: str) -> str:
    """Best-effort regex scan of a job description for pay/stipend info."""
    if not text:
        return "Not specified"
    for pattern in _STIPEND_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(0).strip()
    return "Not specified"
