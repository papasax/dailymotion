# Stage 1: Builder
FROM python:3.14-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .
# Install dependencies into a local folder
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final Production Image
FROM python:3.14-slim

# Install ONLY the runtime library for PostgreSQL (no -dev)
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-privileged user for security
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

# Copy the installed packages from the builder stage
COPY --from=builder /install /usr/local
COPY . .

# Set permissions
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Use 'fastapi run' which is optimized for production
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]