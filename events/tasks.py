import logging
from decimal import Decimal

import requests
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import Category, Event, Venue
from tickets.models import TicketType

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def import_ticketmaster_events(self):
    api_key = settings.TICKETMASTER_API_KEY
    if not api_key:
        logger.warning('TICKETMASTER_API_KEY not configured.')
        return {'imported': 0, 'message': 'API key not configured.'}

    url = settings.TICKETMASTER_DISCOVERY_URL
    params = {
        'apikey': api_key,
        'countryCode': 'BR',
        'size': 10,
        'sort': 'date,asc',
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.exception('Ticketmaster API request failed')
        raise self.retry(exc=exc)

    data = response.json()
    events = data.get('_embedded', {}).get('events', [])

    imported = 0
    for tm_event in events:
        try:
            created = _import_event(tm_event)
            if created:
                imported += 1
        except Exception:
            logger.exception('Failed to import event: %s', tm_event.get('id'))

    return {'imported': imported}


def _import_event(tm_event):
    external_id = tm_event.get('id')
    if not external_id:
        return False

    if Event.objects.filter(title=tm_event.get('name'), starts_at=_parse_starts_at(tm_event)).exists():
        return False

    venue_data = _get_venue(tm_event)
    venue = _get_or_create_venue(venue_data)

    category_name = _get_category_name(tm_event)
    category = _get_or_create_category(category_name)

    organizer = _get_or_create_organizer()

    starts_at = _parse_starts_at(tm_event)
    if not starts_at:
        logger.warning('Event %s has no start date. Skipping.', external_id)
        return False

    event = Event.objects.create(
        title=tm_event.get('name', 'Evento sem título'),
        description=_build_description(tm_event),
        category=category,
        venue=venue,
        organizer=organizer,
        status=Event.Status.PUBLISHED,
        starts_at=starts_at,
        ends_at=_parse_ends_at(tm_event),
        min_age=_get_min_age(tm_event),
        info={
            'ticketmaster_id': external_id,
            'info': tm_event.get('info', ''),
            'pleaseNote': tm_event.get('pleaseNote', ''),
            'url': tm_event.get('url', ''),
        },
    )

    _create_ticket_type(event, tm_event)
    return True


def _get_venue(tm_event):
    venues = tm_event.get('_embedded', {}).get('venues', [])
    if venues:
        return venues[0]
    return {}


def _get_or_create_venue(venue_data):
    name = venue_data.get('name', 'Local não informado')
    defaults = {
        'address': venue_data.get('address', {}).get('line1', ''),
        'city': venue_data.get('city', {}).get('name', 'São Paulo'),
        'state': venue_data.get('state', {}).get('stateCode', 'SP'),
        'capacity': venue_data.get('capacity', 0) or 1000,
    }
    venue, _ = Venue.objects.get_or_create(name=name, defaults=defaults)
    return venue


def _get_category_name(tm_event):
    classifications = tm_event.get('classifications', [])
    if not classifications:
        return 'Show'
    segment = classifications[0].get('segment', {})
    genre = classifications[0].get('genre', {})
    return segment.get('name') or genre.get('name') or 'Show'


def _get_or_create_category(name):
    slug = name.lower().replace(' ', '-').replace('&', 'e')[:100]
    category, _ = Category.objects.get_or_create(
        slug=slug,
        defaults={'name': name},
    )
    return category


def _get_or_create_organizer():
    return User.objects.get_or_create(
        email='ticketmaster@verzel.local',
        defaults={
            'username': 'ticketmaster',
            'first_name': 'Ticketmaster',
            'last_name': 'Importer',
            'role': User.Role.ORGANIZER,
            'is_active': True,
        },
    )[0]


def _parse_starts_at(tm_event):
    dates = tm_event.get('dates', {})
    start = dates.get('start', {})
    date_time = start.get('dateTime')
    if date_time:
        dt = parse_datetime(date_time)
        return _ensure_aware(dt)

    local_date = start.get('localDate')
    local_time = start.get('localTime') or '00:00:00'
    if local_date:
        dt = parse_datetime(f'{local_date}T{local_time}')
        return _ensure_aware(dt)
    return None


def _parse_ends_at(tm_event):
    dates = tm_event.get('dates', {})
    end = dates.get('end', {})
    date_time = end.get('dateTime')
    if date_time:
        dt = parse_datetime(date_time)
        return _ensure_aware(dt)
    return None


def _ensure_aware(dt):
    if not dt:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone=timezone.get_default_timezone())
    return dt


def _build_description(tm_event):
    parts = [
        tm_event.get('info', ''),
        tm_event.get('pleaseNote', ''),
    ]
    return '\n\n'.join(p for p in parts if p).strip() or 'Evento importado da Ticketmaster.'


def _get_min_age(tm_event):
    age = tm_event.get('ageRestrictions', {}).get('legalAgeEnforced')
    return 18 if age else 0


def _create_ticket_type(event, tm_event):
    price = Decimal('0.00')
    price_ranges = tm_event.get('priceRanges', [])
    if price_ranges:
        min_price = price_ranges[0].get('min')
        if min_price is not None:
            price = Decimal(str(min_price))

    TicketType.objects.create(
        event=event,
        name='Geral',
        description='Ingresso geral importado da Ticketmaster.',
        price=price,
        capacity=event.venue.capacity,
    )
