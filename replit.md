# Gachororo Secondary School Website

## Overview

A comprehensive Flask-based web application for Gachororo Secondary School that provides both a public-facing website and an admin dashboard for content management. The system allows school administrators to manage all aspects of the school's online presence including educational content, news, staff profiles, gallery images, and e-learning resources. The application features a responsive design built with Bootstrap and provides a complete content management system specifically tailored for educational institutions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 with Flask for dynamic content rendering
- **CSS Framework**: Bootstrap 5 for responsive, mobile-first design
- **JavaScript**: Vanilla JavaScript with modern ES6+ features for interactive functionality
- **UI Components**: Custom CSS variables for consistent school branding and styling
- **Responsive Design**: Mobile-responsive layout with progressive enhancement

### Backend Architecture
- **Web Framework**: Flask (Python) with modular route organization
- **Authentication**: Flask-Login for session management with role-based access control
- **Database ORM**: SQLAlchemy with declarative base for database operations
- **File Handling**: Local filesystem storage for uploads with secure filename handling
- **Security**: Password hashing with Werkzeug, CSRF protection, and secure file uploads

### Data Storage Solutions
- **Primary Database**: SQLite3 for development with easy migration path to PostgreSQL
- **File Storage**: Local filesystem with organized directory structure (`uploads/` folder)
- **Session Management**: Flask's built-in session handling with configurable secret keys
- **Database Models**: Six core entities (User, SchoolContent, NewsEvent, StaffMember, GalleryImage, ELearningResource)

### Authentication and Authorization
- **Single Admin Model**: One administrator account with full system access
- **Password Security**: Werkzeug password hashing for secure credential storage
- **Session Security**: Configurable session secrets with environment variable support
- **Access Control**: Login-required decorators protecting all administrative functions

### Content Management System
- **School Information**: Editable mission, vision, principal message, and contact details
- **News & Events**: Separate categorization system for announcements and events
- **Staff Profiles**: Complete staff management with photo uploads and qualification tracking
- **Gallery System**: Image upload and management with metadata support
- **E-Learning Platform**: Resource categorization by form level and subject with file upload capabilities

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework for responsive design and UI components
- **Font Awesome 6.4.0**: Icon library for consistent iconography throughout the application
- **Google Fonts (Inter)**: Typography enhancement for professional appearance

### Python Packages
- **Flask**: Core web application framework
- **Flask-SQLAlchemy**: Database ORM and connection management
- **Flask-Login**: User session and authentication management
- **Werkzeug**: WSGI utilities, security helpers, and file handling

### Development Tools
- **SQLite3**: Embedded database for development and small-scale deployment
- **Jinja2**: Template engine integrated with Flask for dynamic content rendering

### File Upload System
- **Local Storage**: Organized file system with separate directories for different content types
- **Security Measures**: Secure filename handling and file type validation
- **Size Limits**: Configurable upload limits (50MB default) for resource management

### Hosting and Deployment
- **Development Server**: Flask's built-in development server
- **Production Ready**: WSGI-compatible for deployment on various hosting platforms
- **Static Assets**: CDN-delivered external libraries for optimal performance