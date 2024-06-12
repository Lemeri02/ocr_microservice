FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    fonts-freefont-ttf

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY models /app/models
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
