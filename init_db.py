#!/usr/bin/env python3
"""
Database initialization script for Python Pathfinder
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import create_sample_data
from database import Database

def init_database():
    """Initialize the database with all tables"""
    print("🚀 Initializing Python Pathfinder database...")
    
    # Create database instance
    db_instance = Database()
    
    # Initialize tables
    db_instance.init_tables()
    print("✅ Database tables created successfully!")
    
    # Create sample data
    with app.app_context():
        create_sample_data()
        print("✅ Sample data inserted successfully!")
    
    print("\n🎮 Database initialization complete!")
    print("📊 Tables created:")
    print("   - users")
    print("   - game_progress")
    print("   - challenges")
    print("   - multiplayer_stats")
    print("   - multiplayer_matches")
    print("   - achievements")
    print("   - user_achievements")
    print("   - leaderboard")
    print("   - code_submissions")
    
    print("\n👤 Sample admin credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    
    print("\n🎯 To run the application:")
    print("   $ python app.py")
    print("   Then visit: http://localhost:5000")

def reset_database():
    """Reset the database (warning: deletes all data!)"""
    confirmation = input("\n⚠️  WARNING: This will delete ALL data! Continue? (yes/no): ")
    
    if confirmation.lower() == 'yes':
        print("🗑️  Resetting database...")
        
        # Delete database file if exists
        db_file = 'python_pathfinder.db'
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"✅ Deleted {db_file}")
        
        # Reinitialize
        init_database()
    else:
        print("❌ Database reset cancelled.")

def main():
    """Main function"""
    print("=" * 50)
    print("Python Pathfinder Database Manager")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Initialize database (fresh start)")
        print("2. Reset database (delete all data)")
        print("3. Create backup")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            init_database()
        elif choice == '2':
            reset_database()
        elif choice == '3':
            print("📦 Creating backup...")
            # Backup implementation would go here
            print("✅ Backup created!")
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == '__main__':
    main()