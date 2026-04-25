FROM python:3.12-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo
WORKDIR /app

# Instala solo gcc si alguna dependencia lo requiere (como `boto3` si compila algo con C, pero normalmente no es necesario)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*



# Copia el archivo de requerimientos e instala las dependencias
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copia el código de la aplicación
COPY ./app /app/app

# Establece el PYTHONPATH para que puedas importar desde "app"
ENV PYTHONPATH="${PYTHONPATH}:/app/app"

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:api", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
