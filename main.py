# main.py
"""
Car Rental System - CLI Version
Main Application Entry Point
"""
import sys
import os
from db_setup import Database
from factories import ModelFactory
from version import APP_VERSION
from views.login_view_cli import LoginViewCLI


class AppCLI:
    """Main CLI Application Class"""
    
    def __init__(self):
        """Initialize the CLI application"""
        self.version = APP_VERSION
        self.db = None
        self.user = None
        self.model_factory = ModelFactory()
        self.current_view = None
        
        # Initialize database
        self.init_database()
        
    def init_database(self):
        """Initialize database connection"""
        try:
            self.db = Database()
            print("✅ Database connected successfully!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.db = None
            sys.exit(1)
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print application header"""
        print("=" * 80)
        print(f"  🚗 CAR RENTAL SYSTEM - CLI v{self.version}")
        if self.user:
            print(f"  👤 Logged in as: {self.user.get('first_name', '')} {self.user.get('last_name', '')}")
            print(f"  🔑 Role: {self.user.get('role', 'staff').upper()}")
        print("=" * 80)
        print()
    
    def print_separator(self):
        """Print a separator line"""
        print("-" * 80)
    
    def print_success(self, message):
        """Print success message"""
        print(f"✅ {message}")
    
    def print_error(self, message):
        """Print error message"""
        print(f"❌ {message}")
    
    def print_warning(self, message):
        """Print warning message"""
        print(f"⚠️  {message}")
    
    def print_info(self, message):
        """Print info message"""
        print(f"ℹ️  {message}")
    
    def get_input(self, prompt):
        """Get user input with prompt"""
        return input(prompt)
    
    def get_user_role(self):
        """Get user role"""
        if self.user:
            return self.user.get('role', 'staff').lower()
        return 'staff'
    
    def is_admin(self):
        """Check if user is admin"""
        return self.get_user_role() == 'admin'
    
    def is_manager(self):
        """Check if user is manager"""
        return self.get_user_role() == 'manager'
    
    def is_staff(self):
        """Check if user is staff"""
        return self.get_user_role() == 'staff'
    
    def is_customer(self):
        """Check if user is customer"""
        return self.get_user_role() == 'customer'
    
    def show_main_menu(self):
        """Show main application menu based on user role"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print("  📋 MAIN MENU")
            print()
            self.print_separator()
            print()
            
            role = self.get_user_role()
            
            # Admin has full access to everything
            if role == 'admin':
                print("  [1] 👤 Customer Management")
                print("  [2] 🚗 Vehicle Categories")
                print("  [3] 🚗 Vehicle Management")
                print("  [4] 🛠️ Maintenance Management")
                print("  [5] 📅 Booking/Rental Management")
                print("  [6] 💰 Payment Management")
                print("  [7] 🔐 Logout")
            
            # Manager has access to vehicle, categories, maintenance, booking, payments
            elif role == 'manager':
                print("  [1] 🚗 Vehicle Categories")
                print("  [2] 🚗 Vehicle Management")
                print("  [3] 🛠️ Maintenance Management")
                print("  [4] 📅 Booking/Rental Management")
                print("  [5] 💰 Payment Management")
                print("  [6] 🔐 Logout")
            
            # Staff has view-only access
            elif role == 'staff':
                print("  [1] 🛠️ Maintenance Management (View Only)")
                print("  [2] 📅 Booking/Rental Management (View Only)")
                print("  [3] 💰 Payment Management (View Only)")
                print("  [4] 🔐 Logout")
            
            # Customer dashboard
            elif role == 'customer':
                print("  [1] 🚗 Browse Available Vehicles")
                print("  [2] 📋 View My Bookings")
                print("  [3] 💰 View My Payments")
                print("  [4] 🔐 Logout")
            
            print()
            self.print_separator()
            print()
            
            choice = self.get_input("  Select option: ").strip()
            
            # Admin options
            if role == 'admin':
                if choice == "1":
                    from views.customer_view_cli import CustomerViewCLI
                    view = CustomerViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "2":
                    from views.vehicle_category_view_cli import VehicleCategoryViewCLI
                    view = VehicleCategoryViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "3":
                    from views.vehicle_view_cli import VehicleViewCLI
                    view = VehicleViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "4":
                    from views.maintenance_view_cli import MaintenanceViewCLI
                    view = MaintenanceViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "5":
                    from views.booking_view_cli import BookingViewCLI
                    view = BookingViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "6":
                    from views.payment_view_cli import PaymentViewCLI
                    view = PaymentViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "7":
                    self.logout()
                    break
                else:
                    self.print_error("Invalid option")
                    self.get_input("\nPress Enter to continue...")
            
            # Manager options
            elif role == 'manager':
                if choice == "1":
                    from views.vehicle_category_view_cli import VehicleCategoryViewCLI
                    view = VehicleCategoryViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "2":
                    from views.vehicle_view_cli import VehicleViewCLI
                    view = VehicleViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "3":
                    from views.maintenance_view_cli import MaintenanceViewCLI
                    view = MaintenanceViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "4":
                    from views.booking_view_cli import BookingViewCLI
                    view = BookingViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "5":
                    from views.payment_view_cli import PaymentViewCLI
                    view = PaymentViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "6":
                    self.logout()
                    break
                else:
                    self.print_error("Invalid option")
                    self.get_input("\nPress Enter to continue...")
            
            # Staff options
            elif role == 'staff':
                if choice == "1":
                    from views.maintenance_view_cli import MaintenanceViewCLI
                    view = MaintenanceViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "2":
                    from views.booking_view_cli import BookingViewCLI
                    view = BookingViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "3":
                    from views.payment_view_cli import PaymentViewCLI
                    view = PaymentViewCLI(self, self.db, self.user)
                    view.show()
                elif choice == "4":
                    self.logout()
                    break
                else:
                    self.print_error("Invalid option")
                    self.get_input("\nPress Enter to continue...")
            
            # Customer options
            elif role == 'customer':
                if choice == "1":
                    from views.customer_dashboard_cli import CustomerDashboardCLI
                    view = CustomerDashboardCLI(self, self.db, self.user)
                    view.show()
                elif choice == "2":
                    from views.customer_dashboard_cli import CustomerDashboardCLI
                    view = CustomerDashboardCLI(self, self.db, self.user)
                    view.show()
                elif choice == "3":
                    from views.customer_dashboard_cli import CustomerDashboardCLI
                    view = CustomerDashboardCLI(self, self.db, self.user)
                    view.show()
                elif choice == "4":
                    self.logout()
                    break
                else:
                    self.print_error("Invalid option")
                    self.get_input("\nPress Enter to continue...")
    
    def logout(self):
        """Logout user"""
        if self.user:
            self.print_success(f"Goodbye, {self.user.get('first_name', '')}!")
        self.user = None
        self.current_view = None
    
    def run(self):
        """Run the application"""
        self.show_login()
    
    def show_login(self):
        """Show login screen"""
        login_view = LoginViewCLI(self, self.db)
        user = login_view.show()
        
        if user:
            self.user = user
            self.show_main_menu()
        else:
            self.print_info("Exiting application...")
            sys.exit(0)
    
    def on_close(self):
        """Clean up on exit"""
        if self.db:
            self.db.close()
        print("\n👋 Thank you for using Car Rental System!")


# Main execution - runs directly when script is executed
if __name__ == "__main__":
    try:
        app = AppCLI()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Application terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        sys.exit(1)