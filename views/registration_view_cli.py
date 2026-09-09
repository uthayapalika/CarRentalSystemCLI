# views/registration_view_cli.py
"""
CLI Registration View
"""
import sys
from controllers.registration_controller_cli import RegistrationControllerCLI


class RegistrationViewCLI:
    """CLI Registration View"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.controller = RegistrationControllerCLI(self, db)
    
    def show(self):
        """Show registration screen"""
        while True:
            self.parent.clear_screen()
            self.parent.print_header()
            
            print("  📝 CREATE NEW ACCOUNT")
            print()
            self.parent.print_separator()
            print()
            print("  Please fill in the following information to create your account.")
            print()
            self.parent.print_separator()
            print()
            
            print("  📋 Personal Information")
            print("  " + "-" * 40)
            print()
            first_name = self.parent.get_input("  First Name *: ").strip()
            last_name = self.parent.get_input("  Last Name *: ").strip()
            email = self.parent.get_input("  Email Address *: ").strip()
            phone = self.parent.get_input("  Phone Number *: ").strip()
            driver_license = self.parent.get_input("  Driver License *: ").strip()
            print()
            
            print("  📍 Address Information")
            print("  " + "-" * 40)
            print()
            address = self.parent.get_input("  Street Address: ").strip()
            city = self.parent.get_input("  City: ").strip()
            state = self.parent.get_input("  State/Province: ").strip()
            zip_code = self.parent.get_input("  ZIP/Postal Code: ").strip()
            full_address = f"{address}, {city}, {state} {zip_code}".strip(", ")
            
            print()
            self.parent.print_separator()
            print()
            
            print("  🔐 Account Information")
            print("  " + "-" * 40)
            print()
            username = self.parent.get_input("  Username *: ").strip()
            password = self.parent.get_input("  Password *: ").strip()
            confirm_password = self.parent.get_input("  Confirm Password *: ").strip()
            
            print()
            self.parent.print_separator()
            print()
            
            # Show summary
            print("  📋 Registration Summary")
            print("  " + "-" * 40)
            print(f"  Name:        {first_name} {last_name}")
            print(f"  Email:       {email}")
            print(f"  Phone:       {phone}")
            print(f"  Username:    {username}")
            print(f"  Address:     {full_address if full_address else 'Not provided'}")
            print()
            self.parent.print_separator()
            print()
            
            confirm = self.parent.get_input("  Create account? (y/n): ").strip().lower()
            if confirm == 'n' or confirm == 'no':
                self.parent.print_warning("Registration cancelled.")
                self.parent.get_input("\nPress Enter to continue...")
                return None
            if confirm != 'y' and confirm != 'yes':
                self.parent.print_warning("Invalid input. Please enter 'y' or 'n'.")
                self.parent.get_input("\nPress Enter to continue...")
                continue
            
            # Prepare data
            data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'driver_license_num': driver_license,
                'address': full_address,
                'username': username,
                'password': password,
                'confirm_password': confirm_password
            }
            
            # Register
            self.parent.print_info("Creating your account...")
            result = self.controller.register(data)
            
            if result['success']:
                self.parent.print_success("✅ " + result['message'])
                print()
                print("  📝 Account Details:")
                print("  " + "-" * 40)
                print(f"  Customer ID:  {result.get('customer_id', 'N/A')}")
                print(f"  Username:     {username}")
                print(f"  Name:         {first_name} {last_name}")
                print(f"  Email:        {email}")
                print()
                self.parent.print_info("You can now login with your credentials.")
                self.parent.get_input("\nPress Enter to continue...")
                return {'success': True, 'customer_id': result.get('customer_id')}
            else:
                self.parent.print_error("❌ " + result['message'])
                self.parent.get_input("\nPress Enter to try again...")
                # Continue to show registration form again
                continue