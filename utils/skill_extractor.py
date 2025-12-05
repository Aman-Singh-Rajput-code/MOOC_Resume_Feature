import spacy
import re
from typing import List, Dict, Set
from config import Config

class SkillExtractor:
    """Extract skills and relevant information from resume text"""
    
    def __init__(self):
        """Initialize the skill extractor with spaCy model"""
        try:
            self.nlp = spacy.load(Config.SPACY_MODEL)
        except OSError:
            print(f"Downloading spaCy model: {Config.SPACY_MODEL}")
            import subprocess
            subprocess.run(['python', '-m', 'spacy', 'download', Config.SPACY_MODEL])
            self.nlp = spacy.load(Config.SPACY_MODEL)
        
        self.technical_skills = set([skill.lower() for skill in Config.TECHNICAL_SKILLS])
        self.domain_keywords = Config.DOMAIN_KEYWORDS
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract technical skills from text
        
        Args:
            text: Resume text
            
        Returns:
            List of extracted skills
        """
        text_lower = text.lower()
        found_skills = []
        
        # Find technical skills using exact matching
        for skill in self.technical_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def extract_education(self, text: str) -> List[str]:
        """
        Extract education-related keywords
        
        Args:
            text: Resume text
            
        Returns:
            List of education indicators
        """
        education_keywords = [
            'bachelor', 'master', 'phd', 'mba', 'degree', 'diploma',
            'computer science', 'engineering', 'mathematics', 'statistics',
            'information technology', 'data science', 'business administration'
        ]
        
        text_lower = text.lower()
        found_education = []
        
        for keyword in education_keywords:
            if keyword in text_lower:
                found_education.append(keyword)
        
        return found_education
    
    def extract_experience_level(self, text: str) -> str:
        """
        Estimate experience level from resume
        
        Args:
            text: Resume text
            
        Returns:
            Experience level (beginner, intermediate, advanced)
        """
        text_lower = text.lower()
        
        # Look for years of experience
        years_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)'
        years_match = re.search(years_pattern, text_lower)
        
        if years_match:
            years = int(years_match.group(1))
            if years < 2:
                return 'beginner'
            elif years < 5:
                return 'intermediate'
            else:
                return 'advanced'
        
        # Check for level indicators
        if any(word in text_lower for word in ['senior', 'lead', 'principal', 'architect']):
            return 'advanced'
        elif any(word in text_lower for word in ['junior', 'intern', 'entry', 'fresher']):
            return 'beginner'
        else:
            return 'intermediate'
    
    def identify_domains(self, skills: List[str]) -> Dict[str, int]:
        """
        Identify relevant domains based on skills
        
        Args:
            skills: List of extracted skills
            
        Returns:
            Dictionary with domain names and their relevance scores
        """
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = 0
            for skill in skills:
                for keyword in keywords:
                    if keyword.lower() in skill.lower() or skill.lower() in keyword.lower():
                        score += 1
            
            if score > 0:
                domain_scores[domain] = score
        
        return domain_scores
    
    def analyze_resume(self, text: str) -> Dict:
        """
        Perform complete analysis of resume text
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary containing all extracted information
        """
        skills = self.extract_skills(text)
        education = self.extract_education(text)
        experience_level = self.extract_experience_level(text)
        domains = self.identify_domains(skills)
        
        # Get top domains
        sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)
        top_domains = [domain for domain, score in sorted_domains[:3]]
        
        return {
            'skills': skills,
            'skill_count': len(skills),
            'education': education,
            'experience_level': experience_level,
            'domains': top_domains,
            'domain_scores': domains,
            'raw_text': text[:500]  # First 500 chars for reference
        }