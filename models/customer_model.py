# models/customer_model.py
import sqlite3
from datetime import datetime
import bcrypt
from db_setup import Database


class CustomerModel:
    """Customer Model for database operations"""
    
    def __init__(self, db):
        """
        Initialize Customer Model
        
        Args:
            db: Database connection object or connection string
        """
        # Handle both Database object and string path
        if isinstance(db, str):
            self.db = Database(db)
        else:
            self.db = db
        
        self.connection = None
        self.table_name = 'customers'
    
    def get_connection(self):
        """Get database connection from the db object"""
        if hasattr(self.db, 'get_connection'):
            return self.db.get_connection()
        elif hasattr(self.db, 'connection'):
            return self.db.connection
        else:
            # Fallback: create a new connection
            if not self.connection:
                self.connection = sqlite3.connect("car_rental_system.db")
                self.connection.row_factory = sqlite3.Row
            return self.connection
    
    def get_cursor(self, conn=None):
        """Get a database cursor"""
        if conn is None:
            conn = self.get_connection()
        return conn.cursor()
    
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
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
    def create(self, data):
        """
        Create a new customer
        
        Args:
            data (dict): Customer data with keys:
                - first_name, last_name, email, phone
                - address (optional), license_number (optional)
                - date_of_birth (optional)
                - username, password (optional - for creating user account)
        
        Returns:
            int: Customer ID if successful
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            # Check if user account should be created
            user_id = None
            if 'username' in data and 'password' in data:
                # Create user account first
                hashed_password = self.hash_password(data['password'])
                cursor.execute('''
                    INSERT INTO users (username, password, role, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    data['username'],
                    hashed_password,
                    'customer',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                user_id = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO customers (
                    user_id, first_name, last_name, email, phone, 
                    driver_license_num, address, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data.get('first_name'),
                data.get('last_name'),
                data.get('email'),
                data.get('phone'),
                data.get('license_number', ''),
                data.get('address', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            customer_id = cursor.lastrowid
            conn.commit()
            return customer_id
            
        except sqlite3.IntegrityError as e:
            conn.rollback()
            error_msg = str(e)
            if "UNIQUE constraint failed: customers.email" in error_msg:
                raise ValueError("Email already exists!")
            elif "UNIQUE constraint failed: customers.phone" in error_msg:
                raise ValueError("Phone number already exists!")
            elif "UNIQUE constraint failed: customers.driver_license_num" in error_msg:
                raise ValueError("License number already exists!")
            elif "UNIQUE constraint failed: users.username" in error_msg:
                raise ValueError("Username already exists!")
            else:
                raise ValueError(f"Database integrity error: {error_msg}")
                
        except sqlite3.Error as e:
            conn.rollback()
            raise sqlite3.Error(f"Database error: {str(e)}")
        finally:
            cursor.close()
            # ✅ DON'T close the connection here - let the Database singleton manage it
    
    def get_all(self, limit=None, offset=0):
        """
        Get all customers
        
        Args:
            limit (int): Maximum number of records to return
            offset (int): Number of records to skip
        
        Returns:
            list: List of customer dictionaries
        """
        query = '''
            SELECT 
                c.customer_id,
                c.user_id,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                c.driver_license_num,
                c.address,
                c.created_at,
                c.updated_at,
                u.username,
                u.role
            FROM customers c
            LEFT JOIN users u ON c.user_id = u.id
            ORDER BY c.last_name, c.first_name
        '''
        
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            return [dict(row) for row in results] if results else []
        except sqlite3.Error as e:
            print(f"❌ Error fetching customers: {e}")
            return []
        finally:
            cursor.close()
            # ✅ DON'T close the connection here
    
    def get_by_id(self, customer_id):
        """
        Get customer by ID
        
        Args:
            customer_id (int): Customer ID
        
        Returns:
            dict: Customer data or None if not found
        """
        query = '''
            SELECT 
                c.customer_id,
                c.user_id,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                c.driver_license_num,
                c.address,
                c.created_at,
                c.updated_at,
                u.username,
                u.role
            FROM customers c
            LEFT JOIN users u ON c.user_id = u.id
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
            # ✅ DON'T close the connection here
    
    def get_by_email(self, email):
        """
        Get customer by email
        
        Args:
            email (str): Customer email
        
        Returns:
            dict: Customer data or None if not found
        """
        query = '''
            SELECT 
                c.customer_id,
                c.user_id,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                c.driver_license_num,
                c.address,
                c.created_at,
                c.updated_at,
                u.username,
                u.role
            FROM customers c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.email = ?
        '''
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            print(f"❌ Error fetching customer: {e}")
            return None
        finally:
            cursor.close()
            # ✅ DON'T close the connection here
    
    def update(self, customer_id, data):
        """
        Update customer information
        
        Args:
            customer_id (int): Customer ID
            data (dict): Updated customer data
        
        Returns:
            bool: True if successful
        """
        update_fields = []
        params = []
        
        allowed_fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'driver_license_num', 'user_id'
        ]
        
        for field in allowed_fields:
            if field in data and data[field] is not None:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if not update_fields:
            return True
        
        update_fields.append("updated_at = ?")
        params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        params.append(customer_id)
        
        query = f'''
            UPDATE customers
            SET {', '.join(update_fields)}
            WHERE customer_id = ?
        '''
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            error_msg = str(e)
            if "UNIQUE constraint failed: customers.email" in error_msg:
                raise ValueError("Email already exists!")
            elif "UNIQUE constraint failed: customers.phone" in error_msg:
                raise ValueError("Phone number already exists!")
            elif "UNIQUE constraint failed: customers.driver_license_num" in error_msg:
                raise ValueError("License number already exists!")
            else:
                raise ValueError(f"Database integrity error: {error_msg}")
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error: {str(e)}")
        finally:
            cursor.close()
            # ✅ DON'T close the connection here
    
    def delete(self, customer_id):
        """
        Delete customer and associated user account
        
        Args:
            customer_id (int): Customer ID
        
        Returns:
            bool: True if successful
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            cursor.execute("SELECT user_id FROM customers WHERE customer_id = ?", (customer_id,))
            result = cursor.fetchone()
            
            if not result:
                raise ValueError("Customer not found!")
            
            user_id = result['user_id'] if hasattr(result, 'keys') else result[0]
            
            cursor.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
            
            if user_id:
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            conn.rollback()
            raise sqlite3.Error(f"Database error: {str(e)}")
        finally:
            cursor.close()
            # ✅ DON'T close the connection here
    
    def search(self, search_term):
        """
        Search customers by name, email, or phone
        
        Args:
            search_term (str): Search term
        
        Returns:
            list: List of matching customers
        """
        query = '''
            SELECT 
                c.customer_id,
                c.user_id,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                c.driver_license_num,
                c.address,
                c.created_at,
                c.updated_at,
                u.username,
                u.role
            FROM customers c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE 
                c.first_name LIKE ? OR 
                c.last_name LIKE ? OR 
                c.email LIKE ? OR 
                c.phone LIKE ?
            ORDER BY c.last_name, c.first_name
        '''
        
        search_pattern = f"%{search_term}%"
        params = [search_pattern, search_pattern, search_pattern, search_pattern]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results] if results else []
        except sqlite3.Error as e:
            print(f"❌ Error searching customers: {e}")
            return []
        finally:
            cursor.close()
            # ✅ DON'T close the connection here
    
    def get_by_user_id(self, user_id):
        """
        Get customer by user ID
        
        Args:
            user_id (int): User ID
        
        Returns:
            dict: Customer data or None if not found
        """
        query = '''
            SELECT 
                c.customer_id,
                c.user_id,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                c.driver_license_num,
                c.address,
                c.created_at,
                c.updated_at,
                u.username,
                u.role
            FROM customers c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.user_id = ?
        '''
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            print(f"❌ Error fetching customer by user_id: {e}")
            return None
        finally:
            cursor.close()
            # ✅ DON'T close the connection here
    
    def count(self):
        """Get total number of customers"""
        query = "SELECT COUNT(*) as total FROM customers"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            return result['total'] if hasattr(result, 'keys') else result[0]
        except sqlite3.Error as e:
            print(f"❌ Error counting customers: {e}")
            return 0
        finally:
            cursor.close()
            # ✅ DON'T close the connection here
    
    def get_customer_with_bookings(self, customer_id):
        """
        Get customer with their booking history
        
        Args:
            customer_id (int): Customer ID
        
        Returns:
            dict: Customer data with bookings
        """
        customer = self.get_by_id(customer_id)
        if not customer:
            return None
        
        # Get bookings
        booking_model = self.db.get_model('booking') if hasattr(self.db, 'get_model') else None
        if booking_model:
            bookings = booking_model.get_by_customer(customer_id)
            customer['bookings'] = bookings
        else:
            customer['bookings'] = []
        
        return customer
    
    def close(self):
        """Close database connection"""
        if hasattr(self.db, 'close'):
            self.db.close()
        elif self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query, params=None):
        """Generic query executor"""
        if hasattr(self.db, 'execute_query'):
            return self.db.execute_query(query, params)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                return [dict(row) for row in results] if results else []
            else:
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"❌ Query error: {e}")
            raise
        finally:
            cursor.close()
           