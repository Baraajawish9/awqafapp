import random
import json
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

ROOM_CHOICES = [(i, f'Room {i}') for i in range(1, 6)]


class RoomQueue(models.Model):
    queue = models.TextField(default="[]")  # stores shuffled room list
    index = models.IntegerField(default=0)

    def get_queue(self):
        import json
        return json.loads(self.queue)

    def next_room(self):
        import json, random
        from .models import ScreenSettings

        room_count = ScreenSettings.get_room_count()
        q = self.get_queue()

        if self.index >= len(q):
            q = list(range(1, room_count + 1))
            random.shuffle(q)
            self.queue = json.dumps(q)
            self.index = 0

        room = q[self.index]
        self.index += 1
        self.queue = json.dumps(q)
        self.save()
        return room



    def __str__(self):
        return f"RoomQueue @ index {self.index} - {self.get_queue()}"


STATUS_CHOICES = [
    ('waiting', 'ينتظر'),
    ('in_exam', 'في السبر'),
    ('on_waiting_list', 'قائمة الانتظار'),
    ('finished', 'تم الانتهاء'),
    ('late','متأخر') 
]


EXAM_TYPE_CHOICES = [
    ('gh', 'غيباً'),
    ('nz', 'نظراً'),
]


class Student(models.Model):
    number = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="الاسم والكنية")
    father_name = models.CharField(max_length=100, verbose_name="اسم الأب", blank=True, null=True)
    birth_year = models.IntegerField(null=True, blank=True, verbose_name="عام التولد")
    institute_name = models.CharField(max_length=100, verbose_name="اسم المعهد", blank=True, null=True)
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES, verbose_name="غيباً/نظراً", blank=True, null=True)
    memorized_parts = models.CharField(max_length=100, verbose_name="الأجزاء المحفوظة", blank=True, null=True)
    grade = models.FloatField(null=True, blank=True)
    mistakes_json = models.TextField(null=True, blank=True)
    preferred_rooms = models.TextField(null=True, blank=True)
    position = models.PositiveIntegerField(default=0)
    subroom = models.IntegerField(default=1)



    room = models.CharField(max_length=50, default="room1")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')


    def save(self, *args, **kwargs):
        from .models import RoomQueue

        if not self.pk:
            last = Student.objects.order_by('-number').first()
            self.number = last.number + 1 if last else 1

        if not self.room:
            queue, _ = RoomQueue.objects.get_or_create(id=1)
            self.room = queue.next_room()

        super().save(*args, **kwargs)

# models.py
from django.db import models

class ScreenSettings(models.Model):
    SCREEN_MODE_CHOICES = [
        ('rooms', 'عرض اللجان الحالي'),
        ('window', 'عرض فترة 15 دقيقة'),
    ]

    room_count = models.IntegerField(default=5)
    waiting_count = models.IntegerField(default=5)
    estimate_time_per_student = models.IntegerField(default=5)  # <--- ADD THIS
    exam_start_time = models.TimeField(default="07:00")  # default 7 AM
    public_screen_mode = models.CharField(max_length=20, choices=SCREEN_MODE_CHOICES, default='rooms')

    @classmethod
    def get_settings(cls):
        return cls.objects.last()

    @staticmethod
    def get_settings():
        settings = ScreenSettings.objects.last()
        if not settings:
            settings = ScreenSettings.objects.create(room_count=5, waiting_count=5)
        return settings

    @staticmethod
    def get_room_count():
        settings = ScreenSettings.objects.first()
        return settings.room_count if settings else 5




class ExamResult(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=200)
    grade = models.FloatField()
    result = models.CharField(max_length=50)
    room = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    sub_room = models.CharField(max_length=10, blank=True, null=True)  # new field for sub-room like 'room11', 'room12'

