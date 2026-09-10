# Car Rental System (CLI Edition)

The **Car Rental System v1.0.0** is a lightweight desktop application developed using **Python and SQLite**, operated entirely through a **Command Line Interface (CLI)**. It provides a simple, structured, menu-driven interface for managing day-to-day car rental operations.

The system reduces manual paperwork, improves data management, and helps make vehicle rental activities faster, more organized, and efficient.

---

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [User Roles and Access](#user-roles-and-access)
* [Technical Features](#technical-features)
* [System Requirements](#system-requirements)
* [Installation Guide](#installation-guide)
* [Operating the System](#operating-the-system)
* [File Structure and Purpose](#file-structure-and-purpose)
* [Database](#database)
* [Versioning](#versioning)
* [Known Issues and Limitations](#known-issues-and-limitations)
* [Troubleshooting](#troubleshooting)
* [License](#license)
* [Credits](#credits)
* [Technologies](#technologies)
* [Support and Future Improvements](#support-and-future-improvements)
* [Project Status](#project-status)

---

## Overview

**Car Rental System v1.0.0** is a Windows-based desktop application, operated through a **Command Line Interface**, designed to manage common car rental activities through a centralized system.

The current release provides **role-based access control** with four user roles:

* **Administrator**
* **Manager**
* **Staff**
* **Customer**

The application uses **SQLite**, so no separate database server is required. User passwords are securely stored using **bcrypt password hashing**.

### Key Benefits

* Easy installation and setup
* No separate database server required
* Role-based access control
* Secure password hashing
* Lightweight, terminal-based desktop application
* Centralized rental information
* Database backup functionality
* Application logging
* Version management

---

## Features

### Authentication and Security

* User login and authentication via CLI prompts
* Role-based access control (RBAC)
* Four user roles
* Secure password hashing using bcrypt
* Access restrictions based on user roles
* Login validation

### Vehicle Management

* Add and manage vehicles
* Manage vehicle categories
* View vehicle information
* Track vehicle availability
* Manage vehicle maintenance records

### Customer Management

* Customer registration
* Customer information management
* Customer booking information
* Customer access through a dedicated CLI dashboard menu

### Booking Management

* Create and manage bookings
* View booking information
* Manage rental operations
* Track customer bookings
* Vehicle availability management

### Payment Management

* Record rental payments
* View payment information
* Manage payment records
* Customer payment information

### Additional Features

* QR code generation
* Database backup
* Application logging
* Version management
* SQLite database
* MVC-style application architecture

---

## User Roles and Access

The system provides four levels of role-based access.

### Administrator

The Administrator has full access to the system, including:

* Manage users
* Manage vehicles
* Manage vehicle categories
* Manage customers
* Manage bookings
* Manage payments
* Manage maintenance records
* Access administrative functions

### Manager

The Manager can manage major rental operations, including:

* Manage vehicles
* Manage vehicle categories
* Manage bookings
* Manage payments
* Manage maintenance records
* View customer information

### Staff

Staff members have limited operational access, including:

* View bookings
* View payments
* View maintenance information
* View customer information
* Perform permitted rental operations

### Customer

Customers can access customer-specific functionality, including:

* Customer login
* View available rental information
* Make bookings
* View booking information
* View payment information

> **Note:** Access permissions are controlled by the application's role-based access control logic.

---

## Technical Features

* **Python** – Application programming language
* **CLI (Command Line Interface)** – User interaction layer
* **SQLite** – Local database
* **bcrypt** – Secure password hashing
* **MVC-style Architecture** – Separation of application responsibilities
* **Factory Method** – Centralized model creation
* **QR Code** – QR code generation
* **Git** – Version control
* **Logging** – Application activity and error logging
* **Database Backup** – Local database backup functionality
* **PyInstaller** – Packaging the application into a standalone Windows `.exe`

---

## System Requirements

### Minimum Requirements

* Windows 10 or later
* Python 3.10 or later
* 500 MB or more available disk space
* Internet connection for initial dependency installation
* Git (optional)
* Virtual environment (recommended)

---

## Installation Guide

### Step 1 – Install Python

Download and install Python from the official Python website.

During installation, make sure:

```text
Add Python to PATH
```

is selected.

Verify the installation:

```bash
python --version
```

---

### Step 2 – Clone the Repository

The project can be downloaded as a ZIP file or cloned using Git.

```bash
git clone https://github.com/uthayapalika/CarRentalSystemCLI.git
```

Move into the project directory:

```bash
cd CarRentalSystemCLI
```

---

### Step 3 – Create a Virtual Environment

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

---

### Step 4 – Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

### Step 5 – Initialize the Database

If the database has not already been created, run:

```bash
python db_setup.py
```

This initializes the SQLite database (`car_rental_system.db`) required by the application.

---

### Step 6 – Run the Application

Start the application using:

```bash
python main.py
```

The CLI login menu should appear in your terminal.

---

## Operating the System

### Administrator

The Administrator can access the complete system functionality.

Typical operations include:

1. Log in using administrator credentials.
2. Manage system users.
3. Manage vehicles.
4. Manage vehicle categories.
5. Manage customers.
6. Manage bookings.
7. Manage payments.
8. Manage vehicle maintenance.

---

### Manager

The Manager can perform operational management activities.

Typical operations include:

1. Log in using manager credentials.
2. View and manage vehicles.
3. Manage vehicle categories.
4. Manage bookings.
5. Manage payments.
6. Manage maintenance records.
7. Review customer information.

---

### Staff

Staff users have restricted operational access.

Typical operations include:

1. Log in using staff credentials.
2. View bookings.
3. View payment information.
4. View maintenance information.
5. Perform permitted customer and rental operations.

---

### Customer

Customers use a separate CLI menu after login.

Typical operations include:

1. Register as a customer.
2. Log in to the system.
3. View available rental information.
4. Make a booking.
5. View booking information.
6. View payment information.

---

## File Structure and Purpose

```text
Car-Rental-System-CLI/
│
├── README.md
├── LICENSE
├── requirements.txt
├── db_setup.py
├── main.py
├── version.py
├── version.txt
├── backup_database.py
├── factories.py
├── logger.py
├── debug_main.py
├── test_minimal.py
├── CHANGELOG.md
├── car_rental_system.db
├── car_rental_system.log
├── main.spec
│
├── controllers/
│   ├── __init__.py
│   ├── login_controller.py
│   ├── registration_controller.py
│   ├── vehicle_category_controller.py
│   ├── vehicle_controller.py
│   ├── booking_controller.py
│   └── payment_controller.py
│
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── vehicle.py
│   ├── vehicle_category.py
│   ├── booking.py
│   ├── payment.py
│   ├── maintenance.py
│   └── customer.py
│
├── views/
│   ├── login_view_cli.py
│   ├── registration_view_cli.py
│   ├── main_dashboard_cli.py
│   ├── customer_dashboard_cli.py
│   ├── customer_view_cli.py
│   ├── employee_view_cli.py
│   ├── booking_view_cli.py
│   ├── customer_payment_cli.py
│   ├── maintenance_view_cli.py
│   └── qr_view_cli.py
│
├── utils/
│   └── (shared helper/validation functions)
│
├── qr_codes/
│   └── (generated QR code images)
│
├── backups/
│   └── (database backup files)
│
├── dist/
│   └── CarRentalSystem/
│       ├── CarRentalSystem.exe
│       ├── car_rental_system.db
│       └── ...
│
└── build/
    └── ...
```

### Directory and File Description

| File / Directory        | Purpose                                                        |
| ------------------------ | --------------------------------------------------------------- |
| `main.py`                | CLI application entry point                                     |
| `db_setup.py`             | Initializes the SQLite database                                 |
| `version.py` / `version.txt` | Stores application version information                     |
| `backup_database.py`     | Creates database backups                                        |
| `factories.py`            | Implements centralized model creation using the Factory Method  |
| `logger.py`               | Configures application-wide error logging                       |
| `debug_main.py`           | Development/debugging entry point                                |
| `test_minimal.py`         | Minimal automated test(s) for core functionality                |
| `CHANGELOG.md`            | Records changes between application versions                    |
| `controllers/`            | Contains application and business logic (MVC Controller layer)  |
| `models/`                 | Contains database models and database operations (MVC Model layer) |
| `views/`                  | Contains CLI menu/screen components (MVC View layer)             |
| `utils/`                  | Contains reusable helper/validation functions                    |
| `qr_codes/`                | Stores QR code images generated for bookings/vehicles            |
| `backups/`                 | Stores database backup files created by `backup_database.py`    |
| `dist/`                    | Contains the packaged standalone `.exe` release                 |
| `build/`                   | Temporary files generated during the PyInstaller build process  |
| `requirements.txt`         | Lists Python dependencies                                       |
| `car_rental_system.db`     | Local SQLite database storing all application data              |
| `car_rental_system.log`    | Stores application log information                               |
| `main.spec`                | PyInstaller build specification file                             |

> **Note:** The `build/` directory contains temporary build files and normally does not need to be included in the GitHub release package.

---

## Database

The application uses **SQLite** as its local database.

SQLite was selected because:

* No database server installation is required
* The database is stored locally
* It is lightweight
* It is suitable for a small desktop application
* It is easy to back up and restore

### Main Data Areas

The database manages information related to:

* Users
* Customers
* Vehicles
* Vehicle categories
* Bookings
* Payments
* Maintenance records

The database is automatically used by the application and does not require a separate database server.

> **Important for the compiled `.exe`:** `car_rental_system.db` must be placed in the same folder as `CarRentalSystem.exe`. It is not bundled inside the executable — see [Known Issues and Limitations](#known-issues-and-limitations).

---

## Versioning

The project uses **Git** for source-code version control and follows a release-based versioning approach.

### Current Version

```text
v1.0.0
```

### Version Format

The project follows the general:

```text
MAJOR.MINOR.PATCH
```

format.

Example:

```text
v1.0.0
v1.1.0
v1.1.1
v2.0.0
```

Major versions may introduce significant changes, while minor and patch versions are used for new features, improvements, and bug fixes.

---

## Known Issues and Limitations

### 1. Database and log file path resolution in the compiled `.exe`

When packaged into a one-file executable using PyInstaller, Python's `__file__` variable resolves to a temporary extraction folder rather than the folder containing the actual `.exe`. If left unhandled, this can cause the application to fail to locate `car_rental_system.db`, or write logs to a temporary location that is deleted after the program closes.

**Fix applied:** Path resolution checks whether the app is running as a frozen executable (`sys.frozen`) and, if so, uses the folder containing `sys.executable` instead of `__file__`, ensuring the database and log file are read from/written to the folder where the `.exe` is located.

**Workaround if using an older build:** Manually copy `car_rental_system.db` into the same folder as `CarRentalSystem.exe` before running it.

### 2. Features not yet implemented (v1.0.0)

* Password reset functionality
* Email notification functionality
* Online/cloud database support
* Online payment integration
* Advanced reporting
* Vehicle availability calendar
* Additional customer booking history features

These features are planned for future releases.

---

## Troubleshooting

### Application does not start

Make sure Python is installed:

```bash
python --version
```

Then activate the virtual environment:

```bash
venv\Scripts\activate
```

Install the dependencies again:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python main.py
```

### Database Error

If the database has not been initialized, run:

```bash
python db_setup.py
```

Make sure the SQLite database file is located in the expected application directory (next to `main.py`, or next to `CarRentalSystem.exe` when using the compiled build).

### Login Problems

Check that:

* The username is correct.
* The password is correct.
* The user account exists in the database.
* The user has an assigned role.
* The database is accessible.

### Application Log

Application errors and events can be checked in:

```text
car_rental_system.log
```

---

## License

This project is licensed under the **MIT License**.

```text
MIT License

Copyright (c) 2026 Uthaya Palika Naganathan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Credits

### Developer

**Uthaya Palika Naganathan**

**Role:** Software Developer

**Email:** [uthayapalika@gmail.com](mailto:uthayapalika@gmail.com)

**GitHub:** [@uthayapalika](https://github.com/uthayapalika/CarRentalSystemCLI)

**LinkedIn:** [www.linkedin.com/in/uthayapalika-naganathan-13a1159b](http://www.linkedin.com/in/uthayapalika-naganathan-13a1159b)

---

## Technologies

* Python
* CLI (Command Line Interface)
* SQLite
* bcrypt
* qrcode
* Git
* PyInstaller
* MVC-style Architecture
* Factory Method Design Pattern

---

## Support and Future Improvements

Future versions may include:

* Advanced reporting and analytics
* Automated database backup
* Improved role-based permissions
* Email notifications
* Online payment integration
* Vehicle availability calendar
* Enhanced customer booking history
* Password reset functionality
* Cloud database support
* Improved system monitoring
* Additional security enhancements

---

## Project Status

**Current Release:** `v1.0.0`

**Application Type:** Windows Desktop Application (CLI)

**Architecture:** MVC-style

**Database:** SQLite

**Status:** Initial Release

---

**Car Rental System © 2026 Uthaya Palika Naganathan**
