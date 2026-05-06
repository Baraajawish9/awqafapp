# myapp/middleware.py

import re

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import resolve, reverse
from screen.models import Student

class RoomAccessMiddleware:
    """
    Restrict access to room pages and mark_student only for the authenticated room user.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.username.startswith('room'):
            current_url = resolve(request.path_info)
            username = request.user.username.lower()  # e.g., room1-2

            match = re.fullmatch(r'room(\d+)-([12])', username)
            if not match:
                logout(request)
                return redirect('home')

            user_room_num = int(match.group(1))
            room_name = f'room{user_room_num}'
            subroom = int(match.group(2))

            if current_url.url_name in {'room_view', 'legacy_room_view'}:
                requested_room = current_url.kwargs.get('room_name', '').lower()
                requested_subroom = current_url.kwargs.get('subroom')

                if requested_room != room_name or requested_subroom != subroom:
                    return redirect(reverse('room_view', kwargs={
                        'room_name': room_name,
                        'subroom': subroom
                    }))

            elif current_url.url_name in {
                'mark_student_view',
                'mark_student_late',
                'submit_grade',
                'legacy_mark_student_view',
                'legacy_mark_student_late',
                'legacy_submit_grade',
            }:
                requested_subroom = current_url.kwargs.get('subroom')
                if requested_subroom != subroom:
                    return redirect(reverse('room_view', kwargs={
                        'room_name': room_name,
                        'subroom': subroom
                    }))

                student_number = current_url.kwargs.get('student_number')
                try:
                    student = Student.objects.get(number=student_number)
                except Student.DoesNotExist:
                    return redirect(reverse('room_view', kwargs={
                        'room_name': room_name,
                        'subroom': subroom
                    }))

                student_room = str(student.room).lower().replace('room', '')
                if student_room != str(user_room_num):
                    return redirect(reverse('room_view', kwargs={
                        'room_name': room_name,
                        'subroom': subroom
                    }))

        return self.get_response(request)
