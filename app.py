from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import json
from datetime import datetime, timedelta
from fuzzy_logic import StressFuzzySystem
from stress_history import StressHistory
from hybrid_engine import HybridEngine
from visual_analytics import StressVisualizer
from database import db, User, Goal, AssessmentEntry
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

# ─── Mappings (shared) ───────────────────────────────────────────────────────
DEADLINE_MAP = {'none': 0, 'upcoming': 5, 'urgent': 10}
ACTIVITY_MAP = {'none': 0, 'light': 3, 'moderate': 6, 'intense': 10}
PROCRASTINATION_MAP = {'low': 2, 'medium': 5, 'high': 8}

QUIZ_QUESTIONS = [
    "I feel overwhelmed by my responsibilities.",
    "I have trouble relaxing.",
    "I worry about my finances.",
    "I feel pressure from deadlines.",
    "I put off tasks until the last minute.",
    "I feel isolated or unsupported.",
    "I have trouble concentrating.",
    "I feel irritable or short-tempered.",
    "I feel tired even after sleeping.",
    "My workload feels unmanageable.",
    "I feel like I have no control over my schedule.",
    "I feel anxious about the future.",
    "I skip meals or eat poorly due to stress.",
    "I get headaches or body tension.",
    "I spend more time on screens than I want to.",
    "I feel guilty about my productivity.",
    "I feel like I am falling behind.",
    "I find it hard to start tasks.",
    "I feel rushed throughout the day.",
    "I feel stressed when I think about my to-do list.",
]


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

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('signup.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('signup.html')

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash(f'Account created! Welcome, {username}!', 'success')
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

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember', False))
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    # Clear wizard session data on logout
    for key in ['wizard_step1', 'wizard_step2', 'wizard_quiz_completed', 'wizard_quiz_score',
                 'wizard_quiz_answers', 'wizard_journal_text', 'wizard_sentiment',
                 'wizard_result', 'wizard_saved_entry_id', 'wizard_saved_at']:
        session.pop(key, None)
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# ============ Home → Redirect to Wizard ============

@app.route('/')
@login_required
def home():
    return redirect(url_for('assess_step1'))


# ============ Wizard Routes ============

@app.route('/assess/step1', methods=['GET', 'POST'])
@login_required
def assess_step1():
    if request.method == 'POST':
        errors = []
        try:
            sleep_hours = float(request.form.get('sleep', ''))
            if not (0 <= sleep_hours <= 12):
                errors.append('Sleep hours must be between 0 and 12.')
        except ValueError:
            errors.append('Please enter a valid number for sleep hours.')
            sleep_hours = 7.0

        try:
            study_hours = float(request.form.get('study', ''))
            if not (0 <= study_hours <= 16):
                errors.append('Study hours must be between 0 and 16.')
        except ValueError:
            errors.append('Please enter a valid number for study hours.')
            study_hours = 4.0

        try:
            screen_time = float(request.form.get('screen_time', ''))
            if not (0 <= screen_time <= 24):
                errors.append('Screen time must be between 0 and 24 hours.')
        except ValueError:
            errors.append('Please enter a valid number for screen time.')
            screen_time = 4.0

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('wizard/step1.html',
                                   data={'sleep': request.form.get('sleep'),
                                         'study': request.form.get('study'),
                                         'screen_time': request.form.get('screen_time')},
                                   step=1)

        session['wizard_step1'] = {
            'sleep': sleep_hours,
            'study': study_hours,
            'screen_time': screen_time,
        }
        # New Step 1 input invalidates any previously computed/saved wizard result.
        for key in ['wizard_step2', 'wizard_quiz_completed', 'wizard_quiz_score',
                'wizard_quiz_answers', 'wizard_journal_text', 'wizard_sentiment',
                'wizard_result', 'wizard_saved_entry_id', 'wizard_saved_at']:
            session.pop(key, None)
        return redirect(url_for('assess_step2'))

    return render_template('wizard/step1.html',
                           data=session.get('wizard_step1', {}),
                           step=1)


@app.route('/assess/step2', methods=['GET', 'POST'])
@login_required
def assess_step2():
    if 'wizard_step1' not in session:
        flash('Please start from Step 1.', 'warning')
        return redirect(url_for('assess_step1'))

    if request.method == 'POST':
        errors = []

        try:
            mood = float(request.form.get('mood', ''))
            if not (1 <= mood <= 10):
                errors.append('Mood must be between 1 and 10.')
        except ValueError:
            errors.append('Please select a mood value.')
            mood = 5.0

        try:
            social_interaction = float(request.form.get('social_interaction', ''))
            if not (0 <= social_interaction <= 10):
                errors.append('Social support must be between 0 and 10.')
        except ValueError:
            errors.append('Please select a social support value.')
            social_interaction = 5.0

        deadline = request.form.get('deadline', 'none')
        if deadline not in DEADLINE_MAP:
            errors.append('Please select a valid deadline pressure level.')

        try:
            financial_stress = float(request.form.get('financial_stress', ''))
            if not (0 <= financial_stress <= 10):
                errors.append('Financial stress must be between 0 and 10.')
        except ValueError:
            errors.append('Please select a financial stress value.')
            financial_stress = 5.0

        procrastination = request.form.get('procrastination', 'medium')
        if procrastination not in PROCRASTINATION_MAP:
            errors.append('Please select a valid procrastination level.')

        activity = request.form.get('activity', 'none')
        if activity not in ACTIVITY_MAP:
            errors.append('Please select a valid activity level.')

        try:
            age = int(request.form.get('age', ''))
            if not (10 <= age <= 80):
                errors.append('Age must be between 10 and 80.')
        except ValueError:
            errors.append('Please enter a valid age.')
            age = 21

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('wizard/step2.html',
                                   data=request.form,
                                   step=2)

        session['wizard_step2'] = {
            'mood': mood,
            'social_interaction': social_interaction,
            'deadline': deadline,
            'financial_stress': financial_stress,
            'procrastination': procrastination,
            'activity': activity,
            'age': age,
        }
        for key in ['wizard_quiz_completed', 'wizard_quiz_score', 'wizard_quiz_answers',
                'wizard_journal_text', 'wizard_sentiment',
                'wizard_result', 'wizard_saved_entry_id', 'wizard_saved_at']:
            session.pop(key, None)
        return redirect(url_for('assess_step3'))

    return render_template('wizard/step2.html',
                           data=session.get('wizard_step2', {}),
                           step=2)


@app.route('/assess/step3', methods=['GET', 'POST'])
@login_required
def assess_step3():
    if 'wizard_step1' not in session or 'wizard_step2' not in session:
        flash('Please complete Steps 1 and 2 first.', 'warning')
        return redirect(url_for('assess_step1'))

    if request.method == 'POST':
        quiz_values = []
        errors = []
        journal_text = request.form.get('journal', '').strip()
        for i in range(1, 21):
            val = request.form.get(f'q{i}')
            if val is None:
                errors.append(f'Please answer question {i}.')
                break
            try:
                val_int = int(val)
                if not (1 <= val_int <= 5):
                    errors.append(f'Question {i} must be between 1 and 5.')
                    break
                quiz_values.append(val_int)
            except ValueError:
                errors.append(f'Invalid value for question {i}.')
                break

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('wizard/step3.html',
                                   questions=QUIZ_QUESTIONS,
                                   data=request.form,
                                   step=3)

        quiz_avg = sum(quiz_values) / len(quiz_values)
        quiz_score = max(0.0, min(100.0, ((quiz_avg - 1) / 4) * 100))

        sentiment = None
        if journal_text:
            try:
                sentiment = hybrid_engine.analyze_sentiment(journal_text)
            except (AttributeError, TypeError, ValueError):
                sentiment = {'polarity': 0.0, 'subjectivity': 0.0}

        session['wizard_quiz_completed'] = True
        session['wizard_quiz_score'] = quiz_score
        session['wizard_quiz_answers'] = quiz_values
        session['wizard_journal_text'] = journal_text
        session['wizard_sentiment'] = sentiment
        for key in ['wizard_result', 'wizard_saved_entry_id', 'wizard_saved_at']:
            session.pop(key, None)
        return redirect(url_for('assess_step4'))

    return render_template('wizard/step3.html',
                           questions=QUIZ_QUESTIONS,
                           data={'journal': session.get('wizard_journal_text', '')},
                           step=3)


@app.route('/assess/skip-quiz', methods=['POST'])
@login_required
def skip_quiz():
    """Skip the quiz — generates an estimated result from Steps 1–2 only."""
    if 'wizard_step1' not in session or 'wizard_step2' not in session:
        flash('Please complete Steps 1 and 2 first.', 'warning')
        return redirect(url_for('assess_step1'))

    session['wizard_quiz_completed'] = False
    session['wizard_quiz_score'] = None
    session['wizard_quiz_answers'] = None
    session['wizard_journal_text'] = None
    session['wizard_sentiment'] = None
    for key in ['wizard_result', 'wizard_saved_entry_id', 'wizard_saved_at']:
        session.pop(key, None)
    return redirect(url_for('assess_step4'))


@app.route('/assess/step4')
@login_required
def assess_step4():
    """Compute and display results. Redirect backward if session is incomplete."""
    if 'wizard_step1' not in session or 'wizard_step2' not in session:
        flash('Please complete Steps 1 and 2 first.', 'warning')
        return redirect(url_for('assess_step1'))

    if 'wizard_quiz_completed' not in session:
        return redirect(url_for('assess_step3'))

    s1 = session['wizard_step1']
    s2 = session['wizard_step2']
    quiz_completed = session['wizard_quiz_completed']
    quiz_score = session.get('wizard_quiz_score')
    sentiment = session.get('wizard_sentiment')
    journal_text = session.get('wizard_journal_text')

    # Use a neutral quiz score (50) when skipped — does not inflate/deflate
    effective_quiz_score = quiz_score if quiz_completed else 50.0

    deadline_level = DEADLINE_MAP.get(s2['deadline'], 0)
    activity_level = ACTIVITY_MAP.get(s2['activity'], 0)
    procrastination_level = PROCRASTINATION_MAP.get(s2['procrastination'], 5)

    stress_score = fuzzy_system.compute_stress(
        s1['sleep'], s1['study'], s2['mood'], deadline_level, activity_level, s1['screen_time'],
        s2['social_interaction'], procrastination_level, s2['financial_stress'], s2['age'],
        effective_quiz_score
    )
    lifestyle_instability = fuzzy_system.compute_instability(
        s2['social_interaction'], procrastination_level, s2['financial_stress'], s2['age']
    )

    # Healing status
    history_manager = StressHistory(user_id=current_user.id)
    healing_status = history_manager.check_healing_status(stress_score)

    # Stress label + badge
    if stress_score > 70:
        stress_label = 'High'
        badge_class = 'badge-high'
    elif stress_score > 40:
        stress_label = 'Moderate'
        badge_class = 'badge-moderate'
    else:
        stress_label = 'Low'
        badge_class = 'badge-low'

    # Top contributing factors
    factors = _compute_top_factors(s1, s2, quiz_score, quiz_completed, sentiment)

    # Actionable tips (2–3)
    tips = _generate_tips(s1, s2, stress_score, sentiment)

    # Adaptive tip
    adaptive_tip = None
    successful_strategy = history_manager.find_effective_strategies()
    if successful_strategy:
        adaptive_tip = f"Last time this helped you: \"{successful_strategy}\""

    # Plain-language explanation
    explanation = _build_explanation(stress_score, s1, s2, quiz_completed, sentiment)

    result = {
        'stress_score': round(stress_score, 1),
        'lifestyle_instability': round(lifestyle_instability, 1),
        'instability_label': ("High" if lifestyle_instability > 70 else "Moderate" if lifestyle_instability > 40 else "Low"),
        'quiz_score': round(quiz_score, 1) if quiz_score is not None else None,
        'quiz_completed': quiz_completed,
        'stress_label': stress_label,
        'badge_class': badge_class,
        'healing_status': healing_status,
        'factors': factors,
        'tips': tips,
        'adaptive_tip': adaptive_tip,
        'explanation': explanation,
        'sentiment': sentiment,
        'journal_present': bool(journal_text),
        'result_type': 'Full result (quiz completed)' if quiz_completed else 'Estimated result (quiz skipped)',
    }
    session['wizard_result'] = result

    # Auto-save exactly once per wizard result; avoids losing data if user leaves Step 4.
    saved_entry, autosaved_now = _persist_wizard_result_if_needed(current_user.id)

    return render_template('wizard/step4.html',
                           result=result,
                           s1=s1,
                           s2=s2,
                           autosaved_now=autosaved_now,
                           autosaved_entry_id=saved_entry.id if saved_entry else None,
                           step=4)


@app.route('/assess/save', methods=['POST'])
@login_required
def assess_save():
    """Persist current wizard result idempotently and open trends."""
    if 'wizard_result' not in session and 'wizard_saved_entry_id' not in session:
        flash('No result to save. Please complete the assessment first.', 'warning')
        return redirect(url_for('assess_step1'))
    _persist_wizard_result_if_needed(current_user.id)

    # Clear wizard session
    for key in ['wizard_step1', 'wizard_step2', 'wizard_quiz_completed',
                 'wizard_quiz_score', 'wizard_quiz_answers', 'wizard_journal_text',
                 'wizard_sentiment', 'wizard_result',
                 'wizard_saved_entry_id', 'wizard_saved_at']:
        session.pop(key, None)

    flash('✅ Assessment saved successfully!', 'success')
    return redirect(url_for('history'))


# ============ History / Trends ============

@app.route('/history')
@login_required
def history():
    history_data = _load_history_entries_for_user(current_user.id)
    active_goals = Goal.query.filter_by(user_id=current_user.id, status='active').all()
    has_unsaved_result = ('wizard_result' in session and 'wizard_saved_entry_id' not in session)

    return render_template('history.html',
                           history_data=history_data,
                           user=current_user,
                           goals=active_goals,
                           has_unsaved_result=has_unsaved_result)


@app.route('/history/data')
@login_required
def history_data():
    """JSON API for trends charts with daily bucketed series."""
    days = request.args.get('days', 30, type=int)
    if days not in (7, 30, 90):
        days = 30

    all_entries = _load_history_entries_for_user(current_user.id)

    parsed_entries = []
    for entry in all_entries:
        entry_dt = _parse_entry_datetime(entry.get('date'))
        if not entry_dt:
            continue
        normalized = dict(entry)
        normalized["_dt"] = entry_dt
        # Backward compatibility for old keys
        if normalized.get('sleep') is None and normalized.get('sleep_hours') is not None:
            normalized['sleep'] = normalized.get('sleep_hours')
        if normalized.get('study') is None and normalized.get('study_hours') is not None:
            normalized['study'] = normalized.get('study_hours')
        parsed_entries.append(normalized)

    parsed_entries.sort(key=lambda e: e["_dt"])

    now = datetime.now()
    period_start = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    filtered = [e for e in parsed_entries if e["_dt"] >= period_start]

    # Build daily buckets so 7/30/90 always reflects the selected time window
    labels = []
    stress_series = []
    instability_series = []
    sleep_series = []
    screen_series = []
    mood_series = []

    for offset in range(days):
        day = period_start + timedelta(days=offset)
        day_label = day.strftime("%b %d")
        labels.append(day_label)

        day_entries = [e for e in filtered if e["_dt"].date() == day.date()]

        stress_series.append(_avg_numeric(day_entries, "stress_score"))
        instability_series.append(_avg_numeric(day_entries, "lifestyle_instability"))
        sleep_series.append(_avg_numeric(day_entries, "sleep"))
        screen_series.append(_avg_numeric(day_entries, "screen_time"))
        mood_series.append(_avg_numeric(day_entries, "mood"))

    stress_ma7 = _moving_average(stress_series, window=7)

    insights = _generate_insights(filtered)

    earliest_dt = parsed_entries[0]["_dt"] if parsed_entries else None
    period_note = ""
    if earliest_dt:
        if days > 7 and earliest_dt >= (now - timedelta(days=7)):
            period_note = "All your saved entries are from the last 7 days, so 30 and 90 days will look the same."
        elif days > 30 and earliest_dt >= (now - timedelta(days=30)):
            period_note = "All your saved entries are from the last 30 days, so the 90-day chart will match 30 days."
    else:
        period_note = "No saved entries yet. Complete and save an assessment to populate trends."

    # Remove helper key before sending to client
    serialized_entries = []
    for e in filtered:
        cloned = dict(e)
        cloned.pop("_dt", None)
        serialized_entries.append(cloned)

    return jsonify({
        'entries': serialized_entries,
        'insights': insights,
        'series': {
            'labels': labels,
            'stress': stress_series,
            'stress_ma7': stress_ma7,
            'instability': instability_series,
            'sleep': sleep_series,
            'screen_time': screen_series,
            'mood': mood_series,
        },
        'meta': {
            'days': days,
            'period_start': period_start.strftime("%Y-%m-%d"),
            'period_end': now.strftime("%Y-%m-%d"),
            'entries_in_period': len(serialized_entries),
            'period_note': period_note,
        }
    })


# ============ Goal Management Routes ============

@app.route('/goals')
@login_required
def goals():
    user_goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.created_at.desc()).all()
    return render_template('goals.html', goals=user_goals, user=current_user)


@app.route('/goals/create', methods=['POST'])
@login_required
def create_goal():
    goal_type = 'avg_stress'
    try:
        target_value = float(request.form.get('target_value'))
    except (TypeError, ValueError):
        flash('Please enter a valid numeric target value.', 'danger')
        return redirect(url_for('goals'))

    if not (0 <= target_value <= 100):
        flash('Target value must be between 0 and 100.', 'danger')
        return redirect(url_for('goals'))

    description = request.form.get('description', '')
    deadline_str = request.form.get('deadline')
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
    except ValueError:
        flash('Please provide a valid deadline date.', 'danger')
        return redirect(url_for('goals'))

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
    flash('Goal deleted.', 'info')
    return redirect(url_for('goals'))


# ============ Helper Functions ============

def _persist_wizard_result_if_needed(user_id):
    """
    Save current wizard result once and return (entry, created_now).
    Idempotent across page refreshes using session marker.
    """
    saved_id = session.get('wizard_saved_entry_id')
    if saved_id:
        existing = AssessmentEntry.query.filter_by(id=saved_id, user_id=user_id).first()
        if existing:
            return existing, False
        # Stale marker (entry removed); continue and recreate.
        session.pop('wizard_saved_entry_id', None)
        session.pop('wizard_saved_at', None)

    required_keys = ('wizard_step1', 'wizard_step2', 'wizard_result')
    if not all(k in session for k in required_keys):
        return None, False

    s1 = session['wizard_step1']
    s2 = session['wizard_step2']
    result = session['wizard_result']
    quiz_answers = session.get('wizard_quiz_answers')
    journal_text = session.get('wizard_journal_text')
    sentiment = session.get('wizard_sentiment')

    entry = AssessmentEntry(
        user_id=user_id,
        sleep_hours=s1['sleep'],
        study_hours=s1['study'],
        screen_time=s1['screen_time'],
        mood=s2['mood'],
        social_interaction=s2['social_interaction'],
        deadline=s2['deadline'],
        financial_stress=s2['financial_stress'],
        procrastination=s2['procrastination'],
        activity=s2['activity'],
        age=s2['age'],
        quiz_completed=result['quiz_completed'],
        quiz_score=result['quiz_score'],
        quiz_answers=json.dumps(quiz_answers) if quiz_answers else None,
        stress_score=result['stress_score'],
        lifestyle_instability=result['lifestyle_instability'],
        healing_status=result['healing_status'],
        recommendation='; '.join(result['tips']),
    )
    db.session.add(entry)
    db.session.commit()

    history_manager = StressHistory(user_id=user_id)
    history_meta = entry.to_history_dict()
    history_meta['journal_present'] = bool(journal_text)
    if sentiment:
        history_meta['sentiment'] = {
            'polarity': round(float(sentiment.get('polarity', 0.0)), 3),
            'subjectivity': round(float(sentiment.get('subjectivity', 0.0)), 3),
        }
    if journal_text:
        history_meta['journal_excerpt'] = journal_text[:180]
    history_manager.save_entry(
        result['stress_score'],
        '; '.join(result['tips']),
        result['healing_status'],
        meta=history_meta
    )
    update_user_goals(user_id, result['stress_score'], history_manager)

    session['wizard_saved_entry_id'] = entry.id
    session['wizard_saved_at'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return entry, True


def _parse_entry_datetime(value):
    """Parse history entry date robustly across legacy formats."""
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue
    return None


def _avg_numeric(entries, key):
    """Average numeric values for a key; returns None if no valid values."""
    values = []
    for entry in entries:
        raw = entry.get(key)
        if raw is None:
            continue
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            continue
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def _moving_average(values, window=7):
    """Moving average that skips None values and aligns to the same timeline."""
    if window <= 1:
        return values
    result = []
    for i in range(len(values)):
        # Only emit an averaged value on days that actually have a data point.
        if values[i] is None:
            result.append(None)
            continue
        chunk = values[max(0, i - window + 1):i + 1]
        numeric = [v for v in chunk if v is not None]
        if not numeric:
            result.append(None)
        else:
            result.append(round(sum(numeric) / len(numeric), 2))
    return result


def _load_history_entries_for_user(user_id):
    """
    Load history with DB-first strategy and legacy JSON fallback:
    - Prefer structured DB entries from AssessmentEntry.
    - Include older legacy JSON entries that predate the first DB entry.
    """
    db_entries = AssessmentEntry.query.filter_by(user_id=user_id).order_by(AssessmentEntry.created_at.asc()).all()
    db_history = [entry.to_history_dict() for entry in db_entries]

    json_history = StressHistory(user_id=user_id).load_history()
    if not db_history:
        return json_history
    if not json_history:
        return db_history

    first_db_dt = _parse_entry_datetime(db_history[0].get("date"))
    legacy_entries = []
    for entry in json_history:
        dt = _parse_entry_datetime(entry.get("date"))
        if not dt:
            continue
        if first_db_dt and dt < first_db_dt:
            legacy_entries.append(entry)

    combined = legacy_entries + db_history
    combined.sort(key=lambda e: _parse_entry_datetime(e.get("date")) or datetime.min)
    return combined


def _compute_top_factors(s1, s2, quiz_score, quiz_completed, sentiment=None):
    """Return a ranked list of (label, value_note) contributing factors."""
    factors = []
    if s1['sleep'] < 6:
        factors.append(('💤 Low sleep', f"{s1['sleep']}h — below recommended 7–8h"))
    if s1['study'] > 8:
        factors.append(('📚 High study load', f"{s1['study']}h per day"))
    if s1['screen_time'] > 7:
        factors.append(('📱 High screen time', f"{s1['screen_time']}h — consider digital breaks"))
    if s2['mood'] < 4:
        factors.append(('😔 Low mood', f"{s2['mood']}/10"))
    if s2['deadline'] == 'urgent':
        factors.append(('⏳ Urgent deadline pressure', 'Active urgent deadline'))
    if s2['financial_stress'] >= 7:
        factors.append(('💸 High financial stress', f"{s2['financial_stress']}/10"))
    if s2['procrastination'] == 'high':
        factors.append(('⏱ High procrastination', 'Frequent task avoidance'))
    if s2['social_interaction'] < 3:
        factors.append(('🤝 Low social support', f"{s2['social_interaction']}/10"))
    if s2['activity'] == 'none':
        factors.append(('🏃 No physical activity', 'Exercise significantly reduces stress'))
    if quiz_completed and quiz_score and quiz_score > 70:
        factors.append(('📝 High quiz stress score', f"{quiz_score:.0f}/100"))
    if sentiment and float(sentiment.get('polarity', 0.0)) < -0.25:
        factors.append(('🗒 Negative journal tone', 'Your reflection language suggests elevated emotional strain'))
    return factors[:5] or [('✅ No major stressors detected', 'Keep up the balance!')]


def _generate_tips(s1, s2, stress_score, sentiment=None):
    """Generate 2–3 personalised, actionable tips."""
    tips = []
    if s1['sleep'] < 7:
        tips.append("🌙 Aim for 7–8 hours of sleep. Set a consistent bedtime to improve sleep quality.")
    if s1['screen_time'] > 6:
        tips.append("📵 Try a 20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds.")
    if s2['activity'] in ('none', 'light'):
        tips.append("🚶 Even a 20-minute walk daily can significantly lower cortisol levels.")
    if s2['procrastination'] == 'high':
        tips.append("✅ Break big tasks into 5-minute micro-tasks. Start with the easiest one.")
    if s2['social_interaction'] < 4:
        tips.append("💬 Reach out to one person today — even a short chat can boost mood.")
    if s2['financial_stress'] >= 7:
        tips.append("💡 Write down one small financial action you can take this week to reduce uncertainty.")
    if sentiment and float(sentiment.get('polarity', 0.0)) < -0.25:
        tips.append("🗒 Try a two-line journal reframe: name the stressor, then write one next action you can control.")
    if stress_score > 70:
        tips.append("🧘 Practice 5 minutes of deep breathing or guided meditation to lower immediate stress.")
    return tips[:3] if tips else ["🌿 You're doing well. Maintain your current routine and check in again tomorrow."]


def _build_explanation(stress_score, s1, s2, quiz_completed, sentiment=None):
    """Return a plain-language explanation of the stress score."""
    base = (
        f"Your overall stress score is <strong>{stress_score:.0f}/100</strong>. "
    )
    if stress_score > 70:
        base += ("This is in the <strong>high</strong> range. Your body and mind are likely under significant pressure. "
                 "Prioritising rest, reducing your workload, and seeking social support can help.")
    elif stress_score > 40:
        base += ("This is in the <strong>moderate</strong> range. There are a few areas of your lifestyle "
                 "that are adding pressure. Small consistent changes often make the biggest difference.")
    else:
        base += ("This is in the <strong>low</strong> range — great news! You're managing your lifestyle well. "
                 "Keep up your healthy habits.")
    if sentiment:
        polarity = float(sentiment.get('polarity', 0.0))
        if polarity < -0.25:
            base += " Your journal tone appeared negative, which often aligns with temporary emotional load."
        elif polarity > 0.25:
            base += " Your journal tone appeared positive, which is a protective signal for recovery."
    if not quiz_completed:
        base += (" <em>(Note: this is an estimated score. Completing the quiz gives a more precise result.)</em>")
    return base


def _generate_insights(entries):
    """Compute simple insight callouts for the trends page."""
    insights = []
    if len(entries) < 3:
        return insights
    low_sleep_high_stress = [
        e for e in entries
        if e.get('sleep', 10) < 6 and e.get('stress_score', 0) > 65
    ]
    if low_sleep_high_stress:
        insights.append("😴 Stress spikes when sleep drops below 6 hours in your history.")
    high_screen = [e for e in entries if e.get('screen_time', 0) > 8]
    if len(high_screen) >= 2:
        avg_stress_high_screen = sum(e.get('stress_score', 0) for e in high_screen) / len(high_screen)
        insights.append(f"📱 On days with >8h screen time your average stress is {avg_stress_high_screen:.0f}.")
    scores = [e.get('stress_score', 0) for e in entries]
    if len(scores) >= 2 and scores[-1] < scores[0]:
        improvement = scores[0] - scores[-1]
        if improvement > 5:
            insights.append(f"📉 Your stress has improved by {improvement:.0f} points over this period. Keep going!")
    return insights


def update_user_goals(user_id, current_stress, history_manager):
    """Update goal progress based on current stress assessment."""
    active_goals = Goal.query.filter_by(user_id=user_id, status='active').all()
    history_data = history_manager.load_history()

    for goal in active_goals:
        if goal.goal_type == 'avg_stress' and len(history_data) > 0:
            avg_stress = sum(entry['stress_score'] for entry in history_data) / len(history_data)
            goal.current_value = avg_stress
        elif goal.goal_type == 'peak_stress' and len(history_data) > 0:
            peak_stress = max(entry['stress_score'] for entry in history_data)
            goal.current_value = peak_stress

        if goal.is_achieved() and goal.status == 'active':
            goal.status = 'completed'
            goal.completed_at = datetime.utcnow()
            flash(f'🎉 Goal achieved: {goal.description}', 'success')

    db.session.commit()


# ============ Database Initialization ============

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, port=5001)
