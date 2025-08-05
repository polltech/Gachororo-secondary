import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


from dotenv import load_dotenv
load_dotenv() 

# Configure logging
logging.basicConfig(level=logging.DEBUG)
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gachororo_school.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models after db is initialized
from models import User, SchoolContent, NewsEvent, StaffMember, GalleryImage, ELearningResource, SiteSettings, ThemeSettings, VideoSettings

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processor for global variables
@app.context_processor
def inject_global_vars():
    try:
        # Get current theme
        current_theme = ThemeSettings.query.filter_by(is_active=True).first()
        theme_name = current_theme.theme_name if current_theme else 'blue'
        # Get active video
        active_video = VideoSettings.query.filter_by(is_active=True).first()
        return {
            'current_theme': theme_name,
            'active_video': active_video
        }
    except:
        # Tables might not exist yet
        return {
            'current_theme': 'blue',
            'active_video': None
        }

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'papers'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'gallery'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'background_videos'), exist_ok=True)

def allowed_file(filename, file_type):
    if file_type == 'image':
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    elif file_type == 'document':
        allowed_extensions = {'pdf', 'doc', 'docx'}
    elif file_type == 'video':
        allowed_extensions = {'mp4', 'avi', 'mov', 'wmv'}
    else:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Email sending function
def send_email(name, email, subject, message):
    """
    Send email using Gmail SMTP
    """
    try:
        # Email configuration - you'll need to set these in environment variables
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.environ.get("EMAIL_ADDRESS")  # Your Gmail address
        sender_password = os.environ.get("EMAIL_PASSWORD")  # App password, not regular password
        if not sender_email or not sender_password:
            print("Email configuration missing. Please set EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.")
            return False
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email  # Send to yourself
        msg['Subject'] = f"Contact Form Submission from {name} - {subject}"
        # Email body
        body = f"""
        You have received a new message from your website contact form.
        Name: {name}
        Email: {email}
        Subject: {subject}
        Message:
        {message}
        Sent from: {request.remote_addr}
        """
        msg.attach(MIMEText(body, 'plain'))
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, sender_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

# Public Routes
@app.route('/')
def index():
    content = SchoolContent.query.first()
    recent_news = NewsEvent.query.filter_by(type='news').order_by(NewsEvent.date_created.desc()).limit(3).all()
    upcoming_events = NewsEvent.query.filter_by(type='event').order_by(NewsEvent.date_created.desc()).limit(3).all()
    gallery_images = GalleryImage.query.order_by(GalleryImage.date_uploaded.desc()).limit(6).all()
    return render_template('index.html', 
                         content=content, 
                         recent_news=recent_news,
                         upcoming_events=upcoming_events,
                         gallery_images=gallery_images)

@app.route('/about')
def about():
    content = SchoolContent.query.first()
    staff_members = StaffMember.query.all()
    return render_template('about.html', content=content, staff_members=staff_members)

@app.route('/gallery')
def gallery():
    images = GalleryImage.query.order_by(GalleryImage.date_uploaded.desc()).all()
    return render_template('gallery.html', images=images)

@app.route('/news')
def news():
    news_items = NewsEvent.query.filter_by(type='news').order_by(NewsEvent.date_created.desc()).all()
    events = NewsEvent.query.filter_by(type='event').order_by(NewsEvent.date_created.desc()).all()
    return render_template('news.html', news_items=news_items, events=events)

@app.route('/achievements')
def achievements():
    content = SchoolContent.query.first()
    return render_template('achievements.html', content=content)

@app.route('/elearning')
def elearning():
    # Get all forms and subjects for filtering
    forms = ['Form 1', 'Form 2', 'Form 3', 'Form 4']
    subjects = ['Mathematics', 'English', 'Kiswahili', 'Biology', 'Chemistry', 'Physics', 
                'History', 'Geography', 'CRE', 'Business Studies', 'Agriculture']
    # Get filter parameters
    selected_form = request.args.get('form', '')
    selected_subject = request.args.get('subject', '')
    # Build query
    query = ELearningResource.query
    if selected_form:
        query = query.filter_by(form=selected_form)
    if selected_subject:
        query = query.filter_by(subject=selected_subject)
    resources = query.order_by(ELearningResource.date_uploaded.desc()).all()
    return render_template('elearning.html', 
                         resources=resources,
                         forms=forms,
                         subjects=subjects,
                         selected_form=selected_form,
                         selected_subject=selected_subject)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        # Validate form data
        if not name or not email or not message:
            flash('All fields are required.', 'error')
            return redirect(url_for('contact'))
        # Send email
        if send_email(name, email, subject, message):
            flash('Thank you for your message! We will get back to you soon.', 'success')
        else:
            flash('There was an error sending your message. Please try again.', 'error')
        return redirect(url_for('contact'))
    content = SchoolContent.query.first()
    return render_template('contact.html', content=content)

@app.route('/ai-tutor', methods=['GET', 'POST'])
def ai_tutor():
    if request.method == 'POST':
        try:
            import json
            from google import genai
            from google.genai import types
            import base64
            from io import BytesIO
            
            # Get Gemini API key from settings
            api_key_setting = SiteSettings.query.filter_by(setting_name='gemini_api_key').first()
            if not api_key_setting or not api_key_setting.setting_value:
                return {'error': 'Gemini API key not configured. Please contact administrator.'}, 400
            
            client = genai.Client(api_key=api_key_setting.setting_value)
            user_question = request.form.get('question')
            if not user_question:
                return {'error': 'Please enter a question.'}, 400
            
            # Enhanced educational context prompt with exam generation capability
            system_prompt = (
                "You are an expert AI tutor for Gachororo Secondary School students. "
                "Provide detailed, step-by-step explanations for educational topics. "
                "Focus on secondary school curriculum topics including Mathematics, "
                "English, Kiswahili, Sciences (Biology, Chemistry, Physics), Social Studies, "
                "and other subjects. "
                "Keep responses clear, educational, and suitable for secondary school students. "
                "When explaining complex concepts, break them down into manageable steps. "
                "Always maintain a patient, encouraging teaching tone. "
                "If a question is not educational, politely redirect to school topics. "
                "When asked to solve problems, show each step clearly with explanations. "
                "Use examples relevant to Kenyan secondary school curriculum. "
                "Include practical applications where possible. "
                "Be thorough but concise in your explanations. "
                "Format responses with clear headings and bullet points where appropriate. "
                "When explaining processes or procedures, use numbered lists for steps. "
                "When explaining concepts that would benefit from visual aids, "
                "generate images that would help illustrate the concept. "
                "If a user specifically asks to generate an exam, create a complete exam "
                "in a printable format with clear question layout and formatting. "
                "For exam generation, provide questions in a clear format with options where applicable. "
                "When generating images, ensure they are educational and appropriate for school use. "
                "Make responses easily copyable by avoiding special characters that might cause issues. "
                "When creating exam images, make them professional, readable, and suitable for printing. "
                "Ensure all text is formatted for easy copying and pasting without formatting issues. "
                "Remove any special characters or formatting that might interfere with copying. "
                "Keep text clean and readable for students to copy directly into their notes. "
            )
            
            # Handle image upload if present
            contents = []
            uploaded_image_data = None
            uploaded_image_type = None
            
            if 'image' in request.files and request.files['image'].filename:
                image_file = request.files['image']
                if allowed_file(image_file.filename, 'image'):
                    image_bytes = image_file.read()
                    uploaded_image_data = image_bytes
                    uploaded_image_type = f"image/{image_file.filename.rsplit('.', 1)[1].lower()}"
                    contents.append(
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type=uploaded_image_type
                        )
                    )
            
            # Add user question
            contents.append(types.Part(text=user_question))
            
            # Check if user is requesting exam generation
            user_question_lower = user_question.lower()
            exam_indicators = [
                'generate exam', 'create exam', 'exam questions', 'exam paper', 
                'past paper', 'practice exam', 'sample exam', 'exam preparation'
            ]
            
            should_generate_exam = any(indicator in user_question_lower for indicator in exam_indicators)
            
            # Check if user is requesting image generation
            image_request_indicators = [
                'draw', 'illustrate', 'show me', 'visualize', 'create image', 
                'generate image', 'picture', 'diagram', 'chart', 'graph',
                'explain with', 'show diagram', 'visual explanation'
            ]
            
            should_generate_image = any(indicator in user_question_lower for indicator in image_request_indicators)
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=contents)
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7
                )
            )
            
            # Process response
            response_text = response.text if response.text else 'Sorry, I could not generate a response.'
            
            # Generate image if requested
            generated_image_data = None
            image_description = None
            
            if should_generate_image or should_generate_exam:
                try:
                    # Create a specific prompt for image generation
                    if should_generate_exam:
                        image_prompt = f"Generate a professional educational exam paper image for: {user_question}. "
                        image_prompt += "This should be suitable for Gachororo Secondary School students. "
                        image_prompt += "Include a clear exam header with subject, form, and title. "
                        image_prompt += "Format questions in a clean, readable layout. "
                        image_prompt += "Make it suitable for printing and copying. "
                        image_prompt += "Include space for students to write answers. "
                        image_prompt += "Use a clean, educational design appropriate for secondary school level."
                    else:
                        image_prompt = f"Generate an educational illustration for: {user_question}. "
                        image_prompt += "This should be suitable for Gachororo Secondary School students. "
                        image_prompt += "Make it clear, educational, and appropriate for the curriculum. "
                        image_prompt += "Design should be professional and suitable for educational use."
                    
                    # Generate image using Gemini's multimodal capabilities
                    image_response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[
                            types.Content(
                                role="user",
                                parts=[types.Part(text=image_prompt)]
                            )
                        ]
                    )
                    
                    # Extract image data from response
                    if hasattr(image_response, 'parts') and image_response.parts:
                        # Look through all parts to find image data
                        for part in image_response.parts:
                            if hasattr(part, 'data') and part.data:
                                generated_image_data = part.data
                                break
                            # Also check for text responses that might indicate success/failure
                            elif hasattr(part, 'text') and part.text:
                                print(f"Image generation returned text: {part.text}")
                    
                except Exception as img_error:
                    print(f"Image generation failed: {img_error}")
                    # Continue with text response
            
            # Enhanced response structure with exam-specific handling
            formatted_response = {
                'response': response_text,
                'type': 'explanation',
                'timestamp': datetime.now().isoformat(),
                'has_uploaded_image': bool(uploaded_image_data),
                'has_generated_image': bool(generated_image_data),
                'uploaded_image_type': uploaded_image_type,
                'uploaded_image_data': base64.b64encode(uploaded_image_data).decode('utf-8') if uploaded_image_data else None,
                'generated_image_data': base64.b64encode(generated_image_data).decode('utf-8') if generated_image_data else None,
                'is_exam': should_generate_exam,
                'original_question': user_question
            }
            
            return formatted_response
            
        except Exception as e:
            return {'error': f'Error processing request: {str(e)}'}, 500
    
    return render_template('ai_tutor.html')

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.password_hash and password and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Admin Dashboard Routes
@app.route('/dashboard')
@login_required
def dashboard():
    # Get statistics
    total_news = NewsEvent.query.filter_by(type='news').count()
    total_events = NewsEvent.query.filter_by(type='event').count()
    total_staff = StaffMember.query.count()
    total_gallery = GalleryImage.query.count()
    total_resources = ELearningResource.query.count()
    recent_news = NewsEvent.query.order_by(NewsEvent.date_created.desc()).limit(5).all()
    return render_template('dashboard.html',
                         total_news=total_news,
                         total_events=total_events,
                         total_staff=total_staff,
                         total_gallery=total_gallery,
                         total_resources=total_resources,
                         recent_news=recent_news)

@app.route('/admin/manage-content', methods=['GET', 'POST'])
@login_required
def manage_content():
    content = SchoolContent.query.first()
    if request.method == 'POST':
        if not content:
            content = SchoolContent()
            db.session.add(content)
        content.school_name = request.form.get('school_name', 'Gachororo Secondary School')
        content.principal_message = request.form.get('principal_message', '')
        content.mission = request.form.get('mission', '')
        content.vision = request.form.get('vision', '')
        content.motto = request.form.get('motto', '')
        content.history = request.form.get('history', '')
        content.achievements = request.form.get('achievements', '')
        content.contact_address = request.form.get('contact_address', '')
        content.contact_phone = request.form.get('contact_phone', '')
        content.contact_email = request.form.get('contact_email', '')
        db.session.commit()
        flash('Content updated successfully!', 'success')
        return redirect(url_for('manage_content'))
    return render_template('admin/manage_content.html', content=content)

@app.route('/admin/manage-home', methods=['GET', 'POST'])
@login_required
def manage_home():
    content = SchoolContent.query.first()
    if not content:
        content = SchoolContent()
        db.session.add(content)
        db.session.commit()
    if request.method == 'POST':
        content.principal_message = request.form.get('principal_message', '')
        content.mission = request.form.get('mission', '')
        content.vision = request.form.get('vision', '')
        content.motto = request.form.get('motto', '')
        content.history = request.form.get('history', '')
        db.session.commit()
        flash('Home page content updated successfully!', 'success')
        return redirect(url_for('manage_home'))
    return render_template('admin/manage_home.html', content=content)

@app.route('/admin/manage-achievements', methods=['GET', 'POST'])
@login_required
def manage_achievements():
    content = SchoolContent.query.first()
    if not content:
        content = SchoolContent()
        db.session.add(content)
        db.session.commit()
    if request.method == 'POST':
        content.achievements = request.form.get('achievements', '')
        db.session.commit()
        flash('Achievements updated successfully!', 'success')
        return redirect(url_for('manage_achievements'))
    return render_template('admin/manage_achievements.html', content=content)

@app.route('/admin/manage-gallery', methods=['GET', 'POST'])
@login_required
def manage_gallery():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'error')
            return redirect(request.url)
        file = request.files['file']
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        if file and file.filename and allowed_file(file.filename, 'image'):
            filename = secure_filename(file.filename)
            # Add timestamp to prevent conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'gallery', filename))
            gallery_image = GalleryImage(
                filename=filename,
                title=title,
                description=description
            )
            db.session.add(gallery_image)
            db.session.commit()
            flash('Image uploaded successfully!', 'success')
        else:
            flash('Invalid file type. Please upload an image.', 'error')
    images = GalleryImage.query.order_by(GalleryImage.date_uploaded.desc()).all()
    return render_template('admin/manage_gallery.html', images=images)

@app.route('/admin/delete-gallery/<int:image_id>')
@login_required
def delete_gallery_image(image_id):
    image = GalleryImage.query.get_or_404(image_id)
    # Delete file from filesystem
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'gallery', image.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('manage_gallery'))

@app.route('/admin/manage-news', methods=['GET', 'POST'])
@login_required
def manage_news():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        news_type = request.form.get('type', 'news')
        news_event = NewsEvent(
            title=title,
            content=content,
            type=news_type
        )
        db.session.add(news_event)
        db.session.commit()
        flash(f'{news_type.title()} created successfully!', 'success')
        return redirect(url_for('manage_news'))
    news_items = NewsEvent.query.order_by(NewsEvent.date_created.desc()).all()
    return render_template('admin/manage_news.html', news_items=news_items)

@app.route('/admin/delete-news/<int:news_id>')
@login_required
def delete_news(news_id):
    news_item = NewsEvent.query.get_or_404(news_id)
    db.session.delete(news_item)
    db.session.commit()
    flash('News/Event deleted successfully!', 'success')
    return redirect(url_for('manage_news'))

@app.route('/admin/manage-staff', methods=['GET', 'POST'])
@login_required
def manage_staff():
    if request.method == 'POST':
        name = request.form.get('name')
        position = request.form.get('position')
        qualifications = request.form.get('qualifications', '')
        subjects = request.form.get('subjects', '')
        # Handle file upload
        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename, 'image'):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                photo_filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'gallery', photo_filename))
        staff_member = StaffMember(
            name=name,
            position=position,
            qualifications=qualifications,
            subjects=subjects,
            photo_filename=photo_filename
        )
        db.session.add(staff_member)
        db.session.commit()
        flash('Staff member added successfully!', 'success')
        return redirect(url_for('manage_staff'))
    staff_members = StaffMember.query.all()
    return render_template('admin/manage_staff.html', staff_members=staff_members)

@app.route('/admin/delete-staff/<int:staff_id>')
@login_required
def delete_staff(staff_id):
    staff_member = StaffMember.query.get_or_404(staff_id)
    # Delete photo if exists
    if staff_member.photo_filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'gallery', staff_member.photo_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(staff_member)
    db.session.commit()
    flash('Staff member deleted successfully!', 'success')
    return redirect(url_for('manage_staff'))

@app.route('/admin/manage-elearning', methods=['GET', 'POST'])
@login_required
def manage_elearning():
    if request.method == 'POST':
        title = request.form.get('title')
        form = request.form.get('form')
        subject = request.form.get('subject')
        description = request.form.get('description', '')
        resource_type = request.form.get('resource_type')
        filename = None
        youtube_url = None
        if resource_type == 'file':
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename and (allowed_file(file.filename, 'document') or allowed_file(file.filename, 'video')):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    # Save to appropriate folder
                    if allowed_file(file.filename, 'document'):
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'papers', filename))
                    else:
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename))
        elif resource_type == 'youtube':
            youtube_url = request.form.get('youtube_url')
        resource = ELearningResource(
            title=title,
            form=form,
            subject=subject,
            description=description,
            resource_type=resource_type,
            filename=filename,
            youtube_url=youtube_url
        )
        db.session.add(resource)
        db.session.commit()
        flash('E-learning resource added successfully!', 'success')
        return redirect(url_for('manage_elearning'))
    resources = ELearningResource.query.order_by(ELearningResource.date_uploaded.desc()).all()
    forms = ['Form 1', 'Form 2', 'Form 3', 'Form 4']
    subjects = ['Mathematics', 'English', 'Kiswahili', 'Biology', 'Chemistry', 'Physics', 
                'History', 'Geography', 'CRE', 'Business Studies', 'Agriculture']
    return render_template('admin/manage_elearning.html', 
                         resources=resources, 
                         forms=forms, 
                         subjects=subjects)

@app.route('/admin/delete-elearning/<int:resource_id>')
@login_required
def delete_elearning(resource_id):
    resource = ELearningResource.query.get_or_404(resource_id)
    # Delete file if exists
    if resource.filename:
        if resource.resource_type == 'document':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'papers', resource.filename)
        else:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', resource.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(resource)
    db.session.commit()
    flash('E-learning resource deleted successfully!', 'success')
    return redirect(url_for('manage_elearning'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if request.method == 'POST':
        new_email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        if not current_user.password_hash or not current_password or not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('admin_settings'))
        current_user.email = new_email
        if new_password:
            current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Admin settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))
    return render_template('admin/admin_settings.html')

@app.route('/admin/theme-settings', methods=['GET', 'POST'])
@login_required
def admin_theme_settings():
    if request.method == 'POST':
        selected_theme = request.form.get('theme')
        # Deactivate all themes
        ThemeSettings.query.update({'is_active': False})
        # Activate selected theme or create new one
        theme = ThemeSettings.query.filter_by(theme_name=selected_theme).first()
        if not theme:
            theme = ThemeSettings(theme_name=selected_theme, is_active=True)
            db.session.add(theme)
        else:
            theme.is_active = True
        db.session.commit()
        flash(f'Theme changed to {selected_theme.title()}!', 'success')
        return redirect(url_for('admin_theme_settings'))
    current_theme = ThemeSettings.query.filter_by(is_active=True).first()
    themes = ['blue', 'red', 'gray']
    return render_template('admin/theme_settings.html', 
                         current_theme=current_theme, 
                         themes=themes)

@app.route('/admin/video-settings', methods=['GET', 'POST'])
@login_required
def admin_video_settings():
    if request.method == 'POST':
        if 'video_file' in request.files:
            file = request.files['video_file']
            title = request.form.get('title', '')
            if file and file.filename and allowed_file(file.filename, 'video'):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'background_videos', filename))
                # Deactivate all current videos
                VideoSettings.query.update({'is_active': False})
                # Create new video setting
                video_setting = VideoSettings(
                    video_filename=filename,
                    video_title=title,
                    is_active=True
                )
                db.session.add(video_setting)
                db.session.commit()
                flash('Background video updated successfully!', 'success')
            else:
                flash('Invalid video file. Please upload MP4, AVI, MOV, or WMV files.', 'error')
        elif 'deactivate_video' in request.form:
            VideoSettings.query.update({'is_active': False})
            db.session.commit()
            flash('Background video disabled.', 'info')
    active_video = VideoSettings.query.filter_by(is_active=True).first()
    all_videos = VideoSettings.query.order_by(VideoSettings.date_uploaded.desc()).all()
    return render_template('admin/video_settings.html', 
                         active_video=active_video, 
                         all_videos=all_videos)

@app.route('/admin/site-settings', methods=['GET', 'POST'])
@login_required
def admin_site_settings():
    if request.method == 'POST':
        gemini_api_key = request.form.get('gemini_api_key')
        # Update or create Gemini API key setting
        setting = SiteSettings.query.filter_by(setting_name='gemini_api_key').first()
        if not setting:
            setting = SiteSettings(setting_name='gemini_api_key', setting_value=gemini_api_key)
            db.session.add(setting)
        else:
            setting.setting_value = gemini_api_key
        db.session.commit()
        flash('Site settings updated successfully!', 'success')
        return redirect(url_for('admin_site_settings'))
    gemini_setting = SiteSettings.query.filter_by(setting_name='gemini_api_key').first()
    return render_template('admin/site_settings.html', 
                         gemini_api_key=gemini_setting.setting_value if gemini_setting else '')

@app.route('/admin/activate-video/<int:video_id>')
@login_required
def activate_video(video_id):
    # Deactivate all videos
    VideoSettings.query.update({'is_active': False})
    # Activate selected video
    video = VideoSettings.query.get_or_404(video_id)
    video.is_active = True
    db.session.commit()
    flash(f'Video "{video.video_title}" activated!', 'success')
    return redirect(url_for('admin_video_settings'))

@app.route('/admin/delete-video/<int:video_id>')
@login_required
def delete_video(video_id):
    video = VideoSettings.query.get_or_404(video_id)
    # Delete file from filesystem
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'background_videos', video.video_filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(video)
    db.session.commit()
    flash('Video deleted successfully!', 'success')
    return redirect(url_for('admin_video_settings'))

# File serving routes
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/uploads/gallery/<filename>')
def gallery_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'gallery'), filename)

@app.route('/uploads/papers/<filename>')
def papers_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'papers'), filename)

@app.route('/uploads/videos/<filename>')
def videos_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), filename)

@app.route('/uploads/background_videos/<filename>')
def background_video_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'background_videos'), filename)

@app.route('/elearning/view/<int:resource_id>')
def view_elearning_resource(resource_id):
    resource = ELearningResource.query.get_or_404(resource_id)
    if resource.resource_type == 'file' and resource.filename:
        # Determine file path based on type
        if allowed_file(resource.filename, 'document'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'papers', resource.filename)
            folder = 'papers'
        else:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', resource.filename)
            folder = 'videos'
        if os.path.exists(file_path):
            return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], folder), resource.filename)
    flash('File not found.', 'error')
    return redirect(url_for('elearning'))

@app.route('/elearning/download/<int:resource_id>')
def download_elearning_resource(resource_id):
    resource = ELearningResource.query.get_or_404(resource_id)
    if resource.resource_type == 'file' and resource.filename:
        # Determine file path based on type
        if allowed_file(resource.filename, 'document'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'papers', resource.filename)
            folder = 'papers'
        else:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', resource.filename)
            folder = 'videos'
        if os.path.exists(file_path):
            return send_from_directory(
                os.path.join(app.config['UPLOAD_FOLDER'], folder), 
                resource.filename, 
                as_attachment=True,
                download_name=f"{resource.title}_{resource.filename}"
            )
    flash('File not found.', 'error')
    return redirect(url_for('elearning'))

# Initialize database and create default admin user
with app.app_context():
    db.create_all()
    # Create default admin user if it doesn't exist
    admin_user = User.query.filter_by(email='paulmunywoki086@gmail.com').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='paulmunywoki086@gmail.com',
            password_hash=generate_password_hash('Antananarivo')
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created: paulmunywoki086@gmail.com / Antananarivo")
    # Create default school content if it doesn't exist
    default_content = SchoolContent.query.first()
    if not default_content:
        default_content = SchoolContent(
            school_name='Gachororo Secondary School',
            principal_message='Welcome to Gachororo Secondary School, where excellence in education meets character development.',
            mission='   TO PROVIDE A FAVOURABLE LEARNING ENVIRONMENT WHERE INDIVIDUAL TALENT CAN BE INDETIFIED, EXPLOITED, AND IMPROVED.',
            vision='TO BE A MODEL SCHOOL OF PRODUCING ALL-ROUND INDIVIDUALS WHO CAN ADAPT TO A CHANGING WORLD.',
            motto='Knowledge Is Power',
            history=' Gachororo Secondary School was established with a vision to provide quality education to the students in our community. Since our founding, we have been committed  academic excellence, character development, and preparing our students for success in their future endeavors.',
            achievements='Our students consistently perform well in KCSE examinations and excel in various co-curricular activities.',
            contact_address='Juja Gachororo,kiambu County Kenya',
            contact_phone='+254 715802318',
            contact_email='Ggachororossc@gmail.com'
        )
        db.session.add(default_content)
        db.session.commit()
        print("Default school content created")
    # Create default theme setting if it doesn't exist
    default_theme = ThemeSettings.query.first()
    if not default_theme:
        default_theme = ThemeSettings(
            theme_name='blue',
            is_active=True
        )
        db.session.add(default_theme)
        db.session.commit()
        print("Default theme setting created")
    # Create default Gemini API key setting if it doesn't exist
    gemini_setting = SiteSettings.query.filter_by(setting_name='gemini_api_key').first()
    if not gemini_setting:
        gemini_setting = SiteSettings(
            setting_name='gemini_api_key',
            setting_value=''
        )
        db.session.add(gemini_setting)
        db.session.commit()
        print("Default Gemini API key setting created")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)