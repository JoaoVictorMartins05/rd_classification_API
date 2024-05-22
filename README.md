## Passo a Passo (Precisa ter o docker instalado)

# Vá até o terminal e rode os seguintes comandos:

1 - docker-compose up --build

# Vá até o navegador e verifique a seguinte url:

http://localhost:8000/

# Crie um super usuário

docker compose run --rm app sh -c "python manage.py createsuperuser"