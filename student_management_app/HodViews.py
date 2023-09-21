import json
from datetime import datetime
from django.db.models import Count
from django.contrib import messages
from django.contrib.sites import requests
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from student_management_app.models import NotificationStaff, NotificationStudent, CustomUser, AttendanceReport, Attendance, Courses, Staffs, Subjects, Students, SessionYearModel, FeedBackStaff, FeedBackStudent, LeaveReportStudent, LeaveReportStaff


def admin_home(request):
    # for admin home card
    student = Students.objects.all().count()
    staff = Staffs.objects.all().count()
    courses = Courses.objects.all().count()
    all_subjects = Subjects.objects.all().count()
    course_all = Courses.objects.all()

    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []
    for course in course_all:
        subjects = Subjects.objects.filter(course_id=course.id).count()
        students = Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)

    # to show graph of student count registered for each course in specific session
    student_counts = Students.objects.values('course_id', 'session_year_id') \
        .annotate(student_count=Count('id')) \
        .order_by('session_year_id', 'course_id')
    student_count_with_course_n_session = []
    course_session_for_lable = []
    for itm in student_counts:
        lable = Courses.objects.get(id=itm['course_id']).course_name + " [" + str(SessionYearModel.objects.get(
            id=itm['session_year_id']).session_start_year) + ", " + str(SessionYearModel.objects.get(id=itm['session_year_id']).session_end_year) + "]"
        course_session_for_lable.append(lable)
        student_count_with_course_n_session.append(itm["student_count"])

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

    # for present & absent ration of each staff
    staff_present = []
    staff_absent = []
    staff_name_list = []
    staffs_list = Staffs.objects.all()
    for itm in staffs_list:
        attendance = AttendanceReport.objects.filter(
            staff_id=itm.id).count()
        leave = LeaveReportStaff.objects.filter(
            staff_id=itm.id, leave_status=1).count()
        staff_present.append(attendance)
        staff_absent.append(leave)
        staff_name_list.append(itm.admin.username)

    # for present & absent ration of each staff
    student_present = []
    student_absent = []
    student_name_list = []
    students_list = Students.objects.all()
    for stu in students_list:
        attendance = AttendanceReport.objects.filter(
            student_id=stu.id, status=True).count()
        absent = AttendanceReport.objects.filter(
            student_id=stu.id, status=False).count()
        leaves = LeaveReportStudent.objects.filter(
            student_id=stu.id, leave_status=1).count()
        student_present.append(attendance)
        student_absent.append(leaves + absent)
        student_name_list.append(stu.admin.username)

    return render(request, "hod_templates/home_content.html", {"total_students": student, "total_staff": staff,
                                                               "total_courses": courses, "total_subject": all_subjects,
                                                               "subject_count_list": subject_count_list, "course_name_list": course_name_list,
                                                               "student_count_list_in_course": student_count_list_in_course,
                                                               "staff_present_list": staff_present, "staff_absent_list": staff_absent,
                                                               "staff_name_list": staff_name_list, "student_present_list": student_present,
                                                               "student_absent_list": student_absent, "student_name_list": student_name_list,
                                                               "course_n_session_lable": course_session_for_lable,
                                                               "student_count_with_course_n_session": student_count_with_course_n_session,
                                                               "staff_wrt_subjects": staff_wrt_subjects,
                                                               "subjects_as_lable": subjects_as_lable,
                                                               "student_wrt_session": students_wrt_sessions,
                                                               "session_as_lable": session_as_lable
                                                               })


# All add tabs

def add_staff(request):
    subjects = Subjects.objects.all()
    return render(request, "hod_templates/add_staff_template.html", {"subjects": subjects})


def delete_staff(request, staff_id):
    Staffs.objects.filter(id=staff_id).delete()
    staffs = Staffs.objects.all()
    return render(request, "hod_templates/manage_staff_template.html", {"staffs": staffs})


def add_staff_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        address = request.POST.get("address")
        subject_teach = request.POST.get("subject_name")

        try:
            user = CustomUser.objects.create_user(
                username=username, password=password, email=email, last_name=last_name, first_name=first_name, user_type=2)
            user.staffs.address = address
            user.staffs.subject_teach = subject_teach
            user.save()
            messages.success(request, "Successfully Added Staff")
            return HttpResponseRedirect("/add_staff")
        except:
            messages.error(request, "Failed to Add Staff")
            return HttpResponseRedirect("/add_staff")


def add_course(request):
    sessions = SessionYearModel.objects.all()
    return render(request, "hod_templates/add_course_template.html", {"sessions": sessions})


def delete_course(request, course_id):
    Courses.objects.filter(id=course_id).delete()
    courses = Courses.objects.all()
    return render(request, "hod_templates/manage_course_template.html", {"courses": courses})


def add_course_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        course_name = request.POST.get("course_name")
        description = request.POST.get("description")
        session = request.POST.get("session")
        try:
            new_course = Courses(course_name=course_name,
                                 description=description)
            session_year = SessionYearModel.objects.get(id=session)
            new_course.session_year_id = session_year
            new_course.save()

            messages.success(request, "Successfully Added Course")
            return HttpResponseRedirect("/add_course")
        except:
            messages.error(request, "Failed to Add Course")
            return HttpResponseRedirect("/add_course")


def add_student(request):
    courses = Courses.objects.all()
    sessions = SessionYearModel.objects.all()
    return render(request, "hod_templates/add_student_template.html", {"courses": courses, "sessions": sessions})


def delete_student(request, student_id):
    Students.objects.filter(id=student_id).delete()
    students = Students.objects.all()
    return render(request, "hod_templates/manage_student_template.html", {"students": students})


def add_student_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        address = request.POST.get("address")
        session_year_id = request.POST.get("session")
        courses = request.POST.get("course")
        gender = request.POST.get("gender")
        try:
            user = CustomUser.objects.create_user(
                username=username, password=password, email=email, last_name=last_name, first_name=first_name, user_type=3)

            user.students.address = address
            courses_obj = Courses.objects.get(id=courses)
            user.students.course_id = courses_obj
            session_year = SessionYearModel.objects.get(id=session_year_id)
            user.students.session_year_id = session_year
            user.students.gender = gender
            user.save()

            messages.success(request, "Successfully Added Student")
            return HttpResponseRedirect("/add_student")
        except:
            messages.error(request, "Failed to Add Student")
            return HttpResponseRedirect("/add_student")


def add_subject(request):
    courses = Courses.objects.all()
   # staffs = CustomUser.objects.filter(user_type=2)
    sessions = SessionYearModel.objects.all()
    return render(request, "hod_templates/add_subject_template.html", {"courses": courses, "sessions": sessions})


def delete_subject(request, subject_id):
    Subjects.objects.filter(id=subject_id).delete()
    subjects = Subjects.objects.all()
    return render(request, "hod_templates/manage_subject_template.html", {"subjects": subjects})


def add_subject_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        subject_name = request.POST.get("subject_name")
        course_id = request.POST.get("course")
        course = Courses.objects.get(id=course_id)

        try:
            subject = Subjects(subject_name=subject_name,
                               course_id=course)
            subject.save()
            messages.success(request, "Successfully Added Subject")
            return HttpResponseRedirect("/add_subject")
        except:
            messages.error(request, "Failed to Add Subject")
            return HttpResponseRedirect("/add_subject")


def manage_staff(request):
    staffs = Staffs.objects.all()
    return render(request, "hod_templates/manage_staff_template.html", {"staffs": staffs})


def manage_student(request):
    students = Students.objects.all()
    return render(request, "hod_templates/manage_student_template.html", {"students": students})


def manage_course(request):
    courses = Courses.objects.all()
    return render(request, "hod_templates/manage_course_template.html", {"courses": courses})


def manage_subject(request):
    subjects = Subjects.objects.all()
    return render(request, "hod_templates/manage_subject_template.html", {"subjects": subjects})


def edit_staff(request, staff_id):
    staffs = Staffs.objects.get(admin=staff_id)
    return render(request, "hod_templates/edit_staff_template.html", {"staffs": staffs})


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        staff_id = request.POST.get("staff_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        address = request.POST.get("address")
        try:
            user = CustomUser.objects.get(id=staff_id)
            user.address = address
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.save()
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()
            messages.success(request, "Successfully Edited Staff Details")
            return HttpResponseRedirect("/edit_staff/"+staff_id)
        except:
            messages.error(request, "Failed to Edit Staff Details")
            return HttpResponseRedirect("/edit_staff/"+staff_id)


def edit_student(request, student_id):
    courses = Courses.objects.all()
    sessions = SessionYearModel.objects.all()
    students = Students.objects.get(admin=student_id)
    return render(request, "hod_templates/edit_student_template.html", {"students": students, "courses": courses, "sessions": sessions})


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        student_id = request.POST.get("students_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        address = request.POST.get("address")
        session_start = request.POST.get("sstart")
        session_end = request.POST.get("send")
        gender = request.POST.get("gender")
        course_id = request.POST.get("course")
        if request.FILES.get("profile_pic", False):
            profile_pic = request.FILES.get("profile_pic")
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            profile_pic_url = fs.url(filename)
        else:
            profile_pic_url = None

        try:
            user = CustomUser.objects.get(id=student_id)
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.save()
            student_model = Students.objects.get(admin=student_id)
            student_model.address = address
            student_model.session_start_year = session_start
            student_model.session_end_year = session_end
            student_model.gender = gender
            course = Courses.objects.get(id=course_id)
            student_model.course_id = course
            if profile_pic_url != None:
                student_model.profile_pic = profile_pic_url
            student_model.save()
            messages.success(request, "Successfully Edited Student Details")
            return HttpResponseRedirect("/edit_student/"+student_id)
        except:
            messages.error(request, "Failed to Edit Student Details")
            return HttpResponseRedirect("/edit_student/"+student_id)


def edit_course(request, course_id):
    sessions = SessionYearModel.objects.all()
    courses = Courses.objects.get(id=course_id)

    return render(request, "hod_templates/edit_courses_template.html", {"course": courses, "sessions": sessions})


def edit_courses_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        course_id = request.POST.get("course_id")
        courses_name = request.POST.get("course_name")
        description = request.POST.get("description")
        session_selected = request.POST.get("session")

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = courses_name
            course.description = description
            new_session = SessionYearModel.objects.get(id=session_selected)
            course.session_year_id = new_session
            course.save()
            messages.success(request, "Successfully Edited Course Details")
            return HttpResponseRedirect("/edit_course/"+course_id)
        except:
            messages.error(request, "Failed to Edit Course Details")
            return HttpResponseRedirect("/edit_course/" + course_id)


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    return render(request, "hod_templates/edit_subject_template.html", {"subject": subject, "courses": courses})


def edit_subject_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        subject_id = request.POST.get("subject_id")
        subject_name = request.POST.get("subject_name")
        course_id = request.POST.get("course")
        try:
            user = Subjects.objects.get(id=subject_id)
            user.subject_name = subject_name
            course = Courses.objects.get(id=course_id)
            user.course_id = course
            user.save()
            messages.success(request, "Successfully Edited Subject Details")
            return HttpResponseRedirect("/edit_subject/"+subject_id)
        except:
            messages.error(request, "Failed to Edit Subject Details")
            return HttpResponseRedirect("/edit_subject/"+subject_id)


def add_session(request):
    return render(request, "hod_templates/add_session_template.html")


def delete_session(request, session_id):
    SessionYearModel.objects.filter(id=session_id).delete()
    session = SessionYearModel.objects.all()
    return render(request, "hod_templates/manage_session_template.html", {"sessions": session})


def add_session_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        session_start = request.POST.get("session_start")
        session_end = request.POST.get("session_end")

        try:
            sessionyearsave = SessionYearModel(
                session_start_year=session_start, session_end_year=session_end)
            sessionyearsave.save()
            messages.success(request, "Successfully Added Session")
            return HttpResponseRedirect("/add_session")
        except:
            messages.error(request, "Failed to Add Session")
            return HttpResponseRedirect("/add_session")


def manage_session(request):
    sessions = SessionYearModel.objects.all()
    return render(request, "hod_templates/manage_session_template.html", {"sessions": sessions})


def edit_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    return render(request, "hod_templates/edit_session_template.html", {"session": session})


def edit_session_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        session_id = request.POST.get("session_id")
        session_start_year = request.POST.get("session_start_year")
        session_end_year = request.POST.get("session_end_year")

        try:
            session = SessionYearModel.objects.get(id=session_id)
            session.session_start_year = session_start_year
            session.session_end_year = session_end_year
            session.save()
            messages.success(request, "Successfully Edited Session Details")
            return HttpResponseRedirect("/edit_session/"+session_id)
        except:
            messages.error(request, "Failed to Edit Session Details")
            return HttpResponseRedirect("/edit_session/"+session_id)


@csrf_exempt
def check_email_exist(request):

    email = request.POST.get("email")
    data = {
        'is_taken': CustomUser.objects.get(email=email).exists()
    }
    if data['is_taken']:
        data['error_message'] = "Already exists"
    return JsonResponse(data)


def student_feedback_message(request):
    feedback = FeedBackStudent.objects.all()
    return render(request, "hod_templates/student_feedback_message.html", {"feedback": feedback})


def staff_feedback_message(request):
    feedback = FeedBackStaff.objects.all()
    return render(request, "hod_templates/staff_feedback_message.html", {"feedback": feedback})


def edit_staff_reply(request, feed_id):
    feedback = FeedBackStaff.objects.get(id=feed_id)
    return render(request, "hod_templates/staff_reply_feedback.html", {"feedback": feedback})


def edit_staff_reply_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        feed_id = request.POST.get("feed_id")
        feedback_reply = request.POST.get("reply")

        try:
            user = FeedBackStaff.objects.get(id=feed_id)
            user.feedback_reply = feedback_reply

            user.save()
            messages.success(request, "Successfully replied to Staff. ")
            return HttpResponseRedirect("/edit_staff_reply/" + feed_id)
        except:
            messages.error(request, "Failed to reply to Staff.")
            return HttpResponseRedirect("/edit_staff_reply/" + feed_id)


def edit_student_reply(request, feed_id):
    feedback = FeedBackStudent.objects.get(id=feed_id)
    return render(request, "hod_templates/student_reply_feedback.html", {"feedback": feedback})


def edit_student_reply_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        feed_id = request.POST.get("feed_id")
        feedback_reply = request.POST.get("reply")

        try:
            user = FeedBackStudent.objects.get(id=feed_id)
            user.feedback_reply = feedback_reply

            user.save()
            messages.success(request, "Successfully replied to Staff. ")
            return HttpResponseRedirect("/edit_student_reply/" + feed_id)
        except:
            messages.error(request, "Failed to reply to Staff.")
            return HttpResponseRedirect("/edit_student_reply/" + feed_id)


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all()
    return render(request, "hod_templates/student_leave_view.html", {"leaves": leaves})


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all()
    return render(request, "hod_templates/staff_leave_view.html", {"leaves": leaves})


def student_approve_leave(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


def student_disapprove_leave(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


def staff_approve_leave(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))


def staff_disapprove_leave(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))


def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    session_year_id = SessionYearModel.objects.all()
    return render(request, "hod_templates/admin_view_attendance.html", {"subjects": subjects, "sessions": session_year_id})


@csrf_exempt
def admin_get_attendance_dates(request):
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
def admin_get_attendance_student(request):
    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    list_data = []

    for student in attendance_data:
        data_small = {"id": student.student_id.admin.id, "name": student.student_id.admin.first_name +
                      " "+student.student_id.admin.last_name, "status": student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def present_student_attendance(request, session_id):
    students = Students.objects.filter(session_year_id=session_id)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    return render(request, "hod_templates/admin_profile.html", {"user": user})


def admin_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        try:
            user = CustomUser.objects.get(id=request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            if password != None and password != "":
                user.password = password
            user.save()
            messages.success(request, "Successfully Edited Admin Details")
            return HttpResponseRedirect("manage_session")
        except:
            messages.error(request, "Failed to Edit Admin Details")
            return HttpResponseRedirect("manage_session")


def admin_sendnotification_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    all_notifications = NotificationStaff.objects.filter(staff_id=staff)
    return render(request, "hod_templates/staff_notification.html", {'staff': staff, 'all_notifications': all_notifications})


def admin_sendnotification_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    all_notifications = NotificationStudent.objects.filter(student_id=student)
    return render(request, "hod_templates/student_notification.html", {'student': student, 'all_notifications': all_notifications})


"""@csrf_exempt
def send_student_notification(request):
    id=request.POST.get("id")
    messages=request.POST.get("messages")
    student=Students.objects.get(admin=id)
    token=student.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "Notification":{
            "Title":"Student Management System",
            "Message":messages
        },
        "To":token
    }
    header={"Content-type":"application/json","Authorization":"key"}
    data=requests.post(url,data=json.dumps(body),headers=header)
    notification = NotificationStudent(student_id=student, message=messages)
    notification.save()
    print(data.text)
    return HttpResponse("True")

@csrf_exempt
def send_staff_notification(request):
    id=request.POST.get("id")
    messages=request.POST.get("messages")
    staff=Staffs.objects.get(admin=id)
    token=staff.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "Notification":{
            "Title":"Student Management System",
            "Message":messages
        },
        "To":token
    }
    header={"Content-type":"application/json","Authorization":"key"}
    data=requests.post(url,data=json.dumps(body),headers=header)
    notification = NotificationStaffs(staff_id=staff, message=messages)
    notification.save()
    print(data.text)
    return HttpResponse("True")"""


def notify_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    return render(request, 'hod_templates/notify_staff.html', {'staff': staff})


def send_staff_notification(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        message = request.POST.get("notice")
        staff_id = request.POST.get("staff_id")
        staff = Staffs.objects.get(admin=staff_id)
        try:
            user = NotificationStaff(staff_id=staff, message=message)

            user.save()
            messages.success(request, "Notification send to Staff.")
            return HttpResponseRedirect("/notify_staff/" + staff_id)
        except:
            messages.error(request, "Failed to notify Staff.")
            return HttpResponseRedirect("/notify_staff/" + staff_id)


def notify_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    return render(request, 'hod_templates/notify_student.html', {'student': student})


def send_student_notification(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        message = request.POST.get("notice")
        std_id = request.POST.get("feed_id")
        student = Students.objects.get(admin=std_id)
        try:
            user = NotificationStudent(student_id=student, message=message)
            user.save()
            messages.success(request, "Notification send to Student.")
            return HttpResponseRedirect("/notify_student/" + std_id)
        except:
            messages.error(request, "Failed to notify Student.")
            return HttpResponseRedirect("/notify_student/" + std_id)
