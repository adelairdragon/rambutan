FROM python:3.12-slim

LABEL org.opencontainers.image.source=https://github.com/adelairdragon/rambutan

WORKDIR /app

COPY . /app

COPY config_example.toml /app/config.toml

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir gunicorn

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]