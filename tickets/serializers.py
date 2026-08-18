from rest_framework import serializers

from .models import TicketType, Ticket


class TicketTypeSerializer(serializers.ModelSerializer):
    available = serializers.IntegerField(read_only=True)
    sold = serializers.IntegerField(read_only=True)

    class Meta:
        model = TicketType
        fields = ['id', 'event', 'name', 'price', 'capacity', 'available', 'sold', 'description']


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'ticket_type', 'owner', 'code', 'sector', 'seat', 'status', 'price_paid', 'created_at']
        read_only_fields = ['code', 'created_at']
