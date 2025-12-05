import os

class Config:
    """Configuration settings for the application"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # File upload settings
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
    
    # Dataset settings
    DATASET_PATH = 'data/output.csv'
    
    # Recommendation settings
    TOP_N_RECOMMENDATIONS = 10
    MIN_SIMILARITY_SCORE = 0.1  # Minimum similarity score to show a recommendation
    
    # NLP settings
    SPACY_MODEL = 'en_core_web_sm'
    
    # Skills database - common technical skills to look for in resumes
    TECHNICAL_SKILLS = [
        # Programming Languages
        'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
        'go', 'rust', 'typescript', 'scala', 'r', 'matlab', 'sql', 'html', 'css',
        
        # Frameworks & Libraries
        'react', 'angular', 'vue', 'django', 'flask', 'spring', 'nodejs', 'express',
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'nlp', 'natural language processing',
        'computer vision', 'data science', 'data analysis', 'statistics',
        'artificial intelligence', 'neural networks', 'ai',
        
        # Databases
        'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sql server',
        'cassandra', 'dynamodb', 'firebase',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
        'ci/cd', 'devops', 'terraform', 'ansible',
        
        # Web Technologies
        'rest api', 'graphql', 'microservices', 'web development', 'frontend',
        'backend', 'full stack', 'responsive design',
        
        # Tools & Platforms
        'tableau', 'power bi', 'excel', 'jupyter', 'linux', 'windows', 'macos',
        'agile', 'scrum', 'jira',
        
        # Other domains
        'blockchain', 'cybersecurity', 'iot', 'mobile development', 'game development',
        'embedded systems', 'networking', 'cloud computing'
    ]
    
    # Domain categories for classification
    DOMAIN_KEYWORDS = {
        'data_science': ['data science', 'machine learning', 'deep learning', 'ai', 
                        'statistics', 'data analysis', 'analytics'],
        'web_development': ['web development', 'frontend', 'backend', 'full stack',
                           'html', 'css', 'javascript', 'react', 'angular'],
        'mobile_development': ['mobile', 'android', 'ios', 'swift', 'kotlin', 'react native'],
        'cloud_computing': ['aws', 'azure', 'gcp', 'cloud', 'devops', 'docker', 'kubernetes'],
        'database': ['database', 'sql', 'mysql', 'postgresql', 'mongodb', 'data modeling'],
        'cybersecurity': ['security', 'cybersecurity', 'encryption', 'penetration testing'],
        'nlp': ['nlp', 'natural language processing', 'text mining', 'linguistics'],
    }