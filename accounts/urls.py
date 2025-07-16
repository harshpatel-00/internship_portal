from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .views import CustomPasswordResetView


urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    # Dashboards
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('recruiter/dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('apply-recruiter/', views.apply_recruiter_view, name='apply_recruiter'),
    path('approve-recruiter/<int:pk>/', views.approve_recruiter, name='approve_recruiter'),
    path('apply-recruiter/setup/<int:pk>/', views.setup_recruiter_account, name='setup_recruiter_account'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/approve-recruiter/<int:pk>/', views.approve_recruiter, name='approve_recruiter'),
    path('admin/reject-recruiter/<int:pk>/', views.reject_recruiter, name='reject_recruiter'),
    


    # Profile
    path('profile/', views.profile_view, name='profile'),

    # Password Change (after login)
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html',
        success_url=reverse_lazy('profile')
    ), name='password_change'),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),

    # Password Reset (forgot password via email)
    path('password_reset/', CustomPasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]
