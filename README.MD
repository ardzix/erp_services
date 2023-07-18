# Django REST Framework App

This is a Django app built with Django REST Framework.

## Installation:
1. Clone the repository:
   `git clone git@github.com:ardzix/erp_services.git`

2. Create and activate a virtual environment:
   - `python -m venv venv`
   - `source venv/bin/activate`

3. Install the required packages:
   `pip install -r requirements.txt`

4. Apply database migrations:
   `python manage.py migrate`

## Running the App:
To run the Django app, execute the following command:
`python manage.py runserver`

The app will be accessible at http://localhost:8000/.

## API Endpoints:
- Login: /api/auth/login/ (POST)
  - Request Body: username and password
  - Response: Authentication token

- Devices: /api/devices/ (GET, POST)
  - Get all devices or create a new device

- Device Detail: /api/devices/{id}/ (GET, PUT, PATCH, DELETE)
  - Get, update, or delete a specific device

- Tracking: /api/tracking/ (GET)
  - Get the list of tracked devices with their last update and current coordinate

## Administration:
To access the Django admin interface, go to /admin/ in your browser.

## API Documentation:
API documentation is available using Swagger and ReDoc:
- Swagger UI: /swagger/
- ReDoc: /redoc/
