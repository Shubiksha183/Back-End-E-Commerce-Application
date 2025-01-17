# Use an official Python base image with Alpine Linux
FROM python:3.10-slim


# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies for PostgreSQL and other libraries
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    cargo \
    make && \
    apt-get clean


# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the application code
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Add the .env file (optional, if needed during development)
COPY .env /app/

# Run the development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
