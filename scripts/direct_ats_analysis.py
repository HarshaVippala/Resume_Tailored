#!/usr/bin/env python3
import os
import sys
import argparse
from dotenv import load_dotenv
from ats_analysis import run_ats_analysis

load_dotenv()

def ensure_dir(directory):
    """Ensure a directory exists, create it if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def run_direct_ats_analysis(resume_path, job_description_path, output_path=None):
    """
    Run just the ATS analysis on a provided resume against a job description.
    
    Args:
        resume_path (str): Path to the resume file (.docx)
        job_description_path (str): Path to the job description file
        output_path (str, optional): Path to save analysis results. If None, will output to console.
    """
    if output_path:
        ensure_dir(os.path.dirname(output_path))
        
    analysis = run_ats_analysis(
        resume_file=resume_path,
        job_description_file=job_description_path,
        output_file=output_path if output_path else None
    )
    
    if not output_path:
        print(analysis)
    else:
        print(f"ATS analysis saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run direct ATS analysis on a resume')
    parser.add_argument('--resume', required=True, help='Path to resume file (.docx)')
    parser.add_argument('--job', required=True, help='Path to job description file')
    parser.add_argument('--output', help='Path to save analysis results (optional)')
    
    args = parser.parse_args()
    
    run_direct_ats_analysis(
        resume_path=args.resume,
        job_description_path=args.job,
        output_path=args.output
    ) 