from calendar import month

from django.contrib.auth.models import User
from django.contrib.sites import requests
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import FeedbackForm
from .models import registration, horoscopedb, zodiacdb, contactdb
from .models import contact
import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login


from django.shortcuts import render
import datetime
import pytz
import swisseph as swe

# Helper function to check if session is valid
# def check_session(request):
#     if request.session.get('uname')=='':
#         return False
#     return True

def check_session(request):
    return bool(request.session.get('uname'))


def login(request):
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        fullname = request.POST['fullname']
        gender = request.POST['gender']
        email = request.POST['email']
        mobile = request.POST['mobile']
        username=request.POST['username']
        password = request.POST['password']
        confirmpassword = request.POST['confirm-password']

        if password==confirmpassword:
            # Check if a registration with the provided email already exists
            if registration.objects.filter(email=email).exists():
                msg = "Email already exists."
            if registration.objects.filter(username=username).exists():
                msg = "username already exists."
            else:
                registersave = registration(fullname=fullname, gender=gender, email=email, mobile=mobile,username=username, password=password)
                registration.save(registersave)
                msg = "Registered Successfully!!"

            return render(request, 'register.html', {'msg': msg})
        else:
            msg="Password and Confirm-password are not match"
            return render(request,'register.html',{'msg':msg})
    else:
        return render(request, 'register.html')


def index(request):
    return render(request, 'index.html')


def aboutpage(request):
    return render(request,'aboutpage.html')



def home(request):
    return render(request, 'home.html')


def checklogin(request):
    if request.method == 'POST':
        uname = request.POST['uname']
        upassword = request.POST['pwd']
        flag = registration.objects.filter(Q(username=uname) & Q(password=upassword))
        if (flag):
            request.session['uname']=uname
            message = "Login Success!!!"
            return render(request, 'index2.html', {'message': message,'uname':uname})
        else:
            message = "Login Failed!!"
            return render(request, 'login.html', {'message': message})

    return render(request, 'login.html')

from django.http import JsonResponse
from datetime import datetime
from .utils import get_zodiac_sign_and_ascendant

def zodiac(request):
    if not check_session(request):
        return redirect('home')

    uname = request.session.get('uname')
    if request.method == 'GET':
        return render(request,'zodiac.html',{'uname':auname})
    if request.method == 'POST':
        try:
            latitude = request.POST.get("latitude")
            longitude = request.POST.get("longitude")
            date = request.POST.get("date")
            time = request.POST.get("time")

            if not latitude or not longitude or not date or not time:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

            dt_str = f"{date}T{time}"
            dt = datetime.fromisoformat(dt_str)

            zodiac_sign, ascendant_sign = get_zodiac_sign_and_ascendant(dt, float(latitude), float(longitude))
            request._zodiac_sign = zodiac_sign
            request._ascendant_sign = ascendant_sign
            return render(request, "zodiac.html", {
                "zodiac_sign": zodiac_sign,
                "ascendant_sign": ascendant_sign,
                "uname":uname
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, "zodiac.html", {"uname": uname})

from django.shortcuts import render, redirect
import requests

def horoscope(request):
    if not check_session(request):
        return redirect('home')
    uname = request.session.get('uname')
    horoscope_data = None
    if request.method == 'POST':
        sign = request.POST.get('sign', '').capitalize()
        day = request.POST.get('day', 'today').upper()
        url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign}&day={day}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                horoscope_data = {
                    'sign': sign,
                    'day': day.capitalize(),
                    'date': data['data']['date'],
                    'description': data['data']['horoscope_data']
                }
            else:
                horoscope_data = {'error': 'Unable to fetch horoscope.'}
        except Exception as e:
            horoscope_data = {'error': str(e)}

    return render(request, 'horoscope.html', {'horoscope': horoscope_data,'uname':uname})


def feedback(request):
    if not check_session(request):
        return redirect('home')
    auname = request.session["uname"]
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('feedback')

    form = FeedbackForm()
    return render(request, 'feedback.html', {'form': form, 'uname': auname})


def changepassword(request):
    if not check_session(request):
        return redirect('home')
    auname = request.session["uname"]
    return render(request, 'changepassword.html', {'uname': auname})


def updatepwd(request):
    if not check_session(request):
        return redirect('home')
    auname = request.session["uname"]
    opwd = request.POST['opwd']
    npwd = request.POST['npwd']
    print(opwd, npwd)

    flag = registration.objects.filter(Q(password=opwd) & Q(username=auname))

    if flag:
        registration.objects.filter(password=opwd).update(password=npwd)
        msg = "Password Updated Successfully"
    else:
        msg = "Old password is incorrect"

    return render(request, 'changepassword.html', {"message": msg})

def contact(request):
    if request.method=='POST':
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        contactdetails=contactdb(firstname=firstname,lastname=lastname,email=email,message=message)
        contactdb.save(contactdetails)

    return render(request,'contactpage.html')

def help(request):
    uname = request.session["uname"]
    return render(request,'help.html',{'uname':uname})

def logout(request):
    request.session.clear()
    request.session.flush()
    request.session['uname']=''
    del request.session['uname']
    # Redirect the user to the home page after logging out
    return redirect('home')

