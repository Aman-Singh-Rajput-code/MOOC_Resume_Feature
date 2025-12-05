// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const resumeFile = document.getElementById('resumeFile');
const fileName = document.getElementById('fileName');
const uploadBtn = document.getElementById('uploadBtn');
const uploadSection = document.getElementById('uploadSection');
const loadingContainer = document.getElementById('loadingContainer');
const errorContainer = document.getElementById('errorContainer');
const errorMessage = document.getElementById('errorMessage');
const resultsSection = document.getElementById('resultsSection');

// File selection handler
resumeFile.addEventListener('change', function(e) {
    if (this.files && this.files[0]) {
        fileName.textContent = this.files[0].name;
    } else {
        fileName.textContent = 'Choose File';
    }
});

// Form submission handler
uploadForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Validate file selection
    if (!resumeFile.files || !resumeFile.files[0]) {
        showError('Please select a file to upload');
        return;
    }
    
    const file = resumeFile.files[0];
    
    // Validate file size (16MB = 16 * 1024 * 1024 bytes)
    if (file.size > 16 * 1024 * 1024) {
        showError('File size exceeds 16MB limit');
        return;
    }
    
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
    if (!allowedTypes.includes(file.type)) {
        showError('Invalid file type. Please upload a PDF or DOCX file');
        return;
    }
    
    // Show loading state
    showLoading();
    
    // Prepare form data
    const formData = new FormData();
    formData.append('resume', file);
    
    try {
        // Send request to server
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Show results
            displayResults(data);
        } else {
            // Show error
            showError(data.error || 'An error occurred while processing your resume');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to connect to server. Please try again.');
    }
});

// Show loading state
function showLoading() {
    uploadSection.style.display = 'none';
    errorContainer.style.display = 'none';
    resultsSection.style.display = 'none';
    loadingContainer.style.display = 'block';
}

// Show error message
function showError(message) {
    uploadSection.style.display = 'none';
    loadingContainer.style.display = 'none';
    resultsSection.style.display = 'none';
    errorContainer.style.display = 'block';
    errorMessage.textContent = message;
}

// Display results
function displayResults(data) {
    // Hide loading and errors
    uploadSection.style.display = 'none';
    loadingContainer.style.display = 'none';
    errorContainer.style.display = 'none';
    
    // Display analysis
    displayAnalysis(data.analysis);
    
    // Display recommendations
    displayRecommendations(data.recommendations);
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Display resume analysis
function displayAnalysis(analysis) {
    // Experience level
    document.getElementById('experienceLevel').textContent = analysis.experience_level;
    
    // Skill count
    document.getElementById('skillCount').textContent = analysis.skill_count;
    
    // Domains
    const domainsList = document.getElementById('domainsList');
    domainsList.innerHTML = '';
    if (analysis.domains && analysis.domains.length > 0) {
        analysis.domains.forEach(domain => {
            const tag = document.createElement('span');
            tag.className = 'domain-tag';
            tag.textContent = domain.replace('_', ' ').toUpperCase();
            domainsList.appendChild(tag);
        });
    } else {
        domainsList.innerHTML = '<span class="domain-tag">General</span>';
    }
    
    // Skills
    const skillsList = document.getElementById('skillsList');
    skillsList.innerHTML = '';
    if (analysis.skills && analysis.skills.length > 0) {
        analysis.skills.slice(0, 10).forEach(skill => {
            const tag = document.createElement('span');
            tag.className = 'skill-tag';
            tag.textContent = skill;
            skillsList.appendChild(tag);
        });
        
        if (analysis.skills.length > 10) {
            const moreTag = document.createElement('span');
            moreTag.className = 'skill-tag';
            moreTag.textContent = `+${analysis.skills.length - 10} more`;
            moreTag.style.background = '#667eea';
            moreTag.style.color = 'white';
            skillsList.appendChild(moreTag);
        }
    } else {
        skillsList.innerHTML = '<span class="skill-tag">No specific skills identified</span>';
    }
}

// Display recommendations
function displayRecommendations(recommendations) {
    const recCount = document.getElementById('recCount');
    const recommendationsList = document.getElementById('recommendationsList');
    
    recCount.textContent = recommendations.length;
    recommendationsList.innerHTML = '';
    
    if (recommendations.length === 0) {
        recommendationsList.innerHTML = '<p style="text-align: center; color: #666;">No recommendations found. Try uploading a more detailed resume.</p>';
        return;
    }
    
    recommendations.forEach((course, index) => {
        const courseCard = createCourseCard(course, index);
        recommendationsList.appendChild(courseCard);
    });
}

// Create course card element
function createCourseCard(course, index) {
    const card = document.createElement('div');
    card.className = 'course-card';
    card.style.animationDelay = `${index * 0.1}s`;
    
    // Generate rating stars
    const rating = course.rating || 0;
    const stars = '⭐'.repeat(Math.floor(rating)) + (rating % 1 >= 0.5 ? '⭐' : '');
    
    // Parse sources if it's a string
    let sourceLinks = '';
    if (course.sources) {
        let sources = course.sources;
        if (typeof sources === 'string') {
            try {
                sources = JSON.parse(sources.replace(/'/g, '"'));
            } catch (e) {
                sources = [sources];
            }
        }
        
        if (Array.isArray(sources) && sources.length > 0) {
            sourceLinks = `<a href="${sources[0]}" target="_blank" rel="noopener noreferrer" class="course-link">View Course →</a>`;
        }
    }
    
    card.innerHTML = `
        <div class="course-header">
            <div>
                <div class="course-title">${course.course_name}</div>
                <div style="color: #666; font-size: 0.9rem; margin-top: 5px;">
                    by ${course.instructor}
                </div>
            </div>
            <div class="match-badge">${course.match_percentage}% Match</div>
        </div>
        
        <div class="course-meta">
            <div class="meta-item">
                <span class="meta-icon rating-stars">${stars}</span>
                <span>${rating.toFixed(1)}</span>
            </div>
            <div class="meta-item">
                <span class="meta-icon">🏢</span>
                <span>${course.platform}</span>
            </div>
            <div class="meta-item">
                <span class="meta-icon">${course.is_paid === 'Paid' ? '💰' : '🆓'}</span>
                <span>${course.is_paid}</span>
            </div>
            ${course.enrolled > 0 ? `
            <div class="meta-item">
                <span class="meta-icon">👥</span>
                <span>${formatNumber(course.enrolled)} students</span>
            </div>
            ` : ''}
        </div>
        
        ${course.match_reasons && course.match_reasons.length > 0 ? `
        <div class="course-reasons">
            <div class="reason-title">Why this course?</div>
            ${course.match_reasons.map(reason => `
                <div class="reason-item">${reason}</div>
            `).join('')}
        </div>
        ` : ''}
        
        ${sourceLinks}
    `;
    
    return card;
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Reset form and go back to upload
function resetForm() {
    uploadForm.reset();
    fileName.textContent = 'Choose File';
    uploadSection.style.display = 'block';
    loadingContainer.style.display = 'none';
    errorContainer.style.display = 'none';
    resultsSection.style.display = 'none';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}