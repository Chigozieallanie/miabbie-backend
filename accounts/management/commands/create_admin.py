from decouple import config
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Creates a superuser from DJANGO_SUPERUSER_* env vars, if one with that email does not already exist.'

    def handle(self, *args, **options):
        email = config('DJANGO_SUPERUSER_EMAIL', default=None)
        phone = config('DJANGO_SUPERUSER_PHONE', default='')
        password = config('DJANGO_SUPERUSER_PASSWORD', default=None)

        if not email or not password:
            self.stdout.write('DJANGO_SUPERUSER_EMAIL/PASSWORD not set — skipping.')
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(f'Superuser "{email}" already exists — skipping.')
            return

        User.objects.create_superuser(email=email, phone=phone, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superuser "{email}" created.'))