from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from tickets.models import Ticket
from .models import Validation


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_ticket(request):
    code = request.data.get('code')
    try:
        ticket = Ticket.objects.get(code=code)
    except Ticket.DoesNotExist:
        Validation.objects.create(
            ticket=None,
            validator=request.user,
            result=Validation.Result.INVALID,
            message='Ingresso não encontrado',
        )
        return Response({'valid': False, 'message': 'Ingresso não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if ticket.status == Ticket.Status.USED:
        Validation.objects.create(
            ticket=ticket,
            validator=request.user,
            result=Validation.Result.USED,
            message='Ingresso já utilizado',
        )
        return Response({'valid': False, 'message': 'Ingresso já utilizado.'}, status=status.HTTP_400_BAD_REQUEST)

    if ticket.status != Ticket.Status.PAID:
        Validation.objects.create(
            ticket=ticket,
            validator=request.user,
            result=Validation.Result.INVALID,
            message='Ingresso não pago',
        )
        return Response({'valid': False, 'message': 'Ingresso não pago.'}, status=status.HTTP_400_BAD_REQUEST)

    ticket.status = Ticket.Status.USED
    ticket.save(update_fields=['status'])
    Validation.objects.create(
        ticket=ticket,
        validator=request.user,
        result=Validation.Result.VALID,
        message='Ingresso validado com sucesso',
    )

    return Response({
        'valid': True,
        'message': 'Ingresso validado com sucesso.',
        'ticket': {
            'code': ticket.code,
            'event': ticket.ticket_type.event.title,
            'type': ticket.ticket_type.name,
            'owner': ticket.owner.email if ticket.owner else None,
        }
    })
