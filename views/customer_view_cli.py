# views/customer_vehicles_cli.py
"""
CLI Customer Vehicles View
"""


class CustomerVehiclesCLI:
    """CLI View for Customer Vehicles"""
    
    def __init__(self, parent, db, customer_id, booking_callback):
        self.parent = parent
        self.db = db
        self.customer_id = customer_id
        self.booking_callback = booking_callback
        self.categories = []
        self.vehicles = []
        self.current_category = "All"
        self.search_term = ""
    
    def show(self):
        """Show available vehicles"""
        while True:
            self.load_data()
            self.parent.clear_screen()
            self.parent.print_header()
            
            print("  🚗 AVAILABLE VEHICLES")
            print()
            self.parent.print_separator()
            print()
            
            # Show categories
            print("  Categories:")
            print("  [0] All")
            for i, cat in enumerate(self.categories, 1):
                print(f"  [{i}] {cat}")
            print()
            
            # Search
            search = self.parent.get_input("  Search (make/model/license) or category number: ").strip()
            
            if search.lower() == 'b' or search.lower() == 'back':
                break
            
            # Check if search is a category number
            try:
                cat_idx = int(search)
                if cat_idx == 0:
                    self.current_category = "All"
                elif 1 <= cat_idx <= len(self.categories):
                    self.current_category = self.categories[cat_idx - 1]
                else:
                    self.parent.print_error("Invalid category number!")
                    self.parent.get_input("\nPress Enter to continue...")
                    continue
                self.search_term = ""
            except ValueError:
                self.search_term = search
                self.current_category = "All"
            
            self.display_vehicles()
    
    def load_data(self):
        """Load categories and vehicles"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Load categories
            cursor.execute("SELECT name FROM vehicle_categories ORDER BY name")
            categories = cursor.fetchall()
            self.categories = []
            for cat in categories:
                if hasattr(cat, 'keys'):
                    self.categories.append(cat['name'])
                else:
                    self.categories.append(cat[0])
            
            cursor.close()
        except Exception as e:
            self.parent.print_error(f"Error loading data: {str(e)}")
    
    def display_vehicles(self):
        """Display vehicles with filters"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    v.id,
                    v.make,
                    v.model,
                    v.year,
                    v.license_plate,
                    v.daily_rate,
                    v.status,
                    v.fuel_type,
                    v.mileage,
                    v.color,
                    v.min_rent_period,
                    v.max_rent_period,
                    vc.name as category_name,
                    vc.late_fee_rate
                FROM vehicles v
                LEFT JOIN vehicle_categories vc ON v.category_id = vc.id
                WHERE v.status = 'available'
            """
            
            params = []
            
            if self.search_term:
                query += " AND (v.make LIKE ? OR v.model LIKE ? OR v.license_plate LIKE ?)"
                search_param = f"%{self.search_term}%"
                params.extend([search_param, search_param, search_param])
            
            if self.current_category != "All":
                query += " AND vc.name = ?"
                params.append(self.current_category)
            
            query += " ORDER BY v.make, v.model"
            
            cursor.execute(query, params)
            vehicles = cursor.fetchall()
            cursor.close()
            
            if not vehicles:
                self.parent.clear_screen()
                self.parent.print_header()
                print("  🚗 AVAILABLE VEHICLES")
                print()
                self.parent.print_separator()
                print()
                self.parent.print_info("No vehicles available matching your criteria.")
                self.parent.get_input("\nPress Enter to continue...")
                return
            
            self.parent.clear_screen()
            self.parent.print_header()
            print("  🚗 AVAILABLE VEHICLES")
            print()
            self.parent.print_separator()
            print()
            
            if self.search_term:
                print(f"  Search: '{self.search_term}'")
            if self.current_category != "All":
                print(f"  Category: {self.current_category}")
            print()
            
            # Display vehicles in a grid
            vehicle_list = []
            for i, vehicle in enumerate(vehicles, 1):
                if hasattr(vehicle, 'keys'):
                    v = dict(vehicle)
                else:
                    # If it's a tuple, create a dict
                    v = {
                        'id': vehicle[0],
                        'make': vehicle[1],
                        'model': vehicle[2],
                        'year': vehicle[3],
                        'license_plate': vehicle[4],
                        'daily_rate': vehicle[5],
                        'status': vehicle[6],
                        'fuel_type': vehicle[7],
                        'mileage': vehicle[8],
                        'color': vehicle[9],
                        'min_rent_period': vehicle[10],
                        'max_rent_period': vehicle[11],
                        'category_name': vehicle[12],
                        'late_fee_rate': vehicle[13]
                    }
                
                vehicle_list.append(v)
                
                print(f"  {i}. 🚗 {v['make']} {v['model']} ({v['year']})")
                print(f"     License: {v['license_plate']}")
                print(f"     Category: {v['category_name'] or 'N/A'}")
                print(f"     Fuel: {v['fuel_type']} | Color: {v['color'] or 'N/A'}")
                print(f"     Mileage: {v['mileage']} km")
                print(f"     💰 Daily Rate: ${v['daily_rate']:.2f}")
                min_period = v['min_rent_period'] or 1
                max_period = v['max_rent_period'] or 30
                print(f"     📅 Min: {min_period} days | Max: {max_period} days")
                if v['late_fee_rate']:
                    print(f"     ⚠️ Late Fee: ${v['late_fee_rate']:.2f}/day")
                print()
            
            print(f"  Total: {len(vehicle_list)} vehicles available")
            print()
            self.parent.print_separator()
            print()
            
            # Option to book
            book_choice = self.parent.get_input("  Enter vehicle number to book, or 'b' to go back: ").strip()
            
            if book_choice.lower() == 'b':
                return
            
            try:
                vehicle_idx = int(book_choice) - 1
                if 0 <= vehicle_idx < len(vehicle_list):
                    vehicle_id = vehicle_list[vehicle_idx]['id']
                    self.booking_callback(vehicle_id)
                else:
                    self.parent.print_error("Invalid vehicle number!")
                    self.parent.get_input("\nPress Enter to continue...")
            except ValueError:
                self.parent.print_error("Invalid input!")
                self.parent.get_input("\nPress Enter to continue...")
                
        except Exception as e:
            self.parent.print_error(f"Error loading vehicles: {str(e)}")
            self.parent.get_input("\nPress Enter to continue...")