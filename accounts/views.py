from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegisterForm, RecruiterAccountSetupForm
from .models import User
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .forms import ProfileUpdateForm, RecruiterUpdateForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,  urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail
from internships.models import Internship, Application
from django.contrib.auth.views import PasswordResetView
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .forms import RecruiterVerificationForm
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from .models import RecruiterVerification
from django.urls import reverse
from django.views.decorators.http import require_POST


@login_required
def admin_dashboard(request):
    pending_requests = RecruiterVerification.objects.filter(is_approved=False)
    return render(request, 'accounts/admin_dashboard.html', {
        'pending_requests': pending_requests
    })

@login_required
def student_dashboard(request):
    return render(request, 'accounts/student_dashboard.html')

@login_required
def recruiter_dashboard(request):
    internships = Internship.objects.filter(posted_by=request.user)
    applications = Application.objects.filter(internship__in=internships)

    context = {
        'internships': internships,
        'total_internships': internships.count(),
        'total_applications': applications.count(),
        'approved_count': applications.filter(status='approved').count(),
        'pending_count': applications.filter(status='pending').count(),
        'rejected_count': applications.filter(status='rejected').count(),
    }

    return render(request, 'accounts/recruiter_dashboard.html', context)


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Require email confirmation
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Activate your Internship Portal account'
            message = render_to_string('accounts/email_confirmation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            email = EmailMultiAlternatives(
                subject=mail_subject,
                body=message,  # Fallback plain text
                from_email=None,
                to=[user.email]
            )
            email.attach_alternative(message, "text/html")  # ✅ Send as HTML
            email.send()

            messages.success(request, "Please confirm your email to complete registration.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been confirmed. You can now log in.')
        return render(request, 'accounts/email_confirmation.html')
    else:
        return HttpResponse('Activation link is invalid!', status=400)
    
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        # Auto-redirect based on role if already logged in
        if request.user.role == 'students':
            return redirect('internship_list')
        elif request.user.role == 'recruiter':
            return redirect('recruiter_dashboard')
        elif request.user.is_superuser:
            return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")

            # Redirect based on role
            if user.role == 'students':
                return redirect('internship_list')
            elif user.role == 'recruiter':
                return redirect('recruiter_dashboard')
            elif user.is_superuser:
                return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})

    return render(request, 'accounts/login.html')



    
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


@login_required
def profile_view(request):
    user = request.user
    if user.role == 'students':
        form_class = ProfileUpdateForm
        redirect_url = 'internship_list'
    elif user.role == 'recruiter':
        form_class = RecruiterUpdateForm
        redirect_url = 'recruiter_dashboard'
    else:
        return redirect('logout')

    if request.method == 'POST':
        form = form_class(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect(redirect_url)
    else:
        form = form_class(instance=user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': user  # needed to show date_joined in template
    })

class CustomPasswordResetView(PasswordResetView):
    html_email_template_name = 'registration/password_reset_email.html'
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        
        subject = render_to_string(subject_template_name, context).strip()
        body = render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        html_email = render_to_string(self.html_email_template_name, context)
        email_message.attach_alternative(body, "text/html")  # Important line
        email_message.send()


def apply_recruiter_view(request):
    if request.method == 'POST':
        form = RecruiterVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            if RecruiterVerification.objects.filter(email=email, is_approved=False).exists():
                messages.warning(request, "You already have a pending request.")
                return redirect('login')

            form.save()

            # Send email to admin
            send_mail(
                subject='New Recruiter Verification Request',
                message='A new recruiter verification has been submitted. Please check the admin dashboard.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL]
            )

            messages.success(request, 'Your recruiter request has been submitted.')
            return redirect('login')
    else:
        form = RecruiterVerificationForm()

    return render(request, 'accounts/apply_recruiter.html', {'form': form})



@login_required
def approve_recruiter(request, pk):
    recruiter = get_object_or_404(RecruiterVerification, pk=pk)

    if recruiter.is_approved:
        messages.info(request, "Recruiter already approved.")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        recruiter.is_approved = True
        recruiter.approved_at = now()
        recruiter.save()

        setup_link = request.build_absolute_uri(
            reverse('setup_recruiter_account', kwargs={'pk': recruiter.pk})
        )

        subject = 'You are approved as a Recruiter – Internship Portal'
        text_content = f'Hi {recruiter.full_name}, please use the link below to set up your account:\n{setup_link}'
        html_content = render_to_string('accounts/recruiter_approval_email.html', {
            'recruiter': recruiter,
            'setup_link': setup_link,
        })

        email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [recruiter.email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        messages.success(request, 'Recruiter approved and email sent.')
        return redirect('admin_dashboard')


@login_required
def reject_recruiter(request, pk):
    recruiter = get_object_or_404(RecruiterVerification, pk=pk)

    if request.method == 'POST':
        # Optionally delete or just mark as rejected
        recruiter.delete()

        # Send rejection email
        send_mail(
            subject='Recruiter Application Rejected – Internship Portal',
            message=f"Hi {recruiter.full_name},\n\nWe regret to inform you that your recruiter application has been rejected after review.\n\nThank you for your interest.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recruiter.email],
            fail_silently=False,
        )

        messages.warning(request, f"{recruiter.full_name}'s request has been rejected.")
        return redirect('admin_dashboard')


def setup_recruiter_account(request, pk):
    verification = get_object_or_404(RecruiterVerification, pk=pk, is_approved=True)

    if request.method == 'POST':
        form = RecruiterAccountSetupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = verification.email
            user.role = 'recruiter'
            user.is_active = True
            user.save()

            messages.success(request, 'Recruiter account created successfully. You can now log in.')
            return redirect('login')
    else:
        form = RecruiterAccountSetupForm()
    return render(request, 'accounts/setup_recruiter_account.html', {'form': form, 'verification': verification})