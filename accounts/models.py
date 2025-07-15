from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('students', 'Students'),
        ('recruiter', 'Recruiter'),
    )
    role = models.CharField(max_length = 20, choices=ROLE_CHOICES)
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')

    location = models.CharField(max_length=100, blank=False)
    college_name = models.CharField(max_length=255, blank=False)
    mobile_number = models.CharField(max_length=15, blank=False)
    last_semester_grade = models.CharField(max_length=10, blank=False)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
class RecruiterVerification(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    institution = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    id_proof = models.FileField(upload_to='recruiter_proofs/')
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} ({'Approved' if self.is_approved else 'Pending'})"