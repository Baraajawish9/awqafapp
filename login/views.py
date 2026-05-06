from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from screen.models import Student
from django.contrib import messages
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import re

@login_required(login_url='')
def home_view(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        return redirect('add_student')

    match = re.fullmatch(r'room(\d+)-([12])', user.username.lower())
    if match:
        room_num, subroom_num = match.groups()
        return redirect('room_view', room_name=f'room{room_num}', subroom=int(subroom_num))

    logout(request)
    return redirect('/')

def mobile_login(request):
    if request.user.is_authenticated:
        user = request.user


        if user.is_staff or user.is_superuser:
            return redirect('add_student')

        match = re.fullmatch(r'room(\d+)-([12])', user.username.lower())
        if match:
            room_num, subroom_num = match.groups()
            return redirect('room_view', room_name=f'room{room_num}', subroom=int(subroom_num))

        logout(request)
        return redirect('/')

    if request.method == 'POST':
        room_name = request.POST.get('room_name', '').strip().lower()
        password = request.POST.get('password', '')

        if room_name.startswith('room') and not re.fullmatch(r'room\d+-[12]', room_name):
            messages.error(request, 'اسم مستخدم اللجنة يجب أن يكون مثل room1-1 أو room1-2')
            return render(request, 'login/login.html')

        user = authenticate(request, username=room_name, password=password)
        if user is not None:
            login(request, user)



            if user.is_staff or user.is_superuser:
                return redirect('add_student')

            match = re.fullmatch(r'room(\d+)-([12])', room_name)
            if match:
                room_num, subroom_num = match.groups()
                return redirect('room_view', room_name=f'room{room_num}', subroom=int(subroom_num))

            logout(request)
            messages.error(request, 'اسم مستخدم اللجنة يجب أن يكون مثل room1-1 أو room1-2')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')

    return render(request, 'login/login.html')


@login_required(login_url='')
def mobile_logout(request):
    logout(request)
    return redirect('')


@login_required
def room_view(request, room_name, subroom):
    match = re.match(r'room(\d+)', room_name)
    if not match:
        return HttpResponse("Invalid room name", status=400)

    room_number = int(match.group(1))

    try:
        subroom_int = int(subroom)
    except ValueError:
        return HttpResponse("Invalid subroom number", status=400)

    if subroom_int not in (1, 2):
        return HttpResponse("Invalid subroom number", status=400)

    students = Student.objects.filter(room__in=[str(room_number), f'room{room_number}']).exclude(status='finished').order_by('position', 'number')

    return render(request, 'mobileapp/room_view.html', {
        'students': students,
        'room': room_number,
        'subroom': subroom_int,
    })


@staff_member_required(login_url='')
def add_student_view(request):
    return render(request, 'screen/add_student.html')
@login_required



def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Parse username 'roomX-Y'
            match = re.fullmatch(r'room(\d+)-([12])', username)
            if match:
                room_num = match.group(1)
                subroom_num = match.group(2)
                return redirect('room_view', room_name=f'room{room_num}', subroom=int(subroom_num))
            
            # fallback redirect
            return redirect('/')
        else:
            # invalid login
            pass
