# Trekking Management System

A web-based trekking management application built with Flask for managing treks, users, staff, and bookings. The project is designed for role-based access with three main users:

- Admin
- Staff
- Regular User

## Features

### Admin
- Manage users and staff accounts
- Approve or reject staff registrations
- Blacklist users
- Add, edit, view, and cancel treks
- View trek bookings
- Search users, staff, and treks

### Staff
- View assigned treks
- Update trek availability and status
- Start or complete treks
- Manage bookings for assigned treks
- Update staff profile

### User
- Register and log in
- Browse available treks
- Search and filter treks by name, difficulty, and status
- Book treks
- View personal bookings
- Update user profile

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- SQLite
- HTML, CSS, Jinja2 Templates

## Project Structure

- app.py - Main Flask application entry point
- application/controller.py - Application routes and business logic
- application/models.py - Database models
- application/database.py - SQLAlchemy database setup
- templates/ - HTML templates for the UI
- static/ - CSS and static assets

## Installation

1. Open the project folder
2. Create and activate a virtual environment

   On Windows:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```bash
   pip install flask flask-sqlalchemy flask-login
   ```

4. Run the application:
   ```bash
   python app.py
   ```

The app will create the SQLite database automatically on first run.

## Default Admin Account

On first launch, the application creates a default admin account:

- Email: admin@gmail.com
- Password: admin123

## Usage

- Open your browser and go to http://127.0.0.1:5000/
- Register a new user account or log in with the default admin credentials
- Use the dashboard based on your role

## Notes

- The database file is created as bytrek.sqlite3 in the project directory
- The app runs in debug mode during development

## License

This project is intended for academic or educational use.
