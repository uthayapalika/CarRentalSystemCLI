# views/booking_view_cli.py
"""
CLI Booking Management View
"""
from datetime import datetime, timedelta
from controllers.booking_controller import BookingController


class BookingViewCLI:
    """CLI View for Booking Management"""
    
    def __init__(self, parent, db, user):
        self.parent = parent
        self.db = db
        self.user = user
        self.controller = BookingController(db)
        
        # Check user role for permissions
        self.user_role = user.get('role', 'staff') if user else 'staff'
        self.is_admin = self.user_role == 'admin'
        self.is_manager = self.user_role == 'manager'
        self.is_staff = self.user_role == 'staff'
        self.is_view_only = self.is_staff
        self.can_edit = self.is_admin or self.is_manager
        self.can_approve = self.is_admin
        
        # Editing state
        self.editing_id = None
        
        # Load data
        self.customers = []
        self.vehicles = []
        self.load_dropdowns()
    
    def _row_to_dict(self, row):
        """Convert sqlite3.Row to dict"""
        if row is None:
            return None
        if hasattr(row, 'keys'):
            return dict(row)
        return row
    
    def _rows_to_dicts(self, rows):
        """Convert list of sqlite3.Row to list of dicts"""
        if not rows:
            return []
        return [self._row_to_dict(row) for row in rows]
    
    def load_dropdowns(self):
        """Load customers and vehicles"""
        try:
            customers_raw = self.controller.get_customers()
            self.customers = self._rows_to_dicts(customers_raw)
            
            vehicles_raw = self.controller.get_vehicles()
            self.vehicles = self._rows_to_dicts(vehicles_raw)
        except Exception as e:
            self.parent.print_warning(f"Could not load dropdown data: {e}")
    
    def show(self):
        """Show booking management menu"""
        while True:
            self.parent.clear_screen()
            self.parent.print_header()
            
            print("  📋 BOOKING MANAGEMENT")
            if self.is_view_only:
                print("  🔒 View Only Mode")
            print()
            self.parent.print_separator()
            print()
            
            # Show statistics
            bookings_raw = self.controller.get_all_bookings()
            bookings = self._rows_to_dicts(bookings_raw)
            total = len(bookings) if bookings else 0
            pending = sum(1 for b in bookings if b.get('booking_status') == 'pending') if bookings else 0
            approved = sum(1 for b in bookings if b.get('booking_status') == 'approved') if bookings else 0
            active = sum(1 for b in bookings if b.get('booking_status') == 'active') if bookings else 0
            completed = sum(1 for b in bookings if b.get('booking_status') == 'completed') if bookings else 0
            
            print(f"  📊 Total Bookings: {total}")
            print(f"  🟡 Pending: {pending}")
            print(f"  🟢 Approved: {approved}")
            print(f"  🔵 Active: {active}")
            print(f"  ✅ Completed: {completed}")
            print()
            self.parent.print_separator()
            print()
            
            print("  [1] 📋 View All Bookings")
            print("  [2] 🔍 Search Bookings")
            print("  [3] 🟡 View Pending Bookings")
            print("  [4] 🟢 View Approved Bookings")
            if self.can_edit:
                print("  [5] ➕ Add Booking")
                print("  [6] ✏️ Edit Booking")
                print("  [7] 🗑️ Delete Booking")
            if self.can_approve:
                print("  [8] ✅ Approve Booking")
                print("  [9] ❌ Reject Booking")
            print("  [0] 📊 Export Bookings")
            print("  [b] ↩️ Back to Main Menu")
            print()
            self.parent.print_separator()
            print()
            
            choice = self.parent.get_input("  Select option: ").strip().lower()
            
            if choice == "1":
                self.view_all_bookings()
            elif choice == "2":
                self.search_bookings()
            elif choice == "3":
                self.view_bookings_by_status("pending")
            elif choice == "4":
                self.view_bookings_by_status("approved")
            elif choice == "5" and self.can_edit:
                self.add_booking()
            elif choice == "6" and self.can_edit:
                self.edit_booking()
            elif choice == "7" and self.can_edit:
                self.delete_booking()
            elif choice == "8" and self.can_approve:
                self.approve_booking()
            elif choice == "9" and self.can_approve:
                self.reject_booking()
            elif choice == "0":
                self.export_menu()
            elif choice == "b":
                break
            else:
                self.parent.print_error("Invalid option")
                self.parent.get_input("\nPress Enter to continue...")
    
    def view_all_bookings(self):
        """View all bookings in table format"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📋 ALL BOOKINGS")
        print()
        
        bookings_raw = self.controller.get_all_bookings()
        bookings = self._rows_to_dicts(bookings_raw)
        
        if not bookings:
            self.parent.print_info("No bookings found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.display_booking_table(bookings)
        
        # Option to view details
        view_details = self.parent.get_input("  View booking details? (y/n): ").strip().lower()
        if view_details == 'y' or view_details == 'yes':
            self.view_booking_details()
        else:
            self.parent.get_input("Press Enter to continue...")
    
    def view_bookings_by_status(self, status):
        """View bookings filtered by status"""
        self.parent.clear_screen()
        self.parent.print_header()
        status_display = {
            'pending': '🟡 PENDING',
            'approved': '🟢 APPROVED',
            'rejected': '🔴 REJECTED',
            'active': '🔵 ACTIVE',
            'completed': '✅ COMPLETED',
            'cancelled': '⚪ CANCELLED'
        }.get(status, status.upper())
        
        print(f"  {status_display} BOOKINGS")
        print()
        
        bookings_raw = self.controller.get_by_status(status)
        bookings = self._rows_to_dicts(bookings_raw)
        
        if not bookings:
            self.parent.print_info(f"No {status} bookings found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.display_booking_table(bookings)
        self.parent.get_input("\nPress Enter to continue...")
    
    def display_booking_table(self, bookings):
        """Display bookings in a formatted table"""
        print("  " + "-" * 145)
        print(f"  {'ID':<5} {'Ref':<14} {'Customer':<20} {'Vehicle':<22} "
              f"{'Start':<12} {'End':<12} {'Total':<10} {'Status':<12}")
        print("  " + "-" * 145)
        
        for booking in bookings:
            status_display = {
                'pending': '🟡 Pending',
                'approved': '🟢 Approved',
                'rejected': '🔴 Rejected',
                'active': '🔵 Active',
                'completed': '✅ Completed',
                'cancelled': '⚪ Cancelled'
            }.get(booking.get('booking_status', ''), booking.get('booking_status', ''))
            
            customer_name = f"{booking.get('first_name', '')} {booking.get('last_name', '')}"[:20]
            vehicle_name = f"{booking.get('make', '')} {booking.get('model', '')}"[:22]
            
            print(f"  {booking.get('booking_id', ''):<5} "
                  f"{booking.get('booking_ref', '')[:14]:<14} "
                  f"{customer_name:<20} "
                  f"{vehicle_name:<22} "
                  f"{booking.get('start_date', '')[:10]:<12} "
                  f"{booking.get('end_date', '')[:10]:<12} "
                  f"${booking.get('total_amount', 0):<9.2f} "
                  f"{status_display:<12}")
        
        print("  " + "-" * 145)
        print(f"  Total: {len(bookings)} bookings")
        print()
    
    def view_booking_details(self):
        """View detailed information about a specific booking"""
        booking_id = self.parent.get_input("  Enter Booking ID to view details: ").strip()
        
        if not booking_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            booking_id = int(booking_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        booking_raw = self.controller.get_booking_by_id(booking_id)
        booking = self._row_to_dict(booking_raw)
        
        if not booking:
            self.parent.print_error("Booking not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print(f"  📋 BOOKING DETAILS - {booking.get('booking_ref', '')}")
        print()
        self.parent.print_separator()
        print()
        
        status_display = {
            'pending': '🟡 Pending',
            'approved': '🟢 Approved',
            'rejected': '🔴 Rejected',
            'active': '🔵 Active',
            'completed': '✅ Completed',
            'cancelled': '⚪ Cancelled'
        }.get(booking.get('booking_status', ''), booking.get('booking_status', ''))
        
        customer_name = f"{booking.get('first_name', '')} {booking.get('last_name', '')}"
        vehicle_name = f"{booking.get('make', '')} {booking.get('model', '')} ({booking.get('license_plate', '')})"
        
        print(f"  Booking ID:        {booking.get('booking_id', '')}")
        print(f"  Reference:         {booking.get('booking_ref', '')}")
        print(f"  Customer:          {customer_name}")
        print(f"  Customer Email:    {booking.get('email', 'N/A')}")
        print(f"  Customer Phone:    {booking.get('phone', 'N/A')}")
        print(f"  Vehicle:           {vehicle_name}")
        print(f"  Start Date:        {booking.get('start_date', '')}")
        print(f"  End Date:          {booking.get('end_date', '')}")
        print(f"  Total Days:        {booking.get('total_days', 0)}")
        print(f"  Daily Rate:        ${booking.get('daily_rate', 0):.2f}")
        print(f"  Total Amount:      ${booking.get('total_amount', 0):.2f}")
        print(f"  Paid Amount:       ${booking.get('paid_amount', 0):.2f}")
        print(f"  Balance Amount:    ${booking.get('balance_amount', 0):.2f}")
        print(f"  Deposit Amount:    ${booking.get('deposit_amount', 0):.2f}")
        print(f"  Pickup Location:   {booking.get('pickup_location', 'N/A')}")
        print(f"  Drop-off Location: {booking.get('dropoff_location', 'N/A')}")
        print(f"  Status:            {status_display}")
        print(f"  Notes:             {booking.get('notes', 'None')}")
        if booking.get('rejection_reason'):
            print(f"  Rejection Reason:  {booking.get('rejection_reason', '')}")
        print()
        self.parent.print_separator()
        print()
        self.parent.get_input("Press Enter to continue...")
    
    def search_bookings(self):
        """Search for bookings"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  🔍 SEARCH BOOKINGS")
        print()
        
        search_term = self.parent.get_input("  Enter search term: ").strip()
        
        if not search_term:
            self.parent.print_warning("No search term entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        bookings_raw = self.controller.search_bookings(search_term)
        bookings = self._rows_to_dicts(bookings_raw)
        
        self.parent.clear_screen()
        self.parent.print_header()
        print(f"  🔍 SEARCH RESULTS: '{search_term}'")
        print()
        
        if not bookings:
            self.parent.print_info("No bookings found matching your search.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.display_booking_table(bookings)
        self.parent.get_input("\nPress Enter to continue...")
    
    def add_booking(self):
        """Add a new booking"""
        if not self.can_edit:
            self.parent.print_error("Access Denied! You don't have permission to add bookings.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print("  ➕ ADD NEW BOOKING")
        print()
        self.parent.print_separator()
        print()
        
        # Customer selection
        if not self.customers:
            self.parent.print_error("No customers available.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print("  Available Customers:")
        for i, c in enumerate(self.customers, 1):
            print(f"  {i}. {c.get('first_name', '')} {c.get('last_name', '')} ({c.get('email', '')})")
        print()
        
        customer_choice = self.parent.get_input("  Select customer (number): ").strip()
        try:
            c_idx = int(customer_choice) - 1
            if c_idx < 0 or c_idx >= len(self.customers):
                self.parent.print_error("Invalid customer selection!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            customer_id = self.customers[c_idx]['customer_id']
        except ValueError:
            self.parent.print_error("Invalid input!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        # Vehicle selection
        if not self.vehicles:
            self.parent.print_error("No vehicles available.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print()
        print("  Available Vehicles:")
        for i, v in enumerate(self.vehicles, 1):
            status = "🔴" if v.get('status') != 'available' else "🟢"
            print(f"  {i}. {v.get('make', '')} {v.get('model', '')} ({v.get('license_plate', '')}) {status}")
        print()
        
        vehicle_choice = self.parent.get_input("  Select vehicle (number): ").strip()
        try:
            v_idx = int(vehicle_choice) - 1
            if v_idx < 0 or v_idx >= len(self.vehicles):
                self.parent.print_error("Invalid vehicle selection!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            vehicle_id = self.vehicles[v_idx]['id']
            daily_rate = self.vehicles[v_idx].get('daily_rate', 0)
        except ValueError:
            self.parent.print_error("Invalid input!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        # Booking details
        print()
        booking_ref = self.controller.get_next_booking_ref()
        print(f"  Booking Reference: {booking_ref}")
        print()
        
        start_date = self.parent.get_input("  Start Date (YYYY-MM-DD): ").strip()
        end_date = self.parent.get_input("  End Date (YYYY-MM-DD): ").strip()
        pickup_location = self.parent.get_input("  Pickup Location: ").strip()
        dropoff_location = self.parent.get_input("  Drop-off Location: ").strip()
        deposit_amount = self.parent.get_input("  Deposit Amount ($): ").strip() or "0"
        notes = self.parent.get_input("  Notes: ").strip()
        
        # Validation
        if not start_date or not end_date:
            self.parent.print_error("Start and end dates are required!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if end <= start:
                self.parent.print_error("End date must be after start date!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            total_days = (end - start).days
        except ValueError:
            self.parent.print_error("Invalid date format! Use YYYY-MM-DD")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            deposit_amount = float(deposit_amount)
            if deposit_amount < 0:
                self.parent.print_error("Deposit cannot be negative!")
                self.parent.get_input("\nPress Enter to continue...")
                return
        except ValueError:
            self.parent.print_error("Deposit must be a number!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        total_amount = total_days * daily_rate
        
        # Confirm
        print()
        print("  Booking Details:")
        print(f"  Reference: {booking_ref}")
        print(f"  Customer: {self.customers[c_idx]['first_name']} {self.customers[c_idx]['last_name']}")
        print(f"  Vehicle: {self.vehicles[v_idx]['make']} {self.vehicles[v_idx]['model']}")
        print(f"  Dates: {start_date} to {end_date} ({total_days} days)")
        print(f"  Daily Rate: ${daily_rate:.2f}")
        print(f"  Total Amount: ${total_amount:.2f}")
        print(f"  Deposit: ${deposit_amount:.2f}")
        print()
        
        confirm = self.parent.get_input("  Add booking? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Booking addition cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        data = {
            'booking_ref': booking_ref,
            'customer_id': customer_id,
            'vehicle_id': vehicle_id,
            'start_date': start_date,
            'end_date': end_date,
            'pickup_location': pickup_location,
            'dropoff_location': dropoff_location,
            'daily_rate': daily_rate,
            'deposit_amount': deposit_amount,
            'booking_status': 'pending',
            'notes': notes
        }
        
        result = self.controller.add_booking(data)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def edit_booking(self):
        """Edit a booking"""
        if not self.can_edit:
            self.parent.print_error("Access Denied! You don't have permission to edit bookings.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        booking_id = self.parent.get_input("  Enter Booking ID to edit: ").strip()
        
        if not booking_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            booking_id = int(booking_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        booking_raw = self.controller.get_booking_by_id(booking_id)
        booking = self._row_to_dict(booking_raw)
        
        if not booking:
            self.parent.print_error("Booking not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print(f"  ✏️ EDIT BOOKING - {booking.get('booking_ref', '')}")
        print()
        self.parent.print_separator()
        print()
        
        # Customer selection
        print("  Available Customers:")
        current_customer_id = booking.get('customer_id')
        for i, c in enumerate(self.customers, 1):
            marker = " (current)" if c.get('customer_id') == current_customer_id else ""
            print(f"  {i}. {c.get('first_name', '')} {c.get('last_name', '')} ({c.get('email', '')}){marker}")
        print()
        
        customer_choice = self.parent.get_input("  Select customer (number) [keep current]: ").strip()
        if customer_choice:
            try:
                c_idx = int(customer_choice) - 1
                if 0 <= c_idx < len(self.customers):
                    customer_id = self.customers[c_idx]['customer_id']
                else:
                    customer_id = current_customer_id
            except ValueError:
                customer_id = current_customer_id
        else:
            customer_id = current_customer_id
        
        # Vehicle selection
        print()
        print("  Available Vehicles:")
        current_vehicle_id = booking.get('vehicle_id')
        for i, v in enumerate(self.vehicles, 1):
            marker = " (current)" if v.get('id') == current_vehicle_id else ""
            status = "🔴" if v.get('status') != 'available' else "🟢"
            print(f"  {i}. {v.get('make', '')} {v.get('model', '')} ({v.get('license_plate', '')}) {status}{marker}")
        print()
        
        vehicle_choice = self.parent.get_input("  Select vehicle (number) [keep current]: ").strip()
        if vehicle_choice:
            try:
                v_idx = int(vehicle_choice) - 1
                if 0 <= v_idx < len(self.vehicles):
                    vehicle_id = self.vehicles[v_idx]['id']
                    daily_rate = self.vehicles[v_idx].get('daily_rate', 0)
                else:
                    vehicle_id = current_vehicle_id
                    daily_rate = booking.get('daily_rate', 0)
            except ValueError:
                vehicle_id = current_vehicle_id
                daily_rate = booking.get('daily_rate', 0)
        else:
            vehicle_id = current_vehicle_id
            daily_rate = booking.get('daily_rate', 0)
        
        # Booking details
        print()
        start_date = self.parent.get_input(f"  Start Date [{booking.get('start_date', '')}]: ").strip()
        end_date = self.parent.get_input(f"  End Date [{booking.get('end_date', '')}]: ").strip()
        pickup_location = self.parent.get_input(f"  Pickup Location [{booking.get('pickup_location', '')}]: ").strip()
        dropoff_location = self.parent.get_input(f"  Drop-off Location [{booking.get('dropoff_location', '')}]: ").strip()
        deposit_amount = self.parent.get_input(f"  Deposit Amount ($) [{booking.get('deposit_amount', 0)}]: ").strip()
        notes = self.parent.get_input(f"  Notes [{booking.get('notes', '')}]: ").strip()
        
        # Use existing values if not changed
        start_date = start_date if start_date else booking.get('start_date', '')
        end_date = end_date if end_date else booking.get('end_date', '')
        
        # Validate dates
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if end <= start:
                self.parent.print_error("End date must be after start date!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            total_days = (end - start).days
        except ValueError:
            self.parent.print_error("Invalid date format! Use YYYY-MM-DD")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            deposit_amount = float(deposit_amount) if deposit_amount else booking.get('deposit_amount', 0)
            if deposit_amount < 0:
                self.parent.print_error("Deposit cannot be negative!")
                self.parent.get_input("\nPress Enter to continue...")
                return
        except ValueError:
            self.parent.print_error("Deposit must be a number!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        total_amount = total_days * daily_rate
        
        data = {
            'booking_ref': booking.get('booking_ref', ''),
            'customer_id': customer_id,
            'vehicle_id': vehicle_id,
            'start_date': start_date,
            'end_date': end_date,
            'pickup_location': pickup_location if pickup_location else booking.get('pickup_location', ''),
            'dropoff_location': dropoff_location if dropoff_location else booking.get('dropoff_location', ''),
            'daily_rate': daily_rate,
            'deposit_amount': deposit_amount,
            'booking_status': booking.get('booking_status', 'pending'),
            'notes': notes if notes else booking.get('notes', '')
        }
        
        # Confirm
        print()
        print("  New values:")
        print(f"  Dates: {start_date} to {end_date} ({total_days} days)")
        print(f"  Total Amount: ${total_amount:.2f}")
        print(f"  Deposit: ${deposit_amount:.2f}")
        print()
        
        confirm = self.parent.get_input("  Save changes? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Changes discarded.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        result = self.controller.update_booking(booking_id, data)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def approve_booking(self):
        """Approve a booking"""
        if not self.can_approve:
            self.parent.print_error("Access Denied! Only administrators can approve bookings.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        booking_id = self.parent.get_input("  Enter Booking ID to approve: ").strip()
        
        if not booking_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            booking_id = int(booking_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        booking_raw = self.controller.get_booking_by_id(booking_id)
        booking = self._row_to_dict(booking_raw)
        
        if not booking:
            self.parent.print_error("Booking not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        if booking.get('booking_status') != 'pending':
            self.parent.print_error(f"Only pending bookings can be approved. Current status: {booking.get('booking_status', '')}")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print()
        print(f"  Booking: {booking.get('booking_ref', '')}")
        print(f"  Customer: {booking.get('first_name', '')} {booking.get('last_name', '')}")
        print(f"  Vehicle: {booking.get('make', '')} {booking.get('model', '')}")
        print(f"  Amount: ${booking.get('total_amount', 0):.2f}")
        print()
        
        confirm = self.parent.get_input("  Approve this booking? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Approval cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        user_id = self.user.get('id', 1)
        result = self.controller.approve_booking(booking_id, user_id)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def reject_booking(self):
        """Reject a booking"""
        if not self.can_approve:
            self.parent.print_error("Access Denied! Only administrators can reject bookings.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        booking_id = self.parent.get_input("  Enter Booking ID to reject: ").strip()
        
        if not booking_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            booking_id = int(booking_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        booking_raw = self.controller.get_booking_by_id(booking_id)
        booking = self._row_to_dict(booking_raw)
        
        if not booking:
            self.parent.print_error("Booking not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        if booking.get('booking_status') != 'pending':
            self.parent.print_error(f"Only pending bookings can be rejected. Current status: {booking.get('booking_status', '')}")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print()
        print(f"  Booking: {booking.get('booking_ref', '')}")
        print(f"  Customer: {booking.get('first_name', '')} {booking.get('last_name', '')}")
        print(f"  Vehicle: {booking.get('make', '')} {booking.get('model', '')}")
        print()
        
        reason = self.parent.get_input("  Rejection Reason: ").strip()
        if not reason:
            self.parent.print_error("Rejection reason is required!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        confirm = self.parent.get_input("  Reject this booking? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Rejection cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        result = self.controller.reject_booking(booking_id, reason)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def delete_booking(self):
        """Delete a booking"""
        if not self.can_edit:
            self.parent.print_error("Access Denied!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        booking_id = self.parent.get_input("  Enter Booking ID to delete: ").strip()
        
        if not booking_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            booking_id = int(booking_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        booking_raw = self.controller.get_booking_by_id(booking_id)
        booking = self._row_to_dict(booking_raw)
        
        if not booking:
            self.parent.print_error("Booking not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print()
        self.parent.print_warning(f"You are about to delete booking: {booking.get('booking_ref', '')}")
        print(f"  Customer: {booking.get('first_name', '')} {booking.get('last_name', '')}")
        print("  This action cannot be undone!")
        print()
        
        confirm = self.parent.get_input("  Confirm delete? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Deletion cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        result = self.controller.delete_booking(booking_id)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_menu(self):
        """Export bookings menu"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📊 EXPORT BOOKINGS")
        print()
        self.parent.print_separator()
        print()
        print("  [1] Export to CSV")
        print("  [2] Export to Excel")
        print("  [3] Export to PDF")
        print("  [4] Back")
        print()
        self.parent.print_separator()
        print()
        
        choice = self.parent.get_input("  Select option: ").strip()
        
        if choice == "1":
            self.export_csv()
        elif choice == "2":
            self.export_excel()
        elif choice == "3":
            self.export_pdf()
        elif choice == "4":
            return
        else:
            self.parent.print_error("Invalid option")
            self.parent.get_input("\nPress Enter to continue...")
    
    def export_csv(self):
        """Export to CSV"""
        bookings_raw = self.controller.get_all_bookings()
        bookings = self._rows_to_dicts(bookings_raw)
        
        if not bookings:
            self.parent.print_warning("No bookings to export.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        import csv
        
        filename = f"bookings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'booking_id', 'booking_ref', 'customer', 'vehicle',
                    'start_date', 'end_date', 'total_days', 'daily_rate',
                    'total_amount', 'paid_amount', 'balance_amount',
                    'deposit_amount', 'booking_status', 'created_at'
                ])
                writer.writeheader()
                for booking in bookings:
                    customer_name = f"{booking.get('first_name', '')} {booking.get('last_name', '')}"
                    vehicle_name = f"{booking.get('make', '')} {booking.get('model', '')} ({booking.get('license_plate', '')})"
                    writer.writerow({
                        'booking_id': booking.get('booking_id', ''),
                        'booking_ref': booking.get('booking_ref', ''),
                        'customer': customer_name,
                        'vehicle': vehicle_name,
                        'start_date': booking.get('start_date', ''),
                        'end_date': booking.get('end_date', ''),
                        'total_days': booking.get('total_days', ''),
                        'daily_rate': booking.get('daily_rate', ''),
                        'total_amount': booking.get('total_amount', ''),
                        'paid_amount': booking.get('paid_amount', ''),
                        'balance_amount': booking.get('balance_amount', ''),
                        'deposit_amount': booking.get('deposit_amount', ''),
                        'booking_status': booking.get('booking_status', ''),
                        'created_at': booking.get('created_at', '')
                    })
            
            self.parent.print_success(f"Exported {len(bookings)} bookings to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_excel(self):
        """Export to Excel"""
        bookings_raw = self.controller.get_all_bookings()
        bookings = self._rows_to_dicts(bookings_raw)
        
        if not bookings:
            self.parent.print_warning("No bookings to export.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            import openpyxl
        except ImportError:
            self.parent.print_error("Please install openpyxl: pip install openpyxl")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        filename = f"bookings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Bookings"
            
            headers = ['ID', 'Reference', 'Customer', 'Vehicle', 'Start Date', 'End Date',
                      'Days', 'Daily Rate', 'Total', 'Paid', 'Balance', 'Deposit', 'Status']
            ws.append(headers)
            
            for booking in bookings:
                customer_name = f"{booking.get('first_name', '')} {booking.get('last_name', '')}"
                vehicle_name = f"{booking.get('make', '')} {booking.get('model', '')} ({booking.get('license_plate', '')})"
                ws.append([
                    booking.get('booking_id', ''),
                    booking.get('booking_ref', ''),
                    customer_name,
                    vehicle_name,
                    booking.get('start_date', ''),
                    booking.get('end_date', ''),
                    booking.get('total_days', ''),
                    booking.get('daily_rate', ''),
                    booking.get('total_amount', ''),
                    booking.get('paid_amount', ''),
                    booking.get('balance_amount', ''),
                    booking.get('deposit_amount', ''),
                    booking.get('booking_status', '')
                ])
            
            wb.save(filename)
            self.parent.print_success(f"Exported {len(bookings)} bookings to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_pdf(self):
        """Export to PDF"""
        bookings_raw = self.controller.get_all_bookings()
        bookings = self._rows_to_dicts(bookings_raw)
        
        if not bookings:
            self.parent.print_warning("No bookings to export.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import landscape, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError:
            self.parent.print_error("Please install reportlab: pip install reportlab")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        filename = f"bookings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
            styles = getSampleStyleSheet()
            
            elements = []
            
            title = Paragraph("Bookings Report", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            data = [['ID', 'Ref', 'Customer', 'Vehicle', 'Start', 'End', 'Total', 'Status']]
            
            for booking in bookings:
                customer_name = f"{booking.get('first_name', '')} {booking.get('last_name', '')}"[:20]
                vehicle_name = f"{booking.get('make', '')} {booking.get('model', '')}"[:20]
                data.append([
                    str(booking.get('booking_id', '')),
                    booking.get('booking_ref', ''),
                    customer_name,
                    vehicle_name,
                    booking.get('start_date', '')[:10],
                    booking.get('end_date', '')[:10],
                    f"${booking.get('total_amount', 0):.2f}",
                    booking.get('booking_status', '').title()
                ])
            
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(table)
            doc.build(elements)
            
            self.parent.print_success(f"Exported {len(bookings)} bookings to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")