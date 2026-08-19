from django.contrib import admin

from .models import Category, Venue, Event


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'capacity']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'venue', 'organizer', 'status', 'starts_at']
    list_filter = ['status', 'category', 'starts_at']
    search_fields = ['title', 'description']
