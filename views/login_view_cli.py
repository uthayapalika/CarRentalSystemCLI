# views/login_view_cli.py
"""
CLI Login View
"""
from controllers.login_controller_cli import LoginControllerCLI
from views.registration_view_cli import RegistrationViewCLI


class LoginViewCLI:
    """CLI Login View"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.controller = LoginControllerCLI(parent, db)
    
    def show(self):
        """Show login screen"""
        while True:
            self.parent.clear_screen()
            self.parent.print_header()
            
            print("  🔐 WELCOME TO CAR RENTAL SYSTEM")
            print()
            self.parent.print_separator()
            print()
            
            print("  [1] 🔑 Login")
            print("  [2] 📝 Create New Account")
            print("  [3] 🚪 Exit")
            print()
            self.parent.print_separator()
            print()
            
            choice = self.parent.get_input("  Select option: ").strip()
            
            if choice == "1":
                # Login flow
                user = self.login_flow()
                if user:
                    return user
            elif choice == "2":
                # Registration flow
                reg_view = RegistrationViewCLI(self.parent, self.db)
                result = reg_view.show()
                if result and result.get('success'):
                    self.parent.print_success("Account created successfully!")
                    self.parent.print_info("Please login with your new credentials.")
                    self.parent.get_input("\nPress Enter to continue...")
                    # After registration, go back to main menu
                    continue
                else:
                    continue
            elif choice == "3":
                self.parent.print_info("Thank you for using Car Rental System!")
                return None
            else:
                self.parent.print_error("Invalid option. Please try again.")
                self.parent.get_input("\nPress Enter to continue...")
    
    def login_flow(self):
        """Handle login flow with attempts"""
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            self.parent.clear_screen()
            self.parent.print_header()
            
            print("  🔐 LOGIN")
            print()
            self.parent.print_separator()
            print()
            print(f"  Attempt {attempts + 1} of {max_attempts}")
            print()
            
            username = self.parent.get_input("  Username: ").strip()
            
            if not username:
                self.parent.print_error("Username is required!")
                self.parent.get_input("\nPress Enter to continue...")
                attempts += 1
                continue
            
            password = self.parent.get_input("  Password: ").strip()
            
            if not password:
                self.parent.print_error("Password is required!")
                self.parent.get_input("\nPress Enter to continue...")
                attempts += 1
                continue
            
            # Show loading
            self.parent.print_info("Authenticating...")
            
            # Authenticate
            user = self.controller.login(username, password)
            
            if user:
                # Debug: Print user info
                print(f"  Debug: User logged in - ID: {user.get('id')}, Role: {user.get('role')}, Customer ID: {user.get('customer_id')}")
                
                self.parent.print_success(f"Welcome back, {user.get('first_name', '')}!")
                self.parent.get_input("\nPress Enter to continue...")
                return user
            else:
                attempts += 1
                remaining = max_attempts - attempts
                if remaining > 0:
                    self.parent.print_error(f"Invalid credentials! {remaining} attempts remaining.")
                    self.parent.get_input("\nPress Enter to continue...")
                else:
                    self.parent.print_error("Too many failed attempts!")
                    self.parent.get_input("\nPress Enter to continue...")
                    return None
        
        return None