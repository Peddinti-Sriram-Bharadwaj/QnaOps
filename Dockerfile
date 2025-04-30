FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code AND the static directory
COPY ./app /app/app
COPY ./static /app/static  

# Expose port and define command (as before)
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

