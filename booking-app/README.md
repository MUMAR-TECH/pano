# Booking Application

## Overview
This is a Django-based booking application that allows users to register as either customers or vendors. The application supports email authentication and social login options, providing a seamless experience for users to manage their profiles and bookings.

## Features
- User authentication via email and social login (Google, Facebook).
- User roles: Customers and Vendors.
- Profile management for users.
- Vendor dashboard for managing properties and bookings.
- Booking management system for users to view and manage their bookings.
- Property management for vendors to list their properties.

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd booking-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   python manage.py migrate
   ```

5. Create a superuser to access the admin panel:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

## Usage
- Access the application at `http://127.0.0.1:8000/`.
- Users can sign up, log in, and manage their profiles.
- Vendors can access their dashboard to manage properties and bookings.

## Templates
The application includes various templates for user authentication, profile management, and booking management, located in the `templates` directory.

## Static Files
Custom CSS and JavaScript files are located in the `static` directory.

## Media Files
Uploaded media files are stored in the `media` directory.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License.