import json

from django.contrib import messages
from django.core import serializers
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from student_management_app.models import CustomUser,Subjects,SessionYearModel,Staffs, LeaveReportStaff,Students, FeedBackStaffs,Courses,Attendance,AttendanceReport


def staff_home(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    course=[]
    for subject in subjects:
        cur=Courses.objects.get(id=subject.course_id.id)
        course.append(cur)

    final_course=[]
    for x in course:
        if x not in final_course:
            final_course.append(x)

    student_final=Students.objects.filter(course_id__in=final_course).count()
    attendance_count=Attendance.objects.filter(subject_id__in=subjects).count()
    staff=Staffs.objects.get(admin=request.user.id)
    leave_approve=LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()
    subject_count=subjects.count()
    subject_list=[]
    attendance_list=[]
    for subject in subjects:
        attendance=Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance)
    students=Students.objects.filter(course_id__in=final_course)
    student_list=[]
    student_attendance_present=[]
    student_attendance_absent=[]
    for student in students:
        total_present = AttendanceReport.objects.filter(student_id__in=student.id, status=True).count()
        total_absent = AttendanceReport.objects.filter(student_id__in=student.id, status=False).count()
        student_list.append(student.admin.username)
        student_attendance_absent.append(total_absent)
        student_attendance_present.append(total_present)
    return render(request,"staff_templates/staff_home_templates.html",{"students":student_final,"total_attendance":attendance_count,"leave":leave_approve,"subjects":subject_count,"subject_list":subject_list,"attendance_list":attendance_list,"student_list":student_list,"present":student_attendance_present,"absent":student_attendance_absent})

def staff_take_attendance(request):
    subjects = Subjects.objects.all()
    session_years=SessionYearModel.objects.all()
    return render(request,"staff_templates/staff_attendance_templates.html",{"subjects":subjects,"sessions":session_years})

@csrf_exempt
def get_students(request):
    subject_id=request.POST.get("subject")
    session_year=request.POST.get("session_year")

    subject=Subjects.objects.get(id=subject_id)
    session_model=SessionYearModel.objects.get(id=session_year)
    students=Students.objects.filter(course_id=subject.course_id,session_year_id=session_model)
    list_data=[]

    for student in students:
        data_small={"id":student.admin.id,"name":student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def save_attendance_data(request):
    student_ids=request.POST.get("student_ids")
    subject_id=request.POST.get("subject_id")
    attendance_date=request.POST.get("attendance_date")
    session_year_id=request.POST.get("session_year_id")

    subject_model=Subjects.objects.get(id=subject_id)
    session_model=SessionYearModel.objects.get(id=session_year_id)
    json_sstudent=json.loads(student_ids)
    #print(data[0]['id'])


    try:
        attendance=Attendance(subject_id=subject_model,attendance_date=attendance_date,session_year_id=session_model)
        attendance.save()

        for stud in json_sstudent:
             student=Students.objects.get(admin=stud['id'])
             attendance_report=AttendanceReport(student_id=student,attendance_id=attendance,status=stud['status'])
             attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERR")

def staff_update_attendance(request):
    subjects=Subjects.objects.all()
    session_year_id=SessionYearModel.objects.all()
    return render(request,"staff_templates/staff_update_attendance.html",{"subjects":subjects,"session_year_id":session_year_id})

@csrf_exempt
def get_attendance_dates(request):
    subject=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    subject_obj=Subjects.objects.get(id=subject)
    session_year_obj=SessionYearModel.objects.get(id=session_year_id)
    attendance=Attendance.objects.filter(subject_id=subject_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance:
        data={"id":attendance_single.id,"attendance_date":str(attendance_single.attendance_date),"session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj),safe=False)

@csrf_exempt
def get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def save_updateattendance_data(request):
    student_ids=request.POST.get("student_ids")
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    json_sstudent=json.loads(student_ids)


    try:
        for stud in json_sstudent:
             student=Students.objects.get(admin=stud['id'])
             attendance_report=AttendanceReport.objects.get(student_id=student,attendance_id=attendance)
             attendance_report.status=stud['status']
             attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERR")


def staff_feedback(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    feedback_data = FeedBackStaffs.objects.filter(staff_id=staff_obj)
    return render(request,"staff_templates/staff_feedback.html",{"feedback_data":feedback_data})

def staff_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect("/staff_feedback")
    else:
        feedback_message=request.POST.get("feedback")
        staff_obj = Staffs.objects.get(admin=request.user.id)
        try:
            feedback_report=FeedBackStaffs(staff_id=staff_obj,feedback=feedback_message,feedback_reply="")
            feedback_report.save()
            messages.success(request, "Feedback Acknowledge")
            return HttpResponseRedirect("/staff_feedback")
        except:
            messages.error(request, "Failed to Acknowledge your feedback")
            return HttpResponseRedirect("/staff_feedback")


def staff_apply_leave(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data=LeaveReportStaff.objects.filter(staff_id=staff_obj)
    return render(request,"staff_templates/staff_apply_leave.html",{"leave_data":leave_data})

def staff_apply_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect("/staff_apply_leave")
    else:
        leave_date=request.POST.get("leave_date")
        reason=request.POST.get("leave_reason")
        staff_obj = Staffs.objects.get(admin=request.user.id)
        try:

            leave_report=LeaveReportStaff(staff_id=staff_obj,leave_date=leave_date,leave_message=reason,leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied for leave")
            return HttpResponseRedirect("/staff_apply_leave")
        except:
            messages.error(request, "Failed to Apply for leave")
            return HttpResponseRedirect("/staff_apply_leave")

def staff_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    staff=Staffs.objects.get(admin=user.id)
    return render(request,"staff_templates/staff_profile.html",{"user":user,"staff":staff})

def staff_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password=request.POST.get("password")
        address=request.POST.get("address")
        try:
            user = CustomUser.objects.get(id=request.user.id)
            user.first_name=first_name
            user.last_name=last_name
            if password!=None and password!="":
                user.password=password
            user.save()
            staff=Staffs.objects.get(admin=user.id)
            staff.address=address
            staff.save()
            messages.success(request, "Successfully Edited Admin Details")
            return HttpResponseRedirect(reverse("staff_profile"))
        except:
            messages.error(request, "Failed to Edit Admin Details")
            return HttpResponseRedirect(reverse("staff_profile"))
