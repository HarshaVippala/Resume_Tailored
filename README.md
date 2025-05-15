# Resume_Tailored – Automated Resume Tailoring & ATS Analysis

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white) ![python-docx](https://img.shields.io/badge/python--docx-3776AB?style=for-the-badge&logo=python&logoColor=white) ![docx2pdf](https://img.shields.io/badge/docx2pdf-4A90E2?style=for-the-badge&logo=python&logoColor=white) ![python-dotenv](https://img.shields.io/badge/python--dotenv-000000?style=for-the-badge&logo=python&logoColor=white) ![argparse](https://img.shields.io/badge/argparse-000000?style=for-the-badge&logo=python&logoColor=white) ![pypandoc](https://img.shields.io/badge/pypandoc-000000?style=for-the-badge&logo=pandoc&logoColor=white)

Automate tailoring your DOCX resume to any job description with LLM-powered ATS analysis, generate DOCX/PDF outputs, and preserve original formatting.

---

## Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/Resume_Tailored.git
   cd Resume_Tailored
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Pandoc (optional, for PDF export):
   - macOS: `brew install pandoc`
   - See https://pandoc.org/installing.html
4. Create a `.env` file at project root with your API key:
   ```ini
   OPENAI_API_KEY=your_api_key_here
   ```

---

## Usage

### Full Automation
Run the complete workflow: ATS analysis, diff generation, resume patching, PDF conversion, and final analysis.
```bash
python scripts/automate_resume.py \
  --job data/JD.txt \
  --company "AcmeCorp" \
  --output output/AcmeCorp
```
Outputs saved under `output/AcmeCorp/`:
- `current_analysis.md` (initial ATS analysis)
- `Resume.docx`, `Resume.pdf` (tailored resume)
- `analysis_after_updating.md` (final ATS analysis)

### Individual Steps
1. **ATS Analysis Only**
   ```bash
   python scripts/direct_ats_analysis.py \
     --resume data/Harsha_Master.docx \
     --job data/JD.txt \
     --output output/AcmeCorp/ats_before.md
   ```
2. **Generate Diff**
   ```bash
   python scripts/get_diff_and_render.py \
     --jd data/JD.txt \
     --template data/placeholder_resume.docx \
     --base data/Harsha_Master.docx \
     --diff data/diff.json
   ```
3. **Apply Diff & Create Resume**
   ```bash
   python scripts/make_resume.py \
     --template data/placeholder_resume.docx \
     --base data/Harsha_Master.docx \
     --diff data/diff.json \
     --output output/AcmeCorp/Resume.docx
   ```

---

## Placeholder Guide

Use `<PLACEHOLDER_NAME>` (e.g., `<SUMMARY>`, `<JOB1_POINT1>`) in `data/placeholder_resume.docx` to mark sections for dynamic, style-preserving replacement.

---

## License

MIT 