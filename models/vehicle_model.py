class VehicleModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        """Get all vehicles with category name"""
        query = """
            SELECT 
                v.id,
                v.category_id,
                v.make,
                v.model,
                v.year,
                v.license_plate,
                v.color,
                v.mileage,
                v.daily_rate,
                v.status,
                v.fuel_type,
                v.min_rent_period,
                v.max_rent_period,
                v.created_at,
                v.updated_at,
                c.name as category_name,
                c.base_rate as category_base_rate
            FROM vehicles v
            LEFT JOIN vehicle_categories c ON v.category_id = c.id
            ORDER BY v.make, v.model
        """
        return self.db.execute_query(query)

    def get_by_id(self, vehicle_id):
        """Get a single vehicle by ID"""
        query = """
            SELECT 
                v.*,
                c.name as category_name,
                c.base_rate as category_base_rate
            FROM vehicles v
            LEFT JOIN vehicle_categories c ON v.category_id = c.id
            WHERE v.id = ?
        """
        result = self.db.execute_query(query, (vehicle_id,))
        return result[0] if result else None

    def get_by_status(self, status):
        """Get vehicles by status"""
        query = """
            SELECT 
                v.*,
                c.name as category_name
            FROM vehicles v
            LEFT JOIN vehicle_categories c ON v.category_id = c.id
            WHERE v.status = ?
            ORDER BY v.make, v.model
        """
        return self.db.execute_query(query, (status,))

    def get_available_vehicles(self):
        """Get all available vehicles"""
        return self.get_by_status('available')

    def search(self, term):
        """Search vehicles by make, model, or license plate"""
        query = """
            SELECT 
                v.*,
                c.name as category_name
            FROM vehicles v
            LEFT JOIN vehicle_categories c ON v.category_id = c.id
            WHERE v.make LIKE ? 
               OR v.model LIKE ? 
               OR v.license_plate LIKE ?
            ORDER BY v.make, v.model
        """
        pattern = f"%{term}%"
        return self.db.execute_query(query, (pattern, pattern, pattern))

    def get_by_category(self, category_id):
        """Get vehicles by category"""
        query = """
            SELECT 
                v.*,
                c.name as category_name
            FROM vehicles v
            LEFT JOIN vehicle_categories c ON v.category_id = c.id
            WHERE v.category_id = ?
            ORDER BY v.make, v.model
        """
        return self.db.execute_query(query, (category_id,))

    def insert(self, data):
        """Insert a new vehicle"""
        query = """
            INSERT INTO vehicles (
                category_id, make, model, year, license_plate, 
                color, mileage, daily_rate, status, fuel_type,
                min_rent_period, max_rent_period
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (
            data['category_id'],
            data['make'],
            data['model'],
            data['year'],
            data['license_plate'],
            data['color'],
            data['mileage'],
            data['daily_rate'],
            data['status'],
            data['fuel_type'],
            data['min_rent_period'],
            data['max_rent_period']
        ))

    def update(self, vehicle_id, data):
        """Update an existing vehicle"""
        query = """
            UPDATE vehicles
            SET 
                category_id = ?,
                make = ?,
                model = ?,
                year = ?,
                license_plate = ?,
                color = ?,
                mileage = ?,
                daily_rate = ?,
                status = ?,
                fuel_type = ?,
                min_rent_period = ?,
                max_rent_period = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        return self.db.execute_query(query, (
            data['category_id'],
            data['make'],
            data['model'],
            data['year'],
            data['license_plate'],
            data['color'],
            data['mileage'],
            data['daily_rate'],
            data['status'],
            data['fuel_type'],
            data['min_rent_period'],
            data['max_rent_period'],
            vehicle_id
        ))

    def delete(self, vehicle_id):
        """Delete a vehicle by ID"""
        query = "DELETE FROM vehicles WHERE id = ?"
        return self.db.execute_query(query, (vehicle_id,))

    def update_status(self, vehicle_id, new_status):
        """Update vehicle status"""
        query = """
            UPDATE vehicles
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        return self.db.execute_query(query, (new_status, vehicle_id))

    def update_mileage(self, vehicle_id, new_mileage):
        """Update vehicle mileage"""
        query = """
            UPDATE vehicles
            SET mileage = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        return self.db.execute_query(query, (new_mileage, vehicle_id))

    def get_count_by_status(self):
        """Get count of vehicles by status"""
        query = """
            SELECT status, COUNT(*) as count
            FROM vehicles
            GROUP BY status
        """
        return self.db.execute_query(query)