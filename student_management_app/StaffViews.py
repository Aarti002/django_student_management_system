import json
from django.db.models import Count
from django.contrib import messages
from django.core import serializers
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from student_management_app.models import NotificationStaff, CustomUser, Subjects, SessionYearModel, Staffs, LeaveReportStaff, Students, FeedBackStaff, Courses, Attendance, AttendanceReport


def staff_home(request):
    staff_detail = Staffs.objects.get(admin=request.user.id)
    total_feedback_send = FeedBackStaff.objects.filter(
        staff_id=staff_detail.id).count()
    total_leave_requests = LeaveReportStaff.objects.filter(
        staff_id=staff_detail.id).count()
    total_notifications = NotificationStaff.objects.filter(
        staff_id=staff_detail.id).count()

    # to show graph of staff count in each subject->
    # select subject_teach,count(*) as staff_count from
    # student_management_system.student_management_app_staffs  group by subject_teach;
    staff_wrt_subjects = []
    staff_in_each_subject = Staffs.objects.values(
        'subject_teach').annotate(staff_count=Count('id'))
    subjects_as_lable = []
    for itm in staff_in_each_subject:
        subjects_as_lable.append(itm['subject_teach'])
        staff_wrt_subjects.append(itm['staff_count'])

    # to show student count in each session period
    # select count(*) as student_count from
    # student_management_system.student_management_app_students  group by session_year_id_id;
    students_wrt_sessions = []
    students_in_each_session = Students.objects.values(
        'session_year_id').annotate(student_count=Count('id'))
    session_as_lable = []
    for itm in students_in_each_session:
        lable = str(SessionYearModel.objects.get(id=itm['session_year_id']).session_start_year) + " - " + str(
            SessionYearModel.objects.get(id=itm['session_year_id']).session_end_year)
        session_as_lable.append(lable)
        students_wrt_sessions.append(itm['student_count'])

    staff_count = Staffs.objects.all().count()
    student_count = Students.objects.all().count()
    return render(request, "staff_templates/staff_home_templates.html", {"total_feedback_send": total_feedback_send,
                                                                         "total_leave_requests": total_leave_requests,
                                                                         "total_notifications": total_notifications,
                                                                         "session_as_lable": session_as_lable,
                                                                         "student_wrt_session": students_wrt_sessions,
                                                                         "total_students": student_count, "total_staff": staff_count,
                                                                         })


def staff_take_attendance(request):
    staff_details = Staffs.objects.get(admin=request.user.id)
    courses = Courses.objects.all()
    sessions = SessionYearModel.objects.all()
    return render(request, "staff_templates/staff_attendance_templates.html", {"all_courses": courses, "all_sessions": sessions, "staff_detail": staff_details})


def fetch_students(request):
    print("in fetch students funtion")
    course_id = request.POST.get("course_id")
    session_id = request.POST.get("session_year")
    students = Students.objects.filter(course_id=course_id)
    student_list = []
    for student in students:
        if student.session_year_id == session_id:
            student_list.append(student)

    return render(request, "staff_templates/staff_attendance_templates.html", {"fetched_students": student_list})


@csrf_exempt
def get_students(request):
    course_id = request.POST.get("course_id")
    session_year = request.POST.get("session_year")

    course = Courses.objects.get(id=course_id)
    session_model = SessionYearModel.objects.get(id=session_year)
    students = Students.objects.filter(
        course_id=course, session_year_id=session_model)
    list_data = []

    for student in students:
        data_small = {"id": student.admin.id,
                      "name": student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)
    print(list_data)
    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def save_attendance_data(request):
    staff_id = request.POST.get("staff_id")
    student_ids = request.POST.get("student_ids")
    course_id = request.POST.get("course_id")
    attendance_date = request.POST.get("attendance_date")
    session_year_id = request.POST.get("session_year_id")

    staff_detail = Staffs.objects.get(admin=staff_id)
    course_detail = Courses.objects.get(id=course_id)
    session_detail = SessionYearModel.objects.get(id=session_year_id)
    json_sstudent = json.loads(student_ids)
    print(student_ids)

    try:
        attendance = Attendance(
            staff_id=staff_detail, session_year_id=session_detail,
            course_id=course_detail)
        attendance.save()

        for stud in json_sstudent:
            student = Students.objects.get(admin=stud['id'])
            attendance_report = AttendanceReport(
                attendance_date=attendance_date, staff_id=staff_detail,
                student_id=student, attendance_id=attendance, status=stud['status'])
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERR")


@csrf_exempt
def get_attendance_dates(request):
    subject = request.POST.get("subject")
    session_year_id = request.POST.get("session_year_id")
    subject_obj = Subjects.objects.get(id=subject)
    session_year_obj = SessionYearModel.objects.get(id=session_year_id)
    attendance = Attendance.objects.filter(
        subject_id=subject_obj, session_year_id=session_year_obj)
    attendance_obj = []
    for attendance_single in attendance:
        data = {"id": attendance_single.id, "attendance_date": str(
            attendance_single.attendance_date), "session_year_id": attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj), safe=False)


@csrf_exempt
def get_attendance_student(request):
    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    list_data = []

    for student in attendance_data:
        data_small = {"id": student.student_id.admin.id, "name": student.student_id.admin.first_name +
                      " "+student.student_id.admin.last_name, "status": student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def staff_feedback(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    feedback_data = FeedBackStaff.objects.filter(staff_id=staff_obj)
    return render(request, "staff_templates/staff_feedback.html", {"feedback_data": feedback_data})


def staff_feedback_save(request):
    if request.method != "POST":
        return HttpResponseRedirect("/staff_feedback")
    else:
        feedback_message = request.POST.get("feedback")
        staff_obj = Staffs.objects.get(admin=request.user.id)
        try:
            feedback_report = FeedBackStaff(
                staff_id=staff_obj, feedback=feedback_message, feedback_reply="")
            feedback_report.save()
            messages.success(request, "Feedback Send")
            return HttpResponseRedirect("/staff_feedback")
        except:
            messages.error(request, "Failed to Send your Feedback")
            return HttpResponseRedirect("/staff_feedback")


def staff_apply_leave(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data = LeaveReportStaff.objects.filter(staff_id=staff_obj)
    return render(request, "staff_templates/staff_apply_leave.html", {"leave_data": leave_data})


def staff_apply_leave_save(request):
    if request.method != "POST":
        return HttpResponseRedirect("/staff_apply_leave")
    else:
        leave_start_date = request.POST.get("leave_start")
        leave_end_date = request.POST.get("leave_end")
        reason = request.POST.get("leave_reason")
        staff_obj = Staffs.objects.get(admin=request.user.id)
        try:

            leave_report = LeaveReportStaff(
                staff_id=staff_obj, leave_start_date=leave_start_date,
                leave_end_date=leave_end_date, leave_message=reason, leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied for leave")
            return HttpResponseRedirect("/staff_apply_leave")
        except:
            messages.error(request, "Failed to Apply for leave")
            return HttpResponseRedirect("/staff_apply_leave")


def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user.id)
    return render(request, "staff_templates/staff_profile.html", {"user": user, "staff": staff})


def staff_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        address = request.POST.get("address")
        try:
            user = CustomUser.objects.get(id=request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            if password != None and password != "":
                user.password = password
            user.save()
            staff = Staffs.objects.get(admin=user.id)
            staff.address = address
            staff.save()
            messages.success(request, "Successfully Edited Admin Details")
            return HttpResponseRedirect(reverse("staff_profile"))
        except:
            messages.error(request, "Failed to Edit Admin Details")
            return HttpResponseRedirect(reverse("staff_profile"))


@csrf_exempt
def staff_fcmtoken_save(request):
    token = request.POST.get("token")
    try:
        staff = Staffs.objects.get(admin=request.user.id)
        staff.fcm_token = token
        staff.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")


def staff_all_notification(request):
    staff = Staffs.objects.get(admin=request.user.id)
    all_notifications = NotificationStaff.objects.filter(staff_id=staff)
    return render(request, "staff_templates/all_notification.html", {"all_notifications": all_notifications})


def delete_notification(request, notice_id):
    NotificationStaff.objects.filter(id=notice_id).delete()
    notice = NotificationStaff.objects.all()
    return render(request, "staff_templates/all_notification.html", {"notification": notice})


def staff_notification_reply(request, notice_id):
    notification = NotificationStaff.objects.get(id=notice_id)
    return render(request, "staff_templates/notification_reply.html", {"notification": notification})


def staff_notification_reply_save(request):
    if request.method != "POST":
        return HttpResponseRedirect("/notification_reply_save")
    else:
        notice_id = request.POST.get("notice_id")
        reply_message = request.POST.get("message_reply")
        try:
            notification = NotificationStaff.objects.get(id=notice_id)
            notification.message_reply = reply_message
            notification.save()
            messages.success(request, "Successfully Replied to Notification")
            return HttpResponseRedirect("/staff_all_notification")
        except:
            messages.error(request, "Failed to send Reply")
            return HttpResponseRedirect("/staff_all_notification")
