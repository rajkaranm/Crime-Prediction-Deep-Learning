from django.db import models

# Create your models here.
class CrimeRate(models.Model):
    state = models.CharField(max_length=100)
    crimerate = models.IntegerField()

    def __str__(self) -> str:
        return self.state
