import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def run_ats_analysis(resume_file, job_description_file, output_file, api_key=None):
    """
    Run ATS analysis on a resume against a job description
    
    Args:
        resume_file (str): Path to the resume file (.docx)
        job_description_file (str): Path to the job description file (.txt, .md, etc.)
        output_file (str): Path to save the analysis results (.md)
        api_key (str, optional): OpenAI API key. Defaults to None (uses env variable).
    
    Returns:
        dict: Analysis results
    """
    # Load content from files
    with open(job_description_file, 'r', encoding='utf-8') as f:
        job_description = f.read()
    
    # Convert docx to text for analysis
    from docx import Document
    doc = Document(resume_file)
    resume_text = '\n'.join([para.text for para in doc.paragraphs])
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
    
    # The ATS scoring prompt
    system_prompt = """You are CareerForgeAI, an elite career strategist and resume optimization specialist with 15+ years of executive recruitment experience across Fortune 500 companies and specialized in applicant tracking systems (ATS) algorithms."""
    
    user_prompt = f"""Analyze the following resume against the job description using this methodology:

1. INITIAL ASSESSMENT
- Conduct deep analysis of both the resume and job description to identify technical and psychological gaps

2. STRATEGIC OPTIMIZATION
- Evaluate resume structure, content strength, and ATS compatibility

Please provide:
1. An ATS compatibility score (0-100) at the top of your analysis. 
2. Keyword match analysis (which keywords from the JD appear/don't appear in the resume)
3. Content strength evaluation of each section

** Be concise and to the point. **

Resume:
{resume_text}

Job Description:
{job_description}

Make sure your analysis is natural-sounding with varied sentence structures and vocabulary to avoid AI detection.
"""
    
    # Make the API call
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    analysis = response.choices[0].message.content
    
    # Save the analysis to a file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(analysis)
    
    return analysis

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run ATS analysis on a resume')
    parser.add_argument('--resume', required=True, help='Path to resume file (.docx)')
    parser.add_argument('--job', required=True, help='Path to job description file')
    parser.add_argument('--output', required=True, help='Path to save analysis results')
    
    args = parser.parse_args()
    
    run_ats_analysis(args.resume, args.job, args.output) 