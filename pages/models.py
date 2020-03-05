from django.db import models

# Create your models here.
class Person(models.Model): 
    name = models.CharField(max_length=80)
    url = models.CharField(max_length=2000)
    urlDisplay = models.CharField(max_length=80)
    photo = models.ImageField()

    def __str__(self):
        return self.name

class Profile(models.Model):
    name = models.CharField(max_length=80)
    url = models.CharField(max_length=2000)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)