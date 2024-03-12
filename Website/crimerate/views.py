from django.shortcuts import render
from django.http import HttpResponse
from .models import CrimeRate
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
import random
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from math import radians, sin, cos, sqrt, atan2
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from .models import UserProfile  # Import your UserProfile model
from django.views.decorators.csrf import csrf_protect
import requests
import json


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

        try:
            # Fetch the user from the database
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return render(request, 'signin.html', {'error_message': 'User does not exist.'})

        # Activate the user account if it's not active
        if not user.is_active:
            user.is_active = True
            user.save()

        # Authenticate the user
        authenticated_user = authenticate(request, username=username, password=pass1)
        print("Authenticated user", authenticated_user.username)

        if authenticated_user is not None:
            
            # Store minimal user information in the session
            request.session['user_id'] = authenticated_user.id
            request.session['username'] = authenticated_user.username
            request.session['first_name'] = authenticated_user.first_name
            fname = authenticated_user.first_name
            authenticated_username = authenticated_user.username
            messages.success(request, "Logged in successfully!")
            return redirect('home')

        messages.error(request, "Invalid credentials.")
        return render(request, 'signin.html', {'error_message': 'Invalid credentials.'})

    return render(request, 'signin.html')



def signout(request):
    pass

# @csrf_protect
@csrf_exempt
# @login_required(login_url='/login') 
def send_sos_signal(request):
    
    if request.method == 'POST':
        try:
            authenticated_username = request.user.username
            print("Is user authenticated?", request.user.is_authenticated)
            data = json.loads(request.body)
            latitude_str = data.get('latitude', '')
            longitude_str = data.get('longitude', '')
            
            
            if request.user.is_authenticated:
                current_user = request.user
                print("Username is", current_user.username)


            if not latitude_str or not longitude_str:
                raise ValueError("Latitude and longitude values are required.")

            latitude = float(latitude_str)
            longitude = float(longitude_str)

            # Retrieve user profile using the current_user directly
            # try:
            #     user_profile = UserProfile.objects.get(user=current_user)
            # except UserProfile.DoesNotExist:
            #     raise ValueError(f"User profile for {current_user.username} does not exist.")

            police_station_name = find_nearest_police_station((latitude, longitude))
            print("Location name", police_station_name)

            # Notify all registered users (excluding the currently logged-in user)
            registered_users = UserProfile.objects.exclude(user=current_user)
            print("Registered users", registered_users)
            for user_profile in registered_users:
                send_signal(police_station_name, user_profile.user.username)

            return JsonResponse({"status": "success", "policeStation": police_station_name})
        except ValueError as e:
            return JsonResponse({"status": "error", "message": str(e)})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {type(e).__name__} - {str(e)}"})
    else:
        return render(request, 'send_sos.html')



def haversine_distance(lat1, lon1, lat2, lon2):
    # Function to calculate haversine distance between two sets of coordinates
    R = 6371  # Radius of the Earth in kilometers

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c  # Distance in kilometers

    return distance

def get_police_station_data_from_database():
    # Replace this with your actual method of retrieving data from a database
    # Example: assuming a list of dictionaries with 'name', 'latitude', and 'longitude' keys
    return [
        {"name": "Vasai Police Station", "latitude": 19.3560, "longitude": 72.8432},
        {"name": "Virar Police Station", "latitude": 19.4550, "longitude": 72.8114},
        {"name": "Nallasopara Police Station", "latitude": 19.4204, "longitude": 72.8220},
        {"name": "Bhayandar Police Station", "latitude": 19.3101, "longitude": 72.8519},
        {"name": "Dahisar Police Station", "latitude": 19.2484, "longitude": 72.8594},
        {"name": "Borivali Police Station", "latitude": 19.2307, "longitude": 72.8567},
        {"name": "Kandivali Police Station", "latitude": 19.2045, "longitude": 72.8418},
        {"name": "Malad Police Station", "latitude": 19.1867, "longitude": 72.8484},
        {"name": "Goregaon Police Station", "latitude": 19.1633, "longitude": 72.8416},
        {"name": "Jogeshwari Police Station", "latitude": 19.1379, "longitude": 72.8446},
        {"name": "Andheri Police Station", "latitude": 19.1197, "longitude": 72.8464},
        {"name": "Vile Parle Police Station", "latitude": 19.1000, "longitude": 72.8409},
        {"name": "Santacruz Police Station", "latitude": 19.0810, "longitude": 72.8376},
        {"name": "Khar Police Station", "latitude": 19.0726, "longitude": 72.8361},
        {"name": "Bandra Police Station", "latitude": 19.0553, "longitude": 72.8297},
        {"name": "Mahim Police Station", "latitude": 19.0414, "longitude": 72.8435},
        {"name": "Matunga Police Station", "latitude": 19.0272, "longitude": 72.8509},
        {"name": "Dadar Police Station", "latitude": 19.0199, "longitude": 72.8428},
        {"name": "Prabhadevi Police Station", "latitude": 19.0149, "longitude": 72.8284},
        {"name": "Lower Parel Police Station", "latitude": 18.9953, "longitude": 72.8301},
        {"name": "Elphinstone Road Police Station", "latitude": 18.9931, "longitude": 72.8358},
        {"name": "Mahalaxmi Police Station", "latitude": 18.9832, "longitude": 72.8271},
    ]

def find_nearest_police_station(user_location):
    police_stations = get_police_station_data_from_database()
    print("User Location:", user_location)  # Add this line
 

    if not police_stations:
        raise ValueError("No police stations provided.")

    user_latitude, user_longitude = user_location

    # Calculate distances for all police stations
    distances = [
        (
            station["name"],
            haversine_distance(
                user_latitude, user_longitude, station["latitude"], station["longitude"]
            ),
        )
        for station in police_stations
    ]



    # Find the nearest police station
    nearest_station_name, _ = min(distances, key=lambda x: x[1])
    print("Station",nearest_station_name)

    return nearest_station_name

# Example usage
user_location = (19.0, 72.0)  # Replace with the actual user's location
nearest_police_station_name = find_nearest_police_station(user_location)
print(f"The nearest police station is: {nearest_police_station_name}")

def send_signal(police_station, username):
    try:
        send_sms_to_police(username, police_station)
        print(f"SOS signal sent to {police_station}")
    except Exception as e:
        print(f"Failed to send SOS signal: {str(e)}")

def send_sms_to_police(username, police_station):
    try:
        user = User.objects.get(username=username)
        user_profile = UserProfile.objects.get(user=user)
        user_phone_number = user_profile.phone_number   

        # Replace these with your actual Twilio credentials and phone numbers
        account_sid = 'ACfbf0611561ddf5c8c406e0069499ab6c'
        auth_token = '73a86e698bfe31ef818efcdc5dc89310'
        twilio_phone_number = '+13346002072'

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=f"SOS signal received. Please respond {police_station}",
            from_=twilio_phone_number,
            to=user_phone_number
        )

        print(f"Twilio Message SID: {message.sid}")

    except User.DoesNotExist:
        print(f"User with username {username} does not exist.")
    except UserProfile.DoesNotExist:
        print(f"UserProfile for user {username} does not exist.")

# Example usage
user_location = (19.0, 72.0)  # Replace with the actual user's location
nearest_police_station_name = find_nearest_police_station(user_location)
print(f"The nearest police station is: {nearest_police_station_name}")

# Example usage
nearest_police_station = "Sample Police Station"
user_username = "sample_user"
send_signal(nearest_police_station, user_username)

