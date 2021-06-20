from django.db import models
from datetime import date

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=30)

class Task(models.Model):
    name = models.CharField(max_length=100)
    isComplete = models.BooleanField(default=False)
    taskCycle = models.JSONField()
    dueDate = models.DateField(null=True)
    userId = models.ForeignKey(to='User', on_delete=models.PROTECT)

class Event(models.Model):
    name = models.CharField(max_length=100)
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    userId = models.ForeignKey(to='User', on_delete=models.PROTECT)
    dateClass = models.CharField(max_length=20)
    master = models.ForeignKey(to='Event', on_delete=models.PROTECT, null=True)