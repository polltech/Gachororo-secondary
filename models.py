from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

class SchoolContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(200), default='Gachororo Secondary School')
    principal_message = db.Column(db.Text)
    mission = db.Column(db.Text)
    vision = db.Column(db.Text)
    motto = db.Column(db.String(200))
    history = db.Column(db.Text)
    achievements = db.Column(db.Text)
    contact_address = db.Column(db.Text)
    contact_phone = db.Column(db.String(50))
    contact_email = db.Column(db.String(120))
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NewsEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'news' or 'event'
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class StaffMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(200), nullable=False)
    qualifications = db.Column(db.Text)
    subjects = db.Column(db.String(500))
    photo_filename = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)

class ELearningResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    form = db.Column(db.String(20), nullable=False)  # Form 1, Form 2, etc.
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    resource_type = db.Column(db.String(20), nullable=False)  # 'file' or 'youtube'
    filename = db.Column(db.String(200))  # For uploaded files
    youtube_url = db.Column(db.String(500))  # For YouTube videos
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)
