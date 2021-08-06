import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from student_management_app.EmailBackEnd import EmailBackEnd


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
            return HttpResponseRedirect("/")


def getuserdetail(request):
    if request.user!=None:
        return HttpResponse("User : "+request.user.email+" usertype : "+str(request.user.user_type))
    else:
        return HttpResponse("Please Login First")

def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")
