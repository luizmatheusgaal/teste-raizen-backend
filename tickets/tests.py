import pytest
from django.urls import reverse

from events.models import Category, Venue, Event
from tickets.models import TicketType, Ticket


@pytest.fixture
def event(django_user_model):
    category = Category.objects.create(name='Show', slug='show')
    venue = Venue.objects.create(name='Arena', city='SP', state='SP', capacity=1000)
    user = django_user_model.objects.create_user(email='org@example.com', username='org', password='123')
    return Event.objects.create(
        title='Show Test',
        description='Test',
        category=category,
        venue=venue,
        organizer=user,
        status='published',
        starts_at='2026-08-20T20:00:00Z',
    )


@pytest.fixture
def ticket_type(event):
    return TicketType.objects.create(event=event, name='Pista', price=100, capacity=500)


@pytest.mark.django_db
def test_list_ticket_types(client, ticket_type):
    response = client.get(reverse('tickettype-list'))
    assert response.status_code == 200
    assert response.json()['count'] == 1


@pytest.mark.django_db
def test_client_sees_only_own_tickets(client, django_user_model, ticket_type):
    owner = django_user_model.objects.create_user(email='client@example.com', username='client', password='123')
    Ticket.objects.create(ticket_type=ticket_type, owner=owner, code='T-001', price_paid=100)
    client.force_login(owner)
    response = client.get(reverse('ticket-list'))
    assert response.status_code == 200
    assert response.json()['count'] == 1
