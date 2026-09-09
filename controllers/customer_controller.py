# controllers/customer_controller.py
import tkinter as tk
from tkinter import messagebox

class CustomerController:
    def __init__(self, view=None, model=None):
        self.view = view
        self.model = model
        
    def register_customer(self):
        """Handle customer registration"""
        if not self.view:
            print("Error: View is not set in customer controller!")
            return
            
        # Get data from view
        data = self.view.get_registration_data()
        
        # Validate required fields
        if not data['first_name']:
            self.view.show_error("First name is required!")
            return
        if not data['last_name']:
            self.view.show_error("Last name is required!")
            return
        if not data['email']:
            self.view.show_error("Email is required!")
            return
        if not data['phone']:
            self.view.show_error("Phone number is required!")
            return
        if not data['driver_license_num']:
            self.view.show_error("Driver license number is required!")
            return
        if not data['username']:
            self.view.show_error("Username is required!")
            return
        if not data['password']:
            self.view.show_error("Password is required!")
            return
        if len(data['password']) < 6:
            self.view.show_error("Password must be at least 6 characters!")
            return
        if data['password'] != data['confirm_password']:
            self.view.show_error("Passwords do not match!")
            return
        
        # Set loading state
        self.view.set_loading()
        
        # Register customer using model
        if self.model:
            try:
                success, customer_id, message = self.model.register_customer(data)
                
                if success:
                    self.view.show_success("Registration successful!")
                    messagebox.showinfo(
                        "Success", 
                        f"Account created successfully!\n\n"
                        f"Customer ID: {customer_id}\n"
                        f"Username: {data['username']}\n\n"
                        "You can now login with your credentials."
                    )
                    self.view.clear_fields()
                    
                    # Close registration and go to login after short delay
                    self.view.window.after(1500, self.go_to_login)
                else:
                    self.view.show_error(message)
                    messagebox.showerror("Registration Failed", message)
                    self.view.reset_loading()
                    
            except Exception as e:
                self.view.show_error(f"Registration error: {str(e)}")
                messagebox.showerror("Error", f"Registration failed: {str(e)}")
                self.view.reset_loading()
        else:
            self.view.show_error("Database connection failed!")
            self.view.reset_loading()

    def load_customers(self):
        """Load all customers into the table"""
        try:
            customers = self.model.get_all_customers()
            if self.view and hasattr(self.view, 'display_customers'):
                self.view.display_customers(customers)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load customers: {str(e)}")

    def delete_customer(self, customer_id):
        """Delete a customer and their user account"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this customer?\nThis will also delete their user account."):
            try:
                success, message = self.model.delete_customer(customer_id)
                if success:
                    messagebox.showinfo("Success", message)
                    self.load_customers()  # Refresh the table
                else:
                    messagebox.showerror("Error", message)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete customer: {str(e)}")

    def go_to_login(self):
        """Go back to login screen"""
        if self.view:
            # Close registration window
            self.view.window.destroy()
            self.view = None

    def set_view(self, view):
        """Set the view for this controller"""
        self.view = view

    def set_model(self, model):
        """Set the model for this controller"""
        self.model = model