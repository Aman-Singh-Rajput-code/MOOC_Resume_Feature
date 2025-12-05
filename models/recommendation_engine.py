import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
from config import Config

class RecommendationEngine:
    """Generate course recommendations based on resume analysis"""
    
    def __init__(self, course_manager):
        """
        Initialize recommendation engine
        
        Args:
            course_manager: CourseManager instance with loaded courses
        """
        self.course_manager = course_manager
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2),  # Use unigrams and bigrams
            min_df=1
        )
        
        # Prepare course vectors
        self.prepare_course_vectors()
    
    def prepare_course_vectors(self):
        """Prepare TF-IDF vectors for all courses"""
        df = self.course_manager.get_dataframe()
        
        if df.empty:
            self.course_vectors = None
            return
        
        # Use combined text field for vectorization
        course_texts = df['combined_text'].fillna('').tolist()
        
        # Fit and transform
        self.course_vectors = self.vectorizer.fit_transform(course_texts)
        print(f"Prepared vectors for {len(course_texts)} courses")
    
    def create_resume_vector(self, resume_analysis: Dict) -> np.ndarray:
        """
        Create a vector representation of the resume
        
        Args:
            resume_analysis: Analysis dictionary from ResumeProcessor
            
        Returns:
            TF-IDF vector for the resume
        """
        # Combine all relevant text from resume
        resume_text_parts = []
        
        # Add skills (weighted more heavily by repeating)
        if resume_analysis.get('skills'):
            skills_text = ' '.join(resume_analysis['skills']) * 3  # Repeat 3 times for weight
            resume_text_parts.append(skills_text)
        
        # Add domains
        if resume_analysis.get('domains'):
            domains_text = ' '.join(resume_analysis['domains']) * 2
            resume_text_parts.append(domains_text)
        
        # Add education keywords
        if resume_analysis.get('education'):
            education_text = ' '.join(resume_analysis['education'])
            resume_text_parts.append(education_text)
        
        # Add full text (once)
        if resume_analysis.get('full_text'):
            resume_text_parts.append(resume_analysis['full_text'])
        
        resume_text = ' '.join(resume_text_parts)
        
        # Transform using the same vectorizer
        resume_vector = self.vectorizer.transform([resume_text])
        
        return resume_vector
    
    def calculate_similarity_scores(
        self, 
        resume_vector: np.ndarray
    ) -> np.ndarray:
        """
        Calculate cosine similarity between resume and all courses
        
        Args:
            resume_vector: TF-IDF vector for resume
            
        Returns:
            Array of similarity scores
        """
        if self.course_vectors is None:
            return np.array([])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(resume_vector, self.course_vectors)
        
        return similarities[0]  # Return 1D array
    
    def apply_boosting(
        self, 
        similarities: np.ndarray, 
        resume_analysis: Dict
    ) -> np.ndarray:
        """
        Apply boosting factors based on various criteria
        
        Args:
            similarities: Base similarity scores
            resume_analysis: Resume analysis data
            
        Returns:
            Boosted similarity scores
        """
        df = self.course_manager.get_dataframe()
        boosted_scores = similarities.copy()
        
        # Boost based on course rating (higher ratings get slight boost)
        rating_boost = df['course_rating'].values / 5.0 * 0.1
        boosted_scores += rating_boost
        
        # Boost based on popularity
        popularity_boost = df['popularity_score'].values * 0.1
        boosted_scores += popularity_boost
        
        # Boost free courses slightly for beginners
        if resume_analysis.get('experience_level') == 'beginner':
            free_boost = (df['is_paid'] == 'Free').astype(float) * 0.05
            boosted_scores += free_boost
        
        return boosted_scores
    
    def get_recommendations(
        self, 
        resume_analysis: Dict, 
        top_n: int = None
    ) -> List[Dict]:
        """
        Generate course recommendations based on resume analysis
        
        Args:
            resume_analysis: Analysis from ResumeProcessor
            top_n: Number of recommendations to return
            
        Returns:
            List of recommended courses with scores
        """
        if top_n is None:
            top_n = Config.TOP_N_RECOMMENDATIONS
        
        # Create resume vector
        resume_vector = self.create_resume_vector(resume_analysis)
        
        # Calculate similarity scores
        similarities = self.calculate_similarity_scores(resume_vector)
        
        if len(similarities) == 0:
            return []
        
        # Apply boosting
        final_scores = self.apply_boosting(similarities, resume_analysis)
        
        # Get top N indices
        top_indices = np.argsort(final_scores)[::-1][:top_n]
        
        # Filter by minimum score
        top_indices = [
            idx for idx in top_indices 
            if final_scores[idx] >= Config.MIN_SIMILARITY_SCORE
        ]
        
        # Build recommendations
        df = self.course_manager.get_dataframe()
        recommendations = []
        
        for idx in top_indices:
            course = df.iloc[idx].to_dict()
            
            # Add recommendation metadata
            course['similarity_score'] = float(final_scores[idx])
            course['match_percentage'] = min(100, int(final_scores[idx] * 100))
            
            # Generate match reasons
            course['match_reasons'] = self.generate_match_reasons(
                course, 
                resume_analysis, 
                final_scores[idx]
            )
            
            recommendations.append(course)
        
        return recommendations
    
    def generate_match_reasons(
        self, 
        course: Dict, 
        resume_analysis: Dict, 
        score: float
    ) -> List[str]:
        """
        Generate human-readable reasons for the match
        
        Args:
            course: Course dictionary
            resume_analysis: Resume analysis
            score: Similarity score
            
        Returns:
            List of match reasons
        """
        reasons = []
        
        # Check skill matches
        course_text_lower = course['combined_text'].lower()
        matched_skills = [
            skill for skill in resume_analysis.get('skills', [])
            if skill.lower() in course_text_lower
        ]
        
        if matched_skills:
            reasons.append(f"Matches your skills: {', '.join(matched_skills[:5])}")
        
        # Check domain matches
        matched_domains = [
            domain for domain in resume_analysis.get('domains', [])
            if domain.replace('_', ' ') in course_text_lower
        ]
        
        if matched_domains:
            domain_names = [d.replace('_', ' ').title() for d in matched_domains]
            reasons.append(f"Aligns with your domain: {', '.join(domain_names)}")
        
        # High rating
        if course['course_rating'] >= 4.5:
            reasons.append(f"Highly rated ({course['course_rating']}/5)")
        
        # Popular course
        if course.get('Number_of_student_enrolled', 0) > 10000:
            reasons.append(f"Popular course with {int(course['Number_of_student_enrolled']):,} students")
        
        # Experience level match
        experience_keywords = {
            'beginner': ['beginner', 'introduction', 'fundamentals', 'basics', 'getting started'],
            'intermediate': ['intermediate', 'advanced', 'deep dive', 'mastering'],
            'advanced': ['advanced', 'expert', 'mastering', 'professional']
        }
        
        user_level = resume_analysis.get('experience_level', 'intermediate')
        level_keywords = experience_keywords.get(user_level, [])
        
        if any(keyword in course_text_lower for keyword in level_keywords):
            reasons.append(f"Suitable for {user_level} level")
        
        # If no specific reasons, give general one
        if not reasons:
            reasons.append("Good match based on your profile")
        
        return reasons[:3]  # Return top 3 reasons