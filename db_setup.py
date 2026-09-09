import sqlite3
import os
from datetime import datetime
import bcrypt
from logger import logger

class Database:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Only initialize once"""
        if Database._initialized:
            return
            
        #self.db_path = "car_rental_system.db"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, "car_rental_system.db")
        self.connection = None
        self.setup_database()
        Database._initialized = True

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

    def setup_database(self):
        """Setup database and create tables"""
        connection = self.get_connection()
        cursor = connection.cursor()

        self.create_users_table(cursor)
        self.create_customers_table(cursor)
        self.create_vehicle_categories_table(cursor)
        self.create_vehicles_table(cursor)
        self.create_maintenance_table(cursor)
        self.create_bookings_table(cursor)
        self.create_payments_table(cursor)

        connection.commit()
        cursor.close()
        
        abs_path = os.path.abspath(self.db_path)
        print(f"Database created at: {abs_path}")

    def create_users_table(self, cursor):
        """Create users table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT CHECK(role IN ('admin', 'staff', 'manager', 'customer')) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("Users table created!")
        
        # Check for existing users and insert missing ones
        default_users = [
            ('admin', 'Admin123!', 'admin'),
            ('staff', 'Staff123!', 'staff'),
            ('manager', 'Manager123!', 'manager'),
            ('customer', 'Customer123!', 'customer')
        ]
        
        for username, password, role in default_users:
            # Check if user already exists
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = ?", (username,))
            count = cursor.fetchone()['count']
            
            if count == 0:
                hashed_password = self.hash_password(password)
                cursor.execute('''
                    INSERT INTO users (username, password, role)
                    VALUES (?, ?, ?)
                ''', (username, hashed_password, role))
                print(f"Default {role} created: {username} / {password}")
            else:
                print(f"User {username} already exists, skipping...")

    def create_customers_table(self, cursor):
        """Create customers table with foreign key to users"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                driver_license_num TEXT UNIQUE NOT NULL,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        print("Customers table created with user relationship!")
        
        # Create default customer profile if it doesn't exist
        cursor.execute("SELECT COUNT(*) as count FROM customers")
        count = cursor.fetchone()['count']
        
        if count == 0:
            # Get the customer user id
            cursor.execute("SELECT id FROM users WHERE username = 'customer'")
            user = cursor.fetchone()
            if user:
                cursor.execute('''
                    INSERT INTO customers (user_id, first_name, last_name, email, phone, driver_license_num, address)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user['id'],
                    'Default',
                    'Customer',
                    'customer@example.com',
                    '1234567890',
                    'DL123456',
                    '123 Main Street, City'
                ))
                print("Default customer profile created!")
            else:
                print("Customer user not found, skipping customer profile creation...")

    def create_vehicle_categories_table(self, cursor):
        """Create vehicle categories table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicle_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                base_rate DECIMAL(10,2) NOT NULL,
                late_fee_rate DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                category_status BOOLEAN DEFAULT 1
            )
        ''')
        print("Vehicle Categories table created!")   

    def create_vehicles_table(self, cursor):
        """Create vehicles table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                license_plate TEXT UNIQUE NOT NULL,
                color TEXT,
                mileage INTEGER DEFAULT 0,
                daily_rate DECIMAL(10,2) NOT NULL,
                status TEXT CHECK(status IN ('available', 'rented', 'maintenance', 'reserved')) 
                    DEFAULT 'available',
                fuel_type TEXT CHECK(fuel_type IN ('Petrol', 'Diesel', 'Electric', 'Hybrid')),
                min_rent_period INTEGER DEFAULT 1,
                max_rent_period INTEGER DEFAULT 30,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES vehicle_categories(id) ON DELETE CASCADE
            )
        ''')
        print("Vehicles table created!")

    def create_maintenance_table(self, cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance (
                maintenance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                maintenance_type TEXT NOT NULL,
                service_date DATE NOT NULL,
                odometer_reading INTEGER,
                cost DECIMAL(10,2) DEFAULT 0.00,
                service_provider TEXT,
                description TEXT,
                status TEXT DEFAULT 'pending',
                next_service_due DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
            )
        ''')
        print("Maintenance table created!")

    def create_bookings_table(self, cursor):
        """Create bookings table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_ref TEXT UNIQUE NOT NULL,
                customer_id INTEGER NOT NULL,
                vehicle_id INTEGER NOT NULL,

                start_date DATE NOT NULL,
                end_date DATE NOT NULL,

                pickup_location TEXT,
                dropoff_location TEXT,

                daily_rate DECIMAL(10,2) NOT NULL,
                total_days INTEGER NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                deposit_amount DECIMAL(10,2) DEFAULT 0.00,
                paid_amount DECIMAL(10,2) DEFAULT 0.00,
                balance_amount DECIMAL(10,2) DEFAULT 0.00,
                booking_status TEXT CHECK(
                    booking_status IN (
                        'pending',
                        'approved',
                        'rejected',
                        'active',
                        'completed',
                        'cancelled'
                    )
                ) DEFAULT 'pending',

                rejection_reason TEXT,

                approved_by INTEGER,
                approved_at TIMESTAMP,

                notes TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (customer_id)
                    REFERENCES customers(customer_id)
                    ON DELETE RESTRICT,

                FOREIGN KEY (vehicle_id)
                    REFERENCES vehicles(id)
                    ON DELETE RESTRICT,

                FOREIGN KEY (approved_by)
                    REFERENCES users(id)
                    ON DELETE SET NULL
            )
        ''')
        print("Bookings table created!")

    def create_payments_table(self, cursor):
        """Create payments table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,

                booking_id INTEGER NOT NULL,

                payment_type TEXT CHECK(
                    payment_type IN (
                        'deposit',
                        'final',
                        'refund'
                    )
                ) NOT NULL,

                amount DECIMAL(10,2) NOT NULL,

                payment_method TEXT CHECK(
                    payment_method IN (
                        'cash',
                        'card',
                        'bank_transfer',
                        'online'
                    )
                ) NOT NULL,

                payment_status TEXT CHECK(
                    payment_status IN (
                        'pending',
                        'paid',
                        'failed',
                        'refunded'
                    )
                ) DEFAULT 'pending',

                transaction_reference TEXT UNIQUE,

                payment_date TIMESTAMP,

                notes TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (booking_id)
                    REFERENCES bookings(booking_id)
                    ON DELETE RESTRICT
            )
        ''')
        print("Payments table created!")     

    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

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
            logger.error(f"Database query error: {e}", exc_info=True)
            return None

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    @classmethod
    def get_instance(cls):
        """Convenience method to get the singleton instance"""
        return cls()


if __name__ == "__main__":
    
    db = Database()
    db.close()
    print("Database setup complete!")