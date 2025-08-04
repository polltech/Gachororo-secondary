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
from models import User, SchoolContent, NewsEvent, StaffMember, GalleryImage, ELearningResource

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'papers'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'gallery'), exist_ok=True)

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
        message = request.form.get('message')
        
        # In a real application, you would send an email or save to database
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    content = SchoolContent.query.first()
    return render_template('contact.html', content=content)

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
            mission='To provide quality education that empowers students to become responsible citizens and leaders.',
            vision='To be a leading institution of academic excellence and character formation.',
            motto='Knowledge, Character, Service',
            history='Gachororo Secondary School was established to serve the educational needs of our community.',
            achievements='Our students consistently perform well in KCSE examinations and excel in various co-curricular activities.',
            contact_address='Gachororo, Kenya',
            contact_phone='+254 700 000 000',
            contact_email='info@gachororo.ac.ke'
        )
        db.session.add(default_content)
        db.session.commit()
        print("Default school content created")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
