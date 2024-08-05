from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "admin"
        EXAM_IMPORTER = "EXAM_IMPORTER", "exam-importer"
        TIME_SETTER = "TIME_SETTER", "time-setter"
        EXAM_GENERATOR = "EXAM_GENERATOR", "exam-generator"
        STUDENT = "STUDENT", "student"
    base_role = Role.ADMIN
    role = models.CharField(max_length=50, choices=Role.choices)
