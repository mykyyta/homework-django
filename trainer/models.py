from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class TrainerDescription(models.Model):
    name = models.TextField()
    trainer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='description')

class TrainerSchedule(models.Model):
    datetime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule')

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    price = models.DecimalField(max_digits=7, decimal_places=2)
    level = models.CharField(max_length=50)
    duration = models.IntegerField(null=True)