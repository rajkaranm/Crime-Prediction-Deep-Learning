from django.shortcuts import render
from django.http import HttpResponse
from .models import CrimeRate
import random
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def crimerate(request):
    if request.method == "POST":
        data = CrimeRate.objects.get(state=request.POST['city'])
        return render(request, 'crimerate.html', {"CrimeRate": float(data.crimerate - random.uniform(-0.2, 0.9)), "State": data.state})

    return render(request, 'crimerate.html', {})

def register(request):
    if request.method == "POST":
        fname = request.POST['fname']
        uname = request.POST['uname']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        cnfPass = request.POST['cnfPass']
        
        myuser = User.objects.create_user(uname, email, password)
        myuser.first_name = fname
        myuser.phone = phone
        # myuser.is_active = False
        myuser.is_active = False
        myuser.save()

        messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")

        return redirect('login')
        
    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        print("Received username:", username)
        print("Received password:", pass1)
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            messages.success(request, "Logged In Sucessfully!!")
            return render(request, "crimerater",{"fname":fname})
        else:
            print("Authentication failed for username:", username)
            messages.error(request, "Bad Credentials!!")
            return redirect('login')
    
    return render(request, 'signin.html')

def signout(request):
    pass