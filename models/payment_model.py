class PaymentModel:

    def __init__(self, db):
        self.db = db

   
    # READ
    

    def get_all(self):

        query = """
            SELECT
                p.payment_id,
                p.booking_id,
                p.payment_type,
                p.amount,
                p.payment_method,
                p.payment_status,
                p.transaction_reference,
                p.payment_date,
                p.notes,
                p.created_at,
                p.updated_at,

                b.booking_ref,

                c.first_name,
                c.last_name

            FROM payments p

            LEFT JOIN bookings b
                ON p.booking_id = b.booking_id

            LEFT JOIN customers c
                ON b.customer_id = c.customer_id

            ORDER BY p.created_at DESC
        """

        return self.db.execute_query(query)

    def get_by_id(self, payment_id):

        query = """
            SELECT
                p.*,
                b.booking_ref,
                c.first_name,
                c.last_name

            FROM payments p

            LEFT JOIN bookings b
                ON p.booking_id = b.booking_id

            LEFT JOIN customers c
                ON b.customer_id = c.customer_id

            WHERE p.payment_id = ?
        """

        result = self.db.execute_query(
            query,
            (payment_id,)
        )

        return result[0] if result else None

    def get_by_booking(self, booking_id):

        query = """
            SELECT
                p.*,
                b.booking_ref

            FROM payments p

            LEFT JOIN bookings b
                ON p.booking_id = b.booking_id

            WHERE p.booking_id = ?

            ORDER BY p.payment_date DESC
        """

        return self.db.execute_query(
            query,
            (booking_id,)
        )

    def search(self, term):

        query = """
            SELECT
                p.*,
                b.booking_ref,
                c.first_name,
                c.last_name

            FROM payments p

            LEFT JOIN bookings b
                ON p.booking_id = b.booking_id

            LEFT JOIN customers c
                ON b.customer_id = c.customer_id

            WHERE
                b.booking_ref LIKE ?
                OR c.first_name LIKE ?
                OR c.last_name LIKE ?
                OR p.transaction_reference LIKE ?

            ORDER BY p.created_at DESC
        """

        pattern = f"%{term}%"

        return self.db.execute_query(
            query,
            (
                pattern,
                pattern,
                pattern,
                pattern
            )
        )

  
    # BOOKINGS
    

    def get_bookings(self):

        query = """
            SELECT
                b.booking_id,
                b.booking_ref,
                b.total_amount,
                b.paid_amount,
                b.balance_amount,
                b.booking_status,

                c.first_name,
                c.last_name

            FROM bookings b

            LEFT JOIN customers c
                ON b.customer_id = c.customer_id

            WHERE b.booking_status NOT IN (
                'rejected',
                'cancelled'
            )

            ORDER BY b.created_at DESC
        """

        return self.db.execute_query(query)

    
    # CREATE
   

    def insert(self, data):

        query = """
            INSERT INTO payments (
                booking_id,
                payment_type,
                amount,
                payment_method,
                payment_status,
                transaction_reference,
                payment_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        return self.db.execute_query(
            query,
            (
                data['booking_id'],
                data['payment_type'],
                data['amount'],
                data['payment_method'],
                data['payment_status'],
                data['transaction_reference'],
                data['payment_date'],
                data['notes']
            )
        )

   
    # UPDATE
    

    def update(self, payment_id, data):

        query = """
            UPDATE payments
            SET
                booking_id = ?,
                payment_type = ?,
                amount = ?,
                payment_method = ?,
                payment_status = ?,
                transaction_reference = ?,
                payment_date = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE payment_id = ?
        """

        return self.db.execute_query(
            query,
            (
                data['booking_id'],
                data['payment_type'],
                data['amount'],
                data['payment_method'],
                data['payment_status'],
                data['transaction_reference'],
                data['payment_date'],
                data['notes'],
                payment_id
            )
        )

   
    # DELETE
    

    def delete(self, payment_id):

        query = """
            DELETE FROM payments
            WHERE payment_id = ?
        """

        return self.db.execute_query(
            query,
            (payment_id,)
        )