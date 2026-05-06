from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from screen.models import ScreenSettings
import re

class Command(BaseCommand):
    help = "Create/update room users with password '12345678' and no admin rights."

    def handle(self, *args, **kwargs):
        settings = ScreenSettings.get_settings()
        if not settings:
            self.stdout.write(self.style.ERROR("ScreenSettings not found."))
            return

        room_count = settings.room_count
        subroom_count = 2  # Or whatever max subrooms per room you want

        password = '12345678'

        for i in range(1, room_count + 1):
            for j in range(1, subroom_count + 1):
                username = f'room{i}-{j}'
                user, created = User.objects.get_or_create(username=username)
                user.set_password(password)
                user.is_staff = False
                user.is_superuser = False
                user.save()

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created user: {username}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Updated user: {username}"))  

        for user in User.objects.filter(username__startswith='room'):
            if re.fullmatch(r'room\d+', user.username.lower()):
                user.is_active = False
                user.set_unusable_password()
                user.save()
                self.stdout.write(self.style.WARNING(f"Disabled plain room user: {user.username}"))
