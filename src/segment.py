SECTION_HEADERS = [
    # Contact / Top of resume
    "contact",
    "contact information",
    "contact info",
    "summary",
    "professional summary",
    "career summary",
    "profile",
    "about me",
    "objective",
    "career objective",

    # Work history
    "experience",
    "employment experience",
    "work experience",
    "working experience",
    "professional experience",
    "employment",
    "employment history",
    "work history",
    "career history",
    "relevant experience",

    # Education
    "education",
    "academic background",
    "educational background",
    "academic qualifications",
    "qualifications",

    # Skills
    "skills",
    "technical skills",
    "core competencies",
    "areas of expertise",
    "technical proficiencies",
    "technologies",
    "tools and technologies",
    "programming languages",

    # Projects
    "projects",
    "personal projects",
    "side projects",
    "selected projects",
    "notable projects",
    "portfolio",

    # Credentials & recognition
    "certifications",
    "certificates",
    "licenses",
    "awards",
    "honors",
    "honors and awards",
    "achievements",
    "accomplishments",

    # Academic / Research
    "publications",
    "research",
    "research experience",
    "conferences",
    "presentations",
    "teaching",
    "teaching experience",
    "coursework",
    "relevant coursework",
    "thesis",

    # Extras
    "languages",
    "interests",
    "hobbies",
    "volunteer",
    "volunteer experience",
    "volunteer work",
    "community service",
    "leadership",
    "leadership experience",
    "activities",
    "extracurricular activities",
    "affiliations",
    "memberships",
    "professional memberships",
    "references",
]

def segment(resume_text : str=None) -> dict:

  segment_dictionary, recent_header = {}, "header"
  segment_dictionary["header"] = []

  for line in resume_text.splitlines():
    cleaned_line = line.lower().strip()
    if cleaned_line in SECTION_HEADERS:
      recent_header = cleaned_line
      segment_dictionary[recent_header] = [] 
      continue
    
    if not recent_header == "":
      segment_dictionary[recent_header].append(line)

  return segment_dictionary



