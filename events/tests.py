import pytest
from django.urls import reverse

from .models import Category, Venue, Event


@pytest.fixture
def category():
    return Category.objects.create(name='Show', slug='show')


@pytest.fixture
def venue():
    return Venue.objects.create(name='Arena Verzel', city='São Paulo', state='SP', capacity=5000)


@pytest.fixture
def event(category, venue, django_user_model):
    user = django_user_model.objects.create_user(email='org@example.com', username='org', password='123')
    return Event.objects.create(
        title='Festival Verano',
        description='Música independente',
        category=category,
        venue=venue,
        organizer=user,
        status='published',
        starts_at='2026-08-20T20:00:00Z',
    )


@pytest.mark.django_db
def test_list_events(client, event):
    response = client.get(reverse('event-list'))
    assert response.status_code == 200
    assert response.json()['count'] == 1


@pytest.mark.django_db
def test_retrieve_event(client, event):
    response = client.get(reverse('event-detail', kwargs={'pk': event.pk}))
    assert response.status_code == 200
    assert response.json()['title'] == 'Festival Verano'


@pytest.mark.django_db
def test_create_event_requires_auth(client, category, venue):
    response = client.post(reverse('event-list'), {
        'title': 'Novo Show',
        'description': 'Show novo',
        'category_id': category.pk,
        'venue_id': venue.pk,
        'starts_at': '2026-08-20T20:00:00Z',
    }, content_type='application/json')
    assert response.status_code == 401
