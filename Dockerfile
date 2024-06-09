
FROM python:3.12-slim

# Defina o diretório de trabalho dentro do container
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential
RUN python3.12 -m pip install --upgrade pip

# Instale o Poetry
RUN pip install poetry

# Adicione Poetry ao PATH
ENV PATH="/root/.local/bin:${PATH}"

# Configure o Poetry para não criar um virtualenv
RUN poetry config virtualenvs.create false

WORKDIR /app

# Copie os arquivos de dependências para o diretório de trabalho
COPY pyproject.toml /app/ 
COPY poetry.lock /app/
COPY best_model.h5 /app/
COPY features.csv /app/
COPY ./pyradiomics-3.1.0 /app/pyradiomics-3.1.0

# Instale as dependências do projeto
RUN poetry install

# Instalando o tensorflow
RUN pip install tensorflow


# Instalando o pyradiomics
WORKDIR /app/pyradiomics-3.1.0
RUN pip install .
WORKDIR /app

# Remova o cache do Poetry
RUN rm -rf $(poetry config cache-dir)

COPY ./rd_classification ./

RUN useradd -m nonrootuser
USER nonrootuser