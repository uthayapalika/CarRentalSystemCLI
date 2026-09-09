# models/maintenance_model.py

class MaintenanceModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        """Get all maintenance records with vehicle info"""
        query = """
            SELECT 
                m.*,
                v.make,
                v.model,
                v.license_plate
            FROM maintenance m
            LEFT JOIN vehicles v ON m.vehicle_id = v.id
            ORDER BY m.service_date DESC
        """
        return self.db.execute_query(query)

    def get_by_vehicle(self, vehicle_id):
        """Get maintenance records for a specific vehicle"""
        query = """
            SELECT 
                m.*,
                v.make,
                v.model,
                v.license_plate
            FROM maintenance m
            LEFT JOIN vehicles v ON m.vehicle_id = v.id
            WHERE m.vehicle_id = ?
            ORDER BY m.service_date DESC
        """
        return self.db.execute_query(query, (vehicle_id,))

    def get_by_status(self, status):
        """Get maintenance records by status"""
        query = """
            SELECT 
                m.*,
                v.make,
                v.model,
                v.license_plate
            FROM maintenance m
            LEFT JOIN vehicles v ON m.vehicle_id = v.id
            WHERE m.status = ?
            ORDER BY m.service_date
        """
        return self.db.execute_query(query, (status,))

    def get_upcoming(self, days=30):
        """Get upcoming maintenance within specified days"""
        query = """
            SELECT 
                m.*,
                v.make,
                v.model,
                v.license_plate
            FROM maintenance m
            LEFT JOIN vehicles v ON m.vehicle_id = v.id
            WHERE m.next_service_due BETWEEN DATE('now') 
                AND DATE('now', '+{} days')
                AND m.status = 'pending'
            ORDER BY m.next_service_due
        """.format(days)
        return self.db.execute_query(query)

    def insert(self, data):
        """Insert a new maintenance record"""
        query = """
            INSERT INTO maintenance (
                vehicle_id, maintenance_type, service_date, odometer_reading,
                cost, service_provider, description, status, next_service_due
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (
            data['vehicle_id'],
            data['maintenance_type'],
            data['service_date'],
            data.get('odometer_reading', 0),
            data.get('cost', 0),
            data.get('service_provider', ''),
            data.get('description', ''),
            data.get('status', 'pending'),
            data.get('next_service_due')
        ))

    def update(self, maintenance_id, data):
        """Update an existing maintenance record"""
        query = """
            UPDATE maintenance
            SET 
                maintenance_type = ?,
                service_date = ?,
                odometer_reading = ?,
                cost = ?,
                service_provider = ?,
                description = ?,
                status = ?,
                next_service_due = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE maintenance_id = ?
        """
        return self.db.execute_query(query, (
            data['maintenance_type'],
            data['service_date'],
            data.get('odometer_reading', 0),
            data.get('cost', 0),
            data.get('service_provider', ''),
            data.get('description', ''),
            data['status'],
            data.get('next_service_due'),
            maintenance_id
        ))

    def update_status(self, maintenance_id, new_status):
        """Update maintenance status"""
        query = """
            UPDATE maintenance
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE maintenance_id = ?
        """
        return self.db.execute_query(query, (new_status, maintenance_id))

    def delete(self, maintenance_id):
        """Delete a maintenance record"""
        query = "DELETE FROM maintenance WHERE maintenance_id = ?"
        return self.db.execute_query(query, (maintenance_id,))

    def get_statistics(self):
        """Get maintenance statistics"""
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(cost) as total_cost,
                AVG(cost) as avg_cost
            FROM maintenance
        """
        result = self.db.execute_query(query)
        return result[0] if result else None