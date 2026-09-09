# views/payment_view_cli.py
"""
CLI Payment Management View
"""
from datetime import datetime
from controllers.payment_controller import PaymentController


class PaymentViewCLI:
    """CLI View for Payment Management"""
    
    def __init__(self, parent, db, user):
        self.parent = parent
        self.db = db
        self.user = user
        self.controller = PaymentController(db)
        
        # Check user role for permissions
        self.user_role = user.get('role', 'staff') if user else 'staff'
        self.is_admin = self.user_role == 'admin'
        self.is_manager = self.user_role == 'manager'
        self.is_staff = self.user_role == 'staff'
        self.is_view_only = self.is_staff
        self.can_edit = self.is_admin or self.is_manager
        
        # Editing state
        self.editing_id = None
        
        # Load bookings
        self.bookings = []
        self.load_bookings()
    
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
    
    def load_bookings(self):
        """Load bookings for dropdown"""
        try:
            bookings_raw = self.controller.get_bookings()
            self.bookings = self._rows_to_dicts(bookings_raw)
        except Exception as e:
            self.parent.print_warning(f"Could not load bookings: {e}")
    
    def show(self):
        """Show payment management menu"""
        while True:
            self.parent.clear_screen()
            self.parent.print_header()
            
            print("  💰 PAYMENT MANAGEMENT")
            if self.is_view_only:
                print("  🔒 View Only Mode")
            print()
            self.parent.print_separator()
            print()
            
            # Show statistics
            payments_raw = self.controller.get_all_payments()
            payments = self._rows_to_dicts(payments_raw)
            total = len(payments) if payments else 0
            paid = sum(1 for p in payments if p.get('payment_status') == 'paid') if payments else 0
            pending = sum(1 for p in payments if p.get('payment_status') == 'pending') if payments else 0
            refunded = sum(1 for p in payments if p.get('payment_status') == 'refunded') if payments else 0
            
            print(f"  📊 Total Payments: {total}")
            print(f"  🟢 Paid: {paid}")
            print(f"  🟡 Pending: {pending}")
            print(f"  🔵 Refunded: {refunded}")
            print(f"  🔴 Failed: {total - paid - pending - refunded}")
            print()
            self.parent.print_separator()
            print()
            
            print("  [1] 📋 View All Payments")
            print("  [2] 🔍 Search Payments")
            if self.can_edit:
                print("  [3] ➕ Add Payment")
                print("  [4] ✏️ Edit Payment")
                print("  [5] 🗑️ Delete Payment")
            print("  [6] 📊 Export Payments")
            print("  [0] ↩️ Back to Main Menu")
            print()
            self.parent.print_separator()
            print()
            
            choice = self.parent.get_input("  Select option: ").strip()
            
            if choice == "1":
                self.view_all_payments()
            elif choice == "2":
                self.search_payments()
            elif choice == "3" and self.can_edit:
                self.add_payment()
            elif choice == "4" and self.can_edit:
                self.edit_payment()
            elif choice == "5" and self.can_edit:
                self.delete_payment()
            elif choice == "6":
                self.export_menu()
            elif choice == "0":
                break
            else:
                self.parent.print_error("Invalid option")
                self.parent.get_input("\nPress Enter to continue...")
    
    def view_all_payments(self):
        """View all payments in table format"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📋 ALL PAYMENTS")
        print()
        
        payments_raw = self.controller.get_all_payments()
        payments = self._rows_to_dicts(payments_raw)
        
        if not payments:
            self.parent.print_info("No payments found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.display_payment_table(payments)
        
        # Option to view details
        view_details = self.parent.get_input("  View payment details? (y/n): ").strip().lower()
        if view_details == 'y' or view_details == 'yes':
            self.view_payment_details()
        else:
            self.parent.get_input("Press Enter to continue...")
    
    def display_payment_table(self, payments):
        """Display payments in a formatted table"""
        print("  " + "-" * 130)
        print(f"  {'ID':<5} {'Booking':<12} {'Customer':<20} {'Type':<10} "
              f"{'Amount':<10} {'Method':<12} {'Status':<10} {'Date':<16}")
        print("  " + "-" * 130)
        
        for payment in payments:
            status_display = {
                'paid': '🟢 Paid',
                'pending': '🟡 Pending',
                'failed': '🔴 Failed',
                'refunded': '🔵 Refunded'
            }.get(payment.get('payment_status', ''), payment.get('payment_status', ''))
            
            customer_name = f"{payment.get('first_name', '')} {payment.get('last_name', '')}"[:20]
            payment_date = payment.get('payment_date', '')
            if payment_date and len(payment_date) > 16:
                payment_date = payment_date[:16]
            
            print(f"  {payment.get('payment_id', ''):<5} "
                  f"{payment.get('booking_ref', '')[:12]:<12} "
                  f"{customer_name:<20} "
                  f"{payment.get('payment_type', '')[:10]:<10} "
                  f"${payment.get('amount', 0):<9.2f} "
                  f"{payment.get('payment_method', '').replace('_', ' ')[:12]:<12} "
                  f"{status_display:<10} "
                  f"{payment_date:<16}")
        
        print("  " + "-" * 130)
        print(f"  Total: {len(payments)} payments")
        print()
    
    def view_payment_details(self):
        """View detailed information about a specific payment"""
        payment_id = self.parent.get_input("  Enter Payment ID to view details: ").strip()
        
        if not payment_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            payment_id = int(payment_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        payment_raw = self.controller.get_payment_by_id(payment_id)
        payment = self._row_to_dict(payment_raw)
        
        if not payment:
            self.parent.print_error("Payment not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print(f"  💰 PAYMENT DETAILS - #{payment_id}")
        print()
        self.parent.print_separator()
        print()
        
        status_display = {
            'paid': '🟢 Paid',
            'pending': '🟡 Pending',
            'failed': '🔴 Failed',
            'refunded': '🔵 Refunded'
        }.get(payment.get('payment_status', ''), payment.get('payment_status', ''))
        
        customer_name = f"{payment.get('first_name', '')} {payment.get('last_name', '')}"
        
        print(f"  Payment ID:        {payment.get('payment_id', '')}")
        print(f"  Booking Reference: {payment.get('booking_ref', 'N/A')}")
        print(f"  Customer:          {customer_name}")
        print(f"  Payment Type:      {payment.get('payment_type', '').title()}")
        print(f"  Amount:            ${payment.get('amount', 0):.2f}")
        print(f"  Payment Method:    {payment.get('payment_method', '').replace('_', ' ').title()}")
        print(f"  Status:            {status_display}")
        print(f"  Transaction Ref:   {payment.get('transaction_reference', 'N/A') or 'N/A'}")
        print(f"  Payment Date:      {payment.get('payment_date', 'N/A') or 'N/A'}")
        print(f"  Notes:             {payment.get('notes', 'None') or 'None'}")
        print()
        self.parent.print_separator()
        print()
        self.parent.get_input("Press Enter to continue...")
    
    def search_payments(self):
        """Search for payments"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  🔍 SEARCH PAYMENTS")
        print()
        
        search_term = self.parent.get_input("  Enter search term: ").strip()
        
        if not search_term:
            self.parent.print_warning("No search term entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        payments_raw = self.controller.search_payments(search_term)
        payments = self._rows_to_dicts(payments_raw)
        
        self.parent.clear_screen()
        self.parent.print_header()
        print(f"  🔍 SEARCH RESULTS: '{search_term}'")
        print()
        
        if not payments:
            self.parent.print_info("No payments found matching your search.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.display_payment_table(payments)
        self.parent.get_input("\nPress Enter to continue...")
    
    def add_payment(self):
        """Add a new payment"""
        if not self.can_edit:
            self.parent.print_error("Access Denied! You don't have permission to add payments.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print("  ➕ ADD NEW PAYMENT")
        print()
        self.parent.print_separator()
        print()
        
        # Booking selection
        if not self.bookings:
            self.parent.print_error("No bookings available.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print("  Available Bookings:")
        for i, b in enumerate(self.bookings, 1):
            customer = f"{b.get('first_name', '')} {b.get('last_name', '')}"
            print(f"  {i}. {b.get('booking_ref', '')} - {customer} (Balance: ${b.get('balance_amount', 0):.2f})")
        print()
        
        booking_choice = self.parent.get_input("  Select booking (number): ").strip()
        try:
            b_idx = int(booking_choice) - 1
            if b_idx < 0 or b_idx >= len(self.bookings):
                self.parent.print_error("Invalid booking selection!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            booking_id = self.bookings[b_idx]['booking_id']
        except ValueError:
            self.parent.print_error("Invalid input!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        # Payment details
        print()
        print("  Payment Types:")
        print("  1. deposit")
        print("  2. final")
        print("  3. refund")
        print()
        
        type_choice = self.parent.get_input("  Select payment type (1-3): ").strip()
        type_map = {
            '1': 'deposit',
            '2': 'final',
            '3': 'refund'
        }
        if type_choice not in type_map:
            self.parent.print_error("Invalid payment type!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        payment_type = type_map[type_choice]
        
        amount = self.parent.get_input("  Amount ($): ").strip()
        if not amount:
            self.parent.print_error("Amount is required!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            amount = float(amount)
            if amount <= 0:
                self.parent.print_error("Amount must be greater than 0!")
                self.parent.get_input("\nPress Enter to continue...")
                return
        except ValueError:
            self.parent.print_error("Amount must be a number!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print()
        print("  Payment Methods:")
        print("  1. cash")
        print("  2. card")
        print("  3. bank_transfer")
        print("  4. online")
        print()
        
        method_choice = self.parent.get_input("  Select payment method (1-4): ").strip()
        method_map = {
            '1': 'cash',
            '2': 'card',
            '3': 'bank_transfer',
            '4': 'online'
        }
        if method_choice not in method_map:
            self.parent.print_error("Invalid payment method!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        payment_method = method_map[method_choice]
        
        print()
        print("  Payment Status:")
        print("  1. paid")
        print("  2. pending")
        print("  3. failed")
        print("  4. refunded")
        print()
        
        status_choice = self.parent.get_input("  Select status (1-4) [default: 1]: ").strip() or "1"
        status_map = {
            '1': 'paid',
            '2': 'pending',
            '3': 'failed',
            '4': 'refunded'
        }
        if status_choice not in status_map:
            self.parent.print_error("Invalid status!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        payment_status = status_map[status_choice]
        
        transaction_ref = self.parent.get_input("  Transaction Reference: ").strip()
        payment_date = self.parent.get_input(f"  Payment Date [YYYY-MM-DD HH:MM:SS] [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: ").strip()
        if not payment_date:
            payment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        notes = self.parent.get_input("  Notes: ").strip()
        
        # Confirm
        print()
        print("  Payment Details:")
        print(f"  Booking: {self.bookings[b_idx]['booking_ref']}")
        print(f"  Type: {payment_type}")
        print(f"  Amount: ${amount:.2f}")
        print(f"  Method: {payment_method.replace('_', ' ').title()}")
        print(f"  Status: {payment_status}")
        print()
        
        confirm = self.parent.get_input("  Add payment? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Payment addition cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        data = {
            'booking_id': booking_id,
            'payment_type': payment_type,
            'amount': amount,
            'payment_method': payment_method,
            'payment_status': payment_status,
            'transaction_reference': transaction_ref,
            'payment_date': payment_date,
            'notes': notes
        }
        
        result = self.controller.add_payment(data)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def edit_payment(self):
        """Edit a payment"""
        if not self.can_edit:
            self.parent.print_error("Access Denied! You don't have permission to edit payments.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        payment_id = self.parent.get_input("  Enter Payment ID to edit: ").strip()
        
        if not payment_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            payment_id = int(payment_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        payment_raw = self.controller.get_payment_by_id(payment_id)
        payment = self._row_to_dict(payment_raw)
        
        if not payment:
            self.parent.print_error("Payment not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print(f"  ✏️ EDIT PAYMENT - #{payment_id}")
        print()
        self.parent.print_separator()
        print()
        
        # Booking selection
        print("  Available Bookings:")
        current_booking_id = payment.get('booking_id')
        for i, b in enumerate(self.bookings, 1):
            customer = f"{b.get('first_name', '')} {b.get('last_name', '')}"
            marker = " (current)" if b.get('booking_id') == current_booking_id else ""
            print(f"  {i}. {b.get('booking_ref', '')} - {customer} (Balance: ${b.get('balance_amount', 0):.2f}){marker}")
        print()
        
        booking_choice = self.parent.get_input("  Select booking (number) [keep current]: ").strip()
        if booking_choice:
            try:
                b_idx = int(booking_choice) - 1
                if 0 <= b_idx < len(self.bookings):
                    booking_id = self.bookings[b_idx]['booking_id']
                else:
                    booking_id = current_booking_id
            except ValueError:
                booking_id = current_booking_id
        else:
            booking_id = current_booking_id
        
        # Payment details
        print()
        print("  Payment Types:")
        print("  1. deposit")
        print("  2. final")
        print("  3. refund")
        print()
        
        current_type = payment.get('payment_type', 'deposit')
        type_map_reverse = {'deposit': '1', 'final': '2', 'refund': '3'}
        default_type = type_map_reverse.get(current_type, '1')
        
        type_choice = self.parent.get_input(f"  Select payment type (1-3) [current: {current_type}]: ").strip() or default_type
        type_map = {
            '1': 'deposit',
            '2': 'final',
            '3': 'refund'
        }
        if type_choice not in type_map:
            self.parent.print_error("Invalid payment type!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        payment_type = type_map[type_choice]
        
        amount = self.parent.get_input(f"  Amount ($) [{payment.get('amount', 0)}]: ").strip()
        if amount:
            try:
                amount = float(amount)
                if amount <= 0:
                    self.parent.print_error("Amount must be greater than 0!")
                    self.parent.get_input("\nPress Enter to continue...")
                    return
            except ValueError:
                self.parent.print_error("Amount must be a number!")
                self.parent.get_input("\nPress Enter to continue...")
                return
        else:
            amount = payment.get('amount', 0)
        
        print()
        print("  Payment Methods:")
        print("  1. cash")
        print("  2. card")
        print("  3. bank_transfer")
        print("  4. online")
        print()
        
        current_method = payment.get('payment_method', 'cash')
        method_map_reverse = {'cash': '1', 'card': '2', 'bank_transfer': '3', 'online': '4'}
        default_method = method_map_reverse.get(current_method, '1')
        
        method_choice = self.parent.get_input(f"  Select payment method (1-4) [current: {current_method}]: ").strip() or default_method
        method_map = {
            '1': 'cash',
            '2': 'card',
            '3': 'bank_transfer',
            '4': 'online'
        }
        if method_choice not in method_map:
            self.parent.print_error("Invalid payment method!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        payment_method = method_map[method_choice]
        
        print()
        print("  Payment Status:")
        print("  1. paid")
        print("  2. pending")
        print("  3. failed")
        print("  4. refunded")
        print()
        
        current_status = payment.get('payment_status', 'paid')
        status_map_reverse = {'paid': '1', 'pending': '2', 'failed': '3', 'refunded': '4'}
        default_status = status_map_reverse.get(current_status, '1')
        
        status_choice = self.parent.get_input(f"  Select status (1-4) [current: {current_status}]: ").strip() or default_status
        status_map = {
            '1': 'paid',
            '2': 'pending',
            '3': 'failed',
            '4': 'refunded'
        }
        if status_choice not in status_map:
            self.parent.print_error("Invalid status!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        payment_status = status_map[status_choice]
        
        transaction_ref = self.parent.get_input(f"  Transaction Reference [{payment.get('transaction_reference', '')}]: ").strip()
        if not transaction_ref:
            transaction_ref = payment.get('transaction_reference', '')
        
        payment_date = self.parent.get_input(f"  Payment Date [{payment.get('payment_date', '')}]: ").strip()
        if not payment_date:
            payment_date = payment.get('payment_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        notes = self.parent.get_input(f"  Notes [{payment.get('notes', '')}]: ").strip()
        if not notes:
            notes = payment.get('notes', '')
        
        # Confirm
        print()
        print("  Updated Details:")
        print(f"  Type: {payment_type}")
        print(f"  Amount: ${amount:.2f}")
        print(f"  Method: {payment_method.replace('_', ' ').title()}")
        print(f"  Status: {payment_status}")
        print()
        
        confirm = self.parent.get_input("  Save changes? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Changes discarded.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        data = {
            'booking_id': booking_id,
            'payment_type': payment_type,
            'amount': amount,
            'payment_method': payment_method,
            'payment_status': payment_status,
            'transaction_reference': transaction_ref,
            'payment_date': payment_date,
            'notes': notes
        }
        
        result = self.controller.update_payment(payment_id, data)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def delete_payment(self):
        """Delete a payment"""
        if not self.can_edit:
            self.parent.print_error("Access Denied!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        payment_id = self.parent.get_input("  Enter Payment ID to delete: ").strip()
        
        if not payment_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            payment_id = int(payment_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        payment_raw = self.controller.get_payment_by_id(payment_id)
        payment = self._row_to_dict(payment_raw)
        
        if not payment:
            self.parent.print_error("Payment not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print()
        self.parent.print_warning(f"You are about to delete payment #{payment_id}")
        print(f"  Amount: ${payment.get('amount', 0):.2f}")
        print(f"  Booking: {payment.get('booking_ref', 'N/A')}")
        print("  This will recalculate the booking balance!")
        print("  This action cannot be undone!")
        print()
        
        confirm = self.parent.get_input("  Confirm delete? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Deletion cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        result = self.controller.delete_payment(payment_id)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_menu(self):
        """Export payments menu"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📊 EXPORT PAYMENTS")
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
        payments_raw = self.controller.get_all_payments()
        payments = self._rows_to_dicts(payments_raw)
        
        if not payments:
            self.parent.print_warning("No payments to export.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        import csv
        
        filename = f"payments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'payment_id', 'booking_ref', 'customer', 'payment_type',
                    'amount', 'payment_method', 'payment_status',
                    'transaction_reference', 'payment_date'
                ])
                writer.writeheader()
                for payment in payments:
                    customer_name = f"{payment.get('first_name', '')} {payment.get('last_name', '')}"
                    writer.writerow({
                        'payment_id': payment.get('payment_id', ''),
                        'booking_ref': payment.get('booking_ref', ''),
                        'customer': customer_name,
                        'payment_type': payment.get('payment_type', ''),
                        'amount': payment.get('amount', ''),
                        'payment_method': payment.get('payment_method', ''),
                        'payment_status': payment.get('payment_status', ''),
                        'transaction_reference': payment.get('transaction_reference', ''),
                        'payment_date': payment.get('payment_date', '')
                    })
            
            self.parent.print_success(f"Exported {len(payments)} payments to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_excel(self):
        """Export to Excel"""
        payments_raw = self.controller.get_all_payments()
        payments = self._rows_to_dicts(payments_raw)
        
        if not payments:
            self.parent.print_warning("No payments to export.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            import openpyxl
        except ImportError:
            self.parent.print_error("Please install openpyxl: pip install openpyxl")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        filename = f"payments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Payments"
            
            headers = ['ID', 'Booking Ref', 'Customer', 'Type', 'Amount', 
                      'Method', 'Status', 'Transaction Ref', 'Payment Date']
            ws.append(headers)
            
            for payment in payments:
                customer_name = f"{payment.get('first_name', '')} {payment.get('last_name', '')}"
                ws.append([
                    payment.get('payment_id', ''),
                    payment.get('booking_ref', ''),
                    customer_name,
                    payment.get('payment_type', ''),
                    payment.get('amount', ''),
                    payment.get('payment_method', ''),
                    payment.get('payment_status', ''),
                    payment.get('transaction_reference', ''),
                    payment.get('payment_date', '')
                ])
            
            wb.save(filename)
            self.parent.print_success(f"Exported {len(payments)} payments to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_pdf(self):
        """Export to PDF"""
        payments_raw = self.controller.get_all_payments()
        payments = self._rows_to_dicts(payments_raw)
        
        if not payments:
            self.parent.print_warning("No payments to export.")
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
        
        filename = f"payments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
            styles = getSampleStyleSheet()
            
            elements = []
            
            title = Paragraph("Payments Report", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            data = [['ID', 'Booking', 'Customer', 'Type', 'Amount', 'Method', 'Status']]
            
            for payment in payments:
                customer_name = f"{payment.get('first_name', '')} {payment.get('last_name', '')}"[:20]
                data.append([
                    str(payment.get('payment_id', '')),
                    payment.get('booking_ref', ''),
                    customer_name,
                    payment.get('payment_type', '').title(),
                    f"${payment.get('amount', 0):.2f}",
                    payment.get('payment_method', '').replace('_', ' ').title(),
                    payment.get('payment_status', '').title()
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
            
            self.parent.print_success(f"Exported {len(payments)} payments to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")