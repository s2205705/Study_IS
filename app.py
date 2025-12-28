from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, User, Challenge, GameProgress, MultiplayerStats, Achievement, Leaderboard
from database import encrypt_data, decrypt_data
import json
from datetime import datetime
import hashlib
import random

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)

# Initialize database
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        theme = request.form.get('theme', 'cute')
        
        # Validate input
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))
        
        # Check if user exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists', 'error')
            return redirect(url_for('register'))
        
        # Create user
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            theme_preference=theme
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Create multiplayer stats for user
            stats = MultiplayerStats(user_id=user.id)
            db.session.add(stats)
            db.session.commit()
            
            # Set session
            session['user_id'] = user.id
            session['username'] = user.username
            session['theme'] = user.theme_preference
            
            flash('Registration successful! Welcome to Python Pathfinder!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter username and password', 'error')
            return redirect(url_for('login'))
        
        # Find user by username or email
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        
        if user:
            # Verify password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user.password_hash == password_hash:
                # Update last login
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Set session
                session['user_id'] = user.id
                session['username'] = user.username
                session['theme'] = user.theme_preference
                
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    # Get user stats
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Calculate stats
    total_score = db.session.query(db.func.sum(GameProgress.score)).filter(
        GameProgress.user_id == user_id
    ).scalar() or 0
    
    levels_completed = db.session.query(db.func.count(GameProgress.level)).filter(
        GameProgress.user_id == user_id
    ).scalar() or 0
    
    highest_level = db.session.query(db.func.max(GameProgress.level)).filter(
        GameProgress.user_id == user_id
    ).scalar() or 1
    
    stats = {
        'total_score': total_score,
        'levels_completed': levels_completed,
        'highest_level': highest_level
    }
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         theme=session.get('theme', 'cute'),
                         stats=stats)

@app.route('/game/<int:level>')
def game(level):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get challenge for this level
    challenge = Challenge.query.filter_by(level=level).first()
    if not challenge:
        # Create a default challenge if none exists
        challenge = {
            'title': f'Level {level}',
            'description': 'Complete the challenge to proceed!',
            'points': 100,
            'difficulty': 'beginner'
        }
    
    return render_template('game.html', 
                         level=level, 
                         challenge=challenge,
                         theme=session.get('theme', 'cute'))

@app.route('/multiplayer')
def multiplayer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get available challenges for multiplayer
    challenges = Challenge.query.filter_by(is_active=True).limit(5).all()
    return render_template('multiplayer.html', 
                         theme=session.get('theme', 'cute'),
                         challenges=challenges)

@app.route('/lessons/<topic>')
def lessons(topic):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    lessons_data = {
        'python_basics': {
            'title': 'Python Fundamentals',
            'content': [
                'Variables and Data Types',
                'Control Structures',
                'Functions',
                'Lists and Dictionaries',
                'File Handling'
            ]
        },
        'web_basics': {
            'title': 'Web Development',
            'content': [
                'HTML Structure',
                'CSS Styling',
                'JavaScript Basics',
                'HTTP Protocol',
                'Flask Framework'
            ]
        },
        'advanced_python': {
            'title': 'Advanced Python',
            'content': [
                'Object-Oriented Programming',
                'Decorators and Generators',
                'Context Managers',
                'Async Programming',
                'Testing and Debugging'
            ]
        },
        'database': {
            'title': 'Database Fundamentals',
            'content': [
                'SQL Basics',
                'Database Design',
                'ORM with SQLAlchemy',
                'Migrations',
                'Performance Optimization'
            ]
        }
    }
    
    lesson = lessons_data.get(topic, {
        'title': 'Topic Not Found',
        'content': ['This lesson is under construction!']
    })
    
    return render_template('lessons.html', 
                         topic=topic, 
                         lesson=lesson,
                         theme=session.get('theme', 'cute'))

@app.route('/save_progress', methods=['POST'])
def save_user_progress():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.json
        user_id = session['user_id']
        
        # Encrypt code solution
        encrypted_solution = encrypt_data({
            'code': data.get('code_solution', ''),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Save progress
        progress = GameProgress(
            user_id=user_id,
            level=data.get('level', 1),
            score=data.get('score', 0),
            code_solution=encrypted_solution,
            time_taken=data.get('time_taken'),
            attempts=data.get('attempts', 1)
        )
        
        db.session.add(progress)
        db.session.commit()
        
        # Check for achievements
        check_achievements(user_id)
        
        return jsonify({'status': 'success', 'message': 'Progress saved'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/leaderboard')
def get_leaderboard():
    # Get top players
    top_players = Leaderboard.query.order_by(
        Leaderboard.total_score.desc()
    ).limit(20).all()
    
    leaderboard_data = []
    for player in top_players:
        leaderboard_data.append({
            'username': player.user.username,
            'total_score': player.total_score,
            'levels_completed': player.levels_completed,
            'multiplayer_rating': player.multiplayer_rating
        })
    
    return jsonify(leaderboard_data)

@app.route('/user_stats')
def get_user_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    # Get basic stats
    total_score = db.session.query(db.func.sum(GameProgress.score)).filter(
        GameProgress.user_id == user_id
    ).scalar() or 0
    
    levels_completed = db.session.query(db.func.count(GameProgress.level)).filter(
        GameProgress.user_id == user_id
    ).scalar() or 0
    
    # Get multiplayer stats
    multiplayer_stats = MultiplayerStats.query.filter_by(user_id=user_id).first()
    
    stats = {
        'total_score': total_score,
        'levels_completed': levels_completed,
        'multiplayer_wins': multiplayer_stats.wins if multiplayer_stats else 0,
        'multiplayer_losses': multiplayer_stats.losses if multiplayer_stats else 0,
        'multiplayer_rating': multiplayer_stats.rating if multiplayer_stats else 1000
    }
    
    return jsonify(stats)

@app.route('/update_theme', methods=['POST'])
def update_theme():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.json
        new_theme = data.get('theme', 'cute')
        
        if new_theme not in ['cute', 'deadly']:
            return jsonify({'error': 'Invalid theme'}), 400
        
        # Update user preference
        user = User.query.get(session['user_id'])
        user.theme_preference = new_theme
        db.session.commit()
        
        # Update session
        session['theme'] = new_theme
        
        return jsonify({'status': 'success', 'theme': new_theme})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        user_id = session['user_id']
        username = session['username']
        
        emit('user_connected', {
            'userId': user_id,
            'username': username
        }, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if 'user_id' in session:
        user_id = session['user_id']
        username = session['username']
        
        emit('user_disconnected', {
            'userId': user_id,
            'username': username
        }, broadcast=True)

@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('room')
    username = data.get('username', 'Anonymous')
    
    if room:
        join_room(room)
        emit('message', {
            'type': 'system',
            'message': f'{username} has joined the room'
        }, room=room)

@socketio.on('leave_room')
def handle_leave_room(data):
    room = data.get('room')
    username = data.get('username', 'Anonymous')
    
    if room:
        leave_room(room)
        emit('message', {
            'type': 'system',
            'message': f'{username} has left the room'
        }, room=room)

@socketio.on('create_room')
def handle_create_room(data):
    room_id = f"room_{random.randint(1000, 9999)}"
    username = data.get('username', 'Anonymous')
    
    join_room(room_id)
    emit('room_created', {
        'roomId': room_id,
        'creator': username,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room_id)

@socketio.on('challenge_submit')
def handle_challenge_submit(data):
    room = data.get('room')
    username = data.get('username')
    code = data.get('code', '')
    challenge_id = data.get('challenge_id')
    
    # Evaluate code (simplified)
    result = evaluate_code(code, challenge_id)
    
    emit('challenge_result', {
        'username': username,
        'result': result,
        'score': result.get('score', 0),
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)

def evaluate_code(code, challenge_id):
    """Evaluate submitted code against challenge requirements"""
    try:
        # In a real implementation, this would:
        # 1. Get challenge test cases
        # 2. Execute code in a sandbox
        # 3. Compare results
        
        # For now, return a mock result
        passed = random.random() > 0.3  # 70% chance of passing
        
        return {
            'passed': passed,
            'output': 'Challenge completed!' if passed else 'Some test cases failed',
            'score': 100 if passed else 0,
            'errors': [] if passed else ['Test case 1 failed', 'Test case 3 failed']
        }
    except Exception as e:
        return {
            'passed': False,
            'output': f'Execution error: {str(e)}',
            'score': 0,
            'errors': [str(e)]
        }

def check_achievements(user_id):
    """Check and award achievements based on user progress"""
    try:
        # Get user's progress
        progress_count = GameProgress.query.filter_by(user_id=user_id).count()
        total_score = db.session.query(db.func.sum(GameProgress.score)).filter(
            GameProgress.user_id == user_id
        ).scalar() or 0
        
        # Check for "First Steps" achievement
        if progress_count >= 1:
            award_achievement(user_id, 'complete_level_1')
        
        # Check for "Python Prodigy" achievement
        python_challenges = GameProgress.query.join(Challenge).filter(
            GameProgress.user_id == user_id,
            Challenge.category == 'python'
        ).count()
        
        if python_challenges >= 5:
            award_achievement(user_id, 'complete_5_python_challenges')
        
        # Check for high score achievement
        if total_score >= 1000:
            award_achievement(user_id, 'score_1000_points')
            
    except Exception as e:
        print(f"Error checking achievements: {e}")

def award_achievement(user_id, criteria):
    """Award an achievement to a user"""
    try:
        achievement = Achievement.query.filter_by(criteria=criteria).first()
        if not achievement:
            return
        
        # Check if user already has this achievement
        from models import UserAchievement
        existing = UserAchievement.query.filter_by(
            user_id=user_id,
            achievement_id=achievement.id
        ).first()
        
        if not existing:
            # Award achievement
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id
            )
            db.session.add(user_achievement)
            db.session.commit()
            
            # Notify user via Socket.IO
            socketio.emit('achievement_unlocked', {
                'userId': user_id,
                'achievement': achievement.to_dict()
            }, room=f"user_{user_id}")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error awarding achievement: {e}")

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', theme=session.get('theme', 'cute')), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', theme=session.get('theme', 'cute')), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)