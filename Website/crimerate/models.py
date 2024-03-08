from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CrimeRate(models.Model):
    state = models.CharField(max_length=100)
    crimerate = models.IntegerField()

    def __str__(self) -> str:
        return self.state



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)  # Adjust the max_length based on your needs

    def __str__(self):
        return self.user.username