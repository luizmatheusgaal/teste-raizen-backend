from django.contrib import admin

from .models import TicketType, Ticket


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'price', 'capacity', 'available', 'sold']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['code', 'ticket_type', 'owner', 'status', 'created_at']
    list_filter = ['status', 'ticket_type__event']
    search_fields = ['code', 'owner__email']
