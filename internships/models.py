from django.db import models
from accounts.models import User


class Internship(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    stipend = models.CharField(max_length=100)
    description = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'recruiter'})
    posted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class Application(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')
    
    class Meta:
        unique_together = ['student', 'internship']
        
    def __str__(self):
        return f"{self.student.username} - {self.internship.title}"
    
