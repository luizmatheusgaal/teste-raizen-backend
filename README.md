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

## Celery e importação automática (Ticketmaster)

O projeto utiliza Celery com Redis para tarefas assíncronas. A tarefa `events.tasks.import_ticketmaster_events` busca 10 eventos no Brasil na API da Ticketmaster todos os dias às 6h.

```bash
# Subir Redis, worker e beat junto com a API
docker compose up -d

# Ou manualmente (com Redis local rodando)
celery -A verzel worker -l info
celery -A verzel beat -l info
```

Configure a chave da API no `.env`:

```env
TICKETMASTER_API_KEY=sua_chave_aqui
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

> **Nota:** a Vercel não suporta workers Celery contínuos. Para produção, use um serviço separado (Railway, Render, ECS, etc.) ou o agendamento de cron da Vercel apontando para um endpoint que dispara a tarefa.
