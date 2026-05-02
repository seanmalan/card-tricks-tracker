FROM python:3.12-slim

WORKDIR /app

# gosu lets us drop from root to a non-root user inside the entrypoint after
# fixing ownership of the bind-mounted data directory.
RUN apt-get update \
 && apt-get install -y --no-install-recommends gosu tzdata \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --system --gid 1000 app \
 && useradd  --system --uid 1000 --gid app --home /app --shell /usr/sbin/nologin app

# Default to NZ time so date.today() reflects the user's wall clock. Overridable
# via the TZ env var in docker-compose.yml.
ENV TZ=Pacific/Auckland

# Install Python dependencies (no pywebview needed for server mode)
COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

# Copy app files
COPY app.py database.py server.py seed.py ./
COPY static/ ./static/
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
 && chown -R app:app /app

# Database lives in a mounted volume at /data
ENV DATA_DIR=/data

EXPOSE 5757

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python3", "server.py"]
