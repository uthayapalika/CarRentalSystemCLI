# controllers/customer_booking_controller.py
"""
Customer Booking Controller
"""
from datetime import datetime


class CustomerBookingController:
    """Controller for customer booking operations"""
    
    def __init__(self, db):
        self.db = db
    
    def get_vehicle_details(self, vehicle_id):
        """Get vehicle details with category info"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    v.*,
                    vc.name as category_name,
                    vc.late_fee_rate
                FROM vehicles v
                LEFT JOIN vehicle_categories vc ON v.category_id = vc.id
                WHERE v.id = ? AND v.status = 'available'
            """, (vehicle_id,))
            
            vehicle = cursor.fetchone()
            cursor.close()
            
            return dict(vehicle) if vehicle else None
            
        except Exception as e:
            print(f"Error getting vehicle details: {e}")
            return None
    
    def create_booking(self, customer_id, vehicle_id, start_date, end_date, 
                       daily_rate, total_days, total_amount, notes=""):
        """Create a new booking"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Generate booking reference
            date_part = datetime.now().strftime("%Y%m%d")
            cursor.execute("SELECT COUNT(*) as count FROM bookings")
            count = cursor.fetchone()
            next_num = count['count'] + 1
            booking_ref = f"BR-{next_num:03d}-{date_part}"
            
            # Check vehicle availability
            cursor.execute("""
                SELECT booking_id FROM bookings 
                WHERE vehicle_id = ? 
                AND booking_status NOT IN ('rejected', 'cancelled', 'completed')
                AND start_date <= ? 
                AND end_date >= ?
            """, (vehicle_id, end_date, start_date))
            
            existing = cursor.fetchone()
            if existing:
                cursor.close()
                return False, "Vehicle is already booked for the selected dates.", None
            
            # Insert booking - FIXED: customer_id is used directly
            cursor.execute("""
                INSERT INTO bookings (
                    booking_ref,
                    customer_id,
                    vehicle_id,
                    start_date,
                    end_date,
                    daily_rate,
                    total_days,
                    total_amount,
                    paid_amount,
                    balance_amount,
                    deposit_amount,
                    booking_status,
                    notes,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                booking_ref,
                customer_id,  # This should be the customer_id from the customer table
                vehicle_id,
                start_date,
                end_date,
                daily_rate,
                total_days,
                total_amount,
                0,  # paid_amount
                total_amount,  # balance_amount
                0,  # deposit_amount
                'pending',  # booking_status
                notes,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            booking_id = cursor.lastrowid
            cursor.close()
            
            return True, "Booking created successfully", booking_ref
            
        except Exception as e:
            print(f"Error creating booking: {e}")
            return False, f"Database error: {str(e)}", None
    
    def get_customer_bookings(self, customer_id):
        """Get all bookings for a customer"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    b.*,
                    v.make,
                    v.model,
                    v.license_plate
                FROM bookings b
                JOIN vehicles v ON b.vehicle_id = v.id
                WHERE b.customer_id = ?
                ORDER BY b.created_at DESC
            """, (customer_id,))
            
            bookings = cursor.fetchall()
            cursor.close()
            
            return [dict(booking) for booking in bookings]
            
        except Exception as e:
            print(f"Error getting customer bookings: {e}")
            return []