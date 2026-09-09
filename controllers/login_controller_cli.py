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
        self.model = None
        self.current_user = None
        
        # Initialize model
        self._init_model()
    
    def _init_model(self):
        """Initialize the model"""
        if self.model is None and self.db is not None:
            try:
                self.model = ModelFactory.create_model("customer", db=self.db)
                print("✅ CustomerModel initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing CustomerModel: {e}")
        return self.model
    
    def login(self, username, password):
        """Handle login process"""
        if not username or not password:
            return None
        
        # Initialize model if needed
        model = self._init_model()
        
        if model:
            try:
                success, user = model.authenticate_user(username, password)
                if success:
                    # Always fetch customer_id for all users (admin/manager/staff may not have one)
                    customer = self.get_customer_by_user_id(user.get('id'))
                    if customer:
                        user['customer_id'] = customer.get('customer_id')
                        # Also update name fields from customer table
                        if not user.get('first_name'):
                            user['first_name'] = customer.get('first_name')
                        if not user.get('last_name'):
                            user['last_name'] = customer.get('last_name')
                        if not user.get('email'):
                            user['email'] = customer.get('email')
                        if not user.get('phone'):
                            user['phone'] = customer.get('phone')
                    else:
                        # If no customer record, set customer_id to None
                        user['customer_id'] = None
                    
                    self.current_user = user
                    
                    # Debug: Print user info
                    print(f"  Debug: User logged in - ID: {user.get('id')}, Role: {user.get('role')}, Customer ID: {user.get('customer_id')}")
                    
                    return user
                else:
                    return None
            except Exception as e:
                self.parent.print_error(f"Authentication error: {str(e)}")
                return None
        else:
            self.parent.print_error("Database connection failed!")
            return None
    
    def get_customer_by_user_id(self, user_id):
        """Get customer by user ID"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT customer_id, first_name, last_name, email, phone, user_id
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
            return None
    
    def logout(self):
        """Handle logout"""
        self.current_user = None
        return True