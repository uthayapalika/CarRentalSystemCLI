import sqlite3
from datetime import datetime
import bcrypt
from db_setup import Database  


class CustomerModel:
    def __init__(self, db):
        # Handle both Database object and string path
        if isinstance(db, str):
            self.db = Database(db)
        else:
            self.db = db
        
        # Initialize connection attribute for close method
        self.connection = None

    def get_connection(self):
        """Get database connection from the db object"""
        # If db has get_connection method, use it
        if hasattr(self.db, 'get_connection'):
            return self.db.get_connection()
        # Otherwise, create a new connection
        elif hasattr(self.db, 'connection'):
            return self.db.connection
        else:
            # Fallback: create a new connection
            import sqlite3
            return sqlite3.connect("car_rental_system.db")

    def hash_password(self, password):
        """Hash password using bcrypt"""
        if hasattr(self.db, 'hash_password'):
            return self.db.hash_password(password)
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        if hasattr(self.db, 'verify_password'):
            return self.db.verify_password(password, hashed_password)
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    def register_customer(self, customer_data):
        """Register a new customer with user account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            hashed_password = self.hash_password(customer_data['password'])
            
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (customer_data['username'], hashed_password, 'customer'))
            
            user_id = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO customers (
                    user_id, first_name, last_name, email, phone,
                    driver_license_num, address, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                customer_data['first_name'],
                customer_data['last_name'],
                customer_data['email'],
                customer_data['phone'],
                customer_data['driver_license_num'],
                customer_data['address'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            customer_id = cursor.lastrowid
            conn.commit()
            return True, customer_id, "Customer registered successfully!"
            
        except sqlite3.IntegrityError as e:
            conn.rollback()
            if "UNIQUE constraint failed: users.username" in str(e):
                return False, None, "Username already exists!"
            elif "UNIQUE constraint failed: customers.email" in str(e):
                return False, None, "Email already registered!"
            elif "UNIQUE constraint failed: customers.phone" in str(e):
                return False, None, "Phone number already registered!"
            elif "UNIQUE constraint failed: customers.driver_license_num" in str(e):
                return False, None, "Driver license number already registered!"
            return False, None, f"Database error: {str(e)}"
            
        except sqlite3.Error as e:
            conn.rollback()
            return False, None, f"Database error: {str(e)}"
        finally:
            cursor.close()

    def authenticate_user(self, username, password):
        """Authenticate user with bcrypt"""
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

    def get_all_customers(self):
        """Get all customers with user info"""
        query = '''
            SELECT 
                c.customer_id,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                c.driver_license_num,
                c.address,
                c.created_at,
                c.updated_at,
                u.id as user_id,
                u.username,
                u.role
            FROM customers c
            JOIN users u ON c.user_id = u.id
            ORDER BY c.created_at DESC
        '''
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except sqlite3.Error as e:
            print(f"❌ Error fetching customers: {e}")
            return []
        finally:
            cursor.close()

    def get_customer_by_id(self, customer_id):
        """Get customer by ID with user info"""
        query = '''
            SELECT 
                c.*,
                u.username,
                u.role
            FROM customers c
            JOIN users u ON c.user_id = u.id
            WHERE c.customer_id = ?
        '''
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, (customer_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            print(f"❌ Error fetching customer: {e}")
            return None
        finally:
            cursor.close()

    def delete_customer(self, customer_id):
        """Delete customer and associated user account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            cursor.execute("SELECT user_id FROM customers WHERE customer_id = ?", (customer_id,))
            result = cursor.fetchone()
            
            if result:
                user_id = result['user_id']
                cursor.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                return True, "Customer deleted successfully!"
            else:
                return False, "Customer not found!"
                
        except sqlite3.Error as e:
            conn.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            cursor.close()

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query, params=None):
        """Generic query executor"""
        return self.db.execute_query(query, params)