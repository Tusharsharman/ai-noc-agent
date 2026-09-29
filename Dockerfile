FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY demo_app ./demo_app

EXPOSE 8001

CMD ["uvicorn", "demo_app.app:app", "--host", "0.0.0.0", "--port", "8001"]
