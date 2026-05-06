from django.contrib import admin
from django.urls import path, include
from login.views import mobile_login  # Your custom login view
from django.contrib.auth import views as auth_views
from mobileapp import views as mobile_views
from screen import views as screen_views
from screen.views import submit_grade, upload_excel

urlpatterns = [
    path('', mobile_login, name='home'),  # Use custom login as homepage

    # Main admin area
    path('dashboard/', screen_views.add_student, name='add_student'),
    path('display/', screen_views.public_screen, name='public_screen'),
    path('settings/', screen_views.edit_settings, name='edit_settings'),

    # Student and exam operations
    path('students/import/', upload_excel, name='upload_excel'),
    path('students/export/', screen_views.export_students_excel, name='export_students_excel'),
    path('students/clear/', screen_views.clear_students, name='clear_students'),
    path('students/<int:student_number>/remove/', screen_views.remove_student, name='remove_student'),
    path('students/<int:student_number>/status/', screen_views.update_student_status, name='update_student_status'),
    path('students/<int:number>/move/', screen_views.move_student_position, name='move_student_position'),
    path('results/clear/', screen_views.clear_all_results, name='clear_all_results'),
    path('status/apply/', screen_views.trigger_automatic_status, name='apply_automatic_status'),
    path('status/automatic/', screen_views.trigger_automatic_status, name='trigger_automatic_status'),

    # Quiz room area
    path('rooms/redirect-after-login/', mobile_views.mobile_redirect_view, name='mobile_redirect'),
    path('rooms/<str:room_name>/', mobile_views.room_redirect_default, name='room_redirect_default'),
    path('rooms/<str:room_name>/<int:subroom>/', mobile_views.room_view, name='room_view'),
    path('rooms/<str:room_name>/<int:subroom>/students/<int:student_number>/grade/', mobile_views.mark_student_view, name='mark_student_view'),
    path('rooms/<str:room_name>/<int:subroom>/students/<int:student_number>/late/', mobile_views.mark_student_late, name='mark_student_late'),
    path('grades/<int:student_number>/<int:subroom>/submit/', submit_grade, name='submit_grade'),

    # Legacy routes kept alive for old bookmarks and open screens.
    path('mobileapp/', include('mobileapp.urls')),
    path('screen/', include('screen.urls')),
    path('admin/', admin.site.urls),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),  # Logout redirect to login
]
