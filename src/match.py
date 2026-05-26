# import to let us work with JSON data
import json
"""
  sentence_transformer: python package for working with sentence embeddings
    - SentenceTransformer: main class for loading and using pretrained models
      that convert text into dense vector embeddings
"""
from sentence_transformers import SentenceTransformer, util

"""
  entities: file called entitites.py
    - extract_entities(text, nlp, matcher, skills_list): Given raw text, 
      a loaded spaCy pipeline, a prebuilt matcher, and a list of skill terms
      returns a dictionary with four sections
    - build_skills_matcher(nlp, skills_list): helper that builds a case-insensitive 
      spacy PhraseMatcher from the skills list
"""
from entities import extract_entities, build_skills_matcher
# function to extract job description
from job_extract import extract_job_description
# function to extract resume information from the pdf
from extract import extract_pdf
# skills list
from utils import SKILLS
# python NLP library that provides fast, pretrained pipelines for tokenization,
# tagging, NER, etc.
import spacy


"""
  loads a pretrained sentence embedding model, so that we can encode text into vectors
    - MiniLM: small, distilled transformer
    - L6: transformer layers
    - all: trained on a broad mix of datasets
    - v2: secodnd version of the model
"""
model = SentenceTransformer("all-MiniLM-L6-v2")

"""
  Loads a small english language pipeline 
    - returns a doc object with tokens, part-of-speech tags, named entities, etc.
"""
nlp = spacy.load("en_core_web_sm")

"""
  calls helper to construct SpaCy PhraseMatcher preloaded with skills vocab
    - All those skill docs are added to the matcher under the label "SKILLS".
"""
skills_matcher = build_skills_matcher(nlp, SKILLS)

"""
  Function: load_resume_jd
  description:
    - extract the text from the pdf resume
    - read the text from the job description
"""
def load_resume_jd(resume_path: str, jd_path: str) -> tuple[str, str]:
  resume_text = extract_pdf(resume_path)

  with open(jd_path, "r", encoding="utf-8") as f:
    jd_text = f.read()

  # return the texts
  return resume_text, jd_text

"""
  Function Name: process_resume
  Description:
    - contact
    - skills
    - education
    - experience
"""
def process_resume(resume_text):
  resume_data = extract_entities(resume_text, nlp, skills_matcher, SKILLS)
  return resume_data

"""
  Function Name: process_jd
  Description:
    - title
    - skills
    - years_experience
    - education
"""
def process_jd(jd_text):
  jd_data = extract_job_description(jd_text, nlp, skills_matcher)
  return jd_data


# Resume --> Text
def to_resume_text(resume):
    return f"""
    Skills: {', '.join(resume['skills'])}
    Experience: {resume['experience']}
    Education: {resume['education']}
    Contact: {resume['contact']}
    """

# JD --> Text
def to_jd_text(jd):
    return f"""
    Title: {jd['title']}
    Skills: {', '.join(jd['skills'])}
    Experience: {jd['years_experience']}
    Education: {jd['education']}
    """


"""
  Function Name: semantic_score
  Description:
    - A function that takes a resume and a job description and returns
      a number representing how semantically similiar they are
"""
def semantic_score(resume_text, jd_text):
  # pass the resume text through a SentenceTransformer model to turn it
  # to turn it into an embedding
  resume_emb = model.encode(resume_text, convert_to_tensor=True)
  jd_emb = model.encode(jd_text, convert_to_tensor=True)
  # computes cosine similarity between the two vectors [-1, 1]
  return util.cos_sim(resume_emb, jd_emb).item()


"""
  Function Name: skill_score
  Description: Find the relevant skills the resume has relative to the job description
"""
def skill_score(resume_skills, jd_skills):
  if not jd_skills:
    return 0
   
  resume_set = set([s.lower() for s in resume_skills])
  jd_set = set([s.lower() for s in jd_skills])

  # Finds the skills that overlap between the resume and job description
  overlap = resume_set.intersection(jd_set)

  # find percent of job description skills the resume has
  return len(overlap) / len(jd_set)


"""
  Function Name: final_score
  Description: combines the two scores into a single overall match score using a weighted average
"""
def final_score(semantic, skill):
  return (0.7 * semantic) + (0.3 * skill)


def match(resume_path, jd_path):
  resume_text, jd_text = load_resume_jd(resume_path, jd_path)

  resume_data, jd_data = process_resume(resume_text), process_jd(jd_text)

  resume_str, jd_str = to_resume_text(resume_data), to_jd_text(jd_data)

  semantic, skills = semantic_score(resume_str, jd_str), skill_score(resume_data["skills"], jd_data["skills"])

  score = final_score(semantic, skills)

  return {
    "final_score": round(score, 4),
    "semantic_score": semantic,
    "skill_score": skills,
    "resume_data": resume_data,
    "jd_data": jd_data
  }