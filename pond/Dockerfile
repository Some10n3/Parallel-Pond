FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pond_mqtt.py .

CMD ["python", "pond_mqtt.py"]
