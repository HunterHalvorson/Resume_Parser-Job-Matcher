# 📄 AI Resume ↔ Job Description Matcher

A Streamlit-based NLP application that scores how well a resume matches a job description. It combines **rule-based entity extraction** (regex + spaCy) with **semantic similarity** (sentence-transformer embeddings) to produce an interpretable match score.

---

## ✨ Features

- **PDF resume parsing** via `pdfplumber`
- **Structured entity extraction** from resumes:
  - Contact info (email, phone, LinkedIn)
  - Skills (matched against a curated skills vocabulary of 800+ terms across tech and non-tech domains)
  - Education (degree, institution, year)
  - Work experience (title, company, date range)
- **Structured job description parsing**:
  - Title
  - Required skills
  - Years of experience
  - Required education level
- **Hybrid scoring**:
  - Semantic similarity using `all-MiniLM-L6-v2`
  - Skill-overlap ratio
  - Weighted final score (70% semantic, 30% skill overlap)
- **Interactive Streamlit UI** with metrics and full JSON inspection of extracted data

---

## 🧠 How It Works

```
┌─────────────┐     ┌─────────────────┐     ┌────────────────┐
│  Resume PDF │────▶│  pdfplumber     │────▶│  Raw text      │
└─────────────┘     └─────────────────┘     └───────┬────────┘
                                                    │
┌─────────────┐                                     ▼
│  JD .txt    │──────────────────────────▶  ┌──────────────────┐
└─────────────┘                             │ Entity extraction│
                                            │  (regex + spaCy) │
                                            └────────┬─────────┘
                                                     │
                                            ┌────────▼─────────┐
                                            │ Sentence-BERT    │
                                            │ embeddings       │
                                            └────────┬─────────┘
                                                     │
                                            ┌────────▼─────────┐
                                            │ Final score      │
                                            │ (0.7·sem + 0.3·skill) │
                                            └──────────────────┘
```

### The pipeline

1. **Parse the resume PDF** → text (`extract.py`)
2. **Read the job description** → text (`match.py::load_resume_jd`)
3. **Extract structured fields** from both documents (`entities.py`, `job_extract.py`)
4. **Encode both as embeddings** using `sentence-transformers` (`match.py::semantic_score`)
5. **Compute cosine similarity** between the embeddings → semantic score `[-1, 1]`
6. **Compute skill overlap** ratio → skill score `[0, 1]`
7. **Combine into a weighted final score**:

   ```
   final = 0.7 × semantic + 0.3 × skill_overlap
   ```

---

## 📁 Project Structure

```
.
├── app.py             # Streamlit UI — file uploads, scoring, display
├── match.py           # End-to-end pipeline: load → parse → score
├── extract.py         # PDF → text using pdfplumber
├── entities.py        # Regex + spaCy extraction for resumes
│                      #   (contact, skills, education, experience)
├── job_extract.py     # Regex + spaCy extraction for job descriptions
│                      #   (title, skills, years_experience, education)
├── segment.py         # Optional: section-header-based resume segmentation
├── utils.py           # Curated SKILLS vocabulary (800+ terms)
└── README.md
```

### Module responsibilities

| Module | Role |
|---|---|
| `app.py` | Streamlit front end — handles file uploads, calls `match()`, renders results |
| `match.py` | Orchestrates the full pipeline and computes the scores |
| `extract.py` | Pulls raw text out of a PDF resume |
| `entities.py` | Extracts contact info, skills, education, and experience from resumes using regex + spaCy NER |
| `job_extract.py` | Extracts title, skills, years of experience, and education level from a JD |
| `segment.py` | Splits a resume into labelled sections (`experience`, `education`, `skills`, etc.) using a list of common section headers |
| `utils.py` | The master `SKILLS` list — both technical and non-technical |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+

### Installation

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd <your-repo-name>

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate         # macOS / Linux
# venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download the spaCy English model
python -m spacy download en_core_web_sm
```

### `requirements.txt`

```
streamlit
pdfplumber
spacy
sentence-transformers
torch
```

### Running the app

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`), upload a PDF resume and a `.txt` job description, then click **Run Match**.

---

## 📊 Output

The app displays:

- **Final Score** — weighted combination of semantic + skill overlap
- **Semantic Score** — cosine similarity of the two embeddings
- **Skill Score** — fraction of JD skills found in the resume
- **Resume Data (JSON)** — structured extraction of contact, skills, education, experience
- **Job Description Data (JSON)** — title, skills, years_experience, education

---

## 🧩 How Extraction Works

### Resumes (`entities.py`)

- **Contact**: regex patterns for emails, phone numbers, LinkedIn URLs
- **Skills**: a spaCy `PhraseMatcher` (case-insensitive) over the curated `SKILLS` list
- **Education**: regex for degree keywords (`B.S.`, `Bachelor's`, `Ph.D.`, etc.), then a ±200-char context window to find an institution (via `INSTITUTION_RE` or fallback `ORG` NER) and the latest 4-digit year
- **Experience**: regex for date ranges (e.g. `Jan 2020 - Mar 2023`, `2020 - Present`), then a context window to find the closest `ORG` entity and a heuristic title pulled from the lines just before the date

### Job descriptions (`job_extract.py`)

- **Skills**: same `PhraseMatcher` approach
- **Years of experience**: regex like `\b(\d{1,2})\+?\s+years?\b` — picks the max
- **Title**: first reasonable line in the document
- **Education**: regex for `bachelor('s)` / `master('s)`

---

## ⚙️ Tuning the Score

The weighting lives in `match.py`:

```python
def final_score(semantic, skill):
    return (0.7 * semantic) + (0.3 * skill)
```

Adjust the coefficients to favor exact skill matching over general semantic fit, or vice versa.

---

## 🛠️ Known Limitations & Possible Improvements

- **Section segmentation isn't wired into `match()`** — `segment.py` exists but isn't used. Plugging it in would let extractors run on the right slice of the resume only (e.g. skill matching only inside the "Skills" section), which usually improves precision.
- **Title heuristics are fragile** — both the resume job title and the JD title rely on "first reasonably short line," which fails on many real layouts.
- **No fuzzy skill matching** — "JS" won't match "JavaScript" unless you add aliases.
- **No multi-page header/footer cleanup** — pdfplumber returns raw page text, so repeated headers can pollute the extraction.
- **Date parsing is shallow** — "Jan 2020 - Present" is captured as strings, not normalized to durations. Computing total years of experience from the resume would let you compare directly against the JD's `years_experience` field.
- **English-only** — both spaCy (`en_core_web_sm`) and the skills vocabulary assume English.
- **`MASTER_RE` is shadowed by `BACHELOR_RE`** in `job_extract.py` because the check uses `elif`. Listing both (or returning the highest degree mentioned) would be more accurate.

---

## 📜 License

MIT (or whatever you prefer — update this section).
