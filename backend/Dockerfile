FROM python:3.10

WORKDIR /app

COPY requirements.txt .

# Установите зависимости с использованием pip
RUN pip install -r requirements.txt --no-cache-dir

COPY foodgram/ .



CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
