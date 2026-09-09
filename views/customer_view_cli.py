# views/customer_view_cli.py
"""
CLI Customer View
"""
from factories import ModelFactory


class CustomerViewCLI:
    """CLI View for Customers"""
    
    def __init__(self, parent, db, user=None):
        """
        Initialize Customer View CLI
        
        Args:
            parent: The main AppCLI instance
            db: Database connection
            user: Current logged-in user (optional)
        """
        self.parent = parent
        self.db = db
        self.user = user
        
        # Initialize models with error handling
        try:
            self.customer_model = ModelFactory.create_model('customer', db)
        except Exception as e:
            print(f"Error loading customer model: {e}")
            self.customer_model = None
        
        try:
            self.booking_model = ModelFactory.create_model('booking', db)
        except Exception as e:
            self.booking_model = None
        
        try:
            self.user_model = ModelFactory.create_model('user', db)
        except Exception as e:
            self.user_model = None
    
    def show(self):
        """Show customer management menu"""
        while True:
            self.parent.clear_screen()
            self.parent.print_header()
            
            print("  👤 CUSTOMER MANAGEMENT")
            print()
            self.parent.print_separator()
            print()
            
            # Show different options based on user role
            if self.parent.is_admin():
                print("  [1] Add Customer")
                print("  [2] View All Customers")
                print("  [3] Search Customers")
                print("  [4] Update Customer")
                print("  [5] Delete Customer")
                print("  [6] View Customer Vehicles")
                print("  [b] Back to Main Menu")
            else:
                print("  [1] View All Customers")
                print("  [2] Search Customers")
                print("  [3] View Customer Vehicles")
                print("  [b] Back to Main Menu")
            
            print()
            self.parent.print_separator()
            print()
            
            choice = self.parent.get_input("  Select option: ").strip()
            
            if choice.lower() == 'b':
                break
            elif choice == '1':
                if self.parent.is_admin():
                    self.add_customer()
                else:
                    self.view_customers()
            elif choice == '2':
                if self.parent.is_admin():
                    self.view_customers()
                else:
                    self.search_customers()
            elif choice == '3':
                if self.parent.is_admin():
                    self.search_customers()
                else:
                    self.view_customer_vehicles()
            elif choice == '4':
                if self.parent.is_admin():
                    self.update_customer()
                else:
                    self.parent.print_error("Access denied! Admin only.")
                    self.parent.get_input("\nPress Enter to continue...")
            elif choice == '5':
                if self.parent.is_admin():
                    self.delete_customer()
                else:
                    self.parent.print_error("Access denied! Admin only.")
                    self.parent.get_input("\nPress Enter to continue...")
            elif choice == '6':
                if self.parent.is_admin():
                    self.view_customer_vehicles()
                else:
                    self.parent.print_error("Access denied! Admin only.")
                    self.parent.get_input("\nPress Enter to continue...")
            else:
                self.parent.print_error("Invalid option!")
                self.parent.get_input("\nPress Enter to continue...")
    
    def add_customer(self):
        """Add a new customer"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  👤 ADD NEW CUSTOMER")
        print()
        self.parent.print_separator()
        print()
        
        try:
            if not self.customer_model:
                self.parent.print_error("Customer model not available!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            # Get customer details
            first_name = self.parent.get_input("  First Name: ").strip()
            if not first_name:
                self.parent.print_error("First name is required!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            last_name = self.parent.get_input("  Last Name: ").strip()
            if not last_name:
                self.parent.print_error("Last name is required!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            email = self.parent.get_input("  Email: ").strip()
            if not email:
                self.parent.print_error("Email is required!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            phone = self.parent.get_input("  Phone: ").strip()
            if not phone:
                self.parent.print_error("Phone is required!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            address = self.parent.get_input("  Address: ").strip()
            license_number = self.parent.get_input("  License Number: ").strip()
            
            # Create customer data
            customer_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'address': address,
                'license_number': license_number
            }
            
            customer_id = self.customer_model.create(customer_data)
            self.parent.print_success(f"Customer {first_name} {last_name} added successfully! (ID: {customer_id})")
            self.parent.get_input("\nPress Enter to continue...")
            
        except ValueError as e:
            self.parent.print_error(f"Error: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")
        except Exception as e:
            self.parent.print_error(f"Error adding customer: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")
    
    def view_customers(self):
        """View all customers"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  👤 ALL CUSTOMERS")
        print()
        self.parent.print_separator()
        print()
        
        try:
            if not self.customer_model:
                self.parent.print_error("Customer model not available!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            customers = self.customer_model.get_all()
            
            if not customers:
                self.parent.print_info("No customers found.")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            # Display in a table format
            print(f"  {'ID':<5} {'Name':<30} {'Email':<30} {'Phone':<15}")
            print("  " + "-" * 80)
            
            for customer in customers:
                name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}"
                customer_id = customer.get('customer_id', customer.get('id', ''))
                print(f"  {customer_id:<5} {name:<30} {customer.get('email', ''):<30} {customer.get('phone', ''):<15}")
            
            print()
            print(f"  Total: {len(customers)} customers")
            self.parent.get_input("\nPress Enter to continue...")
            
        except Exception as e:
            self.parent.print_error(f"Error loading customers: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")
    
    def search_customers(self):
        """Search for customers"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  🔍 SEARCH CUSTOMERS")
        print()
        self.parent.print_separator()
        print()
        
        search_term = self.parent.get_input("  Enter search term (name, email, or phone): ").strip()
        
        if not search_term:
            self.parent.print_error("Search term cannot be empty!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            if not self.customer_model:
                self.parent.print_error("Customer model not available!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            customers = self.customer_model.search(search_term)
            
            self.parent.clear_screen()
            self.parent.print_header()
            print("  🔍 SEARCH RESULTS")
            print()
            self.parent.print_separator()
            print()
            
            if not customers:
                self.parent.print_info(f"No customers found matching '{search_term}'")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            for i, customer in enumerate(customers, 1):
                customer_id = customer.get('customer_id', customer.get('id', ''))
                print(f"  {i}. {customer.get('first_name', '')} {customer.get('last_name', '')} (ID: {customer_id})")
                print(f"     Email: {customer.get('email', '')}")
                print(f"     Phone: {customer.get('phone', '')}")
                if customer.get('address'):
                    print(f"     Address: {customer.get('address', '')}")
                print()
            
            print(f"  Found: {len(customers)} customers")
            self.parent.get_input("\nPress Enter to continue...")
            
        except Exception as e:
            self.parent.print_error(f"Error searching customers: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")
    
    def update_customer(self):
        """Update customer information"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  ✏️ UPDATE CUSTOMER")
        print()
        self.parent.print_separator()
        print()
        
        try:
            if not self.customer_model:
                self.parent.print_error("Customer model not available!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            search_term = self.parent.get_input("  Enter customer name or email to search: ").strip()
            
            if not search_term:
                self.parent.print_error("Search term cannot be empty!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            customers = self.customer_model.search(search_term)
            
            if not customers:
                self.parent.print_info(f"No customers found matching '{search_term}'")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            self.parent.clear_screen()
            self.parent.print_header()
            print("  ✏️ SELECT CUSTOMER TO UPDATE")
            print()
            self.parent.print_separator()
            print()
            
            for i, customer in enumerate(customers, 1):
                customer_id = customer.get('customer_id', customer.get('id', ''))
                print(f"  {i}. {customer.get('first_name', '')} {customer.get('last_name', '')} (ID: {customer_id}) - {customer.get('email', '')}")
            
            print()
            choice = self.parent.get_input("  Select customer number: ").strip()
            
            try:
                idx = int(choice) - 1
                if idx < 0 or idx >= len(customers):
                    self.parent.print_error("Invalid selection!")
                    self.parent.get_input("\nPress Enter to continue...")
                    return
                
                customer = customers[idx]
                customer_id = customer.get('customer_id', customer.get('id', ''))
                
                self.parent.clear_screen()
                self.parent.print_header()
                print("  ✏️ UPDATE CUSTOMER")
                print()
                self.parent.print_separator()
                print()
                
                print(f"  Current: {customer.get('first_name', '')} {customer.get('last_name', '')}")
                print(f"  Email: {customer.get('email', '')}")
                print(f"  Phone: {customer.get('phone', '')}")
                if customer.get('address'):
                    print(f"  Address: {customer.get('address', '')}")
                print()
                
                first_name = self.parent.get_input(f"  First Name ({customer.get('first_name', '')}): ").strip()
                last_name = self.parent.get_input(f"  Last Name ({customer.get('last_name', '')}): ").strip()
                email = self.parent.get_input(f"  Email ({customer.get('email', '')}): ").strip()
                phone = self.parent.get_input(f"  Phone ({customer.get('phone', '')}): ").strip()
                address = self.parent.get_input(f"  Address ({customer.get('address', '')}): ").strip()
                
                update_data = {}
                if first_name:
                    update_data['first_name'] = first_name
                if last_name:
                    update_data['last_name'] = last_name
                if email:
                    update_data['email'] = email
                if phone:
                    update_data['phone'] = phone
                if address:
                    update_data['address'] = address
                
                if update_data:
                    self.customer_model.update(customer_id, update_data)
                    self.parent.print_success("Customer updated successfully!")
                else:
                    self.parent.print_info("No changes made.")
                
                self.parent.get_input("\nPress Enter to continue...")
                
            except ValueError:
                self.parent.print_error("Invalid input! Please enter a number.")
                
        except Exception as e:
            self.parent.print_error(f"Error updating customer: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")
    
    def delete_customer(self):
        """Delete a customer"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  🗑️ DELETE CUSTOMER")
        print()
        self.parent.print_separator()
        print()
        
        try:
            if not self.customer_model:
                self.parent.print_error("Customer model not available!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            search_term = self.parent.get_input("  Enter customer name or email to search: ").strip()
            
            if not search_term:
                self.parent.print_error("Search term cannot be empty!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            customers = self.customer_model.search(search_term)
            
            if not customers:
                self.parent.print_info(f"No customers found matching '{search_term}'")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            self.parent.clear_screen()
            self.parent.print_header()
            print("  🗑️ SELECT CUSTOMER TO DELETE")
            print()
            self.parent.print_separator()
            print()
            
            for i, customer in enumerate(customers, 1):
                customer_id = customer.get('customer_id', customer.get('id', ''))
                print(f"  {i}. {customer.get('first_name', '')} {customer.get('last_name', '')} (ID: {customer_id}) - {customer.get('email', '')}")
            
            print()
            choice = self.parent.get_input("  Select customer number: ").strip()
            
            try:
                idx = int(choice) - 1
                if idx < 0 or idx >= len(customers):
                    self.parent.print_error("Invalid selection!")
                    self.parent.get_input("\nPress Enter to continue...")
                    return
                
                customer = customers[idx]
                customer_id = customer.get('customer_id', customer.get('id', ''))
                
                # Check if customer has bookings
                if self.booking_model and hasattr(self.booking_model, 'get_by_customer'):
                    bookings = self.booking_model.get_by_customer(customer_id)
                    if bookings and len(bookings) > 0:
                        self.parent.print_error(f"Cannot delete customer with {len(bookings)} existing booking(s)!")
                        self.parent.get_input("\nPress Enter to continue...")
                        return
                
                confirm = self.parent.get_input(f"  Are you sure you want to delete {customer.get('first_name', '')} {customer.get('last_name', '')}? (y/n): ").strip().lower()
                
                if confirm == 'y':
                    self.customer_model.delete(customer_id)
                    self.parent.print_success("Customer deleted successfully!")
                else:
                    self.parent.print_info("Deletion cancelled.")
                
                self.parent.get_input("\nPress Enter to continue...")
                
            except ValueError:
                self.parent.print_error("Invalid input! Please enter a number.")
                
        except Exception as e:
            self.parent.print_error(f"Error deleting customer: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")
    
    def view_customer_vehicles(self):
        """View vehicles for a customer"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  🚗 VIEW CUSTOMER VEHICLES")
        print()
        self.parent.print_separator()
        print()
        
        try:
            if not self.customer_model:
                self.parent.print_error("Customer model not available!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            search_term = self.parent.get_input("  Enter customer name or email: ").strip()
            
            if not search_term:
                self.parent.print_error("Search term cannot be empty!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            customers = self.customer_model.search(search_term)
            
            if not customers:
                self.parent.print_info(f"No customers found matching '{search_term}'")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            if len(customers) > 1:
                self.parent.clear_screen()
                self.parent.print_header()
                print("  🚗 SELECT CUSTOMER")
                print()
                self.parent.print_separator()
                print()
                
                for i, customer in enumerate(customers, 1):
                    customer_id = customer.get('customer_id', customer.get('id', ''))
                    print(f"  {i}. {customer.get('first_name', '')} {customer.get('last_name', '')} (ID: {customer_id}) - {customer.get('email', '')}")
                
                print()
                choice = self.parent.get_input("  Select customer number: ").strip()
                
                try:
                    idx = int(choice) - 1
                    if idx < 0 or idx >= len(customers):
                        self.parent.print_error("Invalid selection!")
                        self.parent.get_input("\nPress Enter to continue...")
                        return
                    customer = customers[idx]
                except ValueError:
                    self.parent.print_error("Invalid input!")
                    self.parent.get_input("\nPress Enter to continue...")
                    return
            else:
                customer = customers[0]
            
            customer_id = customer.get('customer_id', customer.get('id', ''))
            
            try:
                from views.customer_vehicles_cli import CustomerVehiclesCLI
                
                def booking_callback(vehicle_id):
                    """Callback for booking a vehicle"""
                    self.parent.clear_screen()
                    self.parent.print_header()
                    print("  📅 CREATE BOOKING")
                    print()
                    self.parent.print_separator()
                    print()
                    
                    try:
                        start_date = self.parent.get_input("  Start Date (YYYY-MM-DD): ").strip()
                        end_date = self.parent.get_input("  End Date (YYYY-MM-DD): ").strip()
                        
                        if not start_date or not end_date:
                            self.parent.print_error("Dates are required!")
                            self.parent.get_input("\nPress Enter to continue...")
                            return
                        
                        if self.booking_model and hasattr(self.booking_model, 'create'):
                            booking_data = {
                                'customer_id': customer_id,
                                'vehicle_id': vehicle_id,
                                'start_date': start_date,
                                'end_date': end_date
                            }
                            self.booking_model.create(booking_data)
                            self.parent.print_success("Booking created successfully!")
                        else:
                            self.parent.print_error("Booking model not available!")
                        
                        self.parent.get_input("\nPress Enter to continue...")
                        
                    except Exception as e:
                        self.parent.print_error(f"Error creating booking: {str(e)}")
                        self.parent.get_input("\nPress Enter to continue...")
                
                vehicle_view = CustomerVehiclesCLI(self.parent, self.db, customer_id, booking_callback)
                vehicle_view.show()
                
            except ImportError as e:
                self.parent.print_error(f"Error loading vehicle view: {e}")
                self.parent.get_input("\nPress Enter to continue...")
                
        except Exception as e:
            self.parent.print_error(f"Error: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")