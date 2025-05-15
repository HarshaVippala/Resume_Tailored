#!/usr/bin/env python3
import os
import sys
import argparse
import datetime
import json
from dotenv import load_dotenv
from make_resume import patch_docx
from get_diff_and_render import get_diff_from_gpt
from ats_analysis import run_ats_analysis

load_dotenv()

def ensure_dir(directory):
    """Ensure a directory exists, create it if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def automate_resume_process(job_description_path, company_name=None, output_dir=None):
    """
    Automate the entire resume tailoring and analysis workflow.
    
    Args:
        job_description_path (str): Path to the job description file
        company_name (str, optional): Name of the company (used for folder naming)
        output_dir (str, optional): Base output directory. Defaults to 'output'
    """
    # Setup paths and directories
    base_resume_path = os.path.join('data', 'Harsha_Master.docx')
    template_path = os.path.join('data', 'placeholder_resume.docx')  # Use the new placeholder template
    
    # Create timestamp for unique ID
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Set company name if not provided
    if not company_name:
        company_name = f"company_{timestamp}"

    # Set output directory
    if not output_dir:
        output_dir = os.path.join('output', company_name)
    
    ensure_dir(output_dir)
    
    # Define output paths
    initial_analysis_path = os.path.join(output_dir, 'current_analysis.md')
    tailored_docx_path = os.path.join(output_dir, "Resume.docx")
    tailored_pdf_path = os.path.join(output_dir, "Resume.pdf")
    final_analysis_path = os.path.join(output_dir, 'analysis_after_updating.md')
    
    print(f"Starting resume tailoring process for {company_name}...")
    print(f"All outputs will be saved to {output_dir}")
    
    # Step 1: Initial ATS Analysis
    print("\n=== STEP 1: Running initial ATS analysis ===")
    run_ats_analysis(
        resume_file=base_resume_path,
        job_description_file=job_description_path,
        output_file=initial_analysis_path
    )
    print(f"Initial ATS analysis saved to {initial_analysis_path}")
    
    # Step 2: Generate tailoring recommendations (diff)
    print("\n=== STEP 2: Generating tailoring recommendations ===")
    diff_data = get_diff_from_gpt(
        jd_path=job_description_path,
        template_path=template_path,
        base_path=base_resume_path,
        api_key=os.getenv('OPENAI_API_KEY')
    )
    # Parse diff JSON directly (do not save to file)
    diff_json = json.loads(diff_data)
    print(f"Tailoring recommendations generated in memory.")
    
    # Step 3: Generate tailored resume
    print("\n=== STEP 3: Generating tailored resume ===")
    patch_docx(
        template_path=template_path,
        diff_json=diff_json,
        base_path=base_resume_path,
        out_path=tailored_docx_path
    )
    print(f"Tailored resume (DOCX) saved to {tailored_docx_path}")
    
    # Convert to PDF
    try:
        from docx2pdf import convert
        convert(tailored_docx_path, tailored_pdf_path)
        print(f"Tailored resume (PDF) saved to {tailored_pdf_path}")
    except Exception as e:
        print(f"Warning: Failed to convert to PDF: {e}")
    
    # Step 4: Final ATS Analysis
    print("\n=== STEP 4: Running final ATS analysis ===")
    run_ats_analysis(
        resume_file=tailored_docx_path,
        job_description_file=job_description_path,
        output_file=final_analysis_path
    )
    print(f"Final ATS analysis saved to {final_analysis_path}")
    
    print("\nResume tailoring process complete!")
    print(f"Review the analyses in {output_dir} to see the improvements.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automate resume tailoring and ATS analysis')
    parser.add_argument('--job', required=True, help='Path to job description file')
    parser.add_argument('--company', help='Company name (for folder naming)')
    parser.add_argument('--output', help='Base output directory')
    
    args = parser.parse_args()
    
    automate_resume_process(
        job_description_path=args.job,
        company_name=args.company,
        output_dir=args.output
    ) 