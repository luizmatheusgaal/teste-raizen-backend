from django.db import models


class TicketType(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ['event', 'name']
        ordering = ['event', 'name']

    def __str__(self):
        return f'{self.event.title} - {self.name}'

    @property
    def sold(self):
        return self.tickets.filter(status__in=['reserved', 'paid']).count()

    @property
    def available(self):
        return self.capacity - self.sold


class Ticket(models.Model):
    class Status(models.TextChoices):
        RESERVED = 'reserved', 'Reservado'
        PAID = 'paid', 'Pago'
        USED = 'used', 'Utilizado'
        CANCELLED = 'cancelled', 'Cancelado'

    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name='tickets')
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='tickets', null=True, blank=True)
    code = models.CharField(max_length=50, unique=True)
    sector = models.CharField(max_length=100, blank=True)
    seat = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RESERVED)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.code
