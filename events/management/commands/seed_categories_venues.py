from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed categories and venues from fixtures'

    def handle(self, *args, **options):
        call_command('loaddata', 'categories_venues.json', app_label='events')
        self.stdout.write(self.style.SUCCESS('Categorias e locais carregados com sucesso.'))
