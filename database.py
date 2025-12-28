import sqlite3
import hashlib
import json
from cryptography.fernet import Fernet
import base64
from datetime import datetime

# Generate a key for encryption (store securely in production)
key = Fernet.generate_key()
cipher_suite = Fernet(key)

class Database:
    def __init__(self, db_name='python_pathfinder.db'):
        self.db_name = db_name
        self.init_tables()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                theme_preference TEXT DEFAULT 'cute',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Game progress table (encrypted)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                level INTEGER NOT NULL,
                score INTEGER DEFAULT 0,
                code_solution TEXT,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Challenges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                python_requirement TEXT,
                web_requirement TEXT,
                test_cases TEXT,
                difficulty TEXT,
                points INTEGER DEFAULT 100
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        if isinstance(data, dict):
            data = json.dumps(data)
        encrypted = cipher_suite.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data):
        """Decrypt encrypted data"""
        decoded = base64.b64decode(encrypted_data)
        decrypted = cipher_suite.decrypt(decoded)
        return json.loads(decrypted.decode())
    
    def create_user(self, username, email, password, theme='cute'):
        """Create a new user with encrypted password"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, theme_preference)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, theme))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, username, password):
        """Authenticate user and return user data if successful"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, theme_preference FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'theme_preference': user[2]
            }
        return None
    
    def save_game_progress(self, user_id, level, score, code_solution):
        """Save encrypted game progress"""
        encrypted_solution = self.encrypt_data({
            'code': code_solution,
            'saved_at': datetime.now().isoformat()
        })
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO game_progress (user_id, level, score, code_solution)
            VALUES (?, ?, ?, ?)
        ''', (user_id, level, score, encrypted_solution))
        
        conn.commit()
        conn.close()
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as levels_completed,
                SUM(score) as total_score,
                MAX(level) as highest_level
            FROM game_progress 
            WHERE user_id = ?
        ''', (user_id,))
        
        stats = cursor.fetchone()
        conn.close()
        
        return {
            'levels_completed': stats[0] or 0,
            'total_score': stats[1] or 0,
            'highest_level': stats[2] or 0
        }

# Initialize database
db = Database()

# Convenience functions
init_db = db.init_tables
create_user = db.create_user
authenticate_user = db.authenticate_user
save_progress = db.save_game_progress
get_user_stats = db.get_user_stats