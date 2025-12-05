import os
from typing import Dict, Optional
from utils.text_extraction import TextExtractor
from utils.skill_extractor import SkillExtractor

class ResumeProcessor:
    """Process and analyze resume files"""
    
    def __init__(self):
        """Initialize the resume processor"""
        self.text_extractor = TextExtractor()
        self.skill_extractor = SkillExtractor()
    
    def process_resume(self, file_path: str) -> Optional[Dict]:
        """
        Process a resume file and extract relevant information
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Dictionary containing extracted information or None if error
        """
        # Extract text from file
        text = self.text_extractor.extract_text(file_path)
        
        if not text:
            return None
        
        # Clean the text
        text = self.clean_text(text)
        
        # Analyze the resume
        analysis = self.skill_extractor.analyze_resume(text)
        
        # Add file information
        analysis['file_name'] = os.path.basename(file_path)
        analysis['text_length'] = len(text)
        analysis['full_text'] = text
        
        return analysis
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep alphanumeric and basic punctuation
        # This helps in skill matching
        import re
        text = re.sub(r'[^\w\s\.\,\-\+\#\(\)]', ' ', text)
        
        return text
    
    def get_resume_summary(self, analysis: Dict) -> str:
        """
        Generate a human-readable summary of the resume analysis
        
        Args:
            analysis: Analysis dictionary from process_resume
            
        Returns:
            Summary string
        """
        summary_parts = []
        
        # Experience level
        summary_parts.append(f"Experience Level: {analysis['experience_level'].capitalize()}")
        
        # Skills count
        summary_parts.append(f"Technical Skills Identified: {analysis['skill_count']}")
        
        # Top domains
        if analysis['domains']:
            domains_str = ', '.join([d.replace('_', ' ').title() for d in analysis['domains']])
            summary_parts.append(f"Primary Domains: {domains_str}")
        
        # Top skills (first 10)
        if analysis['skills']:
            top_skills = ', '.join(analysis['skills'][:10])
            summary_parts.append(f"Key Skills: {top_skills}")
        
        return '\n'.join(summary_parts)