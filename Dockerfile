FROM python:3.14-slim

# libpq-dev is required for psycopg
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
