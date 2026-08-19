from rest_framework import serializers

from .models import Category, Venue, Event


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['id', 'name', 'address', 'city', 'state', 'capacity']


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    venue = VenueSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    venue_id = serializers.PrimaryKeyRelatedField(
        queryset=Venue.objects.all(), source='venue', write_only=True
    )

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'venue',
            'category_id', 'venue_id', 'organizer', 'status',
            'starts_at', 'ends_at', 'min_age', 'info', 'created_at', 'updated_at'
        ]
        read_only_fields = ['organizer', 'created_at', 'updated_at']
