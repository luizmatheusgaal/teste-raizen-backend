import pytest
from decimal import Decimal
from django.urls import reverse

from events.models import Category, Venue, Event
from orders.models import Order
from tickets.models import TicketType


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(email='client@example.com', username='client', password='123')


@pytest.fixture
def ticket_type(django_user_model):
    category = Category.objects.create(name='Show', slug='show')
    venue = Venue.objects.create(name='Arena', city='SP', state='SP', capacity=1000)
    organizer = django_user_model.objects.create_user(email='org@example.com', username='org', password='123')
    event = Event.objects.create(
        title='Show',
        description='Show',
        category=category,
        venue=venue,
        organizer=organizer,
        status='published',
        starts_at='2026-08-20T20:00:00Z',
    )
    return TicketType.objects.create(event=event, name='Pista', price=Decimal('120.00'), capacity=100)


@pytest.mark.django_db
def test_create_order(client, user, ticket_type):
    client.force_login(user)
    response = client.post(reverse('order-list'), {
        'items': [{'ticket_type': ticket_type.pk, 'quantity': 2, 'unit_price': '120.00'}]
    }, content_type='application/json')
    assert response.status_code == 201
    assert response.json()['total'] == '240.00'


@pytest.mark.django_db
def test_pay_order_generates_tickets(client, user, ticket_type):
    client.force_login(user)
    order = Order.objects.create(user=user, status='pending')
    order.items.create(ticket_type=ticket_type, quantity=2, unit_price=ticket_type.price)
    order.recalculate_total()

    response = client.post(reverse('order-pay', kwargs={'pk': order.pk}))
    assert response.status_code == 200
    assert response.json()['status'] == 'pago'
    assert order.tickets.count() == 2
