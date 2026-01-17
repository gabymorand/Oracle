#!/bin/bash
# Initialize database with Alembic migrations

echo "Waiting for database to be ready..."
sleep 5

echo "Creating initial migration..."
alembic revision --autogenerate -m "Initial migration"

echo "Running migrations..."
alembic upgrade head

echo "Database initialized successfully!"
