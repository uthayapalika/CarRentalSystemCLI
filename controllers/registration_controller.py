from controllers.customer_controller import CustomerController
from factories import ModelFactory

class RegistrationController:
    def __init__(self, view=None, model=None):
        self.view = view
        self.model = model
        self.login_controller = None  
        # Use CustomerController for registration logic
        self.customer_controller = CustomerController(view, model)
        
    def register(self):
        """Handle registration - delegate to customer controller"""
        if not self.view:
            print("Error: View is not set in registration controller!")
            return
            
        # Set the view and model in customer controller
        self.customer_controller.view = self.view
        self.customer_controller.model = self.model
        
        # Call customer controller's register method
        self.customer_controller.register_customer()

    def go_to_login(self):
        """Go back to login screen"""
        # Use the login controller to close registration
        if self.login_controller:
            self.login_controller.close_registration()
        elif self.view and self.view.frame:
            # Fallback: destroy the registration frame
            self.view.frame.destroy()
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