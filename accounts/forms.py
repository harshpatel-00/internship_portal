from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import RecruiterVerification

class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('students', 'Students')], widget=forms.Select)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2','location', 'college_name', 'mobile_number', 'last_semester_grade']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email



class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'mobile_number', 'location', 'college_name', 'last_semester_grade'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True



class RecruiterUpdateForm(forms.ModelForm):
    date_joined = forms.DateTimeField(
        label='Date Joined',
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'date_joined']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

class RecruiterVerificationForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    institution = forms.CharField(max_length=255)
    position = forms.CharField(max_length=100)
    id_proof = forms.FileField(help_text="Upload ID or proof you are a teacher/recruiter")
    
class RecruiterVerificationForm(forms.ModelForm):
    class Meta:
        model = RecruiterVerification
        fields = ['full_name', 'email', 'institution', 'position', 'id_proof']
        
class RecruiterAccountSetupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
