# controllers/booking_controller.py

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

# Import the model - make sure this is correct
from models.booking_model import BookingModel


class BookingController:

    def __init__(self, db):
        self.db = db
        self.model = BookingModel(db)

    # ==========================================================
    # READ
    # ==========================================================

    def get_all_bookings(self):
        return self.model.get_all()

    def get_booking_by_id(self, booking_id):
        return self.model.get_by_id(booking_id)

    def get_by_status(self, status):
        return self.model.get_by_status(status)

    def search_bookings(self, term):
        if not term:
            return self.get_all_bookings()

        return self.model.search(term)

    # ==========================================================
    # CUSTOMERS / VEHICLES
    # ==========================================================

    def get_customers(self):
        return self.model.get_customers()

    def get_vehicles(self):
        return self.model.get_vehicles()

    def get_available_vehicles(self):
        return self.model.get_available_vehicles()

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def _validate(self, data, booking_id=None):

        required = [
            'booking_ref',
            'customer_id',
            'vehicle_id',
            'start_date',
            'end_date',
            'daily_rate'
        ]

        for field in required:
            if not data.get(field):
                return None, (
                    f'{field.replace("_", " ").title()} is required'
                )

        # ------------------------------------------------------
        # Dates
        # ------------------------------------------------------

        try:
            start_date = datetime.strptime(
                data['start_date'],
                '%Y-%m-%d'
            )

            end_date = datetime.strptime(
                data['end_date'],
                '%Y-%m-%d'
            )

        except ValueError:
            return None, (
                'Dates must use YYYY-MM-DD format'
            )

        if end_date < start_date:
            return None, (
                'End date cannot be before start date'
            )

        total_days = (
            end_date - start_date
        ).days

        # Rental must be at least 1 day
        if total_days <= 0:
            return None, (
                'Rental period must be at least 1 day'
            )

        # ------------------------------------------------------
        # Daily rate
        # ------------------------------------------------------

        try:
            daily_rate = float(data['daily_rate'])

            if daily_rate < 0:
                return None, (
                    'Daily rate cannot be negative'
                )

        except ValueError:
            return None, (
                'Daily rate must be a number'
            )

        # ------------------------------------------------------
        # Total
        # ------------------------------------------------------

        total_amount = total_days * daily_rate

        # ------------------------------------------------------
        # Deposit
        # ------------------------------------------------------

        try:
            deposit_amount = float(
                data.get('deposit_amount', 0) or 0
            )

            if deposit_amount < 0:
                return None, (
                    'Deposit cannot be negative'
                )

        except ValueError:
            return None, (
                'Deposit must be a number'
            )

        if deposit_amount > total_amount:
            return None, (
                'Deposit cannot be greater than total amount'
            )

        # ------------------------------------------------------
        # Status - Updated to include all valid statuses
        # ------------------------------------------------------

        valid_statuses = [
            'pending',
            'approved',
            'rejected',
            'confirmed',
            'active',
            'completed',
            'cancelled'
        ]

        status = data.get(
            'booking_status',
            'pending'
        )

        if status not in valid_statuses:
            return None, (
                'Invalid booking status'
            )

        # ------------------------------------------------------
        # Booking reference
        # ------------------------------------------------------

        booking_ref = (
            data['booking_ref']
            .strip()
            .upper()
        )

        if not booking_ref:
            return None, (
                'Booking reference is required'
            )

        # ------------------------------------------------------
        # Availability - Skip availability check for updates
        # ------------------------------------------------------

        # Skip availability check if this is an update (booking_id provided)
        # and the status is not 'pending' (already approved/rejected)
        skip_availability = False
        if booking_id:
            existing = self.get_booking_by_id(booking_id)
            if existing and existing.get('booking_status') != 'pending':
                skip_availability = True

        if not skip_availability:
            available = self.model.check_vehicle_availability(
                data['vehicle_id'],
                data['start_date'],
                data['end_date'],
                booking_id
            )

            if not available:
                return None, (
                    'Vehicle is already booked during '
                    'the selected dates.'
                )

        # ------------------------------------------------------
        # Clean data
        # ------------------------------------------------------

        return {
            'booking_ref': booking_ref,
            'customer_id': int(data['customer_id']),
            'vehicle_id': int(data['vehicle_id']),
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'pickup_location': data.get(
                'pickup_location',
                ''
            ).strip(),
            'dropoff_location': data.get(
                'dropoff_location',
                ''
            ).strip(),
            'daily_rate': daily_rate,
            'total_days': total_days,
            'total_amount': total_amount,
            'deposit_amount': deposit_amount,
            'paid_amount': 0,
            'balance_amount': total_amount,
            'booking_status': status,
            'notes': data.get(
                'notes',
                ''
            ).strip()
        }, None

    # ==========================================================
    # CREATE
    # ==========================================================

    def add_booking(self, data):

        clean, error = self._validate(data)

        if error:
            return {
                'success': False,
                'message': error
            }

        result = self.model.insert(clean)

        if result is None:
            return {
                'success': False,
                'message': (
                    'Failed to create booking. '
                    'Booking reference may already exist.'
                )
            }

        return {
            'success': True,
            'message': 'Booking created successfully',
            'id': result
        }

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update_booking(self, booking_id, data):
        

        clean, error = self._validate(
            data,
            booking_id
        )

        if error:
            return {
                'success': False,
                'message': error
            }

        result = self.model.update(
            booking_id,
            clean
        )

        if result is None:
            return {
                'success': False,
                'message': 'Failed to update booking'
            }

        return {
            'success': True,
            'message': 'Booking updated successfully'
        }

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete_booking(self, booking_id):

        result = self.model.delete(
            booking_id
        )

        if result is None:
            return {
                'success': False,
                'message': 'Failed to delete booking'
            }

        return {
            'success': True,
            'message': 'Booking deleted successfully'
        }

    # ==========================================================
    # APPROVE
    # ==========================================================

    def approve_booking(self, booking_id, user_id):
        """Approve a booking"""
        booking = self.get_booking_by_id(booking_id)
        
        if not booking:
            return {
                'success': False,
                'message': 'Booking not found'
            }
        
        if booking['booking_status'] != 'pending':
            return {
                'success': False,
                'message': f'Only pending bookings can be approved. Current status: {booking["booking_status"]}'
            }
        
        result = self.model.update_status(
            booking_id,
            'approved',
            approved_by=user_id
        )
        
        if result is None:
            return {
                'success': False,
                'message': 'Failed to approve booking'
            }
        
        return {
            'success': True,
            'message': 'Booking approved successfully'
        }

    # ==========================================================
    # REJECT
    # ==========================================================

    def reject_booking(self, booking_id, reason):
        """Reject a booking"""
        booking = self.get_booking_by_id(booking_id)
        
        if not booking:
            return {
                'success': False,
                'message': 'Booking not found'
            }
        
        if booking['booking_status'] != 'pending':
            return {
                'success': False,
                'message': f'Only pending bookings can be rejected. Current status: {booking["booking_status"]}'
            }
        
        if not reason.strip():
            return {
                'success': False,
                'message': 'Please enter a rejection reason'
            }
        
        result = self.model.update_status(
            booking_id,
            'rejected',
            rejection_reason=reason.strip()
        )
        
        if result is None:
            return {
                'success': False,
                'message': 'Failed to reject booking'
            }
        
        return {
            'success': True,
            'message': 'Booking rejected successfully'
        }

    # ==========================================================
    # STATUS
    # ==========================================================

    def update_status(self, booking_id, status):
        """Update booking status"""
        valid_statuses = [
            'pending',
            'approved',
            'rejected',
            'confirmed',
            'active',
            'completed',
            'cancelled'
        ]

        if status not in valid_statuses:
            return {
                'success': False,
                'message': 'Invalid status'
            }

        result = self.model.update_status(
            booking_id,
            status
        )

        if result is None:
            return {
                'success': False,
                'message': 'Failed to update status'
            }

        return {
            'success': True,
            'message': f'Booking status updated to {status}'
        }

    # ==========================================================
    # COUNTS
    # ==========================================================

    def get_status_counts(self):

        results = self.model.get_count_by_status()

        counts = {
            'pending': 0,
            'approved': 0,
            'rejected': 0,
            'confirmed': 0,
            'active': 0,
            'completed': 0,
            'cancelled': 0
        }

        for row in results:
            counts[row['booking_status']] = row['count']

        return counts

    # ==========================================================
    # EXPORT CSV
    # ==========================================================

    def export_to_csv(self, bookings):

        filename = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[
                ('CSV files', '*.csv')
            ],
            initialfile=(
                f'bookings_'
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
                    'Vehicle',
                    'Start Date',
                    'End Date',
                    'Days',
                    'Daily Rate',
                    'Total',
                    'Deposit',
                    'Paid',
                    'Balance',
                    'Status',
                    'Created At'
                ])

                for row in bookings:

                    customer = (
                        f"{row['first_name']} "
                        f"{row['last_name']}"
                    )

                    vehicle = (
                        f"{row['make']} "
                        f"{row['model']} "
                        f"({row['license_plate']})"
                    )

                    writer.writerow([
                        row['booking_id'],
                        row['booking_ref'],
                        customer,
                        vehicle,
                        row['start_date'],
                        row['end_date'],
                        row['total_days'],
                        f"${row['daily_rate']:.2f}",
                        f"${row['total_amount']:.2f}",
                        f"${row['deposit_amount']:.2f}",
                        f"${row['paid_amount']:.2f}",
                        f"${row['balance_amount']:.2f}",
                        row['booking_status'].title(),
                        row['created_at']
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

    def export_to_excel(self, bookings):

        filename = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[
                ('Excel files', '*.xlsx')
            ],
            initialfile=(
                f'bookings_'
                f'{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                f'.xlsx'
            )
        )

        if not filename:
            return

        try:

            data = []

            for row in bookings:

                customer = (
                    f"{row['first_name']} "
                    f"{row['last_name']}"
                )

                vehicle = (
                    f"{row['make']} "
                    f"{row['model']} "
                    f"({row['license_plate']})"
                )

                data.append({
                    'ID': row['booking_id'],
                    'Booking Ref': row['booking_ref'],
                    'Customer': customer,
                    'Vehicle': vehicle,
                    'Start Date': row['start_date'],
                    'End Date': row['end_date'],
                    'Days': row['total_days'],
                    'Daily Rate': row['daily_rate'],
                    'Total': row['total_amount'],
                    'Deposit': row['deposit_amount'],
                    'Paid': row['paid_amount'],
                    'Balance': row['balance_amount'],
                    'Status': row['booking_status'].title(),
                    'Created At': row['created_at']
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

    def export_to_pdf(self, bookings):

        filename = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[
                ('PDF files', '*.pdf')
            ],
            initialfile=(
                f'bookings_'
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
                    'Bookings Report',
                    title_style
                ),
                Spacer(1, 20)
            ]

            table_data = [[
                'ID',
                'Ref',
                'Customer',
                'Vehicle',
                'Start',
                'End',
                'Days',
                'Total',
                'Paid',
                'Balance',
                'Status'
            ]]

            for row in bookings:

                customer = (
                    f"{row['first_name']} "
                    f"{row['last_name']}"
                )

                vehicle = (
                    f"{row['make']} "
                    f"{row['model']}"
                )

                table_data.append([
                    str(row['booking_id']),
                    row['booking_ref'],
                    customer,
                    vehicle,
                    row['start_date'],
                    row['end_date'],
                    str(row['total_days']),
                    f"${row['total_amount']:.2f}",
                    f"${row['paid_amount']:.2f}",
                    f"${row['balance_amount']:.2f}",
                    row['booking_status'].title()
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

    # ==========================================================
    # BOOKING REFERENCE GENERATOR
    # ==========================================================

    def get_next_booking_ref(self):
        """
        Generate booking reference.
        Format: BR-001-YYYYMMDD
        """
        next_number = self.model.get_next_booking_number()
        date_part = datetime.now().strftime('%Y%m%d')
        return f"BR-{next_number:03d}-{date_part}"