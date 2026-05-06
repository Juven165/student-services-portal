from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_verified = models.BooleanField(default=False)

    def is_student(self):
        return self.role == 'student'

    def is_staff_user(self):
        return self.role == 'staff'

    def is_admin_user(self):
        return self.role == 'admin'