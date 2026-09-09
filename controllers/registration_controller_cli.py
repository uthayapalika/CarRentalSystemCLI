# controllers/registration_controller_cli.py
"""
CLI Registration Controller
"""
from controllers.customer_controller import CustomerController
from factories import ModelFactory


class RegistrationControllerCLI:
    """CLI Registration Controller"""
    
    def __init__(self, view=None, db=None):
        self.view = view
        self.db = db
        self.model = None
        self.login_controller = None
        
        # Initialize model
        self._init_model()
        
        # Use CustomerController for registration logic
        self.customer_controller = CustomerController(view, self.model)
    
    def _init_model(self):
        """Initialize the model"""
        if self.model is None and self.db is not None:
            try:
                self.model = ModelFactory.create_model("customer", db=self.db)
                print("✅ CustomerModel initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing CustomerModel: {e}")
        return self.model
    
    def register(self, data):
        """Handle registration"""
        # Validate required fields
        if not data.get('first_name'):
            return {'success': False, 'message': 'First name is required!'}
        if not data.get('last_name'):
            return {'success': False, 'message': 'Last name is required!'}
        if not data.get('email'):
            return {'success': False, 'message': 'Email is required!'}
        if not data.get('phone'):
            return {'success': False, 'message': 'Phone number is required!'}
        if not data.get('driver_license_num'):
            return {'success': False, 'message': 'Driver license number is required!'}
        if not data.get('username'):
            return {'success': False, 'message': 'Username is required!'}
        if not data.get('password'):
            return {'success': False, 'message': 'Password is required!'}
        if len(data['password']) < 6:
            return {'success': False, 'message': 'Password must be at least 6 characters!'}
        if data['password'] != data.get('confirm_password'):
            return {'success': False, 'message': 'Passwords do not match!'}
        
        # Register customer using model
        if self.model:
            try:
                success, customer_id, message = self.model.register_customer(data)
                
                if success:
                    return {
                        'success': True,
                        'message': message,
                        'customer_id': customer_id,
                        'username': data['username']
                    }
                else:
                    return {'success': False, 'message': message}
                    
            except Exception as e:
                return {'success': False, 'message': f'Registration error: {str(e)}'}
        else:
            return {'success': False, 'message': 'Database connection failed!'}
    
    def go_to_login(self):
        """Go back to login screen"""
        if self.login_controller:
            self.login_controller.close_registration()
        elif self.view:
            self.view = None

    def set_view(self, view):
        """Set the view"""
        self.view = view
        self.customer_controller.view = view

    def set_model(self, model):
        """Set the model"""
        self.model = model
        self.customer_controller.model = model
        
    def set_login_controller(self, login_controller):
        """Set the login controller reference"""
        self.login_controller = login_controller