# views/vehicle_category_view_cli.py
"""
CLI Vehicle Category Management View
"""
from datetime import datetime
from controllers.vehicle_category_controller import VehicleCategoryController


class VehicleCategoryViewCLI:
    """CLI View for Vehicle Category Management"""
    
    def __init__(self, parent, db, user):
        self.parent = parent
        self.db = db
        self.user = user
        self.controller = VehicleCategoryController(db)
        
        # Check user role for permissions
        self.user_role = user.get('role', 'staff') if user else 'staff'
        self.is_admin = self.user_role == 'admin'
        self.is_manager = self.user_role == 'manager'
        self.is_staff = self.user_role == 'staff'
        self.is_view_only = self.is_staff
        self.can_edit = self.is_admin or self.is_manager
        
        # Editing state
        self.editing_id = None
    
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
    
    def show(self):
        """Show vehicle category management menu"""
        while True:
            self.parent.clear_screen()
            self.parent.print_header()
            
            print("  🚗 VEHICLE CATEGORY MANAGEMENT")
            if self.is_view_only:
                print("  🔒 View Only Mode")
            print()
            self.parent.print_separator()
            print()
            
            # Show statistics - Convert rows to dicts
            categories_raw = self.controller.get_all_categories()
            categories = self._rows_to_dicts(categories_raw)
            total = len(categories) if categories else 0
            active = sum(1 for c in categories if c.get('category_status', 0) == 1) if categories else 0
            
            print(f"  📊 Total Categories: {total}")
            print(f"  🟢 Active: {active}")
            print(f"  🔴 Inactive: {total - active}")
            print()
            self.parent.print_separator()
            print()
            
            print("  [1] 📋 View All Categories")
            print("  [2] 🔍 Search Categories")
            if self.can_edit:
                print("  [3] ➕ Add Category")
                print("  [4] ✏️ Edit Category")
                print("  [5] 🔄 Toggle Category Status")
                print("  [6] 🗑️ Delete Category")
            print("  [7] 📊 Export Categories")
            print("  [8] ↩️ Back to Main Menu")
            print()
            self.parent.print_separator()
            print()
            
            choice = self.parent.get_input("  Select option: ").strip()
            
            if choice == "1":
                self.view_all_categories()
            elif choice == "2":
                self.search_categories()
            elif choice == "3" and self.can_edit:
                self.add_category()
            elif choice == "4" and self.can_edit:
                self.edit_category()
            elif choice == "5" and self.can_edit:
                self.toggle_category_status()
            elif choice == "6" and self.can_edit:
                self.delete_category()
            elif choice == "7":
                self.export_menu()
            elif choice == "8":
                break
            else:
                self.parent.print_error("Invalid option")
                self.parent.get_input("\nPress Enter to continue...")
    
    def view_all_categories(self):
        """View all categories in table format"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📋 ALL VEHICLE CATEGORIES")
        print()
        
        categories_raw = self.controller.get_all_categories()
        categories = self._rows_to_dicts(categories_raw)
        
        if not categories:
            self.parent.print_info("No categories found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print("  " + "-" * 120)
        print(f"  {'ID':<5} {'Name':<25} {'Base Rate':<12} {'Late Fee':<12} {'Status':<12} {'Created At':<20}")
        print("  " + "-" * 120)
        
        for category in categories:
            status = "🟢 Active" if category.get('category_status', 0) == 1 else "🔴 Inactive"
            created_at = category.get('created_at', '')
            if created_at:
                created_at = created_at[:16] if len(created_at) > 16 else created_at
            
            print(f"  {category.get('id', ''):<5} "
                  f"{category.get('name', ''):<25} "
                  f"${category.get('base_rate', 0):<11.2f} "
                  f"${category.get('late_fee_rate', 0):<11.2f} "
                  f"{status:<12} "
                  f"{created_at:<20}")
        
        print("  " + "-" * 120)
        print(f"  Total: {len(categories)} categories")
        print()
        
        # Option to view details
        view_details = self.parent.get_input("  View category details? (y/n): ").strip().lower()
        if view_details == 'y' or view_details == 'yes':
            self.view_category_details()
        else:
            self.parent.get_input("Press Enter to continue...")
    
    def view_category_details(self):
        """View detailed information about a specific category"""
        category_id = self.parent.get_input("  Enter Category ID to view details: ").strip()
        
        if not category_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            category_id = int(category_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        category_raw = self.controller.get_category_by_id(category_id)
        category = self._row_to_dict(category_raw)
        
        if not category:
            self.parent.print_error("Category not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📋 CATEGORY DETAILS")
        print()
        self.parent.print_separator()
        print()
        
        status = "Active" if category.get('category_status', 0) == 1 else "Inactive"
        status_color = "🟢" if category.get('category_status', 0) == 1 else "🔴"
        
        print(f"  ID:           {category.get('id', '')}")
        print(f"  Name:         {category.get('name', '')}")
        print(f"  Description:  {category.get('description', 'No description provided')}")
        print(f"  Base Rate:    ${category.get('base_rate', 0):.2f}")
        print(f"  Late Fee:     ${category.get('late_fee_rate', 0):.2f}")
        print(f"  Status:       {status_color} {status}")
        print(f"  Created At:   {category.get('created_at', 'N/A')}")
        print(f"  Updated At:   {category.get('updated_at', 'N/A')}")
        print()
        self.parent.print_separator()
        print()
        self.parent.get_input("Press Enter to continue...")
    
    def search_categories(self):
        """Search for categories"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  🔍 SEARCH CATEGORIES")
        print()
        
        search_term = self.parent.get_input("  Enter search term: ").strip()
        
        if not search_term:
            self.parent.print_warning("No search term entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        categories_raw = self.controller.search_categories(search_term)
        categories = self._rows_to_dicts(categories_raw)
        
        self.parent.clear_screen()
        self.parent.print_header()
        print(f"  🔍 SEARCH RESULTS: '{search_term}'")
        print()
        
        if not categories:
            self.parent.print_info("No categories found matching your search.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print("  " + "-" * 120)
        print(f"  {'ID':<5} {'Name':<25} {'Base Rate':<12} {'Late Fee':<12} {'Status':<12} {'Created At':<20}")
        print("  " + "-" * 120)
        
        for category in categories:
            status = "🟢 Active" if category.get('category_status', 0) == 1 else "🔴 Inactive"
            created_at = category.get('created_at', '')
            if created_at:
                created_at = created_at[:16] if len(created_at) > 16 else created_at
            
            print(f"  {category.get('id', ''):<5} "
                  f"{category.get('name', ''):<25} "
                  f"${category.get('base_rate', 0):<11.2f} "
                  f"${category.get('late_fee_rate', 0):<11.2f} "
                  f"{status:<12} "
                  f"{created_at:<20}")
        
        print("  " + "-" * 120)
        print(f"  Found: {len(categories)} categories")
        print()
        self.parent.get_input("Press Enter to continue...")
    
    def add_category(self):
        """Add a new category"""
        if not self.can_edit:
            self.parent.print_error("Access Denied! You don't have permission to add categories.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print("  ➕ ADD NEW VEHICLE CATEGORY")
        print()
        self.parent.print_separator()
        print()
        
        name = self.parent.get_input("  Category Name *: ").strip()
        description = self.parent.get_input("  Description: ").strip()
        base_rate = self.parent.get_input("  Base Rate ($) *: ").strip()
        late_fee = self.parent.get_input("  Late Fee Rate ($): ").strip()
        
        if not late_fee:
            late_fee = "0"
        
        # Validation
        if not name:
            self.parent.print_error("Category name is required!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        if not base_rate:
            self.parent.print_error("Base rate is required!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            base_rate = float(base_rate)
            if base_rate < 0:
                self.parent.print_error("Base rate cannot be negative!")
                self.parent.get_input("\nPress Enter to continue...")
                return
        except ValueError:
            self.parent.print_error("Base rate must be a number!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            late_fee = float(late_fee)
            if late_fee < 0:
                self.parent.print_error("Late fee rate cannot be negative!")
                self.parent.get_input("\nPress Enter to continue...")
                return
        except ValueError:
            self.parent.print_error("Late fee rate must be a number!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        # Confirm
        print()
        print("  Category Details:")
        print(f"  Name: {name}")
        print(f"  Description: {description or 'No description'}")
        print(f"  Base Rate: ${base_rate:.2f}")
        print(f"  Late Fee Rate: ${late_fee:.2f}")
        print()
        
        confirm = self.parent.get_input("  Add category? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Category addition cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        # Save
        data = {
            'name': name,
            'description': description,
            'base_rate': base_rate,
            'late_fee_rate': late_fee,
            'status': '1'
        }
        
        result = self.controller.add_category(data)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def edit_category(self):
        """Edit a category"""
        if not self.can_edit:
            self.parent.print_error("Access Denied! You don't have permission to edit categories.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        category_id = self.parent.get_input("  Enter Category ID to edit: ").strip()
        
        if not category_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            category_id = int(category_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        category_raw = self.controller.get_category_by_id(category_id)
        category = self._row_to_dict(category_raw)
        
        if not category:
            self.parent.print_error("Category not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print("  ✏️ EDIT VEHICLE CATEGORY")
        print()
        print(f"  Editing: {category.get('name', '')}")
        print()
        self.parent.print_separator()
        print()
        
        name = self.parent.get_input(f"  Category Name [{category.get('name', '')}]: ").strip()
        description = self.parent.get_input(f"  Description [{category.get('description', '')}]: ").strip()
        base_rate = self.parent.get_input(f"  Base Rate ($) [{category.get('base_rate', 0):.2f}]: ").strip()
        late_fee = self.parent.get_input(f"  Late Fee Rate ($) [{category.get('late_fee_rate', 0):.2f}]: ").strip()
        
        # Use existing values if not changed
        data = {
            'name': name if name else category.get('name', ''),
            'description': description if description else category.get('description', ''),
            'base_rate': float(base_rate) if base_rate else category.get('base_rate', 0),
            'late_fee_rate': float(late_fee) if late_fee else category.get('late_fee_rate', 0),
            'status': str(category.get('category_status', 1))
        }
        
        # Confirm
        print()
        print("  New values:")
        print(f"  Name: {data['name']}")
        print(f"  Description: {data['description'] or 'No description'}")
        print(f"  Base Rate: ${data['base_rate']:.2f}")
        print(f"  Late Fee Rate: ${data['late_fee_rate']:.2f}")
        print()
        
        confirm = self.parent.get_input("  Save changes? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Changes discarded.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        # Update
        result = self.controller.update_category(category_id, data)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def toggle_category_status(self):
        """Toggle category status (activate/deactivate)"""
        if not self.can_edit:
            self.parent.print_error("Access Denied! You don't have permission to modify category status.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        category_id = self.parent.get_input("  Enter Category ID to toggle status: ").strip()
        
        if not category_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            category_id = int(category_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        category_raw = self.controller.get_category_by_id(category_id)
        category = self._row_to_dict(category_raw)
        
        if not category:
            self.parent.print_error("Category not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        current_status = category.get('category_status', 0)
        status_text = "Active" if current_status == 1 else "Inactive"
        action = "deactivate" if current_status == 1 else "activate"
        
        print()
        self.parent.print_warning(f"Category: {category.get('name', '')}")
        print(f"  Current Status: {status_text}")
        print()
        
        confirm = self.parent.get_input(f"  Are you sure you want to {action} this category? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Action cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        result = self.controller.toggle_status(category_id, current_status)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def delete_category(self):
        """Delete a category"""
        if not self.can_edit:
            self.parent.print_error("Access Denied! You don't have permission to delete categories.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        category_id = self.parent.get_input("  Enter Category ID to delete: ").strip()
        
        if not category_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            category_id = int(category_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        category_raw = self.controller.get_category_by_id(category_id)
        category = self._row_to_dict(category_raw)
        
        if not category:
            self.parent.print_error("Category not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print()
        self.parent.print_warning(f"You are about to delete: {category.get('name', '')}")
        print("  This action cannot be undone!")
        print()
        
        confirm = self.parent.get_input("  Confirm delete? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Deletion cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        result = self.controller.delete_category(category_id)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_menu(self):
        """Export categories menu"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📊 EXPORT VEHICLE CATEGORIES")
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
        categories_raw = self.controller.get_all_categories()
        categories = self._rows_to_dicts(categories_raw)
        
        if not categories:
            self.parent.print_warning("No categories to export.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        import csv
        
        filename = f"vehicle_categories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Description', 'Base Rate', 'Late Fee Rate', 'Status', 'Created At'])
                
                for row in categories:
                    status = 'Active' if row.get('category_status', 0) == 1 else 'Inactive'
                    writer.writerow([
                        row.get('id', ''),
                        row.get('name', ''),
                        row.get('description', ''),
                        f"{row.get('base_rate', 0):.2f}",
                        f"{row.get('late_fee_rate', 0):.2f}",
                        status,
                        row.get('created_at', '')
                    ])
            
            self.parent.print_success(f"Exported {len(categories)} categories to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_excel(self):
        """Export to Excel"""
        categories_raw = self.controller.get_all_categories()
        categories = self._rows_to_dicts(categories_raw)
        
        if not categories:
            self.parent.print_warning("No categories to export.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            import openpyxl
        except ImportError:
            self.parent.print_error("Please install openpyxl: pip install openpyxl")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        filename = f"vehicle_categories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Vehicle Categories"
            
            headers = ['ID', 'Name', 'Description', 'Base Rate', 'Late Fee Rate', 'Status', 'Created At']
            ws.append(headers)
            
            for row in categories:
                status = 'Active' if row.get('category_status', 0) == 1 else 'Inactive'
                ws.append([
                    row.get('id', ''),
                    row.get('name', ''),
                    row.get('description', ''),
                    row.get('base_rate', 0),
                    row.get('late_fee_rate', 0),
                    status,
                    row.get('created_at', '')
                ])
            
            wb.save(filename)
            self.parent.print_success(f"Exported {len(categories)} categories to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_pdf(self):
        """Export to PDF"""
        categories_raw = self.controller.get_all_categories()
        categories = self._rows_to_dicts(categories_raw)
        
        if not categories:
            self.parent.print_warning("No categories to export.")
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
        
        filename = f"vehicle_categories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
            styles = getSampleStyleSheet()
            
            elements = []
            
            title = Paragraph("Vehicle Categories Report", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            data = [['ID', 'Name', 'Description', 'Base Rate', 'Late Fee', 'Status']]
            
            for row in categories:
                status = 'Active' if row.get('category_status', 0) == 1 else 'Inactive'
                data.append([
                    str(row.get('id', '')),
                    row.get('name', ''),
                    (row.get('description', '') or '')[:40],
                    f"${row.get('base_rate', 0):.2f}",
                    f"${row.get('late_fee_rate', 0):.2f}",
                    status
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
            
            self.parent.print_success(f"Exported {len(categories)} categories to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")