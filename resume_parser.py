# PDF parsers
import PyPDF2         # Fallback library to extract text from PDFs
import fitz           # More accurate PDF text extraction with table support
# NLP
import spacy          # For name extraction
# Standard libraries
import re             # Regular expressions (pattern matching)
import json           # Read/write JSON
from datetime import datetime  # For timestamping parsed data




class ResumeParser:
    def __init__(self):
        """
        Initialize the ResumeParser with spaCy NLP model and predefined section headers
        for content segmentation and known tech skill terms for skill extraction.
        """


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
            'achievements': ['achievements', 'key achievements', 'accomplishments', "awards"]
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
        """
        Extract raw text from a PDF using multiple methods including table extraction.
        """
        text = ""
        tables_data = []


        # Method 1: Try pdfplumber first (best for tables and structured content)
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract regular text
                    page_text = page.extract_text()
                    if page_text:
                        print(f"\n{page_text}")
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text
                        


                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        for table_num, table in enumerate(tables):
                            table_text = self.process_table_data(table, page_num + 1, table_num + 1)
                            text += f"\n--- Table {table_num + 1} on Page {page_num + 1} ---\n"
                            text += table_text
                            
                       
                        tables_data.append({
                                'page': page_num + 1,
                                'table_num': table_num + 1,
                                'data': table,
                                'processed_text': table_text
                            })
                            

            if text.strip():
                return text, tables_data
        except ImportError:
            print("pdfplumber not installed. Install with: pip install pdfplumber")
        except Exception as e:
            print(f"pdfplumber extraction failed: {e}")


        # Method 2: Try PyMuPDF (fitz) with table detection
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)


                # Extract regular text
                page_text = page.get_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text


                # Try to extract tables using text blocks
                blocks = page.get_text("dict")
               

                table_text = self.extract_tables_from_blocks(blocks, page_num + 1)
                if table_text:
                    text += f"\n--- Structured Content Page {page_num + 1} ---\n"
                    text += table_text


            doc.close()
            if text.strip():
                return text, tables_data
        except Exception as e:
            print(f"PyMuPDF extraction failed: {e}")


        # Method 3: Fallback to PyPDF2
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}")


        return text, tables_data


    def process_table_data(self, table, page_num, table_num):
        """
        Convert table data to readable text format.
        """
        if not table:
            return ""


        processed_text = ""
        headers = []


        # Identify headers (usually first row)
        if table and table[0]:
            headers = [cell.strip() if cell else "" for cell in table[0]]
            processed_text += "Headers: " + " | ".join(headers) + "\n"


        # Process data rows
        for row_num, row in enumerate(table[1:] if len(table) > 1 else table):
            if row and any(cell and cell.strip() for cell in row):
                row_data = []
                for col_num, cell in enumerate(row):
                    cell_text = cell.strip() if cell else ""
                    if cell_text:
                        header = headers[col_num] if col_num < len(headers) and headers[col_num] else f"Col{col_num+1}"
                        row_data.append(f"{header}: {cell_text}")


                if row_data:
                    processed_text += f"Row {row_num + 1}: " + " | ".join(row_data) + "\n"


        return processed_text


    def extract_tables_from_blocks(self, blocks, page_num):
        """
        Extract table-like structures from PyMuPDF text blocks.
        """
        if not blocks or 'blocks' not in blocks:
            return ""


        # Group text blocks that might form tables
        table_candidates = []
        current_y = None
        current_row = []


        for block in blocks['blocks']:
            if 'lines' not in block:
                continue


            for line in block['lines']:
                if 'spans' not in line:
                    continue


                line_text = ""
                line_bbox = line['bbox']


                for span in line['spans']:
                    if 'text' in span:
                        line_text += span['text']


                if line_text.strip():
                    y_pos = line_bbox[1]  # y-coordinate


                    # If this is roughly the same y-position, it's likely the same row
                    if current_y is None or abs(y_pos - current_y) < 5:
                        current_row.append({
                            'text': line_text.strip(),
                            'x': line_bbox[0],
                            'y': y_pos
                        })
                        current_y = y_pos
                    else:
                        # New row
                        if current_row:
                            table_candidates.append(sorted(current_row, key=lambda x: x['x']))
                        current_row = [{
                            'text': line_text.strip(),
                            'x': line_bbox[0],
                            'y': y_pos
                        }]
                        current_y = y_pos


        # Add the last row
        if current_row:
            table_candidates.append(sorted(current_row, key=lambda x: x['x']))


        # Convert to text
        table_text = ""
        for row in table_candidates:
            if len(row) > 1:  # Likely a table row with multiple columns
                row_text = " | ".join([cell['text'] for cell in row])
                table_text += row_text + "\n"


        return table_text


    def extract_contact_info(self, text):
        """ 
        Use regex to extract email, phone, LinkedIn, and GitHub info from resume text.
        Enhanced to work with table-extracted text.
        """
        contact_info = {}


        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]


        # Phone number extraction - improved patterns
        phone_patterns = [
            r'\+?91[-.\s]?(\d{5})[-.\s]?(\d{5})',                          # Indian format
            r'\+?91[-.\s]?(\d{4})[-.\s]?(\d{3})[-.\s]?(\d{3})',            # Indian variation
            r'\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',      # US format
            r'(\d{10})',                                                   # Simple 10-digit
            r'\+(\d{1,3})[-.\s]?(\d{4,5})[-.\s]?(\d{4,6})'                 # International
        ]


        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                phone_number = ''.join(match.groups())
                contact_info['phone'] = phone_number
                break  # Stop after first match


        # LinkedIn extraction
        linkedin_pattern = r'(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+'
        linkedin_match = re.search(linkedin_pattern, text)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group(0)


        # GitHub extraction
        github_pattern = r'(https?://)?(www\.)?github\.com/[A-Za-z0-9_-]+'
        github_match = re.search(github_pattern, text)
        if github_match:
            contact_info['github'] = github_match.group(0)


        return contact_info


    def extract_name(self, text):
        """
        Extract the candidate's name from the first few lines of text using heuristic rules.
        Enhanced to handle table-formatted contact information.
        """
        lines = text.split('\n')


        # Look for name in first 15 lines (increased for table-formatted resumes)
        skip_patterns = [
            r'@', r'\+?\d{10}', r'resume', r'cv', r'curriculum vitae',
            r'software', r'engineer', r'developer', r'summary', r'contact',
            r'skills', r'experience', r'education', r'objective', r'location',
            r'page \d+', r'table \d+', r'headers:', r'row \d+:', r'col\d+'
        ]


        for line in lines[:15]:
            line = line.strip()
            if not line or len(line) < 3:
                continue


            # Skip lines that match skip patterns
            if any(re.search(pattern, line.lower()) for pattern in skip_patterns):
                continue


            # Handle table format - extract from "Name: John Doe" or similar
            if ':' in line:
                parts = line.split(':', 1)
                if parts[0].strip().lower() in ['name', 'candidate name', 'full name']:
                    potential_name = parts[1].strip()
                    if self.is_valid_name(potential_name):
                        return potential_name


            # Look for lines with 2-4 capitalized words (likely names)
            words = line.split()
            if 2 <= len(words) <= 4:
                # Check if all words start with capital letter and are alphabetic
                if all(word[0].isupper() and word.replace('-', '').replace("'", "").isalpha() for word in words):
                    return line


        # Fallback: use spaCy if available
        if self.nlp:
            doc = self.nlp(text[:2000])  # Increased text length for table-formatted resumes
            for ent in doc.ents:
                if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                    return ent.text


        return None


    def is_valid_name(self, name):
        """
        Check if a string looks like a valid name.
        """
        if not name or len(name.split()) < 2:
            return False


        words = name.split()
        # Check if words are alphabetic and properly capitalized
        return all(word.replace('-', '').replace("'", "").isalpha() and word[0].isupper() for word in words)


    def find_section_boundaries(self, text):
        """
        Identify starting line numbers for each resume section based on predefined headers.
        Enhanced to handle table headers and structured content.
        """
        lines = text.split('\n')
        sections = {}


        for section_name, keywords in self.section_headers.items():
            print(f"\nChecking section: {section_name} with keywords: {keywords}")
            for i, line in enumerate(lines):
                line_clean = line.strip().lower()
            
                
                # Skip very long lines (unlikely to be headers)
                if len(line_clean) > 100:
                    continue


                # Handle table headers format
                if 'headers:' in line_clean:
                    header_content = line_clean.replace('headers:', '').strip()
                    print(f"Found 'headers:' at line {i}: {header_content}")
                   
                    for keyword in keywords:
                        if keyword in header_content:
                            sections[section_name] = i
                            break
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
                    print(f"Section '{section_name}' boundary found at line {sections[section_name]}")
                    break


        return sections


    def extract_section_content(self, text, section_name, section_boundaries):
        """
        Extract content of a given section from the resume text based on line positions.
        Enhanced to handle table-formatted content.
        """
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


        # Filter out empty lines at the end
        while content_lines and not content_lines[-1].strip():
            content_lines.pop()


        return '\n'.join(content_lines).strip()


    def extract_experience(self, text):
        """
        Parse the work experience section, extract jobs and related projects with descriptions.
        """
        section_boundaries = self.find_section_boundaries(text)
        experience_text = self.extract_section_content(text, 'experience', section_boundaries)


        if not experience_text:
            return []


        # Try table extraction first
        table_experience = self.extract_experience_from_tables(experience_text)
        if table_experience:
            return table_experience


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


    def extract_experience_from_tables(self, text):
        """
        Extract work experience from table-formatted content.
        """
        experiences = []
        lines = text.split('\n')


        current_job = {}


        for line in lines:
            line = line.strip()
            if not line:
                continue


            # Look for table row patterns
            if 'row' in line.lower() and ':' in line:
                # Parse table row data
                if current_job and any(current_job.values()):
                    experiences.append(current_job)
                    current_job = {}


                # Extract key-value pairs from table row
                parts = line.split('|')
                for part in parts:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()


                        # Map table headers to job fields
                        if any(word in key for word in ['position', 'role', 'title', 'designation']):
                            current_job['position'] = value
                        elif any(word in key for word in ['company', 'organization', 'employer']):
                            current_job['company'] = value
                        elif any(word in key for word in ['duration', 'period', 'from', 'to', 'date']):
                            current_job['duration'] = value
                        elif any(word in key for word in ['description', 'responsibilities', 'duties']):
                            current_job['description'] = value


        if current_job and any(current_job.values()):
            experiences.append(current_job)


        return experiences


    def is_job_header(self, line):
        """
        Determine if a line in text is likely a job title or company heading.
        """
        # Skip very short lines
        if len(line.strip()) < 5:
            return False


        line_lower = line.lower()


        # Common job title indicators
        job_indicators = [
            'software engineer', 'developer', 'analyst', 'manager', 'intern', 'consultant',
            'specialist', 'architect', 'lead', 'senior', 'junior', 'associate', 'trainee'
        ]


        # Company indicators
        company_suffixes = ['ltd', 'inc', 'corp', 'llc', 'pvt', 'limited', 'company', 'solutions', 'technologies', 'systems', 'group', 'labs', 'enterprises']


        # Date patterns that often accompany job headers
        has_date_pattern = bool(re.search(r'\|\s*\d{4}|\(\d{4}', line))


        # Look for job title patterns
        has_job_title = any(indicator in line_lower for indicator in job_indicators)


        # Look for company patterns
        has_company_suffix = any(suffix in line_lower for suffix in company_suffixes)


        # Look for location patterns
        has_location = bool(re.search(r',\s*[A-Z][a-z]+', line))


        return (has_job_title or has_company_suffix) and (has_date_pattern or has_location)


    def is_project_header(self, line):
        """
        Detect whether a line is likely a project header based on keywords and format.
        """
        line_lower = line.lower()
        project_indicators = ['project:', 'project ', 'application', 'system', 'platform', 'tool']


        # Check for project indicators and proper formatting
        has_project_indicator = any(indicator in line_lower for indicator in project_indicators)


        # Check for date patterns that often follow project names
        has_date_pattern = bool(re.search(r'\(\w+\s+\d{4}.*?\)', line))


        return has_project_indicator and (has_date_pattern or len(line) < 100)


    def parse_job_header(self, line, lines, index):
        """
        Extract job title, company, and duration from a block of lines in the experience section.
        """
        job_info = {'raw_header': line}


        # Try to extract company name, position, and dates from current and next few lines
        combined_text = line
        for i in range(1, min(3, len(lines) - index)):
            next_line = lines[index + i].strip()
            if next_line and not next_line.startswith('•') and not self.is_project_header(next_line):
                combined_text += ' ' + next_line
            else:
                break


        # Extract position (look for job titles)
        job_indicators = ['software engineer', 'developer', 'analyst', 'manager', 'intern', 'consultant', 'specialist']
        for indicator in job_indicators:
            if indicator in line.lower():
                job_info['position'] = indicator.title()
                break


        # Extract company (look for company patterns)
        company_patterns = [
            r'([A-Z][A-Za-z\s&,.&-]+(?:Ltd|Inc|Corp|LLC|Pvt|Limited|Company|Solutions|Technologies|Systems|Group|Labs|Enterprises))',
            r'([A-Z][A-Za-z\s&,.&-]+),\s*[A-Z][a-z]+\s*\|'  # Company, City | pattern
        ]


        for pattern in company_patterns:
            company_match = re.search(pattern, combined_text)
            if company_match:
                job_info['company'] = company_match.group(1).strip()
                break


        # Extract duration (look for date patterns)
        duration_patterns = [
            r'\|\s*([^|]+?)(?:\s*$|\s*\n)',  # After | symbol
            r'(\d{4}\s*-\s*(?:\d{4}|Present))',  # Year ranges
            r'([A-Z][a-z]+\s+\d{2}\s*-\s*[A-Z][a-z]+\s+\d{2})',  # Month Year ranges
        ]


        for pattern in duration_patterns:
            date_match = re.search(pattern, combined_text)
            if date_match:
                job_info['duration'] = date_match.group(1).strip()
                break


        return job_info


    def parse_project_header(self, line):
        """
        Extract project title and duration from a single line.
        """
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
        """
        Parse the education section and extract degree, field, institution, and year of completion.
        Enhanced to handle both regular text and table formats.
        """
        section_boundaries = self.find_section_boundaries(text)
        education_text = self.extract_section_content(text, 'education', section_boundaries)


        if not education_text:
            return []


        # Try table extraction first
        table_education = self.extract_education_from_tables(education_text)
        if table_education:
            return table_education


        # Fallback to regular text parsing
        education = []
        lines = education_text.split('\n')


        current_education = None
        i = 0


        while i < len(lines):
            line = lines[i].strip()
            if not line or len(line) < 3:
                i += 1
                continue


            # Look for institution patterns first
            institution_patterns = [
                r'([A-Z][A-Za-z\s&,.&-]+(?:University|College|Institute|School))',
                r'([A-Z][A-Za-z\s&,.&-]+),\s*([A-Za-z]+)'
            ]


            institution_found = False
            for pattern in institution_patterns:
                match = re.search(pattern, line)
                if match:
                    if current_education:
                        education.append(current_education)


                    current_education = {
                        'institution': match.group(1).strip(),
                        'degree': '',
                        'field': '',
                        'year': '',
                        'cgpa': '',
                        'raw_text': line
                    }
                    institution_found = True
                    break


            if not institution_found and current_education:
                # Look for degree patterns
                degree_patterns = [
                    (r'masters?\s+in\s+([^,\n]+)', 'Masters'),
                    (r'master\s*of\s*([^,\n]+)', 'Master of'),
                    (r'bachelor\s*of\s*([^,\n]+)', 'Bachelor of'),
                    (r'b\.?\s*sc\.?\s*in\s*([^,\n]+)', 'B.Sc'),
                    (r'b\.?\s*tech\s*in\s*([^,\n]+)', 'B.Tech'),
                    (r'b\.?\s*e\.?\s*in\s*([^,\n]+)', 'B.E'),
                    (r'm\.?\s*sc\.?\s*in\s*([^,\n]+)', 'M.Sc'),
                    (r'm\.?\s*tech\s*in\s*([^,\n]+)', 'M.Tech'),
                    (r'mba', 'MBA'),
                    (r'diploma\s*in\s*([^,\n]+)', 'Diploma')
                ]


                for pattern, degree_type in degree_patterns:
                    match = re.search(pattern, line.lower())
                    if match:
                        current_education['degree'] = degree_type
                        if match.groups() and match.group(1):
                            current_education['field'] = match.group(1).strip()
                        break


                # Look for year
                year_match = re.search(r'(\d{4})', line)
                if year_match:
                    current_education['year'] = year_match.group(1)


                # Look for CGPA/percentage
                cgpa_match = re.search(r'(cgpa|gpa)[\s:]*(\d+\.?\d*)', line.lower())
                if cgpa_match:
                    current_education['cgpa'] = f"{cgpa_match.group(1).upper()}: {cgpa_match.group(2)}"


                percentage_match = re.search(r'(\d+\.?\d*)%', line)
                if percentage_match:
                    current_education['cgpa'] = f"Percentage: {percentage_match.group(1)}%"


            i += 1


        if current_education:
            education.append(current_education)


        return education


    def extract_education_from_tables(self, text):
        """
        Extract education information specifically from table-formatted content.
        """
        education = []
        lines = text.split('\n')


        current_education = {}


        for line in lines:
            line = line.strip()
            if not line:
                continue


            # Look for table row patterns
            if 'row' in line.lower() and ':' in line:
                # Parse table row data
                if current_education and any(current_education.values()):
                    education.append(current_education)
                    current_education = {}


                # Extract key-value pairs from table row
                parts = line.split('|')
                for part in parts:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()


                        # Map table headers to education fields
                        if any(word in key for word in ['degree', 'qualification', 'course']):
                            current_education['degree'] = value
                        elif any(word in key for word in ['institution', 'university', 'college', 'school']):
                            current_education['institution'] = value
                        elif any(word in key for word in ['field', 'specialization', 'major', 'stream']):
                            current_education['field'] = value
                        elif any(word in key for word in ['year', 'graduation', 'completion']):
                            current_education['year'] = value
                        elif any(word in key for word in ['cgpa', 'gpa', 'percentage', 'marks']):
                            current_education['cgpa'] = value


        if current_education and any(current_education.values()):
            education.append(current_education)


        return education


    def extract_skills(self, text):
        """
        Identify technical and soft skills listed in the resume using predefined terms and format parsing.
        """
        section_boundaries = self.find_section_boundaries(text)
        skills_text = self.extract_section_content(text, 'skills', section_boundaries)


        if not skills_text:
            return []


        found_skills = []


        # Extract from predefined technical skills list ONLY from skills section
        text_lower = skills_text.lower()
        for skill in self.tech_skills:
            if skill.lower() in text_lower:
                # Make sure it's a whole word match
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                    found_skills.append(skill.title())


        # Parse structured skills section
        lines = skills_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue


            # Skip category headers
            if any(header in line.lower() for header in ['languages:', 'frameworks:', 'databases:', 'tools:', 'architecture:']):
                continue


            # Split line by common delimiters and extract skills
            skills_in_line = re.split(r'[,•\n\-\|]', line)
            for skill in skills_in_line:
                skill = skill.strip()


                # Filter out noise - be very strict
                if (2 <= len(skill) <= 25 and
                    not any(noise in skill.lower() for noise in [
                        '@', '.com', 'present', 'mumbai', 'bangalore', 'years', 'experience',
                        'oct', 'dec', 'gained', 'hands', 'system', 'framework', 'between',
                        'time', 'syncing', 'reducing', 'transaction', 'failures', 'collaborated',
                        'frontend', 'meet', 'business', 'goals', 'software', 'engineer'
                    ]) and
                    not skill.isdigit() and  # No pure numbers
                    not re.match(r'^[•\-\*\s]+$', skill) and  # No symbols only
                    not '@' in skill and  # No emails
                    not skill.lower() in ['and', 'the', 'for', 'with', 'from', 'to', 'in', 'on', 'at', 'by']  # No common words
                   ):
                    found_skills.append(skill)


        # Remove duplicates and clean up
        unique_skills = []
        seen = set()
        for skill in found_skills:
            skill_clean = skill.strip()
            skill_lower = skill_clean.lower()
            if skill_lower not in seen and skill_clean:
                seen.add(skill_lower)
                unique_skills.append(skill_clean)


        return unique_skills


    def extract_projects(self, text):
        """
        Extract projects section with better parsing.
        """
        section_boundaries = self.find_section_boundaries(text)
        projects_text = self.extract_section_content(text, 'projects', section_boundaries)


        if not projects_text:
            return []


        projects = []
        lines = projects_text.split('\n')
        current_project = None


        for line in lines:
            line = line.strip()
            if not line:
                continue


            # Look for project names (usually followed by colon or description)
            if ':' in line and len(line) < 100:
                if current_project:
                    projects.append(current_project)


                parts = line.split(':', 1)
                current_project = {
                    'name': parts[0].strip(),
                    'description': parts[1].strip() if len(parts) > 1 else '',
                    'technologies': []
                }
            elif current_project and line:
                # Add to description
                if current_project['description']:
                    current_project['description'] += ' ' + line
                else:
                    current_project['description'] = line


        if current_project:
            projects.append(current_project)


        return projects


    def extract_achievements(self, text):
        """
        Extract achievements/accomplishments section.
        """
        section_boundaries = self.find_section_boundaries(text)
        achievements_text = self.extract_section_content(text, 'achievements', section_boundaries)


        if not achievements_text:
            return []


        achievements = []
        lines = achievements_text.split('\n')


        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                # Remove bullet points
                achievement = re.sub(r'^[•\-\*]\s*', '', line)
                if achievement:
                    achievements.append(achievement)


        return achievements


    def parse_resume(self, file_path):
        """
        Main entry point to parse a resume from a file and return all extracted fields as JSON.
        Enhanced with table support.
        """
        tables_data = []


        # Extract text
        if file_path.lower().endswith('.pdf'):
            text, tables_data = self.extract_text_from_pdf(file_path)
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
            "projects": self.extract_projects(text),
            "achievements": self.extract_achievements(text),
            "tables_detected": len(tables_data),
            "tables_data": tables_data if tables_data else None,
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
    with open("parsed_resume.json", "w", encoding="utf-8") as f:
        f.write(json_output)
