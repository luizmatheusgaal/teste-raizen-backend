# Verzel Events - Backend

API RESTful Django para plataforma de eventos, ingressos e portaria.

## Tecnologias

- Django 6.x
- Django REST Framework
- PostgreSQL (via Docker)
- Docker e Docker Compose
- drf-spectacular (Swagger/OpenAPI)
- pytest-django

## Como executar

### Com Docker

```bash
docker compose up -d
```

A API estará disponível em `http://localhost:8000/api/v1/`.

Para recriar a imagem após mudanças:

```bash
docker compose up -d --build
```

### Localmente (desenvolvimento)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## Testes

```bash
# local
python -m pytest

# docker
docker compose --profile test run --rm test
```

## Endpoints principais

- `GET /api/v1/` - Raiz da API (lista endpoints)
- `GET /api/v1/health/` - Health check
- `POST /api/v1/users/register/` - Cadastro
- `POST /api/v1/users/login/` - Login
- `GET /api/v1/events/` - Eventos
- `GET /api/v1/ticket-types/` - Tipos de ingresso
- `POST /api/v1/orders/` - Criar pedido
- `POST /api/v1/orders/{id}/pay/` - Pagar pedido
- `POST /api/v1/validate/` - Validar ingresso
- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc
