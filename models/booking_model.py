# models/booking_model.py

class BookingModel:
    def __init__(self, db):
        self.db = db

    # ==========================================================
    # HELPER METHODS
    # ==========================================================

    def _to_dict(self, row):
        """Convert sqlite3.Row to dict if needed"""
        if row is None:
            return None
        if isinstance(row, dict):
            return row
        # If it's a sqlite3.Row, convert to dict
        try:
            return {key: row[key] for key in row.keys()}
        except:
            return row

    def _to_dict_list(self, rows):
        """Convert list of sqlite3.Row to list of dicts"""
        if rows is None:
            return []
        if isinstance(rows, list) and len(rows) > 0:
            if isinstance(rows[0], dict):
                return rows
        return [self._to_dict(row) for row in rows] if rows else []

    # ==========================================================
    # READ
    # ==========================================================

    def get_all(self):
        """Get all bookings with customer and vehicle information"""
        query = """
            SELECT
                b.booking_id,
                b.booking_ref,
                b.customer_id,
                b.vehicle_id,
                b.start_date,
                b.end_date,
                b.pickup_location,
                b.dropoff_location,
                b.daily_rate,
                b.total_days,
                b.total_amount,
                b.deposit_amount,
                b.paid_amount,
                b.balance_amount,
                b.booking_status,
                b.rejection_reason,
                b.approved_by,
                b.approved_at,
                b.notes,
                b.created_at,
                b.updated_at,

                c.first_name,
                c.last_name,
                c.email,
                c.phone,

                v.make,
                v.model,
                v.year,
                v.license_plate

            FROM bookings b

            LEFT JOIN customers c
                ON b.customer_id = c.customer_id

            LEFT JOIN vehicles v
                ON b.vehicle_id = v.id

            ORDER BY b.created_at DESC
        """

        result = self.db.execute_query(query)
        return self._to_dict_list(result)

    def get_by_id(self, booking_id):
        """Get booking by ID"""
        query = """
            SELECT
                b.*,

                c.first_name,
                c.last_name,
                c.email,
                c.phone,

                v.make,
                v.model,
                v.year,
                v.license_plate

            FROM bookings b

            LEFT JOIN customers c
                ON b.customer_id = c.customer_id

            LEFT JOIN vehicles v
                ON b.vehicle_id = v.id

            WHERE b.booking_id = ?
        """

        result = self.db.execute_query(query, (booking_id,))
        if result:
            return self._to_dict(result[0])
        return None

    def get_by_status(self, status):
        """Get bookings by status"""
        query = """
            SELECT
                b.*,

                c.first_name,
                c.last_name,

                v.make,
                v.model,
                v.license_plate

            FROM bookings b

            LEFT JOIN customers c
                ON b.customer_id = c.customer_id

            LEFT JOIN vehicles v
                ON b.vehicle_id = v.id

            WHERE b.booking_status = ?

            ORDER BY b.created_at DESC
        """

        result = self.db.execute_query(query, (status,))
        return self._to_dict_list(result)

    def search(self, term):
        """Search bookings"""
        query = """
            SELECT
                b.*,

                c.first_name,
                c.last_name,
                c.email,

                v.make,
                v.model,
                v.license_plate

            FROM bookings b

            LEFT JOIN customers c
                ON b.customer_id = c.customer_id

            LEFT JOIN vehicles v
                ON b.vehicle_id = v.id

            WHERE
                b.booking_ref LIKE ?
                OR c.first_name LIKE ?
                OR c.last_name LIKE ?
                OR c.email LIKE ?
                OR v.make LIKE ?
                OR v.model LIKE ?
                OR v.license_plate LIKE ?

            ORDER BY b.created_at DESC
        """

        pattern = f"%{term}%"

        result = self.db.execute_query(
            query,
            (
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern
            )
        )
        return self._to_dict_list(result)

    # ==========================================================
    # CUSTOMER / VEHICLE DATA
    # ==========================================================

    def get_customers(self):
        """Get customers for booking dropdown"""
        query = """
            SELECT
                customer_id,
                first_name,
                last_name,
                email
            FROM customers
            ORDER BY first_name, last_name
        """

        result = self.db.execute_query(query)
        return self._to_dict_list(result)

    def get_next_booking_number(self):
        """
        Get the next booking number based on the
        highest auto-increment booking_id.
        """

        query = """
            SELECT COALESCE(MAX(booking_id), 0) + 1 AS next_number
            FROM bookings
        """

        result = self.db.execute_query(query)

        if result:
            row = self._to_dict(result[0])
            return int(row.get('next_number', 1))

        return 1

    def get_vehicles(self):
        """Get vehicles"""
        query = """
            SELECT
                id,
                make,
                model,
                year,
                license_plate,
                daily_rate,
                status
            FROM vehicles
            ORDER BY make, model
        """

        result = self.db.execute_query(query)
        return self._to_dict_list(result)

    def get_available_vehicles(self):
        """Get vehicles which are available"""
        query = """
            SELECT
                id,
                make,
                model,
                year,
                license_plate,
                daily_rate,
                status
            FROM vehicles
            WHERE status = 'available'
            ORDER BY make, model
        """

        result = self.db.execute_query(query)
        return self._to_dict_list(result)

    # ==========================================================
    # DOUBLE BOOKING CHECK
    # ==========================================================

    def check_vehicle_availability(
        self,
        vehicle_id,
        start_date,
        end_date,
        exclude_booking_id=None
    ):
        """
        Check whether vehicle is already booked
        during requested period.
        """

        query = """
            SELECT booking_id
            FROM bookings
            WHERE vehicle_id = ?

            AND booking_status NOT IN (
                'rejected',
                'cancelled',
                'completed'
            )

            AND start_date <= ?
            AND end_date >= ?
        """

        params = [
            vehicle_id,
            end_date,
            start_date
        ]

        if exclude_booking_id is not None:
            query += " AND booking_id != ?"
            params.append(exclude_booking_id)

        result = self.db.execute_query(query, tuple(params))

        return len(result) == 0

    # ==========================================================
    # CREATE
    # ==========================================================

    def insert(self, data):
        """Insert booking"""

        query = """
            INSERT INTO bookings (
                booking_ref,
                customer_id,
                vehicle_id,
                start_date,
                end_date,
                pickup_location,
                dropoff_location,
                daily_rate,
                total_days,
                total_amount,
                deposit_amount,
                paid_amount,
                balance_amount,
                booking_status,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        return self.db.execute_query(
            query,
            (
                data['booking_ref'],
                data['customer_id'],
                data['vehicle_id'],
                data['start_date'],
                data['end_date'],
                data['pickup_location'],
                data['dropoff_location'],
                data['daily_rate'],
                data['total_days'],
                data['total_amount'],
                data['deposit_amount'],
                data['paid_amount'],
                data['balance_amount'],
                data['booking_status'],
                data['notes']
            )
        )

    # ==========================================================
    # UPDATE - FIXED
    # ==========================================================

    def update(self, booking_id, data):
        """Update booking"""
        # Make sure we have all required fields
        query = """
            UPDATE bookings
            SET
                booking_ref = ?,
                customer_id = ?,
                vehicle_id = ?,
                start_date = ?,
                end_date = ?,
                pickup_location = ?,
                dropoff_location = ?,
                daily_rate = ?,
                total_days = ?,
                total_amount = ?,
                deposit_amount = ?,
                balance_amount = ?,
                booking_status = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE booking_id = ?
        """

        return self.db.execute_query(
            query,
            (
                data['booking_ref'],
                data['customer_id'],
                data['vehicle_id'],
                data['start_date'],
                data['end_date'],
                data['pickup_location'],
                data['dropoff_location'],
                data['daily_rate'],
                data['total_days'],
                data['total_amount'],
                data['deposit_amount'],
                data['balance_amount'],
                data['booking_status'],
                data['notes'],
                booking_id
            )
        )

    # ==========================================================
    # STATUS
    # ==========================================================

    def update_status(
        self,
        booking_id,
        status,
        approved_by=None,
        rejection_reason=None
    ):
        """Update booking status"""

        if status == 'approved':

            query = """
                UPDATE bookings
                SET
                    booking_status = ?,
                    approved_by = ?,
                    approved_at = CURRENT_TIMESTAMP,
                    rejection_reason = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE booking_id = ?
            """

            return self.db.execute_query(
                query,
                (
                    status,
                    approved_by,
                    booking_id
                )
            )

        elif status == 'rejected':

            query = """
                UPDATE bookings
                SET
                    booking_status = ?,
                    rejection_reason = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE booking_id = ?
            """

            return self.db.execute_query(
                query,
                (
                    status,
                    rejection_reason,
                    booking_id
                )
            )

        else:

            query = """
                UPDATE bookings
                SET
                    booking_status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE booking_id = ?
            """

            return self.db.execute_query(
                query,
                (
                    status,
                    booking_id
                )
            )

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete(self, booking_id):
        """Delete booking"""

        query = """
            DELETE FROM bookings
            WHERE booking_id = ?
        """

        return self.db.execute_query(query, (booking_id,))

    # ==========================================================
    # COUNTS
    # ==========================================================

    def get_count_by_status(self):
        """Get booking counts"""

        query = """
            SELECT
                booking_status,
                COUNT(*) AS count
            FROM bookings
            GROUP BY booking_status
        """

        result = self.db.execute_query(query)
        return self._to_dict_list(result)

    # ==========================================================
    # PAYMENT TOTALS
    # ==========================================================

    def update_payment_totals(self, booking_id):
        """
        Recalculate paid amount and balance
        from payments table.
        """

        query = """
            SELECT
                COALESCE(
                    SUM(
                        CASE
                            WHEN payment_status = 'paid'
                            AND payment_type IN ('deposit', 'final')
                            THEN amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS paid_amount
            FROM payments
            WHERE booking_id = ?
        """

        result = self.db.execute_query(query, (booking_id,))

        paid_amount = 0

        if result:
            row = self._to_dict(result[0])
            paid_amount = float(row.get('paid_amount', 0) or 0)

        booking = self.get_by_id(booking_id)

        if not booking:
            return None

        total_amount = float(booking.get('total_amount', 0) or 0)

        balance_amount = max(
            total_amount - paid_amount,
            0
        )

        update_query = """
            UPDATE bookings
            SET
                paid_amount = ?,
                balance_amount = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE booking_id = ?
        """

        return self.db.execute_query(
            update_query,
            (
                paid_amount,
                balance_amount,
                booking_id
            )
        )