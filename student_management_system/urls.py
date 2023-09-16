"""Student_Management_Branch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from student_management_app import views,HodViews,StaffViews,StudentViews

from student_management_system import settings
admin.autodiscover()

urlpatterns = [

    path('index',views.index),
    path('dologin',views.dologin,name="dologin"),

    path('get_user_details', views.getuserdetail),

    path('admin_home', HodViews.admin_home,name="admin_home"),
    path('admin_sendnotification_staff/<str:staff_id>', HodViews.admin_sendnotification_staff,name="admin_sendnotification_staff"),
    path('admin_sendnotification_student/<str:student_id>', HodViews.admin_sendnotification_student,name="admin_sendnotification_student"),
    path('notify_staff/<str:staff_id>', HodViews.notify_staff,name="notify_staff"),
    path('notify_student/<str:student_id>', HodViews.notify_student,name="notify_student"),
    path('send_staff_notification', HodViews.send_staff_notification,name="send_staff_notification"),
    path('send_student_notification', HodViews.send_student_notification,name="send_student_notification"),
    path('add_staff', HodViews.add_staff),
    path('add_course', HodViews.add_course),
    path('add_staff_save', HodViews.add_staff_save),
    path('add_student', HodViews.add_student),
    path('add_student_save', HodViews.add_student_save),
    path('add_course_save', HodViews.add_course_save),
    path('add_subject', HodViews.add_subject),
    path('add_subject_save', HodViews.add_subject_save),
    path('manage_staff', HodViews.manage_staff),
    path('manage_student', HodViews.manage_student),
    path('manage_course', HodViews.manage_course),
    path('manage_subject', HodViews.manage_subject),
    path('edit_staff/<str:staff_id>', HodViews.edit_staff),
    path('edit_staff_save', HodViews.edit_staff_save),
    path('edit_student/<str:student_id>', HodViews.edit_student),
    path('edit_student_save', HodViews.edit_student_save),
    path('edit_course/<str:course_id>', HodViews.edit_course),
    path('edit_courses_save', HodViews.edit_courses_save),
    path('edit_session/<str:session_id>', HodViews.edit_session),
    path('edit_session_save', HodViews.edit_session_save),
    path('edit_subject/<str:subject_id>', HodViews.edit_subject),
    path('edit_subject_save', HodViews.edit_subject_save),
    path('staff_home', StaffViews.staff_home,name="staff_home"),
    path('student_home', StudentViews.student_home,name="student_home"),
    path('add_session', HodViews.add_session),
    path('add_session_save', HodViews.add_session_save),
    path('manage_session', HodViews.manage_session),
    path('staff_take_attendance', StaffViews.staff_take_attendance),
    path('get_students', StaffViews.get_students, name="get_students"),
    path('staff_apply_leave', StaffViews.staff_apply_leave, name="staff_apply_leave"),
    path('staff_apply_leave_save', StaffViews.staff_apply_leave_save, name="staff_apply_leave_save"),
    path('staff_feedback', StaffViews.staff_feedback, name="staff_feedback"),
    path('staff_feedback_save', StaffViews.staff_feedback_save, name="staff_feedback_save"),
    path('staff_fcmtoken_save', StaffViews.staff_fcmtoken_save, name="staff_fcmtoken_save"),
    path('staff_update_attendance', StaffViews.staff_update_attendance, name="staff_update_attendance"),
    path('staff_all_notification', StaffViews.staff_all_notification, name="staff_all_notification"),
    path('send_notification_reply/<str:notice_id>', StaffViews.send_notification_reply, name="send_notification_reply"),
    path('notification_reply_save', StaffViews.notification_reply_save, name="notification_reply_save"),
    path('delete_notification/<str:notice_id>', StaffViews.delete_notification, name="delete_notification"),
    path('get_students', StaffViews.get_students, name="get_students"),
    path('get_attendance_dates', StaffViews.get_attendance_dates, name="get_attendance_dates"),
    path('get_attendance_student', StaffViews.get_attendance_student, name="get_attendance_student"),
    path('save_attendance_data', StaffViews.save_attendance_data, name="save_attendance_data"),
    path('save_updateattendance_data', StaffViews.save_updateattendance_data,name="save_updateattendance_data"),
    path('student_view_attendance', StudentViews.student_view_attendance, name="student_view_attendance"),
    path('student_view_attendance_save', StudentViews.student_view_attendance_save, name="student_view_attendance_save"),
    path('student_feedback', StudentViews.student_feedback, name="student_feedback"),
    path('student_feedback_save', StudentViews.student_feedback_save, name="student_feedback_save"),
    path('student_apply_leave', StudentViews.student_apply_leave, name="student_apply_leave"),
    path('student_apply_leave_save', StudentViews.student_apply_leave_save, name="student_apply_leave_save"),
    path('check_email_exist', HodViews.check_email_exist,name="check_email_exist"),
    path('student_feedback_message', HodViews.student_feedback_message,name="student_feedback_message"),
    path('staff_feedback_message', HodViews.staff_feedback_message,name="staff_feedback_message"),
    path('edit_staff_reply/<str:feed_id>', HodViews.edit_staff_reply,name="edit_staff_reply"),
    path('edit_staff_reply_save', HodViews.edit_staff_reply_save,name="edit_staff_reply_save"),
    path('edit_student_reply/<str:feed_id>', HodViews.edit_student_reply, name="edit_student_reply"),
    path('notify_staff/<str:feed_id>', HodViews.notify_staff, name="notify_staff"),
    path('edit_student_reply_save', HodViews.edit_student_reply_save, name="edit_student_reply_save"),
    path('student_leave_view', HodViews.student_leave_view, name="student_leave_view"),
    path('staff_leave_view', HodViews.staff_leave_view, name="staff_leave_view"),
    path('student_approve_leave/<str:leave_id>', HodViews.student_approve_leave,name="student_approve_leave"),
    path('student_disapprove_leave/<str:leave_id>', HodViews.student_disapprove_leave,name="student_disapprove_leave"),
    path('staff_approve_leave/<str:leave_id>', HodViews.staff_approve_leave,name="staff_approve_leave"),
    path('staff_disapprove_leave/<str:leave_id>', HodViews.staff_disapprove_leave,name="staff_disapprove_leave"),
    path('admin_view_attendance', HodViews.admin_view_attendance,name="admin_view_attendance"),
    path('delete_student/<str:student_id>', HodViews.delete_student,name="delete_student"),
    path('delete_staff/<str:staff_id>', HodViews.delete_staff,name="delete_staff"),
    path('delete_course/<str:course_id>', HodViews.delete_course,name="delete_course"),
    path('delete_subject/<str:subject_id>', HodViews.delete_subject,name="delete_subject"),
    path('delete_session/<str:session_id>', HodViews.delete_session,name="delete_session"),
    path('present_student_attendance/<str:session_id>', HodViews.present_student_attendance,name="present_student_attendance"),
    path('admin_profile', HodViews.admin_profile, name="admin_profile"),
    path('admin_profile_save', HodViews.admin_profile_save, name="admin_profile_save"),
    path('staff_profile', StaffViews.staff_profile, name="staff_profile"),
    path('staff_profile_save', StaffViews.staff_profile_save, name="staff_profile_save"),
    path('student_profile', StudentViews.student_profile, name="student_profile"),
    path('student_profile_save', StudentViews.student_profile_save, name="student_profile_save"),
    path('student_fcmtoken_save', StudentViews.student_fcmtoken_save, name="student_fcmtoken_save"),
    path('student_all_notification', StudentViews.student_all_notification, name="student_all_notification"),
    path('delete_notification/<str:notice_id>', StudentViews.delete_notification, name="delete_notification"),
    path('logout',views.logout_user),
    path('password_reset/',auth_views.PasswordResetView.as_view(),name="reset_password"),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name="password_reset_done"),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name="password_reset_confirm"),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name="password_reset_complete"),

    path('',views.login_page,name="login_page"),
    path('admin/', admin.site.urls),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
