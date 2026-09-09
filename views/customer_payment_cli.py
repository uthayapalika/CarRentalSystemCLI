# views/customer_payment_cli.py
"""
CLI Customer Payment View
"""
from datetime import datetime
import secrets
import string


class CustomerPaymentCLI:
    """CLI View for Customer Payment"""
    
    def __init__(self, parent, db, customer_id, booking_id, booking_ref, amount):
        self.parent = parent
        self.db = db
        self.customer_id = customer_id
        self.booking_id = booking_id
        self.booking_ref = booking_ref
        self.amount = amount
    
    def generate_transaction_ref(self):
        """Generate a unique transaction reference"""
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return f"TXN-{date_part}-{random_part}"
    
    def show(self):
        """Show payment form"""
        while True:
            self.parent.clear_screen()
            self.parent.print_header()
            
            print("  💳 MAKE PAYMENT")
            print()
            self.parent.print_separator()
            print()
            
            print("  Booking Information:")
            print(f"  Booking Reference: {self.booking_ref}")
            print(f"  Booking ID: #{self.booking_id}")
            print(f"  Total Amount: ${self.amount:.2f}")
            print()
            self.parent.print_separator()
            print()
            
            print("  Payment Type:")
            print("  [1] Deposit (20%)")
            print("  [2] Full Payment")
            print()
            
            payment_type_choice = self.parent.get_input("  Select payment type (1-2): ").strip()
            if payment_type_choice == "1":
                payment_type = "deposit"
                amount = self.amount * 0.20
                self.parent.print_info(f"Deposit amount: ${amount:.2f}")
            elif payment_type_choice == "2":
                payment_type = "final"
                amount = self.amount
                self.parent.print_info(f"Full amount: ${amount:.2f}")
            else:
                self.parent.print_error("Invalid choice!")
                self.parent.get_input("\nPress Enter to continue...")
                continue
            
            print()
            self.parent.print_separator()
            print()
            
            print("  💳 Card Details")
            print()
            card_number = self.parent.get_input("  Card Number (16 digits): ").strip()
            card_holder = self.parent.get_input("  Card Holder Name: ").strip()
            expiry_month = self.parent.get_input("  Expiry Month (MM): ").strip()
            expiry_year = self.parent.get_input("  Expiry Year (YYYY): ").strip()
            cvv = self.parent.get_input("  CVV (3-4 digits): ").strip()
            
            # Validation
            if len(card_number) < 16:
                self.parent.print_error("Please enter a valid 16-digit card number.")
                self.parent.get_input("\nPress Enter to continue...")
                continue
            
            if not card_holder:
                self.parent.print_error("Please enter the card holder name.")
                self.parent.get_input("\nPress Enter to continue...")
                continue
            
            if not expiry_month or not expiry_year:
                self.parent.print_error("Please enter the expiry date.")
                self.parent.get_input("\nPress Enter to continue...")
                continue
            
            if len(cvv) < 3:
                self.parent.print_error("Please enter a valid CVV.")
                self.parent.get_input("\nPress Enter to continue...")
                continue
            
            # Confirm
            print()
            self.parent.print_separator()
            print()
            
            print("  Payment Summary:")
            print(f"  Booking: {self.booking_ref}")
            print(f"  Payment Type: {payment_type.upper()}")
            print(f"  Amount: ${amount:.2f}")
            print()
            
            confirm = self.parent.get_input("  Confirm payment? (y/n): ").strip().lower()
            if confirm == 'n' or confirm == 'no':
                self.parent.print_warning("Payment cancelled.")
                self.parent.get_input("\nPress Enter to continue...")
                return
            if confirm != 'y' and confirm != 'yes':
                self.parent.print_error("Invalid input. Please enter 'y' or 'n'.")
                self.parent.get_input("\nPress Enter to continue...")
                continue
            
            # Process payment
            self.process_payment(payment_type, amount)
            break
    
    def process_payment(self, payment_type, amount):
        """Process the payment"""
        try:
            transaction_ref = self.generate_transaction_ref()
            payment_method = "card"
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Check if booking exists and is approved
            cursor.execute("""
                SELECT booking_status FROM bookings 
                WHERE booking_id = ? AND customer_id = ?
            """, (self.booking_id, self.customer_id))
            
            booking = cursor.fetchone()
            if not booking:
                self.parent.print_error("Booking not found.")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            if booking['booking_status'] != 'approved':
                self.parent.print_error("Booking must be approved before payment.")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            # Insert payment
            cursor.execute("""
                INSERT INTO payments (
                    booking_id,
                    payment_type,
                    amount,
                    payment_method,
                    payment_status,
                    transaction_reference,
                    payment_date,
                    notes,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.booking_id,
                payment_type,
                amount,
                payment_method,
                'paid',
                transaction_ref,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"Card payment for booking {self.booking_ref}",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            # Update booking paid amount
            cursor.execute("""
                UPDATE bookings 
                SET paid_amount = paid_amount + ?,
                    balance_amount = total_amount - paid_amount - ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE booking_id = ?
            """, (amount, amount, self.booking_id))
            
            conn.commit()
            cursor.close()
            
            self.parent.print_success("✅ Payment successful!")
            print()
            print(f"  Transaction Reference: {transaction_ref}")
            print(f"  Booking: {self.booking_ref}")
            print(f"  Amount Paid: ${amount:.2f}")
            print(f"  Payment Type: {payment_type.upper()}")
            print()
            self.parent.print_info("Thank you for your payment!")
            self.parent.get_input("\nPress Enter to continue...")
            
        except Exception as e:
            self.parent.print_error(f"Payment failed: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")