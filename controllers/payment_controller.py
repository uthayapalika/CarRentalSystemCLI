import csv
import pandas as pd

from datetime import datetime
from tkinter import filedialog, messagebox

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.enums import TA_CENTER
from factories import ModelFactory
#from models.payment_model import PaymentModel


class PaymentController:

    def __init__(self, db):
        self.db = db
        self.model = ModelFactory.create_model('payment', db)

    # ==========================================================
    # READ
    # ==========================================================

    def get_all_payments(self):
        return self.model.get_all()

    def get_payment_by_id(self, payment_id):
        return self.model.get_by_id(payment_id)

    def get_by_booking(self, booking_id):
        return self.model.get_by_booking(booking_id)

    def search_payments(self, term):

        if not term:
            return self.get_all_payments()

        return self.model.search(term)

    # ==========================================================
    # BOOKINGS
    # ==========================================================

    def get_bookings(self):
        return self.model.get_bookings()

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def _validate(self, data):

        required = [
            'booking_id',
            'payment_type',
            'amount',
            'payment_method'
        ]

        for field in required:

            if not data.get(field):

                return None, (
                    f'{field.replace("_", " ").title()} '
                    f'is required'
                )

        # ------------------------------------------------------
        # Payment type
        # ------------------------------------------------------

        valid_types = [
            'deposit',
            'final',
            'refund'
        ]

        payment_type = data[
            'payment_type'
        ]

        if payment_type not in valid_types:

            return None, (
                'Invalid payment type'
            )

        # ------------------------------------------------------
        # Payment method
        # ------------------------------------------------------

        valid_methods = [
            'cash',
            'card',
            'bank_transfer',
            'online'
        ]

        payment_method = data[
            'payment_method'
        ]

        if payment_method not in valid_methods:

            return None, (
                'Invalid payment method'
            )

        # ------------------------------------------------------
        # Payment status
        # ------------------------------------------------------

        valid_statuses = [
            'pending',
            'paid',
            'failed',
            'refunded'
        ]

        payment_status = data.get(
            'payment_status',
            'paid'
        )

        if payment_status not in valid_statuses:

            return None, (
                'Invalid payment status'
            )

        # ------------------------------------------------------
        # Amount
        # ------------------------------------------------------

        try:

            amount = float(
                data['amount']
            )

            if amount <= 0:

                return None, (
                    'Payment amount must be greater than 0'
                )

        except ValueError:

            return None, (
                'Payment amount must be a number'
            )

        # ------------------------------------------------------
        # Booking
        # ------------------------------------------------------

        booking_id = int(
            data['booking_id']
        )

        # ------------------------------------------------------
        # Payment date
        # ------------------------------------------------------

        payment_date = data.get(
            'payment_date'
        )

        if not payment_date:

            payment_date = datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S'
            )

        # ------------------------------------------------------
        # Clean
        # ------------------------------------------------------

        return {
            'booking_id': booking_id,
            'payment_type': payment_type,
            'amount': amount,
            'payment_method': payment_method,
            'payment_status': payment_status,
            'transaction_reference': (
                data.get(
                    'transaction_reference',
                    ''
                ).strip()
                or None
            ),
            'payment_date': payment_date,
            'notes': data.get(
                'notes',
                ''
            ).strip()
        }, None

    # ==========================================================
    # CREATE
    # ==========================================================

    def add_payment(self, data):

        clean, error = self._validate(
            data
        )

        if error:

            return {
                'success': False,
                'message': error
            }

        result = self.model.insert(
            clean
        )

        if result is None:

            return {
                'success': False,
                'message': (
                    'Failed to add payment. '
                    'Transaction reference may already exist.'
                )
            }

        # Recalculate booking totals
        self.update_booking_totals(
            clean['booking_id']
        )

        return {
            'success': True,
            'message': 'Payment added successfully',
            'id': result
        }

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update_payment(
        self,
        payment_id,
        data
    ):

        old_payment = self.get_payment_by_id(
            payment_id
        )

        if not old_payment:

            return {
                'success': False,
                'message': 'Payment not found'
            }

        clean, error = self._validate(
            data
        )

        if error:

            return {
                'success': False,
                'message': error
            }

        result = self.model.update(
            payment_id,
            clean
        )

        if result is None:

            return {
                'success': False,
                'message': 'Failed to update payment'
            }

        # Update old booking
        self.update_booking_totals(
            old_payment['booking_id']
        )

        # Update new booking
        self.update_booking_totals(
            clean['booking_id']
        )

        return {
            'success': True,
            'message': 'Payment updated successfully'
        }

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete_payment(
        self,
        payment_id
    ):

        payment = self.get_payment_by_id(
            payment_id
        )

        if not payment:

            return {
                'success': False,
                'message': 'Payment not found'
            }

        result = self.model.delete(
            payment_id
        )

        if result is None:

            return {
                'success': False,
                'message': 'Failed to delete payment'
            }

        self.update_booking_totals(
            payment['booking_id']
        )

        return {
            'success': True,
            'message': 'Payment deleted successfully'
        }

    # ==========================================================
    # BOOKING TOTALS
    # ==========================================================

    def update_booking_totals(
        self,
        booking_id
    ):

        query = """
            SELECT
                COALESCE(
                    SUM(
                        CASE
                            WHEN payment_status = 'paid'
                            AND payment_type IN (
                                'deposit',
                                'final'
                            )
                            THEN amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS paid_amount
            FROM payments
            WHERE booking_id = ?
        """

        result = self.db.execute_query(
            query,
            (booking_id,)
        )

        paid_amount = 0

        if result:

            paid_amount = float(
                result[0]['paid_amount'] or 0
            )

        booking_query = """
            SELECT total_amount
            FROM bookings
            WHERE booking_id = ?
        """

        booking = self.db.execute_query(
            booking_query,
            (booking_id,)
        )

        if not booking:

            return False

        total_amount = float(
            booking[0]['total_amount'] or 0
        )

        balance = max(
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

        self.db.execute_query(
            update_query,
            (
                paid_amount,
                balance,
                booking_id
            )
        )

        return True

    # ==========================================================
    # EXPORT CSV
    # ==========================================================

    def export_to_csv(
        self,
        payments
    ):

        filename = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[
                ('CSV files', '*.csv')
            ],
            initialfile=(
                f'payments_'
                f'{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                f'.csv'
            )
        )

        if not filename:
            return

        try:

            with open(
                filename,
                'w',
                newline='',
                encoding='utf-8-sig'
            ) as f:

                writer = csv.writer(f)

                writer.writerow([
                    'ID',
                    'Booking Ref',
                    'Customer',
                    'Payment Type',
                    'Amount',
                    'Payment Method',
                    'Status',
                    'Transaction Reference',
                    'Payment Date'
                ])

                for row in payments:

                    customer = (
                        f"{row['first_name']} "
                        f"{row['last_name']}"
                    )

                    writer.writerow([
                        row['payment_id'],
                        row['booking_ref'],
                        customer,
                        row['payment_type'].title(),
                        f"${row['amount']:.2f}",
                        row['payment_method'].replace(
                            '_',
                            ' '
                        ).title(),
                        row['payment_status'].title(),
                        row['transaction_reference'] or '',
                        row['payment_date'] or ''
                    ])

            messagebox.showinfo(
                'Success',
                f'Exported to CSV:\n{filename}'
            )

        except Exception as e:

            messagebox.showerror(
                'Error',
                f'CSV export failed: {e}'
            )

    # ==========================================================
    # EXPORT EXCEL
    # ==========================================================

    def export_to_excel(
        self,
        payments
    ):

        filename = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[
                ('Excel files', '*.xlsx')
            ],
            initialfile=(
                f'payments_'
                f'{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                f'.xlsx'
            )
        )

        if not filename:
            return

        try:

            data = []

            for row in payments:

                customer = (
                    f"{row['first_name']} "
                    f"{row['last_name']}"
                )

                data.append({
                    'ID': row['payment_id'],
                    'Booking Ref': row['booking_ref'],
                    'Customer': customer,
                    'Payment Type': (
                        row['payment_type'].title()
                    ),
                    'Amount': row['amount'],
                    'Payment Method': (
                        row['payment_method']
                        .replace('_', ' ')
                        .title()
                    ),
                    'Status': (
                        row['payment_status'].title()
                    ),
                    'Transaction Reference': (
                        row['transaction_reference'] or ''
                    ),
                    'Payment Date': (
                        row['payment_date'] or ''
                    )
                })

            pd.DataFrame(data).to_excel(
                filename,
                index=False,
                engine='openpyxl'
            )

            messagebox.showinfo(
                'Success',
                f'Exported to Excel:\n{filename}'
            )

        except Exception as e:

            messagebox.showerror(
                'Error',
                f'Excel export failed: {e}'
            )

    # ==========================================================
    # EXPORT PDF
    # ==========================================================

    def export_to_pdf(
        self,
        payments
    ):

        filename = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[
                ('PDF files', '*.pdf')
            ],
            initialfile=(
                f'payments_'
                f'{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                f'.pdf'
            )
        )

        if not filename:
            return

        try:

            doc = SimpleDocTemplate(
                filename,
                pagesize=landscape(letter)
            )

            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'Title',
                parent=styles['Title'],
                alignment=TA_CENTER
            )

            elements = [
                Paragraph(
                    'Payments Report',
                    title_style
                ),
                Spacer(1, 20)
            ]

            table_data = [[
                'ID',
                'Booking',
                'Customer',
                'Type',
                'Amount',
                'Method',
                'Status',
                'Date'
            ]]

            for row in payments:

                customer = (
                    f"{row['first_name']} "
                    f"{row['last_name']}"
                )

                table_data.append([
                    str(row['payment_id']),
                    row['booking_ref'],
                    customer,
                    row['payment_type'].title(),
                    f"${row['amount']:.2f}",
                    row['payment_method'].replace(
                        '_',
                        ' '
                    ).title(),
                    row['payment_status'].title(),
                    row['payment_date'] or ''
                ])

            table = Table(
                table_data,
                repeatRows=1
            )

            table.setStyle(
                TableStyle([
                    (
                        'BACKGROUND',
                        (0, 0),
                        (-1, 0),
                        colors.HexColor('#3498db')
                    ),
                    (
                        'TEXTCOLOR',
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        'FONTNAME',
                        (0, 0),
                        (-1, 0),
                        'Helvetica-Bold'
                    ),
                    (
                        'GRID',
                        (0, 0),
                        (-1, -1),
                        1,
                        colors.grey
                    ),
                    (
                        'ALIGN',
                        (0, 0),
                        (-1, -1),
                        'CENTER'
                    )
                ])
            )

            elements.append(table)

            doc.build(elements)

            messagebox.showinfo(
                'Success',
                f'Exported to PDF:\n{filename}'
            )

        except Exception as e:

            messagebox.showerror(
                'Error',
                f'PDF export failed: {e}'
            )