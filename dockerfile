# Use official Python image
FROM python:3.10-slim-bullseye

# Set working directory
WORKDIR /app

# Copy requirements and app code
COPY requirements.txt ./
COPY app.py ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on
EXPOSE 3978

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=3978

# Start the Flask app
CMD ["gunicorn", "app:app", "--bind=0.0.0.0:3978"]