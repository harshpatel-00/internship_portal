from accounts.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Internship
from .forms import InternshipForm
from .models import Application
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
import openpyxl
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
from reportlab.pdfgen import canvas
from django.contrib.auth import get_user_model

# from .models import InternshipApplication


@login_required
def create_internship(request):
    if request.user.role != 'recruiter':
        return redirect('login')
    
    if request.method == 'POST':
        form = InternshipForm(request.POST)
        if form.is_valid():
            internship = form.save(commit=False)
            internship.posted_by = request.user
            internship.save()
            return redirect('internship_list')
    else:
        form = InternshipForm()
            
    return render(request, 'internships/create.html', {'form': form})

from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def internship_list(request):
    query = request.GET.get('q')
    location = request.GET.get('location')
    duration = request.GET.get('duration')
    company = request.GET.get('company')

    internships = Internship.objects.all()

    if query:
        internships = internships.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(location__icontains=query)
        )

    if location:
        internships = internships.filter(location__icontains=location)
    if duration:
        internships = internships.filter(duration__icontains=duration)
    if company:
        internships = internships.filter(company__icontains=company)

    # Pagination
    paginator = Paginator(internships, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Applied internship IDs (for student only)
    applied_ids = []
    if request.user.is_authenticated and request.user.role == 'students':
        applied_ids = Application.objects.filter(student=request.user).values_list('internship_id', flat=True)

    return render(request, 'internships/list.html', {
        'page_obj': page_obj,
        'applied_ids': applied_ids,
        'query': query,
        'location': location,
        'duration': duration,
        'company': company,
    })




@login_required
def apply_for_internship(request, internship_id):
    internship = Internship.objects.get(id=internship_id)
    if request.user.role != 'students':
        return redirect('internship_list')
    
    if internship.posted_by == request.user:
        messages.error(request, "You cannot apply to your own internship.")
        return redirect('internship_list')

    
    already_applied = Application.objects.filter(student=request.user, internship=internship).exists()
    if already_applied:
        messages.warning(request, 'You have already applied for this internship.')
    else:
        Application.objects.create(student=request.user, internship=internship)
        messages.success(request, 'Application applied.')
        
    return redirect('internship_list')
        
@login_required
def my_applications(request):
    student = request.user
    applications = Application.objects.filter(student=student).select_related('internship')

    if 'export' in request.GET:
        export_type = request.GET.get('export')
        
        if export_type == 'excel':
            return export_applications_excel(applications)
        elif export_type == 'pdf':
            return export_applications_pdf(applications)

    return render(request, 'internships/my_applications.html', {'applications': applications})

@login_required
def recruiter_applicants(request):
    if request.user.role != 'recruiter':
        return redirect('login')
    
    internships = Internship.objects.filter(posted_by=request.user)
    applications = Application.objects.filter(internship__in=internships).select_related('internship', 'student')

    paginator = Paginator(applications, 5)  # Show 5 applications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'internships/recruiter_applicants.html', {'page_obj': page_obj})

def export_applications_pdf(request):
    
    applications = Application.objects.filter(student=request.user)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="my_applications.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)
    p.drawString(100, 800, "Internship Applications:")

    # applications = request.user.student.applications.select_related('internship').all()

    y = 780
    for app in applications:
        line = f"{app.internship.title} at {app.internship.posted_by.username} | Status: {app.status}"
        p.drawString(100, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response


def export_applications_excel(request):
    
    user = request.user
    applications = Application.objects.filter(student=user)


    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Applications"

    # Headers
    headers = ['Internship Title', 'Company', 'Location', 'Stipend', 'Status', 'Applied On']
    ws.append(headers)

    for app in applications:
        ws.append([
            app.internship.title,
            app.internship.posted_by.username,
            app.internship.location,
            app.internship.stipend,
            app.status,
            app.applied_at.strftime('%Y-%m-%d %H:%M')
        ])


    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=applications.xlsx'
    wb.save(response)
    return response

@login_required
def update_application_status(request, app_id):
    application = get_object_or_404(Application, id=app_id)
    if request.user == application.internship.posted_by:
        if request.method == 'POST':
            new_status = request.POST.get('status')
            if new_status in ['approved', 'rejected']:
                application.status = new_status
                application.save()
    return redirect('recruiter_applicants')

@login_required
def view_student_profile(request, student_id):
    if request.user.role != 'recruiter':
        return redirect('login')
    
    student = get_object_or_404(User, id=student_id, role='students')
    return render(request, 'internships/student_profile.html', {'student': student})

@login_required
def student_detail(request, student_id):
    if request.user.role != 'recruiter':
        return redirect('login')

    User = get_user_model()
    student = get_object_or_404(User, id=student_id, role='students')
    return render(request, 'internships/student_detail.html', {'student': student})