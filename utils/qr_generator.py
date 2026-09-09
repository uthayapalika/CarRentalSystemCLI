import qrcode
import os
from datetime import datetime
import json


class QRCodeGenerator:
    """QR code generator for bookings, vehicles, and payments."""
    
    def __init__(self, output_dir="qr_codes"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_booking_qr(self, booking_data):
       
        qr_data = {
            'type': 'booking',
            'booking_ref': booking_data.get('booking_ref'),
            'vehicle': f"{booking_data.get('make', '')} {booking_data.get('model', '')}",
            'start_date': booking_data.get('start_date'),
            'end_date': booking_data.get('end_date'),
            'total_amount': float(booking_data.get('total_amount', 0)),
            'customer': f"{booking_data.get('first_name', '')} {booking_data.get('last_name', '')}"
        }
        
        qr_json = json.dumps(qr_data)
        
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_json)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        filename = f"booking_{booking_data.get('booking_ref')}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath)
        
        return filepath
    
    def generate_vehicle_qr(self, vehicle_data):
        
        qr_data = {
            'type': 'vehicle',
            'id': vehicle_data.get('id'),
            'make': vehicle_data.get('make'),
            'model': vehicle_data.get('model'),
            'year': vehicle_data.get('year'),
            'license_plate': vehicle_data.get('license_plate'),
            'daily_rate': float(vehicle_data.get('daily_rate', 0)),
            'fuel_type': vehicle_data.get('fuel_type'),
            'status': vehicle_data.get('status')
        }
        
        qr_json = json.dumps(qr_data)
        
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_json)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        filename = f"vehicle_{vehicle_data.get('id')}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath)
        
        return filepath
    
    def generate_payment_qr(self, payment_data):
        """
        Generate QR code for payment receipt
        
        """
        qr_data = {
            'type': 'payment',
            'transaction_ref': payment_data.get('transaction_reference'),
            'booking_ref': payment_data.get('booking_ref'),
            'amount': float(payment_data.get('amount', 0)),
            'payment_type': payment_data.get('payment_type'),
            'payment_status': payment_data.get('payment_status'),
            'payment_date': payment_data.get('payment_date')
        }
        
        qr_json = json.dumps(qr_data)
        
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_json)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        filename = f"payment_{payment_data.get('transaction_reference')}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath)
        
        return filepath
    
    def generate_qr_code_only(self, data, filename=None):
        """
        Generate a simple QR code with any data
       
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        if not filename:
            filename = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath)
        
        return filepath