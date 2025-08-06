
# 🧠 Resume Parser

A Python-based resume parser that extracts structured data from resume PDFs in bulk. It uses NLP, regex, and PDF parsing to extract:

- 👤 Name  
- 📞 Contact Info (Email, Phone, LinkedIn, GitHub)  
- 💼 Experience (Company, Role, Duration, Projects)  
- 🎓 Education (Degree, Field, Institute, Year)  
- 🛠️ Skills

---

## 📦 Features

- Parse multiple resumes at once
- Structured JSON output
- Works even with noisy or varied resume formats

---

## 🚀 Setup & Usage

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/resume-parser.git
cd resume-parser
````

### 2. Set Up a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install spacy PyPDF2 pymupdf phonenumbers email-validator
python -m spacy download en_core_web_sm
```

---

## 🗂️ Project Structure

```
resume-parser/
├── resume_parser.py           # Core logic
├── simple_run.py              # CLI to run the parser
├── resumes/                   # Folder containing multiple PDF resumes
├── parsed_<filename>.json     # Output for each resume (auto-created)
└── all_parsed_resumes.json    # Combined result from batch parsing
```

---

## ▶️ How to Run

Make sure your PDF resumes are placed in the `resumes/` folder.

```bash
python simple_run.py
```

When prompted:

```bash
Enter y:
```

And the parser will:

* Process all PDF files
* Output JSONs for each
* Save one combined file as `all_parsed_resumes.json`

---

## 🧪 Sample Output (JSON)

```json
{
  "name": " Doe",
  "contact_info": {
    "email": "doe@example.com",
    "phone": "8xxx003210",
    "linkedin": "https://linkedin.com/in/doe"
  },
  "skills": ["Python", "Node.js", "MongoDB"],
  "education": [
    {
      "degree": "Bachelor of Technology",
      "field": "Computer Science",
      "institution": "Tech University",
      "year": "2024"
    }
  ],
  "experience": [
    {
      "company": "Tech Solutions Ltd",
      "position": "Software Engineer",
      "duration": "Jan 2023 – July 2024"
    }
  ],
  "parsed_date": "2025-08-04T16:45:00"
}
```

---

## 📚 Tech Stack

| Library           | Purpose                                |
| ----------------- | -------------------------------------- |
| `PyMuPDF` (fitz)  | Primary PDF text extraction            |
| `PyPDF2`          | Fallback PDF reader                    |
| `spaCy`           | Named Entity Recognition (e.g., names) |
| `re`              | Regex parsing of emails, phones, etc.  |
| `phonenumbers`    | Optional phone normalization           |
| `email-validator` | Optional email validation              |

---

## ✍️ Maintainer

[Vibha Pathak](https://github.com/vibhapathak)

---

## 📄 License

[MIT License](LICENSE)

```

