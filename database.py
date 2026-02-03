from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and data isolation."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Goal(db.Model):
    """Goal model for tracking stress reduction targets."""
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Goal configuration
    goal_type = db.Column(db.String(50), nullable=False)  # 'avg_stress', 'peak_stress', 'streak_days'
    description = db.Column(db.String(255))
    target_value = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, default=0.0)
    
    # Time tracking
    deadline = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Status: 'active', 'completed', 'expired'
    status = db.Column(db.String(20), default='active')
    
    def calculate_progress(self):
        """Calculate goal progress as a percentage (0-100)."""
        if self.goal_type in ['avg_stress', 'peak_stress']:
            # Lower is better for stress goals
            if self.current_value <= self.target_value:
                return 100.0
            # Calculate how far we are from the target
            max_stress = 100.0  # Assuming stress is 0-100
            progress = max(0, (max_stress - self.current_value) / (max_stress - self.target_value) * 100)
            return min(100.0, progress)
        elif self.goal_type == 'streak_days':
            # Higher is better for streak goals
            progress = (self.current_value / self.target_value) * 100
            return min(100.0, progress)
        return 0.0
    
    def is_achieved(self):
        """Check if the goal has been achieved."""
        if self.goal_type in ['avg_stress', 'peak_stress']:
            return self.current_value <= self.target_value
        elif self.goal_type == 'streak_days':
            return self.current_value >= self.target_value
        return False
    
    def __repr__(self):
        return f'<Goal {self.goal_type}: {self.target_value}>'
