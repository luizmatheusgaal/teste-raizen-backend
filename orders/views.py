from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        order = self.get_object()
        if order.status == Order.Status.PAID:
            return Response({'msg': 'Pedido já pago.'}, status=status.HTTP_400_BAD_REQUEST)

        # Simulate payment gateway
        order.status = Order.Status.PAID
        order.payment_id = f'PAY-{order.pk:06d}'
        order.save(update_fields=['status', 'payment_id'])

        # Generate tickets
        from tickets.models import Ticket
        for item in order.items.all():
            for i in range(item.quantity):
                Ticket.objects.create(
                    ticket_type=item.ticket_type,
                    owner=order.user,
                    order=order,
                    code=f'{order.pk}-{item.ticket_type.pk}-{i+1:03d}',
                    price_paid=item.unit_price,
                    status=Ticket.Status.PAID,
                )

        return Response({'status': 'pago', 'order': OrderSerializer(order).data})
