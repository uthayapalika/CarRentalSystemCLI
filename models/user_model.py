import sqlite3
import bcrypt
from datetime import datetime
from database import Database 

class UserModel:
    def __init__(self):
            self.db = db

    def get_connection(self):
        """Get database connection"""
        if not self.connection:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
        self.connection.row_factory = sqlite3.Row
        return self.connection

    def hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except:
            return False

    def authenticate_user(self, username, password):
        """Authenticate user with bcrypt password verification"""
        query = "SELECT * FROM users WHERE username = ?"
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            
            if user and self.verify_password(password, user['password']):
                return True, dict(user)
            return False, None
        except sqlite3.Error as e:
            print(f"❌ Authentication error: {e}")
            return False, None
        finally:
            cursor.close()

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        query = "SELECT id, username, role, created_at FROM users WHERE id = ?"
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
        except sqlite3.Error as e:
            print(f"❌ Error getting user: {e}")
            return None
        finally:
            cursor.close()

    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                cursor.close()
                return results

            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id

        except sqlite3.Error as e:
            conn.rollback()
            cursor.close()
            print(f"❌ Query error: {e}")
            return None

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None