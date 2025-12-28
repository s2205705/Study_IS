from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    theme_preference = db.Column(db.String(20), default='cute')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    progress = db.relationship('GameProgress', backref='user', lazy='dynamic')
    multiplayer_stats = db.relationship('MultiplayerStats', backref='user', uselist=False)
    achievements = db.relationship('Achievement', secondary='user_achievements', backref='users')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'theme_preference': self.theme_preference,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class GameProgress(db.Model):
    __tablename__ = 'game_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, default=0)
    code_solution = db.Column(db.Text)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_taken = db.Column(db.Integer)  # Time in seconds
    attempts = db.Column(db.Integer, default=1)
    
    # Index for faster queries
    __table_args__ = (
        db.Index('idx_user_level', 'user_id', 'level'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'level': self.level,
            'score': self.score,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'time_taken': self.time_taken,
            'attempts': self.attempts
        }

class Challenge(db.Model):
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # python, html, css, javascript, flask
    difficulty = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    points = db.Column(db.Integer, default=100)
    
    # Challenge requirements
    starter_code = db.Column(db.Text)
    solution_code = db.Column(db.Text)
    test_cases = db.Column(db.Text)  # JSON string of test cases
    hints = db.Column(db.Text)  # JSON string of hints
    learning_objectives = db.Column(db.Text)
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_test_cases(self):
        if self.test_cases:
            return json.loads(self.test_cases)
        return []
    
    def get_hints(self):
        if self.hints:
            return json.loads(self.hints)
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'level': self.level,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'points': self.points,
            'starter_code': self.starter_code,
            'learning_objectives': self.learning_objectives
        }

class MultiplayerStats(db.Model):
    __tablename__ = 'multiplayer_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    total_matches = db.Column(db.Integer, default=0)
    win_streak = db.Column(db.Integer, default=0)
    max_win_streak = db.Column(db.Integer, default=0)
    rating = db.Column(db.Integer, default=1000)  # Elo rating system
    last_match = db.Column(db.DateTime)
    
    def win_rate(self):
        if self.total_matches == 0:
            return 0
        return (self.wins / self.total_matches) * 100
    
    def to_dict(self):
        return {
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'total_matches': self.total_matches,
            'win_streak': self.win_streak,
            'max_win_streak': self.max_win_streak,
            'rating': self.rating,
            'win_rate': self.win_rate()
        }

class MultiplayerMatch(db.Model):
    __tablename__ = 'multiplayer_matches'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(50), nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    status = db.Column(db.String(20), default='waiting')  # waiting, active, completed, cancelled
    winner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    player1_score = db.Column(db.Integer, default=0)
    player2_score = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    player1 = db.relationship('User', foreign_keys=[player1_id])
    player2 = db.relationship('User', foreign_keys=[player2_id])
    winner = db.relationship('User', foreign_keys=[winner_id])
    challenge = db.relationship('Challenge')
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'player1': self.player1.username if self.player1 else None,
            'player2': self.player2.username if self.player2 else None,
            'status': self.status,
            'winner': self.winner.username if self.winner else None,
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    points = db.Column(db.Integer, default=10)
    criteria = db.Column(db.String(100))  # e.g., "complete_level_5", "win_10_matches"
    category = db.Column(db.String(50))  # learning, multiplayer, speed, accuracy
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'points': self.points,
            'criteria': self.criteria,
            'category': self.category
        }

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),
    )

class Leaderboard(db.Model):
    __tablename__ = 'leaderboard'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    total_score = db.Column(db.Integer, default=0)
    levels_completed = db.Column(db.Integer, default=0)
    multiplayer_rating = db.Column(db.Integer, default=1000)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User')
    
    def to_dict(self):
        return {
            'username': self.user.username,
            'total_score': self.total_score,
            'levels_completed': self.levels_completed,
            'multiplayer_rating': self.multiplayer_rating,
            'last_updated': self.last_updated.isoformat()
        }

class CodeSubmission(db.Model):
    __tablename__ = 'code_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), default='python')
    status = db.Column(db.String(20), default='pending')  # pending, success, error
    output = db.Column(db.Text)
    error_message = db.Column(db.Text)
    execution_time = db.Column(db.Float)  # in seconds
    memory_used = db.Column(db.Float)  # in MB
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User')
    challenge = db.relationship('Challenge')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'challenge_id': self.challenge_id,
            'language': self.language,
            'status': self.status,
            'output': self.output,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'memory_used': self.memory_used,
            'submitted_at': self.submitted_at.isoformat()
        }

# Initialize database function
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    return db

def create_sample_data():
    """Create sample challenges and achievements"""
    # Only create if tables are empty
    if Challenge.query.count() == 0:
        sample_challenges = [
            Challenge(
                level=1,
                title="Python Variables",
                description="Create a variable called 'name' and assign your username to it",
                category="python",
                difficulty="beginner",
                points=100,
                starter_code="# Create a variable called 'name'\n# and assign your username to it\n\n# Your code here\n",
                solution_code="name = 'your_username'",
                test_cases=json.dumps([
                    {"input": "", "expected": "variable 'name' exists", "type": "variable_check"}
                ]),
                hints=json.dumps([
                    "Use the assignment operator = to create a variable",
                    "Variable names should be descriptive and use lowercase letters",
                    "Strings in Python need to be enclosed in quotes"
                ]),
                learning_objectives="Understand how to create and assign values to variables in Python"
            ),
            Challenge(
                level=2,
                title="Basic Function",
                description="Create a function that adds two numbers and returns the result",
                category="python",
                difficulty="beginner",
                points=150,
                starter_code="# Create a function called add_numbers\n# that takes two parameters and returns their sum\n\ndef add_numbers(a, b):\n    # Your code here\n    pass",
                solution_code="def add_numbers(a, b):\n    return a + b",
                test_cases=json.dumps([
                    {"input": "add_numbers(2, 3)", "expected": "5", "type": "function_call"},
                    {"input": "add_numbers(-1, 1)", "expected": "0", "type": "function_call"},
                    {"input": "add_numbers(0, 0)", "expected": "0", "type": "function_call"}
                ]),
                learning_objectives="Learn function definition, parameters, and return statements"
            ),
            Challenge(
                level=3,
                title="HTML Basic Structure",
                description="Create a basic HTML page with a title and heading",
                category="html",
                difficulty="beginner",
                points=100,
                starter_code="<!-- Create a basic HTML structure -->\n<!DOCTYPE html>\n<html>\n<head>\n    <!-- Add title here -->\n</head>\n<body>\n    <!-- Add heading here -->\n</body>\n</html>",
                solution_code="<!DOCTYPE html>\n<html>\n<head>\n    <title>My First Web Page</title>\n</head>\n<body>\n    <h1>Welcome to Python Pathfinder!</h1>\n</body>\n</html>",
                learning_objectives="Understand HTML document structure, title and heading elements"
            )
        ]
        
        for challenge in sample_challenges:
            db.session.add(challenge)
        
        db.session.commit()
    
    # Create sample achievements
    if Achievement.query.count() == 0:
        sample_achievements = [
            Achievement(
                name="First Steps",
                description="Complete your first coding challenge",
                icon="🏆",
                points=10,
                criteria="complete_level_1",
                category="learning"
            ),
            Achievement(
                name="Python Prodigy",
                description="Complete 5 Python challenges",
                icon="🐍",
                points=50,
                criteria="complete_5_python_challenges",
                category="learning"
            ),
            Achievement(
                name="Multiplayer Champion",
                description="Win 10 multiplayer matches",
                icon="⚔️",
                points=100,
                criteria="win_10_matches",
                category="multiplayer"
            ),
            Achievement(
                name="Speed Coder",
                description="Complete a challenge in under 30 seconds",
                icon="⚡",
                points=30,
                criteria="fast_challenge_completion",
                category="speed"
            ),
            Achievement(
                name="Perfect Score",
                description="Get 100% on 5 challenges in a row",
                icon="💯",
                points=75,
                criteria="perfect_scores_streak",
                category="accuracy"
            )
        ]
        
        for achievement in sample_achievements:
            db.session.add(achievement)
        
        db.session.commit()