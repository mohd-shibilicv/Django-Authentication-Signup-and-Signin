from django.db import models

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    address = models.CharField(max_length=300)

    def __str__(self):
        return f"name: {self.name}, Age: {self.age}, {self.address}"
    

