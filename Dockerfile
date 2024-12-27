# Set the python version as a build-time argument with Python 3.12 as the default
ARG PYTHON_VERSION=3.12-slim-bullseye
FROM python:${PYTHON_VERSION}

# Upgrade pip and set environment variables
RUN pip install --upgrade pip
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libjpeg-dev \
    libcairo2 \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /code

# Copy requirements and install Python packages globally in the container
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Copy the Django project code into the container
COPY . /code

# Set project name as a build argument
ARG PROJ_NAME="cloth_store_api"
ENV DJANGO_PROJECT=${PROJ_NAME}

# Create a bash script to run Django commands at runtime
RUN printf "#!/bin/bash\n" > ./paracord_runner.sh && \
    printf "RUN_PORT=\"\${PORT:-8000}\"\n\n" >> ./paracord_runner.sh && \
    printf "python manage.py migrate --no-input\n" >> ./paracord_runner.sh && \
    printf "python manage.py collectstatic --noinput\n" >> ./paracord_runner.sh && \
    printf "gunicorn \${DJANGO_PROJECT}.wsgi:application --bind \"0.0.0.0:\$RUN_PORT\"\n" >> ./paracord_runner.sh

# Make the bash script executable
RUN chmod +x paracord_runner.sh

# Run the Django project via the runtime script when the container starts
CMD ./paracord_runner.sh
