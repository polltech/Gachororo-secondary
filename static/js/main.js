// Gachororo Secondary School - Main JavaScript File

(function() {
    'use strict';

    // DOM Content Loaded Event
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });

    // Initialize Application
    function initializeApp() {
        setupNavigation();
        setupForms();
        setupImageLazyLoading();
        setupSmoothScrolling();
        setupAnimations();
        setupAlerts();
        setupMobileMenu();
        setupBackToTop();
        setupImageGallery();
        setupFormValidation();
        setupTooltips();
        setupProgressBars();
    }

    // Navigation Enhancement
    function setupNavigation() {
        const navbar = document.querySelector('.navbar');
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        // Add active class to current page
        const currentPath = window.location.pathname;
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });

        // Navbar scroll effect
        if (navbar) {
            let lastScrollTop = 0;
            window.addEventListener('scroll', function() {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                if (scrollTop > 100) {
                    navbar.classList.add('navbar-scrolled');
                } else {
                    navbar.classList.remove('navbar-scrolled');
                }
                
                // Hide/show navbar on scroll (optional)
                if (scrollTop > lastScrollTop && scrollTop > 200) {
                    navbar.style.transform = 'translateY(-100%)';
                } else {
                    navbar.style.transform = 'translateY(0)';
                }
                
                lastScrollTop = scrollTop;
            });
        }
    }

    // Form Enhancements
    function setupForms() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            // Add loading state to submit buttons
            form.addEventListener('submit', function(e) {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn && !form.hasAttribute('data-no-loading')) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                    submitBtn.disabled = true;
                    
                    // Re-enable after 3 seconds (fallback)
                    setTimeout(() => {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }, 3000);
                }
            });

            // Auto-resize textareas
            const textareas = form.querySelectorAll('textarea');
            textareas.forEach(textarea => {
                textarea.addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = this.scrollHeight + 'px';
                });
            });

            // Add character counter to textareas with maxlength
            textareas.forEach(textarea => {
                const maxLength = textarea.getAttribute('maxlength');
                if (maxLength) {
                    addCharacterCounter(textarea, maxLength);
                }
            });
        });
    }

    // Add character counter to textarea
    function addCharacterCounter(textarea, maxLength) {
        const counter = document.createElement('div');
        counter.className = 'form-text text-end character-counter';
        textarea.parentNode.appendChild(counter);

        function updateCounter() {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = `${textarea.value.length}/${maxLength} characters`;
            
            if (remaining < 20) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning');
            }
        }

        textarea.addEventListener('input', updateCounter);
        updateCounter();
    }

    // Image Lazy Loading
    function setupImageLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for older browsers
            images.forEach(img => {
                img.src = img.dataset.src;
                img.classList.remove('lazy');
            });
        }
    }

    // Smooth Scrolling
    function setupSmoothScrolling() {
        const links = document.querySelectorAll('a[href*="#"]:not([href="#"])');
        
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    e.preventDefault();
                    const offsetTop = targetElement.offsetTop - 80; // Account for fixed navbar
                    
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // Animations on Scroll
    function setupAnimations() {
        const animatedElements = document.querySelectorAll('.animate-on-scroll');
        
        if (animatedElements.length > 0) {
            const animationObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-fade-in');
                        animationObserver.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            animatedElements.forEach(el => animationObserver.observe(el));
        }

        // Add scroll animation class to cards
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('animate-on-scroll');
        });
    }

    // Alert Auto-dismiss
    function setupAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        
        alerts.forEach(alert => {
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (alert.classList.contains('show')) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, 5000);
        });
    }

    // Mobile Menu Enhancement
    function setupMobileMenu() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (navbarToggler && navbarCollapse) {
            // Close mobile menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!navbarCollapse.contains(e.target) && !navbarToggler.contains(e.target)) {
                    if (navbarCollapse.classList.contains('show')) {
                        const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                            toggle: false
                        });
                        bsCollapse.hide();
                    }
                }
            });

            // Close mobile menu when clicking on nav links
            const navLinks = navbarCollapse.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    if (navbarCollapse.classList.contains('show')) {
                        const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                            toggle: false
                        });
                        bsCollapse.hide();
                    }
                });
            });
        }
    }

    // Back to Top Button
    function setupBackToTop() {
        // Create back to top button
        const backToTopBtn = document.createElement('button');
        backToTopBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
        backToTopBtn.className = 'btn btn-primary btn-back-to-top';
        backToTopBtn.setAttribute('aria-label', 'Back to top');
        backToTopBtn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        document.body.appendChild(backToTopBtn);

        // Show/hide button based on scroll position
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.style.opacity = '1';
                backToTopBtn.style.visibility = 'visible';
            } else {
                backToTopBtn.style.opacity = '0';
                backToTopBtn.style.visibility = 'hidden';
            }
        });

        // Scroll to top when clicked
        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Image Gallery Enhancement
    function setupImageGallery() {
        const galleryImages = document.querySelectorAll('.gallery-img');
        
        galleryImages.forEach(img => {
            img.addEventListener('click', function() {
                // Add zoom effect on click
                this.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 200);
            });

            // Add error handling
            img.addEventListener('error', function() {
                this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y4ZjlmYSIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0ic2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNHB4IiBmaWxsPSIjNmM3NTdkIj5JbWFnZSBub3QgZm91bmQ8L3RleHQ+Cjwvc3ZnPg==';
                this.alt = 'Image not found';
            });
        });
    }

    // Enhanced Form Validation
    function setupFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    validateField(this);
                });
                
                input.addEventListener('input', function() {
                    if (this.classList.contains('is-invalid')) {
                        validateField(this);
                    }
                });
            });

            form.addEventListener('submit', function(e) {
                let isValid = true;
                
                inputs.forEach(input => {
                    if (!validateField(input)) {
                        isValid = false;
                    }
                });

                if (!isValid) {
                    e.preventDefault();
                    const firstInvalidField = form.querySelector('.is-invalid');
                    if (firstInvalidField) {
                        firstInvalidField.focus();
                    }
                }
            });
        });
    }

    // Validate individual field
    function validateField(field) {
        const value = field.value.trim();
        const fieldType = field.type;
        const isRequired = field.hasAttribute('required');
        let isValid = true;
        let errorMessage = '';

        // Remove existing validation classes
        field.classList.remove('is-valid', 'is-invalid');

        // Required field validation
        if (isRequired && !value) {
            isValid = false;
            errorMessage = 'This field is required.';
        }
        // Email validation
        else if (fieldType === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address.';
            }
        }
        // Phone validation
        else if (fieldType === 'tel' && value) {
            const phoneRegex = /^\+?[\d\s-()]+$/;
            if (!phoneRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid phone number.';
            }
        }
        // URL validation
        else if (fieldType === 'url' && value) {
            const urlRegex = /^https?:\/\/.+/;
            if (!urlRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid URL starting with http:// or https://';
            }
        }

        // Add validation classes and feedback
        if (isValid) {
            field.classList.add('is-valid');
            removeFieldError(field);
        } else {
            field.classList.add('is-invalid');
            showFieldError(field, errorMessage);
        }

        return isValid;
    }

    // Show field error
    function showFieldError(field, message) {
        removeFieldError(field);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
    }

    // Remove field error
    function removeFieldError(field) {
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    // Initialize Tooltips
    function setupTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Progress Bars Animation
    function setupProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        
        if (progressBars.length > 0) {
            const progressObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const progressBar = entry.target;
                        const targetWidth = progressBar.getAttribute('aria-valuenow');
                        
                        progressBar.style.width = '0%';
                        setTimeout(() => {
                            progressBar.style.width = targetWidth + '%';
                        }, 100);
                        
                        progressObserver.unobserve(progressBar);
                    }
                });
            });

            progressBars.forEach(bar => progressObserver.observe(bar));
        }
    }

    // Utility Functions
    window.SchoolApp = {
        // Show loading spinner
        showLoading: function(element) {
            if (element) {
                element.innerHTML = '<div class="loading-spinner"></div>';
            }
        },

        // Hide loading spinner
        hideLoading: function(element, originalContent) {
            if (element) {
                element.innerHTML = originalContent || '';
            }
        },

        // Show toast notification
        showToast: function(message, type) {
            const toast = document.createElement('div');
            toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            toast.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
            toast.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.body.appendChild(toast);
            
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(toast);
                bsAlert.close();
            }, 5000);
        },

        // Format date
        formatDate: function(date) {
            const options = { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            };
            return new Date(date).toLocaleDateString('en-US', options);
        },

        // Debounce function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    };

    // Global error handler
    window.addEventListener('error', function(e) {
        console.error('JavaScript Error:', e.error);
        // You could send this to a logging service
    });

    // Performance monitoring
    window.addEventListener('load', function() {
        if ('performance' in window) {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            console.log('Page load time:', loadTime + 'ms');
        }
    });

})();

// Service Worker Registration (for future PWA support)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Uncomment when you have a service worker
        // navigator.serviceWorker.register('/sw.js');
    });
}
