
FROM python:3.12-slim

# Defina o diretório de trabalho dentro do container
WORKDIR /app

RUN apt-get update -qq
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

# Instale as dependências do projeto
RUN poetry install

# Remova o cache do Poetry
RUN rm -rf $(poetry config cache-dir)

COPY ./rd_classification ./

RUN useradd -m nonrootuser
USER nonrootuser