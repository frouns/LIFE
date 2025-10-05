# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run uvicorn server
# The --host 0.0.0.0 is crucial to allow the container to accept connections from outside
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]