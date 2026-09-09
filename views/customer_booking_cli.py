# views/customer_booking_cli.py (Updated show method with debug)
"""
CLI Customer Booking View
"""
from datetime import datetime, timedelta


class CustomerBookingCLI:
    """CLI View for Customer Booking"""
    
    def __init__(self, parent, db, customer_id, vehicle_id):
        self.parent = parent
        self.db = db
        self.customer_id = customer_id
        self.vehicle_id = vehicle_id
        self.vehicle = None
        self.daily_rate = 0
        self.min_period = 1
        self.max_period = 30
        self.late_fee = 0
    
    def show(self):
        """Show booking form"""
        if not self.load_vehicle():
            return
        
        # Debug: Check if customer_id is valid
        if not self.customer_id:
            self.parent.print_error("❌ No customer profile found. Please contact support.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        while True:
            self.parent.clear_screen()
            self.parent.print_header()
            
            print(f"  📝 BOOK VEHICLE - {self.vehicle['make']} {self.vehicle['model']}")
            print()
            self.parent.print_separator()
            print()
            
            # Show vehicle details
            print("  Vehicle Details:")
            print(f"  Make:       {self.vehicle['make']}")
            print(f"  Model:      {self.vehicle['model']}")
            print(f"  Year:       {self.vehicle['year']}")
            print(f"  License:    {self.vehicle['license_plate']}")
            print(f"  Daily Rate: ${self.vehicle['daily_rate']:.2f}")
            print(f"  Min Period: {self.min_period} days")
            print(f"  Max Period: {self.max_period} days")
            if self.late_fee > 0:
                print(f"  Late Fee:   ${self.late_fee:.2f}/day")
            print()
            self.parent.print_separator()
            print()
            
            # Booking dates
            today = datetime.now().strftime("%Y-%m-%d")
            default_end = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            
            start_date = self.parent.get_input(f"  Start Date (YYYY-MM-DD) [{today}]: ").strip()
            if not start_date:
                start_date = today
            
            end_date = self.parent.get_input(f"  End Date (YYYY-MM-DD) [{default_end}]: ").strip()
            if not end_date:
                end_date = default_end
            
            # Validate dates
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                
                if end <= start:
                    self.parent.print_error("End date must be after start date!")
                    self.parent.get_input("\nPress Enter to continue...")
                    continue
                
                days = (end - start).days
                
                if days < self.min_period:
                    self.parent.print_error(f"Minimum rental period is {self.min_period} day(s)!")
                    self.parent.get_input("\nPress Enter to continue...")
                    continue
                
                if days > self.max_period:
                    self.parent.print_error(f"Maximum rental period is {self.max_period} day(s)!")
                    self.parent.get_input("\nPress Enter to continue...")
                    continue
                
            except ValueError:
                self.parent.print_error("Invalid date format! Use YYYY-MM-DD")
                self.parent.get_input("\nPress Enter to continue...")
                continue
            
            # Calculate cost
            subtotal = days * self.daily_rate
            discount = subtotal * 0.10 if days >= 7 else 0
            total = subtotal - discount
            
            # Special requests
            notes = self.parent.get_input("  Special Requests: ").strip()
            
            print()
            self.parent.print_separator()
            print()
            
            print("  Booking Summary:")
            print(f"  Customer ID: {self.customer_id}")  # Debug: Show customer_id
            print(f"  Vehicle:    {self.vehicle['make']} {self.vehicle['model']}")
            print(f"  Dates:      {start_date} to {end_date}")
            print(f"  Days:       {days}")
            print(f"  Daily Rate: ${self.daily_rate:.2f}")
            print(f"  Subtotal:   ${subtotal:.2f}")
            if discount > 0:
                print(f"  Discount:   -${discount:.2f} (10% for 7+ days)")
            print(f"  Total:      ${total:.2f}")
            print()
            
            confirm = self.parent.get_input("  Confirm booking? (y/n): ").strip().lower()
            if confirm == 'n' or confirm == 'no':
                self.parent.print_warning("Booking cancelled.")
                self.parent.get_input("\nPress Enter to continue...")
                return
            if confirm != 'y' and confirm != 'yes':
                self.parent.print_error("Invalid input. Please enter 'y' or 'n'.")
                self.parent.get_input("\nPress Enter to continue...")
                continue
            
            # Submit booking
            self.submit_booking(start_date, end_date, days, total, notes)
            break
    
    def load_vehicle(self):
        """Load vehicle details"""
        try:
            from controllers.customer_booking_controller import CustomerBookingController
            
            controller = CustomerBookingController(self.db)
            self.vehicle = controller.get_vehicle_details(self.vehicle_id)
            
            if not self.vehicle:
                self.parent.print_error("Vehicle not found or not available.")
                self.parent.get_input("\nPress Enter to continue...")
                return False
            
            self.daily_rate = self.vehicle['daily_rate']
            self.min_period = self.vehicle['min_rent_period'] or 1
            self.max_period = self.vehicle['max_rent_period'] or 30
            self.late_fee = self.vehicle['late_fee_rate'] or 0
            
            return True
            
        except Exception as e:
            self.parent.print_error(f"Error loading vehicle: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")
            return False
    
    def submit_booking(self, start_date, end_date, days, total_amount, notes):
        """Submit booking request"""
        try:
            from controllers.customer_booking_controller import CustomerBookingController
            
            # Debug: Print customer_id before submission
            print(f"  Debug: Submitting booking with customer_id: {self.customer_id}")
            
            controller = CustomerBookingController(self.db)
            success, message, booking_ref = controller.create_booking(
                self.customer_id,
                self.vehicle_id,
                start_date,
                end_date,
                self.daily_rate,
                days,
                total_amount,
                notes
            )
            
            if success:
                self.parent.print_success("✅ Booking request submitted successfully!")
                print()
                print(f"  Booking Reference: {booking_ref}")
                print(f"  Total Amount: ${total_amount:.2f}")
                print()
                self.parent.print_info("Your request has been sent for approval.")
                self.parent.print_info("You will be notified once confirmed.")
                self.parent.get_input("\nPress Enter to continue...")
            else:
                self.parent.print_error(f"❌ {message}")
                self.parent.get_input("\nPress Enter to continue...")
                
        except Exception as e:
            self.parent.print_error(f"Error submitting booking: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")