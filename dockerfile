# FROM python base image
FROM python:3.11-slim

# App papkasiga o‘tish
WORKDIR /app

# Dependencies o‘rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodni nusxalash
COPY . .

# Portni ochish
EXPOSE 8000

# Uvicorn ishga tushurish
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]