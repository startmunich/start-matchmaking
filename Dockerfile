# Use a more robust Python image that includes build tools
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies one by one
RUN while read requirement; do pip install --no-cache-dir -v $requirement; done < requirements.txt

# Copy the rest of the application code
COPY . .

# Specify the command to run your application
CMD ["python", "main.py"]