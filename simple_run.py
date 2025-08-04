# simple_run.py - Basic usage example

from resume_parser import ResumeParser
import json

def parse_single_resume():
    """Parse a single resume"""
    # Initialize the parser
    parser = ResumeParser()
    
    # Parse the resume (replace with your file path)
    resume_file = "sample_resume.pdf" 
    
    print(f"Parsing resume: {resume_file}")
    
    try:
        # Parse the resume
        result = parser.parse_resume(resume_file)
        
        # Print the results nicely formatted
        print("\n" + "="*50)
        print("PARSED RESUME DATA")
        print("="*50)
        
        print(f"Name: {result.get('name', 'Not found')}")
        
        contact = result.get('contact_info', {})
        print(f"Email: {contact.get('email', 'Not found')}")
        print(f"Phone: {contact.get('phone', 'Not found')}")
        print(f"LinkedIn: {contact.get('linkedin', 'Not found')}")
        
        print(f"\nSkills Found: {len(result.get('skills', []))}")
        for skill in result.get('skills', [])[:10]:  # Show first 10 skills
            print(f"  - {skill}")
        
        print(f"\nExperience Entries: {len(result.get('experience', []))}")
        for i, exp in enumerate(result.get('experience', [])[:3]):  # Show first 3
            print(f"  {i+1}. Company: {exp.get('company', 'N/A')}")
            print(f"     Position: {exp.get('position', 'N/A')}")
            print(f"     Duration: {exp.get('duration', 'N/A')}")
        
        print(f"\nEducation Entries: {len(result.get('education', []))}")
        for edu in result.get('education', []):
            print(f"  - {edu.get('degree', 'N/A')} in {edu.get('field', 'N/A')}")
        
        # Save to JSON file
        output_file = "parsed_resume.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Full results saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{resume_file}' not found!")
        print("Make sure to place your resume PDF in the same folder as this script.")
    except Exception as e:
        print(f"Error parsing resume: {str(e)}")

def parse_multiple_resumes():
    """Parse multiple resumes from a folder"""
    import os
    from pathlib import Path
    
    parser = ResumeParser()
    
    # Folder containing resumes
    resumes_folder = "resumes"  
    
    if not os.path.exists(resumes_folder):
        print(f"Folder '{resumes_folder}' not found!")
        return
    
    # Find all PDF files
    pdf_files = list(Path(resumes_folder).glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in '{resumes_folder}' folder!")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process...")
    
    results = []
    
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        
        try:
            result = parser.parse_resume(str(pdf_file))
            
            # Add filename to result
            result['source_file'] = pdf_file.name
            results.append(result)
            
            # Save individual file
            output_file = f"parsed_{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Saved: {output_file}")
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
    
    # Save combined results
    with open("all_parsed_resumes.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ All results saved to: all_parsed_resumes.json")
    print(f"Successfully processed {len(results)} out of {len(pdf_files)} files")

if __name__ == "__main__":
    print("Resume Parser - Choose an option:")
    
    print("Parse multiple resumes from folder- y")
    
    choice = input("Enter y: ").strip()
    
    if choice == "1":
        parse_single_resume()
    elif choice == "y":
        parse_multiple_resumes()
    else:
        print("Invalid choice. Running single resume parse...")
        parse_single_resume()