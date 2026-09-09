class VehicleCategoryModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        query = "SELECT * FROM vehicle_categories ORDER BY name"
        return self.db.execute_query(query)

    def get_by_id(self, category_id):
        query = "SELECT * FROM vehicle_categories WHERE id = ?"
        result = self.db.execute_query(query, (category_id,))
        return result[0] if result else None

    def search(self, term):
        query = """
            SELECT * FROM vehicle_categories
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY name
        """
        pattern = f"%{term}%"
        return self.db.execute_query(query, (pattern, pattern))

    def insert(self, name, description, base_rate, late_fee_rate, status):
        query = """
            INSERT INTO vehicle_categories
            (name, description, base_rate, late_fee_rate, category_status)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (name, description, base_rate, late_fee_rate, status))

    def update(self, category_id, name, description, base_rate, late_fee_rate, status):
        query = """
            UPDATE vehicle_categories
            SET name = ?, description = ?, base_rate = ?, late_fee_rate = ?,
                category_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        return self.db.execute_query(query, (name, description, base_rate, late_fee_rate, status, category_id))

    def delete(self, category_id):
        query = "DELETE FROM vehicle_categories WHERE id = ?"
        return self.db.execute_query(query, (category_id,))

    def toggle_status(self, category_id, new_status):
        query = """
            UPDATE vehicle_categories
            SET category_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        return self.db.execute_query(query, (new_status, category_id))