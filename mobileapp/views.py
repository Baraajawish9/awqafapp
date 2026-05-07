from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from screen.models import Student
from .forms import RoomLoginForm, MarkForm
import csv
import os
import re
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.conf import settings
from screen.views import get_top_active_student_for_room, parse_room_number
from django.shortcuts import redirect
from django.contrib import messages
from screen.models import ExamResult
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Avg
from screen.models import Student

@login_required
def room_view(request, room_name, subroom):
    match = re.match(r'room(\d+)', room_name)
    if not match:
        return HttpResponse("Invalid room name", status=400)

    room_number = match.group(1)  # '7' from 'room7'
    if subroom not in (1, 2):
        return HttpResponse("Invalid subroom number", status=400)

    room_values = [room_number, f'room{room_number}']
    students = Student.objects.filter(room__in=room_values).exclude(status="finished").order_by('position', 'number')

    return render(request, 'mobileapp/room_view.html', {
        'students': students,
        'room_name': room_name,
        'room_number': room_number,
        'subroom': subroom,
    })







@login_required
def mobile_redirect_view(request):
    username = request.user.username.lower()
    match = re.fullmatch(r'room(\d+)-([12])', username)
    if match:
        room_number, subroom = match.groups()
        return redirect('room_view', room_name=f'room{room_number}', subroom=int(subroom))
    elif username.startswith("room"):
        return redirect('/')
    else:
        return redirect('add_student')

@login_required
def mark_student_view(request, room_name, student_number, subroom):
    match = re.match(r'room(\d+)', room_name)
    if not match:
        return HttpResponse("Invalid room name", status=400)
    if subroom not in (1, 2):
        return HttpResponse("Invalid subroom number", status=400)

    room_number = match.group(1)
    student = get_object_or_404(Student, number=student_number, room__in=[room_number, f'room{room_number}'])
    top_student = get_top_active_student_for_room(room_number)
    if not top_student or top_student.number != student.number:
        return redirect('room_view', room_name=room_name, subroom=subroom)

    if student.status != 'in_exam':
        Student.objects.filter(room__in=[room_number, f'room{room_number}'], status='in_exam').exclude(number=student.number).update(status='waiting')
        student.status = 'in_exam'
        student.save(update_fields=['status'])

    subroom_results = ExamResult.objects.filter(number=student.number, sub_room__in=['1', '2'])
    grades = [er.grade for er in subroom_results]
    avg_grade = sum(grades) / len(grades) if grades else 100

    if student.exam_type in ["غيبا", "gh"]:
        questions = ['الأول', 'الثاني', 'الثالث']
    else:
        questions = ['الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس']

    return render(request, 'mobileapp/mark_student.html', {
        'student': student,
        'subroom': subroom,
        'room_name': f'room{parse_room_number(student.room) or room_number}',
        'avg_grade': avg_grade,
        'questions': questions,
    })



def some_view(request):
    username = request.user.username  # e.g. 'room1-2'
    match = re.match(r'(room\d+)-(\d+)', username)
    if match:
        room_name = match.group(1)
        subroom = int(match.group(2))
    else:
        room_name = username
        subroom = 1

    return redirect('room_view', room_name=room_name, subroom=subroom)
@login_required
def room_redirect_default(request, room_name):
    username = request.user.username.lower()
    match = re.fullmatch(r'room(\d+)-([12])', username)
    if match:
        room_number, subroom = match.groups()
        return redirect('room_view', room_name=f'room{room_number}', subroom=int(subroom))
    return HttpResponse("Room login must use roomX-1 or roomX-2", status=403)


@login_required
def mark_student_late(request, room_name, student_number, subroom):
    return HttpResponse("Marking students late is only available from the dashboard.", status=403)

