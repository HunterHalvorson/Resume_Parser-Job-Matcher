import re
import spacy
from spacy.matcher import PhraseMatcher

# ─────────────────────────────────────────────
# Regex patterns
# ─────────────────────────────────────────────

"""
  Email regex
  Explanation: any grouo of word characters, periods, and dashes before the @
               same for after the @ until a '.' is reached, the a group of
               word characters for (ex. com)
"""
EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
"""
  Phone regex
  Explanation: 
    - (\+?\d{1,2}[\s-]?)? : Entire thing is wrapped in (...)? means it is optional
      \+ is an optional + sign, 
      - note: ? = zero or one; + means one or more
      - \d{1, 2} -- 1 or 2 digits, where \d = any digits; {1, 2} = between 1 and 2 times
      - [\s-], an optional seperator, could be a space or a hyphen
    - \(?, optional bracket
    - \d{3} — exactly three digits (area code)
    - \)? — optional closing parenthesis
"""
PHONE_RE = re.compile(r"(\+?\d{1,2}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
"""
  LinkedIn regex
"""
LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+")

"""
  Degree Regex
    - It's one giant alternation — a list of options separated by | (which means "or"). The whole list is wrapped in \b(...)\b to make sure matches land on word boundaries.
    - \b ( option1 | option2 | option3 | ... ) \b
"""

"""
  What does re.compile do?
    - takes a regex pattern and turns it into a reusable Patter Object you can use to 
      search text efficiently
"""
DEGREE_RE = re.compile(
    r"\b("
    r"B\.?S\.?|B\.?A\.?|B\.?Sc\.?|B\.?Eng\.?|"
    r"M\.?S\.?|M\.?A\.?|M\.?Sc\.?|M\.?Eng\.?|MBA|"
    r"Ph\.?D\.?|"
    r"Bachelor(?:'s)?(?:\s+of\s+\w+)?|"
    r"Master(?:'s)?(?:\s+of\s+\w+)?|"
    r"Doctorate|Doctor\s+of\s+\w+|"
    r"Associate(?:'s)?"
    r")\b",
    re.IGNORECASE,
)

YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")

INSTITUTION_RE = re.compile(
    r"\b[\w&.\-']+(?:\s+[\w&.\-']+){0,4}\s+"
    r"(?:University|College|Institute|School|Polytechnic|Academy)"
    r"(?:\s+of\s+[\w\s]+?)?\b",
    re.IGNORECASE,
)

# Date ranges like "Jan 2020 - Mar 2023" or "2020 - Present"
DATE_RANGE_RE = re.compile(
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{4})"
    r"\s*[-–—]+\s*"
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{4}|Present|Current)",
    re.IGNORECASE,
)


# ─────────────────────────────────────────────
# Extractors
# ─────────────────────────────────────────────
"""
  Function Name: extract_contact
  Description: Takes the text of a string and returns a dictionary with the following
               {"Email": ..., "Phone": ..., "LinkedIn": ...}
"""
def extract_contact(text: str) -> dict:
    # dictionary to return
    contact = {}

    ## search for email pattern, enter if m is truthy
    if m := EMAIL_RE.search(text):
        # m.group() returns the marched string
        contact["Email"] = m.group()
    ## search for phone pattern, enter if m is truthy
    if m := PHONE_RE.search(text):
        # m.group() returns the marched string
        contact["Phone"] = m.group().strip()
    ## search for LinkedIn pattern, enter if m is truthy
    if m := LINKEDIN_RE.search(text):
        # m.group() returns the marched string
        contact["LinkedIn"] = m.group()

    # return the dictionary
    return contact

"""
  Function Name: extract_skills
  Description: takes the resume text, nlp pipeline (nlp = spacy.load("en_core_web_sm")),
               matcher is a PhraseMatcher object, which finds a specific phrase in a doc
               (PhraseMatcher(nlp.vocab, attr="LOWER")) where nlp.vocab is a shared vocabulary 
               table a lookup system that maps every word spaCy has ever seen to a unique 
               integer ID (and back).
"""
def extract_skills(text: str, nlp, matcher, skills_list: list[str]) -> list[str]:
    # spacy processes text, raw string --> Doc object
    # nlp = spacy.load("en_core_web_sm"), The default English pipeline looks roughly like:
    # text → tokenizer → tagger → parser → NER → Doc
    doc = nlp(text)
    """
      matcher --> an object that contains matching rules/patterns
      doc --> spacy document
      matcher(doc) --> runs patten against text
      matches --> stores the results found in the text
    """
    matches = matcher(doc)
    # Key, Value pair (lower, Normal)
    canonical = {s.lower(): s for s in skills_list}
    """
      - (match_id, start, end) = internal match id, start token index, end token index
      doc[start:end] returns a span, so to get the actual words call .text
        - .test, .start, .end, .label_ (NER), 
      - canonical["python"] = "Python"
      - only adding a key do the dictionary will create a set (removes duplicates)
    """
    found = {canonical[doc[start:end].text.lower()] for _, start, end in matches}
    # This takes your set (found) and turns it into a sorted list before returning it.
    return sorted(found)


"""
  Function Name: extract_education
  Description: extract education credentials
"""
def extract_education(text: str, nlp) -> list[dict]:
    # holds the results
    results = []
    # searches the text where finditer searches through the entire text looking for the 
    # pattern and returning the matches one by one
    for match in DEGREE_RE.finditer(text):
        """
          match.start() gives the index where the match begins in the text
          max(0, ...) prevents negative indexing
          take up to 200 characters before the match
        """
        start = max(0, match.start() - 200)
        """
          match.end() gives the index where the match ends in the text
          max(len(), ...) prevents out of bounds error
          take up to 200 characters after the match
        """
        end = min(len(text), match.end() + 200)
        # window with the updated start and end, the reason for the larger window is to add context
        window = text[start:end]

        """
          - match.group(0).strip() returns the exact text matched, (group(0) matches whole)
          - two following placeholders
        """
        entry = {
            "degree": match.group(0).strip(),
            "institution": None,
            "year": None,
        }

        # Find institution: first try the keyword regex, then fall back to spaCy NER
        if inst := INSTITUTION_RE.search(window):
            entry["institution"] = inst.group(0).strip()
        # try using window
        else:
            for ent in nlp(window).ents:
                # if an oranization is listed
                if ent.label_ == "ORG":
                    # update the institution
                    entry["institution"] = ent.text
                    break

        # Find graduation year (pick the latest year in the window)
        years = YEAR_RE.findall(window)
        if years:
            # max as grad > start
            entry["year"] = max(years)
        # append the dictionary as a result
        results.append(entry)

    return results


def extract_experience(text: str, nlp) -> list[dict]:
    # Final list that will store all extracted experience entries
    results = []

    # Loop through every date range found in the text (e.g., "2019 - 2021")
    for match in DATE_RANGE_RE.finditer(text):

        # Start a context window 200 characters before the match (clamped to 0)
        before_start = max(0, match.start() - 200)

        # End a context window 200 characters after the match (clamped to text length)
        after_end = min(len(text), match.end() + 200)

        # Full context window around the date range (used for NLP + entity extraction)
        window = text[before_start:after_end]

        # Text only BEFORE the date range (used for finding job title heuristically)
        window_before = text[before_start:match.start()]

        # Create a structured entry for this experience block
        entry = {
            "start": match.group(1).strip(),  # start date of range (e.g., 2019)
            "end": match.group(2).strip(),    # end date of range (e.g., 2021)
            "company": None,                  # placeholder for company name
            "title": None,                    # placeholder for job title
        }

        # -------------------------
        # COMPANY EXTRACTION (NLP)
        # -------------------------

        # Run spaCy NLP on the window and loop through detected entities
        for ent in nlp(window).ents:

            # Look for organization-type entities (companies, universities, etc.)
            if ent.label_ == "ORG":

                # Save first ORG found as the company name
                entry["company"] = ent.text

                # Stop after first match (assumes closest ORG is correct)
                break

        # -------------------------
        # TITLE EXTRACTION (HEURISTIC)
        # -------------------------

        # Split text before the date range into lines, clean whitespace, remove empty lines
        lines = [line.strip() for line in window_before.split("\n") if line.strip()]

        # Check up to last 3 lines before the date range (closest context first)
        for line in reversed(lines[-3:]):

            # Skip lines that already contain the company name
            if entry["company"] and entry["company"] in line:
                continue

            # Skip lines that contain a year (likely not a job title)
            if YEAR_RE.search(line):
                continue

            # Only accept reasonably short lines (heuristic: likely a title, not a paragraph)
            if len(line) < 80:

                # Assign this line as the job title
                entry["title"] = line

                # Stop after first good match
                break

        # Add the extracted experience entry to results list
        results.append(entry)

    # Return all extracted experience blocks
    return results


def extract_entities(text: str, nlp, matcher, skills_list: list[str]) -> dict:
    return {
        "contact": extract_contact(text),
        "skills": extract_skills(text, nlp, matcher, skills_list),
        "education": extract_education(text, nlp),
        "experience": extract_experience(text, nlp),
    }


# ─────────────────────────────────────────────
# Setup helper
# ─────────────────────────────────────────────
def build_skills_matcher(nlp, skills_list: list[str]) -> PhraseMatcher:
    # Create a PhraseMatcher object using spaCy's vocabulary
    # "attr=LOWER" means matching is case-insensitive (Python == python)
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    # Convert each skill string into a spaCy Doc object (tokenized form)
    # Example: "Machine Learning" → Doc["Machine", "Learning"]
    patterns = [nlp.make_doc(skill) for skill in skills_list]

    # Add all patterns to the matcher under the label "SKILLS"
    matcher.add("SKILLS", patterns)

    # Return the configured matcher so it can be used on documents
    return matcher