from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from werkzeug.utils import secure_filename
from config import Config
from models.course_manager import CourseManager
from models.resume_processor import ResumeProcessor
from models.recommendation_engine import RecommendationEngine

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components (loaded once at startup)
print("Loading course data...")
course_manager = CourseManager()
print("Initializing resume processor...")
resume_processor = ResumeProcessor()
print("Initializing recommendation engine...")
recommendation_engine = RecommendationEngine(course_manager)
print("Application ready!")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Home page with upload form"""
    stats = course_manager.get_statistics()
    return render_template('index.html', stats=stats)

@app.route('/upload', methods=['POST'])
def upload_resume():
    """Handle resume upload and processing"""
    
    # Check if file is present
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload PDF or DOCX'}), 400
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process resume
        analysis = resume_processor.process_resume(filepath)
        
        if not analysis:
            # Clean up file
            os.remove(filepath)
            return jsonify({'error': 'Failed to process resume. Please ensure it is a valid PDF or DOCX file'}), 400
        
        # Generate recommendations
        recommendations = recommendation_engine.get_recommendations(analysis)
        
        # Clean up uploaded file (for privacy/security)
        os.remove(filepath)
        
        # Prepare response
        response_data = {
            'success': True,
            'analysis': {
                'skills': analysis['skills'][:20],  # Limit to 20 for display
                'skill_count': analysis['skill_count'],
                'experience_level': analysis['experience_level'],
                'domains': analysis['domains'],
                'education': analysis['education']
            },
            'recommendations': format_recommendations(recommendations),
            'total_recommendations': len(recommendations)
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        # Clean up file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        
        print(f"Error processing resume: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

def format_recommendations(recommendations):
    """Format recommendations for frontend display"""
    formatted = []
    
    for rec in recommendations:
        formatted.append({
            'course_id': rec.get('course_id', ''),
            'course_name': rec.get('course_name', 'Unknown Course'),
            'instructor': rec.get('instructor', 'Unknown'),
            'rating': rec.get('course_rating', 0),
            'platform': rec.get('platform', 'Unknown'),
            'is_paid': rec.get('is_paid', 'Unknown'),
            'enrolled': int(rec.get('Number_of_student_enrolled', 0)),
            'match_percentage': rec.get('match_percentage', 0),
            'match_reasons': rec.get('match_reasons', []),
            'sources': rec.get('sources', [])
        })
    
    return formatted

@app.route('/api/courses')
def get_courses():
    """API endpoint to get all courses"""
    courses = course_manager.get_all_courses()
    return jsonify({'courses': courses, 'total': len(courses)})

@app.route('/api/course/<course_id>')
def get_course(course_id):
    """API endpoint to get specific course"""
    course = course_manager.get_course_by_id(course_id)
    if course:
        return jsonify(course)
    return jsonify({'error': 'Course not found'}), 404

@app.route('/api/search')
def search_courses():
    """API endpoint to search courses"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    
    results = course_manager.search_courses(query, limit)
    return jsonify({'results': results, 'total': len(results)})

@app.route('/api/stats')
def get_stats():
    """API endpoint to get dataset statistics"""
    stats = course_manager.get_statistics()
    return jsonify(stats)

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)