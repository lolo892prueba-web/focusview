FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system deps for pyodbc (if using ODBC on Linux; optional on some PaaS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ unixodbc-dev build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app

ENV PORT=5000

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
