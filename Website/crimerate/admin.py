from django.contrib import admin
from .models import CrimeRate, UserProfile

# Register your models here.
admin.site.register(CrimeRate)
admin.site.register(UserProfile)