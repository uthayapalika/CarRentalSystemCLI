from models.customer_model import CustomerModel
from models.vehicle_model import VehicleModel
from models.booking_model import BookingModel
from models.payment_model import PaymentModel
from models.maintenance_model import MaintenanceModel
from models.vehicle_category_model import VehicleCategoryModel
from models.user_model import UserModel

class ModelFactory:
    """Factory Method for creating model instances"""
    
    @staticmethod
    def create_model(model_type,db=None):
       
        if model_type == "customer":
            return CustomerModel(db)
        elif model_type == "vehicle":
            return VehicleModel(db)
        elif model_type == "vehicle_category":
            return VehicleCategoryModel(db)
        elif model_type == "booking":
            return BookingModel(db)
        elif model_type == "payment":
            return PaymentModel(db)
        elif model_type == "maintenance":
            return MaintenanceModel(db)
        elif model_type == "user":
            return UserModel(db)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
