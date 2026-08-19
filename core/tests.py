from django.urls import reverse


def test_health_check(client):
    response = client.get(reverse('health-check'))
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_api_root(client):
    response = client.get(reverse('api-root'))
    assert response.status_code == 200
    assert 'health' in response.json()
