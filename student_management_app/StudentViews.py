import datetime

from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from student_management_app.models import Staffs,SessionYearModel,NotificationStudent, Subjects, Students, Courses, CustomUser, Attendance, AttendanceReport, FeedBackStudent, LeaveReportStudent


def student_home(request):
    student_obj = Students.objects.get(admin=request.user.id)
    # for leave count
    total_leave = LeaveReportStudent.objects.filter(
        student_id=student_obj).count()
    total_notifications = NotificationStudent.objects.filter(
        student_id=student_obj).count()
    total_feedback_send = FeedBackStudent.objects.filter(
        student_id=student_obj).count()

    # total_attendance=AttendanceReport.objects.filter(student_id=student_obj).count()
    # total_present = AttendanceReport.objects.filter(student_id=student_obj,status=True).count()
    # total_absent = AttendanceReport.objects.filter(student_id=student_obj,status=False).count()

    course = Courses.objects.get(id=student_obj.course_id.id)
    subject = Subjects.objects.filter(course_id=course).count()
    subject_name = []
    subject_present_attendance = []
    subject_absent_attendance = []
    subject_data = Subjects.objects.filter(course_id=student_obj.course_id)
    for sub in subject_data:
        attendance = Attendance.objects.filter(course_id=course)
        attendance_present_count = AttendanceReport.objects.filter(
            attendance_id__in=attendance, status=True, student_id=student_obj.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(
            attendance_id__in=attendance, status=False, student_id=student_obj.id).count()
        subject_name.append(sub.subject_name)
        subject_present_attendance.append(attendance_present_count)
        subject_absent_attendance.append(attendance_absent_count)
    print(attendance_absent_count)
    print(attendance_present_count)
    return render(request, "student_templates/student_home_templates.html", {"total_leave": total_leave,
                                                                             "total_notifications": total_notifications,
                                                                             "total_feedback_send": total_feedback_send,
                                                                             "subject": subject, "subject_name": subject_name,
                                                                             "present_count":attendance_present_count,
                                                                             "absent_count":attendance_absent_count
                                                                             })


def student_view_attendance(request):
    student = Students.objects.get(admin=request.user.id)
    courses = Courses.objects.get(id=student.course_id.id)
    sessions = SessionYearModel.objects.get(id=student.session_year_id.id)
    
    attendance_report = AttendanceReport.objects.filter(student_id=student)
    report_with_subject = []
    for itm in attendance_report:
        print(itm.staff_id.subject_teach)
        report_with_subject.append({
            "subject": itm.staff_id.subject_teach,
            "date": itm.attendance_date,
            "was_present": itm.status
        })
    
    return render(request, "student_templates/student_view_attendance.html", {"courses": courses, "sessions":sessions,"report":report_with_subject})


def student_view_attendance_save(request):
    subject_id = request.POST.get("subject")
    start_year = request.POST.get("start_date")
    end_year = request.POST.get("end_date")
    start_date = datetime.datetime.strptime(start_year, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_year, '%Y-%m-%d').date()
    subj_obj = Subjects.objects.get(id=subject_id)
    user_obj = CustomUser.objects.get(id=request.user.id)
    stu_obj = Students.objects.get(admin=user_obj)
    attendance = Attendance.objects.filter(
        attendance_date__range=(start_date, end_date), subject_id=subj_obj)
    attendance_report = AttendanceReport.objects.filter(
        attendance_id__in=attendance, student_id=stu_obj)
    for report in attendance_report:
        print("Date: "+str(report.attendance_id.attendance_date),
              "Status: "+str(report.attendance_id.status))
    return render(request, "student_templates/student_attendance_data.html", {"attendance_report": attendance_report})


def student_feedback(request):
    student_obj = Students.objects.get(admin=request.user.id)
    feedback_data = FeedBackStudent.objects.filter(student_id=student_obj)
    return render(request, "student_templates/student_feedback.html", {"feedback_data": feedback_data})


def student_feedback_save(request):
    if request.method != "POST":
        return HttpResponseRedirect("/student_feedback")
    else:
        feedback_message = request.POST.get("feedback")
        student_obj = Students.objects.get(admin=request.user.id)
        try:
            feedback_report = FeedBackStudent(
                student_id=student_obj, feedback=feedback_message, feedback_reply="")
            feedback_report.save()
            messages.success(request, "Your feedback has been recorded")
            return HttpResponseRedirect("/student_feedback")
        except:
            messages.error(request, "Something went wrong, try again!")
            return HttpResponseRedirect("/student_feedback")


def student_apply_leave(request):
    student_obj = Students.objects.get(admin=request.user.id)
    leave_data = LeaveReportStudent.objects.filter(student_id=student_obj)
    return render(request, "student_templates/student_apply_leave.html", {"leave_data": leave_data})


def student_apply_leave_save(request):
    if request.method != "POST":
        return HttpResponseRedirect("/student_apply_leave")
    else:
        leave_start_date = request.POST.get("leave_start")
        leave_end_date = request.POST.get("leave_end")
        reason = request.POST.get("leave_reason")
        student_obj = Students.objects.get(admin=request.user.id)
        try:

            leave_report = LeaveReportStudent(
                student_id=student_obj, leave_start_date=leave_start_date,
                leave_end_date=leave_end_date, leave_message=reason, leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied for leave")
            return HttpResponseRedirect("/student_apply_leave")
        except:
            messages.error(request, "Failed to Apply for leave")
            return HttpResponseRedirect("/student_apply_leave")



def student_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    student = Students.objects.get(admin=user.id)
    return render(request, "student_templates/student_profile.html", {"user": user, "student": student})


def student_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("student_profile"))
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
            std = Students.objects.get(admin=user.id)
            std.address = address
            messages.success(request, "Successfully Edited Student Details")
            return HttpResponseRedirect(reverse("student_profile"))
        except:
            messages.error(request, "Failed to Edit Student Details")
            return HttpResponseRedirect(reverse("student_profile"))


@csrf_exempt
def student_fcmtoken_save(request):
    token = request.POST.get("token")
    try:
        student = Students.objects.get(admin=request.user.id)
        student.fcm_token = token
        student.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")


def student_all_notification(request):
    student_object = Students.objects.get(admin=request.user.id)
    notify = NotificationStudent.objects.filter(student_id=student_object)
    return render(request, "student_templates/all_notification.html", {"all_notifications": notify})


def delete_notification(request, notice_id):
    NotificationStudent.objects.filter(id=notice_id).delete()
    notice = NotificationStudent.objects.all()
    return render(request, "student_templates/all_notification.html", {"notification": notice})


def student_notification_reply(request, notice_id):
    notification = NotificationStudent.objects.get(id=notice_id)
    return render(request, "student_templates/notification_reply.html", {"notification": notification})


def student_notification_reply_save(request):
    if request.method != "POST":
        return HttpResponseRedirect("/notification_reply_save")
    else:
        notice_id = request.POST.get("notice_id")
        reply_message = request.POST.get("message_reply")
        try:
            notification = NotificationStudent.objects.get(id=notice_id)
            notification.message_reply = reply_message
            notification.save()
            messages.success(request, "Successfully Replied to Notification")
            return HttpResponseRedirect("/student_all_notification")
        except:
            messages.error(request, "Failed to send Reply")
            return HttpResponseRedirect("/student_all_notification")
