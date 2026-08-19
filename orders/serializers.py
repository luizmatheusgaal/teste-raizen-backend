from rest_framework import serializers

from tickets.models import TicketType
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'ticket_type', 'quantity', 'unit_price', 'subtotal']

    def validate(self, data):
        ticket_type = data.get('ticket_type')
        quantity = data.get('quantity', 0)

        if quantity < 1:
            raise serializers.ValidationError('A quantidade deve ser pelo menos 1.')

        if ticket_type and quantity > ticket_type.available:
            raise serializers.ValidationError(
                f'Apenas {ticket_type.available} ingressos do tipo "{ticket_type.name}" estão disponíveis.'
            )

        if ticket_type and data.get('unit_price') != ticket_type.price:
            raise serializers.ValidationError(
                f'O preço unitário deve ser {ticket_type.price}.'
            )

        return data


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'items', 'payment_id', 'created_at', 'updated_at']
        read_only_fields = ['user', 'status', 'total']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('O pedido deve conter pelo menos um ingresso.')
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        order.recalculate_total()
        return order
