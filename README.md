
# SweeftDigital-test

## Description

This project is a Django web application for managing workouts, users, and fitness goals. It includes authentication, workout modules, and a RESTful API.

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Pro100Sergosha/SweeftDigital-test.git
cd SweeftDigital-test
```

### 2. Set up a virtual environment
It is recommended to use `venv`:
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate    # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply database migrations
```bash
python manage.py makemigrations

python manage.py migrate
```

### 5. Run the server
```bash
python manage.py runserver
```

---

## Docker (optional)

To run the project with Docker:
```bash
docker-compose up --build
```

---

## Testing

Run tests:
```bash
pytest
```

---

## API Documentation

After starting the server, API documentation is available at:
- **Swagger UI:** [`/api/docs/`](http://localhost:8000/api/docs/)
- **Redoc:** [`/api/redoc/`](http://localhost:8000/api/redoc/)

---

## Project Structure

- `apps/authentication/` — authentication and user management
- `apps/workout/` — workout logic, plans, exercises
- `config/settings/` — environment configuration (base, dev, prod)
- `tests/` — pytests

---

## Environment Variables

Create a `.env` file (if needed) and add:
```
DEBUG=True
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Contacts

Questions and suggestions: [Pro100Sergosha](https://github.com/Pro100Sergosha)
