import re
from spacy.matcher import PhraseMatcher

# ----------------------------
# Regex patterns
# ----------------------------

# matches: "3 years", "5+ years"
YEAR_RE = re.compile(r"\b(\d{1,2})\+?\s+years?\b", re.IGNORECASE)

# optional heuristic for titles (not heavily relied on)
TITLE_RE = re.compile(r"(engineer|developer|analyst|manager)", re.IGNORECASE)

# education detection (more robust than plain substring matching)
BACHELOR_RE = re.compile(r"\bbachelor(?:'s)?\b", re.IGNORECASE)
MASTER_RE = re.compile(r"\bmaster(?:'s)?\b", re.IGNORECASE)


# ----------------------------
# Skills Matcher
# ----------------------------

def build_skills_matcher(nlp, skills_list):
    """
    Build a spaCy PhraseMatcher for skill extraction.
    Should be created ONCE and reused for performance.
    """
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in skills_list]
    matcher.add("SKILLS", patterns)
    return matcher


# ----------------------------
# JD Extraction
# ----------------------------

def extract_job_description(text: str, nlp, skills_matcher) -> dict:
    """
    Extract structured information from a job description:
    - title
    - skills
    - years_experience
    - education
    """

    result = {
        "title": None,
        "skills": [],
        "years_experience": None,
        "education": None
    }

    doc = nlp(text)

    # ----------------------------
    # Skill extraction
    # ----------------------------
    matches = skills_matcher(doc)
    found_skills = set()

    for _, start, end in matches:
        skill = doc[start:end].text.lower().strip()
        found_skills.add(skill)

    result["skills"] = sorted(list(found_skills))

    # ----------------------------
    # Years of experience
    # ----------------------------
    years = YEAR_RE.findall(text)
    if years:
        result["years_experience"] = max(int(y) for y in years)

    # ----------------------------
    # Title extraction (heuristic)
    # ----------------------------
    first_lines = [line.strip() for line in text.splitlines() if line.strip()]

    if first_lines:
        # pick first "reasonable" line
        for line in first_lines[:5]:
            if len(line) < 80 and not re.search(r"@", line):
                result["title"] = line
                break

        # fallback if nothing found
        if result["title"] is None:
            result["title"] = first_lines[0]

    # ----------------------------
    # Education extraction
    # ----------------------------
    lower_text = text.lower()

    if BACHELOR_RE.search(lower_text):
        result["education"] = "Bachelor's"
    elif MASTER_RE.search(lower_text):
        result["education"] = "Master's"

    return result