#!/usr/bin/env python3
"""
Script to create sample game data for testing
"""

import sys
import os
import json
from datetime import datetime, timedelta
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, GameProgress, Challenge, Achievement, MultiplayerStats

def create_sample_users():
    """Create sample users"""
    print("👥 Creating sample users...")
    
    users_data = [
        {
            'username': 'coder_pro',
            'email': 'pro@example.com',
            'password_hash': 'hashed_password_123',  # In real app, use proper hashing
            'theme_preference': 'deadly',
            'is_admin': False
        },
        {
            'username': 'web_wizard',
            'email': 'wizard@example.com',
            'password_hash': 'hashed_password_456',
            'theme_preference': 'cute',
            'is_admin': False
        },
        {
            'username': 'python_ninja',
            'email': 'ninja@example.com',
            'password_hash': 'hashed_password_789',
            'theme_preference': 'deadly',
            'is_admin': False
        },
        {
            'username': 'html_hero',
            'email': 'hero@example.com',
            'password_hash': 'hashed_password_101',
            'theme_preference': 'cute',
            'is_admin': False
        },
        {
            'username': 'admin',
            'email': 'admin@example.com',
            'password_hash': 'hashed_password_admin',
            'theme_preference': 'cute',
            'is_admin': True
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        user.created_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        users.append(user)
        db.session.add(user)
    
    db.session.commit()
    print(f"✅ Created {len(users)} sample users")
    return users

def create_sample_progress(users, challenges):
    """Create sample game progress for users"""
    print("📊 Creating sample game progress...")
    
    for user in users:
        # Each user completes random challenges
        completed_challenges = random.sample(challenges, random.randint(3, len(challenges)))
        
        for challenge in completed_challenges:
            progress = GameProgress(
                user_id=user.id,
                level=challenge.level,
                score=challenge.points - random.randint(0, 20),
                code_solution=f"# Solution for {challenge.title}\ndef solution():\n    return 'completed'",
                completed_at=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                time_taken=random.randint(30, 300),
                attempts=random.randint(1, 3)
            )
            db.session.add(progress)
    
    db.session.commit()
    print("✅ Created sample game progress")

def create_sample_multiplayer_stats(users):
    """Create sample multiplayer stats"""
    print("⚔️ Creating sample multiplayer stats...")
    
    for user in users:
        wins = random.randint(0, 20)
        losses = random.randint(0, 15)
        draws = random.randint(0, 5)
        total = wins + losses + draws
        
        stats = MultiplayerStats(
            user_id=user.id,
            wins=wins,
            losses=losses,
            draws=draws,
            total_matches=total,
            win_streak=random.randint(0, 10),
            max_win_streak=random.randint(5, 15),
            rating=1000 + random.randint(-200, 200),
            last_match=datetime.utcnow() - timedelta(days=random.randint(0, 3))
        )
        db.session.add(stats)
    
    db.session.commit()
    print("✅ Created sample multiplayer stats")

def assign_sample_achievements(users, achievements):
    """Assign random achievements to users"""
    print("🏆 Assigning sample achievements...")
    
    from models import UserAchievement
    
    for user in users:
        # Each user gets random achievements
        user_achievements = random.sample(achievements, random.randint(1, len(achievements)))
        
        for achievement in user_achievements:
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id,
                unlocked_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(user_achievement)
    
    db.session.commit()
    print("✅ Assigned sample achievements")

def update_leaderboard(users):
    """Update leaderboard with user stats"""
    print("📈 Updating leaderboard...")
    
    from models import Leaderboard
    
    for user in users:
        # Calculate total score from progress
        total_score = db.session.query(db.func.sum(GameProgress.score)).filter(
            GameProgress.user_id == user.id
        ).scalar() or 0
        
        # Count completed levels
        levels_completed = db.session.query(db.func.count(GameProgress.level)).filter(
            GameProgress.user_id == user.id
        ).scalar() or 0
        
        # Get multiplayer rating
        stats = MultiplayerStats.query.filter_by(user_id=user.id).first()
        multiplayer_rating = stats.rating if stats else 1000
        
        leaderboard = Leaderboard(
            user_id=user.id,
            total_score=total_score,
            levels_completed=levels_completed,
            multiplayer_rating=multiplayer_rating
        )
        db.session.add(leaderboard)
    
    db.session.commit()
    print("✅ Updated leaderboard")

def create_additional_challenges():
    """Create additional sample challenges"""
    print("🎯 Creating additional challenges...")
    
    additional_challenges = [
        {
            'level': 4,
            'title': "CSS Styling",
            'description': "Style a button with hover effects using CSS",
            'category': "css",
            'difficulty': "beginner",
            'points': 120,
            'starter_code': "/* Style the button with the following properties:\n   - Background color: #ff4655\n   - Text color: white\n   - Padding: 10px 20px\n   - Add hover effect */\n\n.button {\n    /* Your code here */\n}",
            'solution_code': ".button {\n    background-color: #ff4655;\n    color: white;\n    padding: 10px 20px;\n    border: none;\n    border-radius: 5px;\n    cursor: pointer;\n    transition: background-color 0.3s;\n}\n\n.button:hover {\n    background-color: #ff6b7a;\n}",
            'learning_objectives': "Learn CSS properties, hover effects, and transitions"
        },
        {
            'level': 5,
            'title': "JavaScript Function",
            'description': "Create a function that toggles an element's visibility",
            'category': "javascript",
            'difficulty': "beginner",
            'points': 130,
            'starter_code': "// Create a function that toggles an element's visibility\nfunction toggleVisibility(elementId) {\n    // Your code here\n}",
            'solution_code': "function toggleVisibility(elementId) {\n    const element = document.getElementById(elementId);\n    if (element.style.display === 'none') {\n        element.style.display = 'block';\n    } else {\n        element.style.display = 'none';\n    }\n}",
            'learning_objectives': "Learn DOM manipulation and JavaScript functions"
        },
        {
            'level': 6,
            'title': "Python Lists",
            'description': "Create a function that filters even numbers from a list",
            'category': "python",
            'difficulty': "intermediate",
            'points': 150,
            'starter_code': "def filter_even_numbers(numbers):\n    \"\"\"Return a new list containing only even numbers\"\"\"\n    # Your code here\n    pass",
            'solution_code': "def filter_even_numbers(numbers):\n    return [num for num in numbers if num % 2 == 0]",
            'learning_objectives': "Learn list comprehensions and filtering in Python"
        }
    ]
    
    challenges = []
    for challenge_data in additional_challenges:
        challenge = Challenge(
            level=challenge_data['level'],
            title=challenge_data['title'],
            description=challenge_data['description'],
            category=challenge_data['category'],
            difficulty=challenge_data['difficulty'],
            points=challenge_data['points'],
            starter_code=challenge_data['starter_code'],
            solution_code=challenge_data['solution_code'],
            learning_objectives=challenge_data['learning_objectives']
        )
        challenges.append(challenge)
        db.session.add(challenge)
    
    db.session.commit()
    print(f"✅ Created {len(challenges)} additional challenges")
    return challenges

def main():
    """Main function to create all sample data"""
    print("=" * 50)
    print("Python Pathfinder Sample Data Creator")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Get existing data
            existing_challenges = Challenge.query.all()
            existing_achievements = Achievement.query.all()
            
            # Create sample users
            users = create_sample_users()
            
            # Create additional challenges if needed
            if len(existing_challenges) < 10:
                additional_challenges = create_additional_challenges()
                all_challenges = existing_challenges + additional_challenges
            else:
                all_challenges = existing_challenges
            
            # Create sample progress
            create_sample_progress(users, all_challenges)
            
            # Create multiplayer stats
            create_sample_multiplayer_stats(users)
            
            # Assign achievements
            if existing_achievements:
                assign_sample_achievements(users, existing_achievements)
            
            # Update leaderboard
            update_leaderboard(users)
            
            print("\n🎉 Sample data creation complete!")
            print(f"📊 Total users: {len(users)}")
            print(f"🎯 Total challenges: {len(all_challenges)}")
            print(f"🏆 Total achievements: {len(existing_achievements)}")
            
            print("\n🔧 You can now run the application with:")
            print("   $ python app.py")
            
        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
            db.session.rollback()

if __name__ == '__main__':
    main()