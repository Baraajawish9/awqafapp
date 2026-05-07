from io import BytesIO
import json
from datetime import datetime, time
from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import get_current_timezone, make_aware
from openpyxl import Workbook, load_workbook

from screen.forms import StudentForm
from screen.models import ExamResult, ScreenSettings, Student
from screen.views import EXAM_TYPE_MAP


class ExportStudentsExcelTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='admin-export', password='12345678')
        self.client.force_login(user)

    def test_export_with_grade_includes_final_grade_and_result(self):
        student = Student.objects.create(
            name='Export Student',
            father_name='Father',
            institute_name='Institute A',
            exam_type='gh',
            memorized_parts='1',
            room='1',
            position=1,
        )
        ExamResult.objects.create(
            number=student.number,
            name=student.name,
            grade=92.5,
            result='ناجح',
            room=1,
            sub_room='0',
        )

        response = self.client.get(reverse('export_students_excel'), {
            'institute': 'Institute A',
            'include_grade': '1',
        })

        self.assertEqual(response.status_code, 200)
        workbook = load_workbook(BytesIO(response.content))
        sheet = workbook.active
        rows = list(sheet.iter_rows(values_only=True))
        student_row = next(row for row in rows if row and row[1] == 'Export Student')

        self.assertEqual(student_row[8], 92.5)
        self.assertEqual(student_row[9], 'ناجح')

    def test_export_without_grade_keeps_original_columns(self):
        Student.objects.create(
            name='No Grade Export Student',
            institute_name='Institute A',
            exam_type='gh',
            room='1',
            position=1,
        )

        response = self.client.get(reverse('export_students_excel'), {
            'institute': 'Institute A',
            'include_grade': '0',
        })

        workbook = load_workbook(BytesIO(response.content))
        sheet = workbook.active
        header_row = next(row for row in sheet.iter_rows(values_only=True) if row and row[0] == 'الرقم')

        self.assertEqual(header_row[:8], ('الرقم', 'الاسم والكنية', 'اسم الأب', 'تاريخ الولادة', 'اسم المعهد', 'غيباً/نظراً', 'الأجزاء المحفوظة', 'الوقت المتوقع'))
        self.assertNotIn('الدرجة', header_row)
        self.assertNotIn('النتيجة', header_row)


class DashboardLateStatusTests(TestCase):
    def test_automatic_status_does_not_promote_top_student_to_in_exam(self):
        User.objects.create_user(username='admin-waiting', password='12345678')
        ScreenSettings.objects.create(room_count=1, waiting_count=5)
        students = [
            Student.objects.create(name='Top Waiting', room='1', status='waiting', position=0),
            Student.objects.create(name='Second Waiting', room='1', status='on_waiting_list', position=1),
        ]

        self.client.login(username='admin-waiting', password='12345678')
        response = self.client.post(reverse('apply_automatic_status'))
        for student in students:
            student.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(students[0].status, 'waiting')
        self.assertEqual(students[1].status, 'waiting')

    def test_dashboard_late_status_is_preserved_after_reordering(self):
        User.objects.create_user(username='admin-late', password='12345678')
        students = [
            Student.objects.create(name='Current', room='1', status='in_exam', position=0),
            Student.objects.create(name='Late Student', room='1', status='waiting', position=1),
            Student.objects.create(name='Next Student', room='1', status='waiting', position=2),
        ]

        self.client.login(username='admin-late', password='12345678')
        response = self.client.post(
            reverse('update_student_status', kwargs={'student_number': students[1].number}),
            {'status': 'late'},
        )
        students[1].refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(students[1].status, 'late')


class PublicScreenModeTests(TestCase):
    def test_window_mode_shows_students_in_next_15_minutes(self):
        user = User.objects.create_user(username='screen-admin', password='12345678', is_staff=True)
        ScreenSettings.objects.create(
            room_count=1,
            waiting_count=5,
            estimate_time_per_student=5,
            exam_start_time=time(8, 0),
            public_screen_mode='window',
        )
        students = [
            Student.objects.create(name=f'Student {idx}', room='1', status='waiting', position=idx)
            for idx in range(6)
        ]
        captured = {}

        def capture_render(request, template_name, context):
            captured.update(context)
            return HttpResponse('ok')

        today = datetime.today().date()
        fake_now = make_aware(datetime.combine(today, time(8, 10)), timezone=get_current_timezone())

        def fake_localtime(value=None, timezone=None):
            if value is None:
                return fake_now
            return value

        self.client.force_login(user)
        with patch('screen.views.render', side_effect=capture_render), patch('screen.views.localtime', side_effect=fake_localtime):
            response = self.client.get(reverse('public_screen'))

        visible_numbers = [student.number for student in captured['schedule_students']]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured['screen_mode'], 'window')
        self.assertEqual(visible_numbers, [student.number for student in students[2:6]])
        self.assertEqual(captured['schedule_window_start'], '08:10')
        self.assertEqual(captured['schedule_window_end'], '08:25')


class StudentImportMappingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin-import', password='12345678', is_staff=True)
        self.client.force_login(self.user)
        ScreenSettings.objects.create(room_count=4, waiting_count=5)

    def make_upload(self, rows):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(['number', 'name', 'father', 'birth', 'institute', 'exam_type', 'parts'])
        for row in rows:
            sheet.append(row)

        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        return SimpleUploadedFile(
            'students.xlsx',
            buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    def test_student_form_allows_empty_room_for_random_assignment(self):
        form = StudentForm(data={
            'name': 'Random Room Student',
            'father_name': '',
            'birth_year': '',
            'institute_name': '',
            'exam_type': 'gh',
            'memorized_parts': '1',
            'room': '',
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data['room'])

    def test_upload_excel_leaves_students_in_assignment_pool(self):
        exam_type_label = next(iter(EXAM_TYPE_MAP.keys()))
        upload = self.make_upload([
            [None, 'Juz One', '', 2010, 'Institute', exam_type_label, 1],
            [None, 'Juz Two', '', 2010, 'Institute', exam_type_label, 2],
            [None, 'Juz Thirty A', '', 2010, 'Institute', exam_type_label, 30],
            [None, 'Juz Thirty B', '', 2010, 'Institute', exam_type_label, 30],
        ])

        response = self.client.post(reverse('upload_excel'), {
            'file': upload,
        })

        self.assertEqual(response.status_code, 302)
        students_by_name = {
            student.name: student
            for student in Student.objects.filter(name__startswith='Juz')
        }

        self.assertEqual({student.room for student in students_by_name.values()}, {'unassigned'})
        self.assertEqual({student.status for student in students_by_name.values()}, {'on_waiting_list'})

    def test_upload_excel_keeps_room_preferences_for_later_assignment(self):
        exam_type_label = next(iter(EXAM_TYPE_MAP.keys()))
        upload = self.make_upload([
            [None, 'Preferred Student', '', 2010, 'Institute', exam_type_label, 30],
        ])

        response = self.client.post(reverse('upload_excel'), {
            'file': upload,
            'mapping_juz_0': ['30'],
            'mapping_room_0': ['2', '4'],
        })
        student = Student.objects.get(name='Preferred Student')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(student.room, 'unassigned')
        self.assertEqual(json.loads(student.preferred_rooms), [2, 4])

    def test_assign_imported_student_moves_one_student_to_a_room(self):
        student = Student.objects.create(
            name='Pool Student',
            room='unassigned',
            status='on_waiting_list',
            exam_type='gh',
        )

        response = self.client.post(reverse('assign_imported_student', kwargs={'student_number': student.number}))
        student.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertIn(str(student.room), {'1', '2', '3', '4'})
        self.assertEqual(student.status, 'waiting')

    def test_assign_imported_student_balances_within_preferred_rooms(self):
        for index in range(6):
            Student.objects.create(name=f'Room 1 Student {index}', room='1', status='waiting', position=index)
        for index in range(2):
            Student.objects.create(name=f'Room 2 Student {index}', room='2', status='waiting', position=index)
        student = Student.objects.create(
            name='Preferred Pool Student',
            room='unassigned',
            status='on_waiting_list',
            exam_type='gh',
            preferred_rooms=json.dumps([1, 2]),
        )

        response = self.client.post(reverse('assign_imported_student', kwargs={'student_number': student.number}))
        student.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(student.room, '2')
        self.assertEqual(student.preferred_rooms, '')
