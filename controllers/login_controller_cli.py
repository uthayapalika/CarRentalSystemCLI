# controllers/login_controller_cli.py
"""
CLI Login Controller
"""
from factories import ModelFactory


class LoginControllerCLI:
    """CLI Login Controller"""
    
    def __init__(self, parent, db=None):
        self.parent = parent
        self.db = db
        self.user_model = None
        self.customer_model = None
        self.current_user = None
        
        # Initialize models
        self._init_models()
    
    def _init_models(self):
        """Initialize the models"""
        if self.db is not None:
            try:
                self.user_model = ModelFactory.create_model("user", db=self.db)
                print("✅ UserModel initialized successfully")
                
                self.customer_model = ModelFactory.create_model("customer", db=self.db)
                print("✅ CustomerModel initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing models: {e}")
        
        return self.user_model is not None
    
    def login(self, username, password):
        """Handle login process"""
        if not username or not password:
            return None
        
        # Initialize models if needed
        if not self._init_models():
            self.parent.print_error("Database connection failed!")
            return None
        
        try:
            # Use UserModel.authenticate()
            user = self.user_model.authenticate(username, password)
            
            if user:
                # Get customer details if user is a customer
                customer = self.get_customer_by_user_id(user.get('id'))
                if customer:
                    # ✅ Use 'customer_id' from the customers table
                    user['customer_id'] = customer.get('customer_id')
                    user['first_name'] = customer.get('first_name', '')
                    user['last_name'] = customer.get('last_name', '')
                    user['email'] = customer.get('email', '')
                    user['phone'] = customer.get('phone', '')
                else:
                    # Admin/Manager/Staff may not have customer record
                    user['customer_id'] = None
                    # For admin, use username as name
                    if not user.get('first_name'):
                        user['first_name'] = user.get('username', '')
                
                self.current_user = user
                
                # Debug: Print user info
                print(f"  Debug: User logged in - ID: {user.get('id')}, Role: {user.get('role')}, Customer ID: {user.get('customer_id')}")
                
                return user
            else:
                return None
                
        except Exception as e:
            self.parent.print_error(f"Authentication error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_customer_by_user_id(self, user_id):
        """Get customer by user ID"""
        try:
            if not self.customer_model:
                return None
            
            # Try using the customer model's method
            if hasattr(self.customer_model, 'get_by_user_id'):
                return self.customer_model.get_by_user_id(user_id)
            
            # Fallback: direct SQL query
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # ✅ Use correct column names from your schema
            cursor.execute("""
                SELECT 
                    customer_id,
                    user_id,
                    first_name,
                    last_name,
                    email,
                    phone,
                    driver_license_num,
                    address,
                    created_at,
                    updated_at
                FROM customers
                WHERE user_id = ?
            """, (user_id,))
            
            customer = cursor.fetchone()
            cursor.close()
            
            if customer:
                return dict(customer)
            return None
            
        except Exception as e:
            self.parent.print_error(f"Error fetching customer: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def logout(self):
        """Handle logout"""
        self.current_user = None
        return True
    
    def get_current_user(self):
        """Get current logged in user"""
        return self.current_user
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def get_user_role(self):
        """Get current user role"""
        if self.current_user:
            return self.current_user.get('role', 'staff')
        return None