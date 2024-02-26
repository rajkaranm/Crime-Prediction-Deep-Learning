from django.shortcuts import render
from django.http import HttpResponse
from .models import CrimeRate
import random

# Create your views here.
def crimerate(request):
    if request.method == "POST":
        data = CrimeRate.objects.get(state=request.POST['city'])
        return render(request, 'crimerate.html', {"CrimeRate": float(data.crimerate - random.uniform(-0.2, 0.9)), "State": data.state})

    return render(request, 'crimerate.html', {})