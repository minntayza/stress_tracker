from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from fuzzy_logic import StressFuzzySystem
from stress_history import StressHistory
from hybrid_engine import HybridEngine
from visual_analytics import StressVisualizer
from database import db, User, Goal
from auth import validate_password, validate_username

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stress_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Systems
fuzzy_system = StressFuzzySystem()
hybrid_engine = HybridEngine()
visualizer = StressVisualizer()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============ Authentication Routes ============

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        is_valid_username, username_msg = validate_username(username)
        if not is_valid_username:
            flash(username_msg, 'danger')
            return render_template('signup.html')
        
        is_valid_password, password_msg = validate_password(password)
        if not is_valid_password:
            flash(password_msg, 'danger')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('signup.html')
        
        # Create user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'Account created successfully! Welcome, {username}!', 'success')
        login_user(new_user)
        return redirect(url_for('home'))
    
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember', False))
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to next page or home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Invalid username/email or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# ============ Main Application Routes ============

@app.route('/')
@login_required
def home():
    return render_template('index.html', user=current_user)


@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    # Get user-specific history manager
    history_manager = StressHistory(user_id=current_user.id)
    
    # 1. Get Inputs
    try:
        sleep_hours = float(request.form.get('sleep'))
        study_hours = float(request.form.get('study'))
        screen_time = float(request.form.get('screen_time'))
        journal_text = request.form.get('journal')
        
        # New Inputs
        mood = float(request.form.get('mood', 5))
        deadline_str = request.form.get('deadline', 'none')
        activity_str = request.form.get('activity', 'none')

        # Map strings to numeric for fuzzy logic
        deadline_map = {'none': 0, 'upcoming': 5, 'urgent': 10}
        activity_map = {'none': 0, 'light': 3, 'moderate': 6, 'intense': 10}
        
        deadline_level = deadline_map.get(deadline_str, 0)
        activity_level = activity_map.get(activity_str, 0)

    except (ValueError, TypeError):
        flash('Invalid input. Please check your entries.', 'danger')
        return redirect(url_for('home'))

    # 2. Compute Stress (Fuzzy Logic)
    stress_score = fuzzy_system.compute_stress(sleep_hours, study_hours, mood, deadline_level, activity_level, screen_time)
    
    # 3. Analyze Sentiment (Hybrid ML)
    sentiment = hybrid_engine.analyze_sentiment(journal_text)
    
    # 4. Check Healing Status (History)
    healing_status = history_manager.check_healing_status(stress_score)
    
    # 5. Determine Recommendation
    if stress_score > 70:
        recommendation = "High stress detected. Prioritize sleep and breaks."
    elif stress_score > 40:
        recommendation = "Moderate stress. Maintain a balanced schedule."
    else:
        recommendation = "Low stress. Great job maintaining balance!"

    if healing_status == "Healing Phase":
        recommendation += " You are in a Healing Phase! Keep it up."
    elif healing_status == "Relapse":
        recommendation += " Warning: Stress levels have increased since last time."
    
    # High screen time warning
    if screen_time > 8:
        recommendation += " Consider reducing screen time to improve well-being."

    # 6. Adaptive Recommendation
    successful_strategy = history_manager.find_effective_strategies()
    adaptive_tip = None
    if successful_strategy:
        adaptive_tip = f"Last time, this helped you: '{successful_strategy}'"

    # 7. Save to History
    history_manager.save_entry(stress_score, recommendation, healing_status)
    
    # 8. Update active goals
    update_user_goals(current_user.id, stress_score, history_manager)

    return render_template('result.html', 
                           stress_score=round(stress_score, 2),
                           sentiment=sentiment,
                           healing_status=healing_status,
                           recommendation=recommendation,
                           adaptive_tip=adaptive_tip,
                           sleep=sleep_hours,
                           study=study_hours,
                           screen_time=screen_time,
                           journal=journal_text,
                           mood=mood,
                           deadline=deadline_str,
                           activity=activity_str,
                           user=current_user)


@app.route('/history')
@login_required
def history():
    history_manager = StressHistory(user_id=current_user.id)
    history_data = history_manager.load_history()
    
    # Get active goals for display
    active_goals = Goal.query.filter_by(user_id=current_user.id, status='active').all()
    
    return render_template('history.html', 
                          history_data=history_data, 
                          user=current_user,
                          goals=active_goals)


# ============ Goal Management Routes ============

@app.route('/goals')
@login_required
def goals():
    user_goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.created_at.desc()).all()
    return render_template('goals.html', goals=user_goals, user=current_user)


@app.route('/goals/create', methods=['POST'])
@login_required
def create_goal():
    goal_type = request.form.get('goal_type')
    target_value = float(request.form.get('target_value'))
    description = request.form.get('description', '')
    deadline_str = request.form.get('deadline')
    
    from datetime import datetime
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
    
    new_goal = Goal(
        user_id=current_user.id,
        goal_type=goal_type,
        target_value=target_value,
        description=description,
        deadline=deadline
    )
    
    db.session.add(new_goal)
    db.session.commit()
    
    flash('Goal created successfully!', 'success')
    return redirect(url_for('goals'))


@app.route('/goals/<int:goal_id>/delete', methods=['POST'])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    
    if goal.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('goals'))
    
    db.session.delete(goal)
    db.session.commit()
    
    flash('Goal deleted successfully.', 'info')
    return redirect(url_for('goals'))


# ============ Helper Functions ============

def update_user_goals(user_id, current_stress, history_manager):
    """Update goal progress based on current stress assessment."""
    active_goals = Goal.query.filter_by(user_id=user_id, status='active').all()
    history_data = history_manager.load_history()
    
    for goal in active_goals:
        if goal.goal_type == 'avg_stress' and len(history_data) > 0:
            # Calculate average stress from history
            avg_stress = sum(entry['stress_score'] for entry in history_data) / len(history_data)
            goal.current_value = avg_stress
            
        elif goal.goal_type == 'peak_stress' and len(history_data) > 0:
            # Get peak (max) stress from history
            peak_stress = max(entry['stress_score'] for entry in history_data)
            goal.current_value = peak_stress
        
        # Check if goal is achieved
        if goal.is_achieved() and goal.status == 'active':
            goal.status = 'completed'
            goal.completed_at = db.datetime.utcnow()
            flash(f'🎉 Congratulations! You achieved your goal: {goal.description}', 'success')
    
    db.session.commit()


# ============ Database Initialization ============

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, port=5001)
