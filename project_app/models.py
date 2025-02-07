from django.contrib.auth.models import AbstractUser
from django.db import models
from .utils import *


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to_do')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
