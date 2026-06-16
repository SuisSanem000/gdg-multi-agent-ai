FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY src/ src/

# Expose default port
EXPOSE 8080

# Run Flask using production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "src.app:app"]
