# controllers/vehicle_controller.py
import csv
import sqlite3
from datetime import datetime
import pandas as pd
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from factories import ModelFactory
#from models.vehicle_model import VehicleModel


class VehicleController:
    def __init__(self, db):
        self.db = db
        self.model = ModelFactory.create_model("vehicle", db=self.db)

    # ---------- READ ----------

    def get_all_vehicles(self):
        return self.model.get_all()

    def get_vehicle_by_id(self, vehicle_id):
        return self.model.get_by_id(vehicle_id)

    def get_available_vehicles(self):
        return self.model.get_available_vehicles()

    def get_by_status(self, status):
        return self.model.get_by_status(status)

    def get_by_category(self, category_id):
        return self.model.get_by_category(category_id)

    def search_vehicles(self, term):
        if not term:
            return self.get_all_vehicles()
        return self.model.search(term)

    # ---------- VALIDATION HELPER ----------

    def _validate(self, data):
        """Validate vehicle data"""
        # Required fields
        required = ['category_id', 'make', 'model', 'year', 'license_plate', 'daily_rate']
        for field in required:
            if not data.get(field):
                return None, f'{field.replace("_", " ").title()} is required'

        # Validate year
        try:
            year = int(data['year'])
            current_year = datetime.now().year
            if year < 1900 or year > current_year + 1:
                return None, f'Year must be between 1900 and {current_year + 1}'
        except ValueError:
            return None, 'Year must be a number'

        # Validate daily rate
        try:
            daily_rate = float(data['daily_rate'])
            if daily_rate < 0:
                return None, 'Daily rate cannot be negative'
        except ValueError:
            return None, 'Daily rate must be a number'

        # Validate mileage
        try:
            mileage = int(data.get('mileage', 0))
            if mileage < 0:
                return None, 'Mileage cannot be negative'
        except ValueError:
            return None, 'Mileage must be a number'

        # Validate rental periods
        try:
            min_period = int(data.get('min_rent_period', 1))
            max_period = int(data.get('max_rent_period', 30))
            if min_period < 0:
                return None, 'Minimum rental period cannot be negative'
            if max_period < 0:
                return None, 'Maximum rental period cannot be negative'
            if min_period > max_period:
                return None, 'Minimum rental period cannot exceed maximum'
        except ValueError:
            return None, 'Rental periods must be numbers'

        # Status validation
        valid_statuses = ['available', 'rented', 'maintenance', 'reserved']
        status = data.get('status', 'available')
        if status not in valid_statuses:
            return None, f'Invalid status. Must be one of: {", ".join(valid_statuses)}'

        # Fuel type validation
        valid_fuels = ['Petrol', 'Diesel', 'Electric', 'Hybrid']
        fuel_type = data.get('fuel_type', 'Petrol')
        if fuel_type not in valid_fuels:
            return None, f'Invalid fuel type. Must be one of: {", ".join(valid_fuels)}'

        # Clean data
        return {
            'category_id': int(data['category_id']),
            'make': data['make'].strip(),
            'model': data['model'].strip(),
            'year': year,
            'license_plate': data['license_plate'].strip().upper(),
            'color': data.get('color', '').strip(),
            'mileage': mileage,
            'daily_rate': daily_rate,
            'status': status,
            'fuel_type': fuel_type,
            'min_rent_period': min_period,
            'max_rent_period': max_period
        }, None

    # ---------- CREATE ----------

    def add_vehicle(self, data):
        clean, error = self._validate(data)
        if error:
            return {'success': False, 'message': error}

        result = self.model.insert(clean)
        if result is None:
            return {'success': False, 'message': 'Failed to add vehicle. License plate may already exist.'}
        return {'success': True, 'message': 'Vehicle added successfully', 'id': result}

    # ---------- UPDATE ----------

    def update_vehicle(self, vehicle_id, data):
        clean, error = self._validate(data)
        if error:
            return {'success': False, 'message': error}

        result = self.model.update(vehicle_id, clean)
        if result is None:
            return {'success': False, 'message': 'Failed to update vehicle'}
        return {'success': True, 'message': 'Vehicle updated successfully'}

    # ---------- DELETE ----------

    def delete_vehicle(self, vehicle_id):
        result = self.model.delete(vehicle_id)
        if result is None:
            return {'success': False, 'message': 'Failed to delete vehicle'}
        return {'success': True, 'message': 'Vehicle deleted successfully'}

    # ---------- STATUS ----------

    def update_status(self, vehicle_id, new_status):
        result = self.model.update_status(vehicle_id, new_status)
        if result is None:
            return {'success': False, 'message': 'Failed to update status'}
        return {'success': True, 'message': f'Vehicle status updated to {new_status}'}

    # ---------- MILEAGE ----------

    def update_mileage(self, vehicle_id, new_mileage):
        try:
            new_mileage = int(new_mileage)
            if new_mileage < 0:
                return {'success': False, 'message': 'Mileage cannot be negative'}
        except ValueError:
            return {'success': False, 'message': 'Mileage must be a number'}

        result = self.model.update_mileage(vehicle_id, new_mileage)
        if result is None:
            return {'success': False, 'message': 'Failed to update mileage'}
        return {'success': True, 'message': 'Mileage updated successfully'}

    # ---------- GET STATUS COUNTS ----------

    def get_status_counts(self):
        results = self.model.get_count_by_status()
        counts = {'available': 0, 'rented': 0, 'maintenance': 0, 'reserved': 0}
        for row in results:
            counts[row['status']] = row['count']
        return counts

    # ---------- EXPORT: CSV ----------

    def export_to_csv(self, vehicles):
        filename = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile=f'vehicles_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'ID', 'Category', 'Make', 'Model', 'Year', 'License Plate',
                    'Color', 'Mileage', 'Daily Rate', 'Status', 'Fuel Type',
                    'Min Period', 'Max Period', 'Created At'
                ])
                for row in vehicles:
                    category_name = row['category_name'] if 'category_name' in row.keys() and row['category_name'] else ''
                    color = row['color'] if row['color'] else ''
                    mileage = row['mileage'] if row['mileage'] else 0
                    fuel_type = row['fuel_type'] if row['fuel_type'] else ''
                    min_period = row['min_rent_period'] if 'min_rent_period' in row.keys() else 1
                    max_period = row['max_rent_period'] if 'max_rent_period' in row.keys() else 30
                    
                    writer.writerow([
                        row['id'],
                        category_name,
                        row['make'],
                        row['model'],
                        row['year'],
                        row['license_plate'],
                        color,
                        mileage,
                        f"${row['daily_rate']:.2f}",
                        row['status'].title(),
                        fuel_type,
                        min_period,
                        max_period,
                        row['created_at'] if row['created_at'] else ''
                    ])
            messagebox.showinfo('Success', f'Exported to CSV:\n{filename}')
        except Exception as e:
            messagebox.showerror('Error', f'CSV export failed: {e}')

    # ---------- EXPORT: EXCEL ----------

    def export_to_excel(self, vehicles):
        filename = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Excel files', '*.xlsx')],
            initialfile=f'vehicles_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        if not filename:
            return

        try:
            data = []
            for row in vehicles:
                category_name = row['category_name'] if 'category_name' in row.keys() and row['category_name'] else ''
                color = row['color'] if row['color'] else ''
                mileage = row['mileage'] if row['mileage'] else 0
                fuel_type = row['fuel_type'] if row['fuel_type'] else ''
                min_period = row['min_rent_period'] if 'min_rent_period' in row.keys() else 1
                max_period = row['max_rent_period'] if 'max_rent_period' in row.keys() else 30
                
                data.append({
                    'ID': row['id'],
                    'Category': category_name,
                    'Make': row['make'],
                    'Model': row['model'],
                    'Year': row['year'],
                    'License Plate': row['license_plate'],
                    'Color': color,
                    'Mileage': mileage,
                    'Daily Rate': f"${row['daily_rate']:.2f}",
                    'Status': row['status'].title(),
                    'Fuel Type': fuel_type,
                    'Min Period': min_period,
                    'Max Period': max_period,
                    'Created At': row['created_at'] if row['created_at'] else ''
                })
            pd.DataFrame(data).to_excel(filename, index=False, engine='openpyxl')
            messagebox.showinfo('Success', f'Exported to Excel:\n{filename}')
        except Exception as e:
            messagebox.showerror('Error', f'Excel export failed: {e}')

    # ---------- EXPORT: PDF ----------

    def export_to_pdf(self, vehicles):
        filename = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[('PDF files', '*.pdf')],
            initialfile=f'vehicles_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        if not filename:
            return

        try:
            doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('Title', parent=styles['Title'], alignment=TA_CENTER)

            elements = [
                Paragraph("Vehicles Report", title_style),
                Spacer(1, 20)
            ]

            table_data = [[
                'ID', 'Category', 'Make', 'Model', 'Year', 'Plate',
                'Daily Rate', 'Status', 'Fuel'
            ]]
            for row in vehicles:
                category_name = row['category_name'] if 'category_name' in row.keys() and row['category_name'] else ''
                fuel_type = row['fuel_type'] if row['fuel_type'] else ''
                
                table_data.append([
                    str(row['id']),
                    category_name[:15] if category_name else '',
                    row['make'],
                    row['model'],
                    str(row['year']),
                    row['license_plate'],
                    f"${row['daily_rate']:.2f}",
                    row['status'].title(),
                    fuel_type
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