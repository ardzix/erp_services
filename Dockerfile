# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    # Clean up to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN apt update && apt install -y \
    build-essential \
    binutils \
    libproj-dev \
    python3-gdal \
    python3-gdl \
    gdal-bin \
    net-tools 

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
# RUN python manage.py collectstatic --noinput

# Make port 8001 available to the world outside this container
EXPOSE 8001

# coppy local setting
RUN cp erp_backoffice/default_local_settings.py erp_backoffice/local_settings.py 

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "erp_backoffice.wsgi:application"]
