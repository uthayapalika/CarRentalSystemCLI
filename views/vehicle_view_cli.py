# views/vehicle_view_cli.py
"""
CLI Vehicle Management View
"""
from datetime import datetime
from controllers.vehicle_controller import VehicleController


class VehicleViewCLI:
    """CLI View for Vehicle Management"""
    
    def __init__(self, parent, db, user):
        self.parent = parent
        self.db = db
        self.user = user
        self.controller = VehicleController(db)
        
        # Check user role for permissions
        self.user_role = user.get('role', 'staff') if user else 'staff'
        self.is_admin = self.user_role == 'admin'
        self.is_manager = self.user_role == 'manager'
        self.is_staff = self.user_role == 'staff'
        self.is_view_only = self.is_staff
        self.can_edit = self.is_admin or self.is_manager
        
        # Editing state
        self.editing_id = None
        
        # Load categories
        self.categories = []
        self.load_categories()
    
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
    
    def load_categories(self):
        """Load categories for dropdown"""
        try:
            from models.vehicle_category_model import VehicleCategoryModel
            model = VehicleCategoryModel(self.db)
            categories_raw = model.get_all()
            self.categories = self._rows_to_dicts(categories_raw)
        except Exception as e:
            self.parent.print_warning(f"Could not load categories: {e}")
    
    def show(self):
        """Show vehicle management menu"""
        while True:
            self.parent.clear_screen()
            self.parent.print_header()
            
            print("  🚗 VEHICLE MANAGEMENT")
            if self.is_view_only:
                print("  🔒 View Only Mode")
            print()
            self.parent.print_separator()
            print()
            
            # Show statistics
            vehicles_raw = self.controller.get_all_vehicles()
            vehicles = self._rows_to_dicts(vehicles_raw)
            total = len(vehicles) if vehicles else 0
            
            # Get status counts - already returns dict, no conversion needed
            counts = self.controller.get_status_counts()
            available = counts.get('available', 0)
            rented = counts.get('rented', 0)
            maintenance = counts.get('maintenance', 0)
            reserved = counts.get('reserved', 0)
            
            print(f"  📊 Total Vehicles: {total}")
            print(f"  🟢 Available: {available}")
            print(f"  🔴 Rented: {rented}")
            print(f"  🟡 Maintenance: {maintenance}")
            print(f"  🔵 Reserved: {reserved}")
            print()
            self.parent.print_separator()
            print()
            
            print("  [1] 📋 View All Vehicles")
            print("  [2] 🔍 Search Vehicles")
            print("  [3] 🟢 View Available Vehicles")
            print("  [4] 🔴 View Rented Vehicles")
            if self.can_edit:
                print("  [5] ➕ Add Vehicle")
                print("  [6] ✏️ Edit Vehicle")
                print("  [7] 🔄 Change Vehicle Status")
                print("  [8] 🗑️ Delete Vehicle")
            print("  [9] 📊 Export Vehicles")
            print("  [0] ↩️ Back to Main Menu")
            print()
            self.parent.print_separator()
            print()
            
            choice = self.parent.get_input("  Select option: ").strip()
            
            if choice == "1":
                self.view_all_vehicles()
            elif choice == "2":
                self.search_vehicles()
            elif choice == "3":
                self.view_vehicles_by_status("available")
            elif choice == "4":
                self.view_vehicles_by_status("rented")
            elif choice == "5" and self.can_edit:
                self.add_vehicle()
            elif choice == "6" and self.can_edit:
                self.edit_vehicle()
            elif choice == "7" and self.can_edit:
                self.change_status()
            elif choice == "8" and self.can_edit:
                self.delete_vehicle()
            elif choice == "9":
                self.export_menu()
            elif choice == "0":
                break
            else:
                self.parent.print_error("Invalid option")
                self.parent.get_input("\nPress Enter to continue...")
    
    def view_all_vehicles(self):
        """View all vehicles in table format"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📋 ALL VEHICLES")
        print()
        
        vehicles_raw = self.controller.get_all_vehicles()
        vehicles = self._rows_to_dicts(vehicles_raw)
        
        if not vehicles:
            self.parent.print_info("No vehicles found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.display_vehicle_table(vehicles)
        
        # Option to view details
        view_details = self.parent.get_input("  View vehicle details? (y/n): ").strip().lower()
        if view_details == 'y' or view_details == 'yes':
            self.view_vehicle_details()
        else:
            self.parent.get_input("Press Enter to continue...")
    
    def view_vehicles_by_status(self, status):
        """View vehicles filtered by status"""
        self.parent.clear_screen()
        self.parent.print_header()
        status_display = {
            'available': '🟢 AVAILABLE',
            'rented': '🔴 RENTED',
            'maintenance': '🟡 MAINTENANCE',
            'reserved': '🔵 RESERVED'
        }.get(status, status.upper())
        
        print(f"  {status_display} VEHICLES")
        print()
        
        vehicles_raw = self.controller.get_by_status(status)
        vehicles = self._rows_to_dicts(vehicles_raw)
        
        if not vehicles:
            self.parent.print_info(f"No {status} vehicles found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.display_vehicle_table(vehicles)
        self.parent.get_input("\nPress Enter to continue...")
    
    def display_vehicle_table(self, vehicles):
        """Display vehicles in a formatted table"""
        print("  " + "-" * 145)
        print(f"  {'ID':<5} {'Category':<15} {'Make':<12} {'Model':<15} {'Year':<6} "
              f"{'License':<12} {'Rate':<10} {'Status':<12} {'Fuel':<10}")
        print("  " + "-" * 145)
        
        for vehicle in vehicles:
            status_display = {
                'available': '🟢 Available',
                'rented': '🔴 Rented',
                'maintenance': '🟡 Maintenance',
                'reserved': '🔵 Reserved'
            }.get(vehicle.get('status', ''), vehicle.get('status', ''))
            
            category_name = vehicle.get('category_name', '') or ''
            fuel_type = vehicle.get('fuel_type', '') or ''
            
            print(f"  {vehicle.get('id', ''):<5} "
                  f"{category_name[:15]:<15} "
                  f"{vehicle.get('make', ''):<12} "
                  f"{vehicle.get('model', ''):<15} "
                  f"{vehicle.get('year', ''):<6} "
                  f"{vehicle.get('license_plate', ''):<12} "
                  f"${vehicle.get('daily_rate', 0):<9.2f} "
                  f"{status_display:<12} "
                  f"{fuel_type[:10]:<10}")
        
        print("  " + "-" * 145)
        print(f"  Total: {len(vehicles)} vehicles")
        print()
    
    def view_vehicle_details(self):
        """View detailed information about a specific vehicle"""
        vehicle_id = self.parent.get_input("  Enter Vehicle ID to view details: ").strip()
        
        if not vehicle_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            vehicle_id = int(vehicle_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        vehicle_raw = self.controller.get_vehicle_by_id(vehicle_id)
        vehicle = self._row_to_dict(vehicle_raw)
        
        if not vehicle:
            self.parent.print_error("Vehicle not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📋 VEHICLE DETAILS")
        print()
        self.parent.print_separator()
        print()
        
        status_display = {
            'available': '🟢 Available',
            'rented': '🔴 Rented',
            'maintenance': '🟡 Maintenance',
            'reserved': '🔵 Reserved'
        }.get(vehicle.get('status', ''), vehicle.get('status', ''))
        
        print(f"  ID:                {vehicle.get('id', '')}")
        print(f"  Category:          {vehicle.get('category_name', 'N/A')}")
        print(f"  Make:              {vehicle.get('make', '')}")
        print(f"  Model:             {vehicle.get('model', '')}")
        print(f"  Year:              {vehicle.get('year', '')}")
        print(f"  License Plate:     {vehicle.get('license_plate', '')}")
        print(f"  Color:             {vehicle.get('color', 'N/A')}")
        print(f"  Mileage:           {vehicle.get('mileage', 0):,}")
        print(f"  Daily Rate:        ${vehicle.get('daily_rate', 0):.2f}")
        print(f"  Status:            {status_display}")
        print(f"  Fuel Type:         {vehicle.get('fuel_type', 'N/A')}")
        print(f"  Min Rent Period:   {vehicle.get('min_rent_period', 1)} days")
        print(f"  Max Rent Period:   {vehicle.get('max_rent_period', 30)} days")
        print(f"  Created At:        {vehicle.get('created_at', 'N/A')}")
        print()
        self.parent.print_separator()
        print()
        self.parent.get_input("Press Enter to continue...")
    
    def search_vehicles(self):
        """Search for vehicles"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  🔍 SEARCH VEHICLES")
        print()
        
        search_term = self.parent.get_input("  Enter search term: ").strip()
        
        if not search_term:
            self.parent.print_warning("No search term entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        vehicles_raw = self.controller.search_vehicles(search_term)
        vehicles = self._rows_to_dicts(vehicles_raw)
        
        self.parent.clear_screen()
        self.parent.print_header()
        print(f"  🔍 SEARCH RESULTS: '{search_term}'")
        print()
        
        if not vehicles:
            self.parent.print_info("No vehicles found matching your search.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.display_vehicle_table(vehicles)
        self.parent.get_input("\nPress Enter to continue...")
    
    def add_vehicle(self):
        """Add a new vehicle"""
        if not self.can_edit:
            self.parent.print_error("Access Denied! You don't have permission to add vehicles.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print("  ➕ ADD NEW VEHICLE")
        print()
        self.parent.print_separator()
        print()
        
        # Category selection
        if not self.categories:
            self.parent.print_error("No categories available. Please add a category first.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print("  Available Categories:")
        for i, cat in enumerate(self.categories, 1):
            print(f"  {i}. {cat.get('name', '')}")
        print()
        
        cat_choice = self.parent.get_input("  Select category (number): ").strip()
        try:
            cat_idx = int(cat_choice) - 1
            if cat_idx < 0 or cat_idx >= len(self.categories):
                self.parent.print_error("Invalid category selection!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            category_id = self.categories[cat_idx]['id']
        except ValueError:
            self.parent.print_error("Invalid input!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        make = self.parent.get_input("  Make *: ").strip()
        model = self.parent.get_input("  Model *: ").strip()
        year = self.parent.get_input("  Year *: ").strip()
        license_plate = self.parent.get_input("  License Plate *: ").strip()
        color = self.parent.get_input("  Color: ").strip()
        mileage = self.parent.get_input("  Mileage: ").strip() or "0"
        daily_rate = self.parent.get_input("  Daily Rate ($) *: ").strip()
        fuel_type = self.parent.get_input("  Fuel Type (Petrol/Diesel/Electric/Hybrid): ").strip() or "Petrol"
        min_period = self.parent.get_input("  Min Rent Period (days) [1]: ").strip() or "1"
        max_period = self.parent.get_input("  Max Rent Period (days) [30]: ").strip() or "30"
        
        # Validation
        if not all([make, model, year, license_plate, daily_rate]):
            self.parent.print_error("All required fields must be filled!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            year = int(year)
            daily_rate = float(daily_rate)
            mileage = int(mileage)
            min_period = int(min_period)
            max_period = int(max_period)
            if year < 1900 or year > datetime.now().year + 1:
                self.parent.print_error(f"Year must be between 1900 and {datetime.now().year + 1}")
                self.parent.get_input("\nPress Enter to continue...")
                return
            if daily_rate < 0:
                self.parent.print_error("Daily rate cannot be negative!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            if mileage < 0:
                self.parent.print_error("Mileage cannot be negative!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            if min_period < 0 or max_period < 0:
                self.parent.print_error("Rental periods cannot be negative!")
                self.parent.get_input("\nPress Enter to continue...")
                return
            if min_period > max_period:
                self.parent.print_error("Min period cannot exceed max period!")
                self.parent.get_input("\nPress Enter to continue...")
                return
        except ValueError:
            self.parent.print_error("Invalid numeric value!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        # Confirm
        print()
        print("  Vehicle Details:")
        print(f"  Category: {self.categories[cat_idx]['name']}")
        print(f"  Make: {make}")
        print(f"  Model: {model}")
        print(f"  Year: {year}")
        print(f"  License Plate: {license_plate}")
        print(f"  Daily Rate: ${daily_rate:.2f}")
        print()
        
        confirm = self.parent.get_input("  Add vehicle? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Vehicle addition cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        data = {
            'category_id': category_id,
            'make': make,
            'model': model,
            'year': year,
            'license_plate': license_plate,
            'color': color,
            'mileage': mileage,
            'daily_rate': daily_rate,
            'status': 'available',
            'fuel_type': fuel_type,
            'min_rent_period': min_period,
            'max_rent_period': max_period
        }
        
        result = self.controller.add_vehicle(data)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def edit_vehicle(self):
        """Edit a vehicle"""
        if not self.can_edit:
            self.parent.print_error("Access Denied! You don't have permission to edit vehicles.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        vehicle_id = self.parent.get_input("  Enter Vehicle ID to edit: ").strip()
        
        if not vehicle_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            vehicle_id = int(vehicle_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        vehicle_raw = self.controller.get_vehicle_by_id(vehicle_id)
        vehicle = self._row_to_dict(vehicle_raw)
        
        if not vehicle:
            self.parent.print_error("Vehicle not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        self.parent.clear_screen()
        self.parent.print_header()
        print("  ✏️ EDIT VEHICLE")
        print()
        print(f"  Editing: {vehicle.get('make', '')} {vehicle.get('model', '')}")
        print()
        self.parent.print_separator()
        print()
        
        # Category selection
        if not self.categories:
            self.parent.print_error("No categories available.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print("  Available Categories:")
        current_cat_id = vehicle.get('category_id')
        for i, cat in enumerate(self.categories, 1):
            marker = " (current)" if cat['id'] == current_cat_id else ""
            print(f"  {i}. {cat.get('name', '')}{marker}")
        print()
        
        cat_choice = self.parent.get_input("  Select category (number) [keep current]: ").strip()
        if cat_choice:
            try:
                cat_idx = int(cat_choice) - 1
                if 0 <= cat_idx < len(self.categories):
                    category_id = self.categories[cat_idx]['id']
                else:
                    category_id = current_cat_id
            except ValueError:
                category_id = current_cat_id
        else:
            category_id = current_cat_id
        
        make = self.parent.get_input(f"  Make [{vehicle.get('make', '')}]: ").strip()
        model = self.parent.get_input(f"  Model [{vehicle.get('model', '')}]: ").strip()
        year = self.parent.get_input(f"  Year [{vehicle.get('year', '')}]: ").strip()
        license_plate = self.parent.get_input(f"  License Plate [{vehicle.get('license_plate', '')}]: ").strip()
        color = self.parent.get_input(f"  Color [{vehicle.get('color', '')}]: ").strip()
        mileage = self.parent.get_input(f"  Mileage [{vehicle.get('mileage', 0)}]: ").strip()
        daily_rate = self.parent.get_input(f"  Daily Rate ($) [{vehicle.get('daily_rate', 0)}]: ").strip()
        fuel_type = self.parent.get_input(f"  Fuel Type [{vehicle.get('fuel_type', 'Petrol')}]: ").strip()
        min_period = self.parent.get_input(f"  Min Rent Period [{vehicle.get('min_rent_period', 1)}]: ").strip()
        max_period = self.parent.get_input(f"  Max Rent Period [{vehicle.get('max_rent_period', 30)}]: ").strip()
        
        # Use existing values if not changed
        try:
            data = {
                'category_id': category_id,
                'make': make if make else vehicle.get('make', ''),
                'model': model if model else vehicle.get('model', ''),
                'year': int(year) if year else vehicle.get('year', 0),
                'license_plate': license_plate if license_plate else vehicle.get('license_plate', ''),
                'color': color if color else vehicle.get('color', ''),
                'mileage': int(mileage) if mileage else vehicle.get('mileage', 0),
                'daily_rate': float(daily_rate) if daily_rate else vehicle.get('daily_rate', 0),
                'fuel_type': fuel_type if fuel_type else vehicle.get('fuel_type', 'Petrol'),
                'min_rent_period': int(min_period) if min_period else vehicle.get('min_rent_period', 1),
                'max_rent_period': int(max_period) if max_period else vehicle.get('max_rent_period', 30),
                'status': vehicle.get('status', 'available')
            }
        except ValueError:
            self.parent.print_error("Invalid numeric value!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        # Confirm
        print()
        print("  New values:")
        print(f"  Make: {data['make']}")
        print(f"  Model: {data['model']}")
        print(f"  Year: {data['year']}")
        print(f"  License Plate: {data['license_plate']}")
        print(f"  Daily Rate: ${data['daily_rate']:.2f}")
        print()
        
        confirm = self.parent.get_input("  Save changes? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Changes discarded.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        result = self.controller.update_vehicle(vehicle_id, data)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def change_status(self):
        """Change vehicle status"""
        if not self.can_edit:
            self.parent.print_error("Access Denied!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        vehicle_id = self.parent.get_input("  Enter Vehicle ID to change status: ").strip()
        
        if not vehicle_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            vehicle_id = int(vehicle_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        vehicle_raw = self.controller.get_vehicle_by_id(vehicle_id)
        vehicle = self._row_to_dict(vehicle_raw)
        
        if not vehicle:
            self.parent.print_error("Vehicle not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print()
        print(f"  Vehicle: {vehicle.get('make', '')} {vehicle.get('model', '')}")
        print(f"  Current Status: {vehicle.get('status', '')}")
        print()
        print("  Available statuses:")
        print("  1. available")
        print("  2. rented")
        print("  3. maintenance")
        print("  4. reserved")
        print()
        
        status_choice = self.parent.get_input("  Select new status (1-4): ").strip()
        status_map = {
            '1': 'available',
            '2': 'rented',
            '3': 'maintenance',
            '4': 'reserved'
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
        
        result = self.controller.update_status(vehicle_id, new_status)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def delete_vehicle(self):
        """Delete a vehicle"""
        if not self.can_edit:
            self.parent.print_error("Access Denied!")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        vehicle_id = self.parent.get_input("  Enter Vehicle ID to delete: ").strip()
        
        if not vehicle_id:
            self.parent.print_warning("No ID entered.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            vehicle_id = int(vehicle_id)
        except ValueError:
            self.parent.print_error("Invalid ID. Must be a number.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        vehicle_raw = self.controller.get_vehicle_by_id(vehicle_id)
        vehicle = self._row_to_dict(vehicle_raw)
        
        if not vehicle:
            self.parent.print_error("Vehicle not found.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        print()
        self.parent.print_warning(f"You are about to delete: {vehicle.get('make', '')} {vehicle.get('model', '')}")
        print("  This action cannot be undone!")
        print()
        
        confirm = self.parent.get_input("  Confirm delete? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            self.parent.print_warning("Deletion cancelled.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        result = self.controller.delete_vehicle(vehicle_id)
        
        if result['success']:
            self.parent.print_success(result['message'])
        else:
            self.parent.print_error(result['message'])
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_menu(self):
        """Export vehicles menu"""
        self.parent.clear_screen()
        self.parent.print_header()
        print("  📊 EXPORT VEHICLES")
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
        vehicles_raw = self.controller.get_all_vehicles()
        vehicles = self._rows_to_dicts(vehicles_raw)
        
        if not vehicles:
            self.parent.print_warning("No vehicles to export.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        import csv
        
        filename = f"vehicles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'category_name', 'make', 'model', 'year',
                    'license_plate', 'color', 'mileage', 'daily_rate',
                    'status', 'fuel_type', 'min_rent_period', 'max_rent_period'
                ])
                writer.writeheader()
                for vehicle in vehicles:
                    writer.writerow({
                        'id': vehicle.get('id', ''),
                        'category_name': vehicle.get('category_name', ''),
                        'make': vehicle.get('make', ''),
                        'model': vehicle.get('model', ''),
                        'year': vehicle.get('year', ''),
                        'license_plate': vehicle.get('license_plate', ''),
                        'color': vehicle.get('color', ''),
                        'mileage': vehicle.get('mileage', ''),
                        'daily_rate': vehicle.get('daily_rate', ''),
                        'status': vehicle.get('status', ''),
                        'fuel_type': vehicle.get('fuel_type', ''),
                        'min_rent_period': vehicle.get('min_rent_period', ''),
                        'max_rent_period': vehicle.get('max_rent_period', '')
                    })
            
            self.parent.print_success(f"Exported {len(vehicles)} vehicles to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_excel(self):
        """Export to Excel"""
        vehicles_raw = self.controller.get_all_vehicles()
        vehicles = self._rows_to_dicts(vehicles_raw)
        
        if not vehicles:
            self.parent.print_warning("No vehicles to export.")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        try:
            import openpyxl
        except ImportError:
            self.parent.print_error("Please install openpyxl: pip install openpyxl")
            self.parent.get_input("\nPress Enter to continue...")
            return
        
        filename = f"vehicles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Vehicles"
            
            headers = ['ID', 'Category', 'Make', 'Model', 'Year', 'License Plate', 
                      'Color', 'Mileage', 'Daily Rate', 'Status', 'Fuel Type',
                      'Min Period', 'Max Period']
            ws.append(headers)
            
            for vehicle in vehicles:
                ws.append([
                    vehicle.get('id', ''),
                    vehicle.get('category_name', ''),
                    vehicle.get('make', ''),
                    vehicle.get('model', ''),
                    vehicle.get('year', ''),
                    vehicle.get('license_plate', ''),
                    vehicle.get('color', ''),
                    vehicle.get('mileage', ''),
                    vehicle.get('daily_rate', ''),
                    vehicle.get('status', ''),
                    vehicle.get('fuel_type', ''),
                    vehicle.get('min_rent_period', ''),
                    vehicle.get('max_rent_period', '')
                ])
            
            wb.save(filename)
            self.parent.print_success(f"Exported {len(vehicles)} vehicles to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")
    
    def export_pdf(self):
        """Export to PDF"""
        vehicles_raw = self.controller.get_all_vehicles()
        vehicles = self._rows_to_dicts(vehicles_raw)
        
        if not vehicles:
            self.parent.print_warning("No vehicles to export.")
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
        
        filename = f"vehicles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        self.parent.print_info(f"Exporting to: {filename}")
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
            styles = getSampleStyleSheet()
            
            elements = []
            
            title = Paragraph("Vehicle Report", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            data = [['ID', 'Make', 'Model', 'Year', 'License', 'Rate', 'Status']]
            
            for vehicle in vehicles:
                data.append([
                    str(vehicle.get('id', '')),
                    vehicle.get('make', ''),
                    vehicle.get('model', ''),
                    str(vehicle.get('year', '')),
                    vehicle.get('license_plate', ''),
                    f"${vehicle.get('daily_rate', 0):.2f}",
                    vehicle.get('status', '').title()
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
            
            self.parent.print_success(f"Exported {len(vehicles)} vehicles to {filename}")
        except Exception as e:
            self.parent.print_error(f"Export failed: {str(e)}")
        
        self.parent.get_input("\nPress Enter to continue...")