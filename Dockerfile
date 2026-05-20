FROM python:3.11-slim
WORKDIR /app
# Install build tools needed for packages like ecos
RUN apt-get update && apt-get install -y gcc g++ build-essential libopenblas-dev curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir numpy==2.2.6
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt
RUN curl -o global-bundle.pem https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
COPY . .
CMD ["uvicorn","src.api.main:app","--host", "0.0.0.0", "--port", "8000"]
