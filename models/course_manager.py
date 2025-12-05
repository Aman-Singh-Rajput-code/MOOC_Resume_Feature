import pandas as pd
import ast
from typing import List, Dict, Optional
from config import Config

class CourseManager:
    """Manage course data loaded from CSV"""
    
    def __init__(self, csv_path: str = None):
        """
        Initialize course manager and load data
        
        Args:
            csv_path: Path to the CSV file (defaults to config setting)
        """
        self.csv_path = csv_path or Config.DATASET_PATH
        self.df = None
        self.courses = []
        self.load_courses()
    
    def load_courses(self):
        """Load courses from CSV file into memory"""
        try:
            self.df = pd.read_csv(self.csv_path)
            print(f"Loaded {len(self.df)} courses from {self.csv_path}")
            
            # Process the dataframe
            self.process_dataframe()
            
            # Convert to list of dictionaries for easier access
            self.courses = self.df.to_dict('records')
            
        except FileNotFoundError:
            print(f"Error: Dataset file not found at {self.csv_path}")
            self.df = pd.DataFrame()
            self.courses = []
        except Exception as e:
            print(f"Error loading courses: {str(e)}")
            self.df = pd.DataFrame()
            self.courses = []
    
    def process_dataframe(self):
        """Process and clean the dataframe"""
        # Handle missing values
        self.df['course_rating'] = pd.to_numeric(self.df['course_rating'], errors='coerce').fillna(0)
        self.df['Number_of_student_enrolled'] = pd.to_numeric(
            self.df['Number_of_student_enrolled'], 
            errors='coerce'
        ).fillna(0)
        
        # Fill missing text fields
        self.df['course_name'] = self.df['course_name'].fillna('')
        self.df['instructor'] = self.df['instructor'].fillna('Unknown')
        self.df['is_paid'] = self.df['is_paid'].fillna('Unknown')
        self.df['platform'] = self.df['platform'].fillna('Unknown')
        
        # Process user_comments if it's a string representation of a list
        if 'user_comments' in self.df.columns:
            self.df['user_comments'] = self.df['user_comments'].apply(self.parse_list_field)
            # Join comments into single text for analysis
            self.df['comments_text'] = self.df['user_comments'].apply(
                lambda x: ' '.join(x) if isinstance(x, list) else ''
            )
        else:
            self.df['comments_text'] = ''
        
        # Create combined text field for matching
        self.df['combined_text'] = (
            self.df['course_name'].astype(str) + ' ' +
            self.df['instructor'].astype(str) + ' ' +
            self.df['comments_text'].astype(str)
        )
        
        # Add popularity score (normalized enrollment)
        max_enrollment = self.df['Number_of_student_enrolled'].max()
        if max_enrollment > 0:
            self.df['popularity_score'] = self.df['Number_of_student_enrolled'] / max_enrollment
        else:
            self.df['popularity_score'] = 0
    
    @staticmethod
    def parse_list_field(field):
        """Parse string representation of list into actual list"""
        if pd.isna(field):
            return []
        if isinstance(field, list):
            return field
        if isinstance(field, str):
            try:
                # Try to parse as Python literal
                parsed = ast.literal_eval(field)
                if isinstance(parsed, list):
                    return parsed
            except:
                pass
            # If parsing fails, return as single-item list
            return [field] if field else []
        return []
    
    def get_all_courses(self) -> List[Dict]:
        """Get all courses as list of dictionaries"""
        return self.courses
    
    def get_course_by_id(self, course_id: str) -> Optional[Dict]:
        """
        Get a specific course by ID
        
        Args:
            course_id: Course identifier
            
        Returns:
            Course dictionary or None
        """
        matching = self.df[self.df['course_id'] == course_id]
        if not matching.empty:
            return matching.iloc[0].to_dict()
        return None
    
    def search_courses(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Simple text search in course names
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching courses
        """
        query_lower = query.lower()
        matching = self.df[
            self.df['course_name'].str.lower().str.contains(query_lower, na=False)
        ]
        return matching.head(limit).to_dict('records')
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get the raw dataframe"""
        return self.df
    
    def get_statistics(self) -> Dict:
        """Get statistics about the course dataset"""
        return {
            'total_courses': len(self.df),
            'platforms': self.df['platform'].unique().tolist(),
            'avg_rating': float(self.df['course_rating'].mean()),
            'paid_courses': int(self.df[self.df['is_paid'] == 'Paid'].shape[0]),
            'free_courses': int(self.df[self.df['is_paid'] == 'Free'].shape[0]),
        }