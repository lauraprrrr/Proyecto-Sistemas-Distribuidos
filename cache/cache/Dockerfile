FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY cache_app.py .
CMD ["python", "-u", "cache_app.py"]