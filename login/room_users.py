import re

from django.contrib.auth.models import User


ROOM_USER_PASSWORD = '12345678'


def ensure_room_users(room_count, password=ROOM_USER_PASSWORD, stdout=None, style=None, reset_existing_password=False):
    for room_number in range(1, room_count + 1):
        for subroom in (1, 2):
            username = f'room{room_number}-{subroom}'
            user, created = User.objects.get_or_create(username=username)
            if created or reset_existing_password:
                user.set_password(password)
            user.is_staff = False
            user.is_superuser = False
            user.is_active = True
            user.save()

            if stdout:
                message = f"{'Created' if created else 'Updated'} user: {username}"
                formatter = style.SUCCESS if created else style.WARNING
                stdout.write(formatter(message))

    for user in User.objects.filter(username__startswith='room'):
        if re.fullmatch(r'room\d+', user.username.lower()):
            user.is_active = False
            user.set_unusable_password()
            user.save()
            if stdout:
                stdout.write(style.WARNING(f"Disabled plain room user: {user.username}"))
