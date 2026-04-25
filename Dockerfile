# Lab 13 Task 3.2: Dockerfile Implementation
FROM python:3.13.1

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Expose the default port (Port 8000 for the Gateway)
EXPOSE 8000

# Task 3.2 Start command: Migrate and then Run
# We use sh -c to allow multiple commands
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
