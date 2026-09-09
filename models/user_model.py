# models/user_model.py
import sqlite3
import bcrypt
from datetime import datetime
from db_setup import Database


class UserModel:
    """User Model for database operations"""
    
    def __init__(self, db):
        """Initialize User Model"""
        # Handle both Database object and string path
        if isinstance(db, str):
            self.db = Database(db)
        else:
            self.db = db
        
        self.connection = None
        self.db_path = "car_rental_system.db"
        self.table_name = 'users'
    
    def get_connection(self):
        """Get database connection"""
        if hasattr(self.db, 'get_connection'):
            return self.db.get_connection()
        elif hasattr(self.db, 'connection'):
            return self.db.connection
        else:
            if not self.connection:
                self.connection = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False
                )
            self.connection.row_factory = sqlite3.Row
            return self.connection
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        if hasattr(self.db, 'hash_password'):
            return self.db.hash_password(password)
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        if hasattr(self.db, 'verify_password'):
            return self.db.verify_password(password, hashed_password)
        try:
            if isinstance(hashed_password, str):
                return bcrypt.checkpw(
                    password.encode('utf-8'), 
                    hashed_password.encode('utf-8')
                )
            else:
                return bcrypt.checkpw(
                    password.encode('utf-8'), 
                    hashed_password
                )
        except Exception as e:
            print(f"❌ Password verification error: {e}")
            return False
    
    def authenticate(self, username, password):
        """
        Authenticate user with bcrypt password verification
        
        Args:
            username (str): Username
            password (str): Password
        
        Returns:
            dict: User data if authenticated, None otherwise
        """
        # ✅ Use 'password' column - 'customer_id' does NOT exist in users table
        query = """
            SELECT 
                id,
                username,
                password,
                role,
                created_at,
                updated_at
            FROM users 
            WHERE username = ?
        """
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            
            if not user:
                print(f"❌ User not found: {username}")
                return None
            
            # Convert to dict
            if hasattr(user, 'keys'):
                user_dict = dict(user)
            else:
                columns = [description[0] for description in cursor.description]
                user_dict = dict(zip(columns, user))
            
            stored_password = user_dict.get('password')
            
            if not stored_password:
                print("❌ No password stored for user")
                return None
            
            # Verify password
            if self.verify_password(password, stored_password):
                # Remove password before returning
                user_dict.pop('password', None)
                print(f"✅ Authentication successful for: {username}")
                return user_dict
            else:
                print(f"❌ Password verification failed for: {username}")
                return None
            
        except sqlite3.Error as e:
            print(f"❌ Authentication error: {e}")
            return None
        finally:
            cursor.close()
            if not hasattr(self.db, 'get_connection'):
                conn.close()
    
    # Legacy method for backward compatibility
    def authenticate_user(self, username, password):
        """Legacy method - use authenticate() instead"""
        result = self.authenticate(username, password)
        return (result is not None), result
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        # ✅ Remove customer_id - it doesn't exist in users table
        query = """
            SELECT 
                id, 
                username, 
                role, 
                created_at, 
                updated_at
            FROM users 
            WHERE id = ?
        """
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return None
            
            if hasattr(user, 'keys'):
                return dict(user)
            else:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, user))
                
        except sqlite3.Error as e:
            print(f"❌ Error getting user: {e}")
            return None
        finally:
            cursor.close()
            if not hasattr(self.db, 'get_connection'):
                conn.close()
    
    def get_by_username(self, username):
        """Get user by username"""
        # ✅ Remove customer_id - it doesn't exist in users table
        query = """
            SELECT 
                id, 
                username, 
                role, 
                created_at, 
                updated_at
            FROM users 
            WHERE username = ?
        """
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            
            if not user:
                return None
            
            if hasattr(user, 'keys'):
                return dict(user)
            else:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, user))
                
        except sqlite3.Error as e:
            print(f"❌ Error getting user: {e}")
            return None
        finally:
            cursor.close()
            if not hasattr(self.db, 'get_connection'):
                conn.close()
    
    def create(self, data):
        """
        Create a new user
        
        Args:
            data (dict): User data with keys:
                - username, password, role
        
        Returns:
            int: User ID if successful
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Hash the password
            hashed_password = self.hash_password(data.get('password', ''))
            
            # ✅ Remove customer_id - it doesn't exist in users table
            cursor.execute('''
                INSERT INTO users (username, password, role, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data.get('username'),
                hashed_password,
                data.get('role', 'staff'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
            
        except sqlite3.IntegrityError as e:
            conn.rollback()
            if "UNIQUE constraint failed: users.username" in str(e):
                raise ValueError("Username already exists!")
            raise ValueError(f"Database integrity error: {str(e)}")
        except sqlite3.Error as e:
            conn.rollback()
            raise sqlite3.Error(f"Database error: {str(e)}")
        finally:
            cursor.close()
            if not hasattr(self.db, 'get_connection'):
                conn.close()
    
    def update(self, user_id, data):
        """Update user information"""
        update_fields = []
        params = []
        
        if 'username' in data:
            update_fields.append("username = ?")
            params.append(data['username'])
        if 'password' in data and data['password']:
            hashed_password = self.hash_password(data['password'])
            update_fields.append("password = ?")
            params.append(hashed_password)
        if 'role' in data:
            update_fields.append("role = ?")
            params.append(data['role'])
        
        if not update_fields:
            return True
        
        update_fields.append("updated_at = ?")
        params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            conn.rollback()
            raise sqlite3.Error(f"Database error: {str(e)}")
        finally:
            cursor.close()
            if not hasattr(self.db, 'get_connection'):
                conn.close()
    
    def delete(self, user_id):
        """Delete a user"""
        query = "DELETE FROM users WHERE id = ?"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            conn.rollback()
            raise sqlite3.Error(f"Database error: {str(e)}")
        finally:
            cursor.close()
            if not hasattr(self.db, 'get_connection'):
                conn.close()
    
    def get_all(self):
        """Get all users"""
        # ✅ Remove customer_id - it doesn't exist in users table
        query = """
            SELECT 
                id,
                username,
                role,
                created_at,
                updated_at
            FROM users
            ORDER BY username
        """
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            
            if results and hasattr(results[0], 'keys'):
                return [dict(row) for row in results]
            else:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in results]
                
        except sqlite3.Error as e:
            print(f"❌ Error fetching users: {e}")
            return []
        finally:
            cursor.close()
            if not hasattr(self.db, 'get_connection'):
                conn.close()
    
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
                if results and hasattr(results[0], 'keys'):
                    return [dict(row) for row in results]
                else:
                    columns = [description[0] for description in cursor.description]
                    return [dict(zip(columns, row)) for row in results]
            
            conn.commit()
            last_id = cursor.lastrowid
            return last_id
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"❌ Query error: {e}")
            return None
        finally:
            cursor.close()
            if not hasattr(self.db, 'get_connection'):
                conn.close()
    
    def close(self):
        """Close database connection"""
        if hasattr(self.db, 'close'):
            self.db.close()
        elif self.connection:
            self.connection.close()
            self.connection = None