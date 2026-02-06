FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install test tools 
RUN pip install --no-cache-dir -U pip "pytest>=8"

# Copy repo
COPY . .

CMD ["pytest", "-q"]
