# Common headers
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

"""
  Function Name: Segment
  Function Params: resume_text (str), text associated with a resume
  Function Return: dictionary of headers as the key, and the lines associated with the header
"""
def segment(resume_text : str) -> dict:

  # dictionary to old the return, and the most recent header that has been seen
  segment_dictionary, recent_header = {}, "header"
  # bucket at the beginning to handle all information above the first header
  segment_dictionary["header"] = []

  # loop through each line in the resume text
  for line in resume_text.splitlines():
    # clean the line by lowering text and stripping white space
    cleaned_line = line.lower().strip()
    # if the cleaned line is a common header, then we need to add a new key, val pair
    if cleaned_line in SECTION_HEADERS:
      # update the most recent seen header
      recent_header = cleaned_line
      # update the segment dictionary with the following: (new header : [])
      segment_dictionary[recent_header] = [] 
      # loop to the next line
      continue
    
    # if continue is not run, then we have a value associated with the most recent header
    # append that value
    segment_dictionary[recent_header].append(line)

  # return the created dictionary
  return segment_dictionary



