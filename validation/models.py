from django.db import models


class Validation(models.Model):
    class Result(models.TextChoices):
        VALID = 'valid', 'Válido'
        USED = 'used', 'Já utilizado'
        INVALID = 'invalid', 'Inválido'

    ticket = models.ForeignKey('tickets.Ticket', on_delete=models.CASCADE, related_name='validations')
    validator = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='validations')
    result = models.CharField(max_length=20, choices=Result.choices)
    message = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Validation {self.ticket.code} - {self.result}'
