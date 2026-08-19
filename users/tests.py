import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_register_user(client):
    response = client.post(reverse('register'), {
        'email': 'cliente@example.com',
        'username': 'cliente',
        'first_name': 'João',
        'last_name': 'Silva',
        'password': 'senhaSegura123',
        'role': 'client',
    }, content_type='application/json')
    assert response.status_code == 201
    assert 'token' in response.json()
    assert response.json()['user']['email'] == 'cliente@example.com'


@pytest.mark.django_db
def test_login_user(client, django_user_model):
    user = django_user_model.objects.create_user(
        email='joao@example.com',
        username='joao',
        password='senhaSegura123',
    )
    response = client.post(reverse('login'), {
        'username': user.email,
        'password': 'senhaSegura123',
    }, content_type='application/json')
    assert response.status_code == 200
    assert 'token' in response.json()
