FROM python:3.12-slim

WORKDIR /app
RUN useradd -m -u 10001 appuser
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
USER appuser
EXPOSE 8089
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8089/health')"
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8089"]
