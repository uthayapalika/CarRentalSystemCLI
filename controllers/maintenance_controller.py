# controllers/maintenance_controller.py
import csv
from datetime import datetime
import pandas as pd
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from models.maintenance_model import MaintenanceModel


class MaintenanceController:
    def __init__(self, db):
        self.db = db
        self.model = MaintenanceModel(db)

    # ---------- READ ----------

    def get_all(self):
        return self.model.get_all()

    def get_by_vehicle(self, vehicle_id):
        return self.model.get_by_vehicle(vehicle_id)

    def get_by_status(self, status):
        return self.model.get_by_status(status)

    def get_upcoming(self, days=30):
        return self.model.get_upcoming(days)

    # ---------- VALIDATION ----------

    def _validate(self, data):
        if not data.get('vehicle_id'):
            return None, 'Vehicle is required'
        
        if not data.get('maintenance_type'):
            return None, 'Maintenance type is required'
        
        if not data.get('service_date'):
            return None, 'Service date is required'

        try:
            cost = float(data.get('cost', 0))
            if cost < 0:
                return None, 'Cost cannot be negative'
        except ValueError:
            return None, 'Cost must be a number'

        return {
            'vehicle_id': int(data['vehicle_id']),
            'maintenance_type': data['maintenance_type'],
            'service_date': data['service_date'],
            'odometer_reading': data.get('odometer_reading', 0),
            'cost': cost,
            'service_provider': data.get('service_provider', ''),
            'description': data.get('description', ''),
            'status': data.get('status', 'pending'),
            'next_service_due': data.get('next_service_due')
        }, None

    # ---------- CREATE ----------

    def add(self, data):
        clean, error = self._validate(data)
        if error:
            return {'success': False, 'message': error}

        result = self.model.insert(clean)
        if result is None:
            return {'success': False, 'message': 'Failed to add maintenance record'}
        return {'success': True, 'message': 'Maintenance record added successfully'}

    # ---------- UPDATE ----------

    def update(self, maintenance_id, data):
        clean, error = self._validate(data)
        if error:
            return {'success': False, 'message': error}

        result = self.model.update(maintenance_id, clean)
        if result is None:
            return {'success': False, 'message': 'Failed to update maintenance record'}
        return {'success': True, 'message': 'Maintenance record updated successfully'}

    # ---------- DELETE ----------

    def delete(self, maintenance_id):
        result = self.model.delete(maintenance_id)
        if result is None:
            return {'success': False, 'message': 'Failed to delete maintenance record'}
        return {'success': True, 'message': 'Maintenance record deleted successfully'}

    # ---------- STATUS ----------

    def update_status(self, maintenance_id, status):
        result = self.model.update_status(maintenance_id, status)
        if result is None:
            return {'success': False, 'message': 'Failed to update status'}
        return {'success': True, 'message': f'Status updated to {status}'}

    # ---------- STATISTICS ----------

    def get_statistics(self):
        return self.model.get_statistics()

    # ---------- EXPORT ----------

    def export_to_csv(self, records):
        filename = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile=f'maintenance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'ID', 'Vehicle', 'Type', 'Date', 'Odometer', 
                    'Cost', 'Provider', 'Status', 'Next Service Due'
                ])
                for row in records:
                    vehicle_name = f"{row['make']} {row['model']} ({row['license_plate']})" if 'make' in row.keys() else ''
                    writer.writerow([
                        row['maintenance_id'],
                        vehicle_name,
                        row['maintenance_type'],
                        row['service_date'],
                        row['odometer_reading'] if row['odometer_reading'] else 0,
                        f"${row['cost']:.2f}",
                        row['service_provider'] or '',
                        row['status'],
                        row['next_service_due'] or ''
                    ])
            messagebox.showinfo('Success', f'Exported to CSV:\n{filename}')
        except Exception as e:
            messagebox.showerror('Error', f'CSV export failed: {e}')

    def export_to_excel(self, records):
        filename = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Excel files', '*.xlsx')],
            initialfile=f'maintenance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        if not filename:
            return

        try:
            data = []
            for row in records:
                vehicle_name = f"{row['make']} {row['model']} ({row['license_plate']})" if 'make' in row.keys() else ''
                data.append({
                    'ID': row['maintenance_id'],
                    'Vehicle': vehicle_name,
                    'Type': row['maintenance_type'],
                    'Date': row['service_date'],
                    'Odometer': row['odometer_reading'] if row['odometer_reading'] else 0,
                    'Cost': f"${row['cost']:.2f}",
                    'Provider': row['service_provider'] or '',
                    'Status': row['status'],
                    'Next Service Due': row['next_service_due'] or ''
                })
            pd.DataFrame(data).to_excel(filename, index=False, engine='openpyxl')
            messagebox.showinfo('Success', f'Exported to Excel:\n{filename}')
        except Exception as e:
            messagebox.showerror('Error', f'Excel export failed: {e}')

    def export_to_pdf(self, records):
        filename = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[('PDF files', '*.pdf')],
            initialfile=f'maintenance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        if not filename:
            return

        try:
            doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('Title', parent=styles['Title'], alignment=TA_CENTER)

            elements = [
                Paragraph("Maintenance Report", title_style),
                Spacer(1, 20)
            ]

            table_data = [['ID', 'Vehicle', 'Type', 'Date', 'Cost', 'Status', 'Next Service']]
            for row in records:
                vehicle_name = f"{row['make']} {row['model']}" if 'make' in row.keys() else ''
                table_data.append([
                    str(row['maintenance_id']),
                    vehicle_name[:20],
                    row['maintenance_type'][:15],
                    row['service_date'],
                    f"${row['cost']:.2f}",
                    row['status'],
                    row['next_service_due'] or ''
                ])

            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            elements.append(table)
            doc.build(elements)
            messagebox.showinfo('Success', f'Exported to PDF:\n{filename}')
        except Exception as e:
            messagebox.showerror('Error', f'PDF export failed: {e}')