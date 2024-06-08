### Passo a Passo (Precisa ter o docker instalado)

## Primeiro acesso

# Vá até o terminal e rode os seguintes comandos:

1 - docker-compose up --build

# Crie um super usuário

docker compose run --rm app sh -c "python manage.py createsuperuser"

# Vá até o navegador e verifique a seguinte url:

http://localhost:8000/


## Demais acessos

# Vá até o terminal e rode o seguinte comando:

docker-compose up