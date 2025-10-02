#!/bin/bash

# Exit on error
set -e

echo "Starting Development Environment..."

echo "Waiting for PostgreSQL..."
while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

# Run migrations
echo "Running migrations..."
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput

# Collect static files (optional in dev)
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || true

# Seed exercises if they don't exist
echo "Seeding exercises..."
python manage.py seed_exercises || true

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell << END
from django.contrib.auth.models import User
import os

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@dev.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'✅ Superuser {username} created successfully')
    print(f'📧 Email: {email}')
    print(f'🔑 Password: {password}')
else:
    print(f'ℹ️  Superuser {username} already exists')
END

echo ""
echo "Development server is ready!"
echo "API: http://localhost:8000"
echo "Admin: http://localhost:8000/admin"
echo "API Docs: http://localhost:8000/api/schema/swagger-ui/"
echo "PgAdmin: http://localhost:5050"
echo "Mailhog: http://localhost:8025"
echo ""
echo "Admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""

exec "$@"