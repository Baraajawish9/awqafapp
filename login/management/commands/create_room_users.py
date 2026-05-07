from django.core.management.base import BaseCommand
from screen.models import ScreenSettings
from login.room_users import ROOM_USER_PASSWORD, ensure_room_users

class Command(BaseCommand):
    help = "Create/update room users with password '12345678' and no admin rights."

    def handle(self, *args, **kwargs):
        settings = ScreenSettings.get_settings()
        if not settings:
            self.stdout.write(self.style.ERROR("ScreenSettings not found."))
            return

        room_count = settings.room_count
        ensure_room_users(
            room_count,
            password=ROOM_USER_PASSWORD,
            stdout=self.stdout,
            style=self.style,
            reset_existing_password=True,
        )
