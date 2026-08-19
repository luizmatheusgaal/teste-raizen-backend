import pytest
from decimal import Decimal
from django.urls import reverse

from events.models import Category, Venue, Event
from orders.models import Order
from tickets.models import TicketType, Ticket


@pytest.fixture
def client_user(client, django_user_model):
    response = client.post(reverse('register'), {
        'email': 'client@example.com',
        'username': 'client',
        'first_name': 'João',
        'last_name': 'Silva',
        'password': 'senhaSegura123',
        'role': 'client',
    }, content_type='application/json')
    return django_user_model.objects.get(email='client@example.com')


@pytest.fixture
def organizer_user(django_user_model):
    return django_user_model.objects.create_user(
        email='org@example.com',
        username='org',
        password='123',
        role='organizer',
    )


@pytest.fixture
def event(organizer_user):
    category = Category.objects.create(name='Festival', slug='festival')
    venue = Venue.objects.create(name='Arena Verzel', city='São Paulo', state='SP', capacity=5000)
    return Event.objects.create(
        title='Festival Verzel',
        description='Música ao vivo',
        category=category,
        venue=venue,
        organizer=organizer_user,
        status='published',
        starts_at='2026-08-20T20:00:00Z',
    )


@pytest.fixture
def ticket_type(event):
    return TicketType.objects.create(event=event, name='Pista', price=Decimal('150.00'), capacity=1000)


@pytest.mark.django_db
def test_full_purchase_and_validation_flow(client, client_user, ticket_type, django_user_model):
    # Client creates an order
    client.force_login(client_user)
    response = client.post(reverse('order-list'), {
        'items': [{'ticket_type': ticket_type.pk, 'quantity': 2, 'unit_price': '150.00'}]
    }, content_type='application/json')
    assert response.status_code == 201
    order_id = response.json()['id']

    # Pays the order
    response = client.post(reverse('order-pay', kwargs={'pk': order_id}))
    assert response.status_code == 200
    assert response.json()['status'] == 'pago'

    # Two tickets generated
    order = Order.objects.get(pk=order_id)
    assert order.tickets.count() == 2
    ticket = order.tickets.first()
    assert ticket.status == Ticket.Status.PAID

    # Door validation
    door = django_user_model.objects.create_user(
        email='door@example.com',
        username='door',
        password='123',
        role='door',
    )
    client.force_login(door)
    response = client.post(reverse('validate-ticket'), {'code': ticket.code}, content_type='application/json')
    assert response.status_code == 200
    assert response.json()['valid'] is True

    ticket.refresh_from_db()
    assert ticket.status == Ticket.Status.USED

    # Second validation fails
    response = client.post(reverse('validate-ticket'), {'code': ticket.code}, content_type='application/json')
    assert response.status_code == 400
    assert response.json()['valid'] is False
