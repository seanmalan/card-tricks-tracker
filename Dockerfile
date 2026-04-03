FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies (no pywebview needed for server mode)
COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

# Copy app files
COPY app.py database.py server.py ./
COPY static/ ./static/

# Database lives in a mounted volume at /data
ENV DATA_DIR=/data

EXPOSE 5757

CMD ["python3", "server.py"]
