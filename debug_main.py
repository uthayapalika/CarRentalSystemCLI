# debug_main.py
"""
Debug version of Car Rental System
"""
import sys
import os
import traceback

# Force output to be unbuffered
sys.stdout.reconfigure(line_buffering=True)

print("=" * 80)
print("🚗 CAR RENTAL SYSTEM - DEBUG VERSION")
print("=" * 80)
print()

try:
    print("Step 1: Importing modules...")
    
    from db_setup import Database
    print("  ✅ Database imported")
    
    from factories import ModelFactory
    print("  ✅ ModelFactory imported")
    
    from version import APP_VERSION
    print(f"  ✅ Version: {APP_VERSION}")
    
    from views.login_view_cli import LoginViewCLI
    print("  ✅ LoginViewCLI imported")
    
except Exception as e:
    print(f"❌ Error importing: {e}")
    traceback.print_exc()
    sys.exit(1)

print()
print("Step 2: Creating Database instance...")

try:
    db = Database()
    print("  ✅ Database created")
except Exception as e:
    print(f"❌ Database error: {e}")
    traceback.print_exc()
    sys.exit(1)

print()
print("Step 3: Testing ModelFactory...")

try:
    # ✅ Use your factory correctly - pass db directly
    customer_model = ModelFactory.create_model('customer', db)
    print("  ✅ CustomerModel created")
    
    user_model = ModelFactory.create_model('user', db)
    print("  ✅ UserModel created")
    
except Exception as e:
    print(f"❌ Factory error: {e}")
    traceback.print_exc()
    sys.exit(1)

print()
print("Step 4: Creating a simple app class...")

class SimpleApp:
    def __init__(self, db):
        self.db = db
        self.user = None
        self.version = APP_VERSION
        # No need for model_factory instance - use static method directly
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        print("=" * 80)
        print(f"  🚗 CAR RENTAL SYSTEM - CLI v{self.version}")
        if self.user:
            print(f"  👤 Logged in as: {self.user.get('username', 'Unknown')}")
        print("=" * 80)
        print()
    
    def print_separator(self):
        print("-" * 80)
    
    def print_success(self, message):
        print(f"✅ {message}")
    
    def print_error(self, message):
        print(f"❌ {message}")
    
    def print_warning(self, message):
        print(f"⚠️  {message}")
    
    def print_info(self, message):
        print(f"ℹ️  {message}")
    
    def get_input(self, prompt):
        return input(prompt)
    
    def get_user_role(self):
        if self.user:
            return self.user.get('role', 'staff').lower()
        return 'staff'
    
    def is_admin(self):
        return self.get_user_role() == 'admin'
    
    def run(self):
        print("Step 5: Starting login...")
        login_view = LoginViewCLI(self, self.db)
        user = login_view.show()
        
        if user:
            print(f"✅ User logged in: {user.get('username')}")
            self.user = user
            
            # Show a simple menu
            while True:
                self.clear_screen()
                self.print_header()
                print("  📋 MAIN MENU")
                print()
                self.print_separator()
                print()
                print("  [1] 👤 Customer Management")
                print("  [2] 🚗 Vehicle Categories")
                print("  [3] 🚗 Vehicle Management")
                print("  [4] 🔐 Logout")
                print()
                self.print_separator()
                print()
                
                choice = self.get_input("  Select option: ").strip()
                
                if choice == "1":
                    try:
                        from views.customer_view_cli import CustomerViewCLI
                        view = CustomerViewCLI(self, self.db, self.user)
                        view.show()
                    except ImportError as e:
                        self.print_error(f"Import Error: {e}")
                        self.print_info("Make sure customer_view_cli.py exists in the views folder")
                        self.get_input("\nPress Enter to continue...")
                    except Exception as e:
                        self.print_error(f"Error: {e}")
                        traceback.print_exc()
                        self.get_input("\nPress Enter to continue...")
                elif choice == "2":
                    self.print_info("Vehicle Categories - Coming soon!")
                    self.get_input("\nPress Enter to continue...")
                elif choice == "3":
                    self.print_info("Vehicle Management - Coming soon!")
                    self.get_input("\nPress Enter to continue...")
                elif choice == "4":
                    self.print_success("Goodbye!")
                    break
                else:
                    self.print_error("Invalid option")
                    self.get_input("\nPress Enter to continue...")
        else:
            self.print_info("Login cancelled. Exiting...")

print()
print("Step 5: Creating app instance...")

try:
    app = SimpleApp(db)
    print("  ✅ App created")
    print()
    print("Step 6: Running app...")
    print()
    app.run()
except Exception as e:
    print(f"❌ App error: {e}")
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 80)
print("Application finished.")
print("=" * 80)