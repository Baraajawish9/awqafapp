from django.urls import path
from . import views
from .views import upload_excel

urlpatterns = [
    # Legacy public screen
    path('', views.public_screen, name='legacy_public_screen'),

    # Legacy student operations
    path('add-student/', views.add_student, name='legacy_add_student'),
    path('remove-student/<int:student_number>/', views.remove_student, name='legacy_remove_student'),
    path('update-status/<int:student_number>/', views.update_student_status, name='legacy_update_student_status'),

    # Legacy grade submission
    path('submit-grade/<int:student_number>/', views.submit_grade, name='legacy_screen_submit_grade'),

    # Legacy Excel import/export
    path('upload-excel/', upload_excel, name='legacy_upload_excel'),
    path('export_excel/', views.export_students_excel, name='legacy_export_students_excel'),

    # Legacy settings
    path('screen/settings/', views.edit_settings, name='legacy_edit_settings'),

    # Legacy status control
    path('apply-status/', views.trigger_automatic_status, name='legacy_apply_automatic_status'),
    path('automatic-status/', views.trigger_automatic_status, name='legacy_trigger_automatic_status'),
    path('clear', views.clear_students, name='legacy_clear_students'),
    path('clear-results-from-screen/', views.clear_all_results, name='legacy_clear_all_results'),

    # Legacy student movement
    path('screen/move/<int:number>/', views.move_student_position, name='legacy_move_student_position'),
]
