from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def login_required(f):
    """
    Decorator to require login for routes.
    Redirects to login page if user is not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def validate_password(password):
    """
    Validate password strength.
    Returns (is_valid, message).
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    
    if password.isalpha() or password.isdigit():
        return False, "Password must contain both letters and numbers."
    
    return True, "Password is valid."


def validate_username(username):
    """
    Validate username format.
    Returns (is_valid, message).
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    
    if not username.isalnum() and '_' not in username:
        return False, "Username can only contain letters, numbers, and underscores."
    
    return True, "Username is valid."
