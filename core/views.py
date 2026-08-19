from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok'})


@api_view(['GET'])
def api_root(request):
    return Response({
        'health': request.build_absolute_uri('health/'),
        'users': request.build_absolute_uri('users/'),
        'events': request.build_absolute_uri('events/'),
        'ticket_types': request.build_absolute_uri('ticket-types/'),
        'orders': request.build_absolute_uri('orders/'),
        'validate': request.build_absolute_uri('validate/'),
        'schema': request.build_absolute_uri('/api/schema/'),
        'docs': request.build_absolute_uri('/api/docs/'),
    })
