import json
import sys
from openai import OpenAI
from make_resume import patch_docx
from dotenv import load_dotenv
import os
from docx2pdf import convert
import re
import argparse
from docxedit import extract_placeholders

load_dotenv()

def extract_json_from_markdown(text):
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return text

def get_diff_from_gpt(jd_path, template_path, base_path, api_key=None):
    client = OpenAI(api_key=api_key)
    job_desc = open(jd_path).read()
    
    from docx import Document
    # Extract placeholders from the template
    template_doc = Document(template_path)
    placeholders = extract_placeholders(template_doc)
    # Build a JSON skeleton and code block
    json_skeleton = '{\n' + ',\n'.join([f'  "{ph}": ""' for ph in placeholders]) + '\n}'
    json_template = "```json\n" + json_skeleton + "\n```"
    placeholder_keys = ', '.join(placeholders)

    # Extract resume text from the base resume
    base_doc = Document(base_path)
    resume_text = '\n'.join([para.text for para in base_doc.paragraphs])

    prompt = (
        "You are CareerForgeAI, an elite career strategist and resume optimization specialist with 15+ years of executive recruitment experience across Fortune 500 companies and specialized in applicant tracking systems (ATS) algorithms."
        "Modern hiring processes rely heavily on automated screening and psychological triggers that determine which candidates advance. 85 percent of resumes are rejected before human eyes ever see them. Standard resume advice fails to address the technical and psychological aspects of successful applications."
        "Conduct deep analysis of both documents to identify technical and psychological gaps"
        "Produce an ATS-optimized resume with properly weighted keywords with STAR format using the job description and base resume."
        "by populating a JSON object. The output MUST be a single, flat JSON object.\n\n"
        "**CRITICAL INSTRUCTIONS FOR JSON KEY FORMATTING:**\n"
        "1. You MUST use the EXACT placeholder keys as provided in the `JSON_TEMPLATE` below.\n"
        "2. Keys are case-sensitive and character-sensitive. They MUST include the angle brackets `<` and `>` and be in ALL CAPS or the exact case as shown in the template (e.g., `<SUMMARY>`, `<JOB1_POINT1>`).\n"
        "3. DO NOT modify the key names in any way. This means:\n"
        "    - NO converting to lowercase.\n"
        "    - NO converting to snake_case or camelCase.\n"
        "    - NO removing or changing angle brackets or any other characters.\n"
        "    - NO adding, removing, or renaming any keys from the template.\n"
        "4. The entire response MUST be ONLY the JSON object, starting with `{` and ending with `}`. Do not include any text before or after the JSON object, including markdown code fences.\n\n"
        f"**JSON_TEMPLATE (Fill in the empty string values for each key. Preserve keys EXACTLY as shown):**\n{json_template}\n\n"
        "**JSON_SKELETON_TO_POPULATE (Fill in the empty string values for each key. Preserve keys EXACTLY as shown. This is the structure your JSON output must follow):**\n{json_skeleton}\n\n"
        "**CONTENT GUIDELINES (for the string values in the JSON):**\n"
        "- If no specific information is available for a placeholder key, use an empty string `\"\"` as its value.\n"
        "- All values associated with keys MUST be strings. Do NOT use nested JSON objects or JSON arrays as values.\n"
        "- For placeholders representing a list of points (e.g., for job experience bullet points like `<JOB1_POINT1>`, `<JOB1_POINT2>`), each such key should receive content for its corresponding single point. If a single key is intended to hold multiple distinct points, combine them into a single string with each point on a new line (separated by `\\n`).\n"
        "- For SKILLS placeholders (e.g., `<SKILLS_CLOUDDEVOPS>`, `<SKILLS_MONITORINGOBSERVABILITY>`): List specific and discrete software, technologies, tools, libraries, frameworks, and well-defined methodologies (e.g., 'Python', 'React', 'AWS Lambda', 'Docker', 'Git', 'Agile', 'Scrum'). Do NOT list general concepts, practices, or categories (e.g., avoid terms like 'cloud computing', 'data analysis', 'software development', 'application performance monitoring' as standalone items unless they are part of a specific, named methodology or platform you are listing). Focus on concrete nouns that represent actual skills a person uses.\n"
        
        "- Focus on concise, relevant bullet points.\n"
        "- Work experience bullet points MUST reference the specific project name or context, list the primary technologies/frameworks used, and include a quantifiable outcome or metric (e.g., 'On [ProjectName] using [TechStack], achieved [Result] resulting in [Metric]').do not reference projects, teams, or activities from any other employer.\n"
        "- In the SUMMARY section, specify an exact number of years of experience either 4 years or 5 years; do not use the "+" notation.\n"
        
        "**CHARACTER LIMIT CONSTRAINTS (CRITICAL FOR PROPER FORMATTING):**\n"
        "- SUMMARY section: ```MUST be between 370-420 characters (including spaces). It must be atleast 370 characters.```. Concise yet comprehensive overview of professional background.\n"
        "- SKILLS sections: Maximum 7 skills per category, listing most important skills first. Skills should be presented as comma-separated values on a single line.\n"
        "- WORK EXPERIENCE bullet points: ```Each bullet point should vary naturally in length between 180-235 characters (including spaces)```. Aim for a mix of concise and detailed points within this range, with some bullets being more succinct (~180-200 chars) and others more comprehensive (~210-235 chars) as the content requires.\n\n"
        "- Keep the count of 7-eleven stores less than 2500 stores for work experience bullet points"
        "- Architecture and design bullet should not have more then 4 values."
        "- Languages and Frameworks should have a mix of languages and their related frameworks. Do not mention HTML and CSS as a language and framework."
        "- Use varied, natural sentence structures.\n"
        "- Be technically specific and accurate: mention technologies, tools, frameworks, methodologies relevant to the job description.\n"
        "- Use project-specific details from the base resume (e.g., '7-Eleven Store Analytics Platform', 'Retail Monitoring Dashboard', 'Claims Processing Pipeline' for Liberty Mutual) with their associated technologies and frameworks. If creating new projects, align them with company operations (e.g., '7-Eleven Inventory Management System', 'Liberty Mutual Policy Validation Service'). For each project, specify the actual technologies used (e.g., OpenTelemetry, AWS CloudWatch, Node.js, TypeScript) and include quantifiable performance metrics and business impact.\n"
        "- Select the most relevant roles for the target job description. It's acceptable if 1 or 2 work experience bullets are not directly related to the job description; prioritize showcasing core strengths and impact.\n"
        "- Include concrete, quantifiable achievements with metrics where possible.\n"
        "- Focus on concise, relevant bullet points.\n"
        "- Avoid formulaic or AI-detectable language.\n\n"
        "- Please check grammer and spelling of the output."
        "**INPUTS:**\n"
        "Base Resume Text (for context):\n"
        f"{resume_text}\n\n"
        "Job Description (to tailor for):\n"
        f"{job_desc}"
    )
    
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )
    
    content = response.choices[0].message.content
    try:
        diff_data = json.loads(content)
    except json.JSONDecodeError:
        clean_content = extract_json_from_markdown(content)
        diff_data = json.loads(clean_content)
    # Check for nested/sectioned output and retry if necessary
    if any(isinstance(v, (list, dict)) for v in diff_data.values()):
        print("Detected nested or sectioned output from LLM. Retrying with explicit flat mapping instructions...")
        retry_prompt = (
            "You must return a FLAT JSON mapping where each key matches the placeholder format (e.g., <SUMMARY>, <JOB1_POINT1>, etc.).\n"
            "Do NOT use sections, arrays, or change key names.\n"
            f"JSON template (fill in the values):\n{json_skeleton}\n\n"
            f"Base Resume:\n{resume_text}\n\n"
            f"Job Description:\n{job_desc}\n"
        )
        retry_response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": retry_prompt}]
        )
        retry_content = retry_response.choices[0].message.content
        try:
            diff_data = json.loads(retry_content)
        except json.JSONDecodeError:
            clean_retry = extract_json_from_markdown(retry_content)
            diff_data = json.loads(clean_retry)
    
    # Verify that all placeholders are included
    missing_placeholders = [p for p in placeholders if p not in diff_data]
    if missing_placeholders:
        missing_json_skeleton = '{\n' + ',\n'.join([f'  "{ph}": ""' for ph in missing_placeholders]) + '\n}'
        missing_list = ', '.join(missing_placeholders)
        print(f"Warning: The following placeholders were not generated: {missing_list}")
        
        # Make another API call to fill missing placeholders
        missing_prompt = (
            f"You previously generated content for a resume but missed the following placeholders: {missing_list}\n\n"
            "Please generate content for ONLY these missing placeholders, considering the job description and base resume. "
            "Return ONLY a valid JSON with these placeholder keys mapped to optimized content strings. DO NOT OMIT ANY KEY.\n\n"
            
            "**CHARACTER LIMIT CONSTRAINTS (CRITICAL FOR PROPER FORMATTING):**\n"
            "- SUMMARY section: Must be between 400-500 characters (including white spaces). Concise yet comprehensive overview of professional background.\n"
            "- SKILLS sections: Maximum 7 skills per category, listing most important skills first. Skills should be presented as comma-separated values on a single line.\n"
            "- WORK EXPERIENCE bullet points: Each bullet must be between 120-240 characters (including white spaces). Include metrics and achievements while maintaining this length constraint.\n\n"
            
            f"JSON template (fill in the values):\n{missing_json_skeleton}\n\n"
            f"Base Resume:\n{resume_text}\n\n"
            f"Job Description:\n{job_desc}\n"
        )
        
        missing_response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": content},
                {"role": "user", "content": missing_prompt}
            ]
        )
        
        missing_content = missing_response.choices[0].message.content
        try:
            # Try to parse directly first
            missing_data = json.loads(missing_content)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from markdown code blocks
            clean_missing = extract_json_from_markdown(missing_content)
            missing_data = json.loads(clean_missing)
        
        # Merge the two sets of data
        diff_data.update(missing_data)
    
    return json.dumps(diff_data, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a diff for resume tailoring")
    parser.add_argument("--jd", required=True, help="Path to job description file")
    parser.add_argument("--template", required=True, help="Path to template resume")
    parser.add_argument("--base", required=True, help="Path to base resume")
    parser.add_argument("--diff", required=True, help="Path to save diff JSON")
    parser.add_argument("--output", help="Path to save output resume (if specified)")
    
    args = parser.parse_args()
    
    api_key = os.getenv("OPENAI_API_KEY")
    diff_data = get_diff_from_gpt(args.jd, args.template, args.base, api_key)
    
    # Save diff to a file
    with open(args.diff, "w") as f:
        f.write(diff_data)
    
    # If output path is provided, generate the resume
    if args.output:
        template_path = os.path.join('data', 'master_resume.dotx')
        patch_docx(
            template_path=template_path,
            base_path=args.base,
            diff_path=args.diff,
            output_path=args.output
        )
        
        # Set permissions on the generated DOCX file to user read/write (chmod 644)
        try:
            os.chmod(args.output, 0o644)
        except Exception as e:
            print(f"Warning: Failed to set permissions on DOCX file: {e}")
        
        # Optionally convert to PDF
        try:
            pdf_path = os.path.splitext(args.output)[0] + ".pdf"
            convert(args.output, pdf_path)
            # Set permissions on the generated PDF file to user read/write (chmod 644)
            try:
                os.chmod(pdf_path, 0o644)
            except Exception as e:
                print(f"Warning: Failed to set permissions on PDF file: {e}")
            print(f"Generated PDF: {pdf_path}")
        except Exception as e:
            print(f"Warning: Failed to convert to PDF with docx2pdf: {e}")
            # Fallback: Try AppleScript via osascript for PDF conversion
            import subprocess
            applescript = f'''
            tell application "Microsoft Word"
                open POSIX file "{os.path.abspath(args.output)}"
                set theDoc to active document
                set pdfPath to "{os.path.abspath(pdf_path)}"
                save as theDoc file format format PDF file name pdfPath
                close theDoc saving no
            end tell
            '''
            try:
                result = subprocess.run([
                    "osascript", "-e", applescript
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"[Fallback] PDF generated via AppleScript: {pdf_path}")
                    try:
                        os.chmod(pdf_path, 0o644)
                    except Exception as e:
                        print(f"Warning: Failed to set permissions on fallback PDF file: {e}")
                else:
                    print(f"[Fallback] AppleScript PDF conversion failed: {result.stderr}")
            except Exception as ase:
                print(f"[Fallback] Exception during AppleScript PDF conversion: {ase}")
            
    print(f"Diff saved to {args.diff}")
    if args.output:
        print(f"Tailored resume saved to {args.output}")
