# views/customer_dashboard_cli.py
"""
CLI Customer Dashboard View
"""
from datetime import datetime


class CustomerDashboardCLI:
    """CLI View for Customer Dashboard"""
    
    def __init__(self, parent, db, user):
        self.parent = parent
        self.db = db
        self.user = user
        self.customer_id = user.get('customer_id') if user else None
        
        # Check if customer has a profile
        self.has_profile = self.customer_id is not None
    
    def show(self):
        """Show customer dashboard"""
        while True:
            self.parent.clear_screen()
            self.parent.print_header()
            
            print("  👤 CUSTOMER DASHBOARD")
            print()
            self.parent.print_separator()
            print()
            
            print("  Welcome! What would you like to do today?")
            print()
            
            print("  [1] 🚗 Browse Available Vehicles")
            print("  [2] 📋 View My Bookings")
            print("  [3] 💰 View My Payments")
            print("  [4] 🔐 Logout")
            print()
            self.parent.print_separator()
            print()
            
            choice = self.parent.get_input("  Select option: ").strip()
            
            if choice == "1":
                self.browse_vehicles()
            elif choice == "2":
                self.view_bookings()
            elif choice == "3":
                self.view_payments()
            elif choice == "4":
                break
            else:
                self.parent.print_error("Invalid option")
                self.parent.get_input("\nPress Enter to continue...")
    
    def browse_vehicles(self):
        """Browse available vehicles"""
        from views.customer_vehicles_cli import CustomerVehiclesCLI
        
        vehicles_view = CustomerVehiclesCLI(
            self.parent, 
            self.db, 
            self.customer_id,
            self.show_booking_form
        )
        vehicles_view.show()
    
    def show_booking_form(self, vehicle_id):
        """Show booking form for a vehicle"""
        from views.customer_booking_cli import CustomerBookingCLI
        
        # Debug: Print customer_id
        print(f"  Debug: Showing booking form with customer_id: {self.customer_id}")
        
        booking_view = CustomerBookingCLI(
            self.parent,
            self.db,
            self.customer_id,
            vehicle_id
        )
        booking_view.show()
    
    def view_bookings(self):
        """View customer bookings"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📋 MY BOOKINGS")
        print()
        
        if not self.customer_id:
            self.parent.print_error("Customer profile not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    b.booking_id,
                    b.booking_ref,
                    b.start_date,
                    b.end_date,
                    b.total_days,
                    b.total_amount,
                    b.paid_amount,
                    b.balance_amount,
                    b.booking_status,
                    b.created_at,
                    v.make,
                    v.model,
                    v.license_plate
                FROM bookings b
                JOIN vehicles v ON b.vehicle_id = v.id
                WHERE b.customer_id = ?
                ORDER BY b.created_at DESC
            """, (self.customer_id,))
            
            bookings = cursor.fetchall()
            cursor.close()
            
            if not bookings:
                self.parent.print_info("You have no bookings yet.")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            print("  " + "-" * 145)
            print(f"  {'ID':<5} {'Reference':<14} {'Vehicle':<22} "
                  f"{'Start':<12} {'End':<12} {'Total':<10} {'Status':<12}")
            print("  " + "-" * 145)
            
            for booking in bookings:
                # Convert to dict if needed
                if hasattr(booking, 'keys'):
                    booking = dict(booking)
                
                status_display = {
                    'pending': '🟡 Pending',
                    'approved': '🟢 Approved',
                    'rejected': '🔴 Rejected',
                    'active': '🔵 Active',
                    'completed': '✅ Completed',
                    'cancelled': '⚪ Cancelled'
                }.get(booking.get('booking_status'), booking.get('booking_status'))
                
                vehicle_name = f"{booking.get('make', '')} {booking.get('model', '')}"[:22]
                
                print(f"  {booking.get('booking_id', ''):<5} "
                      f"{booking.get('booking_ref', '')[:14]:<14} "
                      f"{vehicle_name:<22} "
                      f"{str(booking.get('start_date', ''))[:10]:<12} "
                      f"{str(booking.get('end_date', ''))[:10]:<12} "
                      f"${booking.get('total_amount', 0):<9.2f} "
                      f"{status_display:<12}")
            
            print("  " + "-" * 145)
            print()
            
            # Option to view booking details
            view_detail = self.parent.get_input("  View booking details? (y/n): ").strip().lower()
            if view_detail == 'y' or view_detail == 'yes':
                self.view_booking_details()
            else:
                self.parent.get_input("Press Enter to continue...")
                
        except Exception as e:
            self.parent.print_error(f"Error loading bookings: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")
    
    def view_booking_details(self):
        """View specific booking details"""
        booking_id = self.parent.get_input("  Enter Booking ID to view: ").strip()
        
        if not booking_id:
            return
        
        try:
            booking_id = int(booking_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    b.*,
                    v.make,
                    v.model,
                    v.year,
                    v.license_plate,
                    v.daily_rate as vehicle_daily_rate,
                    vc.name as category_name
                FROM bookings b
                JOIN vehicles v ON b.vehicle_id = v.id
                LEFT JOIN vehicle_categories vc ON v.category_id = vc.id
                WHERE b.booking_id = ? AND b.customer_id = ?
            """, (booking_id, self.customer_id))
            
            booking = cursor.fetchone()
            cursor.close()
            
            if not booking:
                self.parent.print_error("Booking not found.")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            # Convert to dict if needed
            if hasattr(booking, 'keys'):
                booking = dict(booking)
            
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
            }.get(booking.get('booking_status'), booking.get('booking_status'))
            
            vehicle_name = f"{booking.get('make', '')} {booking.get('model', '')} ({booking.get('year', '')})"
            
            print(f"  Booking ID:        {booking.get('booking_id', '')}")
            print(f"  Reference:         {booking.get('booking_ref', '')}")
            print(f"  Vehicle:           {vehicle_name}")
            print(f"  License Plate:     {booking.get('license_plate', '')}")
            print(f"  Category:          {booking.get('category_name', 'N/A')}")
            print(f"  Start Date:        {booking.get('start_date', '')}")
            print(f"  End Date:          {booking.get('end_date', '')}")
            print(f"  Total Days:        {booking.get('total_days', 0)}")
            print(f"  Daily Rate:        ${booking.get('vehicle_daily_rate', 0):.2f}")
            print(f"  Total Amount:      ${booking.get('total_amount', 0):.2f}")
            print(f"  Paid Amount:       ${booking.get('paid_amount', 0):.2f}")
            print(f"  Balance Amount:    ${booking.get('balance_amount', 0):.2f}")
            print(f"  Status:            {status_display}")
            print(f"  Created At:        {booking.get('created_at', '')}")
            print()
            
            # If booking is approved and has balance, offer payment option
            if booking.get('booking_status') == 'approved' and booking.get('balance_amount', 0) > 0:
                self.parent.print_info("This booking is approved and has a pending balance.")
                print()
                pay_choice = self.parent.get_input("  Make a payment? (y/n): ").strip().lower()
                if pay_choice == 'y' or pay_choice == 'yes':
                    from views.customer_payment_cli import CustomerPaymentCLI
                    payment_view = CustomerPaymentCLI(
                        self.parent,
                        self.db,
                        self.customer_id,
                        booking.get('booking_id'),
                        booking.get('booking_ref'),
                        booking.get('balance_amount')
                    )
                    payment_view.show()
                    return
            
            self.parent.get_input("\nPress Enter to continue...")
            
        except Exception as e:
            self.parent.print_error(f"Error loading booking: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")
    
    def view_payments(self):
        """View customer payments"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  💰 MY PAYMENTS")
        print()
        
        if not self.customer_id:
            self.parent.print_error("Customer profile not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    p.payment_id,
                    p.payment_type,
                    p.amount,
                    p.payment_method,
                    p.payment_status,
                    p.transaction_reference,
                    p.payment_date,
                    b.booking_ref
                FROM payments p
                JOIN bookings b ON p.booking_id = b.booking_id
                WHERE b.customer_id = ?
                ORDER BY p.payment_date DESC
            """, (self.customer_id,))
            
            payments = cursor.fetchall()
            cursor.close()
            
            if not payments:
                self.parent.print_info("You have no payments yet.")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            print("  " + "-" * 130)
            print(f"  {'ID':<5} {'Booking':<14} {'Type':<10} "
                  f"{'Amount':<10} {'Method':<14} {'Status':<12} {'Date':<16}")
            print("  " + "-" * 130)
            
            for payment in payments:
                # Convert to dict if needed
                if hasattr(payment, 'keys'):
                    payment = dict(payment)
                
                status_display = {
                    'paid': '🟢 Paid',
                    'pending': '🟡 Pending',
                    'failed': '🔴 Failed',
                    'refunded': '🔵 Refunded'
                }.get(payment.get('payment_status'), payment.get('payment_status'))
                
                payment_method = payment.get('payment_method', '').replace('_', ' ').title()
                
                print(f"  {payment.get('payment_id', ''):<5} "
                      f"{payment.get('booking_ref', '')[:14]:<14} "
                      f"{payment.get('payment_type', '')[:10]:<10} "
                      f"${payment.get('amount', 0):<9.2f} "
                      f"{payment_method[:14]:<14} "
                      f"{status_display:<12} "
                      f"{str(payment.get('payment_date', ''))[:16]:<16}")
            
            print("  " + "-" * 130)
            print()
            self.parent.get_input("Press Enter to continue...")
            
        except Exception as e:
            self.parent.print_error(f"Error loading payments: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")