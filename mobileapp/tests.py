from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from unittest.mock import mock_open, patch

from screen.models import ExamResult, Student


class RoomBranchQuizTests(TestCase):
    def setUp(self):
        self.room1_1 = User.objects.create_user(username='room1-1', password='12345678')
        self.room1_2 = User.objects.create_user(username='room1-2', password='12345678')

    def test_room_branches_show_the_same_students(self):
        Student.objects.create(name='First Student', room='1', subroom=1, status='in_exam', position=1)
        Student.objects.create(name='Second Student', room='room1', subroom=2, status='waiting', position=2)

        def render_student_names(request, template_name, context):
            return HttpResponse('\n'.join(student.name for student in context['students']))

        with patch('mobileapp.views.render', side_effect=render_student_names):
            self.client.force_login(self.room1_1)
            branch_one = self.client.get(reverse('room_view', kwargs={'room_name': 'room1', 'subroom': 1}))

            self.client.force_login(self.room1_2)
            branch_two = self.client.get(reverse('room_view', kwargs={'room_name': 'room1', 'subroom': 2}))

            self.assertContains(branch_one, 'First Student')
            self.assertContains(branch_one, 'Second Student')
            self.assertContains(branch_two, 'First Student')
            self.assertContains(branch_two, 'Second Student')

    def test_room_view_stays_single_live_queue_without_result_pages(self):
        for index in range(7):
            Student.objects.create(name=f'Queue Student {index + 1}', room='1', status='waiting', position=index)
        ExamResult.objects.create(
            number=90,
            name='Recent Result',
            grade=94,
            result='ناجح',
            room=1,
            sub_room='0',
        )

        def capture_room_context(request, template_name, context):
            self.assertNotIn('queue_pages', context)
            self.assertNotIn('result_pages', context)
            self.assertEqual(len(context['students']), 7)
            return HttpResponse('room context captured')

        self.client.force_login(self.room1_1)
        with patch('mobileapp.views.render', side_effect=capture_room_context):
            response = self.client.get(reverse('room_view', kwargs={'room_name': 'room1', 'subroom': 1}))

        self.assertEqual(response.status_code, 200)

    def test_plain_room_login_is_rejected(self):
        User.objects.create_user(username='room1', password='12345678')

        with patch('login.views.render', return_value=HttpResponse('login')):
            response = self.client.post('/', {'room_name': 'room1', 'password': '12345678'})

            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_room_user_cannot_mark_student_late_from_mobile(self):
        student = Student.objects.create(name='Late Blocked Student', room='1', status='in_exam', position=1)

        self.client.force_login(self.room1_1)
        response = self.client.get(
            reverse('mark_student_late', kwargs={
                'room_name': 'room1',
                'student_number': student.number,
                'subroom': 1,
            })
        )
        student.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(student.status, 'in_exam')

    def test_room_user_cannot_open_grade_page_for_non_current_student(self):
        current_student = Student.objects.create(name='Current Student', room='1', status='in_exam', position=1)
        waiting_student = Student.objects.create(name='Waiting Student', room='1', status='waiting', position=2)

        self.client.force_login(self.room1_1)
        with patch('mobileapp.views.render', return_value=HttpResponse('grade page')):
            current_response = self.client.get(
                reverse('mark_student_view', kwargs={
                    'room_name': 'room1',
                    'student_number': current_student.number,
                    'subroom': 1,
                })
            )
        waiting_response = self.client.get(
            reverse('mark_student_view', kwargs={
                'room_name': 'room1',
                'student_number': waiting_student.number,
                'subroom': 1,
            })
        )

        self.assertEqual(current_response.status_code, 200)
        self.assertRedirects(waiting_response, '/rooms/room1/1/', fetch_redirect_response=False)

    def test_room_user_clicking_top_waiting_student_promotes_student(self):
        student = Student.objects.create(name='Top Waiting Student', room='1', status='waiting', position=1)

        self.client.force_login(self.room1_1)
        with patch('mobileapp.views.render', return_value=HttpResponse('grade page')):
            response = self.client.get(
                reverse('mark_student_view', kwargs={
                    'room_name': 'room1',
                    'student_number': student.number,
                    'subroom': 1,
                })
            )
        student.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(student.status, 'in_exam')

    def test_room_user_cannot_submit_grade_for_non_current_student(self):
        Student.objects.create(name='Current Student', room='1', status='in_exam', position=1)
        waiting_student = Student.objects.create(name='Waiting Student', room='1', status='waiting', position=2)

        self.client.force_login(self.room1_1)
        response = self.client.post(
            reverse('submit_grade', kwargs={'student_number': waiting_student.number, 'subroom': 1}),
            {'final_grade': '100'},
        )

        self.assertRedirects(response, '/rooms/room1/1/', fetch_redirect_response=False)
        self.assertFalse(ExamResult.objects.filter(number=waiting_student.number).exists())

    def test_both_branch_submissions_are_averaged_before_finishing_student(self):
        student = Student.objects.create(
            name='Average Student',
            room='1',
            status='in_exam',
            exam_type='gh',
            position=1,
        )
        next_student = Student.objects.create(name='Next Student', room='1', status='waiting', position=2)

        with patch('builtins.open', mock_open()), patch('screen.views.os.path.isfile', return_value=True):
            self.client.force_login(self.room1_1)
            first_response = self.client.post(
                reverse('submit_grade', kwargs={'student_number': student.number, 'subroom': 1}),
                {'final_grade': '80'},
            )
            student.refresh_from_db()

            self.assertRedirects(first_response, '/rooms/room1/1/', fetch_redirect_response=False)
            self.assertEqual(student.status, 'in_exam')
            self.assertFalse(ExamResult.objects.filter(number=student.number, sub_room='0').exists())

            self.client.force_login(self.room1_2)
            second_response = self.client.post(
                reverse('submit_grade', kwargs={'student_number': student.number, 'subroom': 2}),
                {'final_grade': '100'},
            )
            student.refresh_from_db()
            final_result = ExamResult.objects.get(number=student.number, sub_room='0')

            self.assertRedirects(second_response, '/rooms/room1/2/', fetch_redirect_response=False)
            self.assertEqual(student.status, 'finished')
            next_student.refresh_from_db()
            self.assertEqual(next_student.status, 'waiting')
            self.assertEqual(final_result.grade, 90)
            self.assertEqual(ExamResult.objects.filter(number=student.number, sub_room__in=['1', '2']).count(), 2)
