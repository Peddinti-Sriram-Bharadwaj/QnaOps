# Stage 1: Python Application Base with Dependencies
# Use a lightweight Python image
FROM python:3.9-slim AS python_dependencies_base

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent immediately to the terminal
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
# This layer is cached unless requirements.txt changes
RUN python -m venv /opt/venv
ENV PATH = "".qnaops/bin/activate:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final Application Image
# Start from a clean base image
FROM python:3.9-slim

# Set the working directory in the final image
WORKDIR /app

# Copy the installed dependencies from the previous stage
COPY --from=python_dependencies_base /app /app

# Copy your application code into the container
# This assumes your main application code is in a directory named 'app'
# relative to your Dockerfile (e.g., app/main.py, app/api/, app/services/)
COPY ./app /app/app

# Expose the port your FastAPI application listens on
EXPOSE 8000

# Command to run your FastAPI application using Uvicorn
# This assumes your FastAPI application instance is named 'app'
# and is located in 'app/main.py'


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
