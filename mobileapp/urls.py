from django.urls import path
from . import views
from screen.views import submit_grade

urlpatterns = [
    # Legacy redirect URLs with just room_name to the user's own subroom
    path('room/<str:room_name>/', views.room_redirect_default, name='legacy_room_redirect_default'),

    # Legacy room view with room_name and subroom
    path('room/<str:room_name>/<int:subroom>/', views.room_view, name='legacy_room_view'),

    # Legacy redirect after login
    path('redirect-after-login/', views.mobile_redirect_view, name='legacy_mobile_redirect'),

    # Legacy submit grade
    path('submit-grade/<int:student_number>/<int:subroom>/', submit_grade, name='legacy_submit_grade'),

    # Legacy mark student actions
    path('mark/<str:room_name>/<int:student_number>/<int:subroom>/', views.mark_student_view, name='legacy_mark_student_view'),
    path('mark-late/<str:room_name>/<int:student_number>/<int:subroom>/', views.mark_student_late, name='legacy_mark_student_late'),
]
