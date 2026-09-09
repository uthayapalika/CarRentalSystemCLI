# views/maintenance_view_cli.py
"""
CLI Maintenance Management View
"""
from datetime import datetime, timedelta
from controllers.maintenance_controller import MaintenanceController


class MaintenanceViewCLI:
    """CLI View for Maintenance Management"""
    
    def __init__(self, parent, db, user):
        self.parent = parent
        self.db = db
        self.user = user
        self.controller = MaintenanceController(db)
        
        # Check user role for permissions
        self.user_role = user.get('role', 'staff') if user else 'staff'
        self.is_admin = self.user_role == 'admin'
        self.is_manager = self.user_role == 'manager'
        self.is_staff = self.user_role == 'staff'
        self.is_view_only = self.is_staff
        self.can_edit = self.is_admin or self.is_manager
        
        # Editing state
        self.editing_id = None
        
        # Load vehicles
        self.vehicles = []
        self.load_vehicles()
    
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
    
    def load_vehicles(self):
        """Load vehicles for dropdown"""
        try:
            from models.vehicle_model import VehicleModel
            model = VehicleModel(self.db)
            vehicles_raw = model.get_all()
            self.vehicles = self._rows_to_dicts(vehicles_raw)
        except Exception as e:
            self.parent.print_warning(f"Could not load vehicles: {e}")
    
    def show(self):
        """Show maintenance management menu"""
        while True:
            self.parent.clear_screen()
            self.parent.print_header()
            
            print("  🛠️ MAINTENANCE MANAGEMENT")
            if self.is_view_only:
                print("  🔒 View Only Mode")
            print()
            self.parent.print_separator()
            print()
            
            # Show statistics
            records_raw = self.controller.get_all()
            records = self._rows_to_dicts(records_raw)
            total = len(records) if records else 0
            pending = sum(1 for r in records if r.get('status') == 'pending') if records else 0
            completed = sum(1 for r in records if r.get('status') == 'completed') if records else 0
            cancelled = sum(1 for r in records if r.get('status') == 'cancelled') if records else 0
            
            print(f"  📊 Total Records: {total}")
            print(f"  🟡 Pending: {pending}")
            print(f"  🟢 Completed: {completed}")
            print(f"  🔴 Cancelled: {cancelled}")
            print()
            self.parent.print_separator()
            print()
            
            print("  [1] 📋 View All Records")
            print("  [2] 🔍 Search Records")
            print("  [3] 🟡 View Pending Records")
            print("  [4] 🟢 View Completed Records")
            if self.can_edit:
                print("  [5] ➕ Add Record")
                print("  [6] ✏️ Edit Record")
                print("  [7] 🔄 Change Record Status")
                print("  [8] 🗑️ Delete Record")
            print("  [9] 📊 Export Records")
            print("  [0] ↩️ Back to Main Menu")
            print()
            self.parent.print_separator()
            print()
            
            choice = self.parent.get_input("  Select option: ").strip()
            
            if choice == "1":
                self.view_all_records()
            elif choice == "2":
                self.search_records()
            elif choice == "3":
                self.view_records_by_status("pending")
            elif choice == "4":
                self.view_records_by_status("completed")
            elif choice == "5" and self.can_edit:
                self.add_record()
            elif choice == "6" and self.can_edit:
                self.edit_record()
            elif choice == "7" and self.can_edit:
                self.change_status()
            elif choice == "8" and self.can_edit:
                self.delete_record()
            elif choice == "9":
                self.export_menu()
            elif choice == "0":
                break
            else:
                self.parent.print_error("Invalid option")
                self.parent.get_input("\nPress Enter to continue...")
    
    def view_all_records(self):
        """View all maintenance records"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📋 ALL MAINTENANCE RECORDS")
        print()
        
        records_raw = self.controller.get_all()
        records = self._rows_to_dicts(records_raw)
        
        if not records:
            self.parent.print_info("No maintenance records found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.display_record_table(records)
        
        # Option to view details
        view_details = self.parent.get_input("  View record details? (y/n): ").strip().lower()
        if view_details == 'y' or view_details == 'yes':
            self.view_record_details()
        else:
            self.parent.get_input("Press Enter to continue...")
    
    def view_records_by_status(self, status):
        """View records filtered by status"""
        self.parent.clear_screen()
        self.parent.print_header()
        status_display = {
            'pending': '🟡 PENDING',
            'completed': '🟢 COMPLETED',
            'cancelled': '🔴 CANCELLED'
        }.get(status, status.upper())
        
        print(f"  {status_display} MAINTENANCE RECORDS")
        print()
        
        records_raw = self.controller.get_by_status(status)
        records = self._rows_to_dicts(records_raw)
        
        if not records:
            self.parent.print_info(f"No {status} maintenance records found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.display_record_table(records)
        self.parent.get_input("\nPress Enter to continue...")
    
    def display_record_table(self, records):
        """Display maintenance records in a formatted table"""
        print("  " + "-" * 140)
        print(f"  {'ID':<5} {'Vehicle':<22} {'Type':<20} {'Date':<12} "
              f"{'Cost':<10} {'Status':<12} {'Next Service':<12}")
        print("  " + "-" * 140)
        
        for record in records:
            vehicle_name = f"{record.get('make', '')} {record.get('model', '')}"[:20]
            status_display = {
                'pending': '🟡 Pending',
                'completed': '🟢 Completed',
                'cancelled': '🔴 Cancelled'
            }.get(record.get('status', ''), record.get('status', ''))
            
            next_service = record.get('next_service_due', '')
            if next_service:
                next_service = next_service[:10] if len(next_service) > 10 else next_service
            
            print(f"  {record.get('maintenance_id', ''):<5} "
                  f"{vehicle_name:<22} "
                  f"{record.get('maintenance_type', '')[:20]:<20} "
                  f"{record.get('service_date', '')[:10]:<12} "
                  f"${record.get('cost', 0):<9.2f} "
                  f"{status_display:<12} "
                  f"{next_service:<12}")
        
        print("  " + "-" * 140)
        print(f"  Total: {len(records)} records")
        print()
    
    def view_record_details(self):
        """View detailed information about a specific record"""
        record_id = self.parent.get_input("  Enter Record ID to view details: ").strip()
        
        if not record_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            record_id = int(record_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        all_records_raw = self.controller.get_all()
        all_records = self._rows_to_dicts(all_records_raw)
        record = None
        for r in all_records:
            if r.get('maintenance_id') == record_id:
                record = r
                break
        
        if not record:
            self.parent.print_error("Record not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📋 MAINTENANCE RECORD DETAILS")
        print()
        self.parent.print_separator()
        print()
        
        status_display = {
            'pending': '🟡 Pending',
            'completed': '🟢 Completed',
            'cancelled': '🔴 Cancelled'
        }.get(record.get('status', ''), record.get('status', ''))
        
        vehicle_name = f"{record.get('make', '')} {record.get('model', '')}"
        license_plate = record.get('license_plate', 'N/A')
        
        print(f"  ID:                {record.get('maintenance_id', '')}")
        print(f"  Vehicle:           {vehicle_name}")
        print(f"  License Plate:     {license_plate}")
        print(f"  Maintenance Type:  {record.get('maintenance_type', '')}")
        print(f"  Service Date:      {record.get('service_date', '')}")
        print(f"  Odometer:          {record.get('odometer_reading', 0):,}")
        print(f"  Cost:              ${record.get('cost', 0):.2f}")
        print(f"  Provider:          {record.get('service_provider', 'N/A')}")
        print(f"  Status:            {status_display}")
        print(f"  Next Service Due:  {record.get('next_service_due', 'Not set')}")
        print(f"  Description:       {record.get('description', 'No description')}")
        print()
        self.parent.print_separator()
        print()
        self.parent.get_input("Press Enter to continue...")
    
    def search_records(self):
        """Search for maintenance records"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  🔍 SEARCH MAINTENANCE RECORDS")
        print()
        
        search_term = self.parent.get_input("  Enter search term: ").strip()
        
        if not search_term:
            self.parent.print_warning("No search term entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        all_records_raw = self.controller.get_all()
        all_records = self._rows_to_dicts(all_records_raw)
        records = []
        for r in all_records:
            vehicle_name = f"{r.get('make', '')} {r.get('model', '')} {r.get('license_plate', '')}"
            if (search_term.lower() in vehicle_name.lower() or
                search_term.lower() in r.get('maintenance_type', '').lower() or
                search_term.lower() in (r.get('service_provider', '') or '').lower()):
                records.append(r)
        
        self.parent.clear_screen()
        self.parent.print_header()
        print(f"  🔍 SEARCH RESULTS: '{search_term}'")
        print()
        
        if not records:
            self.parent.print_info("No records found matching your search.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.display_record_table(records)
        self.parent.get_input("\nPress Enter to continue...")
    
    def add_record(self):
        """Add a new maintenance record"""
        if not self.can_edit:
            self.parent.print_error("Access Denied! You don't have permission to add records.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print("  ➕ ADD MAINTENANCE RECORD")
        print()
        self.parent.print_separator()
        print()
        
        # Vehicle selection
        if not self.vehicles:
            self.parent.print_error("No vehicles available.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print("  Available Vehicles:")
        for i, v in enumerate(self.vehicles, 1):
            print(f"  {i}. {v.get('make', '')} {v.get('model', '')} ({v.get('license_plate', '')})")
        print()
        
        vehicle_choice = self.parent.get_input("  Select vehicle (number): ").strip()
        try:
            v_idx = int(vehicle_choice) - 1
            if v_idx < 0 or v_idx >= len(self.vehicles):
                self.parent.print_error("Invalid vehicle selection!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            vehicle_id = self.vehicles[v_idx]['id']
        except ValueError:
            self.parent.print_error("Invalid input!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        # Maintenance Type
        print()
        print("  Maintenance Types:")
        types = [
            "Oil Change", "Tire Replacement", "Brake Service", "Engine Service",
            "Transmission Service", "Battery Replacement", "Wheel Alignment",
            "AC Service", "General Inspection", "Body Repair", "Paint Work",
            "Accident Repair", "Routine Service", "Major Service", "Other"
        ]
        for i, t in enumerate(types, 1):
            print(f"  {i}. {t}")
        print()
        
        type_choice = self.parent.get_input("  Select maintenance type (number): ").strip()
        try:
            t_idx = int(type_choice) - 1
            if t_idx < 0 or t_idx >= len(types):
                self.parent.print_error("Invalid type selection!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            maintenance_type = types[t_idx]
        except ValueError:
            self.parent.print_error("Invalid input!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        service_date = self.parent.get_input(f"  Service Date [YYYY-MM-DD] [{datetime.now().strftime('%Y-%m-%d')}]: ").strip()
        if not service_date:
            service_date = datetime.now().strftime('%Y-%m-%d')
        
        odometer = self.parent.get_input("  Odometer Reading: ").strip() or "0"
        cost = self.parent.get_input("  Cost ($): ").strip() or "0"
        provider = self.parent.get_input("  Service Provider: ").strip()
        description = self.parent.get_input("  Description: ").strip()
        
        next_service = self.parent.get_input(f"  Next Service Due [{(datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')}]: ").strip()
        if not next_service:
            next_service = (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')
        
        # Validation
        try:
            odometer = int(odometer)
            if odometer < 0:
                self.parent.print_error("Odometer cannot be negative!")
                self.parent.get_input("\nPress Enter to continue...")
                return
        except ValueError:
            self.parent.print_error("Odometer must be a number!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            cost = float(cost)
            if cost < 0:
                self.parent.print_error("Cost cannot be negative!")
                self.parent.get_input("\nPress Enter to continue...")
                return
        except ValueError:
            self.parent.print_error("Cost must be a number!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        # Confirm
        print()
        print("  Record Details:")
        print(f"  Vehicle: {self.vehicles[v_idx]['make']} {self.vehicles[v_idx]['model']}")
        print(f"  Type: {maintenance_type}")
        print(f"  Date: {service_date}")
        print(f"  Cost: ${cost:.2f}")
        print()
        
        confirm = self.parent.get_input("  Add record? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Record addition cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        data = {
            'vehicle_id': vehicle_id,
            'maintenance_type': maintenance_type,
            'service_date': service_date,
            'odometer_reading': odometer,
            'cost': cost,
            'service_provider': provider,
            'description': description,
            'status': 'pending',
            'next_service_due': next_service
        }
        
        result = self.controller.add(data)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def edit_record(self):
        """Edit a maintenance record"""
        if not self.can_edit:
            self.parent.print_error("Access Denied! You don't have permission to edit records.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        record_id = self.parent.get_input("  Enter Record ID to edit: ").strip()
        
        if not record_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            record_id = int(record_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        all_records_raw = self.controller.get_all()
        all_records = self._rows_to_dicts(all_records_raw)
        record = None
        for r in all_records:
            if r.get('maintenance_id') == record_id:
                record = r
                break
        
        if not record:
            self.parent.print_error("Record not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print("  ✏️ EDIT MAINTENANCE RECORD")
        print()
        print(f"  Editing Record #{record_id}")
        print()
        self.parent.print_separator()
        print()
        
        # Get current vehicle info
        vehicle_name = f"{record.get('make', '')} {record.get('model', '')}"
        print(f"  Vehicle: {vehicle_name}")
        print()
        
        maintenance_type = self.parent.get_input(f"  Maintenance Type [{record.get('maintenance_type', '')}]: ").strip()
        service_date = self.parent.get_input(f"  Service Date [{record.get('service_date', '')}]: ").strip()
        odometer = self.parent.get_input(f"  Odometer [{record.get('odometer_reading', 0)}]: ").strip()
        cost = self.parent.get_input(f"  Cost ($) [{record.get('cost', 0)}]: ").strip()
        provider = self.parent.get_input(f"  Provider [{record.get('service_provider', '')}]: ").strip()
        description = self.parent.get_input(f"  Description [{record.get('description', '')}]: ").strip()
        next_service = self.parent.get_input(f"  Next Service Due [{record.get('next_service_due', '')}]: ").strip()
        
        # Use existing values if not changed
        try:
            data = {
                'vehicle_id': record.get('vehicle_id'),
                'maintenance_type': maintenance_type if maintenance_type else record.get('maintenance_type', ''),
                'service_date': service_date if service_date else record.get('service_date', ''),
                'odometer_reading': int(odometer) if odometer else record.get('odometer_reading', 0),
                'cost': float(cost) if cost else record.get('cost', 0),
                'service_provider': provider if provider else record.get('service_provider', ''),
                'description': description if description else record.get('description', ''),
                'status': record.get('status', 'pending'),
                'next_service_due': next_service if next_service else record.get('next_service_due', '')
            }
        except ValueError:
            self.parent.print_error("Invalid numeric value!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        # Confirm
        print()
        print("  New values:")
        print(f"  Type: {data['maintenance_type']}")
        print(f"  Date: {data['service_date']}")
        print(f"  Cost: ${data['cost']:.2f}")
        print()
        
        confirm = self.parent.get_input("  Save changes? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Changes discarded.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        result = self.controller.update(record_id, data)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def change_status(self):
        """Change record status"""
        if not self.can_edit:
            self.parent.print_error("Access Denied!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        record_id = self.parent.get_input("  Enter Record ID to change status: ").strip()
        
        if not record_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            record_id = int(record_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        all_records_raw = self.controller.get_all()
        all_records = self._rows_to_dicts(all_records_raw)
        record = None
        for r in all_records:
            if r.get('maintenance_id') == record_id:
                record = r
                break
        
        if not record:
            self.parent.print_error("Record not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print()
        print(f"  Record Type: {record.get('maintenance_type', '')}")
        print(f"  Current Status: {record.get('status', '')}")
        print()
        print("  Available statuses:")
        print("  1. pending")
        print("  2. completed")
        print("  3. cancelled")
        print()
        
        status_choice = self.parent.get_input("  Select new status (1-3): ").strip()
        status_map = {
            '1': 'pending',
            '2': 'completed',
            '3': 'cancelled'
        }
        
        if status_choice not in status_map:
            self.parent.print_error("Invalid status selection!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        new_status = status_map[status_choice]
        
        confirm = self.parent.get_input(f"  Change status to '{new_status}'? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Status change cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        result = self.controller.update_status(record_id, new_status)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def delete_record(self):
        """Delete a maintenance record"""
        if not self.can_edit:
            self.parent.print_error("Access Denied!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        record_id = self.parent.get_input("  Enter Record ID to delete: ").strip()
        
        if not record_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            record_id = int(record_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        all_records_raw = self.controller.get_all()
        all_records = self._rows_to_dicts(all_records_raw)
        record = None
        for r in all_records:
            if r.get('maintenance_id') == record_id:
                record = r
                break
        
        if not record:
            self.parent.print_error("Record not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print()
        self.parent.print_warning(f"You are about to delete maintenance record #{record_id}")
        print(f"  Type: {record.get('maintenance_type', '')}")
        print("  This action cannot be undone!")
        print()
        
        confirm = self.parent.get_input("  Confirm delete? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Deletion cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        result = self.controller.delete(record_id)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_menu(self):
        """Export records menu"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📊 EXPORT MAINTENANCE RECORDS")
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
        records_raw = self.controller.get_all()
        records = self._rows_to_dicts(records_raw)
        
        if not records:
            self.parent.print_warning("No records to export.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        import csv
        
        filename = f"maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'maintenance_id', 'vehicle', 'license_plate', 'maintenance_type',
                    'service_date', 'odometer_reading', 'cost', 'service_provider',
                    'status', 'next_service_due', 'description'
                ])
                writer.writeheader()
                for record in records:
                    vehicle_name = f"{record.get('make', '')} {record.get('model', '')}"
                    writer.writerow({
                        'maintenance_id': record.get('maintenance_id', ''),
                        'vehicle': vehicle_name,
                        'license_plate': record.get('license_plate', ''),
                        'maintenance_type': record.get('maintenance_type', ''),
                        'service_date': record.get('service_date', ''),
                        'odometer_reading': record.get('odometer_reading', ''),
                        'cost': record.get('cost', ''),
                        'service_provider': record.get('service_provider', ''),
                        'status': record.get('status', ''),
                        'next_service_due': record.get('next_service_due', ''),
                        'description': record.get('description', '')
                    })
            
            self.parent.print_success(f"Exported {len(records)} records to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_excel(self):
        """Export to Excel"""
        records_raw = self.controller.get_all()
        records = self._rows_to_dicts(records_raw)
        
        if not records:
            self.parent.print_warning("No records to export.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            import openpyxl
        except ImportError:
            self.parent.print_error("Please install openpyxl: pip install openpyxl")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        filename = f"maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Maintenance Records"
            
            headers = ['ID', 'Vehicle', 'License Plate', 'Type', 'Date', 
                      'Odometer', 'Cost', 'Provider', 'Status', 'Next Service']
            ws.append(headers)
            
            for record in records:
                vehicle_name = f"{record.get('make', '')} {record.get('model', '')}"
                ws.append([
                    record.get('maintenance_id', ''),
                    vehicle_name,
                    record.get('license_plate', ''),
                    record.get('maintenance_type', ''),
                    record.get('service_date', ''),
                    record.get('odometer_reading', ''),
                    record.get('cost', ''),
                    record.get('service_provider', ''),
                    record.get('status', ''),
                    record.get('next_service_due', '')
                ])
            
            wb.save(filename)
            self.parent.print_success(f"Exported {len(records)} records to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_pdf(self):
        """Export to PDF"""
        records_raw = self.controller.get_all()
        records = self._rows_to_dicts(records_raw)
        
        if not records:
            self.parent.print_warning("No records to export.")
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
        
        filename = f"maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
            styles = getSampleStyleSheet()
            
            elements = []
            
            title = Paragraph("Maintenance Report", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            data = [['ID', 'Vehicle', 'Type', 'Date', 'Cost', 'Status']]
            
            for record in records:
                vehicle_name = f"{record.get('make', '')} {record.get('model', '')}"[:25]
                data.append([
                    str(record.get('maintenance_id', '')),
                    vehicle_name,
                    record.get('maintenance_type', ''),
                    record.get('service_date', '')[:10],
                    f"${record.get('cost', 0):.2f}",
                    record.get('status', '').title()
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
            
            self.parent.print_success(f"Exported {len(records)} records to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")