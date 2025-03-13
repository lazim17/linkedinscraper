FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    firefox-esr \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q "https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-linux64.tar.gz" \
    && tar -xzf geckodriver-linux64.tar.gz -C /usr/local/bin \
    && rm geckodriver-linux64.tar.gz

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
