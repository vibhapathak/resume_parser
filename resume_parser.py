import PyPDF2
import fitz  # PyMuPDF
import spacy
import re
import json
from datetime import datetime
import phonenumbers
from email_validator import validate_email, EmailNotValidError

class ResumeParser:
    def __init__(self):
        # Load spaCy model (download with: python -m spacy download en_core_web_sm)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Please install spaCy English model: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Improved section headers with more variations
        self.section_headers = {
            'contact': ['contact', 'personal information', 'personal details', 'contact information'],
            'summary': ['summary', 'profile', 'objective', 'about', 'professional summary', 'career objective'],
            'experience': ['experience', 'work experience', 'employment', 'work history', 'professional experience', 'work', 'career', 'employment history'],
            'education': ['education', 'academic background', 'qualifications', 'academic', 'educational background'],
            'skills': ['skills', 'technical skills', 'competencies', 'technologies', 'technical competencies', 'core competencies'],
            'projects': ['projects', 'personal projects', 'key projects', 'project'],
            'certifications': ['certifications', 'certificates', 'licenses', 'certification'],
            'achievements': ['achievements', 'key achievements', 'accomplishments']
        }
        
        # Common technical skills for better extraction
        self.tech_skills = [
            # Programming Languages
            'java', 'python', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'kotlin', 'swift',
            'typescript', 'scala', 'r', 'matlab', 'perl', 'rust', 'dart', 'j2ee',
            
            # Frameworks & Libraries
            'spring', 'spring boot', 'spring mvc', 'hibernate', 'react', 'angular', 'vue.js', 'node.js', 'express',
            'django', 'flask', 'rails', 'laravel', '.net', 'asp.net', 'jquery', 'bootstrap', 'struts',
            
            # Databases
            'mysql', 'postgresql', 'mongodb', 'oracle', 'sql server', 'sqlite', 'redis', 'cassandra',
            'dynamodb', 'elasticsearch', 'neo4j', 'rdbms',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab',
            'terraform', 'ansible', 'chef', 'puppet', 'ci/cd',
            
            # Tools & Technologies
            'kafka', 'rabbitmq', 'microservices', 'restful api', 'rest api', 'graphql', 'soap', 'junit', 'selenium',
            'postman', 'swagger', 'maven', 'gradle', 'npm', 'webpack', 'tomcat', 'jpa', 'orm',
            
            # Operating Systems
            'linux', 'unix', 'windows', 'macos',
            
            # Methodologies
            'agile', 'scrum', 'kanban', 'devops', 'tdd', 'bdd'
        ]
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using both PyPDF2 and PyMuPDF as fallback"""
        text = ""
        
        # Try PyMuPDF first (better text extraction)
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()
            if text.strip():
                return text
        except:
            pass
        
        # Fallback to PyPDF2
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except:
            pass
        
        return text
    
    def extract_contact_info(self, text):
        """Extract contact information using regex patterns"""
        contact_info = {}
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone number extraction - improved patterns
        phone_patterns = [
            r'\+?91[-.\s]?(\d{5})[-.\s]?(\d{5})',  # Indian format
            r'\+?91[-.\s]?(\d{4})[-.\s]?(\d{3})[-.\s]?(\d{3})',  # Indian format variation
            r'\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',  # US format
            r'(\d{10})',  # Simple 10 digit
            r'\+(\d{1,3})[-.\s]?(\d{4,5})[-.\s]?(\d{4,6})'  # International
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                if isinstance(phones[0], tuple):
                    contact_info['phone'] = ''.join(phones[0])
                else:
                    contact_info['phone'] = phones[0]
                break
        
        # LinkedIn URL
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.search(linkedin_pattern, text.lower())
        if linkedin:
            contact_info['linkedin'] = 'https://' + linkedin.group()
        
        # GitHub URL
        github_pattern = r'github\.com/[\w-]+'
        github = re.search(github_pattern, text.lower())
        if github:
            contact_info['github'] = 'https://' + github.group()
        
        return contact_info
    
    def extract_name(self, text):
        """Extract name using improved logic"""
        lines = text.split('\n')
        
        # Look for name in first 10 lines, skip lines with email/phone/common headers
        skip_patterns = [
            r'@', r'\+?\d{10}', r'resume', r'cv', r'curriculum vitae',
            r'software', r'engineer', r'developer', r'summary', r'contact',
            r'skills', r'experience', r'education', r'objective', r'location'
        ]
        
        for line in lines[:10]:
            line = line.strip()
            if not line or len(line) < 3:
                continue
                
            # Skip lines that match skip patterns
            if any(re.search(pattern, line.lower()) for pattern in skip_patterns):
                continue
            
            # Look for lines with 2-4 capitalized words (likely names)
            words = line.split()
            if 2 <= len(words) <= 4:
                # Check if all words start with capital letter and are alphabetic
                if all(word[0].isupper() and word.replace('-', '').replace("'", "").isalpha() for word in words):
                    return line
        
        # Fallback: use spaCy if available
        if self.nlp:
            doc = self.nlp(text[:1000])
            for ent in doc.ents:
                if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                    return ent.text
        
        return None
    
    def find_section_boundaries(self, text):
        """Find section start and end positions with improved accuracy"""
        lines = text.split('\n')
        sections = {}
        
        for section_name, keywords in self.section_headers.items():
            for i, line in enumerate(lines):
                line_clean = line.strip().lower()
                
                # Skip very long lines (unlikely to be headers)
                if len(line_clean) > 100:
                    continue
                
                # Check if line matches section keywords
                for keyword in keywords:
                    # More precise matching for section headers
                    if (line_clean == keyword or 
                        (keyword in line_clean and len(line_clean) < 50 and 
                         (line_clean.startswith(keyword) or line_clean.endswith(keyword) or
                          line_clean == keyword + ':' or line_clean == keyword + ' :'))):
                        sections[section_name] = i
                        break
                if section_name in sections:
                    break
        
        return sections
    
    def extract_section_content(self, text, section_name, section_boundaries):
        """Extract content between section boundaries"""
        if section_name not in section_boundaries:
            return ""
        
        lines = text.split('\n')
        start_idx = section_boundaries[section_name]
        
        # Find next section or end of document
        end_idx = len(lines)
        for other_section, other_idx in section_boundaries.items():
            if other_idx > start_idx and other_idx < end_idx:
                end_idx = other_idx
        
        # Extract content (skip the header line)
        content_lines = lines[start_idx + 1:end_idx]
        return '\n'.join(content_lines).strip()
    
    def extract_experience(self, text):
        """Extract work experience with improved parsing for multiple jobs and projects"""
        section_boundaries = self.find_section_boundaries(text)
        experience_text = self.extract_section_content(text, 'experience', section_boundaries)
        
        if not experience_text:
            return []
        
        experiences = []
        lines = experience_text.split('\n')
        
        current_job = None
        current_project = None
        project_description = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Check if this is a job title/company line
            if self.is_job_header(line):
                # Save previous project if exists
                if current_project and project_description:
                    current_project['description'] = ' '.join(project_description)
                    if current_job:
                        if 'projects' not in current_job:
                            current_job['projects'] = []
                        current_job['projects'].append(current_project)
                
                # Save previous job if exists
                if current_job:
                    experiences.append(current_job)
                
                # Start new job
                current_job = self.parse_job_header(line, lines, i)
                current_project = None
                project_description = []
                
            # Check if this is a project header
            elif self.is_project_header(line):
                # Save previous project if exists
                if current_project and project_description:
                    current_project['description'] = ' '.join(project_description)
                    if current_job:
                        if 'projects' not in current_job:
                            current_job['projects'] = []
                        current_job['projects'].append(current_project)
                
                # Start new project
                current_project = self.parse_project_header(line)
                project_description = []
                
            # Check if this is a bullet point or description
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                bullet_text = re.sub(r'^[•\-\*]\s*', '', line)
                if bullet_text:
                    project_description.append(bullet_text)
            
            # Check if this looks like a description line
            elif current_project and len(line) > 20:
                project_description.append(line)
            
            i += 1
        
        # Save the last project and job
        if current_project and project_description:
            current_project['description'] = ' '.join(project_description)
            if current_job:
                if 'projects' not in current_job:
                    current_job['projects'] = []
                current_job['projects'].append(current_project)
        
        if current_job:
            experiences.append(current_job)
        
        return experiences
    
    def is_job_header(self, line):
        """Check if line is a job title/company header"""
        # Common job title indicators
        job_indicators = [
            'developer', 'engineer', 'analyst', 'manager', 'intern', 'consultant', 
            'specialist', 'architect', 'lead', 'senior', 'junior', 'associate'
        ]
        
        # Check if line contains job indicators and company-like patterns
        line_lower = line.lower()
        
        # Look for job title patterns
        has_job_title = any(indicator in line_lower for indicator in job_indicators)
        
        # Look for company patterns (contains company suffixes or location)
        company_suffixes = ['ltd', 'inc', 'corp', 'llc', 'pvt', 'limited', 'company', 'solutions', 'technologies', 'systems', 'group', 'labs']
        has_company_suffix = any(suffix in line_lower for suffix in company_suffixes)
        
        # Look for location indicators
        has_location = bool(re.search(r',\s*[A-Z][a-z]+', line))
        
        return has_job_title or has_company_suffix or has_location
    
    def is_project_header(self, line):
        """Check if line is a project header"""
        line_lower = line.lower()
        project_indicators = ['project:', 'project ', 'application', 'system', 'platform', 'tool']
        
        # Check for project indicators and proper formatting
        has_project_indicator = any(indicator in line_lower for indicator in project_indicators)
        
        # Check for date patterns that often follow project names
        has_date_pattern = bool(re.search(r'\(\w+\s+\d{4}.*?\)', line))
        
        return has_project_indicator and (has_date_pattern or len(line) < 100)
    
    def parse_job_header(self, line, lines, index):
        """Parse job header to extract company, position, and duration"""
        job_info = {'raw_header': line}
        
        # Try to extract company name, position, and dates from current and next few lines
        combined_text = line
        for i in range(1, min(4, len(lines) - index)):
            next_line = lines[index + i].strip()
            if next_line and not next_line.startswith('•') and not self.is_project_header(next_line):
                combined_text += ' ' + next_line
            else:
                break
        
        # Extract position (usually first line or contains job title keywords)
        job_indicators = ['developer', 'engineer', 'analyst', 'manager', 'intern', 'consultant', 'specialist']
        for indicator in job_indicators:
            if indicator in line.lower():
                job_info['position'] = line.strip()
                break
        
        # Extract company (look for company suffixes)
        company_pattern = r'([A-Z][A-Za-z\s&,.-]+(?:Ltd|Inc|Corp|LLC|Pvt|Limited|Company|Solutions|Technologies|Systems|Group|Labs))'
        company_match = re.search(company_pattern, combined_text)
        if company_match:
            job_info['company'] = company_match.group(1).strip()
        
        # Extract duration
        date_pattern = r'\(([^)]+)\)'
        date_match = re.search(date_pattern, combined_text)
        if date_match:
            job_info['duration'] = date_match.group(1).strip()
        
        return job_info
    
    def parse_project_header(self, line):
        """Parse project header to extract project name and duration"""
        project_info = {'raw_header': line}
        
        # Extract project name (before date or colon)
        project_name_match = re.match(r'Project:\s*([^(]+)', line)
        if project_name_match:
            project_info['name'] = project_name_match.group(1).strip()
        else:
            # Fallback: everything before parentheses
            name_match = re.match(r'([^(]+)', line)
            if name_match:
                project_info['name'] = name_match.group(1).strip()
        
        # Extract duration
        date_pattern = r'\(([^)]+)\)'
        date_match = re.search(date_pattern, line)
        if date_match:
            project_info['duration'] = date_match.group(1).strip()
        
        return project_info
    
    def extract_education(self, text):
        """Extract education information with improved parsing"""
        section_boundaries = self.find_section_boundaries(text)
        education_text = self.extract_section_content(text, 'education', section_boundaries)
        
        if not education_text:
            return []
        
        education = []
        lines = education_text.split('\n')
        
        current_education = None
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            # Check for degree patterns - more precise matching
            degree_patterns = [
                (r'bachelor\s*of\s*engineering\s*in\s*([^,\n]+)', 'Bachelor of Engineering'),
                (r'bachelor\s*of\s*technology\s*in\s*([^,\n]+)', 'Bachelor of Technology'),
                (r'bachelor\s*of\s*science\s*in\s*([^,\n]+)', 'Bachelor of Science'),
                (r'b\.?tech\s*in\s*([^,\n]+)', 'B.Tech'),
                (r'b\.?e\.?\s*in\s*([^,\n]+)', 'B.E.'),
                (r'b\.?sc?\s*in\s*([^,\n]+)', 'B.Sc'),
                (r'master\s*of\s*science\s*in\s*([^,\n]+)', 'Master of Science'),
                (r'master\s*of\s*technology\s*in\s*([^,\n]+)', 'Master of Technology'),
                (r'm\.?tech\s*in\s*([^,\n]+)', 'M.Tech'),
                (r'm\.?sc?\s*in\s*([^,\n]+)', 'M.Sc'),
                (r'mba\s*in\s*([^,\n]*)', 'MBA'),
                (r'ph\.?d\.?\s*in\s*([^,\n]+)', 'Ph.D'),
                (r'diploma\s*in\s*([^,\n]+)', 'Diploma'),
                (r'(\d+(?:th|nd|rd|st)\s*grade)', ''),  # For school grades
            ]
            
            found_degree = False
            for pattern, degree_type in degree_patterns:
                match = re.search(pattern, line.lower())
                if match:
                    field = match.group(1).strip() if match.group(1) else ""
                    
                    # Clean up field
                    field = re.sub(r'[,•\-\|].*$', '', field).strip()
                    
                    current_education = {
                        'degree': degree_type or match.group(0),
                        'field': field,
                        'institution': '',
                        'year': '',
                        'additional_info': '',
                        'raw_text': line
                    }
                    found_degree = True
                    break
            
            # If no degree found but current_education exists, try to extract other info
            if not found_degree and current_education:
                # Check for institution
                if any(keyword in line.lower() for keyword in ['university', 'college', 'institute', 'school']):
                    current_education['institution'] = line
                
                # Check for graduation year
                year_match = re.search(r'graduated:\s*(\d{4})', line.lower())
                if year_match:
                    current_education['year'] = year_match.group(1)
                
                # Check for CGPA/percentage
                grade_match = re.search(r'(cgpa|percentage):\s*([\d.]+)', line.lower())
                if grade_match:
                    current_education['additional_info'] = f"{grade_match.group(1).upper()}: {grade_match.group(2)}"
            
            # If we have complete education info, add it to list
            if found_degree or (current_education and 
                              any(keyword in line.lower() for keyword in ['university', 'college', 'institute', 'school'])):
                if current_education and current_education not in education:
                    # Extract additional info from same line
                    year_match = re.search(r'(\d{4})', line)
                    if year_match:
                        current_education['year'] = year_match.group(1)
                    
                    education.append(current_education)
                    current_education = None
        
        # Add the last education entry if exists
        if current_education:
            education.append(current_education)
        
        return education
    
    def extract_skills(self, text):
        """Extract skills with improved accuracy"""
        section_boundaries = self.find_section_boundaries(text)
        skills_text = self.extract_section_content(text, 'skills', section_boundaries)
        
        if not skills_text:
            # Fallback: look for skills in entire text
            skills_text = text
        
        found_skills = []
        text_lower = skills_text.lower()
        
        # Extract from predefined technical skills list
        for skill in self.tech_skills:
            if skill.lower() in text_lower:
                # Make sure it's a whole word match
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                    found_skills.append(skill.title())
        
        # Also look for skills in structured format (comma/bullet separated)
        if skills_text != text:  # Only if we found a skills section
            # Split by common delimiters
            skill_patterns = re.split(r'[,•\n\-\|:]', skills_text)
            for skill in skill_patterns:
                skill = skill.strip()
                # Filter out very short/long items and common non-skills
                if (3 <= len(skill) <= 30 and 
                    not any(word in skill.lower() for word in ['years', 'experience', 'knowledge', 'skills', 'technologies', 'programming', 'languages', 'frameworks', 'databases', 'tools', 'deployment', 'containers', 'design', 'patterns']) and
                    not skill.isdigit() and
                    not re.match(r'^[•\-\*\s]*$', skill)):
                    found_skills.append(skill)
        
        # Remove duplicates and return
        unique_skills = []
        seen = set()
        for skill in found_skills:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                seen.add(skill_lower)
                unique_skills.append(skill)
        
        return unique_skills
    
    def parse_resume(self, file_path):
        """Main method to parse resume and return JSON"""
        
        # Extract text
        if file_path.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(file_path)
        else:
            # For text files
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        if not text.strip():
            return {"error": "Could not extract text from file"}
        
        # Parse information
        parsed_data = {
            "name": self.extract_name(text),
            "contact_info": self.extract_contact_info(text),
            "experience": self.extract_experience(text),
            "education": self.extract_education(text),
            "skills": self.extract_skills(text),
            "raw_text": text,
            "parsed_date": datetime.now().isoformat()
        }
        
        return parsed_data

# Usage example
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Parse a resume
    resume_data = parser.parse_resume("sample_resume.pdf")
    
    # Convert to JSON
    json_output = json.dumps(resume_data, indent=2, ensure_ascii=False)
    print(json_output)
    
    # Save to file
    with open("parsed_resume.json", "w") as f:
        f.write(json_output)