FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY parsers ./parsers
COPY docker-entrypoint.sh ./
RUN chmod +x /app/docker-entrypoint.sh \
    && mkdir -p /data/resources \
    && chown -R 1000:1000 /data

USER 1000:1000
WORKDIR /data
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "-m", "src"]
