from django.urls import path
from . import views

urlpatterns = [
    path('',views.internship_list, name='internship_list'),
    path('create/', views.create_internship, name='create_internship'),
    path('apply/<int:internship_id>/', views.apply_for_internship, name='apply_for_internship'),
    path('my_applications/', views.my_applications, name='my_applications'),
    path('applicants/', views.recruiter_applicants, name='recruiter_applicants'),
    path('my_applications/pdf/', views.export_applications_pdf, name='export_applications_pdf'),
    path('my_applications/excel/', views.export_applications_excel, name='export_applications_excel'),
    path('update_application/<int:app_id>/', views.update_application_status, name='update_application_status'),
    path('student/<int:student_id>/', views.view_student_profile, name='view_student_profile'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),

]