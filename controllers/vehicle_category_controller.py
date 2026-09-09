# controllers/vehicle_category_controller.py
"""
Vehicle Category Controller
"""
import csv
from datetime import datetime
from factories import ModelFactory


class VehicleCategoryController:
    def __init__(self, db):
        self.db = db
        self.model = ModelFactory.create_model("vehicle_category", db=db)

    # ---------- READ ----------

    def get_all_categories(self):
        return self.model.get_all()

    def get_category_by_id(self, category_id):
        return self.model.get_by_id(category_id)

    def search_categories(self, term):
        if not term:
            return self.get_all_categories()
        return self.model.search(term)

    # ---------- VALIDATION HELPER ----------

    def _validate(self, data):
        name = data.get('name', '').strip()
        base_rate = data.get('base_rate', '').strip()
        late_fee = data.get('late_fee_rate', '').strip()

        if not name:
            return None, 'Category name is required'

        try:
            base_rate = float(base_rate)
            if base_rate < 0:
                return None, 'Base rate cannot be negative'
        except ValueError:
            return None, 'Base rate must be a number'

        try:
            late_fee = float(late_fee) if late_fee else 0
            if late_fee < 0:
                return None, 'Late fee rate cannot be negative'
        except ValueError:
            return None, 'Late fee rate must be a number'

        status = 1 if data.get('status', '1') == '1' else 0
        description = data.get('description', '').strip()

        return {
            'name': name,
            'description': description,
            'base_rate': base_rate,
            'late_fee_rate': late_fee,
            'status': status
        }, None

    # ---------- CREATE ----------

    def add_category(self, data):
        clean, error = self._validate(data)
        if error:
            return {'success': False, 'message': error}

        result = self.model.insert(
            clean['name'], clean['description'],
            clean['base_rate'], clean['late_fee_rate'], clean['status']
        )
        if result is None:
            return {'success': False, 'message': 'Category name already exists or failed to add'}
        return {'success': True, 'message': 'Category added successfully'}

    # ---------- UPDATE ----------

    def update_category(self, category_id, data):
        clean, error = self._validate(data)
        if error:
            return {'success': False, 'message': error}

        result = self.model.update(
            category_id, clean['name'], clean['description'],
            clean['base_rate'], clean['late_fee_rate'], clean['status']
        )
        if result is None:
            return {'success': False, 'message': 'Failed to update category'}
        return {'success': True, 'message': 'Category updated successfully'}

    # ---------- DELETE ----------

    def delete_category(self, category_id):
        result = self.model.delete(category_id)
        if result is None:
            return {'success': False, 'message': 'Failed to delete category'}
        return {'success': True, 'message': 'Category deleted successfully'}

    # ---------- TOGGLE ----------

    def toggle_status(self, category_id, current_status):
        new_status = 0 if current_status == 1 else 1
        result = self.model.toggle_status(category_id, new_status)
        if result is None:
            return {'success': False, 'message': 'Failed to toggle status'}
        action = 'activated' if new_status == 1 else 'deactivated'
        return {'success': True, 'message': f'Category {action} successfully'}

    # ---------- EXPORT: CSV ----------

    def export_to_csv(self, categories, filename=None):
        if not filename:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[('CSV files', '*.csv')],
                initialfile=f'vehicle_categories_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
            if not filename:
                return

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Description', 'Base Rate', 'Late Fee Rate', 'Status', 'Created At'])
                for row in categories:
                    # Handle both dict and sqlite3.Row
                    if hasattr(row, 'keys'):
                        row_dict = dict(row)
                    else:
                        row_dict = row
                    
                    status = 'Active' if row_dict.get('category_status', 0) == 1 else 'Inactive'
                    writer.writerow([
                        row_dict.get('id', ''),
                        row_dict.get('name', ''),
                        row_dict.get('description', ''),
                        f"{row_dict.get('base_rate', 0):.2f}",
                        f"{row_dict.get('late_fee_rate', 0):.2f}",
                        status,
                        row_dict.get('created_at', '')
                    ])
            return {'success': True, 'message': f'Exported to CSV: {filename}'}
        except Exception as e:
            return {'success': False, 'message': f'CSV export failed: {e}'}

    # ---------- EXPORT: EXCEL ----------

    def export_to_excel(self, categories, filename=None):
        if not filename:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[('Excel files', '*.xlsx')],
                initialfile=f'vehicle_categories_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
            if not filename:
                return

        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Vehicle Categories"

            headers = ['ID', 'Name', 'Description', 'Base Rate', 'Late Fee Rate', 'Status', 'Created At']
            ws.append(headers)

            for row in categories:
                if hasattr(row, 'keys'):
                    row_dict = dict(row)
                else:
                    row_dict = row
                
                status = 'Active' if row_dict.get('category_status', 0) == 1 else 'Inactive'
                ws.append([
                    row_dict.get('id', ''),
                    row_dict.get('name', ''),
                    row_dict.get('description', ''),
                    row_dict.get('base_rate', 0),
                    row_dict.get('late_fee_rate', 0),
                    status,
                    row_dict.get('created_at', '')
                ])

            wb.save(filename)
            return {'success': True, 'message': f'Exported to Excel: {filename}'}
        except Exception as e:
            return {'success': False, 'message': f'Excel export failed: {e}'}

    # ---------- EXPORT: PDF ----------

    def export_to_pdf(self, categories, filename=None):
        if not filename:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension='.pdf',
                filetypes=[('PDF files', '*.pdf')],
                initialfile=f'vehicle_categories_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            )
            if not filename:
                return

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import landscape, letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER

            doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('Title', parent=styles['Title'], alignment=TA_CENTER)

            elements = [
                Paragraph("Vehicle Categories Report", title_style),
                Spacer(1, 20)
            ]

            table_data = [['ID', 'Name', 'Description', 'Base Rate', 'Late Fee', 'Status']]
            
            for row in categories:
                if hasattr(row, 'keys'):
                    row_dict = dict(row)
                else:
                    row_dict = row
                
                status = 'Active' if row_dict.get('category_status', 0) == 1 else 'Inactive'
                table_data.append([
                    str(row_dict.get('id', '')),
                    row_dict.get('name', ''),
                    (row_dict.get('description', '') or '')[:40],
                    f"${row_dict.get('base_rate', 0):.2f}",
                    f"${row_dict.get('late_fee_rate', 0):.2f}",
                    status
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
            return {'success': True, 'message': f'Exported to PDF: {filename}'}
        except Exception as e:
            return {'success': False, 'message': f'PDF export failed: {e}'}