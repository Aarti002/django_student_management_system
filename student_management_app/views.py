import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from student_management_app.models import CustomUser

from student_management_app.EmailBackEnd import EmailBackEnd

def showFirebaseJS(request):
    data='importScripts("https://www.gstatic.com/firebasejs/7.14.6/firebase-app.js");' \
         'importScripts("https://www.gstatic.com/firebasejs/7.14.6/firebase-messaging.js"); ' \
         'var firebaseConfig = {' \
         '        apiKey: "YOUR_API_KEY",' \
         '        authDomain: "FIREBASE_AUTH_URL",' \
         '        databaseURL: "FIREBASE_DATABASE_URL",' \
         '        projectId: "FIREBASE_PROJECT_ID",' \
         '        storageBucket: "FIREBASE_STORAGE_BUCKET_URL",' \
         '        messagingSenderId: "FIREBASE_SENDER_ID",' \
         '        appId: "FIREBASE_APP_ID",' \
         '        measurementId: "FIREBASE_MEASUREMENT_ID"' \
         ' };' \
         'firebase.initializeApp(firebaseConfig);' \
         'const messaging=firebase.messaging();' \
         'messaging.setBackgroundMessageHandler(function (payload) {' \
         '    console.log(payload);' \
         '    const notification=JSON.parse(payload);' \
         '    const notificationOption={' \
         '        body:notification.body,' \
         '        icon:notification.icon' \
         '    };' \
         '    return self.registration.showNotification(payload.notification.title,notificationOption);' \
         '});'

    return HttpResponse(data,content_type="text/javascript")



def index(request):
    return render(request,"index.html")

def login_page(request):
    return render(request,"login.html")

def dologin(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user=EmailBackEnd.authenticate(request,username=request.POST['email'],password=request.POST['password'])
        if user!=None:
            login(request, user)
            if user.user_type=='1':
                return HttpResponseRedirect('/admin_home')
            elif user.user_type=='2':
                return HttpResponseRedirect('/staff_home')
            elif user.user_type=='3':
                return HttpResponseRedirect('/student_home')

        else:
            messages.error(request,"Invalid Login Details")
            return HttpResponseRedirect("https://smsdjango.herokuapp.com/")


def getuserdetail(request):
    if request.user!=None:
        return HttpResponse("User : "+request.user.email+" usertype : "+str(request.user.user_type))
    else:
        return HttpResponse("Please Login First")

def logout_user(request):

    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("main:homepage")
"""
def Change_password(request):
    return render(request,'registration/change_password.html')

def Forget_password(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user_email=request.POST.get('email')
        if not CustomUser.objects.filter(email=user_email).first():
            messages.error(request,"User not found!")
            return redirect('/registration/forget_password/')

        user_obj=CustomUser.objects.get(email=user_email)"""