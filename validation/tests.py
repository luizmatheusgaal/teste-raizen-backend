import pytest
from decimal import Decimal
from django.urls import reverse

from events.models import Category, Venue, Event
from tickets.models import TicketType, Ticket
from orders.models import Order


@pytest.fixture
def paid_ticket(django_user_model):
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
    ticket_type = TicketType.objects.create(event=event, name='Pista', price=Decimal('120.00'), capacity=100)
    owner = django_user_model.objects.create_user(email='client@example.com', username='client', password='123')
    order = Order.objects.create(user=owner, status='paid', payment_id='PAY-001')
    return Ticket.objects.create(
        ticket_type=ticket_type,
        owner=owner,
        order=order,
        code='T-001',
        price_paid=ticket_type.price,
        status=Ticket.Status.PAID,
    )


@pytest.mark.django_db
def test_validate_paid_ticket(client, paid_ticket, django_user_model):
    validator = django_user_model.objects.create_user(email='door@example.com', username='door', password='123', role='door')
    client.force_login(validator)
    response = client.post(reverse('validate-ticket'), {'code': paid_ticket.code}, content_type='application/json')
    assert response.status_code == 200
    assert response.json()['valid'] is True
    paid_ticket.refresh_from_db()
    assert paid_ticket.status == Ticket.Status.USED


@pytest.mark.django_db
def test_validate_used_ticket_returns_error(client, paid_ticket, django_user_model):
    paid_ticket.status = Ticket.Status.USED
    paid_ticket.save()
    validator = django_user_model.objects.create_user(email='door@example.com', username='door', password='123', role='door')
    client.force_login(validator)
    response = client.post(reverse('validate-ticket'), {'code': paid_ticket.code}, content_type='application/json')
    assert response.status_code == 400
    assert response.json()['valid'] is False
