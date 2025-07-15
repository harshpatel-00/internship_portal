from django import forms
from .models import Internship

class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = ['title', 'company', 'description', 'location', 'stipend', 'duration']